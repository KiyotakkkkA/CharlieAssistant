import argparse

from core.general.agent.Assistant import Assistant
from core.ui.components.chat import CharlieChatApp
from core.exeptions import NoPortError

class App:
    def __init__(self, args: argparse.Namespace) -> None:
        self.tui_mode = args.tui_mode
        self.detached_mode = args.detached_mode
        self.port = args.port

        if self.detached_mode and not self.port:
            raise NoPortError()

        if self.detached_mode and self.tui_mode:
            raise ValueError("Нельзя одновременно использовать режим TUI и фоновый режим работы.")

    def run(self) -> None:
        if self.tui_mode:
            self._run_tui_mode()
        elif self.detached_mode:
            self._run_detached_mode()
    
    def _run_tui_mode(self) -> None:
        CharlieChatApp(
            assistant=Assistant(),
        ).run()
    
    def _run_detached_mode(self) -> None:
        raise NotImplementedError("Фоновый режим работы ещё не реализован.")