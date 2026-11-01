"""Identifica los errores lexicos con su posicion en el archivo fuente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorLexico:
    mensaje: str
    lexema: str
    linea: int
    columna: int

    def __str__(self) -> str:
        return (
            f'Error lexico: {self.mensaje} "{self.lexema}" '
            f"[linea {self.linea}, columna {self.columna}]"
        )
