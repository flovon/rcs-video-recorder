# config.py — Edit this file before running any script

# ── Device ────────────────────────────────────────────────────────────────────
# ADB device serial (leave empty to use the first detected device)
# Run `adb devices` to find your serial, e.g. "R58M41XXXXX"
DEVICE_SERIAL = ""

# Path on the device where the recording is stored temporarily
REMOTE_VIDEO_PATH = "/sdcard/rcs_demo.mp4"

# Local output directory on your Mac/PC
LOCAL_OUTPUT_DIR = "./output"

# Maximum recording duration in seconds (ADB hard limit: 180)
MAX_RECORD_SECONDS = 120

# ── Messages App ──────────────────────────────────────────────────────────────
# Google Messages (default on Pixel and most Android devices):
MESSAGES_PACKAGE  = "com.google.android.apps.messaging"
MESSAGES_ACTIVITY = "com.google.android.apps.messaging.ui.ConversationListActivity"

# Samsung Messages (use these instead on Samsung devices):
# MESSAGES_PACKAGE  = "com.samsung.android.messaging"
# MESSAGES_ACTIVITY = "com.samsung.android.messaging.ui.ConversationListActivity"

# ── Vonage API ────────────────────────────────────────────────────────────────
VONAGE_API_KEY    = "YOUR_API_KEY"
VONAGE_API_SECRET = "YOUR_API_SECRET"

# Technical sender ID used in API calls (e.g. "mbapi_demo")
VONAGE_FROM_RCS = "YOUR_RCS_SENDER_ID"

# Display name shown in the Messages app — may differ from the sender ID!
# Run `python3 debug_ui.py` with the Messages app open to find the exact name.
AGENT_DISPLAY_NAME = "YOUR_AGENT_DISPLAY_NAME"

# Destination phone number including country code (e.g. "+15551234567")
TARGET_PHONE = "+1XXXXXXXXXX"

# ── Timing (seconds) ──────────────────────────────────────────────────────────
WAIT_APP_OPEN       = 3   # After launching the Messages app
WAIT_MESSAGE_ARRIVE = 8   # Time to wait for an incoming message to appear
WAIT_AFTER_TAP      = 3   # Pause after tapping a button
WAIT_SCROLL         = 1   # After a scroll gesture

# ── Opt-In Flow ───────────────────────────────────────────────────────────────
OPTIN_TEXT = "Hi! Would you like to receive exclusive offers and updates from us?"

OPTIN_BUTTONS = [
    {"text": "Yes, sign me up!", "postbackData": "OPTIN_YES"},
    {"text": "No thanks",        "postbackData": "OPTIN_NO"},
]

# Which button should the script tap automatically?
OPTIN_TAP_BUTTON = "Yes, sign me up!"

# ── Marketing Message (Rich Card) ─────────────────────────────────────────────
MARKETING_TITLE       = "Exclusive offer: 20% off!"
MARKETING_DESCRIPTION = "Today only: save 20% on all products. Grab your deal now!"

# Publicly reachable HTTPS image URL for the Rich Card (min. 600x400 px)
MARKETING_IMAGE_URL = "https://your-domain.com/banner.jpg"

MARKETING_BUTTONS = [
    # Button WITH "url" → rendered as a URL-action button (opens browser)
    {"text": "Learn more",    "postbackData": "LEARN_MORE", "url": "https://www.vonage.com"},
    # Button WITHOUT "url" → rendered as a quick-reply button
    {"text": "Decline offer", "postbackData": "DECLINE"},
]

# Which button should the script tap automatically?
MARKETING_TAP_BUTTON = "Learn more"

# ── Opt-Out Flow ──────────────────────────────────────────────────────────────
# Keyword the script types and SENDS from the phone to trigger the opt-out
OPTOUT_KEYWORD = "stop"

OPTOUT_TEXT = "Would you like to unsubscribe and stop receiving messages?"

OPTOUT_BUTTONS = [
    {"text": "Unsubscribe",  "postbackData": "OPTOUT_YES"},
    {"text": "Stay subscribed", "postbackData": "OPTOUT_NO"},
]

# Which button should the script tap automatically?
OPTOUT_TAP_BUTTON = "Unsubscribe"
