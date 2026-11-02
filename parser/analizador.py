"""Analizador descendente con las producciones completas de Quantum Coffee."""

from collections.abc import Sequence

from parser.asa_constructores import crear_programa
from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import FlujoTokens, NodoASA, ResultadoParseo
from parser.producciones_declaraciones import (
    INICIO_TIPO,
    ProduccionesDeclaraciones,
)
from parser.producciones_expresiones import (
    ProduccionesExpresiones,
    fallar,
)
from parser.producciones_control import ProduccionesControl
from parser.producciones_cuanticas import ProduccionesCuanticas
from scanner import Token, TokenType

INICIO_CUANTICA = (
    TokenType.QUBIT,
    TokenType.COMPUERTA_H,
    TokenType.COMPUERTA_X,
    TokenType.COMPUERTA_Z,
    TokenType.CNOT,
    TokenType.MEDIR,
)

INICIO_SENTENCIA = (
    INICIO_TIPO
    + INICIO_CUANTICA
    + (
        TokenType.IDENTIFICADOR,
        TokenType.HIERVE,
        TokenType.CHORREANDO,
        TokenType.RECOLAR,
        TokenType.DEGUSTAR,
    )
)

INICIO_DECLARACION = (TokenType.CAFETERIA, TokenType.BARISTA)


class Analizador:
    def analizar(self, tokens: Sequence[Token]) -> ResultadoParseo:
        self.control = ControlSintactico(FlujoTokens(tokens))
        self.flujo = self.control.flujo
        self.cuanticas = ProduccionesCuanticas(self.control)
        self.expresiones = ProduccionesExpresiones(
            self.control, self.cuanticas
        )
        self.declaraciones = ProduccionesDeclaraciones(
            self.control, self.expresiones
        )
        self.estructuras = ProduccionesControl(self)
        arbol = self.programa()
        return ResultadoParseo(arbol, tuple(self.control.errores))

    def sentencia(self) -> NodoASA:
        """Elige la produccion de `sentencia` con el token actual."""
        token = self.flujo.mirar()
        tipo = token.tipo

        if tipo in INICIO_TIPO:
            return self.declaraciones.declaracion_local()
        if tipo == TokenType.IDENTIFICADOR:
            return self.declaraciones.sentencia_identificador()
        if tipo == TokenType.DEGUSTAR:
            return self.declaraciones.retorno()
        if tipo == TokenType.HIERVE:
            return self.estructuras.condicional()
        if tipo == TokenType.CHORREANDO:
            return self.estructuras.chorreando()
        if tipo == TokenType.RECOLAR:
            return self.estructuras.recolar()
        if tipo in INICIO_CUANTICA:
            return self.cuanticas.sentencia_cuantica()

        self.control.esperar(*INICIO_SENTENCIA, contexto="sentencia")
        raise AssertionError("esperar debia fallar")


    def _declaracion_de_programa(self) -> NodoASA | None:
        """Una global o funcion; None cuando llega `barista chorreador`."""
        actual = self.flujo.mirar()

        if actual.tipo == TokenType.CAFETERIA:
            return self.declaraciones.declaracion_global()

        if actual.tipo == TokenType.BARISTA:
            siguiente = self.flujo.mirar(1)
            if siguiente.tipo == TokenType.CHORREADOR:
                return None
            if siguiente.tipo == TokenType.IDENTIFICADOR:
                return self.estructuras.funcion()
            fallar(
                self.control,
                "Despues de 'barista' se esperaba el nombre de la funcion "
                f"o 'chorreador', pero se encontro {siguiente.lexema!r}"
                if siguiente.tipo != TokenType.FIN_ARCHIVO
                else "Despues de 'barista' se esperaba el nombre "
                "de la funcion "
                "o 'chorreador', pero se encontro fin de archivo",
                siguiente,
                (TokenType.IDENTIFICADOR, TokenType.CHORREADOR),
            )

        if actual.tipo == TokenType.FIN_ARCHIVO:
            fallar(
                self.control,
                "Falta la funcion principal 'barista chorreador()' "
                "al final del programa",
                actual,
                INICIO_DECLARACION,
            )

        self.control.esperar(*INICIO_DECLARACION, contexto="programa")
        raise AssertionError("esperar debia fallar")

    def _sincronizar_declaracion(self, indice_inicial: int) -> None:
        """Salta hasta la siguiente declaracion de nivel superior."""
        if self.flujo.indice == indice_inicial:
            self.flujo.avanzar()
        while self.flujo.mirar().tipo not in (
            *INICIO_DECLARACION,
            TokenType.FIN_ARCHIVO,
        ):
            self.flujo.avanzar()

    def programa(self) -> NodoASA | None:
        declaraciones: list[NodoASA] = []

        while True:
            indice = self.flujo.indice
            try:
                nodo = self._declaracion_de_programa()
            except FalloSintactico:
                if self.flujo.en_fin:
                    break
                self._sincronizar_declaracion(indice)
                continue
            if nodo is None:
                break
            declaraciones.append(nodo)

        if self.flujo.mirar().tipo != TokenType.BARISTA:
            return None

        try:
            principal = self.estructuras.chorreador()
            if not self.flujo.en_fin:
                extra = self.flujo.mirar()
                fallar(
                    self.control,
                    "Despues de 'barista chorreador' no puede haber mas "
                    f"codigo; se encontro {extra.lexema!r}",
                    extra,
                    (TokenType.FIN_ARCHIVO,),
                )
        except FalloSintactico:
            return None

        return crear_programa(declaraciones, principal)
