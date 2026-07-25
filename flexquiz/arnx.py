from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from flexquiz.diagnostics import malformed_archive_error, missing_asset_error
from flexquiz.models import QuizDocument

QUIZ_DATA_FILENAME = "quiz_data.json"
ASSETS_PREFIX = "assets/"


@dataclass(slots=True)
class QuizPackage:
    document: QuizDocument
    archive_path: Path


def _validate_asset_references(doc: QuizDocument, names: set[str]) -> None:
    referenced_paths: set[str] = set()
    for question in doc.questions:
        if question.image_path:
            referenced_paths.add(question.image_path)
    for candidate in (doc.cover_page.cover_bg_image_path, doc.cover_page.cover_logo_path):
        if candidate:
            referenced_paths.add(candidate)

    for relative in referenced_paths:
        normalized = relative.replace("\\", "/").lstrip("/")
        if normalized and normalized not in names:
            raise missing_asset_error(normalized)


def load_arnx(path: str | Path) -> QuizPackage:
    archive = Path(path)
    try:
        with ZipFile(archive, "r") as zf:
            names = set(zf.namelist())
            if QUIZ_DATA_FILENAME not in names:
                raise malformed_archive_error(archive, "quiz_data.json not found")
            payload = json.loads(zf.read(QUIZ_DATA_FILENAME).decode("utf-8"))
            doc = QuizDocument.from_dict(payload)
            _validate_asset_references(doc, names)
    except BadZipFile as exc:
        raise malformed_archive_error(archive, "Invalid ZIP structure") from exc
    except json.JSONDecodeError as exc:
        raise malformed_archive_error(archive, f"Malformed JSON: {exc.msg}") from exc
    return QuizPackage(document=doc, archive_path=archive)


def save_arnx(path: str | Path, document: QuizDocument, asset_sources: dict[str, str] | None = None) -> Path:
    document.validate()
    archive = Path(path)
    archive.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr(QUIZ_DATA_FILENAME, json.dumps(document.to_dict(), indent=2, ensure_ascii=False))
        for archive_name, source_path in (asset_sources or {}).items():
            normalized = archive_name.replace("\\", "/")
            if not normalized.startswith(ASSETS_PREFIX):
                normalized = f"{ASSETS_PREFIX}{normalized.lstrip('/')}"
            zf.write(source_path, normalized)
    return archive


async def load_arnx_async(path: str | Path) -> QuizPackage:
    return await asyncio.to_thread(load_arnx, path)


async def save_arnx_async(path: str | Path, document: QuizDocument, asset_sources: dict[str, str] | None = None) -> Path:
    return await asyncio.to_thread(save_arnx, path, document, asset_sources)
