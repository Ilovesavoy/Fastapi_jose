# ============================================
# API REST - CONSULTA DE ESTUDIANTES IUTIRLA
# Estudiante: jose velasquez
# Cédula: V-27650743
# ============================================

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from modelos import Estudiante, EstudianteCreate, EstudianteReemplazo, EstudianteUpdate
from datos import estudiantes_db, buscar_estudiante, filtrar_por_seccion, obtener_aprobados

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Estudiantes IUTIRLA",
    description="API para consultar estudiantes de Programación III",
    version="1.0.0",
    contact={"name": "Prof. Jhonatan Fernandez"}
)

# ============================================
# ENDPOINTS (RUTAS DE LA API)
# ============================================
@app.get("/")
def raiz():
    """Endpoint raíz - Información general"""
    return {
        "mensaje": "Bienvenido a la API de Estudiantes IUTIRLA",
        "profesor": "Jhonatan Fernandez",
        "asignatura": "Programación III",
        "documentacion": "/docs"
    }

@app.get("/estudiantes", response_model=List[Estudiante])
def listar_estudiantes(
    seccion: Optional[str] = Query(None, description="Filtrar por sección"),
    solo_aprobados: Optional[bool] = Query(False, description="Solo estudiantes aprobados")
): 
    """Obtener lista de todos los estudiantes con filtros opcionales"""
    resultado = estudiantes_db
    if seccion:
        resultado = [e for e in resultado if e.seccion == seccion]
    elif solo_aprobados:
        resultado = [e for e in resultado if e.aprobo()]
    return resultado

@app.get("/estudiantes/seccion/{seccion}", response_model=List[Estudiante])
def estudiantes_por_seccion(seccion: str):
    """Obtener todos los estudiantes de una sección específica"""
    resultado = filtrar_por_seccion(seccion)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No hay estudiantes en la sección {seccion}")
    return resultado

@app.get("/estudiantes/{cedula}")
def obtener_estudiante(cedula: str):
    """Obtener un estudiante específico por cédula"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@app.get("/estadisticas")
def obtener_estadisticas():
    """Obtener estadísticas generales del sistema"""
    total = len(estudiantes_db)
    aprobados = len(obtener_aprobados())
    reprobados = total - aprobados
    promedio = sum(est.nota for est in estudiantes_db) / total if total > 0 else 0

    return {
        "total_estudiantes": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": round(promedio, 2),
        "porcentaje_aprobacion": round((aprobados/total)*100, 2) if total > 0 else 0
    }

@app.post("/estudiantes", response_model=Estudiante, status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    """Registrar un nuevo estudiante"""
    # Verificar si ya existe
    if buscar_estudiante(estudiante.cedula):
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    # Crear nuevo estudiante
    nuevo = Estudiante(**estudiante.model_dump(), activo=True)
    estudiantes_db.append(nuevo)
    return nuevo

# ============================================
# PUT - Reemplazar completo
# ============================================
@app.put("/estudiantes/{cedula}", response_model=Estudiante)
def reemplazar_estudiante(cedula: str, datos: EstudianteReemplazo):
    """Reemplazar TODOS los datos de un estudiante (la cédula no cambia)"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
 
    indice = estudiantes_db.index(estudiante)
    reemplazo = Estudiante(**{**datos.model_dump(), "cedula": cedula})
    estudiantes_db[indice] = reemplazo
    return reemplazo
 
 
# ============================================
# PATCH - Actualizar parcial
# ============================================
@app.patch("/estudiantes/{cedula}", response_model=Estudiante)
def actualizar_estudiante(cedula: str, cambios: EstudianteUpdate):
    """Actualizar SOLO los campos enviados (por ejemplo, nada más la nota)"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
 
    campos = cambios.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="No se envió ningún campo para actualizar")
 
    indice = estudiantes_db.index(estudiante)
    actualizado = estudiante.model_copy(update=campos)
    estudiantes_db[indice] = actualizado
    return actualizado
 
 
# ============================================
# DELETE - Eliminar
# ============================================
@app.delete("/estudiantes/{cedula}")
def eliminar_estudiante(cedula: str):
    """Eliminar un estudiante por cédula"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
 
    estudiantes_db.remove(estudiante)
    return {"mensaje": f"Estudiante {estudiante.nombre} {estudiante.apellido} eliminado", "cedula": cedula}
 

# ============================================
# PUNTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)