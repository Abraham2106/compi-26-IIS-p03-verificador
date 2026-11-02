"""Producciones de expresiones de Quantum Coffee (tarea 3.2).

Cada metodo corresponde a una produccion de la seccion 5 de la EBNF y
devuelve un NodoASA. Los operadores binarios se acumulan hacia la izquierda;
los prefijos (`Amargo`, `+`, `-`) se construyen de derecha a izquierda.
Las producciones auxiliares no crean nodos propios.
"""

from typing import NoReturn

from parser.asa_constructores import (
    agrupar,
    crear_binaria,
    crear_identificador,
    crear_literal,
    crear_lista,
    crear_llamada,
    crear_operacion_lista,
    crear_unaria,
)
from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import ErrorSintactico, NodoASA
from parser.producciones_cuanticas import ProduccionesCuanticas
from scanner import Token, TokenType

OPERADORES_RELACIONALES = (
    TokenType.IGUALDAD,
    TokenType.DIFERENTE,
    TokenType.MENOR,
    TokenType.MENOR_IGUAL,
    TokenType.MAYOR,
    TokenType.MAYOR_IGUAL,
)

TIPOS_LITERAL = (
    TokenType.ENTERO,
    TokenType.DECIMAL,
    TokenType.CADENA,
    TokenType.FUERTE,
    TokenType.RALO,
    TokenType.DESCAFEINADO,
    TokenType.SE_QUEMO_EL_CAFE,
)

METODOS_LISTA = (TokenType.INSERTAR, TokenType.EXTRAER, TokenType.BUSCAR)

# Tokens con los que puede comenzar una expresion (FIRST de `expresion`).
INICIO_EXPRESION = TIPOS_LITERAL + (
    TokenType.CORCHETE_ABRE,
    TokenType.IDENTIFICADOR,
    TokenType.MEDIR,
    TokenType.PARENTESIS_ABRE,
    TokenType.AMARGO,
    TokenType.SUMA,
    TokenType.RESTA,
)


def fallar(
    control: ControlSintactico,
    mensaje: str,
    encontrado: Token,
    esperados: tuple[TokenType, ...] = (),
) -> NoReturn:
    """Registra un error sintactico propio y lo lanza como `esperar`."""
    error = ErrorSintactico(mensaje, encontrado, tuple(esperados))
    control.errores.append(error)
    raise FalloSintactico(error)


