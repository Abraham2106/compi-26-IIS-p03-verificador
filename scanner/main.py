"""Ejecuta el scanner desde la terminal con un archivo .qc."""

import sys
from pathlib import Path
from typing import List, Tuple

if __package__:
    from .errores import ErrorLexico
    from .scanner import Scanner
    from .tokens import Token
else:
    from errores import ErrorLexico
    from scanner import Scanner
    from tokens import Token

EXTENSION_FUENTE = ".qc"
CODIFICACION = "utf-8-sig"
COD_OK = 0
COD_ERRORES_LEXICOS = 1
COD_USO = 2


def explorar_archivo(ruta: Path) -> Tuple[List[Token], list[ErrorLexico]]:
    fuente = ruta.read_text(encoding=CODIFICACION)
    return Scanner(fuente).escanear()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Uso: python main.py <archivo.qc>")
        return COD_USO

    ruta = Path(argv[1])

    if ruta.suffix.lower() != EXTENSION_FUENTE:
        print("Error: el archivo fuente debe tener extension .qc")
        return COD_USO

    try:
        tokens, errores = explorar_archivo(ruta)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: no se pudo leer '{ruta}': {exc}")
        return COD_USO

    for token in tokens:
        print(token)

    for error in errores:
        print(error)

    return COD_ERRORES_LEXICOS if errores else COD_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
