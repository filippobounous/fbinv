"Generic security class, to correctly initialise from a given code"

from typing import ClassVar, Optional

from .base import BaseSecurity

class Generic:
    """
    Generic Security.
    
    Initialises a generic security from its code by checking available secuirty
    mappings. If available will locate the correct BaseSecurity subclass to
    initialise. Initialised with:
        code (str): The Bloomberg ticker for the security.
        
    Use self.security to return the initialised security
    """
    entity_type: ClassVar[str] = "generic"
    security: BaseSecurity

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:
        """Initialise the wrapped security from local mapping."""
        from ...datasource.local import LocalDataSource

        if code is not None:
            kwargs["code"] = code

        self.security = LocalDataSource().load_generic_security(**kwargs)
