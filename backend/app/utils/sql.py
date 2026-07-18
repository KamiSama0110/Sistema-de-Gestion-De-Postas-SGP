def _escape_like(value: str) -> str:
    return value.replace("%", "\\%").replace("_", "\\_")
