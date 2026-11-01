import difflib
import importlib
import unittest
from pathlib import Path

from parser.asa_impresion import a_texto, recorrer_preorden
from parser.integracion import explorar_para_parser
from parser.verificacion.asa_manual import asa_manual

AQUI = Path(__file__).resolve().parent
PROGRAMA = AQUI.parent / "ejemplos_completos" / "08_asa_manual.qc"
ESPERADO = AQUI / "esperados" / "08_asa_manual.preorden.txt"

MODULO_PARSER = "parser.analizador"
CLASE_PARSER = "Analizador"


def comparar(esperado: str, generado: str) -> str:
    """Diferencias linea por linea (vacio si coinciden)."""
    return "".join(difflib.unified_diff(
        esperado.splitlines(True), generado.splitlines(True),
        "esperado", "generado"))


class TestAsaManual(unittest.TestCase):
    def test_preorden_manual_coincide_con_esperado(self):
        esperado = ESPERADO.read_text("utf-8")
        self.assertEqual(comparar(esperado, a_texto(asa_manual())), "")

    def test_rangos_consistentes(self):
        for _, nodo in recorrer_preorden(asa_manual()):
            anterior = None
            for hijo in nodo.hijos:
                self.assertLessEqual(
                    nodo.rango.inicio, hijo.rango.inicio, nodo.clase)
                self.assertLessEqual(
                    hijo.rango.fin, nodo.rango.fin, nodo.clase)
                if anterior is not None:
                    self.assertLessEqual(anterior.rango.fin, hijo.rango.inicio)
                anterior = hijo

    def test_rango_de_hojas_coincide_con_tokens_del_scanner(self):
        tokens = explorar_para_parser(
            PROGRAMA.read_text("utf-8")).tokens_para_parser()
        posiciones = {(t.linea, t.columna, t.columna + len(t.lexema)): t.lexema
                      for t in tokens}
        hojas = [n for _, n in recorrer_preorden(asa_manual())
                 if n.clase.value in ("Identificador", "Literal")]
        self.assertTrue(hojas)
        for hoja in hojas:
            r = hoja.rango
            lexema = posiciones.get(
                (r.inicio.linea, r.inicio.columna, r.fin.columna))
            self.assertEqual(lexema, hoja.atributos.get(
                "lexema", hoja.atributos.get("nombre")))

    def test_programa_manual_no_tiene_errores_lexicos(self):
        self.assertTrue(explorar_para_parser(PROGRAMA.read_text("utf-8")).apta)


def _cargar_parser():
    modulo = importlib.import_module(MODULO_PARSER)
    return getattr(modulo, CLASE_PARSER)()


def _analizar_programa():
    entrada = explorar_para_parser(PROGRAMA.read_text("utf-8"))
    return _cargar_parser().analizar(entrada.tokens_para_parser())


class TestParserContraManual(unittest.TestCase):
    """6.4: ASA manual (referencia) contra el generado por el parser real."""

    def test_preorden_generado_igual_al_manual(self):
        resultado = _analizar_programa()
        self.assertTrue(resultado.correcto, resultado.errores)
        esperado = ESPERADO.read_text("utf-8")
        self.assertEqual(comparar(esperado, a_texto(resultado.arbol)), "")

    def test_arbol_generado_igual_al_manual_con_rangos(self):
        resultado = _analizar_programa()
        self.assertTrue(resultado.correcto, resultado.errores)
        self.assertEqual(resultado.arbol.a_dict(), asa_manual().a_dict())

    def test_error_si_se_altera_un_nodo(self):
        """Control negativo: la comparacion detecta una diferencia real."""
        resultado = _analizar_programa()
        alterado = a_texto(resultado.arbol).replace('"Binaria", "+"', '"Binaria", "-"', 1)
        self.assertNotEqual(comparar(ESPERADO.read_text("utf-8"), alterado), "")


if __name__ == "__main__":
    unittest.main()
