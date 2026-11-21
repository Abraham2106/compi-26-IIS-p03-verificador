"""Pruebas representativas de la inferencia de tipos de Quantum Coffee."""

import unittest
from pathlib import Path

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.inferencia_tipos import InferidorTipos
from parser.semantica.tabla_simbolos import TablaSimbolos
from parser.semantica.verificador_identificadores import (
    VerificadorIdentificadores,
)


class TestInferenciaTipos(unittest.TestCase):
    def analizar(self, fuente):
        entrada = explorar_para_parser(fuente)
        resultado = Analizador().analizar(entrada.tokens_para_parser())
        self.assertTrue(resultado.correcto, resultado.errores)
        arbol = resultado.arbol
        tabla = TablaSimbolos()
        verificador = VerificadorIdentificadores(
            tabla.resolver, tabla.declarar, tabla.entrar, tabla.salir
        )
        self.assertEqual(verificador.verificar(arbol), [])
        errores = InferidorTipos().inferir(arbol)
        return arbol, errores

    def test_expresiones_validas(self):
        casos = [
            ("grano x = 5;", "grano"),
            ('granoMolido x = "hola";', "granoMolido"),
            ("cafe x = fuerte;", "cafe"),
            ("poso x = 5 + 2.5;", "poso"),
            ("poso x = 5 / 2;", "poso"),
            ('granoMolido x = "a" + "b";', "granoMolido"),
            ("cafe x = 5 < 10;", "cafe"),
            ("cafe x = fuerte SinAzucar ralo;", "cafe"),
            ("cafe x = Amargo fuerte;", "cafe"),
            ("taza grano xs = [1, 2];", "taza grano"),
            ("taza poso xs = [1, 2.5];", "taza poso"),
            ("taza grano xs = [];", "taza grano"),
            ("taza taza grano xs = [[], [1, 2]];", "taza taza grano"),
            ("granoMolido x = leer();", "granoMolido"),
        ]
        for cuerpo, tipo in casos:
            with self.subTest(cuerpo=cuerpo):
                arbol, errores = self.analizar(
                    f"barista chorreador() {{ {cuerpo} }}"
                )
                self.assertEqual(errores, [])
                inicial = arbol.hijos[0].hijos[0].hijos[0].hijos[0]
                self.assertEqual(inicial.semantica.tipo_inferido, tipo)

    def test_errores_de_tipos(self):
        casos = [
            ('grano x = "hola";', "no se puede asignar"),
            ('granoMolido x = "hola" + 5;', "no se puede aplicar '+'"),
            ("cafe x = fuerte SinAzucar 5;", "SinAzucar"),
            ("cafe x = Amargo 5;", "Amargo"),
            ('granoMolido x = -"hola";', "no se puede aplicar '-'"),
            ('taza grano xs = [1, "hola"];', "elementos de lista"),
            ("grano x = [];", "lista vacia"),
            ("grano x = servir(10);", "sin_valor"),
            ("leer(10);", "leer no recibe argumentos"),
            ("servir();", "servir requiere"),
            ("hierve (5) {}", "hierve requiere"),
            ("grano n = 5; n.buscar(1);", "no es una lista"),
            ('taza grano xs = [1]; xs.insertar("a");', "insertar"),
            ("grano n = 5; H(n);", "requiere un qubit"),
            ("grano n = 5; cafe x = medir(n);", "medir requiere"),
        ]
        for cuerpo, mensaje in casos:
            with self.subTest(cuerpo=cuerpo):
                _, errores = self.analizar(
                    f"barista chorreador() {{ {cuerpo} }}"
                )
                self.assertTrue(errores, cuerpo)
                self.assertTrue(any(mensaje in e for e in errores), errores)

    def test_funciones_y_recursion(self):
        casos = [
            (
                "barista f(grano n) { degustar n; } "
                "barista chorreador() { grano x = f(2); }", "grano", []
            ),
            (
                "barista f() { degustar 2; } "
                "barista chorreador() { f(); }", "grano", []
            ),
            (
                "barista f() { degustar f(); } "
                "barista chorreador() { f(); }", None,
                ["no se pudo inferir el tipo de retorno"]
            ),
            (
                "barista f(grano n) { hierve (n <= 0) "
                "{ degustar 0; } enfria { degustar f(n - 1); } } "
                "barista chorreador() { grano x = f(3); }", "grano", []
            ),
            (
                "barista f() { degustar g(); } "
                "barista g() { degustar 1; } "
                "barista chorreador() { f(); }", "grano", []
            ),
            (
                "barista f(grano n) {} "
                'barista chorreador() { f("a"); }',
                "sin_valor", ["argumento 1"]
            ),
            (
                "barista f(grano n) {} "
                "barista chorreador() { f(); }",
                "sin_valor", ["requiere 1 argumento(s)"]
            ),
            (
                "barista f() { degustar descafeinado; } "
                "barista chorreador() {}", "descafeinado", []
            ),
            (
                "barista f() { degustar SeQuemoElCafe; } "
                "barista chorreador() {}", "SeQuemoElCafe", []
            ),
        ]
        for fuente, tipo, esperado in casos:
            with self.subTest(fuente=fuente[:35]):
                arbol, errores = self.analizar(fuente)
                self.assertEqual(len(errores), len(esperado))
                for mensaje in esperado:
                    self.assertTrue(any(mensaje in e for e in errores))
                self.assertEqual(arbol.hijos[0].semantica.tipo_inferido, tipo)

    def test_cuantica_y_listas(self):
        fuente = (
            "barista chorreador() { qubit q; H(q); "
            "cafe m = medir(q); taza grano xs = [1, 2]; "
            "cafe encontrado = xs.buscar(2); grano v = xs.extraer(0); "
            "recolar (grano n en xs) {} }"
        )
        arbol, errores = self.analizar(fuente)
        self.assertEqual(errores, [])
        nodos = arbol.hijos[0].hijos[0].hijos
        self.assertEqual(nodos[0].semantica.tipo_inferido, "qubit")
        self.assertEqual(nodos[1].semantica.tipo_inferido, "sin_valor")
        self.assertEqual(nodos[2].hijos[0].semantica.tipo_inferido, "cafe")
        self.assertEqual(nodos[4].hijos[0].semantica.tipo_inferido, "cafe")
        self.assertEqual(nodos[5].hijos[0].semantica.tipo_inferido, "grano")

    def test_ejemplos_completos(self):
        base = Path(__file__).resolve().parents[1] / "ejemplos_completos"
        ejemplos = [
            "04_ejercicio.qc", "05_ejercicio.qc",
            "06_cuantica.qc", "07_ajustes.qc",
        ]
        for nombre in ejemplos:
            with self.subTest(ejemplo=nombre):
                fuente = (base / nombre).read_text(encoding="utf-8")
                _, errores = self.analizar(fuente)
                self.assertEqual(errores, [])


if __name__ == "__main__":
    unittest.main()
