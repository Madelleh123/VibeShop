from .db_utils import get_connection

# --- Commission Configuration ---
COMMISSION_RATE = 0.05  # 5%

def calculate_commission(amount: int):
    """
    Calculates the commission and the final amount for the seller.
    """
    commission = int(amount * COMMISSION_RATE)
    seller_amount = amount - commission
    return commission, seller_amount

# --- Transaction Logic ---

def create_transaction(product_id: int, store_id: int, buyer_phone: str, amount: int, reference: str):
    """
    Creates a new transaction record in the database with a 'pending' status
    and returns the calculated commission and seller amount.
    """
    commission, seller_amount = calculate_commission(amount)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO transactions 
            (product_id, store_id, buyer_phone, amount, commission, seller_amount, status, reference_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (product_id, store_id, buyer_phone, amount, commission, seller_amount, "pending", reference)
        )
        conn.commit()
        print(f"Successfully created transaction {reference} for product {product_id}.")
    except Exception as e:
        print(f"Error creating transaction: {e}")
        conn.rollback()
        # If the transaction fails, we should not proceed with the payment.
        return None, None
    finally:
        cur.close()
        conn.close()
        
    return commission, seller_amount