from langchain_groq import ChatGroq
from backend.utils.config import settings
from backend.utils.logging import setup_logger

logger = setup_logger("llm_service")

def get_llm(temperature: float = None):
    temp = temperature if temperature is not None else settings.TEMPERATURE
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.LLM_MODEL,
        temperature=temp,
        max_tokens=2048
    )
