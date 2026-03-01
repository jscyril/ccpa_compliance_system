#!/usr/bin/env python3
"""
CCPA Statute Markdown Extraction Script

Parses ccpa_statute.md into ccpa_sections.json with hierarchical
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

# Path configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "app", "data")
MD_PATH = os.path.join(DATA_DIR, "ccpa_statute.md")
OUTPUT_PATH = os.path.join(DATA_DIR, "ccpa_sections.json")


def parse_ccpa_markdown(md_path: str) -> list[dict]:
    """Parse the CCPA markdown file into structured sections."""
    print(f"Reading Markdown: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Split into sections based on '## 1798.XXX.'
    raw_sections = re.split(r"\n##\s+(1798\.\d+(?:\.\d+)?)\.\s+([^\n]+)", full_text)
    
    # raw_sections[0] is everything before the first '## ' (title, intro)
    sections = []
    
    # Iterate through the split results.
    # Pattern: [preamble, id1, title1, text1, id2, title2, text2, ...]
    for i in range(1, len(raw_sections), 3):
        section_id = raw_sections[i].strip()
        title = raw_sections[i + 1].strip()
        section_text = raw_sections[i + 2].strip()
        
        # Extract subsections
        subsections = extract_subsections(section_id, section_text)
        
        sections.append({
            "section_id": section_id,
            "title": title,
            "full_text": section_text,
            "subsections": subsections
        })

    return sections


def extract_subsections(section_id: str, section_text: str) -> list[dict]:
    """Extract subsections from a section's markdown text.
    
    Handles patterns like:
    **(a)** text...
    **(b)** text...
    """
    subsections = []
    
    # Split by the bold subsection markers: `\n**(a)**`
    parts = re.split(r"\n\*\*\((\w+)\)\*\*\s*", "\n" + section_text)
    
    if len(parts) <= 1:
        # No standard subsections found, it's a single block
        return subsections
    
    # parts[0] is preamble (often empty if section starts immediately with a subsection)
    # parts[1] is "a", parts[2] is text for a, parts[3] is "b", etc.
    i = 1
    while i < len(parts) - 1:
        marker = parts[i].strip()
        sub_text = parts[i + 1].strip()
        subsection_id = f"{section_id}({marker})"
        
        if sub_text:  # Only add non-empty subsections
            subsections.append({
                "id": subsection_id,
                "text": sub_text,
            })
        i += 2
    
    return subsections


def main():
    if not os.path.exists(MD_PATH):
        print(f"ERROR: Markdown file not found at {MD_PATH}")
        sys.exit(1)
    
    sections = parse_ccpa_markdown(MD_PATH)
    
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
