"""Analisis semantico completo: identificadores + tipos + reporte.

La tabla de simbolos (1.2) vive en tabla_simbolos.py. verificar_semantica
acepta cualquier tabla con las cuatro operaciones del contrato (resolver,
declarar, entrar, salir); por omision crea una con FABRICA_TABLA.
"""

from parser.integracion import NodoASA
from parser.semantica.errores_semanticos import ErrorSemantico, recolectar
from parser.semantica.inferencia_tipos import InferidorTipos
from parser.semantica.tabla_simbolos import TablaSimbolos
from parser.semantica.verificador_identificadores import (
    VerificadorIdentificadores,
)

FABRICA_TABLA = TablaSimbolos


def verificar_semantica(arbol: NodoASA, tabla=None) -> list[ErrorSemantico]:
    """Corre identificadores y tipos; retorna los errores ordenados.

    Si se pasa `tabla`, al terminar conserva todos los simbolos registrados
    (con el tipo inferido de las funciones), listos para consultar o imprimir.
    """
    tabla = tabla if tabla is not None else FABRICA_TABLA()
    identificadores = VerificadorIdentificadores(
        tabla.resolver, tabla.declarar, tabla.entrar, tabla.salir
    ).verificar(arbol)
    # Un nombre sin declarar deja su tipo en None y la inferencia no lo
    # usa, asi que correr ambas fases no genera errores en cascada.
    tipos = InferidorTipos().inferir(arbol)
    return recolectar(("identificadores", identificadores), ("tipos", tipos))
