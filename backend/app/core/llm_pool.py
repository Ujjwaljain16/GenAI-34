import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiPool:
    def __init__(self):
        # Parse comma separated keys from GEMINI_API_KEYS
        raw_keys = getattr(settings, "GEMINI_API_KEYS", "")
        keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        
        # Fallback to single key GEMINI_API_KEY if exists
        single_key = getattr(settings, "GEMINI_API_KEY", None)
        if not keys and single_key:
            keys = [single_key]
            
        if not keys:
            raise ValueError("No Gemini API keys configured. Set GEMINI_API_KEY or GEMINI_API_KEYS.")
            
        self.keys = keys
        self.clients = [genai.Client(api_key=k) for k in self.keys]
        self._current_index = 0
        
        if len(self.keys) > 1:
            logger.info(f"Initialized Gemini Pool with {len(self.keys)} API keys.")
        else:
            logger.info("Initialized Gemini with a single API key.")

    def get_client(self) -> genai.Client:
        return self.clients[self._current_index]
        
    def rotate(self) -> genai.Client:
        if len(self.clients) > 1:
            self._current_index = (self._current_index + 1) % len(self.clients)
            logger.warning(f"Rate limit hit! Rotating to API Key #{self._current_index + 1}")
        return self.get_client()

# Global singleton to share state across requests/workers
gemini_pool = GeminiPool()
