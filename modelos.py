# ============================================
# MODELOS DE DATOS - FASTAPI + PYDANTIC
# Estudiante: Jose velasquez
# Cédula: V-27650743
# ============================================

from pydantic import BaseModel, Field
from typing import Optional

class Estudiante(BaseModel):
    """Modelo que representa un estudiante del IUTIRLA"""
    cedula: str = Field(..., description="Cédula de identidad")
    nombre: str = Field(..., description="Nombre del estudiante")
    apellido: str = Field(..., description="Apellido del estudiante")
    seccion: str = Field(..., description="Sección académica")
    nota: float = Field(..., ge=0, le=20, description="Nota final (0-20)")
    activo: bool = Field(default=True, description="¿Está activo?")

    # Método para verificar si aprobó
    def aprobo(self) -> bool:
        return self.nota >= 10

    # Método para obtener estatus
    def get_estatus(self) -> str:
        if self.nota >= 18:
            return "EXCELENTE"
        elif self.nota >= 14:
            return "BUENO"
        elif self.nota >= 10:
            return "SATISFACTORIO"
        else:
            return "DEFICIENTE"

class EstudianteCreate(BaseModel):
    """Modelo para crear nuevo estudiante (sin cédula automática)"""
    cedula: str
    nombre: str
    apellido: str
    seccion: str
    nota: float = Field(..., ge=0, le=20)

class EstudianteReemplazo(BaseModel):
    #modelo para crear un nuevo estudiante
    cedula: str
    nombre: str
    apellido: str
    seccion: str
    nota: float = Field(..., ge=0, le=20)
    activo: bool = True

class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    seccion: Optional[str] = None
    nota: Optional[float] =Field(None, ge=0, le=20)
    activo: Optional[bool] = None