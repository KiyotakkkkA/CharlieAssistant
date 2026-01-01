from core.types.ai import ToolObject


class ToolBuilder:
    def __init__(self):
        self.tool: ToolObject = {
            "type": "function",
            "requires_confirmation": False,
            "humanized_description": "",
            "function": {
                "name": "",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "required": []
            }
        }
    
    def set_requires_confirmation(self, requires: bool) -> 'ToolBuilder':
        self.tool["requires_confirmation"] = requires
        return self

    def set_name(self, name: str) -> 'ToolBuilder':
        self.tool["function"]["name"] = name
        return self

    def set_description(self, description: str) -> 'ToolBuilder':
        self.tool["function"]["description"] = description
        return self
    
    def set_humanized_description(self, humanized_description: str) -> 'ToolBuilder':
        self.tool["humanized_description"] = humanized_description
        return self

    def add_property(self, name: str, prop_type: str, **kwargs) -> 'ToolBuilder':
        props = self.tool["function"]["parameters"]["properties"]

        normalized_type = self._normalize_json_schema_type(prop_type)
        props[name] = {"type": normalized_type, **kwargs}
        return self

    @staticmethod
    def _normalize_json_schema_type(prop_type: str) -> str | None:
        if not isinstance(prop_type, str):
            return "string"

        t = prop_type.strip()
        tl = t.lower()

        allowed = {"string", "number", "integer", "boolean", "object", "array", "null"}
        if tl not in allowed:
            raise ValueError(f"Недопустимый тип свойства инструмента: {prop_type} | Допустимые типы: {', '.join(allowed)}")

    def add_requirements(self, reqs: list[str]) -> 'ToolBuilder':
        self.tool["function"]["required"].extend(reqs)
        return self

    def build(self) -> ToolObject:
        return self.tool