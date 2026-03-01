---
phase: 2
plan: 2
wave: 2
---

# Plan 2.2: Prompt Engineering & Response Parsing

## Objective
Build the prompt template with few-shot examples and CCPA context injection, plus the strict JSON response parser with confidence-based fallback to avoid the "zero marks" trap.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- .gsd/DECISIONS.md (ADR-3, ADR-4)
- backend/app/services/prompt_builder.py (empty stub)
- backend/app/core/response_parser.py (empty stub)
- backend/app/services/ccpa_knowledge.py (Phase 1)

## Tasks

<task type="auto">
  <name>Implement prompt builder with few-shot examples</name>
  <files>backend/app/services/prompt_builder.py</files>
  <action>
    Create a PromptBuilder class with a `build_prompt(user_query: str, context_sections: list[dict]) -> str` method.

    The prompt MUST follow this exact structure:
    1. **System instruction**: "You are a CCPA Compliance Auditor. Analyze the following business practice against the provided CCPA statute sections. Output ONLY valid JSON with no additional text."
    2. **Output format instruction**: Specify exact schema:
       ```
       {"harmful": true/false, "articles": ["Section 1798.xxx", ...]}
       If not harmful, articles must be an empty list [].
       ```
    3. **Few-shot examples** (3 examples):
       Example 1 (harmful): Selling data without opt-out → Section 1798.120
       Example 2 (safe): Company provides clear privacy policy with opt-out → not harmful
       Example 3 (harmful): Ignoring deletion requests → Section 1798.105
    4. **Retrieved CCPA context**: The actual statute text from retrieved sections
    5. **User query**: The business practice to analyze
    6. **Output marker**: "JSON Output:"

    For Llama 3.1 Instruct format, wrap in the chat template:
    - Use `<|begin_of_text|><|start_header_id|>system<|end_header_id|>` for system message
    - Use `<|start_header_id|>user<|end_header_id|>` for user message
    - Use `<|start_header_id|>assistant<|end_header_id|>` for assistant response start

    CRITICAL: The few-shot examples must use the EXACT output format expected: {"harmful": bool, "articles": [...]}
    CRITICAL: Articles must use format "Section 1798.XXX" (with "Section" prefix)
    AVOID: Do NOT include explanations in few-shot outputs — JSON only.
  </action>
  <verify>cd backend && python -c "
from app.services.prompt_builder import PromptBuilder
pb = PromptBuilder()
prompt = pb.build_prompt('A company sells user data.', [{'section_id': '1798.120', 'title': 'Test', 'full_text': 'Test text'}])
assert 'harmful' in prompt
assert '1798.120' in prompt
assert 'JSON' in prompt
print(f'Prompt length: {len(prompt)} chars')
print('PASS: Prompt contains required elements')
"</verify>
  <done>PromptBuilder generates Llama 3.1 chat-format prompt with system instruction, 3 few-shot examples, context sections, and user query</done>
</task>

<task type="auto">
  <name>Implement strict JSON response parser with fallback</name>
  <files>backend/app/core/response_parser.py</files>
  <action>
    Create a `parse_response(raw_output: str) -> dict` function that:
    1. Attempts to extract JSON from the LLM's raw output:
       - Try direct `json.loads(raw_output.strip())`
       - If that fails, search for JSON within markdown code fences: ```json...```
       - If that fails, use regex to find `{...}` pattern in the text
    2. Validates the extracted JSON:
       - `harmful` must be a boolean (True/False)
       - `articles` must be a list of strings
       - If `harmful` is False, `articles` must be empty `[]`
       - If `harmful` is True, `articles` must be non-empty
    3. Normalizes article format:
       - Ensure each article starts with "Section " prefix
       - e.g., "1798.120" → "Section 1798.120"
       - e.g., "Section 1798.120(a)" → "Section 1798.120(a)" (keep as-is)
       - e.g., "Article 1798.120" → "Section 1798.120" (normalize prefix)
    4. **Confidence fallback (ADR-4)**:
       - If JSON parsing fails entirely → return `{"harmful": false, "articles": []}`
       - If `harmful` is True but articles list is empty → return `{"harmful": false, "articles": []}`
       - This is the "zero marks trap" defense: better to miss than to guess wrong

    CRITICAL: This function must NEVER raise an exception — always return valid JSON.
    CRITICAL: Return a plain dict, not a Pydantic model (conversion happens at API layer).
  </action>
  <verify>cd backend && python -c "
from app.core.response_parser import parse_response

# Test 1: Valid JSON
r = parse_response('{\"harmful\": true, \"articles\": [\"Section 1798.120\"]}')
assert r == {'harmful': True, 'articles': ['Section 1798.120']}, f'Test 1 failed: {r}'

# Test 2: JSON in markdown fence
r = parse_response('Here is the answer:\n\`\`\`json\n{\"harmful\": false, \"articles\": []}\n\`\`\`')
assert r == {'harmful': False, 'articles': []}, f'Test 2 failed: {r}'

# Test 3: Garbage input → fallback
r = parse_response('I think this might violate something but I am not sure')
assert r == {'harmful': False, 'articles': []}, f'Test 3 failed: {r}'

# Test 4: harmful true but empty articles → fallback
r = parse_response('{\"harmful\": true, \"articles\": []}')
assert r == {'harmful': False, 'articles': []}, f'Test 4 failed: {r}'

# Test 5: Normalize article format
r = parse_response('{\"harmful\": true, \"articles\": [\"1798.120\"]}')
assert r['articles'] == ['Section 1798.120'], f'Test 5 failed: {r}'

print('All 5 parser tests passed')
"</verify>
  <done>parse_response() handles valid JSON, markdown fences, garbage input, and normalizes article prefixes. Fallback always returns safe default.</done>
</task>

## Success Criteria
- [ ] PromptBuilder produces Llama 3.1 chat-format prompt with system instruction + 3 few-shot examples
- [ ] Prompt includes retrieved CCPA context and user query
- [ ] parse_response() extracts JSON from multiple output formats
- [ ] parse_response() normalizes article format to "Section 1798.XXX"
- [ ] Fallback returns `{"harmful": false, "articles": []}` on any error
- [ ] All 5 parser unit tests pass
