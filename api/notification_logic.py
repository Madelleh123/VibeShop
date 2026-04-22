import os
from urllib.parse import quote

import requests
from .db_utils import get_connection
from .config import FEATURES

def notify_seller_of_payment(transaction_id: int):
    """
    Notify seller of successful payment.
    Sends a WhatsApp notification via Twilio when credentials are configured,
    otherwise logs the notification message for manual follow-up.
    """
    if not FEATURES.get("ENABLE_SELLER_NOTIFICATIONS", False):
        print(f"Seller notification disabled. Transaction {transaction_id} completed.")
        return

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get transaction details
        cur.execute("""
            SELECT t.amount, t.commission, t.seller_amount, t.reference_code,
                   p.name as product_name, s.name as store_name, s.phone_number
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN stores s ON t.store_id = s.store_id
            WHERE t.id = %s
        """, (transaction_id,))

        details = cur.fetchone()
        cur.close()
        conn.close()

        if not details:
            print(f"Transaction {transaction_id} not found for notification")
            return

        amount, commission, seller_amount, reference, product_name, store_name, seller_phone = details

        # Build notification message
        message = f"""🔔 NEW PAYMENT RECEIVED!

Product: {product_name}
Amount Paid: {amount} UGX
Commission: {commission} UGX
You Receive: {seller_amount} UGX
Reference: {reference}

Please prepare the item for pickup/delivery."""

        if not send_whatsapp_message(seller_phone, message):
            print(f"NOTIFICATION TO {seller_phone}: {message}")

    except Exception as e:
        print(f"Error sending seller notification: {e}")

def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """Try to send a WhatsApp message using Twilio if environment variables are provided."""
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_WHATSAPP_FROM")

    if not twilio_sid or not twilio_token or not twilio_from:
        return False

    whatsapp_to = phone_number if phone_number.startswith("whatsapp:") else f"whatsapp:{phone_number}"
    whatsapp_from = twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"

    payload = {
        "From": whatsapp_from,
        "To": whatsapp_to,
        "Body": message
    }

    try:
        response = requests.post(url, data=payload, auth=(twilio_sid, twilio_token), timeout=15)
        if response.status_code >= 400:
            print(f"Twilio WhatsApp send failed ({response.status_code}): {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message via Twilio: {e}")
        return False
def notify_seller_of_lead(lead_id: int):
    """
    Notify seller of new lead (when user selects product but hasn't paid yet).
    """
    if not FEATURES.get("ENABLE_SELLER_NOTIFICATIONS", False):
        return

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT p.name as product_name, s.name as store_name, s.phone_number, l.reference_code
            FROM leads l
            JOIN products p ON l.product_id = p.product_id
            JOIN stores s ON l.store_id = s.store_id
            WHERE l.id = %s
        """, (lead_id,))

        details = cur.fetchone()
        cur.close()
        conn.close()

        if not details:
            return

        product_name, store_name, seller_phone, reference = details

        message = f"""🔔 NEW CUSTOMER INTEREST!

Product: {product_name}
Reference: {reference}

A customer is interested in this product. They may contact you soon."""

        if not send_whatsapp_message(seller_phone, message):
            print(f"LEAD NOTIFICATION TO {seller_phone}: {message}")

    except Exception as e:
        print(f"Error sending lead notification: {e}")