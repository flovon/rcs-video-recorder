#!/usr/bin/env python3
"""
record_rcs_demo.py
------------------
Automated RCS demo video recorder for the Vonage RCS Agent Review process.
<<<<<<< HEAD
=======
Uses the Vonage Python SDK v4 with JWT authentication.
>>>>>>> 7e42969 (Lokalen Projektstand sichern)

Flow:
  1. Unlock screen
  2. Open Messages app
  3. Start screen recording
  4. Opt-In:    send message + reply buttons → tap configured button
  5. Marketing: send Rich Card               → tap configured button → return to app
  6. Opt-Out:   type keyword from phone      → bot replies with buttons → tap configured button
  7. Stop recording → pull video to computer → kill Messages app

Usage:
  python3 record_rcs_demo.py --trigger      # Send API messages + record + interact
  python3 record_rcs_demo.py --no-trigger   # Record only (trigger messages externally)
"""

import argparse
import time
import os
import datetime
<<<<<<< HEAD
import requests
=======

from vonage import Vonage, Auth
from vonage_messages import RcsCustom, RcsText
>>>>>>> 7e42969 (Lokalen Projektstand sichern)

import config
from adb_helper import (
    get_device_serial, start_screenrecord, stop_screenrecord,
    pull_video, open_messages_app, tap, unlock_screen, dump_ui,
    get_screen_size, type_and_send, _adb,
)
from ui_helper import find_element_by_text


<<<<<<< HEAD
# ── Vonage Messages API ───────────────────────────────────────────────────────

