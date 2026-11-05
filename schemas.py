from pydantic import BaseModel, ConfigDict
from typing import Optional

class Obra(BaseModel):
    id: Optional[int] = None
    titulo: str
    sinopse: str
    autor: str
    nota: float
    ativo: bool = True

    model_config = ConfigDict(from_attributes = True)

class ObraStatus(BaseModel):
    ativo: bool

class ObraUpdate(BaseModel):
    titulo: Optional[str] = None
    sinopse: Optional[str] = None
    autor: Optional[str] = None
    nota: Optional[float] = None

class ObraSearch(BaseModel):
    id: int
    titulo: str

    model_config = ConfigDict(from_attributes = True)