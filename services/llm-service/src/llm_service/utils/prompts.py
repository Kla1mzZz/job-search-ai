from pathlib import Path
from src.llm_service.core.logger import logger
import aiofiles


PROMPT_DIR = Path(__file__).parent.parent.parent.parent / "resources" / "prompts"


async def load_prompt(filename: str) -> str:
    path = PROMPT_DIR / filename
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return await f.read()
    except FileNotFoundError:
        logger.info(f"Prompt not found: {filename}")
        raise
