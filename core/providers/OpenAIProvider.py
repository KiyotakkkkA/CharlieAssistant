from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import Generator
from core.general import Config
from core.exeptions import NoClientError, NoModelError
from core.types.ai import AIChunk
from .BaseAIProvider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self, config: Config):
        super().__init__(
            api_key=config.OPENAI_API_KEY,
            api_base=config.OPENAI_API_BASE
        )

    def provider_setup(self):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )
    
    def chat_completion(self, messages, **kwargs) -> Generator[AIChunk, None, None]:
        if not self.client:
            raise NoClientError("OpenAIProvider")
        
        for chunk in self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            **kwargs,
        ):
            chunk: ChatCompletionChunk
            yield AIChunk(content=chunk.choices[0].delta.content or '')
        

        
