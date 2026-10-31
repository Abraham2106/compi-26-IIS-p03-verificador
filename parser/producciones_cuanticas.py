"""Producciones de la extension cuantica de Quantum Coffee."""

from parser.errores_sintacticos import ControlSintactico
from parser.integracion import ClaseNodo, NodoASA, RangoFuente
from scanner import TokenType


class ProduccionesCuanticas:
    """Reconoce las construcciones cuanticas del lenguaje."""

    def __init__(self, control: ControlSintactico) -> None:
        self.control = control

    def declaracion_qubit(self) -> NodoASA:
        """Reconoce una declaracion de qubit y construye su ASA."""

        inicio = self.control.esperar(
            TokenType.QUBIT,
            contexto="declaracion de qubit",
        )

        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="nombre del qubit",
        )

        fin = self.control.esperar(
            TokenType.PUNTO_COMA,
            contexto="declaracion de qubit",
        )

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=RangoFuente.de_token(fin).fin,
        )

        return NodoASA(
            clase=ClaseNodo.QUBIT,
            rango=rango,
            atributos={"nombre": nombre.lexema},
        )

    def compuerta_unaria(self) -> NodoASA:
        """Reconoce las compuertas H, X y Z."""

        inicio = self.control.esperar(
            TokenType.COMPUERTA_H,
            TokenType.COMPUERTA_X,
            TokenType.COMPUERTA_Z,
            contexto="compuerta unaria",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="compuerta unaria",
        )

        objetivo = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="qubit de compuerta unaria",
        )

        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="compuerta unaria",
        )

        nodo_objetivo = NodoASA(
            clase=ClaseNodo.IDENTIFICADOR,
            rango=RangoFuente.de_token(objetivo),
            atributos={"nombre": objetivo.lexema},
        )

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=RangoFuente.de_token(fin).fin,
        )

        return NodoASA(
            clase=ClaseNodo.COMPUERTA,
            rango=rango,
            atributos={"compuerta": inicio.lexema},
            hijos=(nodo_objetivo,),
        )

    def compuerta_binaria(self) -> NodoASA:
        """Reconoce la compuerta CNOT con dos qubits."""

        inicio = self.control.esperar(
            TokenType.CNOT,
            contexto="compuerta binaria",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="compuerta CNOT",
        )

        primer_qubit = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="primer qubit de CNOT",
        )

        self.control.esperar(
            TokenType.COMA,
            contexto="compuerta CNOT",
        )

        segundo_qubit = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="segundo qubit de CNOT",
        )

        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="compuerta CNOT",
        )

        nodo_primero = NodoASA(
            clase=ClaseNodo.IDENTIFICADOR,
            rango=RangoFuente.de_token(primer_qubit),
            atributos={"nombre": primer_qubit.lexema},
        )

        nodo_segundo = NodoASA(
            clase=ClaseNodo.IDENTIFICADOR,
            rango=RangoFuente.de_token(segundo_qubit),
            atributos={"nombre": segundo_qubit.lexema},
        )

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=RangoFuente.de_token(fin).fin,
        )

        return NodoASA(
            clase=ClaseNodo.COMPUERTA,
            rango=rango,
            atributos={"compuerta": inicio.lexema},
            hijos=(nodo_primero, nodo_segundo),
        )

    def medicion(self) -> NodoASA:
        """Reconoce medir(qubit) y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.MEDIR,
            contexto="medicion cuantica",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="medicion cuantica",
        )

        qubit = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="qubit de medicion",
        )

        fin = self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="medicion cuantica",
        )

        nodo_qubit = NodoASA(
            clase=ClaseNodo.IDENTIFICADOR,
            rango=RangoFuente.de_token(qubit),
            atributos={"nombre": qubit.lexema},
        )

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=RangoFuente.de_token(fin).fin,
        )

        return NodoASA(
            clase=ClaseNodo.MEDICION,
            rango=rango,
            hijos=(nodo_qubit,),
        )

    def sentencia_cuantica(self) -> NodoASA:
        """Reconoce una sentencia cuantica completa."""

        tipo = self.control.flujo.mirar().tipo

        # La declaracion de qubit ya consume el punto y coma.
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

        # Las operaciones y mediciones usadas como sentencias
        # requieren punto y coma.
        self.control.esperar(
            TokenType.PUNTO_COMA,
            contexto="sentencia cuantica",
        )

        return nodo
