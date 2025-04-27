DAO_TEMPLATE = """
from {{ project_name }}.daos.base_daos import BaseDAO

from {{ project_name }}.models.{{ model.name }}_models import {{ model.name_cc }}
from {{ project_name }}.dtos.{{ model.name }}_dtos import {{ model.name_cc }}InputDTO, {{ model.name_cc }}UpdateDTO


class {{ model.name_cc }}DAO(
    BaseDAO[
        {{ model.name_cc }},
        {{ model.name_cc }}InputDTO,
        {{ model.name_cc }}UpdateDTO,
    ]
):
    \"\"\"{{ model.name_cc }} DAO.\"\"\"
"""
