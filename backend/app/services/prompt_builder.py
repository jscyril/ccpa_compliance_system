"""
Prompt Builder

Constructs prompts for Gemini API with few-shot examples and
CCPA context injection for compliance analysis.

Prompt structure:
1. System instruction (CCPA Compliance Auditor role)
2. Few-shot examples (3: 2 harmful, 1 safe)
3. Retrieved CCPA context sections
4. User query
5. Output instruction
"""


# Few-shot examples for the prompt
FEW_SHOT_EXAMPLES = [
    {
        "practice": (
            "A company collects personal data from users and sells it to "
            "third-party advertisers without informing users or providing "
            "any option to opt out of the sale."
        ),
        "output": '{"harmful": true, "articles": ["Section 1798.120"], "explanation": "The CCPA grants consumers the right to opt-out of the sale of their personal information. Selling data without informing users or providing an opt-out mechanism is a direct violation.", "referenced_articles": ["A consumer shall have the right, at any time, to direct a business that sells or shares personal information about the consumer to third parties not to sell or share the consumer\'s personal information."]}',
    },
    {
        "practice": (
            "A company maintains a clear and accessible privacy policy that "
            "details exactly what data is collected, provides a 'Do Not Sell "
            "My Personal Information' link, and honors all opt-out requests "
            "within 15 business days."
        ),
        "output": '{"harmful": false, "articles": [], "explanation": "The company provides the required notice and honors opt-out requests within the statutory 15-day window, fully complying with CCPA requirements.", "referenced_articles": []}',
    },
    {
        "practice": (
            "A consumer submits a verified request to delete their personal "
            "data, but the company ignores the request and continues to "
            "retain and use the data for marketing purposes."
        ),
        "output": '{"harmful": true, "articles": ["Section 1798.105"], "explanation": "Businesses must respect verified deletion requests. Retaining and using the data for marketing after a deletion request is a violation.", "referenced_articles": ["A business that receives a verifiable consumer request from a consumer to delete the consumer\'s personal information [...] shall delete the consumer\'s personal information from its records."]}',
    },
]

SYSTEM_PROMPT = """You are a CCPA Compliance Auditor. Your job is to analyze business data practices against the California Consumer Privacy Act (CCPA) statute.

Given a description of a business practice:
1. Determine if it violates any CCPA section
2. Identify the specific section(s) violated

Output ONLY valid JSON in exactly this format:
{"harmful": true, "articles": ["Section 1798.xxx", ...], "explanation": "Why it violates...", "referenced_articles": ["Excerpt from statute..."]}

If the practice does NOT violate the CCPA:
{"harmful": false, "articles": [], "explanation": "Why it complies...", "referenced_articles": []}

Rules:
- Output ONLY the JSON. No explanation, no markdown, no additional text.
- Articles must use the format "Section 1798.xxx"
- If harmful is false, explanation should explain why, and referenced_articles must be an empty list []
- If harmful is true, articles must contain at least one section
- The explanation must be a clear human-readable string.
- The referenced_articles must contain short quotes or titles from the cited sections to prove the violation.
- Only cite sections you are confident about"""


class PromptBuilder:
    """Builds prompts for CCPA compliance analysis."""

    def build_prompt(
        self,
        user_query: str,
        context_sections: list[dict],
    ) -> str:
        """
        Build a complete prompt with system instruction, few-shot examples,
        retrieved CCPA context, and user query.

        Args:
            user_query: The business practice to analyze.
            context_sections: Retrieved CCPA sections (from vector search).
                Each dict should have: section_id, title, full_text

        Returns:
            Complete prompt string for Gemini API.
        """
        parts = []

        # System instruction
        parts.append(SYSTEM_PROMPT)
        parts.append("")

        # Few-shot examples
        parts.append("Here are examples of correct analysis:")
        parts.append("")
        for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
            parts.append(f"Example {i}:")
            parts.append(f"Practice: {example['practice']}")
            parts.append(f"Output: {example['output']}")
            parts.append("")

        # Retrieved CCPA context sections
        MAX_SECTION_CHARS = 2000
        MAX_SECTIONS = 3
        if context_sections:
            parts.append("Relevant CCPA Statute Sections:")
            parts.append("")
            for section in context_sections[:MAX_SECTIONS]:
                sid = section.get("section_id", "Unknown")
                title = section.get("title", "")
                text = section.get("full_text", "")
                if len(text) > MAX_SECTION_CHARS:
                    text = text[:MAX_SECTION_CHARS] + "... [truncated]"
                parts.append(f"--- Section {sid}: {title} ---")
                parts.append(text)
                parts.append("")

        # User query
        parts.append(f"Business Practice to Analyze:")
        parts.append(user_query)
        parts.append("")
        parts.append("Provide your analysis as JSON only:")

        return "\n".join(parts)


# Module-level singleton
prompt_builder = PromptBuilder()
