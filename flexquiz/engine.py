from __future__ import annotations

import random
from dataclasses import dataclass

from flexquiz.models import Question, QuizDocument


@dataclass(slots=True)
class PresentedQuestion:
    question: Question
    displayed_options: list[str]
    option_index_map: list[int]


class QuizSession:
    def __init__(self, document: QuizDocument):
        self.document = document
        self._rng = random.Random()
        self._questions = list(document.questions)
        if document.global_rules.shuffle_questions:
            self._rng.shuffle(self._questions)
        self._index = 0
        self.score = 0
        self.max_score = sum(q.points_weight for q in self._questions)

    def has_next(self) -> bool:
        return self._index < len(self._questions)

    def next_question(self) -> PresentedQuestion:
        question = self._questions[self._index]
        self._index += 1

        option_index_map = list(range(len(question.options)))
        displayed = list(question.options)
        if self.document.global_rules.shuffle_options:
            pairs = list(enumerate(displayed))
            self._rng.shuffle(pairs)
            option_index_map = [idx for idx, _ in pairs]
            displayed = [text for _, text in pairs]

        return PresentedQuestion(question=question, displayed_options=displayed, option_index_map=option_index_map)

    def submit(self, presented: PresentedQuestion, selected_display_index: int | None) -> bool:
        if selected_display_index is None or selected_display_index < 0:
            return False
        original_index = presented.option_index_map[selected_display_index]
        correct = original_index == presented.question.correct_index
        if correct:
            self.score += presented.question.points_weight
        return correct

    def pass_status(self) -> bool:
        if self.max_score <= 0:
            return True
        percentage = (self.score / self.max_score) * 100
        return percentage >= self.document.global_rules.pass_percentage
