from core.ui.css.CSS import CSSBlock

GENERAL_CSS_BLOCK = CSSBlock(
    """
    #root {
        height: 100%;
        width: 100%;
        layout: horizontal;
    }

    #composer {
        height: auto;
        padding: 1 2;
        background: {WPRIMARY_DARK};
        border-top: solid #3a3a3a;
    }

    Screen {
        background: {WPRIMARY_DARKER};
    }

    Header {
        background: {WPRIMARY};
        color: {WTEXT};
    }

    Footer {
        background: {WPRIMARY};
        color: {WTEXT_WEAK};
    }

    ModalScreen {
        align: center middle;
        background: $background 60%;
    }

    Input {
        background: transparent;
        color: {WTEXT};
        border: solid {WSECONDARY};
    }

    Input:focus {
        border: solid {WACCENT};
    }

    .muted {
        color: {WTEXT_MUTED};
    }
    """
)