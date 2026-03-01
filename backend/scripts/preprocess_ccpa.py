#!/usr/bin/env python3
"""
CCPA Statute PDF Extraction Script

Parses ccpa_statute.pdf into ccpa_sections.json with hierarchical
parent-child structure for parent-document retrieval in the RAG pipeline.

Output schema per section:
{
    "section_id": "1798.100",
    "title": "General Duties of Businesses that Collect Personal Information",
    "full_text": "...(entire section)...",
    "subsections": [
        {"id": "1798.100(a)", "text": "..."},
        {"id": "1798.100(b)", "text": "..."}
    ]
}
"""

import json
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)


# Path configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "app", "data")
PDF_PATH = os.path.join(DATA_DIR, "ccpa_statute.pdf")
OUTPUT_PATH = os.path.join(DATA_DIR, "ccpa_sections.json")

# Regex for section headers like "1798.100.  General Duties..."
# Matches: 1798.XXX. or 1798.XXX.XX. followed by title text (1+ spaces)
SECTION_HEADER_RE = re.compile(
    r"^(1798\.\d+(?:\.\d+)?)\.\s{1,}(.+?)$", re.MULTILINE
)

# Regex for subsection markers like (a), (b), (1), (2)
SUBSECTION_RE = re.compile(r"^\(([a-z]|\d+)\)\s*$", re.MULTILINE)


def extract_full_text(pdf_path: str) -> str:
    """Extract all text from PDF, skipping the table of contents pages."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        # Remove page headers like "Page X of Y"
        text = re.sub(r"^Page \d+ of \d+\s*$", "", text, flags=re.MULTILINE)
        full_text += text + "\n"
    doc.close()
    return full_text


def find_section_boundaries(text: str) -> list[dict]:
    """Find all section headers and their positions in the text."""
    sections = []
    for match in SECTION_HEADER_RE.finditer(text):
        section_id = match.group(1)
        title = match.group(2).strip()
        start = match.start()
        
        # Skip table-of-contents entries (contain dotted separator lines)
        if "....." in title or title.strip().startswith("("):
            continue
        
        # Clean multi-line title artifacts  
        title = re.sub(r"\.{2,}.*$", "", title).strip()
        
        sections.append({
            "section_id": section_id,
            "title": title,
            "start": start,
        })
    return sections


def extract_subsections(section_id: str, section_text: str) -> list[dict]:
    """Extract subsections from a section's text.
    
    Handles patterns like:
    (a) text...
    (b) text...
    (1) text...
    """
    subsections = []
    
    # Find all top-level subsection markers (a), (b), etc.
    # We look for lines that start with (letter) or (number) pattern
    parts = re.split(r"\n(\([a-z]\))\s*\n", section_text)
    
    if len(parts) <= 1:
        # No standard subsections found, try numbered ones
        parts = re.split(r"\n(\(\d+\))\s*\n", section_text)
    
    if len(parts) <= 1:
        # Still no subsections — the section is a single block
        return subsections
    
    # parts[0] is text before first subsection (often empty or preamble)
    # parts[1] is "(a)", parts[2] is text after (a), parts[3] is "(b)", etc.
    i = 1
    while i < len(parts) - 1:
        marker = parts[i].strip("()")
        sub_text = parts[i + 1].strip()
        subsection_id = f"{section_id}({marker})"
        
        if sub_text:  # Only add non-empty subsections
            subsections.append({
                "id": subsection_id,
                "text": sub_text,
            })
        i += 2
    
    return subsections


def parse_ccpa_statute(pdf_path: str) -> list[dict]:
    """Main parsing function: extract PDF into structured sections."""
    print(f"Reading PDF: {pdf_path}")
    full_text = extract_full_text(pdf_path)
    print(f"Extracted {len(full_text)} characters of text")
    
    # Find all section boundaries
    boundaries = find_section_boundaries(full_text)
    print(f"Found {len(boundaries)} section headers")
    
    if not boundaries:
        print("ERROR: No sections found! Check the PDF format.")
        sys.exit(1)
    
    sections = []
    for i, boundary in enumerate(boundaries):
        # Get section text: from this header to the next header (or end)
        start = boundary["start"]
        end = boundaries[i + 1]["start"] if i + 1 < len(boundaries) else len(full_text)
        
        section_text = full_text[start:end].strip()
        
        # Clean up the text
        section_text = re.sub(r"\s+", " ", section_text)  # collapse whitespace for full_text
        
        # Extract subsections from the raw (non-collapsed) text
        raw_section_text = full_text[start:end]
        subsections = extract_subsections(boundary["section_id"], raw_section_text)
        
        section = {
            "section_id": boundary["section_id"],
            "title": boundary["title"],
            "full_text": section_text,
            "subsections": subsections,
        }
        sections.append(section)
    
    return sections


def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)
    
    sections = parse_ccpa_statute(PDF_PATH)
    
    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    
    # Summary
    total_subsections = sum(len(s["subsections"]) for s in sections)
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Sections extracted: {len(sections)}")
    print(f"Total subsections:  {total_subsections}")
    print(f"Output written to:  {OUTPUT_PATH}")
    print(f"\nKey sections:")
    
    key_sections = ["1798.100", "1798.105", "1798.110", "1798.115",
                    "1798.120", "1798.125", "1798.130", "1798.135",
                    "1798.140", "1798.145", "1798.150"]
    for sid in key_sections:
        found = any(s["section_id"] == sid for s in sections)
        status = "✓" if found else "✗ MISSING"
        title = next((s["title"] for s in sections if s["section_id"] == sid), "")
        print(f"  {status} {sid}: {title[:60]}")


if __name__ == "__main__":
    main()
