"""Pruebas del reporte de errores semanticos (1.3.4)."""

import io
import unittest
from unittest import mock

from parser.semantica import errores_semanticos as es
from parser.semantica.errores_semanticos import (
    ErrorSemantico,
    convertir,
    formatear,
    recolectar,
    reportar,
)


class TestErroresSemanticos(unittest.TestCase):

    def test_convertir_formato_de_los_verificadores(self):
        [error] = convertir(
            ["Linea 4, columna 21: identificador 'x' no declarado"],
            "identificadores",
        )
        self.assertEqual(error, ErrorSemantico(
            4, 21, "identificador 'x' no declarado", "identificadores"))

    def test_convertir_texto_sin_formato_usa_posicion_cero(self):
        [error] = convertir(["algo raro"])
        self.assertEqual((error.linea, error.columna), (0, 0))
        self.assertEqual(error.mensaje, "algo raro")

    def test_recolectar_ordena_por_posicion_entre_fases(self):
        errores = recolectar(
            ("identificadores", ["Linea 9, columna 1: b"]),
            ("tipos", ["Linea 2, columna 7: a", "Linea 2, columna 3: c"]),
        )
        self.assertEqual([e.mensaje for e in errores], ["c", "a", "b"])
        self.assertEqual(errores[2].fase, "identificadores")

    def test_recolectar_elimina_duplicados(self):
        errores = recolectar(
            ("identificadores", ["Linea 1, columna 1: igual"]),
            ("tipos", ["Linea 1, columna 1: igual"]),
        )
        self.assertEqual(len(errores), 1)

    def test_formato_con_fragmento_y_caret(self):
        error = ErrorSemantico(2, 5, "mensaje")
        texto = formatear(error, "a.qc", ["linea uno", "    x = 1 ;"])
        self.assertEqual(
            texto,
            "a.qc:2:5: error semantico: mensaje\n"
            "        x = 1 ;\n"
            "        ^",
        )

    def test_formato_conserva_tabuladores_bajo_el_caret(self):
        error = ErrorSemantico(1, 3, "m")
        texto = formatear(error, "a.qc", ["\t\tx"])
        self.assertTrue(texto.endswith("\n    \t\t^"))

    def test_formato_sin_fragmento(self):
        error = ErrorSemantico(1, 1, "m")
        with mock.patch.object(es, "MOSTRAR_FRAGMENTO", False):
            self.assertEqual(
                formatear(error, "a.qc", ["x"]),
                "a.qc:1:1: error semantico: m")

    def test_linea_fuera_de_rango_no_falla(self):
        error = ErrorSemantico(50, 1, "m")
        self.assertEqual(
            formatear(error, "a.qc", ["x"]), "a.qc:50:1: error semantico: m")

    def test_reportar_cuenta_e_imprime_resumen(self):
        salida = io.StringIO()
        errores = [ErrorSemantico(1, 1, "uno"), ErrorSemantico(1, 2, "dos")]
        self.assertEqual(reportar(errores, "a.qc", "ab", salida), 2)
        self.assertIn("2 errores semanticos", salida.getvalue())

    def test_reportar_singular(self):
        salida = io.StringIO()
        reportar([ErrorSemantico(1, 1, "uno")], "a.qc", "", salida)
        self.assertIn("1 error semantico\n", salida.getvalue())

    def test_reportar_sin_errores_no_imprime(self):
        salida = io.StringIO()
        self.assertEqual(reportar([], "a.qc", "", salida), 0)
        self.assertEqual(salida.getvalue(), "")

    def test_reportar_respeta_limite(self):
        salida = io.StringIO()
        errores = [ErrorSemantico(i, 1, f"e{i}") for i in range(1, 6)]
        with mock.patch.object(es, "LIMITE_ERRORES", 2):
            self.assertEqual(reportar(errores, "a.qc", "", salida), 5)
        texto = salida.getvalue()
        self.assertIn("e2", texto)
        self.assertNotIn("e3", texto)
        self.assertIn("5 errores semanticos (2 mostrados)", texto)


if __name__ == "__main__":
    unittest.main()
