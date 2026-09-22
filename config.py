# Copy this file to config.py and set your local values.

# Device
DEVICE_SERIAL = ""
REMOTE_VIDEO_PATH = "/sdcard/rcs_demo.mp4"
LOCAL_OUTPUT_DIR = "./output"
MAX_RECORD_SECONDS = 120

# Messages App
MESSAGES_PACKAGE = "com.google.android.apps.messaging"
MESSAGES_ACTIVITY = "com.google.android.apps.messaging.ui.ConversationListActivity"

# Samsung Messages:
# MESSAGES_PACKAGE = "com.samsung.android.messaging"
# MESSAGES_ACTIVITY = "com.samsung.android.messaging.ui.ConversationListActivity"

# Vonage API
VONAGE_APPLICATION_ID = "ac01bba6-cc6d-476b-9546-5d7dfcd3c716"
VONAGE_PRIVATE_KEY_PATH = "./private.key"
VONAGE_FROM_RCS = "mbapi_demo"
AGENT_DISPLAY_NAME = "Magenta Business API DEMO"

# Country code plus phone number, without a leading '+'
TARGET_PHONE = "4915568421774"

# Delays in seconds
WAIT_APP_OPEN = 3
WAIT_MESSAGE_ARRIVE = 8
WAIT_AFTER_TAP = 3
WAIT_SCROLL = 1

# OPT-IN flow
OPTIN_TEXT = "Hallo! Möchten Sie exklusive Angebote und Updates von uns erhalten? Sie haben jederzeit die möglichket der Abmeldung mit dem senden von 'STOP'."

OPTIN_BUTTONS = [
    {"text": "Ja, ich bin dabei!", "postbackData": "OPTIN_YES"},
    {"text": "Nein danke",         "postbackData": "OPTIN_NO"},
]

# Which button should be tapped automatically?
OPTIN_TAP_BUTTON = "Ja, ich bin dabei!"

# ── Marketing message ─────────────────────────────────────────────────────────
MARKETING_TITLE       = "Exklusiv fuer Sie: 20% Rabatt!"
MARKETING_DESCRIPTION = "Nur heute: Sparen Sie 20% auf alle Produkte außer Tiernahrung. Jetzt Angebot sichern!"
MARKETING_IMAGE_URL  = "https://www.froelichundkaufmann.de/out/pictures/ddmedia/fuk_kategorie_header_20-prozent_1.jpg"

MARKETING_BUTTONS = [
    # With "url" → URL action button (opens browser)
    {"text": "Mehr erfahren",    "postbackData": "LEARN_MORE", "url": "https://www.vonage.com"},
    # Without "url" → quick reply button
    {"text": "Angebot ablehnen", "postbackData": "DECLINE"},
]

# Which button should be tapped automatically?
MARKETING_TAP_BUTTON = "Mehr erfahren"

# ── OPT-OUT flow ───────────────────────────────────────────────────────────────
# Keyword that the phone sends first into the chat to trigger opt-out
OPTOUT_KEYWORD = "stop"

OPTOUT_TEXT = "Möchten Sie sich abmelden und keine Nachrichten mehr erhalten? Sie können sich jederzeit erneut anmelden, indem Sie 'START' senden."

OPTOUT_BUTTONS = [
    {"text": "Abmelden",           "postbackData": "OPTOUT_YES"},
    {"text": "Angemeldet bleiben", "postbackData": "OPTOUT_NO"},
]

# Which button should be tapped automatically?
OPTOUT_TAP_BUTTON = "Abmelden"