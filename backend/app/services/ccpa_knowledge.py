"""
CCPA Knowledge Service

Loads structured CCPA statute sections from ccpa_sections.json
and provides retrieval methods for the RAG pipeline.

Key method: get_parent_sections() enables parent-document retrieval
where we search by subsection (child) but return full section (parent)
to the LLM for complete legal context.
"""

import json
import os
import re
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SECTIONS_PATH = os.path.join(DATA_DIR, "ccpa_sections.json")


class CCPAKnowledge:
    """Manages CCPA statute knowledge base for RAG retrieval."""

    def __init__(self, sections_path: str = SECTIONS_PATH):
        """Load CCPA sections from JSON file at initialization."""
        if not os.path.exists(sections_path):
            raise FileNotFoundError(
                f"CCPA sections file not found: {sections_path}. "
                "Run: python scripts/preprocess_ccpa.py"
            )

        with open(sections_path, "r", encoding="utf-8") as f:
            self._sections: list[dict] = json.load(f)

        # Build lookup indexes for fast retrieval
        self._section_by_id: dict[str, dict] = {
            s["section_id"]: s for s in self._sections
        }

        # Build subsection-to-parent mapping
        # e.g., "1798.100(a)" -> "1798.100"
        self._subsection_to_parent: dict[str, str] = {}
        for section in self._sections:
            for sub in section.get("subsections", []):
                self._subsection_to_parent[sub["id"]] = section["section_id"]

    def get_all_sections(self) -> list[dict]:
        """Return all CCPA section objects."""
        return self._sections

    def get_section_by_id(self, section_id: str) -> Optional[dict]:
        """
        Lookup a section by its ID.

        Args:
            section_id: e.g., "1798.100"

        Returns:
            Section dict or None if not found.
        """
        return self._section_by_id.get(section_id)

    def get_all_subsections(self) -> list[dict]:
        """
        Return a flattened list of all subsections with parent_section_id attached.

        Used for embedding child chunks in the vector store.
        Each returned dict has: id, text, parent_section_id
        """
        subsections = []
        for section in self._sections:
            for sub in section.get("subsections", []):
                subsections.append({
                    "id": sub["id"],
                    "text": sub["text"],
                    "parent_section_id": section["section_id"],
                })
        return subsections

    def get_parent_sections(self, subsection_ids: list[str]) -> list[dict]:
        """
        Given subsection IDs, return their full parent section objects (deduplicated).

        This is the core of parent-document retrieval:
        - Vector search finds relevant subsections (children)
        - We return the full section (parent) to give the LLM complete legal context

        Args:
            subsection_ids: e.g., ["1798.100(a)", "1798.120(a)"]

        Returns:
            Deduplicated list of parent section dicts.
        """
        seen_parent_ids = set()
        parents = []

        for sub_id in subsection_ids:
            # Try direct lookup
            parent_id = self._subsection_to_parent.get(sub_id)

            if not parent_id:
                # Try extracting parent ID from subsection format
                # "1798.100(a)" -> "1798.100"
                match = re.match(r"(1798\.\d+(?:\.\d+)?)", sub_id)
                if match:
                    parent_id = match.group(1)

            if parent_id and parent_id not in seen_parent_ids:
                section = self._section_by_id.get(parent_id)
                if section:
                    parents.append(section)
                    seen_parent_ids.add(parent_id)

        return parents

    def get_sections_for_context(self, section_ids: list[str]) -> str:
        """
        Format multiple sections into a context string for the LLM prompt.

        Args:
            section_ids: List of section IDs to include.

        Returns:
            Formatted text with section headers and content.
        """
        parts = []
        for sid in section_ids:
            section = self._section_by_id.get(sid)
            if section:
                parts.append(
                    f"Section {section['section_id']}: {section['title']}\n"
                    f"{section['full_text']}"
                )
        return "\n\n---\n\n".join(parts)


# Module-level singleton
ccpa_kb = CCPAKnowledge()
