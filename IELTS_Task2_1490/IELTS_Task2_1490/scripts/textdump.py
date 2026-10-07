#!/usr/bin/env python3
"""Dump readable text (and link lists) from cached raw HTML files."""
import os
import re
import sys

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "text")


def text_of(path: str) -> str:
    with open(path, "rb") as fh:
        soup = BeautifulSoup(fh.read(), "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:]
    files = (
        [os.path.join(RAW, n) for n in names]
        if names
        else [os.path.join(RAW, f) for f in sorted(os.listdir(RAW)) if f.endswith(".html")]
    )
    for path in files:
        if not os.path.exists(path):
            print("missing", path)
            continue
        text = text_of(path)
        base = os.path.basename(path).rsplit(".", 1)[0]
        dst = os.path.join(OUT, base + ".txt")
        with open(dst, "w") as fh:
            fh.write(text)
        bands = re.findall(r"Band\s*[0-9](?:\.[0-9])?", text, flags=re.I)
        from collections import Counter
        print(f"{base}\tchars={len(text)}\tbands={dict(Counter(b.title() for b in bands))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
