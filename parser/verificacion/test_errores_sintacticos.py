"""Pruebas del manejo de errores sintacticos."""

import unittest

from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import FlujoTokens, explorar_para_parser
from scanner import TokenType


def crear_control(codigo):
    """Crea un controlador usando el scanner real."""
    entrada = explorar_para_parser(codigo)
    tokens = entrada.tokens_para_parser()
    return ControlSintactico(FlujoTokens(tokens))


class TestErroresSintacticos(unittest.TestCase):
    def test_token_correcto(self):
        control = crear_control("grano")

        token = control.esperar(TokenType.GRANO)

        self.assertEqual(token.lexema, "grano")

    def test_punto_coma_faltante(self):
        control = crear_control("25 }")

        control.esperar(TokenType.ENTERO)

        with self.assertRaises(FalloSintactico) as resultado:
            control.esperar(TokenType.PUNTO_COMA)

        error = resultado.exception.error

        self.assertEqual(error.encontrado.lexema, "}")
        self.assertEqual(error.encontrado.columna, 4)

    def test_fin_archivo_inesperado(self):
        control = crear_control("25")

        control.esperar(TokenType.ENTERO)

        with self.assertRaises(FalloSintactico) as resultado:
            control.esperar(TokenType.PUNTO_COMA)

        mensaje = resultado.exception.error.mensaje

        self.assertIn("fin de archivo", mensaje)

    def test_recuperacion(self):
        control = crear_control("grano x = 10; cafe")

        encontrado = control.sincronizar(consumir_punto_coma=True)

        self.assertEqual(encontrado.tipo, TokenType.PUNTO_COMA)

        self.assertEqual(control.flujo.mirar().tipo, TokenType.CAFE)
    
    def test_registro_de_errores(self):
        control = crear_control("25 }")

        control.esperar(TokenType.ENTERO)

        with self.assertRaises(FalloSintactico):
            control.esperar(TokenType.PUNTO_COMA)

        self.assertEqual(len(control.errores), 1)

        self.assertEqual(
            control.errores[0].encontrado.tipo,
            TokenType.LLAVE_CIERRA,
        )

        self.assertEqual(
            control.errores[0].esperados,
            (TokenType.PUNTO_COMA,),
        )

if __name__ == "__main__":
    unittest.main()
