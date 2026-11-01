"""
Adapta la salida real del Scanner sin reescanear ni convertir sus
lexemas.
"""

from dataclasses import dataclass
from typing import Sequence, Tuple

from scanner import ErrorLexico, Scanner, Token, TokenType


class EntradaConErroresLexicos(ValueError):
    """
    El parser no debe aceptar como limpio un texto con tokens
    descartados.
    """


@dataclass(frozen=True)
class EntradaParser:
    tokens: Tuple[Token, ...]
    errores_lexicos: Tuple[ErrorLexico, ...]

    @property
    def apta(self) -> bool:
        return not self.errores_lexicos

    def tokens_para_parser(self) -> Tuple[Token, ...]:
        if not self.apta:
            raise EntradaConErroresLexicos(
                (
                    "Hay errores lexicos: mostrar errores_lexicos antes de "
                    "invocar el parser."
                )
            )
        return self.tokens


def explorar_para_parser(fuente: str) -> EntradaParser:
    """Retorna tokens originales + un unico FIN_ARCHIVO y errores originales.

    Acepta un BOM inicial igual que el lector UTF-8-sig de main.py. No elimina
    BOM interiores ni normaliza saltos de linea. No interpreta literales.
    """
    if fuente.startswith("\ufeff"):
        fuente = fuente[1:]
    scanner = Scanner(fuente)
    tokens, errores = scanner.escanear()
    fin = Token(TokenType.FIN_ARCHIVO, "", scanner.linea, scanner.columna)
    return EntradaParser(tuple(tokens) + (fin,), tuple(errores))


class FlujoTokens:
    """Cursor con anticipacion y EOF estable; no implementa recuperacion."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        self._tokens = tuple(tokens)
        if (
            not self._tokens
            or self._tokens[-1].tipo is not TokenType.FIN_ARCHIVO
        ):
            raise ValueError("La secuencia debe terminar con FIN_ARCHIVO.")
        if any(t.tipo is TokenType.FIN_ARCHIVO for t in self._tokens[:-1]):
            raise ValueError(
                "FIN_ARCHIVO solo puede aparecer una vez, al final."
            )
        self._indice = 0

    @property
    def indice(self) -> int:
        return self._indice

    @property
    def en_fin(self) -> bool:
        return self.mirar().tipo is TokenType.FIN_ARCHIVO

    def mirar(self, adelanto: int = 0) -> Token:
        if adelanto < 0:
            raise ValueError("El adelanto no puede ser negativo.")
        return self._tokens[
            min(self._indice + adelanto, len(self._tokens) - 1)
        ]

    def avanzar(self) -> Token:
        actual = self.mirar()
        if not self.en_fin:
            self._indice += 1
        return actual
