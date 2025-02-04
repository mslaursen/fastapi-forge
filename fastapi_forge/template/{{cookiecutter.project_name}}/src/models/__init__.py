{%- for model in cookiecutter.models.models -%}
from src.models.{{ model.name | camel_to_snake }}_models import {{ model.name }}
{% endfor %}

__all__ = [
    {% for model in cookiecutter.models.models %}
    "{{ model.name }}",
    {% endfor %}
]
