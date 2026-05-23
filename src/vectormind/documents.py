"""Shared document models for ingestion pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ParsedPage:
    """A normalized page extracted from a source document."""

    page_number: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """A normalized document produced by an ingestion parser."""

    source_path: Path
    file_name: str
    page_count: int
    pages: tuple[ParsedPage, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
