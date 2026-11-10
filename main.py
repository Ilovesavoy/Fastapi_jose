# ============================================
# API REST - CONSULTA DE ESTUDIANTES IUTIRLA
# Estudiante: jose velasquez
# Cédula: V-27650743
# ============================================

from fastapi import FastAPI, HTTPException, Query, Response
from typing import List, Optional
from modelos import (
    Estudiante, EstudianteCreate, EstudianteReemplazo, EstudianteUpdate,
    EstudianteDetalle, NotasEstudiante,
)
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

def a_detalle(est: Estudiante) -> EstudianteDetalle:
    """Recalcula promedio y estatus del estudiante al momento de responder"""
    return EstudianteDetalle(
        **est.model_dump(),
        promedio=est.get_promedio(),
        estatus=est.get_estatus(),
    )

def validar_notas(notas: List[float]) -> float:
    """Valida que sean exactamente 5 notas entre 0 y 20 y devuelve el promedio"""
    if len(notas) != 5:
        raise HTTPException(status_code=400, detail="Se necesitan exactamente 5 notas")
    for nota in notas:
        if nota < 0 or nota > 20:
            raise HTTPException(status_code=400, detail=f"La nota {nota} es inválida: debe estar entre 0 y 20")
    return round(sum(notas) / 5, 2)

# ============================================
# REQUERIMIENTO 2 - GET /estudiantes (con filtros)
# ============================================
@app.get("/estudiantes", response_model=List[EstudianteDetalle])
def listar_estudiantes(
    seccion: Optional[str] = Query(None, description="Filtrar por sección"),
    cedula: Optional[str] = Query(None, description="Filtrar por cédula"),
    solo_aprobados: Optional[bool] = Query(False, description="Solo estudiantes aprobados")
):
    """Lista de estudiantes con su promedio y estatus (filtros opcionales)"""
    resultado = estudiantes_db
    if seccion:
        resultado = [e for e in resultado if e.seccion == seccion]
    if cedula:
        resultado = [e for e in resultado if e.cedula == cedula]
    if solo_aprobados:
        resultado = [e for e in resultado if e.aprobo()]
    return [a_detalle(e) for e in resultado]

@app.get("/estudiantes/seccion/{seccion}", response_model=List[EstudianteDetalle])
def estudiantes_por_seccion(seccion: str):
    """Obtener todos los estudiantes de una sección específica"""
    resultado = filtrar_por_seccion(seccion)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No hay estudiantes en la sección {seccion}")
    return [a_detalle(e) for e in resultado]

@app.get("/estudiantes/{cedula}", response_model=EstudianteDetalle)
def obtener_estudiante(cedula: str):
    """Obtener un estudiante específico por cédula"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return a_detalle(estudiante)

@app.get("/estadisticas")
def obtener_estadisticas():
    """Obtener estadísticas generales del sistema"""
    total = len(estudiantes_db)
    aprobados = len(obtener_aprobados())
    reprobados = total - aprobados
    promedio = sum(est.get_promedio() for est in estudiantes_db) / total if total > 0 else 0

    return {
        "total_estudiantes": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": round(promedio, 2),
        "porcentaje_aprobacion": round((aprobados/total)*100, 2) if total > 0 else 0
    }

@app.post("/estudiantes", response_model=EstudianteDetalle, status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    """Registrar un nuevo estudiante con sus 5 notas"""
    # Verificar si ya existe
    if buscar_estudiante(estudiante.cedula):
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    promedio = validar_notas(estudiante.notas)
    nuevo = Estudiante(**estudiante.model_dump(), nota=promedio, activo=True)
    estudiantes_db.append(nuevo)
    return a_detalle(nuevo)

# ============================================
# REQUERIMIENTO 1 - CARGAR O ACTUALIZAR NOTAS (PUT o POST)
# ============================================
@app.put("/estudiantes/{cedula}/notas")
def cargar_notas(cedula: str, datos: NotasEstudiante, response: Response):
    """Carga 5 notas: si la cédula existe actualiza al estudiante, si no, lo crea"""
    # 1. Validar que la cédula del cuerpo (si viene) coincida con la de la URL
    if datos.cedula and datos.cedula != cedula:
        raise HTTPException(status_code=400, detail="La cédula del cuerpo no coincide con la de la URL")

    # 2. Validar las 5 notas (0 a 20) y calcular el promedio
    promedio = validar_notas(datos.notas)

    # 3. Buscar si la cédula ya existe: actualizar o crear
    estudiante = buscar_estudiante(cedula)
    if estudiante:
        indice = estudiantes_db.index(estudiante)
        estudiante = estudiante.model_copy(update={
            "nombre": datos.nombre,
            "apellido": datos.apellido,
            "seccion": datos.seccion,
            "notas": datos.notas,
            "nota": promedio,
        })
        estudiantes_db[indice] = estudiante
        mensaje = "Notas actualizadas"
    else:
        estudiante = Estudiante(
            cedula=cedula,
            nombre=datos.nombre,
            apellido=datos.apellido,
            seccion=datos.seccion,
            notas=datos.notas,
            nota=promedio,
        )
        estudiantes_db.append(estudiante)
        response.status_code = 201
        mensaje = "Estudiante creado y notas guardadas"

    return {
        "mensaje": mensaje,
        "estudiante": estudiante,
        "promedio": promedio,
        "estatus": estudiante.get_estatus(),
    }

# ============================================
# PUT - Reemplazar completo
# ============================================
@app.put("/estudiantes/{cedula}", response_model=EstudianteDetalle)
def reemplazar_estudiante(cedula: str, datos: EstudianteReemplazo):
    """Reemplazar TODOS los datos de un estudiante, incluidas sus 5 notas (la cédula no cambia)"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    promedio = validar_notas(datos.notas)
    indice = estudiantes_db.index(estudiante)
    reemplazo = Estudiante(**datos.model_dump(), cedula=cedula, nota=promedio)
    estudiantes_db[indice] = reemplazo
    return a_detalle(reemplazo)


# ============================================
# PATCH - Actualizar parcial
# ============================================
@app.patch("/estudiantes/{cedula}", response_model=EstudianteDetalle)
def actualizar_estudiante(cedula: str, cambios: EstudianteUpdate):
    """Actualizar SOLO los campos enviados (si envías notas, deben ser las 5)"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    campos = {k: v for k, v in cambios.model_dump(exclude_unset=True).items() if v is not None}
    if not campos:
        raise HTTPException(status_code=400, detail="No se envió ningún campo para actualizar")

    # Si vienen notas, se validan y se recalcula la nota final (promedio)
    if "notas" in campos:
        campos["nota"] = validar_notas(campos["notas"])

    indice = estudiantes_db.index(estudiante)
    actualizado = estudiante.model_copy(update=campos)
    estudiantes_db[indice] = actualizado
    return a_detalle(actualizado)


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