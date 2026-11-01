"""Declaraciones, asignaciones y retornos de Quantum Coffee."""

from parser.asa_constructores import (
    como_sentencia,
    crear_asignacion,
    crear_declaracion,
    crear_retorno,
)
from parser.errores_sintacticos import ControlSintactico
from parser.integracion import ClaseNodo, NodoASA
from parser.producciones_expresiones import (
    INICIO_EXPRESION,
    ProduccionesExpresiones,
)
from scanner import TokenType

TIPOS_BASE = (
    TokenType.GRANO,
    TokenType.POSO,
    TokenType.GRANO_MOLIDO,
    TokenType.CAFE,
)

INICIO_TIPO = TIPOS_BASE + (TokenType.TAZA,)


class ProduccionesDeclaraciones:
    """Reconoce tipos, variables, asignaciones, llamadas y retornos."""

    def __init__(
        self, control: ControlSintactico, expresiones: ProduccionesExpresiones
    ) -> None:
        self.control = control
        self.expresiones = expresiones

    def tipo(self) -> str:
        """tipo ::= base | "taza" tipo. Devuelve el texto escrito."""
        token = self.control.esperar(*INICIO_TIPO, contexto="tipo")
        if token.tipo == TokenType.TAZA:
            return f"{token.lexema} {self.tipo()}"
        return token.lexema

    def _inicializador_opcional(self) -> NodoASA | None:
        if self.control.flujo.mirar().tipo != TokenType.ASIGNACION:
            return None
        self.control.flujo.avanzar()
        return self.expresiones.expresion()

    def _declaracion(self, clase: ClaseNodo, contexto: str) -> NodoASA:
        inicio = self.control.flujo.mirar()
        if clase == ClaseNodo.GLOBAL:
            self.control.esperar(TokenType.CAFETERIA, contexto=contexto)
        tipo = self.tipo()
        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto=f"nombre en {contexto}"
        )
        inicial = self._inicializador_opcional()
        # Sin inicializador, el mensaje de error sugiere ";" o "=".
        esperados = (TokenType.PUNTO_COMA,)
        if inicial is None:
            esperados += (TokenType.ASIGNACION,)
        punto_coma = self.control.esperar(*esperados, contexto=contexto)
        return crear_declaracion(
            clase, tipo, nombre, inicial, inicio, punto_coma
        )

    def declaracion_global(self) -> NodoASA:
        """declaracion_global ::= "cafeteria" tipo id [ "=" expr ] ";"."""
        return self._declaracion(ClaseNodo.GLOBAL, "declaracion global")

    def declaracion_local(self) -> NodoASA:
        """declaracion_var_local ::= tipo id [ "=" expr ] ";"."""
        return self._declaracion(ClaseNodo.LOCAL, "declaracion de variable")

    def sentencia_identificador(self) -> NodoASA:
        """identificador ( "=" expr | llamada | metodo_lista ) ";"."""
        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="sentencia"
        )
        siguiente = self.control.flujo.mirar().tipo

        if siguiente == TokenType.ASIGNACION:
            self.control.flujo.avanzar()
            valor = self.expresiones.expresion()
            punto_coma = self.control.esperar(
                TokenType.PUNTO_COMA, contexto="asignacion"
            )
            return crear_asignacion(nombre, valor, punto_coma)

        if siguiente == TokenType.PARENTESIS_ABRE:
            expresion = self.expresiones.llamada(nombre)
        elif siguiente == TokenType.PUNTO:
            expresion = self.expresiones.operacion_lista(nombre)
        else:
            self.control.esperar(
                TokenType.ASIGNACION,
                TokenType.PARENTESIS_ABRE,
                TokenType.PUNTO,
                contexto=f"sentencia que inicia con {nombre.lexema!r}",
            )
            raise AssertionError("esperar debia fallar")

        punto_coma = self.control.esperar(
            TokenType.PUNTO_COMA, contexto="sentencia"
        )
        return como_sentencia(expresion, punto_coma)

    def retorno(self) -> NodoASA:
        """retorno_degustar ::= "degustar" [ expresion ] ";"."""
        degustar = self.control.esperar(TokenType.DEGUSTAR, contexto="retorno")
        valor = None
        if self.control.flujo.mirar().tipo in INICIO_EXPRESION:
            valor = self.expresiones.expresion()
        punto_coma = self.control.esperar(
            TokenType.PUNTO_COMA, contexto="retorno"
        )
        return crear_retorno(degustar, valor, punto_coma)
