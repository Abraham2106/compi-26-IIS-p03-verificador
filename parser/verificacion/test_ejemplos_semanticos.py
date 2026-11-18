"""Ejecucion de los ejemplos .qc con el verificador semantico (1.5.3)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.analisis import verificar_semantica

PARSER = Path(__file__).resolve().parents[1]
RAIZ = PARSER.parent
VALIDOS = PARSER / "ejemplos_completos"
CON_ERRORES = PARSER / "ejemplos_semanticos"


def verificar_archivo(ruta):
    entrada = explorar_para_parser(ruta.read_text(encoding="utf-8-sig"))
    resultado = Analizador().analizar(entrada.tokens_para_parser())
    assert resultado.correcto, resultado.errores
    return verificar_semantica(resultado.arbol)


class TestEjemplosSemanticos(unittest.TestCase):

    def test_ejemplos_validos_no_tienen_errores(self):
        archivos = sorted(VALIDOS.glob("*.qc"))
        self.assertGreaterEqual(len(archivos), 8)
        for archivo in archivos:
            with self.subTest(ejemplo=archivo.name):
                self.assertEqual(verificar_archivo(archivo), [])

    def test_ejemplos_con_errores_dan_los_errores_esperados(self):
        casos = json.loads(
            (CON_ERRORES / "casos.json").read_text(encoding="utf-8"))
        archivos = {p.name for p in CON_ERRORES.glob("*.qc")}
        self.assertEqual(set(casos), archivos)
        for nombre, esperados in casos.items():
            with self.subTest(ejemplo=nombre):
                errores = verificar_archivo(CON_ERRORES / nombre)
                self.assertEqual(len(errores), len(esperados),
                                 [e.mensaje for e in errores])
                for error, (linea, columna, fragmento) in zip(
                        errores, esperados):
                    self.assertEqual((error.linea, error.columna),
                                     (linea, columna))
                    self.assertIn(fragmento, error.mensaje)

    def test_linea_de_comandos(self):
        def ejecutar(ruta):
            return subprocess.run(
                [sys.executable, "-m", "parser.semantica", str(ruta)],
                cwd=RAIZ, capture_output=True, text=True,
            )

        correcto = ejecutar(VALIDOS / "07_ajustes.qc")
        self.assertEqual(correcto.returncode, 0)
        self.assertIn("verificacion semantica correcta", correcto.stdout)
        self.assertEqual(correcto.stderr, "")

        fallido = ejecutar(CON_ERRORES / "E01_no_declarado.qc")
        self.assertEqual(fallido.returncode, 1)
        self.assertIn(":4:21: error semantico:", fallido.stderr)
        self.assertIn("2 errores semanticos", fallido.stderr)

    def test_linea_de_comandos_con_error_sintactico(self):
        ruta = CON_ERRORES / "casos.json"  # No es codigo .qc valido.
        resultado = subprocess.run(
            [sys.executable, "-m", "parser.semantica", str(ruta)],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(resultado.returncode, 1)


if __name__ == "__main__":
    unittest.main()
