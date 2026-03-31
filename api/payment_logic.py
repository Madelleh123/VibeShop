from .db_utils import get_connection
from .notification_logic import notify_seller_of_payment

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
            RETURNING id
            """,
            (product_id, store_id, buyer_phone, amount, commission, seller_amount, "pending", reference)
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Failed to insert transaction, no row returned")

        transaction_id = row[0]
        conn.commit()
        print(f"Successfully created transaction {reference} (ID: {transaction_id}) for product {product_id}.")
        return commission, seller_amount, transaction_id
    except Exception as e:
        print(f"Error creating transaction: {e}")
        conn.rollback()
        return None, None, None
    finally:
        cur.close()
        conn.close()

def update_transaction_status(reference: str, status: str):
    """
    Update transaction status and notify seller if completed.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE transactions SET status = %s WHERE reference_code = %s RETURNING id",
            (status, reference)
        )
        result = cur.fetchone()
        conn.commit()

        if result and status == "completed":
            transaction_id = result[0]
            notify_seller_of_payment(transaction_id)

        return result is not None
    except Exception as e:
        print(f"Error updating transaction status: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_transaction_details(reference: str):
    """
    Get transaction details by reference code.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT t.id, t.amount, t.commission, t.seller_amount, t.status,
                   p.name as product_name, s.name as store_name
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN stores s ON t.store_id = s.store_id
            WHERE t.reference_code = %s
        """, (reference,))

        return cur.fetchone()
    except Exception as e:
        print(f"Error getting transaction details: {e}")
        return None
    finally:
        cur.close()
        conn.close()
