"""Pruebas de la impresion de cambios de la tabla de simbolos (1.4.1)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.analisis import verificar_semantica
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


class TestLineaDeComandos(unittest.TestCase):

    def ejecutar(self, *opciones):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "p.qc"
            ruta.write_text(
                "barista chorreador() { grano x = 1; grano y = 2; "
                "servir(x); }",
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
        estado_x = resultado.stdout.split("registrar  x", 1)[1].split(
            "registrar  y", 1)[0]
        self.assertIn("x: variable local grano", estado_x)
        self.assertNotIn("y: variable local grano", estado_x)
        self.assertLess(
            resultado.stdout.index("Tabla de simbolos final"),
            resultado.stdout.index("ASA decorado en preorden"))
        self.assertIn("decorado=[tipo=grano;", resultado.stdout)
        self.assertIn("nombre=def:DeclaracionLocal:x@", resultado.stdout)

    def test_sin_tabla_no_imprime_historial(self):
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertNotIn("Cambios", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
