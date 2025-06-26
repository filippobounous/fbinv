"Base class for initialisations from the mapping csv files available"

from typing import Dict, Any

from pydantic import BaseModel

from ..datasource.local import LocalDataSource

class BaseMappingEntity(BaseModel):
    """
    BaseMappingEntity.
    
    Returns required attributes to a class from the base csv mapping files.
    Initialised with:
        entity_type (str): The entity type to select the correct load_method.
        code (str): The code for the entity to select the correct parameters.
    """
    entity_type: str
    code: str
    _local_datasource: LocalDataSource = LocalDataSource

    def __init__(self, **kwargs):
        """Initialise entity attributes from the local mapping files."""
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "composite": lds.load_composite_security,
            "currency_cross": lds.load_security,
            "etf": lds.load_security,
            "fund": lds.load_security,
            "portfolio": lds.load_portfolio,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: Dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)
