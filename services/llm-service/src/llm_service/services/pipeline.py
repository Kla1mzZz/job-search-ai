import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.llm_service.core.config import config, LLMConfig
from src.llm_service.core.logger import logger


class LLMPipeline:
    _instance = None

    def __new__(cls, config: LLMConfig):
        if cls._instance is None:
            cls._instance = super(LLMPipeline, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: LLMConfig):
        if self._initialized:
            return
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = config.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        self._initialized = True

    def load_model(self):
        if not self.is_loaded:
            logger.info(
                f"[LLMPipeline] Start loading {self.config.model_name} on {self.device}"
            )
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_name, use_fast=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name
                )
                self.model.to(self.device)
                self.model.eval()
                self.is_loaded = True
                logger.info(
                    f"[LLMPipeline] Model {self.config.model_name} loaded on {self.device}"
                )
            except Exception as e:
                logger.error(f"[LLMPipeline] Failed to load model: {e}", exc_info=True)
                raise
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        if not self.is_loaded:
            self.load_model()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            padding=True,
            truncation=True,
            max_length=1024,
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        with torch.inference_mode():
            try:
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=self.config.max_new_tokens,
                    attention_mask=model_inputs.attention_mask,
                    temperature=self.config.temperature,
                    top_k=self.config.top_k,
                    top_p=self.config.top_p,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            except Exception as e:
                logger.error("LLM generation failed", exc_info=True)
                return {"error": "Generation failed", "details": str(e)}

        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]

        return response

pipeline = LLMPipeline(config.llm_config)
