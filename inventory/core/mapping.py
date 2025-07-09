from pydantic import BaseModel

class BaseMappingEntity(BaseModel):
    entity_type: str
    id: int
    code: str
    name: str
    description: str = ""
    notes: str = ""

__all__ = [
    "BaseMappingEntity",
]
