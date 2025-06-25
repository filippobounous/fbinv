from typing import ClassVar, Optional

from .base import BaseSecurity

class Generic:
    entity_type: ClassVar[str] = "generic"
    security: BaseSecurity

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:
        from ...datasource.local import LocalDataSource

        if code is not None:
            kwargs["code"] = code

        self.security = LocalDataSource().load_generic_security(**kwargs)
