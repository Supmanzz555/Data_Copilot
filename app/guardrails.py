import sqlparse


def is_read_query(sql: str) -> bool:
    """Allow only single SELECT/WITH statements using sqlparse."""
    parsed = sqlparse.parse(sql.strip())
    if not parsed or len(parsed) != 1:
        return False
    stmt = parsed[0]
    if stmt.get_type() not in ("SELECT", "UNKNOWN"):
        return False
    upper = stmt.value.strip().upper()
    first = upper.split("--")[0].strip()
    return first.startswith("SELECT") or first.startswith("WITH")
