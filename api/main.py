from typing import Any, Dict, Optional

from fastapi import FastAPI, UploadFile, Form, File, Body, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
from xml.sax.saxutils import escape
from .search_logic import search_products
from .lead_logic import log_lead_and_get_details
from .image_embedding_logic import get_image_embedding
from .db_utils import get_connection
from .config import FEATURES, DEFAULT_STORE_ID
from .payment_logic import create_transaction, update_transaction_status
from .notification_logic import notify_seller_of_lead
from ussd.provider import trigger_ussd_payment
import os
import requests
import random
import string

app = FastAPI()

def generate_store_code():
    """Generate a unique store code in format VIBE-XXXXX."""
    charset = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(charset, k=5))
        store_code = f"VIBE-{code}"

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT store_id FROM stores WHERE store_code = %s", (store_code,))
            if not cur.fetchone():
                return store_code
        except Exception:
            return store_code
        finally:
            cur.close()
            conn.close()

# typed user state to reduce optional-access warnings
user_states: Dict[str, Dict[str, Any]] = {}


def twilio_message_response(message: str):
    escaped = escape(message)
    xml = f"<Response><Message>{escaped}</Message></Response>"
    return Response(content=xml, media_type="application/xml")


def whatsapp_help_text():
    return (
        "Welcome to VibeShop Assistant! Send an image of a product you want, "
        "then reply with the result number (1-3) to select it. After selection, "
        "reply with 'PAY' to proceed with payment."
    )


# --- Structured User State Management ---
# Key: user_phone_number
# Value: {
#     "last_results": [],  # List of product dicts from search
#     "selected_product": {},  # Currently selected product
#     "state": "IDLE" | "WAITING_AMOUNT"  # User state in payment flow
# }

@app.get("/", response_class=PlainTextResponse)
def root():
    return "VibeShop is running 🚀 Go to /portal"

