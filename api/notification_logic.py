from .db_utils import get_connection
from .config import FEATURES

def notify_seller_of_payment(transaction_id: int):
    """
    Notify seller of successful payment.
    This is prepared but NOT activated in MVP.
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

        # TODO: Send WhatsApp message to seller
        # This would integrate with WhatsApp Business API
        print(f"NOTIFICATION TO {seller_phone}: {message}")

    except Exception as e:
        print(f"Error sending seller notification: {e}")

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

        # TODO: Send WhatsApp message to seller
        print(f"LEAD NOTIFICATION TO {seller_phone}: {message}")

    except Exception as e:
        print(f"Error sending lead notification: {e}")