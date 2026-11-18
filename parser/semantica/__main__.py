"""Verificador semantico: python -m parser.semantica programa.qc.

Retorna 0 si el programa es correcto y 1 si hay errores lexicos,
sintacticos o semanticos.
"""

import argparse
import sys
from pathlib import Path

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.analisis import verificar_semantica
from parser.semantica.errores_semanticos import reportar


def main():
    argumentos = argparse.ArgumentParser(
        description="Verificador semantico de Quantum Coffee"
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
    errores = verificar_semantica(resultado.arbol)
    if reportar(errores, str(ruta), fuente):
        return 1
    print(f"{ruta}: verificacion semantica correcta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
