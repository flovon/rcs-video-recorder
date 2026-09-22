# Vonage RCS Video Recorder

Automated toolset for recording RCS demo videos on an Android device via USB/ADB. Produces a complete screen recording of the Opt-In, Marketing and Opt-Out flows for the RCS Agent Review process.

---

## Prerequisites

- Android device with **USB Debugging** enabled
- **ADB** installed on your Mac/PC
- **Python 3.9+**
- Vonage account with an RCS-capable agent

---

## Installation

```bash
# 1. Install ADB (Mac)
brew install android-platform-tools

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install requests
```

> The `venv` must be re-activated in every new terminal window:
> ```bash
> source venv/bin/activate
> ```

---

## Android Device Setup

1. **Enable Developer Options:**
   `Settings → About phone → Build number` (tap 7 times)

2. **Enable USB Debugging:**
   `Developer options → USB Debugging → On`

3. **Connect via USB**, select "File Transfer" mode and confirm the trust dialog on the phone.

4. **Verify the connection:**
   ```bash
   adb devices
   # Expected output:  R58M41XXXXX   device
   ```

5. **Disable the screen lock** (recommended) so the script can reliably unlock the screen.

---

## Configuration

All settings live in `config.py`. Fill it in before running any script.

### Device & Paths

| Variable | Description |
|---|---|
| `DEVICE_SERIAL` | ADB serial of the device (empty = first detected device) |
| `LOCAL_OUTPUT_DIR` | Local folder for the finished video (e.g. `./output`) |
| `MAX_RECORD_SECONDS` | Max recording duration in seconds (ADB hard limit: **180**) |
| `MESSAGES_PACKAGE` | Package name of the Messages app (Google or Samsung, see below) |

```python
# Google Messages (Pixel & most Android devices):
MESSAGES_PACKAGE  = "com.google.android.apps.messaging"
MESSAGES_ACTIVITY = "com.google.android.apps.messaging.ui.ConversationListActivity"

# Samsung Messages:
MESSAGES_PACKAGE  = "com.samsung.android.messaging"
MESSAGES_ACTIVITY = "com.samsung.android.messaging.ui.ConversationListActivity"
```

### Vonage API

| Variable | Description |
|---|---|
| `VONAGE_API_KEY` | Vonage API Key |
| `VONAGE_API_SECRET` | Vonage API Secret |
| `VONAGE_FROM_RCS` | Technical sender ID of the RCS agent (e.g. `mbapi_demo`) |
| `AGENT_DISPLAY_NAME` | Name as shown in the Messages app — **may differ from the sender ID!** |
| `TARGET_PHONE` | Destination phone number with country code (e.g. `+15551234567`) |
| `MARKETING_IMAGE_URL` | Publicly reachable HTTPS image URL for the Rich Card (min. 600×400 px) |

> **Finding `AGENT_DISPLAY_NAME`:** run `python3 debug_ui.py` with the Messages app open — all visible UI texts will be printed.

### Demo Content (fully customisable)

All message texts and buttons are defined in `config.py`. `record_rcs_demo.py` contains no hardcoded content.

**Opt-In flow:**
```python
OPTIN_TEXT       = "Hi! Would you like to receive exclusive offers from us?"
OPTIN_BUTTONS    = [
    {"text": "Yes, sign me up!", "postbackData": "OPTIN_YES"},
    {"text": "No thanks",        "postbackData": "OPTIN_NO"},
]
OPTIN_TAP_BUTTON = "Yes, sign me up!"   # This button is tapped automatically
```

**Marketing message (Rich Card):**
```python
MARKETING_TITLE       = "Exclusive offer: 20% off!"
MARKETING_DESCRIPTION = "Today only: save 20% on all products."
MARKETING_BUTTONS     = [
    {"text": "Learn more",    "postbackData": "LEARN_MORE", "url": "https://..."},  # URL button
    {"text": "Decline offer", "postbackData": "DECLINE"},                           # Quick Reply
]
MARKETING_TAP_BUTTON  = "Learn more"
```