@app.get("/portal", response_class=HTMLResponse)
def portal_root():
    portal_path = os.path.join(os.path.dirname(__file__), "..", "portal", "index.html")
    with open(portal_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...), NumMedia: int = Form(0), MediaUrl0: str = Form(None)):
    """
    Main webhook to handle incoming WhatsApp messages.
    Handles image search, product selection, and payment flow.
    """
    user_phone = From.replace("whatsapp:", "")

    # Initialize user state if not exists
    if user_phone not in user_states:
        user_states[user_phone] = {
            "last_results": [],
            "selected_product": None,
            "state": "IDLE"
        }

    user_state = user_states[user_phone]

    # --- SCENARIO 1: User sends an image to search ---
    if NumMedia > 0 and MediaUrl0:
        import requests
        try:
            # Download image from Twilio URL
            response = requests.get(MediaUrl0)
            image_bytes = response.content

            # Search for similar products across all stores
            results, distance = search_products(image_bytes)

            if not results:
                return twilio_message_response("Sorry, I couldn't find any similar products. Try sending a different image.")

            # Store results in user state
            user_state["last_results"] = results
            user_state["state"] = "IDLE"

            # Format results for display
            result_lines = []
            for i, r in enumerate(results):
                result_lines.append(
                    f"{i+1}️⃣ {r['name']}\n"
                    f"💰 {r['price']} UGX\n"
                    f"🏪 {r['store_name']}\n"
                    f"📍 {r['location']}"
                )

            formatted_results = "\n\n".join(result_lines)
            response = f"Here are some matches I found!\n\n{formatted_results}\n\nReply with the number to select a product, or 'PAY' to proceed with payment."
            return twilio_message_response(response)

        except Exception as e:
            print(f"Error processing image: {e}")
            return twilio_message_response("Sorry, there was an error processing your image. Please try again.")

    # --- SCENARIO 2: Handle PAY flow ---
    body = Body.strip()
    normalized_body = body.upper()

    if normalized_body in ["HELP", "START"]:
        return twilio_message_response(whatsapp_help_text())

    if normalized_body == "PAY":
        selected_product = user_state.get("selected_product")
        if not selected_product or not isinstance(selected_product, dict):
            return twilio_message_response("Please select a product first by replying with its number (1, 2, or 3).")

        user_state["state"] = "WAITING_AMOUNT"
        product = selected_product
        product_name = product.get("name", "selected product")
        product_price = product.get("price", "unknown")

        return twilio_message_response(
            f"Great! You selected: {product_name} for {product_price} UGX.\n\nPlease enter the amount you're willing to pay."
        )

    # --- SCENARIO 3: User enters payment amount ---
    if user_state.get("state") == "WAITING_AMOUNT":
        try:
            amount = int(body.replace(',', '').replace('UGX', '').strip())
            if amount <= 0:
                return twilio_message_response("Please enter a valid amount greater than 0.")

            selected_product = user_state.get("selected_product")
            if not selected_product or not isinstance(selected_product, dict):
                user_state["state"] = "IDLE"
                return twilio_message_response("No product selected. Please choose a product first.")

            product = selected_product
            product_id = product.get("product_id")
            store_id = product.get("store_id")

            if product_id is None or store_id is None:
                user_state["state"] = "IDLE"
                user_state["selected_product"] = None
                return twilio_message_response("Selected product is invalid. Please search again and pick a valid option.")

            # Create transaction
            commission, seller_amount, transaction_id = create_transaction(
                product_id,
                store_id,
                user_phone,
                amount,
                f"PAY-{user_phone[-4:]}"  # Simple reference
            )

            if commission is None:
                return twilio_message_response("Sorry, there was an error processing your payment. Please try again.")

            # Process payment
            if FEATURES["ENABLE_USSD_PAYMENT"]:
                # Trigger USSD payment
                payment_result = trigger_ussd_payment(user_phone, amount, f"PAY-{user_phone[-4:]}")

                if not payment_result or payment_result.get("status") != "success":
                    message = payment_result.get("message", "Unknown error") if isinstance(payment_result, dict) else "Unknown error"
                    return twilio_message_response(f"Payment failed: {message}. Please try again or contact support.")

                # Update transaction status
                from .payment_logic import update_transaction_status
                update_transaction_status(f"PAY-{user_phone[-4:]}" , "completed")

                # Reset user state
                user_state["state"] = "IDLE"
                user_state["selected_product"] = None

                return twilio_message_response(
                    f"Payment successful! 🎉\n\nAmount paid: {amount} UGX\nCommission: {commission} UGX\nSeller receives: {seller_amount} UGX\n\nYour seller will be notified automatically."
                )
            else:
                # Fallback: Just show payment details
                user_state["state"] = "IDLE"
                user_state["selected_product"] = None

                return twilio_message_response(
                    f"Payment recorded! 📝\n\nAmount: {amount} UGX\nCommission: {commission} UGX\nSeller receives: {seller_amount} UGX\n\nUSSD payment is disabled in this demo. Contact the seller directly."
                )

        except ValueError:
            return twilio_message_response("Please enter a valid number for the amount (e.g., 25000).")

    # --- SCENARIO 4: User selects a product ---
    if body.isdigit():
        last_results = user_state.get("last_results")
        if not last_results or not isinstance(last_results, list):
            return twilio_message_response("Sorry, I don't have any previous search results for you. Please send an image of what you're looking for.")

        try:
            selected_index = int(body) - 1
            if selected_index < 0 or selected_index >= len(last_results):
                return twilio_message_response("Invalid selection. Please choose a number from the list.")

            selected_product = last_results[selected_index]
            user_state["selected_product"] = selected_product

            lead_result = log_lead_and_get_details(selected_product["product_id"])
            if lead_result:
                lead_id, _, _ = lead_result
                if lead_id is not None:
                    notify_seller_of_lead(lead_id)

            return twilio_message_response(
                f"Selected: {selected_product['name']} for {selected_product['price']} UGX\n\nReply with 'PAY' to proceed with payment, or send another image to search again."
            )
        except (ValueError, IndexError):
            return twilio_message_response("Invalid selection. Please choose a number from the list.")

    # --- Fallback: Unknown command ---
    return twilio_message_response(
        "I didn't understand that. Send an image to search for products, select a product with its number (1-3), or type 'PAY' to proceed with payment. "
        "Type 'HELP' to see the instructions again."
    )

# --- Portal Routes ---

@app.get("/portal/", response_class=HTMLResponse)
def portal_index():
    """Serve the seller portal"""
    portal_path = os.path.join(os.path.dirname(__file__), "..", "portal", "index.html")
    with open(portal_path, "r", encoding="utf-8") as f:
        return f.read()

app.mount("/portal", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "portal")), name="portal")

