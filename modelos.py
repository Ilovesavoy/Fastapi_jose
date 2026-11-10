# ============================================
# MODELOS DE DATOS - FASTAPI + PYDANTIC
# Estudiante: Jose velasquez
# Cédula: V-27650743
# ============================================

from pydantic import BaseModel, Field
from typing import List, Optional

class Estudiante(BaseModel):
    """Modelo que representa un estudiante del IUTIRLA"""
    cedula: str = Field(..., description="Cédula de identidad")
    nombre: str = Field(..., description="Nombre del estudiante")
    apellido: str = Field(..., description="Apellido del estudiante")
    seccion: str = Field(..., description="Sección académica")
    nota: float = Field(..., ge=0, le=20, description="Nota final (0-20)")
    activo: bool = Field(default=True, description="¿Está activo?")
    notas: List[float] = Field(default_factory=list, description="Las 5 notas del estudiante (si fueron cargadas)")

    # Promedio calculado al momento: si hay 5 notas cargadas, se promedian;
    # si no, se usa la nota final que ya tenía el estudiante
    def get_promedio(self) -> float:
        if len(self.notas) == 5:
            return round(sum(self.notas) / 5, 2)
        return self.nota

    # Método para verificar si aprobó
    def aprobo(self) -> bool:
        return self.get_promedio() >= 10

    # Método para obtener estatus (escala del IUTIRLA)
    def get_estatus(self) -> str:
        promedio = self.get_promedio()
        if promedio >= 18:
            return "EXCELENTE"
        elif promedio >= 14:
            return "BUENO"
        elif promedio >= 10:
            return "SATISFACTORIO"
        else:
            return "DEFICIENTE"

class EstudianteCreate(BaseModel):
    """Modelo para crear un nuevo estudiante con sus 5 notas (POST)"""
    cedula: str
    nombre: str
    apellido: str
    seccion: str
    notas: List[float]


class EstudianteReemplazo(BaseModel):
    """Modelo para PUT: reemplazo completo (la cédula va en la URL)"""
    nombre: str
    apellido: str
    seccion: str
    notas: List[float]
    activo: bool = True


class EstudianteUpdate(BaseModel):
    """Modelo para PATCH: todos los campos son opcionales"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    seccion: Optional[str] = None
    notas: Optional[List[float]] = None
    activo: Optional[bool] = None


class EstudianteDetalle(Estudiante):
    """Estudiante + promedio y estatus calculados al generar la respuesta"""
    promedio: float
    estatus: str


class NotasEstudiante(BaseModel):
    """Entrada de PUT/POST /estudiantes/{cedula}/notas
    (las notas se validan a mano en el endpoint: exactamente 5, entre 0 y 20)"""
    cedula: Optional[str] = None
    nombre: str
    apellido: str
    seccion: str
    notas: List[float]