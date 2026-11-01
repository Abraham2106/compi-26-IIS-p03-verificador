"""Producciones de estructuras de control de Quantum Coffee."""

from collections.abc import Callable

from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import ClaseNodo, NodoASA, Posicion, RangoFuente
from scanner import TokenType


class ProduccionesControl:
    """Reconoce bloques y estructuras de control del lenguaje."""

    def __init__(
        self,
        control: ControlSintactico,
        analizar_sentencia: Callable[[], NodoASA],
        analizar_expresion: Callable[[], NodoASA] | None = None,
        analizar_tipo: Callable[[], str] | None = None,
        recuperar_errores: bool = False,
    ) -> None:
        self.control = control
        self.analizar_sentencia = analizar_sentencia
        self.analizar_expresion = analizar_expresion
        self.analizar_tipo = analizar_tipo
        self.recuperar_errores = recuperar_errores

    def bloque(self) -> NodoASA:
        """Reconoce un bloque y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.LLAVE_ABRE,
            contexto="bloque",
        )

        sentencias = []

        while self.control.flujo.mirar().tipo not in (
            TokenType.LLAVE_CIERRA,
            TokenType.FIN_ARCHIVO,
        ):
            posicion_anterior = self.control.flujo.indice
            try:
                sentencia = self.analizar_sentencia()

            except FalloSintactico:
                if not self.recuperar_errores:
                    raise

                # Buscar el siguiente punto seguro.
                self.control.sincronizar(consumir_punto_coma=True)
                continue
            if self.control.flujo.indice == posicion_anterior:
                raise RuntimeError("El analizador de sentencias no avanzo.")
            sentencias.append(sentencia)

        fin = self.control.esperar(
            TokenType.LLAVE_CIERRA,
            contexto="bloque",
        )

        rango = RangoFuente(
            inicio=Posicion(inicio.linea, inicio.columna),
            fin=RangoFuente.de_token(fin).fin,
        )

        return NodoASA(
            clase=ClaseNodo.BLOQUE,
            rango=rango,
            hijos=tuple(sentencias),
        )

    def condicional(self) -> NodoASA:
        """Reconoce hierve/enfria y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.HIERVE,
            contexto="condicional",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="condicional",
        )

        if self.analizar_expresion is None:
            raise RuntimeError("Falta el analizador de expresiones.")

        # Analizar la condicion utilizando el parser del punto 3.
        posicion_anterior = self.control.flujo.indice
        condicion = self.analizar_expresion()

        if self.control.flujo.indice == posicion_anterior:
            raise RuntimeError("La expresion no consumio tokens.")

        self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="condicional",
        )

        # Bloque que se ejecutaria si la condicion fuera verdadera.
        bloque_verdadero = self.bloque()

        hijos = [condicion, bloque_verdadero]
        ultimo_bloque = bloque_verdadero

        # La parte enfria es opcional.
        if self.control.flujo.mirar().tipo == TokenType.ENFRIA:
            self.control.esperar(TokenType.ENFRIA)
            bloque_falso = self.bloque()

            hijos.append(bloque_falso)
            ultimo_bloque = bloque_falso

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=ultimo_bloque.rango.fin,
        )

        return NodoASA(
            clase=ClaseNodo.CONDICIONAL,
            rango=rango,
            hijos=tuple(hijos),
        )

    def chorreando(self) -> NodoASA:
        """Reconoce un ciclo chorreando y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.CHORREANDO,
            contexto="ciclo chorreando",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="ciclo chorreando",
        )

        if self.analizar_expresion is None:
            raise RuntimeError("Falta el analizador de expresiones.")

        posicion_anterior = self.control.flujo.indice
        condicion = self.analizar_expresion()

        if self.control.flujo.indice == posicion_anterior:
            raise RuntimeError("La expresion no consumio tokens.")

        self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="ciclo chorreando",
        )

        cuerpo = self.bloque()

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=cuerpo.rango.fin,
        )

        return NodoASA(
            clase=ClaseNodo.MIENTRAS,
            rango=rango,
            hijos=(condicion, cuerpo),
        )

    def recolar(self) -> NodoASA:
        """Reconoce un ciclo recolar y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.RECOLAR,
            contexto="ciclo recolar",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="ciclo recolar",
        )

        if self.analizar_tipo is None:
            raise RuntimeError("Falta el analizador de tipos.")

        posicion_anterior = self.control.flujo.indice
        tipo = self.analizar_tipo()

        if self.control.flujo.indice == posicion_anterior:
            raise RuntimeError("El analizador de tipos no consumio tokens.")

        variable = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="variable del ciclo recolar",
        )

        self.control.esperar(
            TokenType.EN,
            contexto="ciclo recolar",
        )

        lista = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="lista del ciclo recolar",
        )

        self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="ciclo recolar",
        )

        cuerpo = self.bloque()

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=cuerpo.rango.fin,
        )

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
        """Reconoce una funcion barista y construye su nodo ASA."""

        inicio = self.control.esperar(
            TokenType.BARISTA,
            contexto="declaracion de funcion",
        )

        nombre = self.control.esperar(
            TokenType.IDENTIFICADOR,
            contexto="nombre de funcion",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="parametros de funcion",
        )

        parametros = []

        # Los parametros son opcionales.
        if self.control.flujo.mirar().tipo != TokenType.PARENTESIS_CIERRA:
            while True:
                if self.analizar_tipo is None:
                    raise RuntimeError("Falta el analizador de tipos.")

                inicio_tipo = self.control.flujo.mirar()
                posicion_anterior = self.control.flujo.indice
                tipo = self.analizar_tipo()

                if self.control.flujo.indice == posicion_anterior:
                    raise RuntimeError("El analizador de tipos no avanzo.")

                identificador = self.control.esperar(
                    TokenType.IDENTIFICADOR,
                    contexto="nombre del parametro",
                )

                rango_parametro = RangoFuente(
                    inicio=RangoFuente.de_token(inicio_tipo).inicio,
                    fin=RangoFuente.de_token(identificador).fin,
                )

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

                # Si no hay coma, terminamos la lista.
                if self.control.flujo.mirar().tipo != TokenType.COMA:
                    break

                self.control.esperar(TokenType.COMA)

        self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="parametros de funcion",
        )

        cuerpo = self.bloque()

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=cuerpo.rango.fin,
        )

        return NodoASA(
            clase=ClaseNodo.FUNCION,
            rango=rango,
            atributos={"nombre": nombre.lexema},
            hijos=tuple(parametros) + (cuerpo,),
        )

    def chorreador(self) -> NodoASA:
        """Reconoce la funcion principal de Quantum Coffee."""

        inicio = self.control.esperar(
            TokenType.BARISTA,
            contexto="funcion principal",
        )

        self.control.esperar(
            TokenType.CHORREADOR,
            contexto="funcion principal",
        )

        self.control.esperar(
            TokenType.PARENTESIS_ABRE,
            contexto="funcion principal",
        )

        self.control.esperar(
            TokenType.PARENTESIS_CIERRA,
            contexto="funcion principal",
        )

        cuerpo = self.bloque()

        rango = RangoFuente(
            inicio=RangoFuente.de_token(inicio).inicio,
            fin=cuerpo.rango.fin,
        )

        return NodoASA(
            clase=ClaseNodo.PRINCIPAL,
            rango=rango,
            atributos={"nombre": "chorreador"},
            hijos=(cuerpo,),
        )
