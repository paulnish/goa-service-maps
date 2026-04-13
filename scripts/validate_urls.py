#!/usr/bin/env python3
"""
Validate all channel URLs across all ministry JSON files.

Checks every non-mailto URL for HTTP status. Reports broken links
grouped by ministry with the service name and expected URL.

Usage:
    python3 scripts/validate_urls.py

Requires: requests (pip3 install requests)
"""

import json
import glob
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Missing dependency. Run: pip3 install requests")
    sys.exit(1)


def collect_urls(data_dir: Path):
    """Yield (ministry_prefix, service_name, channel_label, url) for every channel URL."""
    for f in sorted(data_dir.glob("*.json")):
        if f.name.endswith("_legislation.json") or f.name in ("ministries.json", "config.json"):
            continue
        data = json.loads(f.read_text())
        prefix = data.get("prefix", f.stem)
        for goal in data.get("goals", []):
            for ms in goal.get("main_services", []):
                for sup in ms.get("supporting", []):
                    for ch in sup.get("channels", []):
                        url = ch.get("url")
                        if url and not url.startswith("mailto:"):
                            yield prefix, sup["name"], ch.get("label", ""), url


def check_url(url: str, timeout: int = 15) -> tuple:
    """Return (status_code, final_url, error_msg). status_code is 0 on connection error."""
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/125.0.0.0 Safari/537.36"
        })
        final_url = r.url if r.url != url else None
        return r.status_code, final_url, None
    except requests.exceptions.Timeout:
        return 0, None, "timeout"
    except requests.exceptions.ConnectionError as e:
        return 0, None, f"connection error: {e}"
    except Exception as e:
        return 0, None, str(e)


def main():
    data_dir = Path(__file__).resolve().parent.parent / "data" / "ab"
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        sys.exit(1)

    # Collect all URLs and deduplicate
    all_entries = list(collect_urls(data_dir))
    unique_urls = sorted(set(url for _, _, _, url in all_entries))

    print(f"Found {len(all_entries)} channel URLs ({len(unique_urls)} unique) across all ministries\n")

    # Check each unique URL once
    results = {}
    for i, url in enumerate(unique_urls, 1):
        sys.stdout.write(f"  [{i}/{len(unique_urls)}] {url[:80]}...")
        sys.stdout.flush()
        status, final_url, error = check_url(url)
        results[url] = (status, final_url, error)
        if status == 200:
            redir_note = f" -> {final_url}" if final_url else ""
            print(f" ✅ 200{redir_note}")
        elif status == 0:
            print(f" ❌ {error}")
        else:
            print(f" ❌ {status}")

    # Summary
    broken = {url: r for url, r in results.items() if r[0] != 200}
    redirected = {url: r for url, r in results.items() if r[0] == 200 and r[1]}

    print(f"\n{'='*70}")
    print(f"RESULTS: {len(unique_urls)} URLs checked")
    print(f"  ✅ OK: {len(unique_urls) - len(broken)}")
    print(f"  ❌ Broken: {len(broken)}")
    if redirected:
        print(f"  ↪  Redirected (still OK): {len(redirected)}")

    if broken:
        print(f"\n{'='*70}")
        print("BROKEN URLS:\n")
        for url, (status, final_url, error) in sorted(broken.items()):
            status_str = str(status) if status else error
            # Find which ministries/services use this URL
            users = [(p, s) for p, s, _, u in all_entries if u == url]
            for prefix, svc in users:
                print(f"  [{prefix}] {svc}")
            print(f"    URL: {url}")
            print(f"    Status: {status_str}")
            print()

    if redirected:
        print(f"\n{'='*70}")
        print("REDIRECTED URLS (working, but consider updating):\n")
        for url, (status, final_url, error) in sorted(redirected.items()):
            users = [(p, s) for p, s, _, u in all_entries if u == url]
            for prefix, svc in users:
                print(f"  [{prefix}] {svc}")
            print(f"    URL: {url}")
            print(f"    Redirects to: {final_url}")
            print()

    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
