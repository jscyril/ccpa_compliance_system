"""
CCPA Compliance Analyzer — FastAPI Application

Exposes:
- POST /analyze — Analyze a business practice against CCPA
- GET /health — Health check (model loaded and ready)

On startup, loads the LLM and builds the vector search index.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.core.llm_engine import llm_engine
from app.core.vector_store import vector_store
from app.schemas.api import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import analyzer
from app.services.ccpa_knowledge import ccpa_kb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Safe default response
SAFE_DEFAULT = AnalyzeResponse(harmful=False, articles=[])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Startup: load model and build index
    logger.info("=" * 60)
    logger.info("STARTING CCPA COMPLIANCE ANALYZER")
    logger.info("=" * 60)

    try:
        # Load LLM
        logger.info("Loading LLM engine...")
        llm_engine.load()
        logger.info("LLM engine loaded successfully")

        # Build vector index
        logger.info("Building vector search index...")
        subsections = ccpa_kb.get_all_subsections()
        vector_store.build_index(subsections)
        logger.info(f"Vector index built with {len(subsections)} subsections")

        logger.info("=" * 60)
        logger.info("SERVER READY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        # Don't crash — /health will report not ready

    yield

    # Shutdown (nothing to clean up)
    logger.info("Shutting down CCPA Compliance Analyzer")


app = FastAPI(
    title="CCPA Compliance Analyzer",
    description="Analyze business practices against the CCPA statute",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check endpoint — returns 200 when ready, 503 when not."""
    if llm_engine.is_ready and vector_store.is_ready:
        return {"status": "healthy"}
    raise HTTPException(
        status_code=503,
        detail="Service not ready. Model or index not loaded.",
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze a business practice for CCPA compliance.

    Returns strict JSON: {"harmful": bool, "articles": [...]}
    """
    try:
        result = analyzer.analyze(request.prompt)
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Analyze endpoint error: {e}", exc_info=True)
        return SAFE_DEFAULT


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all: never return anything except valid JSON."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        content={"harmful": False, "articles": []},
        status_code=200,
    )
