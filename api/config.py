# Config
FEATURES = {
    "ENABLE_CHAT_HANDOFF": True,
    "ENABLE_MARKET_FALLBACK": False,
    "ENABLE_USSD_PAYMENT": True,  # Activated for live testing
    "ENABLE_COMMISSION": True,
    "ENABLE_SELLER_NOTIFICATIONS": True  # Activated for live testing
}

# Default store ID for MVP (single-tenant mode)
# In production, this would be mapped from WhatsApp number
DEFAULT_STORE_ID = 1

