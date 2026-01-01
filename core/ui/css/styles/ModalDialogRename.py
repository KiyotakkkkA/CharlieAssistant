from core.ui.css.CSS import CSSBlock

MODAL_DIALOG_RENAME_CSS_BLOCK = CSSBlock(
    """
    RenameDialogModal > Container {
        width: 60;
        height: auto;
        padding: 1 2;
    }

    RenameDialogModal #modal_title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    RenameDialogModal #rename_input {
        width: 100%;
        margin-bottom: 1;
    }

    RenameDialogModal #modal_actions {
        width: 100%;
        height: auto;
        align: center middle;
    }

    RenameDialogModal Button {
        min-width: 16;
        margin: 0 1;
    }
    """
)