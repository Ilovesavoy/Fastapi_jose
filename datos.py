# ============================================
# DATOS FIJOS - SIMULACIÓN DE BASE DE DATOS
# ============================================

from modelos import Estudiante

# Lista de estudiantes (Array de objetos)
# Cada uno tiene 5 notas; 'nota' es el promedio de esas 5 notas
estudiantes_db = [
    Estudiante(
        cedula="V-12345678",
        nombre="Carlos",
        apellido="Pérez",
        seccion="4DA",
        notas=[16, 17, 16, 17, 16.5],
        nota=16.5,
        activo=True
    ),

    Estudiante(
        cedula="V-23456789",
        nombre="María",
        apellido="González",
        seccion="4DA",
        notas=[18, 17, 19, 18, 18],
        nota=18.0,
        activo=True
    ),

    Estudiante(
        cedula="V-34567890",
        nombre="Juan",
        apellido="Rodríguez",
        seccion="4DB",
        notas=[12, 13, 12, 13, 12.5],
        nota=12.5,
        activo=True
    ),

    Estudiante(
        cedula="V-45678901",
        nombre="Ana",
        apellido="Martínez",
        seccion="4DA",
        notas=[9, 8, 10, 9, 9],
        nota=9.0,
        activo=False
    ),

    Estudiante(
        cedula="V-56789012",
        nombre="Pedro",
        apellido="López",
        seccion="4DB",
        notas=[20, 20, 20, 20, 20],
        nota=20.0,
        activo=True
    )
]

# Función para buscar estudiante por cédula
def buscar_estudiante(cedula: str):
    for est in estudiantes_db:
        if est.cedula == cedula:
            return est
    return None

# Función para filtrar por sección
def filtrar_por_seccion(seccion: str):
    return [est for est in estudiantes_db if est.seccion == seccion]

# Función para obtener aprobados
def obtener_aprobados():
    return [est for est in estudiantes_db if est.aprobo()]