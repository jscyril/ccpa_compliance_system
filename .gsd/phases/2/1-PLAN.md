---
phase: 2
plan: 1
wave: 1
depends_on: []
files_modified:
  - backend/app/schemas/api.py
  - backend/app/services/prompt_builder.py
autonomous: true

must_haves:
  truths:
    - "API schema AnalyzeResponse includes explanation and referenced_articles"
    - "Prompt builder few-shot examples include the new fields"
    - "System prompt instructs Gemini to generate explanation and referenced_articles"
  artifacts:
    - "api.py AnalyzeResponse has 4 fields"
    - "prompt_builder.py SYSTEM_PROMPT is updated"
---

# Plan 2.1: Update API Schema & Prompt Builder

## Objective
Expand the `AnalyzeResponse` schema to include `explanation` and `referenced_articles`, and update the prompt builder to instruct Gemini to generate these new fields.

Purpose: Delivers REQ-03 from SPEC.md. Provides rich context to the frontend so users understand *why* a practice is harmful and *where* to look in the statute.

## Context
- .gsd/SPEC.md
- backend/app/schemas/api.py
- backend/app/services/prompt_builder.py

## Tasks

<task type="auto">
  <name>Expand AnalyzeResponse schema</name>
  <files>backend/app/schemas/api.py</files>
  <action>
    Update `AnalyzeResponse`:
    1. Keep `harmful: bool` and `articles: list[str]`
    2. Add `explanation: str` (A clear, concise explanation of the analysis)
    3. Add `referenced_articles: list[str]` (Specific excerpts or titles from the cited sections to provide context)

    Keep validation simple (just the types).

    AVOID: Don't change AnalyzeRequest.
  </action>
  <verify>python -c "from app.schemas.api import AnalyzeResponse; r = AnalyzeResponse(harmful=True, articles=[], explanation='test', referenced_articles=[]); assert hasattr(r, 'explanation'); print('OK')"</verify>
  <done>AnalyzeResponse schema has 4 fields: harmful, articles, explanation, referenced_articles.</done>
</task>

<task type="auto">
  <name>Update PromptBuilder for new schema</name>
  <files>backend/app/services/prompt_builder.py</files>
  <action>
    Update prompt_builder.py to generate the new 4-field JSON:

    1. Update SYSTEM_PROMPT:
       - Change output format instruction to: `{"harmful": true, "articles": ["Section 1798.xxx", ...], "explanation": "Why it violates...", "referenced_articles": ["Excerpt from statute..."]}`
       - Add rules: `explanation` must be a clear human-readable string. `referenced_articles` must contain short quotes or titles from the cited sections to prove the violation.
       - If harmful is false, `explanation` should explain why it complies, and `referenced_articles` should be empty `[]`.

    2. Update FEW_SHOT_EXAMPLES:
       - Update all 3 examples to use the new JSON format.
       - Example 1 (harmful): Add a clear explanation about selling data without opt-out.
       - Example 2 (safe): Add a clear explanation about honoring privacy policies.
       - Example 3 (harmful): Add a clear explanation about ignoring deletion requests.

    AVOID: Don't change build_prompt() method signature or logic. Just the prompt strings.
  </action>
  <verify>python -c "from app.services.prompt_builder import SYSTEM_PROMPT; assert 'explanation' in SYSTEM_PROMPT; assert 'referenced_articles' in SYSTEM_PROMPT; print('OK')"</verify>
  <done>prompt_builder.py instructs Gemini to return the 4-field JSON format.</done>
</task>

## Success Criteria
- [ ] `api.py` AnalyzeResponse reflects the new 4-field structure
- [ ] `prompt_builder.py` output format reflects the new 4-field structure
- [ ] All few-shot examples are updated to 4 fields
