"""Pruebas de las construcciones cuanticas de Quantum Coffee."""

import unittest

from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import ClaseNodo, FlujoTokens, explorar_para_parser
from parser.producciones_cuanticas import ProduccionesCuanticas
from scanner import TokenType


def crear_producciones(fuente):
    entrada = explorar_para_parser(fuente)
    flujo = FlujoTokens(entrada.tokens_para_parser())
    control = ControlSintactico(flujo)
    return control, ProduccionesCuanticas(control)


class TestQubits(unittest.TestCase):
    """Comprueba las declaraciones de qubits."""

    def test_declaracion_valida(self):
        control, producciones = crear_producciones("qubit q0;")

        nodo = producciones.declaracion_qubit()

        self.assertEqual(nodo.clase, ClaseNodo.QUBIT)
        self.assertEqual(nodo.atributos["nombre"], "q0")
        self.assertEqual(nodo.hijos, ())
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_punto_coma_faltante(self):
        _, producciones = crear_producciones("qubit q0")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.declaracion_qubit()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.PUNTO_COMA,),
        )

    def test_identificador_invalido(self):
        _, producciones = crear_producciones("qubit 10;")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.declaracion_qubit()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.IDENTIFICADOR,),
        )


class TestCompuertasUnarias(unittest.TestCase):
    """Pruebas de las compuertas cuanticas H, X y Z."""

    def test_compuertas_validas(self):
        for compuerta in ("H", "X", "Z"):
            with self.subTest(compuerta=compuerta):
                control, producciones = crear_producciones(f"{compuerta}(q0);")

                nodo = producciones.compuerta_unaria()

                self.assertEqual(nodo.clase, ClaseNodo.COMPUERTA)
                self.assertEqual(
                    nodo.atributos["compuerta"],
                    compuerta,
                )
                self.assertEqual(len(nodo.hijos), 1)
                self.assertEqual(
                    nodo.hijos[0].clase,
                    ClaseNodo.IDENTIFICADOR,
                )
                self.assertEqual(
                    nodo.hijos[0].atributos["nombre"],
                    "q0",
                )

                # El punto y coma lo consume la regla sentencia.
                self.assertEqual(
                    control.flujo.mirar().tipo,
                    TokenType.PUNTO_COMA,
                )

    def test_argumento_invalido(self):
        _, producciones = crear_producciones("H(10);")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.compuerta_unaria()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.IDENTIFICADOR,),
        )

    def test_parentesis_faltante(self):
        _, producciones = crear_producciones("X(q0;")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.compuerta_unaria()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.PARENTESIS_CIERRA,),
        )


class TestCompuertaBinaria(unittest.TestCase):
    """Pruebas de la compuerta cuantica CNOT."""

    def test_cnot_valido(self):
        control, producciones = crear_producciones(
            "CNOT(q0, q1);"
        )

        nodo = producciones.compuerta_binaria()

        self.assertEqual(nodo.clase, ClaseNodo.COMPUERTA)
        self.assertEqual(nodo.atributos["compuerta"], "CNOT")
        self.assertEqual(len(nodo.hijos), 2)

        self.assertEqual(
            nodo.hijos[0].atributos["nombre"], "q0"
        )
        self.assertEqual(
            nodo.hijos[1].atributos["nombre"], "q1"
        )

        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.PUNTO_COMA,
        )

    def test_cnot_sin_coma(self):
        _, producciones = crear_producciones(
            "CNOT(q0 q1);"
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.compuerta_binaria()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.COMA,),
        )

    def test_cnot_segundo_argumento_invalido(self):
        _, producciones = crear_producciones(
            "CNOT(q0, 10);"
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.compuerta_binaria()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.IDENTIFICADOR,),
        )


class TestMedicion(unittest.TestCase):
    """Pruebas de la medicion cuantica."""

    def test_medicion_valida(self):
        control, producciones = crear_producciones(
            "medir(q0);"
        )

        nodo = producciones.medicion()

        self.assertEqual(nodo.clase, ClaseNodo.MEDICION)
        self.assertEqual(len(nodo.hijos), 1)
        self.assertEqual(
            nodo.hijos[0].clase,
            ClaseNodo.IDENTIFICADOR,
        )
        self.assertEqual(
            nodo.hijos[0].atributos["nombre"],
            "q0",
        )

        # El punto y coma pertenece a la sentencia.
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.PUNTO_COMA,
        )

    def test_medicion_argumento_invalido(self):
        _, producciones = crear_producciones(
            "medir(10);"
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.medicion()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.IDENTIFICADOR,),
        )


class TestSentenciasCuanticas(unittest.TestCase):
    """Pruebas de integracion de sentencias cuanticas."""

    def test_sentencias_validas(self):
        casos = (
            ("qubit q0;", ClaseNodo.QUBIT),
            ("H(q0);", ClaseNodo.COMPUERTA),
            ("X(q0);", ClaseNodo.COMPUERTA),
            ("Z(q0);", ClaseNodo.COMPUERTA),
            ("CNOT(q0, q1);", ClaseNodo.COMPUERTA),
            ("medir(q0);", ClaseNodo.MEDICION),
        )

        for fuente, clase_esperada in casos:
            with self.subTest(fuente=fuente):
                control, producciones = crear_producciones(fuente)

                nodo = producciones.sentencia_cuantica()

                self.assertEqual(nodo.clase, clase_esperada)
                self.assertEqual(
                    control.flujo.mirar().tipo,
                    TokenType.FIN_ARCHIVO,
                )

    def test_punto_coma_faltante(self):
        _, producciones = crear_producciones("H(q0)")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.sentencia_cuantica()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.PUNTO_COMA,),
        )


if __name__ == "__main__":
    unittest.main()
