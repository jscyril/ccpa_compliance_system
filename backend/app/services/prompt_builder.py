"""
Prompt Builder

Constructs LLM prompts with Llama 3.1 Instruct chat format,
few-shot examples, and CCPA context injection for compliance analysis.

Prompt structure:
1. System instruction (CCPA Compliance Auditor role)
2. Few-shot examples (3: 2 harmful, 1 safe)
3. Retrieved CCPA context sections
4. User query
5. Output marker
"""


# Few-shot examples for the prompt
FEW_SHOT_EXAMPLES = [
    {
        "practice": (
            "A company collects personal data from users and sells it to "
            "third-party advertisers without informing users or providing "
            "any option to opt out of the sale."
        ),
        "output": '{"harmful": true, "articles": ["Section 1798.120"]}',
    },
    {
        "practice": (
            "A company maintains a clear and accessible privacy policy that "
            "details exactly what data is collected, provides a 'Do Not Sell "
            "My Personal Information' link, and honors all opt-out requests "
            "within 15 business days."
        ),
        "output": '{"harmful": false, "articles": []}',
    },
    {
        "practice": (
            "A consumer submits a verified request to delete their personal "
            "data, but the company ignores the request and continues to "
            "retain and use the data for marketing purposes."
        ),
        "output": '{"harmful": true, "articles": ["Section 1798.105"]}',
    },
]

SYSTEM_PROMPT = """You are a CCPA Compliance Auditor. Your job is to analyze business data practices against the California Consumer Privacy Act (CCPA) statute.

Given a description of a business practice:
1. Determine if it violates any CCPA section
2. Identify the specific section(s) violated

Output ONLY valid JSON in exactly this format:
{"harmful": true, "articles": ["Section 1798.xxx", ...]}

If the practice does NOT violate the CCPA:
{"harmful": false, "articles": []}

Rules:
- Output ONLY the JSON. No explanation, no markdown, no additional text.
- Articles must use the format "Section 1798.xxx"
- If harmful is false, articles must be an empty list []
- If harmful is true, articles must contain at least one section
- Only cite sections you are confident about"""


class PromptBuilder:
    """Builds prompts for CCPA compliance analysis using Llama 3.1 chat format."""

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
            Complete prompt string in Llama 3.1 chat format.
        """
        # Build the system message with few-shot examples
        system_content = SYSTEM_PROMPT + "\n\n"
        system_content += "Here are examples of correct analysis:\n\n"

        for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
            system_content += f"Example {i}:\n"
            system_content += f"Practice: {example['practice']}\n"
            system_content += f"Output: {example['output']}\n\n"

        # Build the user message with context and query
        user_content = ""

        # Add retrieved CCPA sections as context (truncated to fit context window)
        MAX_SECTION_CHARS = 2000
        MAX_SECTIONS = 3
        if context_sections:
            user_content += "Relevant CCPA Statute Sections:\n\n"
            for section in context_sections[:MAX_SECTIONS]:
                sid = section.get("section_id", "Unknown")
                title = section.get("title", "")
                text = section.get("full_text", "")
                if len(text) > MAX_SECTION_CHARS:
                    text = text[:MAX_SECTION_CHARS] + "... [truncated]"
                user_content += f"--- Section {sid}: {title} ---\n"
                user_content += f"{text}\n\n"

        user_content += f"Business Practice to Analyze:\n{user_query}\n\n"
        user_content += "Provide your analysis as JSON only:"

        # Format as Llama 3.1 Instruct chat template
        prompt = (
            "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_content}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            f"{user_content}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        return prompt


# Module-level singleton
prompt_builder = PromptBuilder()
