from __future__ import annotations

from app.dsl.tokenizer import Token
from app.dsl.ast import Field, Number, String, Compare, Not, And, Or, Node
from app.dsl.errors import DslIssue


class Parser:
    def __init__(self, tokens: list[Token], src: str):
        self.toks = tokens
        self.src = src
        self.i = 0

    def cur(self) -> Token:
        return self.toks[self.i]

    def eat(self, kind: str | None = None) -> Token:
        t = self.cur()
        if kind and t.kind != kind:
            raise self._err("DSL_PARSE_ERROR", f"Expected {kind}, got {t.kind}", t.pos)
        self.i += 1
        return t

    def _near(self, pos: int) -> str:
        return self.src[pos:pos+20]

    def _err(self, code: str, msg: str, pos: int) -> Exception:
        e = ValueError(msg)
        e.dsl_issue = DslIssue(code=code, message=msg, position=pos, near=self._near(pos))
        return e

    # Grammar:
    # expr := orExpr
    # orExpr := andExpr (OR andExpr)*
    # andExpr := unary (AND unary)*
    # unary := NOT unary | primary
    # primary := '(' expr ')' | comparison
    # comparison := operand OP operand
    # operand := IDENT | NUMBER | STRING
    def parse(self) -> Node:
        node = self._or()
        if self.cur().kind != "EOF":
            raise self._err("DSL_PARSE_ERROR", "Unexpected token", self.cur().pos)
        return node

    def _or(self) -> Node:
        node = self._and()
        while self.cur().kind == "OR":
            op = self.eat("OR")
            right = self._and()
            node = Or(pos=op.pos, left=node, right=right)
        return node

    def _and(self) -> Node:
        node = self._unary()
        while self.cur().kind == "AND":
            op = self.eat("AND")
            right = self._unary()
            node = And(pos=op.pos, left=node, right=right)
        return node

    def _unary(self) -> Node:
        if self.cur().kind == "NOT":
            t = self.eat("NOT")
            expr = self._unary()
            return Not(pos=t.pos, expr=expr)
        return self._primary()

    def _primary(self) -> Node:
        if self.cur().kind == "LPAREN":
            lp = self.eat("LPAREN")
            node = self._or()
            if self.cur().kind != "RPAREN":
                raise self._err("DSL_PARSE_ERROR", "Missing ')'", lp.pos)
            self.eat("RPAREN")
            return node
        return self._comparison()

    def _comparison(self) -> Node:
        left = self._operand()
        if self.cur().kind != "OP":
            raise self._err("DSL_PARSE_ERROR", "Expected operator", self.cur().pos)
        op = self.eat("OP")
        right = self._operand()
        return Compare(pos=op.pos, op=op.text, left=left, right=right)

    def _operand(self) -> Node:
        t = self.cur()
        if t.kind == "IDENT":
            self.eat("IDENT")
            return Field(pos=t.pos, name=t.text)
        if t.kind == "NUMBER":
            self.eat("NUMBER")
            try:
                return Number(pos=t.pos, value=float(t.text))
            except Exception:
                raise self._err("DSL_PARSE_ERROR", "Invalid number", t.pos)
        if t.kind == "STRING":
            self.eat("STRING")
            return String(pos=t.pos, value=t.text)
        raise self._err("DSL_PARSE_ERROR", "Expected operand", t.pos)
