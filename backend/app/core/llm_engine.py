"""
LLM Engine — Dual-Model with Timeout Fallback

Loads TWO models at startup:
  1. Primary:  DeepSeek-R1-Distill-Llama-8B  (best reasoning, ~5GB 4-bit)
  2. Fallback: microsoft/Phi-4-mini-reasoning (faster, ~3GB 4-bit)

On each generate() call:
  - Tries the primary model with a 90-second timeout.
  - If the primary times out or fails, immediately retries with the fallback.
  - Both models produce the same strict JSON output format.

Supports CUDA (4-bit quantized), MPS (Apple Silicon), and CPU modes.
"""

import logging
import os
import threading
from typing import Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

logger = logging.getLogger(__name__)

# Dual-model configuration
PRIMARY_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
FALLBACK_MODEL = "microsoft/Phi-4-mini-reasoning"

# Timeout for primary model inference (seconds)
PRIMARY_TIMEOUT_SECONDS = 90


class _SingleModel:
    """Wraps a single model + tokenizer pair."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.device = None

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.tokenizer is not None

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Run inference and return the generated text."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self.model.device)

        input_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        new_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return response.strip()


class LLMEngine:
    """Dual-model engine with timeout-based fallback."""

    def __init__(self):
        self._primary = _SingleModel(PRIMARY_MODEL)
        self._fallback = _SingleModel(FALLBACK_MODEL)

    @property
    def is_ready(self) -> bool:
        """At least one model must be loaded."""
        return self._primary.is_ready or self._fallback.is_ready

    def load(self) -> None:
        """
        Load both models at startup. Each model independently tries
        the best available strategy (4-bit GPU > float16 GPU > float32 MPS > float16 CPU).

        If a model fails to load entirely, it's skipped (the other one
        must succeed or we raise RuntimeError).
        """
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            logger.warning("HF_TOKEN not set. Some models may not be accessible.")

        has_cuda = torch.cuda.is_available()
        has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        logger.info(f"CUDA available: {has_cuda}, MPS available: {has_mps}")
        if has_cuda:
            logger.info(
                f"GPU: {torch.cuda.get_device_name(0)}, "
                f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f}GB"
            )

        # Load primary model
        logger.info(f"=== Loading PRIMARY model: {PRIMARY_MODEL} ===")
        self._load_model(self._primary, hf_token, has_cuda, has_mps)

        # Load fallback model
        logger.info(f"=== Loading FALLBACK model: {FALLBACK_MODEL} ===")
        self._load_model(self._fallback, hf_token, has_cuda, has_mps)

        if not self.is_ready:
            raise RuntimeError(
                "Failed to load any model. Check HF_TOKEN and available memory."
            )

        loaded = []
        if self._primary.is_ready:
            loaded.append(f"Primary: {PRIMARY_MODEL} on {self._primary.device}")
        if self._fallback.is_ready:
            loaded.append(f"Fallback: {FALLBACK_MODEL} on {self._fallback.device}")
        logger.info(f"Models loaded: {', '.join(loaded)}")

    def _load_model(
        self, wrapper: _SingleModel, hf_token: str, has_cuda: bool, has_mps: bool
    ) -> None:
        """Try loading a single model with the best available strategy."""
        strategies = []
        if has_cuda:
            strategies.append(("4-bit quantized (GPU)", self._load_quantized))
            strategies.append(("float16 (GPU)", self._load_float16_gpu))
        if has_mps:
            strategies.append(("float32 (MPS)", self._load_float32_mps))
        strategies.append(("float16 (CPU)", self._load_float16_cpu))

        for strategy_name, load_fn in strategies:
            try:
                logger.info(f"Trying: {wrapper.model_id} — {strategy_name}")
                load_fn(wrapper, hf_token)
                wrapper.device = next(wrapper.model.parameters()).device
                logger.info(
                    f"Loaded: {wrapper.model_id} via {strategy_name} "
                    f"on device: {wrapper.device}"
                )
                return
            except Exception as e:
                logger.warning(f"Failed [{strategy_name}] {wrapper.model_id}: {e}")
                wrapper.model = None
                wrapper.tokenizer = None
                continue

        logger.error(f"Could not load {wrapper.model_id} with any strategy.")

    # ───────────────────── Loading strategies ─────────────────────

    def _load_tokenizer(self, wrapper: _SingleModel, hf_token: Optional[str]) -> None:
        wrapper.tokenizer = AutoTokenizer.from_pretrained(
            wrapper.model_id, token=hf_token, trust_remote_code=True,
        )
        if wrapper.tokenizer.pad_token is None:
            wrapper.tokenizer.pad_token = wrapper.tokenizer.eos_token

    def _load_quantized(self, wrapper: _SingleModel, hf_token: Optional[str]) -> None:
        self._load_tokenizer(wrapper, hf_token)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        wrapper.model = AutoModelForCausalLM.from_pretrained(
            wrapper.model_id,
            quantization_config=bnb_config,
            device_map="auto",
            token=hf_token,
            trust_remote_code=True,
        )

    def _load_float16_gpu(self, wrapper: _SingleModel, hf_token: Optional[str]) -> None:
        self._load_tokenizer(wrapper, hf_token)
        wrapper.model = AutoModelForCausalLM.from_pretrained(
            wrapper.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            token=hf_token,
            trust_remote_code=True,
        )

    def _load_float32_mps(self, wrapper: _SingleModel, hf_token: Optional[str]) -> None:
        self._load_tokenizer(wrapper, hf_token)
        wrapper.model = AutoModelForCausalLM.from_pretrained(
            wrapper.model_id,
            torch_dtype=torch.float32,
            device_map="cpu",
            token=hf_token,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )
        wrapper.model = wrapper.model.to("mps")

    def _load_float16_cpu(self, wrapper: _SingleModel, hf_token: Optional[str]) -> None:
        self._load_tokenizer(wrapper, hf_token)
        wrapper.model = AutoModelForCausalLM.from_pretrained(
            wrapper.model_id,
            torch_dtype=torch.float16,
            device_map="cpu",
            token=hf_token,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

    # ───────────────────── Inference with fallback ─────────────────────

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text with timeout-based fallback.

        1. Try primary model with a 90-second timeout.
        2. If primary times out or fails, use fallback model (no timeout).
        3. If both fail, raise RuntimeError (caught by analyzer → safe default).
        """
        if not self.is_ready:
            raise RuntimeError("No models loaded. Call load() first.")

        # Try primary model with timeout
        if self._primary.is_ready:
            result = self._generate_with_timeout(
                self._primary, prompt, max_new_tokens, PRIMARY_TIMEOUT_SECONDS
            )
            if result is not None:
                return result

        # Fallback model (no timeout — must complete)
        if self._fallback.is_ready:
            logger.info(
                f"Using fallback model: {self._fallback.model_id}"
            )
            try:
                result = self._fallback.generate(prompt, max_new_tokens)
                logger.info(f"Fallback model succeeded")
                return result
            except Exception as e:
                logger.error(f"Fallback model failed: {e}")

        raise RuntimeError("Both primary and fallback models failed.")

    def _generate_with_timeout(
        self, wrapper: _SingleModel, prompt: str, max_new_tokens: int, timeout: int
    ) -> Optional[str]:
        """Run inference in a thread with a timeout. Returns None on timeout/error."""
        result_container = {"output": None, "error": None}

        def _run():
            try:
                result_container["output"] = wrapper.generate(prompt, max_new_tokens)
            except Exception as e:
                result_container["error"] = e

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            logger.warning(
                f"Primary model ({wrapper.model_id}) timed out "
                f"after {timeout}s — switching to fallback"
            )
            return None

        if result_container["error"]:
            logger.warning(
                f"Primary model error: {result_container['error']} — "
                f"switching to fallback"
            )
            return None

        return result_container["output"]


# Module-level singleton
llm_engine = LLMEngine()
