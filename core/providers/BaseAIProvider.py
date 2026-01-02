from typing import Generator

from openai.types.responses import ResponseInputParam

from core.types.ai import AIResponseChunk


class BaseAIProvider:

    REQUIRES_API_KEY: bool = True
    REQUIRES_API_BASE: bool = True

    def __init__(self, api_key: str, api_base: str) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.client = None
        self.model_name = ''
    
        self._provider_setup()

    def _provider_setup(self):
        if self.REQUIRES_API_BASE and not self.api_base:
            raise ValueError("API base не был установлен")
        if self.REQUIRES_API_KEY and not self.api_key:
            raise ValueError("API key не был установлен")
        
        return self.provider_setup()
    
    def generate_response(self, messages: ResponseInputParam , **kwargs) -> Generator[AIResponseChunk, None, None]:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def provider_setup(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def set_model(self, model_name: str):
        self.model_name = model_name
        return self