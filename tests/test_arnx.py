import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from flexquiz.arnx import QUIZ_DATA_FILENAME, load_arnx, save_arnx
from flexquiz.diagnostics import FlexQuizError, diagnose_exception
from flexquiz.models import default_quiz_document


def test_roundtrip_arnx(tmp_path: Path):
    doc = default_quiz_document()
    out = tmp_path / "sample.arnx"
    save_arnx(out, doc)

    package = load_arnx(out)
    assert package.document.metadata.quiz_title == doc.metadata.quiz_title
    assert len(package.document.questions) == 1


def test_missing_asset_detection(tmp_path: Path):
    doc = default_quiz_document()
    doc.questions[0].image_path = "assets/does-not-exist.png"
    out = tmp_path / "broken.arnx"

    with ZipFile(out, "w", ZIP_DEFLATED) as zf:
        zf.writestr(QUIZ_DATA_FILENAME, json.dumps(doc.to_dict()))

    with pytest.raises(FlexQuizError) as exc:
        load_arnx(out)

    diagnostic = diagnose_exception(exc.value)
    assert diagnostic.title == "Missing Asset"


def test_malformed_json_reports_context(tmp_path: Path):
    out = tmp_path / "bad.arnx"
    with ZipFile(out, "w", ZIP_DEFLATED) as zf:
        zf.writestr(QUIZ_DATA_FILENAME, "{oops")

    with pytest.raises(FlexQuizError) as exc:
        load_arnx(out)

    assert "Malformed JSON" in exc.value.details