def vonage_send_rcs(text=None, suggestions=None, rich_card=None):
    """Send an RCS message via the Vonage Messages API."""
    base = {
        "from": config.VONAGE_FROM_RCS,
        "to":   config.TARGET_PHONE,
        "channel": "rcs",
    }

    if rich_card:
        def _build_suggestion(b):
            if b.get("url"):
                return {"action": {
                    "text": b["text"],
                    "postbackData": b["postbackData"],
                    "openUrlAction": {"url": b["url"]},
                }}
            return {"reply": {
                "text": b["text"],
                "postbackData": b["postbackData"],
            }}

        payload = {**base, "message_type": "custom", "custom": {
=======
# ── Vonage SDK client (JWT) ───────────────────────────────────────────────────

def _get_vonage_client() -> Vonage:
    """
    Initialise and return a Vonage client using JWT authentication.
    Authenticates via Application ID + Private Key — no API key/secret needed.
    """
    auth = Auth(
        application_id=config.VONAGE_APPLICATION_ID,
        private_key=config.VONAGE_PRIVATE_KEY_PATH,
    )
    return Vonage(auth=auth)


# ── RCS message helpers ───────────────────────────────────────────────────────

def _build_suggestion(b: dict) -> dict:
    """
    Convert a button dict from config into an RCS suggestion object.
    Buttons with "url" become URL-action buttons; others become quick-replies.
    """
    if b.get("url"):
        return {
            "action": {
                "text": b["text"],
                "postbackData": b["postbackData"],
                "openUrlAction": {"url": b["url"]},
            }
        }
    return {
        "reply": {
            "text": b["text"],
            "postbackData": b["postbackData"],
        }
    }


def vonage_send_rcs(client: Vonage,
                    text: str | None = None,
                    suggestions: list | None = None,
                    rich_card: dict | None = None) -> dict:
    """
    Send an RCS message using the Vonage SDK (JWT auth).

    - Plain text:           pass text only
    - Text + reply buttons: pass text + suggestions
    - Rich Card:            pass rich_card dict with title/description/imageUrl/buttons
    """

    if rich_card:
        # Standalone Rich Card with mixed button types
        custom_payload = {
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
            "contentMessage": {
                "richCard": {
                    "standaloneCard": {
                        "thumbnailImageAlignment": "RIGHT",
                        "cardOrientation": "VERTICAL",
                        "cardContent": {
                            "title":       rich_card["title"],
                            "description": rich_card["description"],
                            "media": {
                                "height": "MEDIUM",
                                "contentInfo": {"fileUrl": rich_card["imageUrl"]},
                            },
                            "suggestions": [_build_suggestion(b)
                                            for b in rich_card.get("buttons", [])],
                        },
                    }
                }
            }
<<<<<<< HEAD
        }}

    elif suggestions:
        payload = {**base, "message_type": "custom", "custom": {
            "contentMessage": {
                "text": text,
                "suggestions": [
                    {"reply": {"text": s["text"], "postbackData": s["postbackData"]}}
                    for s in suggestions
                ],
            }
        }}

    else:
        payload = {**base, "message_type": "text", "text": text}

    resp = requests.post(
        "https://api.nexmo.com/v1/messages",
        json=payload,
        auth=(config.VONAGE_API_KEY, config.VONAGE_API_SECRET),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    label = text or (rich_card or {}).get("title", "RichCard")
    print(f"  [API] Sent: {str(label)[:60]}")
    return resp.json()
=======
        }
        message = RcsCustom(
            from_=config.VONAGE_FROM_RCS,
            to=config.TARGET_PHONE,
            custom=custom_payload,
        )

    elif suggestions:
        # Text message with suggested reply buttons
        custom_payload = {
            "contentMessage": {
                "text": text,
                "suggestions": [_build_suggestion(s) for s in suggestions],
            }
        }
        message = RcsCustom(
            from_=config.VONAGE_FROM_RCS,
            to=config.TARGET_PHONE,
            custom=custom_payload,
        )

    else:
        # Plain text RCS message
        message = RcsText(
            from_=config.VONAGE_FROM_RCS,
            to=config.TARGET_PHONE,
            text=text,
        )

    response = client.messages.send(message)
    label = text or (rich_card or {}).get("title", "RichCard")
    print(f"  [API] Sent (JWT): {str(label)[:60]}")
    return response
>>>>>>> 7e42969 (Lokalen Projektstand sichern)


# ── UI helpers ────────────────────────────────────────────────────────────────

<<<<<<< HEAD
def wait_and_tap(serial, button_text, timeout=20, interval=2.0) -> bool:
=======
def wait_and_tap(serial: str, button_text: str,
                 timeout: int = 20, interval: float = 2.0) -> bool:
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
    """Poll the UI until button_text appears, then tap it."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xml  = dump_ui(serial)
        elem = find_element_by_text(xml, button_text)
        if elem:
            print(f"  [UI] Tapping '{button_text}' @ ({elem['x']},{elem['y']})")
            tap(serial, elem["x"], elem["y"])
            return True
        print(f"  [UI] Waiting for '{button_text}'...")
        time.sleep(interval)
    print(f"  [UI] Warning: '{button_text}' not found after {timeout}s")
    return False


<<<<<<< HEAD
def open_conversation(serial, sender_name, timeout=20) -> bool:
=======
def open_conversation(serial: str, sender_name: str, timeout: int = 20) -> bool:
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
    """Open the conversation thread with the given sender name."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xml  = dump_ui(serial)
        elem = find_element_by_text(xml, sender_name)
        if elem:
            print(f"  [UI] Opening conversation '{sender_name}'")
            tap(serial, elem["x"], elem["y"])
            time.sleep(2)
            return True
        time.sleep(2)
    print(f"  [UI] Warning: conversation '{sender_name}' not found")
    return False


# ── Main flow ─────────────────────────────────────────────────────────────────

def run_demo(trigger_api: bool = True):
    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_path = f"/sdcard/rcs_demo_{timestamp}.mp4"

    print("=" * 60)
    print("  RCS Demo Video Recorder — Vonage")
    print("=" * 60)

<<<<<<< HEAD
=======
    # Initialise Vonage SDK client once (JWT is generated on first request)
    client = _get_vonage_client() if trigger_api else None
    if client:
        print(f"[OK] Vonage SDK ready (App ID: {config.VONAGE_APPLICATION_ID})")

>>>>>>> 7e42969 (Lokalen Projektstand sichern)
    serial = get_device_serial(config.DEVICE_SERIAL)
    w, h   = get_screen_size(serial)
    print(f"[OK] Device: {serial}  |  Resolution: {w}x{h}")

    print("\n[1/7] Unlocking screen...")
    unlock_screen(serial)

    print("[2/7] Opening Messages app...")
    open_messages_app(serial, config.MESSAGES_PACKAGE, config.MESSAGES_ACTIVITY)
    time.sleep(config.WAIT_APP_OPEN)

    print("[3/7] Starting screen recording...")
    rec_thread, rec_stop = start_screenrecord(serial, remote_path,
                                               config.MAX_RECORD_SECONDS)
    print(f"  Device path: {remote_path}")

    try:
        # ── OPT-IN ───────────────────────────────────────────────────────
        print("\n[4/7] Opt-In flow...")
        if trigger_api:
            vonage_send_rcs(
<<<<<<< HEAD
=======
                client,
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
                text=config.OPTIN_TEXT,
                suggestions=config.OPTIN_BUTTONS,
            )

        time.sleep(config.WAIT_MESSAGE_ARRIVE)
        open_conversation(serial, config.AGENT_DISPLAY_NAME)
        time.sleep(2)
        wait_and_tap(serial, config.OPTIN_TAP_BUTTON, timeout=15)
        time.sleep(config.WAIT_AFTER_TAP)

        # ── MARKETING MESSAGE ─────────────────────────────────────────────
        print("\n[5/7] Marketing message flow...")
        if trigger_api:
            vonage_send_rcs(
<<<<<<< HEAD
=======
                client,
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
                rich_card={
                    "title":       config.MARKETING_TITLE,
                    "description": config.MARKETING_DESCRIPTION,
                    "imageUrl":    config.MARKETING_IMAGE_URL,
                    "buttons":     config.MARKETING_BUTTONS,
<<<<<<< HEAD
                }
=======
                },
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
            )

        time.sleep(config.WAIT_MESSAGE_ARRIVE)
        wait_and_tap(serial, config.MARKETING_TAP_BUTTON, timeout=15)
        time.sleep(config.WAIT_AFTER_TAP)

        # Return to Messages app (browser may have opened)
        open_messages_app(serial, config.MESSAGES_PACKAGE, config.MESSAGES_ACTIVITY)
        time.sleep(config.WAIT_APP_OPEN)
        open_conversation(serial, config.AGENT_DISPLAY_NAME)
        time.sleep(2)

        # ── OPT-OUT ───────────────────────────────────────────────────────
        print("\n[6/7] Opt-Out flow...")

        # Step 1: phone types and sends the opt-out keyword (e.g. "stop")
        print(f"  Sending keyword '{config.OPTOUT_KEYWORD}' from the phone...")
        type_and_send(serial, config.OPTOUT_KEYWORD)
        time.sleep(config.WAIT_MESSAGE_ARRIVE)

