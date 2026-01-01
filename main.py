import argparse

from core import App

def args_parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Charlie CLI")
    parser.add_argument(
        "-tm",
        '--tui-mode',
        action='store_true',
        help="Режим текстового интерфейса (TUI).",
    )
    parser.add_argument(
        "-dm",
        '--detached-mode',
        action='store_true',
        help="Режим фоновой работы через механизм WebSockets (требует указание порта прослушивания [--port]).",
    )
    parser.add_argument(
        '--port',
        type=int,
        default=0,
        help="Порт для режима фоновой работы через механизм WebSockets.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    App(args_parse()).run()