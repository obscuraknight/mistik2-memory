"""Immutable per-user storage-path map. Construction-time ownership."""
from __future__ import annotations

import dataclasses
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Union

_TARGET_FILENAMES: Mapping[str, str] = MappingProxyType({
    "longmem": "longmem.json",
    "corrections": "corrections.json",
    "people": "people.json",
    "advanced_memory": "advanced_memory.json",
    "kb": "knowledge.db",
    "vec": "knowledge.db",
})

REQUIRED_PATH_KEYS = frozenset(_TARGET_FILENAMES)


def _build_paths(root: Path) -> Mapping[str, Path]:
    return MappingProxyType({key: root / name for key, name in _TARGET_FILENAMES.items()})


@dataclasses.dataclass(frozen=True)
class StorageContext:
    """Filesystem identity only: user_id, root, and a read-only path map."""

    user_id: str
    root: Path
    paths: Mapping[str, Path]

    @classmethod
    def from_root(cls, user_id: str, root: Union[Path, str]) -> "StorageContext":
        if not user_id or not str(user_id).strip():
            raise ValueError("StorageContext requires a non-empty user_id")
        root_path = Path(root)
        return cls(user_id=user_id, root=root_path, paths=_build_paths(root_path))
