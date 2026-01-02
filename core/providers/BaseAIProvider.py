from typing import Iterable, Generator

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolUnionParam

from core.types.ai import AIChunk


class BaseAIProvider:

    def __init__(self, api_key: str, api_base: str) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.client = None
        self.model_name = ''
    
        self._provider_setup()

    def _provider_setup(self):
        if not self.api_key or not self.api_base:
            raise ValueError("API key или API base не были установлены")
        
        return self.provider_setup()
    
    def chat_completion(self, messages: Iterable[ChatCompletionMessageParam], tools: Iterable[ChatCompletionToolUnionParam], **kwargs) -> Generator[AIChunk, None, None]:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def provider_setup(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def set_model(self, model_name: str):
        self.model_name = model_name
        return self