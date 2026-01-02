from typing import TypedDict

from openai.types.chat import ChatCompletionChunk

class AIChunk(TypedDict):
    content: ChatCompletionChunk