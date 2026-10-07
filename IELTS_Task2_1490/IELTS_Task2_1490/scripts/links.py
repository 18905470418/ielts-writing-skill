#!/usr/bin/env python3
"""Print links from cached raw HTML, optionally filtered by substring."""
import os
import sys

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        path = os.path.join(RAW, sys.argv[1])
    needle = sys.argv[2] if len(sys.argv) > 2 else ""
    with open(path, "rb") as fh:
        soup = BeautifulSoup(fh.read(), "lxml")
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if needle and needle not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        label = " ".join(a.get_text(" ", strip=True).split())[:70]
        print(f"{href}\t{label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
