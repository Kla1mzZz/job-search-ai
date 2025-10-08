import re
import orjson
from typing import Dict, Any
from src.llm_service.core.logger import logger


def safe_json_parse(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return orjson.loads(cleaned)
    except orjson.JSONDecodeError as e1:
        fixed = re.sub(r",\s*([\]}])", r"\1", cleaned)
        try:
            return orjson.loads(fixed)
        except orjson.JSONDecodeError:
            logger.info(cleaned)
            raise ValueError(f"Invalid JSON response")
