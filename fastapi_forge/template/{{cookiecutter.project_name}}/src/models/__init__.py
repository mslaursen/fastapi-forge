{%- for model in cookiecutter.models.models -%}
from src.models.{{ model.name }}_models import {{ model.name_cc }}
{% endfor %}

__all__ = [
    {% for model in cookiecutter.models.models %}
    "{{ model.name_cc }}",
    {% endfor %}
]
