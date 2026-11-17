
"""Pruebas del recorrido Top-Down del ASA."""

import unittest

from parser.analizador import Analizador
from parser.integracion import ClaseNodo, explorar_para_parser
from parser.semantica.visitante import VisitanteASA


class VisitanteRegistro(VisitanteASA):
    """Visitante de prueba que registra los nodos recorridos."""

    def __init__(self):
        self.recorrido = []
        self.variables = []

    def visitar(self, nodo):
        self.recorrido.append(nodo.clase)
        return super().visitar(nodo)

    def visitar_local(self, nodo):
        self.variables.append(nodo.atributos["nombre"])
        self.visitar_hijos(nodo)


class TestVisitante(unittest.TestCase):

    def test_recorrido_top_down(self):
        fuente = (
            "barista chorreador() { "
            "grano x = 1 + 2; "
            "x = x + 1; "
            "}"
        )

        entrada = explorar_para_parser(fuente)
        resultado = Analizador().analizar(
            entrada.tokens_para_parser()
        )

        self.assertTrue(resultado.correcto)

        visitante = VisitanteRegistro()
        visitante.visitar(resultado.arbol)

        esperado = [
            ClaseNodo.PROGRAMA,
            ClaseNodo.PRINCIPAL,
            ClaseNodo.BLOQUE,
            ClaseNodo.LOCAL,
            ClaseNodo.BINARIA,
            ClaseNodo.LITERAL,
            ClaseNodo.LITERAL,
            ClaseNodo.ASIGNACION,
            ClaseNodo.BINARIA,
            ClaseNodo.IDENTIFICADOR,
            ClaseNodo.LITERAL,
        ]

        self.assertEqual(visitante.recorrido, esperado)
        self.assertEqual(visitante.variables, ["x"])


if __name__ == "__main__":
    unittest.main()
