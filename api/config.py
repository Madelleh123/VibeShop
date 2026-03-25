# VibeShop Assistant Feature Flags
# This file controls the activation of various features in the system.

FEATURES = {
    # Enables the WhatsApp chat handoff flow after a user makes a selection.
    # If False, the flow would stop after showing search results.
    "ENABLE_CHAT_HANDOFF": True,

    # If True and no direct matches are found, the system could potentially
    # search for items in the same market as a fallback. (Future feature)
    "ENABLE_MARKET_FALLBACK": False,

    # Enables the USSD payment flow. If True, instead of a chat link,
    # the user will be prompted to complete a payment.
    "ENABLE_USSD_PAYMENT": False,

    # Enables commission calculation and logging. This should be enabled
    # along with ENABLE_USSD_PAYMENT for the full payment flow.
    "ENABLE_COMMISSION": False
}