from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Diagnostic:
    title: str
    details: str
    repair_hint: str
    can_reset: bool


class FlexQuizError(Exception):
    def __init__(self, title: str, details: str, repair_hint: str, can_reset: bool = True):
        super().__init__(details)
        self.title = title
        self.details = details
        self.repair_hint = repair_hint
        self.can_reset = can_reset


def diagnose_exception(exc: Exception, source_path: str | None = None) -> Diagnostic:
    if isinstance(exc, FlexQuizError):
        return Diagnostic(exc.title, exc.details, exc.repair_hint, exc.can_reset)

    if isinstance(exc, FileNotFoundError):
        path = source_path or str(getattr(exc, "filename", "unknown file"))
        return Diagnostic(
            title="Missing File",
            details=f"Required file not found: {path}",
            repair_hint="Restore or re-link the missing file and retry.",
            can_reset=True,
        )

    if isinstance(exc, PermissionError):
        path = source_path or str(getattr(exc, "filename", "target path"))
        return Diagnostic(
            title="Permission Denied",
            details=f"Unable to access: {path}",
            repair_hint="Choose another location or run with sufficient account permissions.",
            can_reset=False,
        )

    return Diagnostic(
        title="Unexpected Error",
        details=str(exc),
        repair_hint="Use Reset/Repair to restore defaults, then try again.",
        can_reset=True,
    )


def missing_asset_error(asset_path: str) -> FlexQuizError:
    return FlexQuizError(
        title="Missing Asset",
        details=f"Asset referenced by quiz_data.json was not found: {asset_path}",
        repair_hint="Re-export the .arnx package with the missing asset included in assets/.",
        can_reset=False,
    )


def malformed_archive_error(path: Path, message: str) -> FlexQuizError:
    return FlexQuizError(
        title="Malformed .arnx Archive",
        details=f"{path.name}: {message}",
        repair_hint="Open the quiz in editor mode and use Reset/Repair to rebuild quiz_data.json.",
        can_reset=True,
    )
