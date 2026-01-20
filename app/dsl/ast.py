from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Node:
    pos: int


@dataclass(frozen=True)
class Field(Node):
    name: str


@dataclass(frozen=True)
class Number(Node):
    value: float


@dataclass(frozen=True)
class String(Node):
    value: str


@dataclass(frozen=True)
class Compare(Node):
    op: str
    left: Node
    right: Node


@dataclass(frozen=True)
class Not(Node):
    expr: Node


@dataclass(frozen=True)
class And(Node):
    left: Node
    right: Node


@dataclass(frozen=True)
class Or(Node):
    left: Node
    right: Node
