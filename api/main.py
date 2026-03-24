
from fastapi import FastAPI, UploadFile, Form
from .search_logic import search_products
from .lead_logic import log_lead_and_get_details

app = FastAPI()

# --- In-Memory State Management (for MVP) ---
# This will store the last search results for each user (identified by phone number)
# Key: user_phone_number (e.g., "+256772123456")
# Value: list of product dictionaries from the last search
user_state = {}

@app.get("/")
def root():
    return {"message": "VibeShop Assistant Running"}


@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...), NumMedia: int = Form(0), MediaUrl0: str = Form(None)):
    """
    Main webhook to handle incoming WhatsApp messages.
    It can handle both image uploads and text messages (for selections).
    """
    user_phone = From.replace("whatsapp:", "")

    # --- SCENARIO 1: User sends an image to search ---
    if NumMedia > 0 and MediaUrl0:
        # In a real app, we would download the image from MediaUrl0
        # For this MVP, we'll assume the user re-uploads the file for simplicity
        # This part of the code would need to be adapted for a live Twilio environment
        # For now, we will simulate the image search part and focus on the handoff
        return {"message": "Image search is not connected in this version. Please reply with 1, 2, or 3 to test the handoff flow."}

    # --- SCENARIO 2: User sends a text message (a selection) ---
    selection = Body.strip()
    if selection in ["1", "2", "3"]:
        last_results = user_state.get(user_phone)
        if not last_results:
            return {"message": "Sorry, I don't have any previous search results for you. Please send an image of what you're looking for."}
        
        try:
            selected_index = int(selection) - 1
            if selected_index >= len(last_results):
                return {"message": "Invalid selection. Please choose a number from the list."}

            selected_product = last_results[selected_index]
            product_id = selected_product["product_id"]

            # Log the lead and generate the WhatsApp link
            whatsapp_link, store_name = log_lead_and_get_details(product_id)

            if not whatsapp_link:
                return {"message": "Sorry, something went wrong. Please try again."}

            # Clear the state for this user after successful handoff
            del user_state[user_phone]

            response_message = f"Great choice! Chat with {store_name} directly on WhatsApp to finalize your purchase:\n\n{whatsapp_link}"
            return {"message": response_message}

        except (ValueError, IndexError):
            return {"message": "Invalid selection. Please choose a number from the list."}

    # --- Fallback for other text messages ---
    # This is a simulation of a search result to test the handoff flow
    # In a real scenario, this would be populated by an actual image search
    sample_results = [
        {'product_id': 1, 'product_name': 'Blue Denim Jacket', 'price': 45000, 'store_name': 'Owino Denim House', 'location': 'Owino Market, Kampala'},
        {'product_id': 2, 'product_name': 'Black Denim Jacket', 'price': 48000, 'store_name': 'Owino Denim House', 'location': 'Owino Market, Kampala'},
        {'product_id': 5, 'product_name': 'Black Street Hoodie', 'price': 35000, 'store_name': 'StreetWear Owino', 'location': 'Owino Market, Kampala'}
    ]
    user_state[user_phone] = sample_results

    # Format the results for display
    result_lines = []
    for i, r in enumerate(sample_results):
        result_lines.append(
            f"{i+1}️⃣ {r['product_name']}\n"
            f"💰 {r['price']} UGX\n"
            f"🏪 {r['store_name']}\n"
            f"📍 {r['location']}"
        )
    
    formatted_results = "\n\n".join(result_lines)
    response = f"Here are some matches we found!\n\n{formatted_results}\n\nReply with the number to chat with the seller."
    return {"message": response}