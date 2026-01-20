from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ValueType(str, Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOL = "BOOL"
    NULL = "NULL"


@dataclass(frozen=True)
class FieldDef:
    name: str
    type: ValueType
    nullable: bool = False
