from api.config import FEATURES

def trigger_ussd_payment(phone: str, amount: int, reference: str):
    """
    Trigger USSD payment for the given phone number and amount.
    This is feature-flagged and returns appropriate responses.
    """
    if not FEATURES["ENABLE_USSD_PAYMENT"]:
        return {
            "status": "disabled",
            "message": "USSD payment is disabled in this demo"
        }

    try:
        print(f"USSD Payment Triggered:")
        print(f"Phone: {phone}")
        print(f"Amount: {amount} UGX")
        print(f"Reference: {reference}")

        # Simulate USSD push
        # In production, this would integrate with MTN/Airtel USSD APIs

        # For demo purposes, assume payment succeeds
        return {
            "status": "success",
            "message": "USSD payment initiated successfully",
            "reference": reference
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"USSD payment failed: {str(e)}"
        }
