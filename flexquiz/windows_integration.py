from __future__ import annotations

import os
import struct
import zlib
from pathlib import Path


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def _png_rgba(size: int = 32, color: tuple[int, int, int, int] = (65, 105, 225, 255)) -> bytes:
    raw = b"".join(b"\x00" + bytes(color) * size for _ in range(size))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def generate_placeholder_icon(icon_path: str | Path) -> Path:
    path = Path(icon_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    png = _png_rgba()
    header = struct.pack("<HHH", 0, 1, 1)
    directory = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(png), 22)
    path.write_bytes(header + directory + png)
    return path


def register_arnx_user_association(executable_path: str, extension: str = ".arnx", prog_id: str = "FlexQuiz.arnx") -> bool:
    if os.name != "nt":
        return False

    import winreg  # pylint: disable=import-error

    command = f'"{executable_path}" "%1"'
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}") as ext_key:
        winreg.SetValueEx(ext_key, "", 0, winreg.REG_SZ, prog_id)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}") as prog_key:
        winreg.SetValueEx(prog_key, "", 0, winreg.REG_SZ, "FlexQuiz Package")

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\shell\\open\\command") as cmd_key:
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

    return True
