from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from flexquiz.config import AppConfig, ensure_workspace
from flexquiz.diagnostics import diagnose_exception
from flexquiz.windows_integration import register_arnx_user_association


class SetupWizard(QWizard):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.setWindowTitle("FlexQuiz - First-Time Setup")
        self._config = config

        self.workspace_page = WorkspacePage(config.workspace_dir)
        self.theme_page = ThemePage(config.theme)
        self.association_page = AssociationPage()

        self.addPage(self.workspace_page)
        self.addPage(self.theme_page)
        self.addPage(self.association_page)

    def collect_config(self) -> AppConfig:
        return AppConfig(
            setup_complete=True,
            workspace_dir=self.workspace_page.workspace_input.text().strip(),
            theme=self.theme_page.selected_theme(),
        )

    def apply_post_finish(self) -> None:
        try:
            ensure_workspace(self.workspace_page.workspace_input.text().strip())
            if self.association_page.should_register_association():
                register_arnx_user_association(sys.executable)
        except Exception as exc:  # noqa: BLE001
            diagnostic = diagnose_exception(exc)
            QMessageBox.warning(self, diagnostic.title, f"{diagnostic.details}\n\n{diagnostic.repair_hint}")


class WorkspacePage(QWizardPage):
    def __init__(self, default_path: str):
        super().__init__()
        self.setTitle("Workspace Setup")
        self.setSubTitle("Choose a workspace directory for FlexQuiz projects.")

        self.workspace_input = QLineEdit(default_path)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._choose_workspace)

        form = QFormLayout()
        form.addRow("Workspace Directory:", self.workspace_input)
        form.addRow("", browse)
        self.setLayout(form)

    def validatePage(self) -> bool:
        value = self.workspace_input.text().strip()
        if not value:
            QMessageBox.warning(self, "Workspace Required", "Please select a workspace directory.")
            return False
        return True

    def _choose_workspace(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select Workspace Directory", self.workspace_input.text())
        if selected:
            self.workspace_input.setText(selected)


class ThemePage(QWizardPage):
    def __init__(self, default_theme: str):
        super().__init__()
        self.setTitle("Theme Preferences")
        self.setSubTitle("Select your preferred UI theme.")

        self.dark = QRadioButton("Dark Theme")
        self.light = QRadioButton("Light Theme")
        self.dark.setChecked(default_theme.lower() != "light")
        self.light.setChecked(default_theme.lower() == "light")

        layout = QVBoxLayout()
        layout.addWidget(self.dark)
        layout.addWidget(self.light)
        self.setLayout(layout)

    def selected_theme(self) -> str:
        return "light" if self.light.isChecked() else "dark"


class AssociationPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("File Association")
        self.setSubTitle("Register .arnx under current user (no admin rights required).")

        self.enable_radio = QRadioButton("Register .arnx file association for this user")
        self.disable_radio = QRadioButton("Skip for now")
        self.enable_radio.setChecked(True)

        info = QLabel("Association is written to HKEY_CURRENT_USER\\Software\\Classes.")
        info.setWordWrap(True)

        box = QVBoxLayout()
        box.addWidget(info)
        box.addWidget(self.enable_radio)
        box.addWidget(self.disable_radio)

        wrapper = QWidget()
        wrapper.setLayout(box)
        self.setLayout(box)

    def should_register_association(self) -> bool:
        return self.enable_radio.isChecked()
