from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from flexquiz.config import load_config, save_config
from flexquiz.ui.main_window import MainWindow
from flexquiz.ui.setup_wizard import SetupWizard
from flexquiz.windows_integration import generate_placeholder_icon


def main() -> int:
    app = QApplication(sys.argv)

    generate_placeholder_icon(Path("assets") / "icon.ico")

    cfg = load_config()
    if not cfg.setup_complete:
        wizard = SetupWizard(cfg)
        if wizard.exec() == wizard.DialogCode.Accepted:
            cfg = wizard.collect_config()
            save_config(cfg)
            wizard.apply_post_finish()
        else:
            return 0

    window = MainWindow(Path(cfg.workspace_dir), cfg.theme)
    window.show()
    return app.exec()
