"""Pruebas de la impresion de cambios de la tabla de simbolos (1.4.1)."""

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.analisis import verificar_semantica
from parser.semantica.impresion_tabla import (
    cambios_a_texto, imprimir_cambios, lineas_cambios,
)
from parser.semantica.tabla_simbolos import TablaSimbolos, TipoCambio

E, R, C, S = (TipoCambio.ENTRAR, TipoCambio.REGISTRAR,
              TipoCambio.CONFLICTO, TipoCambio.SALIR)


def tabla_de(fuente):
    entrada = explorar_para_parser(fuente)
    resultado = Analizador().analizar(entrada.tokens_para_parser())
    assert resultado.correcto, resultado.errores
    tabla = TablaSimbolos()
    verificar_semantica(resultado.arbol, tabla)
    return tabla


class TestRegistroDeCambios(unittest.TestCase):

    def test_orden_de_los_cambios(self):
        tabla = tabla_de(
            "cafeteria grano g = 1; "
            "barista f(grano a) { grano b = a; } "
            "barista chorreador() { }")
        self.assertEqual(
            [(c.tipo, c.simbolo.nombre if c.simbolo else None)
             for c in tabla.cambios],
            [(R, "g"), (R, "f"),
             (E, None), (R, "a"),          # Ambito de f: parametros.
             (E, None), (R, "b"), (S, None),   # Cuerpo de f.
             (S, None),
             (E, None), (S, None)])        # Bloque de chorreador.

    def test_conflicto_guarda_ambas_declaraciones(self):
        tabla = tabla_de("barista chorreador() { grano x = 1; poso x; }")
        conflicto = [c for c in tabla.cambios if c.tipo == C][0]
        self.assertEqual(conflicto.simbolo.tipo, "poso")
        self.assertEqual(conflicto.existente.tipo, "grano")
        self.assertIs(conflicto.ambito, conflicto.existente.ambito)

    def test_salir_guarda_el_contenido_del_ambito(self):
        tabla = tabla_de(
            "barista chorreador() { grano x = 1; qubit q; "
            "hierve (fuerte) { grano y = 2; } }")
        salidas = [c for c in tabla.cambios if c.tipo == S]
        self.assertEqual([[s.nombre for s in c.contenido] for c in salidas],
                         [["y"], ["x", "q"]])

    def test_entradas_y_salidas_en_pareja(self):
        tabla = tabla_de(
            "barista chorreador() { taza grano xs = [1]; "
            "recolar (grano n en xs) { chorreando (ralo) { } } }")
        tipos = [c.tipo for c in tabla.cambios]
        self.assertEqual(tipos.count(E), tipos.count(S))
        self.assertEqual(tabla.nivel, 0)

    def test_tabla_nueva_sin_cambios(self):
        self.assertEqual(TablaSimbolos().cambios, [])
        self.assertEqual(cambios_a_texto(TablaSimbolos()), "(sin cambios)\n")


class TestTexto(unittest.TestCase):

    def test_lineas(self):
        tabla = tabla_de(
            "barista doble(grano a) { degustar a * 2; }\n"
            "barista chorreador() {\n"
            "    grano x = 1;\n"
            "    grano x = 2;\n"
            "}")
        self.assertEqual(lineas_cambios(tabla), [
            " 1  registrar  doble: funcion (grano) -> grano (1:1) "
            "en ambito 0",
            " 2  entrar     Ambito 1 (nivel 1, dentro de 0)",
            " 3    registrar  a: parametro grano (1:15) en ambito 1",
            " 4    entrar     Ambito 2 (nivel 2, dentro de 1)",
            " 5    salir      Ambito 2: (vacio)",
            " 6  salir      Ambito 1: a",
            " 7  entrar     Ambito 3 (nivel 1, dentro de 0)",
            " 8    registrar  x: variable local grano (3:5) en ambito 3",
            " 9    conflicto  x: variable local grano (4:5) ya declarado "
            "en 3:5 como variable local",
            "10  salir      Ambito 3: x",
        ])

    def test_imprimir_incluye_cambios_y_tabla_final(self):
        tabla = tabla_de("barista chorreador() { grano x = 1; }")
        salida = io.StringIO()
        imprimir_cambios(tabla, salida)
        texto = salida.getvalue()
        self.assertIn("Cambios de la tabla de simbolos", texto)
        self.assertIn("Tabla de simbolos final", texto)
        self.assertIn("registrar  x: variable local grano", texto)


class TestLineaDeComandos(unittest.TestCase):

    def ejecutar(self, *opciones):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "p.qc"
            ruta.write_text("barista chorreador() { grano x = 1; }",
                            encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-m", "parser.semantica", str(ruta),
                 *opciones],
                capture_output=True, text=True,
                cwd=Path(__file__).resolve().parents[2])

    def test_con_tabla(self):
        resultado = self.ejecutar("--tabla")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Cambios de la tabla de simbolos", resultado.stdout)
        self.assertIn("registrar  x", resultado.stdout)

    def test_sin_tabla_no_cambia_la_salida(self):
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertNotIn("Cambios", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
