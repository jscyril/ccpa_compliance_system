---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: CCPA Statute PDF Extraction

## Objective
Parse the CCPA statute PDF into a structured JSON knowledge base with hierarchical parent-child chunks, enabling parent-document retrieval for the RAG pipeline.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- backend/app/data/ccpa_statute.pdf
- backend/scripts/preprocess_ccpa.py (empty stub)
- backend/app/data/ccpa_sections.json (empty stub)

## Tasks

<task type="auto">
  <name>Update requirements.txt with data dependencies</name>
  <files>backend/requirements.txt</files>
  <action>
    Add the following packages to backend/requirements.txt:
    - PyMuPDF>=1.24 (PDF parsing — imported as `fitz`)
    - chromadb>=0.5 (in-memory vector store)
    - sentence-transformers>=2.7 (embedding model)
    - bitsandbytes>=0.43 (4-bit quantization)
    - accelerate>=0.30 (model loading acceleration)

    DO NOT remove the existing 4 packages (fastapi, uvicorn, torch, transformers).
    DO NOT pin exact versions — use >= for flexibility.
  </action>
  <verify>cat backend/requirements.txt | grep -c ">="; should return 9 (4 existing + 5 new)</verify>
  <done>requirements.txt contains all 9 dependencies with >= version constraints</done>
</task>

<task type="auto">
  <name>Implement CCPA PDF extraction script</name>
  <files>backend/scripts/preprocess_ccpa.py</files>
  <action>
    Create a Python script that:
    1. Opens `backend/app/data/ccpa_statute.pdf` using PyMuPDF (fitz)
    2. Extracts all text page by page
    3. Parses the text to identify CCPA sections using regex patterns:
       - Section headers: "1798.XXX." or "Section 1798.XXX"
       - Subsection markers: "(a)", "(b)", "(1)", "(2)", etc.
    4. Builds a list of section objects with this structure:
       ```json
       {
         "section_id": "1798.100",
         "title": "General Duties of Businesses that Collect Personal Information",
         "full_text": "...(entire section text)...",
         "subsections": [
           {"id": "1798.100(a)", "text": "...subsection text..."},
           {"id": "1798.100(b)", "text": "...subsection text..."}
         ]
       }
       ```
    5. Writes the result to `backend/app/data/ccpa_sections.json`
    6. Prints summary: number of sections extracted, total subsections

    Key sections to capture (at minimum):
    - 1798.100 (Right to Know / General Duties)
    - 1798.105 (Right to Delete)
    - 1798.110 (Right to Know What Is Collected)
    - 1798.115 (Right to Know What Is Sold/Disclosed)
    - 1798.120 (Right to Opt-Out of Sale)
    - 1798.125 (Right to Non-Discrimination)
    - 1798.130 (Notice/Submission Methods)
    - 1798.135 (Methods for Opt-Out)
    - 1798.140 (Definitions)
    - 1798.145 (Exemptions)
    - 1798.150 (Personal Information Security Breaches)
    - 1798.155 (Administrative Enforcement)
    - 1798.185 (Regulations)
    - 1798.199 (Operative Date)

    AVOID: Do NOT use `unstructured` library — it requires Java and heavy deps.
    AVOID: Do NOT hardcode section content — extract dynamically from the PDF.
    HANDLE: If regex misses sections, use a fallback page-by-page approach with manual section markers.
  </action>
  <verify>cd backend && python scripts/preprocess_ccpa.py && python -c "import json; d=json.load(open('app/data/ccpa_sections.json')); print(f'{len(d)} sections'); assert len(d) >= 10, 'Too few sections'"</verify>
  <done>ccpa_sections.json contains ≥10 CCPA sections with section_id, title, full_text, and subsections fields</done>
</task>

## Success Criteria
- [ ] `requirements.txt` has 9 dependencies
- [ ] `preprocess_ccpa.py` runs without errors
- [ ] `ccpa_sections.json` is populated with ≥10 structured sections
- [ ] Each section has `section_id`, `title`, `full_text`, `subsections` fields
- [ ] Key sections (1798.100, .105, .120, .125) are present
