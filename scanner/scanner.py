"""Define la interfaz compartida del scanner de Quantum Coffee.

El scanner devuelve tokens y errores. main.py muestra los resultados.
Las etapas posteriores pueden reutilizar la lista de tokens.
"""

from typing import List, Optional, Tuple

if __package__:
    from .errores import ErrorLexico
    from .tokens import (
        Token,
        TokenType,
        PALABRAS_RESERVADAS,
        SIMBOLOS_DOBLES,
        SIMBOLOS_SIMPLES,
    )
else:  # Compatibilidad: python scanner/main.py archivo.qc
    from errores import ErrorLexico
    from tokens import (
        Token,
        TokenType,
        PALABRAS_RESERVADAS,
        SIMBOLOS_DOBLES,
        SIMBOLOS_SIMPLES,
    )

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
DIGITOS = "0123456789"


class Scanner:
    def __init__(self, fuente: str) -> None:
        self.fuente = fuente
        self.pos = 0
        self.linea = 1
        self.columna = 1

        self.tokens: List[Token] = []
        self.errores: List[ErrorLexico] = []

        self._ini_pos = 0
        self._ini_linea = 1
        self._ini_columna = 1

    def escanear(self) -> Tuple[List[Token], List[ErrorLexico]]:
        """Devuelve los tokens y errores de toda la fuente.

        No agrega un token FIN_ARCHIVO.
        """
        while not self._fin():
            self._saltar_ignorables()

            if self._fin():
                break

            self._marcar_inicio()
            self._escanear_siguiente()

        return self.tokens, self.errores

    def _escanear_siguiente(self) -> None:
        c = self._actual()

        if c in LETRAS:
            self._leer_identificador()
        elif c in DIGITOS:
            self._leer_numero()
        elif c == '"':
            self._leer_cadena()
        else:
            self._leer_simbolo()

    def _emitir(self, tipo: TokenType, lexema: Optional[str] = None) -> None:
        """Conserva en el token la posicion inicial del lexema."""
        if lexema is None:
            lexema = self.fuente[self._ini_pos:self.pos]

        self.tokens.append(
            Token(
                tipo=tipo,
                lexema=lexema,
                linea=self._ini_linea,
                columna=self._ini_columna,
            )
        )

    def _registrar_error(
        self,
        mensaje: str,
        lexema: Optional[str] = None,
    ) -> None:
        """Registra el error y permite continuar el analisis."""
        if lexema is None:
            lexema = self.fuente[self._ini_pos:self.pos]

        self.errores.append(
            ErrorLexico(
                mensaje=mensaje,
                lexema=lexema,
                linea=self._ini_linea,
                columna=self._ini_columna,
            )
        )

    # ------------------------------------------------------------------
    # Primitivas de lectura y seguimiento de posicion (2.2)
    # ------------------------------------------------------------------

    def _fin(self) -> bool:
        """Indica si ya se consumio toda la fuente."""
        return self.pos >= len(self.fuente)

    def _actual(self) -> str:
        """Caracter actual sin avanzar; '\\0' si se llego al final."""
        if self._fin():
            return "\0"
        return self.fuente[self.pos]

    def _siguiente(self) -> str:
        """Caracter siguiente sin avanzar; '\\0' si no existe."""
        if self.pos + 1 >= len(self.fuente):
            return "\0"
        return self.fuente[self.pos + 1]

    def _avanzar(self) -> str:
        """Consume un caracter y actualiza pos, linea y columna.

        LF, CRLF y CR representan un salto de linea cada uno.
        Las columnas cuentan caracteres; un tabulador cuenta como uno.
        """
        c = self.fuente[self.pos]
        self.pos += 1

        if c == "\r":
            self.linea += 1
            self.columna = 1
        elif c == "\n":
            if self.pos < 2 or self.fuente[self.pos - 2] != "\r":
                self.linea += 1
            self.columna = 1
        else:
            self.columna += 1

        return c

    def _marcar_inicio(self) -> None:
        """Guarda la posicion donde empieza el lexema que se va a leer."""
        self._ini_pos = self.pos
        self._ini_linea = self.linea
        self._ini_columna = self.columna

    # ------------------------------------------------------------------
    # Whitespace y comentarios (2.3 y 2.4)
    # ------------------------------------------------------------------

    def _saltar_ignorables(self) -> None:
        """Omite espacios, tabs, saltos de linea y comentarios '#'.

        Los comentarios llegan hasta el fin de linea (sin consumir el
        salto) y no producen tokens.
        """
        while not self._fin():
            c = self._actual()

            if c in " \t\r\n":
                self._avanzar()
            elif c == "#":
                while not self._fin() and self._actual() not in "\r\n":
                    self._avanzar()
            else:
                break

    # ------------------------------------------------------------------
    # Errores
    # ------------------------------------------------------------------

    def _error_simbolo_desconocido(self) -> None:
        """Consume el simbolo invalido, lo registra y deja continuar."""
        self._avanzar()
        self._registrar_error("Simbolo desconocido")

    def _leer_identificador(self):
        """Reconoce palabras reservadas e identificadores."""

        while not self._fin() and (self._actual() in LETRAS or self._actual()
                                   in DIGITOS or self._actual() == "_"):
            self._avanzar()

        lexema = self.fuente[self._ini_pos:self.pos]

        tipo = PALABRAS_RESERVADAS.get(lexema, TokenType.IDENTIFICADOR)

        self._emitir(tipo)

    def _leer_numero(self) -> None:
        """Reconoce numeros enteros y decimales."""

        while not self._fin() and self._actual() in DIGITOS:
            self._avanzar()

        tipo = TokenType.ENTERO

        if not self._fin() and self._actual() == ".":
            siguiente = self._siguiente()

            if siguiente and siguiente in DIGITOS:
                tipo = TokenType.DECIMAL
                self._avanzar()

                while not self._fin() and self._actual() in DIGITOS:
                    self._avanzar()

        self._emitir(tipo)

    def _leer_cadena(self) -> None:
        """Reconoce cadenas de texto y detecta cadenas sin cerrar."""

        self._avanzar()

        while not self._fin() and self._actual() not in ('"', '\n', '\r'):
            self._avanzar()

        if not self._fin() and self._actual() == '"':
            self._avanzar()
            self._emitir(TokenType.CADENA)

        else:
            self._registrar_error("Cadena sin cerrar")

    def _leer_simbolo(self) -> None:
        """Reconoce operadores y delimitadores del lenguaje."""

        doble = self._actual() + self._siguiente()

        if doble in SIMBOLOS_DOBLES:
            self._avanzar()
            self._avanzar()
            self._emitir(SIMBOLOS_DOBLES[doble])
            return

        simple = self._actual()

        if simple in SIMBOLOS_SIMPLES:
            self._avanzar()
            self._emitir(SIMBOLOS_SIMPLES[simple])
            return

        self._error_simbolo_desconocido()


"""
Se debe detectar el fin de la entrada y consultar el caracter actual.
Luego se debe consultar el siguiente caracter sin avanzar.
Se debe avanzar y actualizar la linea y la columna.
Se debe guardar la posicion inicial de cada lexema.
Se deben omitir espacios, tabulaciones, saltos de linea y comentarios #.
Los comentarios no deben producir tokens.

Se debe leer cada identificador y consultar PALABRAS_RESERVADAS.
Si el lexema no aparece en el catalogo, se debe emitir IDENTIFICADOR.
Luego se deben reconocer los literales ENTERO, DECIMAL y CADENA.
Las cadenas deben conservar el texto original y las comillas.
Se debe acordar cualquier error adicional para cadenas sin cerrar.

Se deben comprobar SIMBOLOS_DOBLES antes de SIMBOLOS_SIMPLES.
Este orden permite reconocer el lexema valido mas largo.
Si no hay coincidencia, se debe llamar a _error_simbolo_desconocido().
Se debe consumir el simbolo desconocido y registrar su linea y columna.
Luego se debe continuar con el siguiente caracter.

Aun no hay recuperacion en modo panico, recuperacion
a nivel de frase, tabla de simbolos ni analisis sintactico.
"""
