from pydantic import BaseModel

class BaseMappingEntity(BaseModel):
    entity_type: str
    code: str
    
    def __init__(self, **kwargs):
        from ..datasource.local import LocalDataSource

        super().__init__(**kwargs)

        load_methods = {
            "security": LocalDataSource.load_security,
            "currency_cross": LocalDataSource.load_security,
            "etf": LocalDataSource.load_security,
            "fund": LocalDataSource.load_security,
            "portfolio": LocalDataSource.load_portfolio,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)
