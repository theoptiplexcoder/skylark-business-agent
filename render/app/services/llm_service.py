from typing import Optional
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

try:
    from langchain_huggingface import HuggingFaceEndpoint
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not installed — LLM features disabled")

FALLBACK_MODELS = [
    "microsoft/Phi-3-mini-4k-instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.3",
]


class LLMService:
    """Hugging Face Inference API wrapper via LangChain."""

    def __init__(self):
        self._llm = None
        self._model_name = None
        self._initialized = False
        if LANGCHAIN_AVAILABLE and settings.HF_API_KEY:
            import threading
            threading.Thread(target=self._try_init, daemon=True).start()

    def _try_init(self):
        models_to_try = [settings.HF_MODEL] + [m for m in FALLBACK_MODELS if m != settings.HF_MODEL]
        for model in models_to_try:
            try:
                llm = HuggingFaceEndpoint(
                    repo_id=model,
                    huggingfacehub_api_token=settings.HF_API_KEY,
                    task="text-generation",
                    max_new_tokens=512,
                    temperature=0.3,
                    timeout=10,
                )
                self._llm = llm
                self._model_name = model
                self._initialized = True
                logger.info("LLM initialized: %s", model)
                return
            except Exception as e:
                logger.warning("Failed to init model %s: %s", model, e)
                continue
        logger.error("All LLM models failed to initialize")

    @property
    def available(self) -> bool:
        return self._llm is not None

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.available:
            return ""

        import asyncio
        import concurrent.futures

        try:
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    concurrent.futures.ThreadPoolExecutor(max_workers=1),
                    self._llm.invoke,
                    full_prompt,
                ),
                timeout=5,
            )
            return result if isinstance(result, str) else str(result)
        except (asyncio.TimeoutError, Exception) as e:
            logger.error("LLM generation failed: %s", e)
            return ""

    async def generate_insight(self, data_summary: str, question: str) -> str:
        system = (
            "You are Skylark BI, an expert business intelligence analyst. "
            "Analyze the provided data and give concise, executive-level insights. "
            "Use specific numbers from the data. Be actionable. "
            "If data shows Rs. 0 for revenue, acknowledge that the data may be masked or unavailable."
        )
        prompt = f"Data Summary:\n{data_summary}\n\nQuestion: {question}\n\nProvide a clear, data-driven answer based ONLY on the numbers provided:"
        return await self.generate(prompt, system)


llm_service = LLMService()
