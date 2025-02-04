import asyncio
import inspect
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from src.db import Base
import factory
from typing import Any

{% for model in cookiecutter.models.models -%}
from src.models.{{ model.name | camel_to_snake }}_models import {{ model.name }}
{% endfor %}


class BaseFactory[Model: Base](factory.Factory):
    """
    This is the base factory class for all factories.
    
    Inherit from this class to create a new factory that provides a way to create
    new instances of a specific model, used for testing purposes.

    Example:
    >>> class UserFactory(BaseFactory[User]):
    >>>     ...
    >>>     class Meta:
    >>>         model = User
    """
    session: AsyncSession

    class Meta:
        abstract = True

    @classmethod
    async def create(cls, *args: Any, **kwargs: Any) -> Model:
        """Create and commit a new instance of the model."""
        instance = await super().create(*args, **kwargs)
        await cls.session.commit()
        return instance
    
    @classmethod
    async def create_batch(cls, size: int, *args: Any, **kwargs: Any) -> list[Model]:
        """Create a batch of new instances of the model."""
        return [await cls.create(*args, **kwargs) for _ in range(size)]

    @classmethod
    def _create(
        cls,
        model_class: type["BaseFactory[Model]"],
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task["BaseFactory[Model]"]:
        async def maker_coroutine() -> "BaseFactory[Model]":
            for key, value in kwargs.items():
                if inspect.isawaitable(value):
                    kwargs[key] = await value
            return await cls._create_model(model_class, *args, **kwargs)

        return asyncio.create_task(maker_coroutine())
    
    @classmethod
    async def _create_model(
        cls,
        model_class: type["BaseFactory[Model]"],
        *args: Any,
        **kwargs: Any,
    ) -> "BaseFactory[Model]":
        """Create a new instance of the model."""
        model = model_class(*args, **kwargs)
        cls.session.add(model)
        return model


###################
# Factory classes #
###################


{% for model in cookiecutter.models.models %}
class {{ model.name }}Factory(BaseFactory[{{ model.name }}]):
    """{{ model.name }} factory."""
    class Meta:
        model = {{ model.name }}

    {%- for field in model.fields %}
    {%- if "id" not in field.name %}
    {{ field.name | camel_to_snake }} = {{ field.factory_field_value }}
    {%- endif %}
    {%- endfor %}

    {%- if model.relationships %}
    @classmethod
    async def _create_model(
        cls, model_class: type[BaseFactory[{{ model.name }}]], *args: Any, **kwargs: Any
    ) -> BaseFactory[{{ model.name }}]:
        """Create a new instance of the model."""

        {%- for relationship in model.relationships %}
        if "{{ relationship.target | camel_to_snake }}" not in kwargs:
            kwargs["{{ relationship.target | camel_to_snake }}"] = await {{ relationship.target }}Factory.create()
        {%- endfor %}
        return await super()._create_model(model_class, *args, **kwargs)
    {%- endif %}
{% endfor %}
