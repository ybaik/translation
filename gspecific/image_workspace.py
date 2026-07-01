"""Shared paths and artifact naming for game-specific image tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ImageWorkspace:
    root: Path
    platform: str = "pc98"

    @property
    def source_root(self) -> Path:
        return self.root / f"jpn-{self.platform}"

    @property
    def image_root(self) -> Path:
        return self.root / f"image-{self.platform}"

    def source(self, relative_path: str | Path) -> Path:
        return self.source_root / relative_path

    def artifacts(self, relative_path: str | Path) -> Path:
        path = self.image_root / relative_path
        path.mkdir(parents=True, exist_ok=True)
        return path


def native_artifact_name(source_name: str, language: str) -> str:
    if language not in {"jpn", "kor"}:
        raise ValueError(f"unsupported language: {language}")
    source = Path(source_name)
    return f"{source.stem}.{language}{source.suffix}"


def offset_stem(offset: int) -> str:
    if offset < 0:
        raise ValueError("offset must not be negative")
    return f"{offset:06X}"


def update_meta(path: Path, **values: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"{path}: metadata root must be an object")
        data.update(loaded)
    data.update(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data
