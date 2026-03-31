import random
import string
from urllib.parse import quote
from .db_utils import get_connection

def generate_reference_code():
    """Generates a random 3-digit reference code prefixed with 'VS'."""
    number = ''.join(random.choices(string.digits, k=3))
    return f"VS{number}"

def log_lead_and_get_details(product_id: int):
    """
    Logs a lead in the database, generates a reference code,
    and fetches the necessary details to create a WhatsApp chat link.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Fetch product and store details in one go
    query = """
    SELECT 
        p.name AS product_name,
        p.price,
        s.name AS store_name,
        s.phone_number,
        p.store_id
    FROM products p
    JOIN stores s ON p.store_id = s.store_id
    WHERE p.product_id = %s;
    """
    cur.execute(query, (product_id,))
    details = cur.fetchone()

    if not details:
        cur.close()
        conn.close()
        return None, None

    product_name, price, store_name, phone_number, store_id = details
    
    # Generate reference code and log the lead
    ref_code = generate_reference_code()
    cur.execute(
        "INSERT INTO leads (product_id, store_id, reference_code) VALUES (%s, %s, %s)",
        (product_id, store_id, ref_code)
    )
    conn.commit()
    
    cur.close()
    conn.close()

    # Create the pre-filled WhatsApp message
    message = (
        f"Hello, I saw this {product_name} ({price} UGX) on VibeShop "
        f"[{ref_code}]. Is it available?"
    )
    
    # URL-encode the message
    encoded_message = quote(message)
    
    # Generate the final WhatsApp link
    whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"
    
    return whatsapp_link, store_name
