class CSSTemplate:
    def __init__(self,
                 WACCENT: str,
                 WTEXT: str,
                 WTEXT_WEAK: str,
                 WTEXT_MUTED: str,
                 WSECONDARY: str,
                 WPRIMARY: str,
                 WPRIMARY_DARK: str,
                 WPRIMARY_DARKER: str,
                 WPRIMARY_DARKEST: str
                ):
        self.WACCENT_COLOR = WACCENT
        self.WTEXT_COLOR = WTEXT
        self.WTEXT_WEAK_COLOR = WTEXT_WEAK
        self.WTEXT_MUTED_COLOR = WTEXT_MUTED
        self.WSECONDARY_COLOR = WSECONDARY
        self.WPRIMARY_COLOR = WPRIMARY
        self.WPRIMARY_DARK_COLOR = WPRIMARY_DARK
        self.WPRIMARY_DARKER_COLOR = WPRIMARY_DARKER
        self.WPRIMARY_DARKEST_COLOR = WPRIMARY_DARKEST


class CSSBlock:
    def __init__(self, content: str) -> None:
        self.content = content
    
    def create(self, template: CSSTemplate) -> str:
        return (
            self.content
            .replace("{WACCENT}", template.WACCENT_COLOR)
            .replace("{WTEXT}", template.WTEXT_COLOR)
            .replace("{WTEXT_WEAK}", template.WTEXT_WEAK_COLOR)
            .replace("{WTEXT_MUTED}", template.WTEXT_MUTED_COLOR)
            .replace("{WSECONDARY}", template.WSECONDARY_COLOR)
            .replace("{WPRIMARY}", template.WPRIMARY_COLOR)
            .replace("{WPRIMARY_DARK}", template.WPRIMARY_DARK_COLOR)
            .replace("{WPRIMARY_DARKER}", template.WPRIMARY_DARKER_COLOR)
            .replace("{WPRIMARY_DARKEST}", template.WPRIMARY_DARKEST_COLOR)
        )


class GlobalStyleSheet:
    def __init__(self, styled_blocks: list[CSSBlock], template: CSSTemplate) -> None:
        self.styled_blocks = styled_blocks
        self.template = template
    
    def create(self) -> str:
        return "\n".join([block.create(self.template) for block in self.styled_blocks])
