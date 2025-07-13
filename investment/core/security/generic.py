"""Factory class used to initialise the correct security from a given code"""

from typing import ClassVar, Type

from .base import BaseSecurity


class Generic:
    """
    Generic Security.

    Acts as a factory returning the correct :class:`BaseSecurity` subclass for
    the provided ``code``.  Example::

        sec = Generic("SPY US")  # ``sec`` is an instance of :class:`ETF`

    ``code`` is the Bloomberg ticker for the security.
    """

    entity_type: ClassVar[str] = "generic"

    def __new__(
        cls: Type["Generic"], code: str | None = None, **kwargs
    ) -> "BaseSecurity":
        """Initialise the wrapped security from local mapping."""
        from ...datasource.local import LocalDataSource

        if code is not None:
            kwargs["code"] = code

        return LocalDataSource().load_generic_security(**kwargs)


__all__ = [
    "Generic",
]
