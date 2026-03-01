"""
Analyzer Service

Orchestrates the full CCPA compliance analysis pipeline:
1. Vector search → relevant subsections
2. Parent-document retrieval → full sections
3. Prompt construction → Llama 3.1 chat format
4. LLM inference → raw text
5. Response parsing → validated JSON

On ANY error, returns the safe default: {"harmful": false, "articles": []}
"""

import logging

from app.core.llm_engine import llm_engine
from app.core.response_parser import parse_response
from app.core.vector_store import vector_store
from app.services.ccpa_knowledge import ccpa_kb
from app.services.prompt_builder import prompt_builder

logger = logging.getLogger(__name__)

# Safe default — returned on any pipeline failure
SAFE_DEFAULT = {"harmful": False, "articles": []}


class Analyzer:
    """Orchestrates CCPA compliance analysis pipeline."""

    def __init__(self):
        self._llm = llm_engine
        self._vector_store = vector_store
        self._kb = ccpa_kb
        self._prompt_builder = prompt_builder

    def analyze(self, prompt: str) -> dict:
        """
        Analyze a business practice for CCPA compliance.

        Args:
            prompt: Natural language description of a business practice.

        Returns:
            Dict with {"harmful": bool, "articles": list[str]}.
            Never raises — returns safe default on any error.
        """
        try:
            return self._run_pipeline(prompt)
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
            return SAFE_DEFAULT.copy()

    def _run_pipeline(self, prompt: str) -> dict:
        """Execute the full analysis pipeline."""
        # Step 1: Vector search for relevant subsections
        logger.info("Searching for relevant CCPA subsections...")
        search_results = self._vector_store.search(prompt, top_k=5)
        logger.info(f"Found {len(search_results)} relevant subsections")

        # Step 2: Get full parent sections (parent-document retrieval)
        subsection_ids = [r["id"] for r in search_results]
        parent_sections = self._kb.get_parent_sections(subsection_ids)
        logger.info(
            f"Retrieved {len(parent_sections)} parent sections"
        )

        # Step 3: Build LLM prompt with context
        full_prompt = self._prompt_builder.build_prompt(
            user_query=prompt,
            context_sections=parent_sections,
        )
        logger.info(f"Prompt built: {len(full_prompt)} characters")

        # Step 4: LLM inference
        logger.info("Running LLM inference...")
        raw_output = self._llm.generate(full_prompt)
        logger.info(f"LLM output: {raw_output[:200]}...")

        # Step 5: Parse and validate response
        result = parse_response(raw_output)
        logger.info(f"Analysis result: {result}")

        return result


# Module-level singleton
analyzer = Analyzer()
