from core.ui.css.CSS import CSSBlock

COMMAND_PALETTE_CSS_BLOCK = CSSBlock(
    """
    #command_palette {
        height: auto;
        margin: 0 0 1 0;
        border: solid {WSECONDARY};
        background: {WPRIMARY_DARKER};
    }

    #command_palette.hidden {
        display: none;
    }

    #command_palette_list {
        height: auto;
        background: transparent;
        border: none;
    }

    #command_palette_list:focus {
        border: none;
    }

    #command_palette_list > ListItem {
        background: transparent;
        color: {WTEXT};
        padding: 0 1;
        margin: 0;
    }

    #command_palette_list > ListItem:hover {
        background: {WPRIMARY};
    }

    #command_palette_list > ListItem.-highlight,
    #command_palette_list > ListItem.--highlight,
    #command_palette_list > ListItem.-selected,
    #command_palette_list > ListItem.--selected {
        background: {WACCENT};
        color: #1c1c1c;
    }
    """
)