> Buttons **with** `"url"` are rendered as URL-action buttons (open browser).
> Buttons **without** `"url"` are rendered as quick-reply buttons.

**Opt-Out flow:**
```python
OPTOUT_KEYWORD    = "stop"              # Typed and sent from the phone
OPTOUT_TEXT       = "Would you like to unsubscribe?"
OPTOUT_BUTTONS    = [
    {"text": "Unsubscribe",     "postbackData": "OPTOUT_YES"},
    {"text": "Stay subscribed", "postbackData": "OPTOUT_NO"},
]
OPTOUT_TAP_BUTTON = "Unsubscribe"
```

### Timing

```python
WAIT_APP_OPEN       = 3   # Seconds after launching the app
WAIT_MESSAGE_ARRIVE = 8   # Seconds to wait for an incoming message
WAIT_AFTER_TAP      = 3   # Seconds after tapping a button
```

---

## Scripts

### `record_rcs_demo.py` — Record the demo video

Records the complete Opt-In → Marketing → Opt-Out flow.

```bash
# Send API messages + record + interact:
python3 record_rcs_demo.py --trigger

# Record only (messages triggered externally):
python3 record_rcs_demo.py --no-trigger
```

**Flow steps:**

| Step | Action |
|---|---|
| 1 | Unlock screen |
| 2 | Open Messages app |
| 3 | Start screen recording |
| 4 | **Opt-In:** send message with reply buttons → tap configured button |
| 5 | **Marketing:** send Rich Card with URL + quick-reply button → tap URL button → return to app |
| 6 | **Opt-Out:** type `OPTOUT_KEYWORD` from phone → bot replies → tap Unsubscribe button |
| 7 | Stop recording → pull video to computer → kill Messages app |

**Output:** `./output/rcs_demo_YYYYMMDD_HHMMSS.mp4`

---

### `add_rcs_tester.py` — Register device as RCS tester

Opens the **RBM Tester Manager** conversation and taps "Make me a tester" automatically.

```bash
python3 add_rcs_tester.py

# With a specific device and longer timeout:
python3 add_rcs_tester.py --serial R58M41XXXXX --timeout 60
```

> Run this **after** the tester invitation has been sent from the RBM Developer Console.

---

### `debug_ui.py` — Print all visible UI texts

Dumps all UI element texts from the current screen. Useful for finding the correct `AGENT_DISPLAY_NAME` or button labels.

```bash
# Open the Messages app first, then:
python3 debug_ui.py
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `No ADB device found` | Check USB Debugging; run `adb kill-server && adb start-server` |
| Conversation / button not found | Increase `WAIT_MESSAGE_ARRIVE`; run `debug_ui.py` to verify names |
| Wrong agent name | Check `AGENT_DISPLAY_NAME` with `debug_ui.py` — must match exactly |
| Samsung device | Set `MESSAGES_PACKAGE` / `MESSAGES_ACTIVITY` to the Samsung values in `config.py` |
| Screen stays locked | Disable the screen lock on the device |
| Recording stops after 3 min | ADB limit: `MAX_RECORD_SECONDS` must be ≤ 180 |
| `type_and_send` types in wrong field | Run `debug_ui.py` and check the `resource-id` of the compose field |

**Inspect the UI dump manually:**
```bash
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml .
# Open ui.xml in a browser or Android Studio (UI Automator Viewer)
```

---

## Post-processing

Trim individual flows with `ffmpeg`:

```bash
ffmpeg -i rcs_demo.mp4 -ss 00:00:05 -to 00:00:35 -c copy clip_optin.mp4
ffmpeg -i rcs_demo.mp4 -ss 00:00:38 -to 00:01:10 -c copy clip_marketing.mp4
ffmpeg -i rcs_demo.mp4 -ss 00:01:15 -to 00:01:45 -c copy clip_optout.mp4
```
