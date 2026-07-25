from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from flexquiz.arnx import load_arnx, save_arnx
from flexquiz.diagnostics import diagnose_exception
from flexquiz.engine import QuizSession
from flexquiz.models import BIO, CONTACT, DEVELOPER, TITLE, QuizDocument, default_quiz_document


class MainWindow(QMainWindow):
    def __init__(self, workspace: Path, theme: str):
        super().__init__()
        self.workspace = workspace
        self.theme = theme
        self.setWindowTitle("FlexQuiz")
        self.resize(1260, 780)

        self.document = default_quiz_document()
        self.session: QuizSession | None = None
        self.presented = None
        self.remaining_seconds = 0

        root = QWidget()
        root_layout = QHBoxLayout(root)

        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        for label in ["Cover", "Editor", "Quiz Engine", "About"]:
            self.nav.addItem(QListWidgetItem(label))
        self.nav.currentRowChanged.connect(self._switch_page)
        self.nav.setCurrentRow(0)

        self.stack = QStackedWidget()
        self.cover_page = self._build_cover_page()
        self.editor_page = self._build_editor_page()
        self.engine_page = self._build_engine_page()
        self.about_page = self._build_about_page()

        self.stack.addWidget(self.cover_page)
        self.stack.addWidget(self.editor_page)
        self.stack.addWidget(self.engine_page)
        self.stack.addWidget(self.about_page)

        root_layout.addWidget(self.nav)
        root_layout.addWidget(self.stack)
        self.setCentralWidget(root)

        self._apply_theme()
        self._refresh_cover()

    def _apply_theme(self) -> None:
        royal_blue = "#4169E1"
        base_style = "QMainWindow{background:#111827;color:#E5E7EB;} QLabel{color:#E5E7EB;} QPlainTextEdit{background:#0B1220;color:#E5E7EB;}"
        if self.theme == "light":
            base_style = "QMainWindow{background:#f5f7fb;color:#111827;} QLabel{color:#111827;}"
        self.setStyleSheet(base_style)
        self.nav.item(3).setBackground(self.palette().highlight())
        self.nav.item(3).setForeground(self.palette().window())
        self.nav.setStyleSheet(f"QListWidget::item:selected{{background:{royal_blue}; color:white;}}")

    def _switch_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def _build_cover_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.cover_title = QLabel()
        self.cover_subtitle = QLabel()
        self.cover_meta = QLabel()
        self.cover_title.setStyleSheet("font-size:28px; font-weight:600;")
        layout.addWidget(self.cover_title)
        layout.addWidget(self.cover_subtitle)
        layout.addWidget(self.cover_meta)

        controls = QHBoxLayout()
        start_btn = QPushButton("Start Quiz")
        start_btn.clicked.connect(self._start_quiz)
        save_btn = QPushButton("Save .arnx")
        save_btn.clicked.connect(self._save_document)
        load_btn = QPushButton("Load .arnx")
        load_btn.clicked.connect(self._load_document)
        controls.addWidget(start_btn)
        controls.addWidget(save_btn)
        controls.addWidget(load_btn)
        layout.addLayout(controls)
        return page

    def _build_editor_page(self) -> QWidget:
        page = QWidget()
        layout = QGridLayout(page)

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(json.dumps(self.document.to_dict(), indent=2))
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)

        layout.addWidget(QLabel("Editor"), 0, 0)
        layout.addWidget(QLabel("Live Preview"), 0, 1)
        layout.addWidget(self.editor, 1, 0)
        layout.addWidget(self.preview, 1, 1)

        apply_btn = QPushButton("Apply JSON to Quiz")
        apply_btn.clicked.connect(self._apply_editor_document)
        layout.addWidget(apply_btn, 2, 0)

        self.preview_timer = QTimer(self)
        self.preview_timer.setInterval(250)
        self.preview_timer.timeout.connect(self._update_preview)
        self.preview_timer.start()
        return page

    def _build_engine_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        self.engine_question = QLabel("Press Start Quiz from Cover page")
        self.engine_timer = QLabel("Timer: --")
        self.engine_progress = QProgressBar()
        self.engine_options_box = QVBoxLayout()
        self.option_buttons: list[QRadioButton] = []

        submit = QPushButton("Submit Answer")
        submit.clicked.connect(self._submit_answer)
        reveal = QPushButton("Reveal Correct Answer")
        reveal.clicked.connect(self._reveal_answer_with_guard)

        layout.addWidget(self.engine_question)
        layout.addWidget(self.engine_timer)
        layout.addWidget(self.engine_progress)

        options_frame = QFrame()
        options_frame.setLayout(self.engine_options_box)
        layout.addWidget(options_frame)
        layout.addWidget(submit)
        layout.addWidget(reveal)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick_timer)
        return page

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        page.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0A0F1F, stop:1 #1E1B4B);"
            "border:1px solid #D4AF37;border-radius:12px;padding:20px;"
        )

        title = QLabel("About FlexQuiz")
        title.setStyleSheet("font-size:26px;color:#D4AF37;font-weight:700;")
        credits = QLabel(
            f"Developer: {DEVELOPER}\n"
            f"Title: {TITLE}\n"
            f"Bio: {BIO}\n"
            f"Contact: {CONTACT}"
        )
        credits.setWordWrap(True)
        credits.setStyleSheet("font-size:16px;")
        layout.addWidget(title)
        layout.addWidget(credits)
        return page

    def _refresh_cover(self) -> None:
        md = self.document.metadata
        cover = self.document.cover_page
        self.cover_title.setText(cover.cover_title or md.quiz_title)
        self.cover_subtitle.setText(cover.cover_subtitle or md.quiz_subtitle)
        self.cover_meta.setText(f"{cover.institution_name} • {cover.author_name} • v{md.version}")

    def _save_document(self) -> None:
        try:
            self.document.validate()
            save_arnx(self.workspace / "latest.arnx", self.document)
            QMessageBox.information(self, "Saved", "Saved to workspace/latest.arnx")
        except Exception as exc:  # noqa: BLE001
            d = diagnose_exception(exc)
            QMessageBox.critical(self, d.title, f"{d.details}\n\n{d.repair_hint}")

    def _load_document(self) -> None:
        try:
            package = load_arnx(self.workspace / "latest.arnx")
            self.document = package.document
            self.editor.setPlainText(json.dumps(self.document.to_dict(), indent=2))
            self._refresh_cover()
            QMessageBox.information(self, "Loaded", "Loaded workspace/latest.arnx")
        except Exception as exc:  # noqa: BLE001
            d = diagnose_exception(exc)
            QMessageBox.critical(self, d.title, f"{d.details}\n\n{d.repair_hint}")

    def _apply_editor_document(self) -> None:
        try:
            payload = json.loads(self.editor.toPlainText())
            self.document = QuizDocument.from_dict(payload)
            self._refresh_cover()
        except Exception as exc:  # noqa: BLE001
            d = diagnose_exception(exc)
            QMessageBox.warning(self, d.title, f"{d.details}\n\n{d.repair_hint}")

    def _update_preview(self) -> None:
        text = self.editor.toPlainText()
        try:
            payload = json.loads(text)
            doc = QuizDocument.from_dict(payload)
            self.preview.setPlainText(
                f"Title: {doc.metadata.quiz_title}\nQuestions: {len(doc.questions)}\n"
                f"Pass %: {doc.global_rules.pass_percentage}\n"
                f"Misfire Protection: {doc.safety.enable_misfire_protection}"
            )
        except Exception as exc:  # noqa: BLE001
            self.preview.setPlainText(f"Preview diagnostics:\n{exc}")

    def _start_quiz(self) -> None:
        self.session = QuizSession(self.document)
        self.nav.setCurrentRow(2)
        self._advance_question()

    def _advance_question(self) -> None:
        assert self.session is not None
        if not self.session.has_next():
            result = "PASS" if self.session.pass_status() else "FAIL"
            QMessageBox.information(self, "Quiz Complete", f"Score: {self.session.score}/{self.session.max_score}\nResult: {result}")
            self.timer.stop()
            return

        self.presented = self.session.next_question()
        q = self.presented.question
        self.engine_question.setText(q.question_text)
        self.remaining_seconds = q.timer_seconds
        self.engine_progress.setMaximum(q.timer_seconds)
        self.engine_progress.setValue(q.timer_seconds)
        self.engine_timer.setText(f"Timer: {self.remaining_seconds}s")

        self._clear_options()
        for option in self.presented.displayed_options:
            button = QRadioButton(option)
            button.setEnabled(True)
            self.option_buttons.append(button)
            self.engine_options_box.addWidget(button)

        self.timer.start()

    def _clear_options(self) -> None:
        while self.engine_options_box.count():
            item = self.engine_options_box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.option_buttons = []

    def _tick_timer(self) -> None:
        self.remaining_seconds -= 1
        self.engine_progress.setValue(max(0, self.remaining_seconds))
        self.engine_timer.setText(f"Timer: {max(0, self.remaining_seconds)}s")
        if self.remaining_seconds <= 0:
            self.timer.stop()
            for btn in self.option_buttons:
                btn.setEnabled(False)

    def _submit_answer(self) -> None:
        if self.session is None or self.presented is None:
            return
        self.timer.stop()
        selected = next((idx for idx, btn in enumerate(self.option_buttons) if btn.isChecked()), None)
        self.session.submit(self.presented, selected)
        self._advance_question()

    def _reveal_answer_with_guard(self) -> None:
        if self.presented is None:
            return
        if self.document.safety.enable_misfire_protection:
            confirm = QMessageBox.question(
                self,
                "Misfire Protection",
                self.document.safety.misfire_warning_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
        correct = self.presented.question.correct_index
        reverse_lookup = {original: display for display, original in enumerate(self.presented.option_index_map)}
        idx = reverse_lookup.get(correct)
        if idx is not None and idx < len(self.option_buttons):
            self.option_buttons[idx].setChecked(True)
