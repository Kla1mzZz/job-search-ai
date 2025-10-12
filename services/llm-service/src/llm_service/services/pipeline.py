import ollama
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
        self.model_name = config.model_name
        self.is_loaded = False
        self._initialized = True

    def load_model(self):
        try:
            logger.info(f"[LLMPipeline] Checking Ollama model: {self.model_name}")
            available_models = [m["model"] for m in ollama.list()["models"]]
            if self.model_name not in available_models:
                logger.info(f"[LLMPipeline] Pulling {self.model_name}...")
                ollama.pull(self.model_name)
            self.is_loaded = True
            logger.info(f"[LLMPipeline] Model {self.model_name} is ready.")
        except Exception as e:
            logger.error(f"[LLMPipeline] Failed to load model: {e}", exc_info=True)
            raise

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.is_loaded:
            self.load_model()

        try:
            logger.info(f"[LLMPipeline] Generating with {self.model_name}")

            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "num_predict": self.config.max_new_tokens,
                },
            )

            content = response["message"]["content"]
            logger.info(f"[LLMPipeline] Generation completed successfully.")
            return content

        except Exception as e:
            logger.error("LLM generation failed", exc_info=True)
            return {"error": "Generation failed", "details": str(e)}


pipeline = LLMPipeline(config.llm_config)
