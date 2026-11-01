"""
Contratos de entrada y salida para parser y ASA, sin implementar el
parser.
"""

from .entrada import EntradaParser, FlujoTokens, explorar_para_parser
from .contratos import (
    AnalizadorSintactico,
    ClaseNodo,
    ErrorSintactico,
    NodoASA,
    Posicion,
    RangoFuente,
    ResultadoParseo,
)

__all__ = [
    "EntradaParser",
    "FlujoTokens",
    "explorar_para_parser",
    "AnalizadorSintactico",
    "ClaseNodo",
    "ErrorSintactico",
    "NodoASA",
    "Posicion",
    "RangoFuente",
    "ResultadoParseo",
]
