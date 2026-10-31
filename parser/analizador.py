"""Nucleo del analizador sintactico de Quantum Coffee.

NO importa las producciones de bloques, estructuras de control,
funciones, `chorreador` y extension cuantica. Esas se enganchan desde fuera
con `registrar_*`. Ejemplo:

    def conectar(analisis):
        control = ProduccionesControl(
            analisis.control, analisis.sentencia,
            analisis.expresion, analisis.tipo)
        analisis.registrar_sentencia(TokenType.HIERVE, control.condicional)
        analisis.registrar_funcion(control.funcion)
        analisis.registrar_principal(control.chorreador)

    resultado = Analizador(conectar).analizar(tokens)
"""

from collections.abc import Callable, Iterable, Sequence
from typing import NoReturn

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
from scanner import Token, TokenType

INICIO_CUANTICA = (
    TokenType.QUBIT,
    TokenType.COMPUERTA_H,
    TokenType.COMPUERTA_X,
    TokenType.COMPUERTA_Z,
    TokenType.CNOT,
    TokenType.MEDIR,
)

INICIO_SENTENCIA = INICIO_TIPO + INICIO_CUANTICA + (
    TokenType.IDENTIFICADOR,
    TokenType.HIERVE,
    TokenType.CHORREANDO,
    TokenType.RECOLAR,
    TokenType.DEGUSTAR,
)

INICIO_DECLARACION = (TokenType.CAFETERIA, TokenType.BARISTA)


# Construcciones que el nucleo reconoce pero cuya produccion es de la 4.0.
INICIO_EXTERNAS = INICIO_CUANTICA + (
    TokenType.HIERVE,
    TokenType.CHORREANDO,
    TokenType.RECOLAR,
)

Conexion = Callable[["Analisis"], None]
Produccion = Callable[[], NodoASA]


class Analizador:
    """Valida la estructura de un programa y construye su ASA.

    `conectar` recibe el `Analisis` de cada corrida y registra en el las
    producciones de la tarea 4.0. Con errores, `ResultadoParseo.correcto`
    siempre es falso.
    """

    def __init__(self, conectar: Conexion | None = None) -> None:
        self.conectar = conectar

    def analizar(self, tokens: Sequence[Token]) -> ResultadoParseo:
        analisis = Analisis(tokens)
        if self.conectar is not None:
            self.conectar(analisis)
        return analisis.ejecutar()


class Analisis:
    """Estado de una sola corrida: cursor, errores y producciones."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        self.control = ControlSintactico(FlujoTokens(tokens))
        self.flujo = self.control.flujo
        self.expresiones = ProduccionesExpresiones(
            self.control, self._medicion
        )
        self.declaraciones = ProduccionesDeclaraciones(
            self.control, self.expresiones
        )
        self._sentencias: dict[TokenType, Produccion] = {}
        self._funcion: Produccion | None = None
        self._principal: Produccion | None = None
        self._medicion_externa: Produccion | None = None

    # puntos de enganche para la tarea 4.0 (actividad 4.4)

    def registrar_sentencia(self, tipos: TokenType | Iterable[TokenType],
                            produccion: Produccion) -> None:
        """Produccion completa de una sentencia que inicia con `tipos`."""
        if isinstance(tipos, TokenType):
            tipos = (tipos,)
        for tipo in tipos:
            self._sentencias[tipo] = produccion

    def registrar_funcion(self, produccion: Produccion) -> None:
        """`barista nombre(...) bloque`, con el cursor en `barista`."""
        self._funcion = produccion

    def registrar_principal(self, produccion: Produccion) -> None:
        """`barista chorreador() bloque`, con el cursor en `barista`."""
        self._principal = produccion

    def registrar_medicion(self, produccion: Produccion) -> None:
        """`medir(q)` usado dentro de una expresion."""
        self._medicion_externa = produccion

    # acceso para las producciones externas

    def expresion(self) -> NodoASA:
        return self.expresiones.expresion()

    def tipo(self) -> str:
        return self.declaraciones.tipo()

    # sentencias

    def _no_conectada(self, nombre: str) -> NoReturn:
        fallar(
            self.control,
            f"La construccion '{nombre}' aun no esta conectada al nucleo "
            "(actividad 4.4)",
            self.flujo.mirar(),
        )

    def _medicion(self) -> NodoASA:
        if self._medicion_externa is None:
            self._no_conectada("medir")
        return self._medicion_externa()

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
        if tipo in self._sentencias:
            return self._sentencias[tipo]()
        if tipo in INICIO_EXTERNAS:
            self._no_conectada(token.lexema)

        self.control.esperar(*INICIO_SENTENCIA, contexto="sentencia")
        raise AssertionError("esperar debia fallar")

    # programa

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
                if self._funcion is None:
                    self._no_conectada("barista")
                return self._funcion()
            fallar(
                self.control,
                "Despues de 'barista' se esperaba el nombre de la funcion "
                f"o 'chorreador', pero se encontro {siguiente.lexema!r}"
                if siguiente.tipo != TokenType.FIN_ARCHIVO else
                "Despues de 'barista' se esperaba el nombre de la funcion "
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
            self.flujo.avanzar()  # garantiza progreso
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
                    break  # sin chorreador: ya se informo
                self._sincronizar_declaracion(indice)
                continue
            if nodo is None:
                break
            declaraciones.append(nodo)

        if self.flujo.mirar().tipo != TokenType.BARISTA:
            return None

        try:
            if self._principal is None:
                self._no_conectada("chorreador")
            principal = self._principal()
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

    def ejecutar(self) -> ResultadoParseo:
        arbol = self.programa()
        return ResultadoParseo(arbol, tuple(self.control.errores))
