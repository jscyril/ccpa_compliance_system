"""
LLM Engine

Loads and manages an LLM for CCPA compliance analysis.
Supports CUDA (4-bit quantized), MPS (Apple Silicon), and CPU modes.

Model priority: Llama 3.2 3B → Qwen 2.5 3B (fallback)

The model is loaded lazily via load() — called during FastAPI startup,
not at import time.
"""

import logging
import os
from typing import Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

logger = logging.getLogger(__name__)

# Model priority: 3B models fit in 24GB RAM
PRIMARY_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
FALLBACK_MODEL = "Qwen/Qwen2.5-3B-Instruct"


class LLMEngine:
    """Manages quantized LLM loading and inference."""

    def __init__(self, model_name: str = PRIMARY_MODEL):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._device = None

    @property
    def is_ready(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        return self._model is not None and self._tokenizer is not None

    def load(self) -> None:
        """
        Load the model, trying multiple strategies:
        1. 4-bit quantized on CUDA GPU (fastest, lowest VRAM)
        2. float16 on GPU without quantization
        3. float16 on CPU (slowest, needs ~16GB RAM, but always works)

        For each strategy, tries primary model then fallback model.
        """
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            logger.warning(
                "HF_TOKEN not set. Some models may not be accessible."
            )

        has_cuda = torch.cuda.is_available()
        has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        logger.info(f"CUDA available: {has_cuda}, MPS available: {has_mps}")
        if has_cuda:
            logger.info(
                f"GPU: {torch.cuda.get_device_name(0)}, "
                f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f}GB"
            )

        models_to_try = [self.model_name]
        if self.model_name == PRIMARY_MODEL:
            models_to_try.append(FALLBACK_MODEL)

        # Build loading strategies in priority order
        strategies = []
        if has_cuda:
            strategies.append(("4-bit quantized (GPU)", self._load_quantized))
            strategies.append(("float16 (GPU)", self._load_float16_gpu))
        if has_mps:
            strategies.append(("float16 (MPS/Apple Silicon)", self._load_float16_mps))
        strategies.append(("float16 (CPU)", self._load_float16_cpu))

        for strategy_name, load_fn in strategies:
            for model_id in models_to_try:
                try:
                    logger.info(
                        f"Trying: {model_id} — {strategy_name}"
                    )
                    load_fn(model_id, hf_token)
                    self.model_name = model_id
                    self._device = next(self._model.parameters()).device
                    logger.info(
                        f"Model loaded successfully: {model_id} "
                        f"via {strategy_name} on device: {self._device}"
                    )
                    return

                except Exception as e:
                    logger.warning(
                        f"Failed [{strategy_name}] {model_id}: {e}"
                    )
                    self._model = None
                    self._tokenizer = None
                    continue

        raise RuntimeError(
            f"Failed to load any model with any strategy. "
            f"Tried: {models_to_try}. Check HF_TOKEN and available memory."
        )

    def _load_tokenizer(self, model_id: str, hf_token: Optional[str]) -> None:
        """Load tokenizer for a model."""
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=hf_token,
            trust_remote_code=True,
        )
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

    def _load_quantized(self, model_id: str, hf_token: Optional[str]) -> None:
        """Strategy 1: 4-bit quantized on CUDA GPU."""
        self._load_tokenizer(model_id, hf_token)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            token=hf_token,
            trust_remote_code=True,
        )

    def _load_float16_gpu(self, model_id: str, hf_token: Optional[str]) -> None:
        """Strategy 2: float16 on GPU without quantization."""
        self._load_tokenizer(model_id, hf_token)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            token=hf_token,
            trust_remote_code=True,
        )

    def _load_float16_mps(self, model_id: str, hf_token: Optional[str]) -> None:
        """Strategy: float16 on Apple Silicon MPS (Metal)."""
        self._load_tokenizer(model_id, hf_token)
        # Load to CPU first, then move to MPS (device_map doesn't support MPS)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="cpu",
            token=hf_token,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )
        self._model = self._model.to("mps")

    def _load_float16_cpu(self, model_id: str, hf_token: Optional[str]) -> None:
        """Strategy: float16 on CPU (no GPU required)."""
        self._load_tokenizer(model_id, hf_token)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="cpu",
            token=hf_token,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The full prompt string (including system/user formatting).
            max_new_tokens: Maximum number of new tokens to generate.
            temperature: Sampling temperature (low = more deterministic).

        Returns:
            The generated text (excluding the input prompt).
        """
        if not self.is_ready:
            raise RuntimeError("Model not loaded. Call load() first.")

        inputs = self._tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self._model.device)

        input_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self._tokenizer.pad_token_id,
            )

        # Decode only the NEW tokens (exclude input)
        new_tokens = outputs[0][input_length:]
        response = self._tokenizer.decode(new_tokens, skip_special_tokens=True)

        return response.strip()


# Module-level singleton (loaded lazily via load())
llm_engine = LLMEngine()
