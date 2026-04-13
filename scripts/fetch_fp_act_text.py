#!/usr/bin/env python3
"""
Fetch full legislative text for Forestry & Parks acts from King's Printer PDFs,
inject anchor IDs, and write full_text into data/ab/fp_legislation.json.

Usage:
    pip install pymupdf
    python scripts/fetch_fp_act_text.py

Run from the goa-service-maps root directory.
"""

import json
import re
import urllib.request
import tempfile
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: pymupdf is required. Install with: pip install pymupdf")
    exit(1)


ACTS = {
    "FA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/f22.pdf",
        "anchors": {
            "FA-Part1": r"(?mi)Part 1\b.*\n.*Management of Forest|(?mi)Management of Forest Land",
            "FA-Part2": r"(?mi)Part 2\b.*\n.*Timber|(?mi)Timber Dispositions",
            "FA-s33": r"(?mi)Timber dues\b|(?mi)\b33\s+.*dues",
            "FA-TMR-damage": r"(?mi)damage assessment|(?mi)timber damage",
            "FA-s40": r"(?mi)personal.use timber|(?mi)\b40\s+.*personal.use",
        },
    },
    "FPPA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/f19.pdf",
        "anchors": {
            "FPPA-s7": r"(?mi)fire permit|(?mi)\b7\s+.*permit.*fire",
            "FPPA-s17": r"(?mi)fire ban|(?mi)fire advisory|(?mi)fire restriction",
            "FPPA-s3": r"(?mi)duty.*prevent|(?mi)prevent.*fire.*spread",
            "FPPA-s14": r"(?mi)duty.*report.*fire|(?mi)\b14\s+.*report",
            "FPPA-Part2": r"(?mi)Part 2\b.*\n.*Suppression|(?mi)Wildfire Officers",
            "FPPA-s23": r"(?mi)public.*notice.*fire|(?mi)\b23\s+.*notice",
        },
    },
    "PPA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/p35.pdf",
        "anchors": {
            "PPA-s6": r"(?mi)establish.*provincial park|(?mi)\b6\s+.*establish",
            "PPA-GenReg-camping": r"(?mi)camping|(?mi)campsite|(?mi)overnight",
            "PPA-fees": r"(?mi)\bfee\b|(?mi)conservation pass",
        },
    },
    "PLA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/p40.pdf",
        "anchors": {
            "PLA-PLUZ": r"(?mi)public land use zone",
            "PLA-PLAR-camping": r"(?mi)camping pass|(?mi)random camping",
            "PLA-enforcement": r"(?mi)trespass|(?mi)enforcement.*officer|(?mi)offence",
        },
    },
}


def fetch_pdf_text(url):
    """Download PDF and extract text."""
    print(f"  Downloading {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        pdf_data = response.read()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_data)
        tmp_path = tmp.name

    try:
        doc = fitz.open(tmp_path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n".join(pages)
    finally:
        os.unlink(tmp_path)


def inject_anchors(text, anchors):
    """Inject HTML anchor spans at matching locations in the text."""
    for anchor_id, pattern in anchors.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pos = match.start()
            line_start = text.rfind("\n", 0, pos) + 1
            anchor_html = f'<span class="sec-anchor" id="{anchor_id}">'
            line_end = text.find("\n", pos)
            if line_end == -1:
                line_end = len(text)

            text = (
                text[:line_start]
                + anchor_html
                + text[line_start:line_end]
                + "</span>"
                + text[line_end:]
            )
            print(f"    Anchored {anchor_id}")
        else:
            print(f"    WARNING: No match for {anchor_id} (pattern: {pattern[:50]}...)")

    return text


def main():
    leg_path = os.path.join("data", "ab", "fp_legislation.json")
    with open(leg_path, "r") as f:
        leg = json.load(f)

    for act in leg["acts"]:
        abbrev = act["abbrev"]
        if abbrev not in ACTS:
            continue

        config = ACTS[abbrev]
        print(f"\nProcessing {abbrev}...")

        try:
            text = fetch_pdf_text(config["url"])
            print(f"  Extracted {len(text):,} chars")

            text = inject_anchors(text, config["anchors"])
            act["full_text"] = text
            print(f"  Done ({len(text):,} chars with anchors)")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    with open(leg_path, "w") as f:
        json.dump(leg, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {leg_path}")

    # Summary
    print("\nFull text status:")
    for act in leg["acts"]:
        ft = act.get("full_text", "")
        status = f"{len(ft):,} chars" if ft else "EMPTY"
        print(f"  {act['abbrev']}: {status}")


if __name__ == "__main__":
    main()
