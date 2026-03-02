---
phase: 1
plan: 2
wave: 1
depends_on: []
files_modified:
  - backend/app/services/prompt_builder.py
  - backend/app/core/response_parser.py
autonomous: true

must_haves:
  truths:
    - "Prompt uses Gemini's native format (no Llama chat tags)"
    - "Response parser handles Gemini's cleaner JSON output"
    - "DeepSeek <think> tag stripping is removed"
  artifacts:
    - "prompt_builder.py has no Llama-specific formatting"
    - "response_parser.py is simplified for Gemini output"
---

# Plan 1.2: Adapt Prompt Builder & Response Parser for Gemini

## Objective
Remove Llama 3.1 chat template formatting from prompt_builder.py and simplify response_parser.py for Gemini's cleaner output. These files have no dependency on Plan 1.1 (they don't import llm_engine), so they can execute in parallel.

Purpose: Gemini doesn't need `<|begin_of_text|>` tags or `<think>` tag stripping. Cleaner prompts = better Gemini output.

## Context
- .gsd/SPEC.md
- backend/app/services/prompt_builder.py (129 lines — Llama chat format)
- backend/app/core/response_parser.py (167 lines — DeepSeek think tags)

## Tasks

<task type="auto">
  <name>Rewrite prompt_builder.py for Gemini</name>
  <files>backend/app/services/prompt_builder.py</files>
  <action>
    Rewrite PromptBuilder to produce plain-text prompts (no Llama chat tags):
    1. Keep the same SYSTEM_PROMPT content and FEW_SHOT_EXAMPLES
    2. Remove all Llama 3.1 Instruct tags: <|begin_of_text|>, <|start_header_id|>, <|end_header_id|>, <|eot_id|>
    3. Instead, build the prompt as a simple structured string:
       - System instruction block
       - Few-shot examples block
       - Retrieved CCPA context sections
       - User query
       - Output instruction
    4. Keep the same build_prompt(user_query, context_sections) interface
    5. Keep the same module-level singleton

    AVOID: Don't use Gemini's multi-turn format — we're passing a single prompt string to generate_content().
    AVOID: Don't change the method signature — analyzer.py depends on it.
  </action>
  <verify>python -c "from app.services.prompt_builder import prompt_builder; p = prompt_builder.build_prompt('test', []); assert '<|' not in p; print('OK')"</verify>
  <done>
    - No Llama chat tags in prompt output
    - Same build_prompt() interface preserved
    - Few-shot examples and system prompt content intact
  </done>
</task>

<task type="auto">
  <name>Simplify response_parser.py for Gemini</name>
  <files>backend/app/core/response_parser.py</files>
  <action>
    Simplify the response parser:
    1. Remove DeepSeek <think> tag stripping (line 62)
    2. Keep all 4 JSON extraction strategies (direct, markdown fence, regex)
    3. Keep the validation and normalization logic
    4. Keep the SAFE_DEFAULT fallback behavior
    5. Keep _normalize_article() unchanged

    This is a minor change — just remove the one DeepSeek-specific line.

    AVOID: Don't change the parse_response() return type or interface.
  </action>
  <verify>python -c "from app.core.response_parser import parse_response; r = parse_response('{\"harmful\": true, \"articles\": [\"Section 1798.120\"]}'); assert r['harmful'] == True; print('OK')"</verify>
  <done>
    - No <think> tag references in code
    - parse_response() still works for direct JSON, markdown fences, and regex extraction
    - SAFE_DEFAULT fallback intact
  </done>
</task>

## Success Criteria
- [ ] prompt_builder.build_prompt() returns clean text with no Llama tags
- [ ] response_parser.parse_response() works without <think> stripping
- [ ] Both modules maintain their existing interfaces
