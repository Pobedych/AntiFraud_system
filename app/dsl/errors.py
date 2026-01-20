from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DslIssue:
    code: str
    message: str
    position: int | None = None
    near: str | None = None
