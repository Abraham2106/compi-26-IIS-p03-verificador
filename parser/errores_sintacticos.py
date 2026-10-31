"""Manejo de errores sintacticos de Quantum Coffee."""

from parser.integracion import ErrorSintactico, FlujoTokens
from scanner import Token, TokenType


class FalloSintactico(Exception):
    """Representa un error encontrado durante el analisis."""

    def __init__(self, error: ErrorSintactico) -> None:
        self.error = error
        super().__init__(error.mensaje)


class ControlSintactico:
    """Comprueba los tokens que exige la gramatica."""
    def __init__(self, flujo: FlujoTokens) -> None:
        self.flujo = flujo
        self.errores: list[ErrorSintactico] = []

    def esperar(self, *tipos: TokenType, contexto: str = "") -> Token:
        """Consume un token esperado o reporta un error sintactico."""

        if not tipos:
            raise ValueError("Debe indicarse al menos un token esperado.")

        actual = self.flujo.mirar()

        # Si encontramos el token correcto, avanzamos.
        if actual.tipo in tipos:
            return self.flujo.avanzar()

        # Preparar los nombres de los tokens esperados.
        esperados = " o ".join(tipo.name for tipo in tipos)

        # Distinguir entre token incorrecto y fin del archivo.
        if actual.tipo == TokenType.FIN_ARCHIVO:
            encontrado = "fin de archivo"
        else:
            encontrado = f"{actual.tipo.name} ({actual.lexema!r})"

        mensaje = f"Se esperaba {esperados}, pero se encontro {encontrado}"

        if contexto:
            mensaje += f" al analizar {contexto}"

        # Crear el error utilizando la interfaz del equipo.
        error = ErrorSintactico(
            mensaje=mensaje,
            encontrado=actual,
            esperados=tuple(tipos),
        )
        self.errores.append(error)
        raise FalloSintactico(error)

    def sincronizar(self, consumir_punto_coma: bool = False) -> Token:
        """Avanza hasta un punto seguro despues de un error."""

        limites = {
            TokenType.PUNTO_COMA,
            TokenType.LLAVE_CIERRA,
            TokenType.FIN_ARCHIVO,
        }

        while self.flujo.mirar().tipo not in limites:
            self.flujo.avanzar()

        actual = self.flujo.mirar()

        if consumir_punto_coma and actual.tipo == TokenType.PUNTO_COMA:
            self.flujo.avanzar()

        return actual
