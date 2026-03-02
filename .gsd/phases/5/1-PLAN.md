---
phase: 5
plan: 1
wave: 1
depends_on: []
files_modified:
  - backend/scripts/test_integration.py
autonomous: true

must_haves:
  truths:
    - "A functional integration test script exists that tests both endpoints and streaming"
    - "End-to-end latency is measured for queries"
  artifacts:
    - "backend/scripts/test_integration.py exists and handles API keys"
---

# Plan 5.1: End-to-End Testing

## Objective
Create a comprehensive integration test script to verify that the CCPA Compliance Analyzer API correctly handles standard queries, streaming queries, and authentication. This script will double as a benchmark to ensure we meet the <2s response time goal from SPEC.md.

Purpose: Verifies the "high performance" and "rich response schema" goals, ensuring the system is ready for frontend consumption.

## Context
- .gsd/SPEC.md
- backend/app/main.py

## Tasks

<task type="auto">
  <name>Create Integration Test Script</name>
  <files>backend/scripts/test_integration.py</files>
  <action>
    Create a new standalone Python script `backend/scripts/test_integration.py`.
    The script should:
    1. Import `requests`, `time`, `json`, `os`, `sseclient` (or parse SSE manually).
    2. Read `API_KEY` from environment (fallback to empty if not set).
    3. Test `GET /health` to ensure the server is up.
    4. Test `POST /analyze` with a known harmful prompt. Extract and print the response time. Assert the schema contains `harmful`, `articles`, `explanation`, and `referenced_articles`.
    5. Test `GET /analyze/stream` with a known safe prompt. Capture chunks and print the total streaming time.

    AVOID: Do not use pytest for this; keep it as a standalone executable script that a user could easily run against a deployed environment. Use standard library or `requests` only if possible. A simple custom generator parsing `data: ` is preferred for SSE to avoid extra dependencies.
  </action>
  <verify>python -c "import os; assert os.path.exists('backend/scripts/test_integration.py'); print('OK')"</verify>
  <done>test_integration.py is created and contains testing logic.</done>
</task>

<task type="auto">
  <name>Update Requirements for Testing</name>
  <files>backend/requirements.txt</files>
  <action>
    Add `requests` to `backend/requirements.txt` if not already present, so the test script can be run easily from the root environment.
  </action>
  <verify>grep -q "requests" backend/requirements.txt</verify>
  <done>requests is listed in requirements.txt.</done>
</task>

## Success Criteria
- [ ] `test_integration.py` successfully executes against a running instance
- [ ] Latency is measured and printed for both standard and streaming requests
- [ ] Requirements contains necessary testing dependencies
