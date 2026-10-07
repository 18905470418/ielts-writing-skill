"""Helpers for pulling JSON objects out of Next.js RSC payloads."""
from __future__ import annotations

import json
import re


def _unescape_js_string(s: str) -> str:
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n:
            nxt = s[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "'": "'"}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt == "u" and i + 5 < n:
                try:
                    out.append(chr(int(s[i + 2 : i + 6], 16)))
                    i += 6
                    continue
                except ValueError:
                    pass
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def rsc_blob(html: str) -> str:
    """Return the decoded RSC stream text from an HTML document."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*"((?:[^"\\]|\\.)*)"\]\)', html)
    if chunks:
        return "".join(_unescape_js_string(c) for c in chunks)
    # fall back: any big inline script
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S)
    best = max(scripts, key=len, default="")
    return _unescape_js_string(best)


def find_json_objects(blob: str, key: str) -> list[dict]:
    """Find every `"<key>": { ... }` JSON object in a blob and parse it."""
    results: list[dict] = []
    needle = '"%s":' % key
    start = 0
    while True:
        idx = blob.find(needle, start)
        if idx == -1:
            return results
        brace = blob.find("{", idx)
        if brace == -1:
            return results
        end = _match_brace(blob, brace)
        if end == -1:
            start = idx + len(needle)
            continue
        raw = blob[brace : end + 1]
        try:
            results.append(json.loads(raw))
        except json.JSONDecodeError:
            # tolerate trailing content by trimming to the last balanced brace
            pass
        start = end + 1


def _match_brace(s: str, start: int) -> int:
    depth = 0
    i = start
    n = len(s)
    in_str = False
    escape = False
    while i < n:
        ch = s[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1
