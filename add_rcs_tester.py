#!/usr/bin/env python3
"""
add_rcs_tester.py
-----------------
Opens the Messages app, waits for a message from the "RBM Tester Manager"
agent, and taps "Make me a tester" automatically.

Prerequisites:
  - The tester invitation must already have been sent from the
    RBM Developer Console before running this script.
  - config.py, adb_helper.py and ui_helper.py must be in the same directory.

Usage:
  python3 add_rcs_tester.py
  python3 add_rcs_tester.py --serial R58M41XXXXX   # specific device
  python3 add_rcs_tester.py --timeout 60            # longer wait time
"""

import argparse
import time
import sys

import config
from adb_helper import (
    get_device_serial, open_messages_app, unlock_screen,
    dump_ui, tap, get_screen_size, _adb,
)
from ui_helper import find_element_by_text

# Adjust these if the names shown in the Messages app differ
RBM_AGENT_NAME  = "RBM Tester Manager"
RBM_BUTTON_TEXT = "Make me a tester"


def open_rbm_conversation(serial: str, timeout: int = 30) -> bool:
    """Wait until the RBM Tester Manager conversation is visible and open it."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xml  = dump_ui(serial)
        elem = find_element_by_text(xml, RBM_AGENT_NAME)
        if elem:
            print(f"  [UI] Conversation found: '{RBM_AGENT_NAME}' "
                  f"@ ({elem['x']},{elem['y']})")
            tap(serial, elem["x"], elem["y"])
            time.sleep(2)
            return True
        print(f"  [UI] Waiting for conversation '{RBM_AGENT_NAME}'...")
        time.sleep(2)
    return False


def tap_make_me_tester(serial: str, timeout: int = 20) -> bool:
    """Wait until the 'Make me a tester' button is visible and tap it."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xml  = dump_ui(serial)
        elem = find_element_by_text(xml, RBM_BUTTON_TEXT)
        if elem:
            print(f"  [UI] Button found: '{RBM_BUTTON_TEXT}' "
                  f"@ ({elem['x']},{elem['y']})")
            tap(serial, elem["x"], elem["y"])
            return True
        print(f"  [UI] Waiting for button '{RBM_BUTTON_TEXT}'...")
        time.sleep(2)
    return False


def run(serial_override: str = "", timeout: int = 30):
    print("=" * 55)
    print("  RBM Tester Manager — Register as Tester")
    print("=" * 55)

    serial = get_device_serial(serial_override or config.DEVICE_SERIAL)
    w, h   = get_screen_size(serial)
    print(f"[OK] Device: {serial}  |  Resolution: {w}x{h}")

    print("\n[1/5] Unlocking screen...")
    unlock_screen(serial)

    print("[2/5] Opening Messages app...")
    open_messages_app(serial, config.MESSAGES_PACKAGE, config.MESSAGES_ACTIVITY)
    time.sleep(config.WAIT_APP_OPEN)

    print(f"[3/5] Waiting for conversation '{RBM_AGENT_NAME}'...")
    if not open_rbm_conversation(serial, timeout=timeout):
        print(f"\nError: conversation '{RBM_AGENT_NAME}' not found after {timeout}s.")
        print("Tips:")
        print("  - Has the tester invitation been sent from the RBM Developer Console?")
        print("  - Run `python3 debug_ui.py` to check the exact name shown in the app.")
        sys.exit(1)

    print(f"[4/5] Looking for button '{RBM_BUTTON_TEXT}'...")
    if not tap_make_me_tester(serial, timeout=20):
        print(f"\nError: button '{RBM_BUTTON_TEXT}' not found.")
        print("Tips:")
        print("  - Has the invitation message arrived? Increase WAIT_MESSAGE_ARRIVE.")
        print("  - Run `python3 debug_ui.py` to verify the exact button text.")
        sys.exit(1)

    print("[5/5] Waiting 2 seconds for the agent response...")
    time.sleep(2)

    print("  Killing Messages app...")
    _adb(["-s", serial, "shell", "am", "force-stop", config.MESSAGES_PACKAGE])

    print("\nDone! Device successfully registered as tester.")
    print("=" * 55)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatically tap 'Make me a tester' in the RBM Tester Manager"
    )
    parser.add_argument("--serial",  default="",
                        help="ADB device serial (empty = first detected device)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Max seconds to wait for the conversation (default: 30)")
    args = parser.parse_args()
    run(serial_override=args.serial, timeout=args.timeout)
