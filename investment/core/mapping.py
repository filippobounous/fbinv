from pydantic import BaseModel
from typing import Dict, Any

from ..datasource.local import LocalDataSource

class BaseMappingEntity(BaseModel):
    entity_type: str
    code: str
    _local_datasource: LocalDataSource = LocalDataSource

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "security": lds.load_security,
            "currency_cross": lds.load_security,
            "etf": lds.load_security,
            "fund": lds.load_security,
            "portfolio": lds.load_portfolio,
            "composite": lds.load_composite,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: Dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)
