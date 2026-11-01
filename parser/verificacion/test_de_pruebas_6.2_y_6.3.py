"""Casos completos de aceptacion y rechazo para las tareas 6.2 y 6.3."""
import unittest

from parser.verificacion.pruebas_6_2_6_3 import ejecutar


class TestPruebas62y63(unittest.TestCase):
    def test_casos_documentados(self):
        for resultado in ejecutar():
            with self.subTest(caso=resultado['id']):
                self.assertTrue(resultado['pasa'], resultado['problemas'])
