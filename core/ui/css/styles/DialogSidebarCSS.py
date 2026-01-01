from ..CSS import CSSBlock

DIALOG_SIDEBAR_CSS_BLOCK = CSSBlock(
    """
        #sidebar {
        width: 28;
        min-width: 24;
        max-width: 32;
        background: {WPRIMARY_DARKER};
        border-right: solid {WSECONDARY};
        padding: 0 0 1 1;
    }

    #sidebar.collapsed {
        width: 0;
        min-width: 0;
        max-width: 0;
        padding: 0;
        border: none;
        display: none;
    }

    #sidebar_title {
        margin-right: 1;
        color: {WTEXT};
        text-style: bold;
        text-align: center;
        border: solid {WSECONDARY}
    }

    #dialog_list {
        height: 1fr;
        border: solid {WSECONDARY};
        background: transparent;
        margin-right: 1;
    }

    ListView#dialog_list:focus {
        border: solid {WACCENT};
    }

    ListView#dialog_list > ListItem {
        background: transparent;
        color: {WTEXT};
        padding: 1 1;
        margin: 0;
    }

    ListView#dialog_list > ListItem:hover {
        background: {WPRIMARY};
    }

    ListView#dialog_list:focus > ListItem.-highlight,
    ListView#dialog_list:focus > ListItem.--highlight,
    ListView#dialog_list:focus > ListItem.-selected,
    ListView#dialog_list:focus > ListItem.--selected {
        background: {WACCENT};
        color: #1c1c1c;
    }
    """
)