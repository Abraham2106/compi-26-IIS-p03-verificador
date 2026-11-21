"""Impresion del estado de la tabla en cada cambio (1.4.1)."""

import sys
from typing import TextIO

from parser.semantica.tabla_simbolos import (
    Cambio, Simbolo, TablaSimbolos, TipoCambio,
)

def _posicion(simbolo: Simbolo) -> str:
    p = simbolo.posicion
    return f"{p.linea}:{p.columna}" if p else "-"


def _simbolo(simbolo: Simbolo) -> str:
    return (f"{simbolo.nombre}: {simbolo.categoria.value} "
            f"{simbolo.describir_tipo()} ({_posicion(simbolo)})")


def formatear_cambio(cambio: Cambio) -> str:
    """Texto de un cambio, sin numero ni sangria."""
    ambito = cambio.ambito
    if cambio.tipo == TipoCambio.ENTRAR:
        detalle = ambito.describir()
    elif cambio.tipo == TipoCambio.REGISTRAR:
        detalle = f"{_simbolo(cambio.simbolo)} en ambito {ambito.numero}"
    elif cambio.tipo == TipoCambio.CONFLICTO:
        existente = cambio.existente
        detalle = (f"{_simbolo(cambio.simbolo)} ya declarado en "
                   f"{_posicion(existente)} como "
                   f"{existente.categoria.value}")
    else:
        nombres = ", ".join(s.nombre for s in cambio.contenido)
        detalle = f"Ambito {ambito.numero}: {nombres or '(vacio)'}"
    return f"{cambio.tipo.value.ljust(9)}  {detalle}"


def imprimir_cambio_parcial(
    tabla: TablaSimbolos,
    cambio: Cambio,
    salida: TextIO | None = None,
) -> None:
    """Imprime el estado visible justo despues de cada cambio."""
    salida = salida or sys.stdout
    salida.write(f"{len(tabla.cambios)}  {formatear_cambio(cambio)}\n")
    salida.write("    Estado parcial:\n")
    ambitos = []
    ambito = tabla.actual
    while ambito is not None:
        ambitos.append(ambito)
        ambito = ambito.padre
    for ambito in reversed(ambitos):
        simbolos = "; ".join(
            _simbolo(simbolo) for simbolo in ambito.simbolos.values()
        ) or "(vacio)"
        salida.write(f"    {ambito.describir()}: {simbolos}\n")
