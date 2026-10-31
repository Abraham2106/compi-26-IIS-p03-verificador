import json
import unittest
from pathlib import Path

from parser.asa_constructores import (agrupar, como_sentencia, con_hijo,
                                      crear_asignacion, crear_binaria,
                                      crear_declaracion, crear_identificador,
                                      crear_literal, crear_llamada,
                                      crear_unaria, desde_dict)
from parser.asa_impresion import (a_texto, formatear_nodo, lineas_preorden,
                                  recorrer_preorden)
from parser.integracion import ClaseNodo, explorar_para_parser

RAIZ = Path(__file__).resolve().parents[2]


def tokens(fuente):
    return list(explorar_para_parser(fuente).tokens_para_parser())


class TestConstructores(unittest.TestCase):
    def test_binaria_conserva_lexemas_y_rango(self):
        t = tokens("a + 10")
        nodo = crear_binaria(crear_identificador(t[0]), t[1], crear_literal(t[2]))
        self.assertEqual(nodo.clase, ClaseNodo.BINARIA)
        self.assertEqual(nodo.atributos["operador"], "+")
        self.assertEqual((nodo.rango.inicio.columna, nodo.rango.fin.columna), (1, 7))
        self.assertEqual(nodo.hijos[1].atributos["lexema"], "10")

    def test_literal_no_convierte_valores(self):
        for fuente, categoria in (("00012", "ENTERO"), ("01.50", "DECIMAL"),
                                  ('"hola"', "CADENA"), ("fuerte", "FUERTE")):
            nodo = crear_literal(tokens(fuente)[0])
            self.assertEqual(nodo.atributos["lexema"], fuente)
            self.assertEqual(nodo.atributos["categoria"], categoria)

    def test_declaracion_y_asignacion_incluyen_punto_coma(self):
        t = tokens("grano x = 5 ;")
        decl = crear_declaracion(ClaseNodo.LOCAL, "grano", t[1],
                                 crear_literal(t[3]), t[0], t[4])
        self.assertEqual(decl.rango.fin.columna, 14)
        t = tokens("x = 5 ;")
        asig = crear_asignacion(t[0], crear_literal(t[2]), t[3])
        self.assertEqual(asig.rango.fin.columna, 8)

    def test_declaracion_rechaza_clase_incorrecta(self):
        t = tokens("grano x ;")
        with self.assertRaises(ValueError):
            crear_declaracion(ClaseNodo.BLOQUE, "grano", t[1], None, t[0], t[2])

    def test_llamada_sin_argumentos_y_como_sentencia(self):
        t = tokens("f() ;")
        llamada = crear_llamada(t[0], [], t[2])
        self.assertEqual(llamada.hijos, ())
        self.assertEqual(como_sentencia(llamada, t[3]).rango.fin.columna, 6)

    def test_agrupar_no_crea_nodo(self):
        t = tokens("(a)")
        nodo = agrupar(crear_identificador(t[1]), t[0], t[2])
        self.assertEqual(nodo.clase, ClaseNodo.IDENTIFICADOR)
        self.assertEqual((nodo.rango.inicio.columna, nodo.rango.fin.columna), (1, 4))

    def test_con_hijo_inserta_sin_mutar(self):
        t = tokens("-a")
        unaria = crear_unaria(t[0], crear_identificador(t[1]))
        otro = crear_identificador(t[1])
        nuevo = con_hijo(unaria, otro, 0)
        self.assertEqual(len(unaria.hijos), 1)
        self.assertEqual(len(nuevo.hijos), 2)
        self.assertIs(nuevo.hijos[0], otro)


class TestImpresion(unittest.TestCase):
    def test_preorden_hijos_izquierda_a_derecha(self):
        t = tokens("a + b * c")
        mult = crear_binaria(crear_identificador(t[2]), t[3], crear_identificador(t[4]))
        raiz = crear_binaria(crear_identificador(t[0]), t[1], mult)
        orden = [nodo.atributos.get("nombre") or nodo.atributos["operador"]
                 for _, nodo in recorrer_preorden(raiz)]
        self.assertEqual(orden, ["+", "a", "*", "b", "c"])

    def test_formato_y_escape_de_comillas(self):
        nodo = crear_literal(tokens('"hola"')[0])
        self.assertEqual(formatear_nodo(nodo),
                         '<"Literal", "\\"hola\\"", "categoria=CADENA">')

    def test_un_nodo_por_linea_y_sangria(self):
        t = tokens("-a")
        raiz = crear_unaria(t[0], crear_identificador(t[1]))
        self.assertEqual(lineas_preorden(raiz), [
            '<"Unaria", "-", "">',
            '  <"Identificador", "a", "">',
        ])
        self.assertEqual(lineas_preorden(raiz, sangria=None)[1],
                         '<"Identificador", "a", "">')

    def test_con_rango_opcional(self):
        nodo = crear_identificador(tokens("abc")[0])
        self.assertIn("rango=1:1-1:4", formatear_nodo(nodo, con_rango=True))

    def test_arbol_muy_profundo_no_desborda_recursion(self):
        t = tokens("-a")
        nodo = crear_identificador(t[1])
        for _ in range(3000):
            nodo = crear_unaria(t[0], nodo)
        self.assertEqual(len(a_texto(nodo).splitlines()), 3001)

    def test_json_de_referencia_se_imprime(self):
        datos = json.loads((RAIZ / "docs" / "asa_referencia.json").read_text("utf-8"))
        raiz = desde_dict(datos)
        self.assertEqual(raiz.a_dict(), datos)
        lineas = lineas_preorden(raiz, sangria=None)
        self.assertEqual(lineas[0], '<"Programa", "", "">')
        self.assertEqual(lineas[1], '<"FuncionPrincipal", "chorreador", "">')
        self.assertEqual(lineas[3], '<"DeclaracionLocal", "x", "tipo=grano">')


if __name__ == "__main__":
    unittest.main()
