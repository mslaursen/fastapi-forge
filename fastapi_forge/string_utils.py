import inflect

p = inflect.engine()


def _convert(s: str, separator: str) -> str:
    return "".join([separator + c.lower() if c.isupper() else c for c in s]).lstrip(
        separator,
    )


def camel_to_snake(s: str) -> str:
    return _convert(s, "_")


def snake_to_camel(s: str) -> str:
    s = s.removesuffix("_id")
    words = s.split("_")
    return "".join(word.capitalize() for word in words)


def pluralize(s: str) -> str:
    is_singular = not p.singular_noun(s)
    if is_singular:
        return p.plural(s)
    return s


def number_to_word(v: int | str) -> str:
    words = p.number_to_words(v)
    word: str = words[0] if isinstance(words, list) else words
    return word.replace(" ", "_")
