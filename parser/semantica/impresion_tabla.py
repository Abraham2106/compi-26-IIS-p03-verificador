"""Impresion de los cambios de la tabla de simbolos (1.4.1).

La tabla anota cada operacion en `tabla.cambios` mientras el verificador
recorre el ASA. Este modulo los convierte en texto, uno por linea y con
sangria segun el nivel del ambito:

     1  registrar  limite: variable global grano (2:1) en ambito 0
     2  entrar     Ambito 1 (nivel 1, dentro de 0)
     3    registrar  a: parametro grano (4:15) en ambito 1
     4    conflicto  a: parametro grano (4:24) ya declarado en 4:15 como
                     parametro
     5  salir      Ambito 1: a

Los tipos se muestran al imprimir, no al registrar: si se imprime despues de
verificar_semantica, las funciones ya muestran su tipo de retorno inferido.
"""

import sys
from typing import TextIO

from parser.semantica.tabla_simbolos import (
    Cambio, Simbolo, TablaSimbolos, TipoCambio,
)

SANGRIA = "  "


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


def _profundidad(cambio: Cambio) -> int:
    # Entrar y salir se escriben al nivel del ambito que los contiene.
    if cambio.tipo in (TipoCambio.ENTRAR, TipoCambio.SALIR):
        return cambio.ambito.nivel - 1
    return cambio.ambito.nivel


def lineas_cambios(tabla: TablaSimbolos) -> list[str]:
    ancho = len(str(len(tabla.cambios)))
    return [
        f"{str(i).rjust(ancho)}  {SANGRIA * _profundidad(cambio)}"
        f"{formatear_cambio(cambio)}"
        for i, cambio in enumerate(tabla.cambios, 1)
    ]


def cambios_a_texto(tabla: TablaSimbolos) -> str:
    lineas = lineas_cambios(tabla) or ["(sin cambios)"]
    return "\n".join(lineas) + "\n"


def imprimir_cambios(tabla: TablaSimbolos,
                     salida: TextIO | None = None) -> None:
    """Imprime el historial de cambios y la tabla final."""
    salida = salida or sys.stdout
    salida.write("Cambios de la tabla de simbolos\n")
    salida.write(cambios_a_texto(tabla))
    salida.write("\nTabla de simbolos final\n")
    salida.write(tabla.a_texto())
