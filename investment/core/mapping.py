from pydantic import BaseModel
from typing import Dict, Any, ClassVar, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..datasource.local import LocalDataSource

class BaseMappingEntity(BaseModel):
    entity_type: str
    code: str

    @classmethod
    def _get_local_datasource(cls) -> "LocalDataSource":
        if cls._local_datasource is None:
            from ..datasource.local import LocalDataSource
            cls._local_datasource = LocalDataSource()
        return cls._local_datasource

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        lds = self._get_local_datasource()

        load_methods = {
            "security": lds.load_security,
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
