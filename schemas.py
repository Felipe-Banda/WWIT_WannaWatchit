from pydantic import BaseModel
from typing import Optional

class Obra(BaseModel):
    id: int
    titulo: str
    sinopse: str
    autor: str
    nota: float
    ativo: bool = True

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