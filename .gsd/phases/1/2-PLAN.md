---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: CCPA Knowledge Retrieval Layer

## Objective
Build the knowledge service that loads the structured CCPA sections and provides retrieval methods for the RAG pipeline. This service is consumed by the analyzer in Phase 2.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- backend/app/data/ccpa_sections.json (populated by Plan 1.1)
- backend/app/services/ccpa_knowledge.py (empty stub)
- backend/app/services/__init__.py (empty stub)

## Tasks

<task type="auto">
  <name>Implement ccpa_knowledge.py service</name>
  <files>backend/app/services/ccpa_knowledge.py</files>
  <action>
    Create a CCPAKnowledge class that:
    1. Loads `ccpa_sections.json` at initialization from a path relative to the data directory
    2. Stores sections in memory as a list of dicts
    3. Exposes these methods:
       - `get_all_sections() -> list[dict]` — returns all section objects
       - `get_section_by_id(section_id: str) -> dict | None` — lookup by section_id (e.g., "1798.100")
       - `get_all_subsections() -> list[dict]` — returns flattened list of all subsections with their parent section_id attached (used for embedding child chunks)
       - `get_parent_sections(subsection_ids: list[str]) -> list[dict]` — given subsection IDs like "1798.100(a)", returns the full parent section objects (deduplicated)
    4. Create a module-level singleton instance: `ccpa_kb = CCPAKnowledge()`

    IMPORTANT: The `get_parent_sections` method is critical — it enables "Parent-Document Retrieval" where we search by subsection (child) but return the full section (parent) to the LLM.

    AVOID: Do NOT load the file on every method call — load once at init.
    AVOID: Do NOT import any external libraries — this is pure Python/JSON.
  </action>
  <verify>cd backend && python -c "
from app.services.ccpa_knowledge import ccpa_kb
sections = ccpa_kb.get_all_sections()
print(f'Total sections: {len(sections)}')
assert len(sections) >= 10

sub = ccpa_kb.get_all_subsections()
print(f'Total subsections: {len(sub)}')
assert len(sub) >= 20

s = ccpa_kb.get_section_by_id('1798.100')
assert s is not None
print(f'Section 1798.100 title: {s[\"title\"]}')

parents = ccpa_kb.get_parent_sections(['1798.100(a)', '1798.120(a)'])
print(f'Parent sections retrieved: {len(parents)}')
assert len(parents) >= 2
print('All checks passed')
"</verify>
  <done>ccpa_knowledge.py loads ccpa_sections.json and all 4 methods return correct results</done>
</task>

<task type="auto">
  <name>Wire up service __init__.py exports</name>
  <files>backend/app/services/__init__.py, backend/app/core/__init__.py, backend/app/schemas/__init__.py</files>
  <action>
    Update the three __init__.py files to export their modules for clean imports:

    backend/app/services/__init__.py:
    ```python
    from .ccpa_knowledge import ccpa_kb
    ```

    backend/app/core/__init__.py and backend/app/schemas/__init__.py:
    Leave as empty files for now (will be populated in Phase 2 and 3).
    Just ensure they exist so the packages are importable.
  </action>
  <verify>cd backend && python -c "from app.services import ccpa_kb; print(f'Imported ccpa_kb with {len(ccpa_kb.get_all_sections())} sections')"</verify>
  <done>Importing `from app.services import ccpa_kb` works and returns valid data</done>
</task>

## Success Criteria
- [ ] `ccpa_knowledge.py` implements CCPAKnowledge with all 4 methods
- [ ] Singleton `ccpa_kb` is importable from `app.services`
- [ ] `get_all_sections()` returns ≥10 sections
- [ ] `get_all_subsections()` returns ≥20 subsections
- [ ] `get_parent_sections()` correctly maps child IDs to parent sections
