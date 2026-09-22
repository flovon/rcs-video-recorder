"""
ui_helper.py
------------
UIAutomator XML parsing helpers for finding on-screen elements.
"""

import xml.etree.ElementTree as ET


def find_element_by_text(xml_content: str, text: str) -> dict | None:
    """
    Search the UIAutomator dump for an element whose 'text' or
    'content-desc' attribute contains the given string (case-insensitive).

    Returns {'x': int, 'y': int, 'bounds': str} or None if not found.
    """
    root = ET.fromstring(xml_content)
    for node in root.iter("node"):
        node_text = node.get("text", "") or node.get("content-desc", "")
        if text.lower() in node_text.lower():
            coords = _parse_bounds(node.get("bounds", ""))
            if coords:
                return coords
    return None


def _parse_bounds(bounds: str) -> dict | None:
    """Convert '[x1,y1][x2,y2]' into a centre-point dict."""
    try:
        parts = bounds.replace("][", ",").strip("[]").split(",")
        x1, y1, x2, y2 = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        return {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2, "bounds": bounds}
    except Exception:
        return None
