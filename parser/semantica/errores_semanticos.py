"""Reporte de errores semanticos (1.3.4).

Los verificadores (identificadores e inferencia de tipos) devuelven listas de
textos con el formato "Linea L, columna C: mensaje". Este modulo los convierte
en ErrorSemantico, los ordena por posicion, elimina duplicados y los imprime
con el mismo estilo que el parser: archivo:linea:columna: mensaje.
"""

import re
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence, TextIO

# Configuracion del reporte.
PREFIJO_ERROR = "error semantico"
# Muestra la linea de codigo y un ^ bajo la columna del error.
MOSTRAR_FRAGMENTO = True
LIMITE_ERRORES: int | None = None    # None = sin limite.

_PATRON = re.compile(r"^Linea (\d+), columna (\d+): (.*)$", re.DOTALL)


@dataclass(frozen=True)
class ErrorSemantico:
    linea: int
    columna: int
    mensaje: str
    fase: str = ""    # "identificadores" o "tipos".


def convertir(textos: Iterable[str], fase: str = "") -> list[ErrorSemantico]:
    """Convierte "Linea L, columna C: mensaje". Si no calza, usa 0:0."""
    errores = []
    for texto in textos:
        coincidencia = _PATRON.match(texto)
        if coincidencia:
            linea, columna, mensaje = coincidencia.groups()
            errores.append(ErrorSemantico(
                int(linea), int(columna), mensaje, fase))
        else:
            errores.append(ErrorSemantico(0, 0, texto, fase))
    return errores


def recolectar(*fases: tuple[str, Iterable[str]]) -> list[ErrorSemantico]:
    """Une los errores de varias fases, sin duplicados y por posicion."""
    todos: list[ErrorSemantico] = []
    vistos = set()
    for fase, textos in fases:
        for error in convertir(textos, fase):
            clave = (error.linea, error.columna, error.mensaje)
            if clave not in vistos:
                vistos.add(clave)
                todos.append(error)
    return sorted(todos, key=lambda e: (e.linea, e.columna))


def formatear(
    error: ErrorSemantico,
    ruta: str,
    lineas_fuente: Sequence[str] | None = None,
) -> str:
    texto = (f"{ruta}:{error.linea}:{error.columna}: "
             f"{PREFIJO_ERROR}: {error.mensaje}")
    if (MOSTRAR_FRAGMENTO and lineas_fuente
            and 1 <= error.linea <= len(lineas_fuente)):
        codigo = lineas_fuente[error.linea - 1]
        relleno = "".join(
            "\t" if c == "\t" else " " for c in codigo[:error.columna - 1])
        texto += f"\n    {codigo}\n    {relleno}^"
    return texto


def reportar(
    errores: Sequence[ErrorSemantico],
    ruta: str,
    fuente: str = "",
    salida: TextIO | None = None,
) -> int:
    """Imprime los errores y un resumen. Retorna la cantidad de errores."""
    salida = salida or sys.stderr
    lineas = fuente.splitlines()
    mostrados = errores if LIMITE_ERRORES is None else errores[:LIMITE_ERRORES]
    for error in mostrados:
        print(formatear(error, ruta, lineas), file=salida)
    if errores:
        total = len(errores)
        resumen = f"{total} error{'es' if total != 1 else ''} semantico"
        resumen += "s" if total != 1 else ""
        if len(mostrados) < total:
            resumen += f" ({len(mostrados)} mostrados)"
        print(resumen, file=salida)
    return len(errores)
