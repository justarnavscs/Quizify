from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


DEVELOPER = "Arnav Agarwal"
TITLE = "Software Architect"
BIO = "Designing lightweight, high-performance software solutions and exceptional user experiences."
CONTACT = "justarnav.scs@gmail.com"


@dataclass(slots=True)
class QuizMetadata:
    quiz_title: str
    quiz_subtitle: str
    quiz_description: str
    version: str
    created_by: str
    creation_date: str


@dataclass(slots=True)
class CoverConfig:
    cover_title: str
    cover_subtitle: str
    institution_name: str
    author_name: str
    cover_bg_color: str
    cover_bg_image_path: str
    cover_logo_path: str


@dataclass(slots=True)
class Question:
    question_id: str
    question_text: str
    options: list[str]
    correct_index: int
    timer_seconds: int
    points_weight: int
    image_path: str | None
    explanation: str
    hint: str

    def validate(self) -> None:
        if not self.options or len(self.options) < 2:
            raise ValueError(f"Question '{self.question_id}' must contain at least two options.")
        if self.correct_index < 0 or self.correct_index >= len(self.options):
            raise ValueError(f"Question '{self.question_id}' has invalid correct_index.")
        if self.timer_seconds <= 0:
            raise ValueError(f"Question '{self.question_id}' timer_seconds must be > 0.")
        if self.points_weight <= 0:
            raise ValueError(f"Question '{self.question_id}' points_weight must be > 0.")


@dataclass(slots=True)
class SafetySettings:
    enable_misfire_protection: bool
    misfire_warning_text: str


@dataclass(slots=True)
class GlobalEngineRules:
    shuffle_questions: bool
    shuffle_options: bool
    pass_percentage: int
    allow_review_mode: bool
    show_immediate_feedback: bool

    def validate(self) -> None:
        if self.pass_percentage < 0 or self.pass_percentage > 100:
            raise ValueError("pass_percentage must be between 0 and 100.")


@dataclass(slots=True)
class QuizDocument:
    metadata: QuizMetadata
    cover_page: CoverConfig
    questions: list[Question] = field(default_factory=list)
    safety: SafetySettings = field(default_factory=lambda: SafetySettings(True, "Are you sure you want to reveal answers?"))
    global_rules: GlobalEngineRules = field(
        default_factory=lambda: GlobalEngineRules(False, False, 40, True, False)
    )

    def validate(self) -> None:
        if not self.metadata.quiz_title.strip():
            raise ValueError("quiz_title cannot be empty.")
        if not self.questions:
            raise ValueError("Quiz must contain at least one question.")
        self.global_rules.validate()
        for q in self.questions:
            q.validate()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QuizDocument":
        metadata = QuizMetadata(**payload["metadata"])
        cover_page = CoverConfig(**payload["cover_page"])
        questions = [Question(**q) for q in payload.get("questions", [])]
        safety = SafetySettings(**payload["safety"])
        global_rules = GlobalEngineRules(**payload["global_rules"])
        doc = cls(
            metadata=metadata,
            cover_page=cover_page,
            questions=questions,
            safety=safety,
            global_rules=global_rules,
        )
        doc.validate()
        return doc


def default_quiz_document() -> QuizDocument:
    today = datetime.now().strftime("%Y-%m-%d")
    doc = QuizDocument(
        metadata=QuizMetadata(
            quiz_title="Sample Quiz",
            quiz_subtitle="Welcome to FlexQuiz",
            quiz_description="A lightweight and responsive quiz session.",
            version="1.0.0",
            created_by=DEVELOPER,
            creation_date=today,
        ),
        cover_page=CoverConfig(
            cover_title="FlexQuiz",
            cover_subtitle="Interactive Assessment",
            institution_name="Your Institution",
            author_name=DEVELOPER,
            cover_bg_color="#111827",
            cover_bg_image_path="",
            cover_logo_path="",
        ),
        questions=[
            Question(
                question_id="Q1",
                question_text="What does async UI design primarily prevent?",
                options=["UI freezes", "Compilation", "Disk usage", "CPU instructions"],
                correct_index=0,
                timer_seconds=30,
                points_weight=10,
                image_path=None,
                explanation="Non-blocking operations keep the event loop responsive.",
                hint="Think about responsiveness.",
            )
        ],
        safety=SafetySettings(
            enable_misfire_protection=True,
            misfire_warning_text="Confirm before revealing answers to avoid accidental clicks.",
        ),
        global_rules=GlobalEngineRules(
            shuffle_questions=False,
            shuffle_options=False,
            pass_percentage=40,
            allow_review_mode=True,
            show_immediate_feedback=False,
        ),
    )
    doc.validate()
    return doc
