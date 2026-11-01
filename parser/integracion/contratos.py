"""Interfaz propuesta para parser y ASA. No contiene un analizador sintactico.

Los nodos representan estructura y lexemas; no contienen tipos inferidos,
resultados de evaluacion, simbolos resueltos ni instrucciones generadas.
"""

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional, Protocol, Sequence, Tuple

from scanner import Token, TokenType


@dataclass(frozen=True, order=True)
class Posicion:
    linea: int
    columna: int

    def __post_init__(self) -> None:
        if self.linea < 1 or self.columna < 1:
            raise ValueError("Las posiciones comienzan en 1.")


@dataclass(frozen=True)
class RangoFuente:
    inicio: Posicion
    fin: Posicion  # Exclusivo: primera posicion posterior al fragmento.

    def __post_init__(self) -> None:
        if self.fin < self.inicio:
            raise ValueError("El fin no puede estar antes del inicio.")

    @classmethod
    def de_token(cls, token: Token) -> "RangoFuente":
        # Todo token valido actual ocupa una sola linea; EOF tiene ancho cero.
        return cls(
            Posicion(token.linea, token.columna),
            Posicion(token.linea, token.columna + len(token.lexema)),
        )


class ClaseNodo(str, Enum):
    PROGRAMA = "Programa"
    GLOBAL = "DeclaracionGlobal"
    FUNCION = "Funcion"
    PRINCIPAL = "FuncionPrincipal"
    PARAMETRO = "Parametro"
    BLOQUE = "Bloque"
    LOCAL = "DeclaracionLocal"
    ASIGNACION = "Asignacion"
    LLAMADA = "Llamada"
    OPERACION_LISTA = "OperacionLista"
    CONDICIONAL = "Condicional"
    MIENTRAS = "Mientras"
    PARA_CADA = "ParaCada"
    RETORNO = "Retorno"
    QUBIT = "DeclaracionQubit"
    COMPUERTA = "Compuerta"
    MEDICION = "Medicion"
    BINARIA = "Binaria"
    UNARIA = "Unaria"
    IDENTIFICADOR = "Identificador"
    LITERAL = "Literal"
    LISTA = "Lista"


@dataclass(frozen=True)
class NodoASA:
    clase: ClaseNodo
    rango: RangoFuente
    atributos: Mapping[str, str] = field(default_factory=dict)
    hijos: Tuple["NodoASA", ...] = ()

    def __post_init__(self) -> None:
        # Copias defensivas: el renderer no debe modificar el arbol del parser.
        if not isinstance(self.clase, ClaseNodo):
            raise TypeError("clase debe pertenecer a ClaseNodo.")
        if any(
            not isinstance(k, str) or not isinstance(v, str)
            for k, v in self.atributos.items()
        ):
            raise TypeError(
                "Los atributos conservan texto, no valores evaluados."
            )
        object.__setattr__(
            self, "atributos", MappingProxyType(dict(self.atributos))
        )
        object.__setattr__(self, "hijos", tuple(self.hijos))

    def a_dict(self) -> dict:
        """Estructura serializable con json.dumps(..., ensure_ascii=False)."""
        return {
            "clase": self.clase.value,
            "rango": {
                "inicio": {
                    "linea": self.rango.inicio.linea,
                    "columna": self.rango.inicio.columna,
                },
                "fin": {
                    "linea": self.rango.fin.linea,
                    "columna": self.rango.fin.columna,
                },
            },
            "atributos": dict(self.atributos),
            "hijos": [hijo.a_dict() for hijo in self.hijos],
        }


@dataclass(frozen=True)
class ErrorSintactico:
    mensaje: str
    encontrado: Token
    esperados: Tuple[TokenType, ...] = ()


@dataclass(frozen=True)
class ResultadoParseo:
    arbol: Optional[NodoASA]
    errores: Tuple[ErrorSintactico, ...] = ()

    @property
    def correcto(self) -> bool:
        return self.arbol is not None and not self.errores


class AnalizadorSintactico(Protocol):
    def analizar(self, tokens: Sequence[Token]) -> ResultadoParseo:
        """Consume una secuencia limpia con un unico FIN_ARCHIVO final.

        Debe consumir el programa completo. Un arbol parcial con errores no
        representa aceptacion; en ese caso ResultadoParseo.correcto es False.
        """
        ...
