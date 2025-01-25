import asyncio
import inspect
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from src.models import Base
import factory
from typing import Any

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