class ProduccionesExpresiones:
    """Analiza expresiones aritmeticas, relacionales y logicas."""

    def __init__(
        self,
        control: ControlSintactico,
        cuanticas: ProduccionesCuanticas,
    ) -> None:
        self.control = control
        self.cuanticas = cuanticas

    def _tipo_actual(self) -> TokenType:
        return self.control.flujo.mirar().tipo

    # niveles de precedencia (menor a mayor)

    def expresion(self) -> NodoASA:
        return self.expresion_or()

    def expresion_or(self) -> NodoASA:
        nodo = self.expresion_and()
        while self._tipo_actual() == TokenType.SIN_AZUCAR:
            operador = self.control.flujo.avanzar()
            nodo = crear_binaria(nodo, operador, self.expresion_and())
        return nodo

    def expresion_and(self) -> NodoASA:
        nodo = self.expresion_not()
        while self._tipo_actual() == TokenType.CON_AZUCAR:
            operador = self.control.flujo.avanzar()
            nodo = crear_binaria(nodo, operador, self.expresion_not())
        return nodo

    def expresion_not(self) -> NodoASA:
        operadores: list[Token] = []
        while self._tipo_actual() == TokenType.AMARGO:
            operadores.append(self.control.flujo.avanzar())
        nodo = self.expresion_relacional()
        # `Amargo Amargo x` = Amargo(Amargo(x)): el mas cercano primero.
        for operador in reversed(operadores):
            nodo = crear_unaria(operador, nodo)
        return nodo

    def expresion_relacional(self) -> NodoASA:
        nodo = self.expresion_aritmetica()
        if self._tipo_actual() in OPERADORES_RELACIONALES:
            operador = self.control.flujo.avanzar()
            nodo = crear_binaria(nodo, operador, self.expresion_aritmetica())
            siguiente = self.control.flujo.mirar()
            if siguiente.tipo in OPERADORES_RELACIONALES:
                fallar(
                    self.control,
                    "No se admiten comparaciones encadenadas; use "
                    "'a < b ConAzucar b < c'",
                    siguiente,
                )
        return nodo

    def expresion_aritmetica(self) -> NodoASA:
        nodo = self.termino()
        while self._tipo_actual() in (TokenType.SUMA, TokenType.RESTA):
            operador = self.control.flujo.avanzar()
            nodo = crear_binaria(nodo, operador, self.termino())
        return nodo

    def termino(self) -> NodoASA:
        nodo = self.unario()
        while self._tipo_actual() in (
            TokenType.MULTIPLICACION,
            TokenType.DIVISION,
            TokenType.MODULO,
        ):
            operador = self.control.flujo.avanzar()
            nodo = crear_binaria(nodo, operador, self.unario())
        return nodo

    def unario(self) -> NodoASA:
        signos: list[Token] = []
        while self._tipo_actual() in (TokenType.SUMA, TokenType.RESTA):
            signos.append(self.control.flujo.avanzar())
        nodo = self.factor()
        for signo in reversed(signos):
            nodo = crear_unaria(signo, nodo)
        return nodo

    # factores

    def factor(self) -> NodoASA:
        tipo = self._tipo_actual()

        if tipo in TIPOS_LITERAL:
            return crear_literal(self.control.flujo.avanzar())
        if tipo == TokenType.CORCHETE_ABRE:
            return self.arreglo()
        if tipo == TokenType.IDENTIFICADOR:
            return self.factor_identificador()
        if tipo == TokenType.MEDIR:
            return self.cuanticas.medicion()
        if tipo == TokenType.PARENTESIS_ABRE:
            abre = self.control.flujo.avanzar()
            interno = self.expresion()
            cierra = self.control.esperar(
                TokenType.PARENTESIS_CIERRA,
                contexto="expresion entre parentesis",
            )
            return agrupar(interno, abre, cierra)

        # Token que no inicia ninguna expresion.
        self.control.esperar(*INICIO_EXPRESION, contexto="expresion")
        raise AssertionError("esperar debia fallar")

    def _argumentos(self, cierre: TokenType) -> list[NodoASA]:
        argumentos = []
        if self._tipo_actual() != cierre:
            argumentos.append(self.expresion())
            while self._tipo_actual() == TokenType.COMA:
                self.control.flujo.avanzar()
                argumentos.append(self.expresion())
        return argumentos

    def arreglo(self) -> NodoASA:
        abre = self.control.esperar(
            TokenType.CORCHETE_ABRE, contexto="arreglo"
        )
        elementos = self._argumentos(TokenType.CORCHETE_CIERRA)
        cierra = self.control.esperar(
            TokenType.CORCHETE_CIERRA,
            TokenType.COMA,
            contexto="arreglo",
        )
        return crear_lista(abre, elementos, cierra)

    def factor_identificador(self) -> NodoASA:
        """identificador [ sufijo_llamada | sufijo_lista ]"""
        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="expresion"
        )
        siguiente = self._tipo_actual()
        if siguiente == TokenType.PARENTESIS_ABRE:
            return self.llamada(nombre)
        if siguiente == TokenType.PUNTO:
            return self.operacion_lista(nombre)
        return crear_identificador(nombre)

    def llamada(self, nombre: Token) -> NodoASA:
        """sufijo_llamada ::= "(" [ argumentos ] ")" (ya leido el nombre)."""
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="llamada a funcion"
        )
        argumentos = self._argumentos(TokenType.PARENTESIS_CIERRA)
        cierra = self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            TokenType.COMA,
            contexto="argumentos de llamada",
        )
        return crear_llamada(nombre, argumentos, cierra)

    def operacion_lista(self, receptor: Token) -> NodoASA:
        """sufijo_lista ::= "." metodo_lista "(" expresion ")"."""
        self.control.esperar(TokenType.PUNTO, contexto="metodo de lista")
        metodo = self.control.esperar(
            *METODOS_LISTA, contexto="metodo de lista"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="metodo de lista"
        )
        argumento = self.expresion()
        cierra = self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="metodo de lista"
        )
        return crear_operacion_lista(receptor, metodo, argumento, cierra)
