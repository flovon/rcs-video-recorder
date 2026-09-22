#!/usr/bin/env python3
"""
debug_ui.py
-----------
Prints all visible UI text elements on the current screen.
Use this to find the exact AGENT_DISPLAY_NAME or button text
to set in config.py.

Usage:
  1. Open the Messages app on the phone (conversation list visible)
  2. python3 debug_ui.py
  3. Look for the RCS agent name in the output
"""

import subprocess
import xml.etree.ElementTree as ET
import sys

DEVICE_SERIAL = ""   # Leave empty to use the first detected device


def adb(args, serial=""):
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def get_serial():
    out   = adb(["devices"])
    lines = [l for l in out.splitlines() if "\tdevice" in l]
    if not lines:
        raise RuntimeError("No device found. Is USB Debugging enabled?")
    return DEVICE_SERIAL if DEVICE_SERIAL else lines[0].split("\t")[0]


def dump_and_print(serial):
    print(f"[debug] Device: {serial}")
    adb(["-s", serial, "shell", "uiautomator", "dump", "/sdcard/ui_debug.xml"])
    xml = adb(["-s", serial, "shell", "cat", "/sdcard/ui_debug.xml"])

    print("\n=== All visible UI texts ===\n")
    root = ET.fromstring(xml)
    seen = set()
    for node in root.iter("node"):
        text   = node.get("text",         "").strip()
        desc   = node.get("content-desc", "").strip()
        res_id = node.get("resource-id",  "")
        cls    = node.get("class",        "")
        for val in [text, desc]:
            if val and val not in seen:
                seen.add(val)
                print(f"  text={val!r:50s}  class={cls.split('.')[-1]}  res-id={res_id}")

    print("\n=== Raw XML (first 3000 chars) ===\n")
    print(xml[:3000])


if __name__ == "__main__":
    try:
        serial = get_serial()
        dump_and_print(serial)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)