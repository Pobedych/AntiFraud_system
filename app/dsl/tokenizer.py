from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    pos: int  # 0-based char position


KEYWORDS = {"AND", "OR", "NOT"}


def tokenize(src: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(src)

    def add(kind: str, text: str, pos: int):
        tokens.append(Token(kind=kind, text=text, pos=pos))

    while i < n:
        c = src[i]

        # whitespace
        if c.isspace():
            i += 1
            continue

        # parentheses
        if c == "(":
            add("LPAREN", "(", i)
            i += 1
            continue
        if c == ")":
            add("RPAREN", ")", i)
            i += 1
            continue

        # operators (2-char first)
        if src.startswith(">=", i) or src.startswith("<=", i) or src.startswith("!=", i):
            add("OP", src[i:i+2], i)
            i += 2
            continue
        if c in "<>=":
            add("OP", c, i)
            i += 1
            continue

        # string literal: '...'
        if c == "'":
            start = i
            i += 1
            buf = []
            while i < n:
                if src[i] == "'":
                    add("STRING", "".join(buf), start)
                    i += 1
                    break
                # simple escaping for \' and \\ (optional)
                if src[i] == "\\" and i + 1 < n:
                    nxt = src[i+1]
                    if nxt in ["\\", "'"]:
                        buf.append(nxt)
                        i += 2
                        continue
                buf.append(src[i])
                i += 1
            else:
                # unterminated string -> still emit, parser will error
                add("UNTERM_STRING", src[start:], start)
            continue

        # number: digits with optional dot
        if c.isdigit():
            start = i
            while i < n and (src[i].isdigit() or src[i] == "."):
                i += 1
            add("NUMBER", src[start:i], start)
            continue

        # identifier: letters, digits, underscore, dot
        if c.isalpha() or c == "_":
            start = i
            while i < n and (src[i].isalnum() or src[i] in "._"):
                i += 1
            text = src[start:i]
            up = text.upper()
            if up in KEYWORDS:
                add(up, up, start)
            else:
                add("IDENT", text, start)
            continue

        # unknown char
        add("UNKNOWN", c, i)
        i += 1

    add("EOF", "", n)
    return tokens
