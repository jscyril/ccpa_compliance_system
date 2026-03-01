"""
LLM Engine

Loads and manages a quantized LLM (Llama 3.1 8B Instruct or Mistral 7B fallback)
for CCPA compliance analysis. Uses bitsandbytes 4-bit quantization to fit
within consumer GPU VRAM.

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

# Model priority: try Llama first, fall back to Mistral
PRIMARY_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"


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
        Load the model with 4-bit quantization.

        Tries the primary model first; if it fails (e.g., gated model,
        insufficient VRAM), falls back to the secondary model.
        """
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            logger.warning(
                "HF_TOKEN not set. Some models may not be accessible."
            )

        # 4-bit quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        models_to_try = [self.model_name]
        if self.model_name == PRIMARY_MODEL:
            models_to_try.append(FALLBACK_MODEL)

        for model_id in models_to_try:
            try:
                logger.info(f"Loading model: {model_id}")
                self._tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    token=hf_token,
                    trust_remote_code=True,
                )

                # Ensure pad token is set
                if self._tokenizer.pad_token is None:
                    self._tokenizer.pad_token = self._tokenizer.eos_token

                self._model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=bnb_config,
                    device_map="auto",
                    token=hf_token,
                    trust_remote_code=True,
                )

                self.model_name = model_id
                self._device = next(self._model.parameters()).device
                logger.info(
                    f"Model loaded successfully: {model_id} "
                    f"on device: {self._device}"
                )
                return

            except Exception as e:
                logger.error(f"Failed to load {model_id}: {e}")
                self._model = None
                self._tokenizer = None
                if model_id != models_to_try[-1]:
                    logger.info("Trying fallback model...")
                continue

        raise RuntimeError(
            f"Failed to load any model. Tried: {models_to_try}. "
            "Check HF_TOKEN and GPU availability."
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
