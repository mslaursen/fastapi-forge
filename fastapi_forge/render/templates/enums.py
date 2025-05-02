ENUMS_TEMPLATE = """
from enum import StrEnum, auto

{% for enum in enums %}
{{ enum.class_definition }}
{% endfor %}
"""
