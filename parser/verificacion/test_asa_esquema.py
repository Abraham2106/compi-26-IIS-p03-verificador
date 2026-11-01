"""Pruebas del esquema del ASA."""

import unittest

from parser.asa_esquema import ESQUEMA, problemas_nodo, validar_arbol
from parser.integracion import ClaseNodo as C, NodoASA, Posicion, RangoFuente
from parser.verificacion.asa_manual import asa_manual

R = RangoFuente(Posicion(1, 1), Posicion(1, 2))


def nodo(clase, atributos=None, *hijos):
    return NodoASA(clase, R, atributos or {}, hijos)


def ident(nombre="x"):
    return nodo(C.IDENTIFICADOR, {"nombre": nombre})


def literal(lexema="1", categoria="ENTERO"):
    return nodo(C.LITERAL, {"categoria": categoria, "lexema": lexema})


def programa(*sentencias):
    principal = nodo(
        C.PRINCIPAL, {"nombre": "chorreador"}, nodo(C.BLOQUE, {}, *sentencias)
    )
    return nodo(C.PROGRAMA, {}, principal)


class TestEsquema(unittest.TestCase):
    def test_todas_las_clases_tienen_esquema(self):
        self.assertEqual(set(ESQUEMA), set(C))

    def test_arbol_manual_es_valido(self):
        self.assertEqual(validar_arbol(asa_manual()), [])

    def test_raiz_debe_ser_programa(self):
        self.assertTrue(validar_arbol(ident()))

    def test_atributo_faltante_o_sobrante(self):
        self.assertTrue(problemas_nodo(nodo(C.IDENTIFICADOR)))
        self.assertTrue(
            problemas_nodo(nodo(C.IDENTIFICADOR, {"nombre": "x", "otro": "y"}))
        )

    def test_binaria_requiere_dos_hijos(self):
        self.assertTrue(
            problemas_nodo(nodo(C.BINARIA, {"operador": "+"}, literal()))
        )
        self.assertEqual(
            problemas_nodo(
                nodo(C.BINARIA, {"operador": "+"}, literal(), literal())
            ),
            [],
        )

    def test_operador_invalido(self):
        self.assertTrue(
            problemas_nodo(
                nodo(C.BINARIA, {"operador": "**"}, literal(), literal())
            )
        )
        self.assertTrue(
            problemas_nodo(nodo(C.UNARIA, {"operador": "*"}, literal()))
        )

    def test_tipo_debe_ser_canonico(self):
        malo = nodo(C.LOCAL, {"nombre": "a", "tipo": "taza"})
        bueno = nodo(C.LOCAL, {"nombre": "a", "tipo": "taza taza grano"})
        self.assertTrue(problemas_nodo(malo))
        self.assertEqual(problemas_nodo(bueno), [])

    def test_condicional_acepta_uno_o_dos_bloques(self):
        b = nodo(C.BLOQUE)
        self.assertEqual(
            problemas_nodo(nodo(C.CONDICIONAL, {}, ident(), b)), []
        )
        self.assertEqual(
            problemas_nodo(nodo(C.CONDICIONAL, {}, ident(), b, b)), []
        )
        self.assertTrue(
            problemas_nodo(nodo(C.CONDICIONAL, {}, ident(), b, b, b))
        )
        self.assertTrue(problemas_nodo(nodo(C.CONDICIONAL, {}, b)))

    def test_funcion_parametros_y_luego_bloque(self):
        p = nodo(C.PARAMETRO, {"nombre": "a", "tipo": "grano"})
        b = nodo(C.BLOQUE)
        self.assertEqual(
            problemas_nodo(nodo(C.FUNCION, {"nombre": "f"}, p, p, b)), []
        )
        self.assertTrue(problemas_nodo(nodo(C.FUNCION, {"nombre": "f"}, b, p)))

    def test_compuertas(self):
        self.assertEqual(
            problemas_nodo(nodo(C.COMPUERTA, {"compuerta": "H"}, ident("q"))),
            [],
        )
        self.assertEqual(
            problemas_nodo(
                nodo(
                    C.COMPUERTA, {"compuerta": "CNOT"}, ident("a"), ident("b")
                )
            ),
            [],
        )
        self.assertTrue(
            problemas_nodo(
                nodo(C.COMPUERTA, {"compuerta": "CNOT"}, ident("a"))
            )
        )
        self.assertTrue(
            problemas_nodo(nodo(C.COMPUERTA, {"compuerta": "Y"}, ident("a")))
        )

    def test_una_declaracion_no_puede_estar_en_un_bloque(self):
        glob = nodo(C.GLOBAL, {"nombre": "a", "tipo": "grano"})
        self.assertTrue(validar_arbol(programa(glob)))

    def test_el_problema_indica_la_ruta(self):
        mala = nodo(C.ASIGNACION, {"nombre": "a"})
        mensajes = validar_arbol(programa(mala))
        self.assertTrue(any("Asignacion[0]" in m for m in mensajes))


if __name__ == "__main__":
    unittest.main()
