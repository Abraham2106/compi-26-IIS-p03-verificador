"""Producciones de estructuras de control de Quantum Coffee."""

from parser.asa_constructores import rango_entre
from parser.errores_sintacticos import FalloSintactico
from parser.integracion import ClaseNodo, NodoASA
from scanner import TokenType


class ProduccionesControl:
    """Reconoce bloques y estructuras de control del lenguaje."""

    def __init__(self, analizador, recuperar_errores: bool = True) -> None:
        self.analizador = analizador
        self.control = analizador.control
        self.recuperar_errores = recuperar_errores

    def bloque(self) -> NodoASA:
        inicio = self.control.esperar(TokenType.LLAVE_ABRE, contexto="bloque")
        sentencias = []
        while self.control.flujo.mirar().tipo not in (
            TokenType.LLAVE_CIERRA,
            TokenType.FIN_ARCHIVO,
        ):
            posicion_anterior = self.control.flujo.indice
            try:
                sentencia = self.analizador.sentencia()
            except FalloSintactico:
                if not self.recuperar_errores:
                    raise
                self.control.sincronizar(consumir_punto_coma=True)
                continue
            if self.control.flujo.indice == posicion_anterior:
                raise RuntimeError("El analizador de sentencias no avanzo.")
            sentencias.append(sentencia)
        fin = self.control.esperar(TokenType.LLAVE_CIERRA, contexto="bloque")
        rango = rango_entre(inicio, fin)
        return NodoASA(
            clase=ClaseNodo.BLOQUE, rango=rango, hijos=tuple(sentencias)
        )

    def _condicion(self, contexto: str) -> NodoASA:
        self.control.esperar(TokenType.PARENTESIS_ABRE, contexto=contexto)
        posicion_anterior = self.control.flujo.indice
        condicion = self.analizador.expresiones.expresion()
        if self.control.flujo.indice == posicion_anterior:
            raise RuntimeError("La expresion no consumio tokens.")
        self.control.esperar(TokenType.PARENTESIS_CIERRA, contexto=contexto)
        return condicion

    def condicional(self) -> NodoASA:
        inicio = self.control.esperar(TokenType.HIERVE, contexto="condicional")
        condicion = self._condicion("condicional")
        bloque_verdadero = self.bloque()
        hijos = [condicion, bloque_verdadero]
        ultimo_bloque = bloque_verdadero
        if self.control.flujo.mirar().tipo == TokenType.ENFRIA:
            self.control.esperar(TokenType.ENFRIA)
            bloque_falso = self.bloque()
            hijos.append(bloque_falso)
            ultimo_bloque = bloque_falso
        rango = rango_entre(inicio, ultimo_bloque)
        return NodoASA(
            clase=ClaseNodo.CONDICIONAL, rango=rango, hijos=tuple(hijos)
        )

    def chorreando(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.CHORREANDO, contexto="ciclo chorreando"
        )
        condicion = self._condicion("ciclo chorreando")
        cuerpo = self.bloque()
        rango = rango_entre(inicio, cuerpo)
        return NodoASA(
            clase=ClaseNodo.MIENTRAS, rango=rango, hijos=(condicion, cuerpo)
        )

    def recolar(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.RECOLAR, contexto="ciclo recolar"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="ciclo recolar"
        )
        posicion_anterior = self.control.flujo.indice
        tipo = self.analizador.declaraciones.tipo()
        if self.control.flujo.indice == posicion_anterior:
            raise RuntimeError("El analizador de tipos no consumio tokens.")
        variable = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="variable del ciclo recolar"
        )
        self.control.esperar(TokenType.EN, contexto="ciclo recolar")
        lista = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="lista del ciclo recolar"
        )
        self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="ciclo recolar"
        )
        cuerpo = self.bloque()
        rango = rango_entre(inicio, cuerpo)
        return NodoASA(
            clase=ClaseNodo.PARA_CADA,
            rango=rango,
            atributos={
                "tipo": tipo,
                "nombre": variable.lexema,
                "lista": lista.lexema,
            },
            hijos=(cuerpo,),
        )

    def funcion(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.BARISTA, contexto="declaracion de funcion"
        )
        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR, contexto="nombre de funcion"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="parametros de funcion"
        )
        parametros = []
        if self.control.flujo.mirar().tipo != TokenType.PARENTESIS_CIERRA:
            while True:
                inicio_tipo = self.control.flujo.mirar()
                posicion_anterior = self.control.flujo.indice
                tipo = self.analizador.declaraciones.tipo()
                if self.control.flujo.indice == posicion_anterior:
                    raise RuntimeError("El analizador de tipos no avanzo.")
                identificador = self.control.esperar(
                    TokenType.IDENTIFICADOR, contexto="nombre del parametro"
                )
                rango_parametro = rango_entre(inicio_tipo, identificador)
                parametros.append(
                    NodoASA(
                        clase=ClaseNodo.PARAMETRO,
                        rango=rango_parametro,
                        atributos={
                            "nombre": identificador.lexema,
                            "tipo": tipo,
                        },
                    )
                )
                if self.control.flujo.mirar().tipo != TokenType.COMA:
                    break
                self.control.esperar(TokenType.COMA)
        self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="parametros de funcion"
        )
        cuerpo = self.bloque()
        rango = rango_entre(inicio, cuerpo)
        return NodoASA(
            clase=ClaseNodo.FUNCION,
            rango=rango,
            atributos={"nombre": nombre.lexema},
            hijos=tuple(parametros) + (cuerpo,),
        )

    def chorreador(self) -> NodoASA:
        inicio = self.control.esperar(
            TokenType.BARISTA, contexto="funcion principal"
        )
        self.control.esperar(
            TokenType.CHORREADOR, contexto="funcion principal"
        )
        self.control.esperar(
            TokenType.PARENTESIS_ABRE, contexto="funcion principal"
        )
        self.control.esperar(
            TokenType.PARENTESIS_CIERRA, contexto="funcion principal"
        )
        cuerpo = self.bloque()
        rango = rango_entre(inicio, cuerpo)
        return NodoASA(
            clase=ClaseNodo.PRINCIPAL,
            rango=rango,
            atributos={"nombre": "chorreador"},
            hijos=(cuerpo,),
        )
