import re

import inflect

p = inflect.engine()


def camel_to_snake(s: str) -> str:
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub("__([A-Z])", r"_\1", s)
    s = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


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
    words = p.number_to_words(v)  # type: ignore
    word: str = words[0] if isinstance(words, list) else words
    return word.replace(" ", "_")
