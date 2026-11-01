"""Pruebas de integración del scanner, parser real y ASA."""

import unittest
from pathlib import Path

from parser.analizador import Analizador
from parser.asa_esquema import validar_arbol
from parser.integracion import explorar_para_parser


class TestParserCompleto(unittest.TestCase):
    def parsear(self, fuente):
        entrada = explorar_para_parser(fuente)
        self.assertTrue(entrada.apta, entrada.errores_lexicos)
        return Analizador().analizar(entrada.tokens_para_parser())

    def test_programas_de_referencia(self):
        carpeta = Path(__file__).resolve().parents[1] / "ejemplos_completos"
        for archivo in sorted(carpeta.glob("*.qc")):
            with self.subTest(programa=archivo.name):
                resultado = self.parsear(archivo.read_text(encoding="utf-8"))
                self.assertTrue(resultado.correcto, resultado.errores)
                self.assertEqual(validar_arbol(resultado.arbol), [])

    def test_recuperacion_conserva_sentencia_posterior(self):
        resultado = self.parsear(
            "barista chorreador() { grano a = ; grano b = ; grano c = 3; }"
        )
        self.assertFalse(resultado.correcto)
        self.assertEqual(len(resultado.errores), 2)
        bloque = resultado.arbol.hijos[-1].hijos[0]
        self.assertEqual(bloque.hijos[-1].atributos["nombre"], "c")
        self.assertTrue(
            all(e.encontrado.linea == 1 for e in resultado.errores)
        )

    def test_fin_inesperado_y_cierre_de_bloque(self):
        for fuente in (
            "barista chorreador() { hierve (fuerte) { grano a = } }",
            "barista chorreador() { hierve (fuerte) {",
        ):
            with self.subTest(fuente=fuente):
                resultado = self.parsear(fuente)
                self.assertFalse(resultado.correcto)
                self.assertTrue(resultado.errores)
