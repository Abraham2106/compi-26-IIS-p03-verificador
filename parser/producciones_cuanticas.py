"""Producciones de la extension cuantica de Quantum Coffee."""

from parser.asa_constructores import crear_identificador, rango_entre
from parser.errores_sintacticos import ControlSintactico
from parser.integracion import ClaseNodo, NodoASA
from scanner import TokenType


class ProduccionesCuanticas:
    """Reconoce las construcciones cuanticas del lenguaje."""

    def __init__(self, control: ControlSintactico) -> None:
        self.control = control

    def declaracion_qubit(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.QUBIT, contexto="declaracion de qubit"
        )
        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="nombre del qubit"
        )
        fin = self.control.esperar(
            TokenType.PUNTO_COMA, contexto="declaracion de qubit"
        )
        rango = rango_entre(inicio, fin)
        return NodoASA(
            clase=ClaseNodo.QUBIT,
            rango=rango,
            atributos={"nombre": nombre.lexema},
        )

    def compuerta_unaria(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.COMPUERTA_H,
            TokenType.COMPUERTA_X,
            TokenType.COMPUERTA_Z,
            contexto="compuerta unaria",
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="compuerta unaria"
        )
        objetivo = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="qubit de compuerta unaria"
        )
        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="compuerta unaria"
        )
        nodo_objetivo = crear_identificador(objetivo)
        rango = rango_entre(inicio, fin)
        return NodoASA(
            clase=ClaseNodo.COMPUERTA,
            rango=rango,
            atributos={"compuerta": inicio.lexema},
            hijos=(nodo_objetivo,),
        )

    def compuerta_binaria(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.CNOT, contexto="compuerta binaria"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="compuerta CNOT"
        )
        primer_qubit = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="primer qubit de CNOT"
        )
        self.control.esperar(TokenType.COMA, contexto="compuerta CNOT")
        segundo_qubit = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="segundo qubit de CNOT"
        )
        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="compuerta CNOT"
        )
        nodo_primero = crear_identificador(primer_qubit)
        nodo_segundo = crear_identificador(segundo_qubit)
        rango = rango_entre(inicio, fin)
        return NodoASA(
            clase=ClaseNodo.COMPUERTA,
            rango=rango,
            atributos={"compuerta": inicio.lexema},
            hijos=(nodo_primero, nodo_segundo),
        )

    def medicion(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.MEDIR, contexto="medicion cuantica"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="medicion cuantica"
        )
        qubit = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="qubit de medicion"
        )
        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="medicion cuantica"
        )
        nodo_qubit = crear_identificador(qubit)
        rango = rango_entre(inicio, fin)
        return NodoASA(
            clase=ClaseNodo.MEDICION, rango=rango, hijos=(nodo_qubit,)
        )

    def sentencia_cuantica(self) -> NodoASA:
        tipo = self.control.flujo.mirar().tipo
        if tipo == TokenType.QUBIT:
            return self.declaracion_qubit()
        if tipo in (
            TokenType.COMPUERTA_H,
            TokenType.COMPUERTA_X,
            TokenType.COMPUERTA_Z,
        ):
            nodo = self.compuerta_unaria()
        elif tipo == TokenType.CNOT:
            nodo = self.compuerta_binaria()
        elif tipo == TokenType.MEDIR:
            nodo = self.medicion()
        else:
            self.control.esperar(
                TokenType.QUBIT,
                TokenType.COMPUERTA_H,
                TokenType.COMPUERTA_X,
                TokenType.COMPUERTA_Z,
                TokenType.CNOT,
                TokenType.MEDIR,
                contexto="sentencia cuantica",
            )
            raise AssertionError("Token inesperado")
        self.control.esperar(
            TokenType.PUNTO_COMA, contexto="sentencia cuantica"
        )
        return nodo
