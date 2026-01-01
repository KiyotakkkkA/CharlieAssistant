from core.ui.css.CSS import CSSBlock

CHAT_BUBBLE_CSS_BLOCK = CSSBlock(
    """
    .bubble {
        margin: 0 0 1 0;
    }

    .bubble_user {
        padding: 0 1;
        border: round {WACCENT};
    }

    .bubble_ai {
        padding: 0 1;
        border: round {WSECONDARY};
    }

    .bubble_title {
        color: {WTEXT_WEAK};
        padding: 0 0 0 0;
    }

    .bubble_content {
        padding: 0 0 0 0;
        color: {WTEXT};
    }
    """
)