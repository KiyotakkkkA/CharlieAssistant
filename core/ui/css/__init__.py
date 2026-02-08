from core.ui.css.CSS import CSSTemplate, GlobalStyleSheet

from core.ui.css.styles import (
    DIALOG_SIDEBAR_CSS_BLOCK,
    CHAT_BUBBLE_CSS_BLOCK,
    CHAT_CSS_BLOCK,
    COMMAND_PALETTE_CSS_BLOCK,
    GENERAL_CSS_BLOCK,
    MODAL_DIALOG_RENAME_CSS_BLOCK,
    MODAL_DIALOG_DELETE_CSS_BLOCK
)


_STYLED_BLOCKS = [
    DIALOG_SIDEBAR_CSS_BLOCK,
    CHAT_BUBBLE_CSS_BLOCK,
    CHAT_CSS_BLOCK,
    COMMAND_PALETTE_CSS_BLOCK,
    GENERAL_CSS_BLOCK,
    MODAL_DIALOG_RENAME_CSS_BLOCK,
    MODAL_DIALOG_DELETE_CSS_BLOCK,
]


def build_application_css(template: CSSTemplate) -> str:
    return GlobalStyleSheet(styled_blocks=_STYLED_BLOCKS, template=template).create()

DARK_ORANGE_CSS_THEME = CSSTemplate(
    WACCENT="#ffa500",
    WTEXT="#f2f2f2",
    WTEXT_WEAK="#cccccc",
    WTEXT_MUTED="#909090",
    WSECONDARY="#444444",
    WPRIMARY="#262626",
    WPRIMARY_DARK="#212121",
    WPRIMARY_DARKER="#1c1c1c",
    WPRIMARY_DARKEST="#181818",
)

APPLICATION_THEME = GlobalStyleSheet(styled_blocks=_STYLED_BLOCKS, template=DARK_ORANGE_CSS_THEME)

__all__ = [
    "DARK_ORANGE_CSS_THEME",
    "APPLICATION_THEME",
    "build_application_css",
    "CSSTemplate",
]