<<<<<<< HEAD
        # Step 2: bot replies with the opt-out message and buttons
        if trigger_api:
            vonage_send_rcs(
=======
        # Step 2: bot replies with the opt-out confirmation message + buttons
        if trigger_api:
            vonage_send_rcs(
                client,
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
                text=config.OPTOUT_TEXT,
                suggestions=config.OPTOUT_BUTTONS,
            )

        time.sleep(config.WAIT_MESSAGE_ARRIVE)
        wait_and_tap(serial, config.OPTOUT_TAP_BUTTON, timeout=15)
        time.sleep(config.WAIT_AFTER_TAP)

<<<<<<< HEAD
        # Short pause so the result is visible in the recording
=======
        # Short pause so the final state is visible in the recording
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
        time.sleep(3)

    finally:
        print("\n[7/7] Stopping recording and transferring video...")
        stop_screenrecord(rec_stop, rec_thread)
        local_file = pull_video(serial, remote_path, config.LOCAL_OUTPUT_DIR)

        print("  Killing Messages app...")
        _adb(["-s", serial, "shell", "am", "force-stop", config.MESSAGES_PACKAGE])

        print(f"\nDone! Video saved at: {os.path.abspath(local_file)}")
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
<<<<<<< HEAD
        description="Automated RCS demo video recorder for Vonage Agent Review"
=======
        description="Automated RCS demo video recorder — Vonage Agent Review"
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
    )
    parser.add_argument("--trigger",    dest="trigger", action="store_true",  default=True,
                        help="Send messages via Vonage API (default: on)")
    parser.add_argument("--no-trigger", dest="trigger", action="store_false",
                        help="Record only — trigger messages externally")
    args = parser.parse_args()
    run_demo(trigger_api=args.trigger)
