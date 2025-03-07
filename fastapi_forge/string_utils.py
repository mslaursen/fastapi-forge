def _convert(value: str, separator: str) -> str:
    return "".join([separator + c.lower() if c.isupper() else c for c in value]).lstrip(
        separator
    )


def camel_to_snake(value: str) -> str:
    return _convert(value, "_")


def camel_to_snake_hyphen(value: str) -> str:
    return _convert(value, "-")


def snake_to_camel(s: str) -> str:
    s = s[:-3] if s.endswith("_id") else s
    words = s.split("_")
    return "".join(word.capitalize() for word in words)
