---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: LLM Engine & Vector Store

## Objective
Implement the two core inference components: the quantized LLM engine for text generation and the ChromaDB vector store with bge-small-en-v1.5 embeddings for semantic search over CCPA subsections.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- .gsd/DECISIONS.md (ADR-1, ADR-2, ADR-5)
- backend/app/core/llm_engine.py (empty stub)
- backend/app/services/ccpa_knowledge.py (implemented in Phase 1)
- backend/requirements.txt

## Tasks

<task type="auto">
  <name>Implement LLM engine with 4-bit quantization</name>
  <files>backend/app/core/llm_engine.py</files>
  <action>
    Create an LLMEngine class that:
    1. Reads `HF_TOKEN` from `os.environ.get("HF_TOKEN")` — MUST NOT hardcode token
    2. Loads `meta-llama/Llama-3.1-8B-Instruct` using transformers AutoModelForCausalLM
       with bitsandbytes 4-bit quantization config:
       - `load_in_4bit=True`
       - `bnb_4bit_compute_dtype=torch.float16`
       - `bnb_4bit_quant_type="nf4"`
    3. Loads the matching tokenizer via AutoTokenizer
    4. Exposes a `generate(prompt: str, max_new_tokens: int = 1024) -> str` method:
       - Tokenize the prompt
       - Run model.generate with `temperature=0.1`, `do_sample=True`, `top_p=0.9`
       - Decode and return only the NEW tokens (exclude input tokens)
    5. Exposes an `is_ready() -> bool` property to check if model is loaded
    6. Handle model loading in a separate `load()` method (called during startup, not __init__)

    CRITICAL: Use `device_map="auto"` for automatic GPU/CPU placement.
    CRITICAL: Pass `token=hf_token` to both from_pretrained calls.
    AVOID: Do NOT use pipeline() — we need fine control over generation params.
    AVOID: Do NOT import bitsandbytes directly — just use the BitsAndBytesConfig from transformers.
    FALLBACK: If Llama fails to load (e.g., gated model), catch the error and try `mistralai/Mistral-7B-Instruct-v0.3` as backup.
  </action>
  <verify>cd backend && python -c "
from app.core.llm_engine import LLMEngine
engine = LLMEngine()
print(f'Model name: {engine.model_name}')
print(f'Ready before load: {engine.is_ready}')
print('LLMEngine class instantiates without error')
"</verify>
  <done>LLMEngine class instantiates, has generate() method, load() method, and is_ready property. Token read from env var.</done>
</task>

<task type="auto">
  <name>Implement ChromaDB vector store with bge-small embeddings</name>
  <files>backend/app/core/vector_store.py (NEW)</files>
  <action>
    Create a VectorStore class that:
    1. Uses ChromaDB's in-memory client (`chromadb.Client()`)
    2. Creates a collection named "ccpa_subsections"
    3. Uses `sentence-transformers` to load `BAAI/bge-small-en-v1.5` as the embedding model
       - Use SentenceTransformer directly, NOT chromadb's built-in embedding
       - This gives us control over batching and the model instance
    4. Exposes a `build_index(subsections: list[dict])` method:
       - Takes the output of `ccpa_kb.get_all_subsections()`
       - Embeds each subsection's "text" field
       - Adds documents to ChromaDB with IDs and metadata (parent_section_id)
    5. Exposes a `search(query: str, top_k: int = 5) -> list[dict]` method:
       - Embeds the query using the same model
       - Queries ChromaDB for nearest neighbors
       - Returns list of dicts with: id, text, parent_section_id, distance
    6. Exposes an `is_ready() -> bool` property

    IMPORTANT: The embedding model (bge-small, ~130MB) is separate from the LLM.
    It should be loaded on CPU to save GPU VRAM for the LLM.
    Use `SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")`

    AVOID: Do NOT use chromadb's default embedding function — we need our own model.
    AVOID: Do NOT persist the collection to disk — in-memory is sufficient.
  </action>
  <verify>cd backend && python -c "
from app.core.vector_store import VectorStore
vs = VectorStore()
print(f'Ready before build: {vs.is_ready}')
print('VectorStore class instantiates without error')
print('Has build_index:', hasattr(vs, 'build_index'))
print('Has search:', hasattr(vs, 'search'))
"</verify>
  <done>VectorStore class instantiates, has build_index() and search() methods, uses bge-small-en-v1.5 on CPU</done>
</task>

## Success Criteria
- [ ] LLMEngine loads Llama 3.1 8B with 4-bit quantization (or Mistral fallback)
- [ ] LLMEngine.generate() returns decoded text (excluding input tokens)
- [ ] HF_TOKEN read from environment only
- [ ] VectorStore uses ChromaDB in-memory with bge-small-en-v1.5 on CPU
- [ ] VectorStore.search() returns ranked results with parent_section_id
