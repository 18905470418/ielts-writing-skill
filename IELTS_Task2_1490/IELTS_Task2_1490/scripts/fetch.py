#!/usr/bin/env python3
"""Download pages to data/raw, with on-disk caching keyed by URL.

Usage:
  python scripts/fetch.py <urls-file>            # one URL per line
  python scripts/fetch.py --url <url> [--name f] # single URL
"""
import argparse
import concurrent.futures
import hashlib
import os
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def key_for(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def cache_path(url: str) -> str:
    return os.path.join(RAW, key_for(url) + ".html")


def fetch(url: str, force: bool = False, timeout: int = 45) -> str | None:
    os.makedirs(RAW, exist_ok=True)
    path = cache_path(url)
    if os.path.exists(path) and not force and os.path.getsize(path) > 0:
        return path
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.content:
                with open(path, "wb") as fh:
                    fh.write(r.content)
                return path
            last = f"HTTP {r.status_code} ({len(r.content)} bytes)"
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
        time.sleep(1.5 * (attempt + 1))
    sys.stderr.write(f"[fetch] FAILED {url}: {last}\n")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls_file", nargs="?")
    ap.add_argument("--url")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    urls: list[str] = []
    if args.url:
        urls.append(args.url)
    if args.urls_file:
        with open(args.urls_file) as fh:
            urls.extend(line.strip() for line in fh if line.strip() and not line.startswith("#"))

    ok = 0
    for url in urls:
        path = fetch(url, force=args.force)
        status = "ok" if path else "fail"
        ok += 1 if path else 0
        print(f"{status}\t{url}\t{path or ''}")
    print(f"-- {ok}/{len(urls)} fetched", file=sys.stderr)
    return 0 if ok else 1


def fetch_many(urls: list[str], workers: int = 8, force: bool = False) -> dict[str, str]:
    """Fetch many URLs concurrently; returns {url: path} for successes."""
    out: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch, u, force): u for u in urls}
        for fut in concurrent.futures.as_completed(futures):
            url = futures[fut]
            try:
                path = fut.result()
            except Exception:  # noqa: BLE001
                path = None
            if path:
                out[url] = path
    return out


if __name__ == "__main__":
    raise SystemExit(main())
