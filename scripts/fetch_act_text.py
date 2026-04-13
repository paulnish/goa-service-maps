#!/usr/bin/env python3
"""
Fetch full legislative text from Kings Printer PDFs and inject anchor IDs
into cfs_legislation.json.

Usage:
    pip install pymupdf
    python scripts/fetch_act_text.py

This fetches the PDF text for CYFEA, FLA, and C-92, injects HTML anchor
spans at the relevant section headings, and writes the full_text into
data/cfs_legislation.json.

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


# Acts to fetch — URL and anchor mappings
ACTS = {
    "CYFEA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/c12.pdf",
        "anchors": {
            # Maps anchor_id -> regex pattern to find in text
            "CYFEA-s2": r"(?m)^.*child in need of intervention",
            "CYFEA-s4": r"(?m)^.*duty to report",
            "CYFEA-Part2Div2": r"(?m)^.*Division 2.*\n.*Family Enhancement",
            "CYFEA-Part3": r"(?m)^.*Part 3.*\n.*Protective Services",
            "CYFEA-Part3Div4": r"(?m)^.*foster care|(?m)^.*placement of children",
            "CYFEA-s57": r"(?m)^.*57\.3.*support and financial assistance",
            "CYFEA-Part4": r"(?m)^.*Part 4.*\n.*Adoption",
            "CYFEA-s105": r"(?m)^.*105\.91.*delegation|(?m)^.*delegated first nation",
        }
    },
    "FLA": {
        "url": "https://kings-printer.alberta.ca/documents/Acts/f04p5.pdf",
        "anchors": {
            "FLA-Part2": r"(?m)^.*Part 2.*\n.*Parentage",
            "FLA-Part3": r"(?m)^.*Part 3.*\n.*Guardianship",
        }
    },
    "C-92": {
        "url": "https://laws-lois.justice.gc.ca/PDF/F-11.73.pdf",
        "anchors": {
            "C92-s9": r"(?m)^.*best interests of.*child|(?m)^.*9\s.*best interests",
            "C92-s18": r"(?m)^.*18\s.*indigenous governing bod|(?m)^.*Part 3",
        }
    }
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
            # Find the start of the line
            line_start = text.rfind("\n", 0, pos) + 1
            anchor_html = f'<span class="sec-anchor" id="{anchor_id}">'
            # Find end of line for closing span
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
    leg_path = os.path.join("data", "cfs_legislation.json")
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
        status = f"{len(act['full_text']):,} chars" if act["full_text"] else "EMPTY"
        print(f"  {act['abbrev']}: {status}")


if __name__ == "__main__":
    main()
