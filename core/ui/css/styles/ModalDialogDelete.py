from core.ui.css.CSS import CSSBlock

MODAL_DIALOG_DELETE_CSS_BLOCK = CSSBlock(
    """
    ConfirmDeleteDialogModal > Container {
        width: 60;
        height: auto;
        padding: 1 2;
    }

    ConfirmDeleteDialogModal #modal_title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    ConfirmDeleteDialogModal #modal_message {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        margin-bottom: 1;
    }

    ConfirmDeleteDialogModal #modal_actions {
        width: 100%;
        height: auto;
        align: center middle;
    }

    ConfirmDeleteDialogModal Button {
        min-width: 16;
        margin: 0 1;
    }
    """
)