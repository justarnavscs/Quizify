from pathlib import Path

from flexquiz.windows_integration import generate_placeholder_icon


def test_generate_placeholder_icon(tmp_path: Path):
    icon = generate_placeholder_icon(tmp_path / "assets" / "icon.ico")
    data = icon.read_bytes()
    assert icon.exists()
    assert len(data) > 32
    assert data[:4] == b"\x00\x00\x01\x00"
