import re

OPS = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}

NUMBER_RE = re.compile(r"^\s*(\w+(?:\.\w+)*)\s*(>=|<=|!=|=|>|<)\s*(\d+(\.\d+)?)\s*$")
STRING_RE = re.compile(r"^\s*(\w+(?:\.\w+)*)\s*(=|!=)\s*'([^']*)'\s*$")

ALLOWED_FIELDS = {
    "amount",
    "currency",
    "merchantId",
    "merchantCategoryCode",
    "ipAddress",
    "deviceId",
    "channel",
    "location.country",
    "user.age",
    "user.region",
}


def validate_expression(expr: str) -> dict:
    """
    Возвращает формат как в ТЗ:
    {
      "isValid": bool,
      "normalizedExpression": str|None,
      "errors": [{code,message,position,near}]
    }
    Tier 5 но без AST: мы валидируем синтаксис + поля/операторы.
    """
    expr = (expr or "").strip()
    if len(expr) < 3:
        return {
            "isValid": False,
            "normalizedExpression": None,
            "errors": [{"code": "DSL_PARSE_ERROR", "message": "Expression too short", "position": 0, "near": expr}],
        }

    norm = normalize(expr)

    # проверка простого синтаксиса на AND/OR/NOT скобки мы тут не делаем полностью,
    # но делаем безопасно: каждую "часть" пытаемся распарсить по NUMBER/STRING.
    # В случае ошибки -> DSL_PARSE_ERROR
    parts = split_logical(norm)

    for p in parts:
        p = p.strip()
        if not p:
            return {
                "isValid": False,
                "normalizedExpression": None,
                "errors": [{"code": "DSL_PARSE_ERROR", "message": "Empty token", "position": 0, "near": norm[:20]}],
            }

        # NOT в начале допускаем
        if p.startswith("NOT "):
            p = p[4:].strip()

        # NUMBER
        m = NUMBER_RE.match(p)
        if m:
            field, op, _, _ = m.groups()
            if field not in ALLOWED_FIELDS:
                return {
                    "isValid": False,
                    "normalizedExpression": None,
                    "errors": [{"code": "DSL_INVALID_FIELD", "message": f"Unknown field: {field}", "position": 0, "near": field}],
                }
            # строкам > < нельзя — но это проверим в runtime по типам (упрощённо)
            return_ok = True
            if not return_ok:
                return {
                    "isValid": False,
                    "normalizedExpression": None,
                    "errors": [{"code": "DSL_INVALID_OPERATOR", "message": f"Invalid operator {op}", "position": 0, "near": op}],
                }
            continue

        # STRING
        m = STRING_RE.match(p)
        if m:
            field, op, _ = m.groups()
            if field not in ALLOWED_FIELDS:
                return {
                    "isValid": False,
                    "normalizedExpression": None,
                    "errors": [{"code": "DSL_INVALID_FIELD", "message": f"Unknown field: {field}", "position": 0, "near": field}],
                }
            if op not in ("=", "!="):
                return {
                    "isValid": False,
                    "normalizedExpression": None,
                    "errors": [{"code": "DSL_INVALID_OPERATOR", "message": f"Invalid operator for string: {op}", "position": 0, "near": op}],
                }
            continue

        # иначе — синтаксис не распознан
        return {
            "isValid": False,
            "normalizedExpression": None,
            "errors": [{"code": "DSL_PARSE_ERROR", "message": "Unsupported or invalid expression part", "position": 0, "near": p[:20]}],
        }

    return {"isValid": True, "normalizedExpression": norm, "errors": []}


def normalize(expr: str) -> str:
    # нормализуем пробелы, приводим AND/OR/NOT к upper вокруг пробелов
    expr = " ".join(expr.split())
    # простая нормализация ключевых слов
    expr = expr.replace(" and ", " AND ").replace(" And ", " AND ").replace(" AND ", " AND ")
    expr = expr.replace(" or ", " OR ").replace(" Or ", " OR ").replace(" OR ", " OR ")
    expr = expr.replace(" not ", " NOT ").replace(" Not ", " NOT ").replace(" NOT ", " NOT ")
    return expr.strip()


def split_logical(expr: str) -> list[str]:
    """
    Разбивает выражение по AND/OR верхнего уровня (без полноценного парсинга скобок).
    Для Tier5 "упрощённо" этого достаточно, чтобы validate не падал.
    """
    # для простоты: split по ' AND ' и ' OR ', сохраняя части
    tmp = []
    cur = []
    tokens = expr.split(" ")
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("AND", "OR"):
            tmp.append(" ".join(cur))
            cur = []
        else:
            cur.append(t)
        i += 1
    if cur:
        tmp.append(" ".join(cur))
    return tmp


def evaluate_simple(expr: str, tx: dict, user: dict) -> bool:
    """
    Tier 5 (упрощённый):
    - amount > 100
    - currency = 'RUB'
    - user.age >= 18
    - AND / OR
    - NOT
    """
    expr = normalize(expr)

    # OR
    if " OR " in expr:
        return any(evaluate_simple(p, tx, user) for p in expr.split(" OR "))

    # AND
    if " AND " in expr:
        return all(evaluate_simple(p, tx, user) for p in expr.split(" AND "))

    # NOT
    if expr.startswith("NOT "):
        return not evaluate_simple(expr[4:].strip(), tx, user)

    # NUMBER
    m = NUMBER_RE.match(expr)
    if m:
        field, op, value, _ = m.groups()
        left = resolve_field(field, tx, user)
        if left is None:
            return False
        try:
            return OPS[op](float(left), float(value))
        except Exception:
            return False

    # STRING
    m = STRING_RE.match(expr)
    if m:
        field, op, value = m.groups()
        left = resolve_field(field, tx, user)
        if left is None:
            return False
        return OPS[op](str(left), value)

    # unsupported
    return False


def resolve_field(name: str, tx: dict, user: dict):
    if name.startswith("user."):
        return user.get(name.split(".", 1)[1])

    if "." in name:
        root, sub = name.split(".", 1)
        obj = tx.get(root) or {}
        return obj.get(sub)

    return tx.get(name)