@app.post("/api/portal/create-store")
def create_store(name: str = Form(...), phone_number: str = Form(...), location: str = Form(...)):
    """Create a new store"""
    try:
        store_code = generate_store_code()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO stores (name, phone_number, location, store_code) VALUES (%s, %s, %s, %s) RETURNING store_id",
            (name, phone_number, location, store_code)
        )
        store_id_row = cur.fetchone()
        if not store_id_row:
            raise ValueError("Failed to create store, no store_id returned from database")
        store_id = store_id_row[0]

        cur.execute(
            "INSERT INTO activity (store_code, action) VALUES (%s, %s)",
            (store_code, "create_store")
        )
        conn.commit()

        cur.close()
        conn.close()

        return {"status": "success", "store_id": store_id, "store_code": store_code, "message": f"Store '{name}' created successfully"}
    except Exception as e:
        error_msg = str(e)
        
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return {
                "status": "error", 
                "message": "Database not available. Please set up PostgreSQL (see DATABASE_SETUP.md) and try again.",
                "help": "https://github.com/vibeshop/DATABASE_SETUP.md"
            }
        
        return {"status": "error", "message": error_msg}

@app.post("/api/portal/upload-product")
def upload_product(
    store_id: Optional[int] = Form(None),
    store_code: Optional[str] = Form(None),
    name: str = Form(...),
    price: int = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(None),
    image_url: Optional[str] = Form(None)
):
    """Upload a product to store"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        if store_id is None:
            if not store_code:
                raise ValueError("Missing store_id or store_code")
            cur.execute("SELECT store_id FROM stores WHERE store_code = %s", (store_code,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Store code not found")
            store_id = row[0]

        cur.execute(
            """
            INSERT INTO products (store_id, name, description, price, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING product_id
            """,
            (store_id, name, description or "", price, image_url or "")
        )
        product_id_row = cur.fetchone()
        if not product_id_row:
            raise ValueError("Failed to upload product, no product_id returned from database")
        product_id = product_id_row[0]

        if not store_code:
            cur.execute("SELECT store_code FROM stores WHERE store_id = %s", (store_id,))
            row = cur.fetchone()
            store_code = row[0] if row else None

        cur.execute(
            "INSERT INTO activity (store_code, action) VALUES (%s, %s)",
            (store_code or "UNKNOWN", "add_product")
        )
        conn.commit()

        cur.close()
        conn.close()

        return {"status": "success", "product": {"id": product_id, "name": name, "price": price}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/portal/products")
def get_store_products(store_id: Optional[int] = None, store_code: Optional[str] = None):
    """Get all products for a store"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        if store_id is None:
            if not store_code:
                raise ValueError("Missing store_id or store_code")
            cur.execute("SELECT store_id FROM stores WHERE store_code = %s", (store_code,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Store code not found")
            store_id = row[0]

        cur.execute(
            """
            SELECT product_id, name, description, price, image_url
            FROM products
            WHERE store_id = %s
            ORDER BY product_id DESC
            """,
            (store_id,)
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        products = []
        for r in rows:
            products.append({
                "product_id": r[0],
                "name": r[1],
                "description": r[2] or "",
                "price": r[3],
                "image_url": r[4] or ""
            })

        return {"status": "success", "products": products}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/store/{store_code}")
def get_store_by_code(store_code: str):
    """Get store details by store_code."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT store_id, name, market, phone_number, location, store_code FROM stores WHERE store_code = %s",
            (store_code,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return {"status": "error", "message": "Store not found"}

        return {
            "status": "success",
            "store": {
                "store_id": row[0],
                "name": row[1],
                "market": row[2],
                "phone_number": row[3],
                "location": row[4],
                "store_code": row[5]
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/admin/activity")
def get_admin_activity():
    """Return activity tracking for stores."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT store_code, action, created_at FROM activity ORDER BY created_at DESC"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        activity = [
            {"store_code": r[0], "action": r[1], "timestamp": r[2].isoformat() if r[2] else None}
            for r in rows
        ]

        return {"status": "success", "activity": activity}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/portal/delete-product")
async def delete_product(body: Dict[str, Any] = Body(...)):
    """Delete a product"""
    try:
        product_id = body.get("product_id")
        if not product_id:
            return {"status": "error", "message": "Missing product_id"}

        conn = get_connection()
        cur = conn.cursor()

        # Delete the product
        cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "Product deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
