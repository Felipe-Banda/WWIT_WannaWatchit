from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from database import Base

class Obra(Base):
     __tablename__ = 'obras'

     id = Column(Integer, primary_key = True, index = True)
     titulo = Column(String(255), index = True, nullable = False)
     sinopse = Column(Text, nullable = False)
     autor = Column(String(100), nullable = False)
     nota = Column(Float, nullable = False)
     ativo = Column(Boolean, default = True)