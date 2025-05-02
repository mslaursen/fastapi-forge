{% for model in cookiecutter.models.models if model.metadata.create_daos -%}
from {{cookiecutter.project_name}}.daos.{{ model.name }}_daos import {{ model.name_cc }}DAO
{% endfor %}
from {{cookiecutter.project_name}}.db.db_dependencies import GetDBSession
from fastapi import Depends
from typing import Annotated


class AllDAOs:
    """
    A centralized container for all DAOs used in the application.
    This class provides an organized way to access different DAOs as properties.

    Example:
        To add a new DAO, define a property method that returns
        an instance of the desired DAO:

        >>> @property
        >>> def user(self) -> UserDAO:
        >>>     return UserDAO(self.session)

        This allows you to access the `UserDAO` like so:

        >>> @router.post("/myroute")
        >>> async def my_route(daos: GetDAOs) -> ...:
        >>>     await daos.user.create(...)
    """

    def __init__(self, session: GetDBSession):
        self.session = session

    {% for model in cookiecutter.models.models if model.metadata.create_daos %}
    @property
    def {{ model.name }}(self) -> {{ model.name_cc }}DAO:
        return {{ model.name_cc }}DAO(self.session)
    {% endfor %}


GetDAOs = Annotated[AllDAOs, Depends()]
