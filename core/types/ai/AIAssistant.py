from typing import Any, Callable, Dict, Literal, Tuple, Type

from core.providers import BaseAIProvider

AllowedAIToolTypes = Literal['normal', 'flat']
AllowedAIProviders = Literal['openrouter', 'ollama']

AIProviderRecord = Tuple[
    str,
    Type[BaseAIProvider],
    Callable[..., Any],
    AllowedAIToolTypes
]

AIProviders = Dict[AllowedAIProviders, AIProviderRecord]
    