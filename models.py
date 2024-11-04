from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
import json

class Usuario(BaseModel):
    id: str
    nombre: str
    email: str
    edad: int

class Proyecto(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    id_usuario: str
    # fecha_creacion: datetime = Field(default = json.dumps(date.today().strftime("%Y-%m-%d %H:%M:%S")))
    fecha_creacion: str = Field(default = date.today())