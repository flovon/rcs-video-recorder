"""
adb_helper.py
-------------
Low-level ADB wrapper functions used by all scripts in this project.
"""

import subprocess
import time
import os
import threading
import xml.etree.ElementTree as ET


def _adb(args: list, serial: str = "", timeout: int = 30) -> str:
    """Run an ADB command and return stdout. Raises RuntimeError on failure."""
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"ADB error: {result.stderr.strip()}")
    return result.stdout.strip()


def get_device_serial(preferred: str = "") -> str:
    """Return the serial of the connected device. Raises if none is found."""
    output = _adb(["devices"])
    lines = [l for l in output.splitlines() if "\tdevice" in l]
    if not lines:
        raise RuntimeError("No ADB device found. Is USB Debugging enabled?")
    if preferred:
        for l in lines:
            if preferred in l:
                return preferred
    return lines[0].split("\t")[0]


def start_screenrecord(serial: str, remote_path: str, max_seconds: int = 120):
    """
    Start a screen recording in a background thread.
    Returns (thread, stop_event). Call stop_screenrecord() to end it.
    """
    stop_event = threading.Event()

    def _record():
        try:
            cmd = [
                "adb", "-s", serial, "shell",
                f"screenrecord --bit-rate 8000000 --time-limit {max_seconds} {remote_path}"
            ]
            proc = subprocess.Popen(cmd)
            while not stop_event.wait(timeout=1):
                if proc.poll() is not None:
                    break
            proc.terminate()
        except Exception as e:
            print(f"[screenrecord] Error: {e}")

    t = threading.Thread(target=_record, daemon=True)
    t.start()
    time.sleep(1)  # Give screenrecord time to initialise
    return t, stop_event


def stop_screenrecord(stop_event, thread, timeout: int = 5):
    """Signal the recording to stop and wait for the thread to finish."""
    stop_event.set()
    thread.join(timeout=timeout)
    time.sleep(2)  # Allow the device to close/flush the file


def pull_video(serial: str, remote_path: str, local_dir: str) -> str:
    """Pull the recorded video from the device to the local machine."""
    os.makedirs(local_dir, exist_ok=True)
    filename  = os.path.basename(remote_path)
    local_path = os.path.join(local_dir, filename)
    _adb(["-s", serial, "pull", remote_path, local_path])
    print(f"[pull] Video saved: {local_path}")
    return local_path


def open_messages_app(serial: str, package: str, activity: str):
    """Launch the Messages app via an explicit intent."""
    _adb(["-s", serial, "shell", "am", "start", "-n", f"{package}/{activity}"])


def tap(serial: str, x: int, y: int):
    """Tap at screen coordinates (x, y)."""
    _adb(["-s", serial, "shell", "input", "tap", str(x), str(y)])


def swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500):
    """Swipe from (x1, y1) to (x2, y2) over duration_ms milliseconds."""
    _adb(["-s", serial, "shell", "input",
          "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])


def get_screen_size(serial: str) -> tuple:
    """Return the screen resolution as (width, height)."""
    out = _adb(["-s", serial, "shell", "wm", "size"])
    size_str = out.split(":")[-1].strip()
    w, h = size_str.split("x")
    return int(w), int(h)


def dump_ui(serial: str, remote_xml: str = "/sdcard/ui_dump.xml") -> str:
    """Run a UIAutomator dump and return the XML content as a string."""
    _adb(["-s", serial, "shell", "uiautomator", "dump", remote_xml])
    time.sleep(0.5)
    return _adb(["-s", serial, "shell", "cat", remote_xml])


def unlock_screen(serial: str):
    """Wake the screen and swipe up to dismiss the lock screen."""
    _adb(["-s", serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP"])
    time.sleep(1)
    w, h = get_screen_size(serial)
    swipe(serial, w // 2, int(h * 0.8), w // 2, int(h * 0.2), 600)
    time.sleep(1)


def type_and_send(serial: str, text: str):
    """
    Type a message into the Messages app compose field and send it.

    Discovery order for the input field:
      1. resource-id containing 'compose_message_text'
      2. First clickable EditText element
      3. Fallback: bottom-centre of the screen (92% height)

    Discovery order for the send button:
      1. resource-id containing 'send_message_button'
      2. content-desc matching 'send' / 'senden' / 'absenden'
      3. Fallback: KEYCODE_ENTER
    """
    def _parse_bounds(bounds):
        try:
            parts = bounds.replace("][", ",").strip("[]").split(",")
            x1, y1, x2, y2 = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            return (x1 + x2) // 2, (y1 + y2) // 2
        except Exception:
            return None

    def _ui_dump():
        _adb(["-s", serial, "shell", "uiautomator", "dump", "/sdcard/ui_type.xml"])
        time.sleep(0.5)
        return _adb(["-s", serial, "shell", "cat", "/sdcard/ui_type.xml"])

    # Locate the compose field
    xml  = _ui_dump()
    root = ET.fromstring(xml)
    input_coords = None
    for node in root.iter("node"):
        res_id = node.get("resource-id", "")
        cls    = node.get("class", "")
        if "compose_message_text" in res_id or (
                "EditText" in cls and node.get("clickable") == "true"):
            coords = _parse_bounds(node.get("bounds", ""))
            if coords:
                input_coords = coords
                break

    if not input_coords:
        w, h = get_screen_size(serial)
        input_coords = (w // 2, int(h * 0.92))
        print(f"  [type] Compose field not found, using fallback @ {input_coords}")

    # Tap the field and enter text
    _adb(["-s", serial, "shell", "input", "tap",
          str(input_coords[0]), str(input_coords[1])])
    time.sleep(0.5)
    escaped = text.replace(" ", "%s").replace("'", "\\'")
    _adb(["-s", serial, "shell", "input", "text", escaped])
    time.sleep(0.5)
    print(f"  [type] Typed: '{text}'")

    # Locate and tap the send button
    xml  = _ui_dump()
    root = ET.fromstring(xml)
    send_coords = None
    for node in root.iter("node"):
        res_id = node.get("resource-id", "")
        desc   = node.get("content-desc", "").lower()
        if "send_message_button" in res_id or desc in ("send", "senden", "absenden"):
            coords = _parse_bounds(node.get("bounds", ""))
            if coords:
                send_coords = coords
                break

    if send_coords:
        _adb(["-s", serial, "shell", "input", "tap",
              str(send_coords[0]), str(send_coords[1])])
        print(f"  [type] Sent via send button @ {send_coords}")
    else:
        _adb(["-s", serial, "shell", "input", "keyevent", "KEYCODE_ENTER"])
        print("  [type] Sent via KEYCODE_ENTER (fallback)")

<<<<<<< HEAD
    time.sleep(1)
=======
    time.sleep(1)
>>>>>>> 7e42969 (Lokalen Projektstand sichern)
