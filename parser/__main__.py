"""Ejecuta el parser: python -m parser programa.qc."""

import argparse
import sys
from pathlib import Path

from parser.analizador import Analizador
from parser.asa_impresion import imprimir_preorden
from parser.integracion import explorar_para_parser


def main():
    argumentos = argparse.ArgumentParser(
        description="Parser de Quantum Coffee"
    )
    argumentos.add_argument("archivo", type=Path)
    ruta = argumentos.parse_args().archivo
    try:
        fuente = ruta.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        argumentos.error(str(error))
    entrada = explorar_para_parser(fuente)
    if not entrada.apta:
        for error in entrada.errores_lexicos:
            print(error, file=sys.stderr)
        return 1
    resultado = Analizador().analizar(entrada.tokens_para_parser())
    for error in resultado.errores:
        token = error.encontrado
        print(
            f"{ruta}:{token.linea}:{token.columna}: {error.mensaje}",
            file=sys.stderr,
        )
    if not resultado.correcto:
        return 1
    imprimir_preorden(resultado.arbol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
