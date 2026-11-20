"""Pruebas de ambitos y niveles de anidamiento (1.5.2).

Usan verificar_semantica con la tabla de FABRICA_TABLA (la tabla de simbolos
de 1.2).
"""

import unittest

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.analisis import verificar_semantica
from parser.semantica.tabla_simbolos import TablaSimbolos


def verificar(fuente, tabla=None):
    entrada = explorar_para_parser(fuente)
    resultado = Analizador().analizar(entrada.tokens_para_parser())
    assert resultado.correcto, resultado.errores
    return verificar_semantica(resultado.arbol, tabla)


def principal(cuerpo):
    return f"barista chorreador() {{ {cuerpo} }}"


class TablaEspia(TablaSimbolos):
    """Tabla que registra cuantos ambitos se abren a la vez."""

    def __init__(self):
        super().__init__()
        self.entradas = 0
        self.salidas = 0
        self.nivel_maximo = 0

    def entrar(self):
        ambito = super().entrar()
        self.entradas += 1
        self.nivel_maximo = max(self.nivel_maximo, self.nivel)
        return ambito

    def salir(self):
        super().salir()
        self.salidas += 1


class TestVisibilidad(unittest.TestCase):

    def assertSinErrores(self, fuente):
        self.assertEqual([e.mensaje for e in verificar(fuente)], [])

    def assertError(self, fuente, *fragmentos):
        mensajes = [e.mensaje for e in verificar(fuente)]
        self.assertEqual(len(mensajes), len(fragmentos), mensajes)
        for fragmento in fragmentos:
            self.assertTrue(
                any(fragmento in m for m in mensajes), (fragmento, mensajes))

    def test_global_visible_en_funciones_y_principal(self):
        self.assertSinErrores(
            "cafeteria grano g = 1; "
            "barista f() { degustar g; } "
            + principal("grano x = g;"))

    def test_funcion_se_puede_llamar_antes_de_su_declaracion(self):
        self.assertSinErrores(
            "barista f() { degustar g(); } "
            "barista g() { degustar 1; } "
            + principal("grano x = f();"))

    def test_funcion_no_ve_locales_de_otra(self):
        self.assertError(
            "barista f() { grano a = 1; } "
            "barista g() { grano b = a; } "
            + principal(""),
            "'a' no declarado")

    def test_principal_no_ve_locales_de_funciones(self):
        self.assertError(
            "barista f() { grano a = 1; } " + principal("grano b = a;"),
            "'a' no declarado")

    def test_variable_externa_visible_en_bloque_interno(self):
        self.assertSinErrores(principal(
            "grano x = 1; hierve (fuerte) { x = x + 1; }"))

    def test_variable_interna_no_sale_del_bloque(self):
        self.assertError(principal(
            "hierve (fuerte) { grano y = 1; } y = 2;"),
            "'y' no declarado")

    def test_variable_del_hierve_no_visible_en_enfria(self):
        self.assertError(principal(
            "hierve (fuerte) { grano a = 1; } enfria { a = 2; }"),
            "'a' no declarado")

    def test_variable_de_chorreando_no_sale_del_ciclo(self):
        self.assertError(principal(
            "chorreando (ralo) { grano k = 1; } k = 2;"),
            "'k' no declarado")

    def test_variable_usada_antes_de_declararse(self):
        self.assertError(principal("x = 1; grano x = 0;"),
                         "'x' no declarado")

    def test_variable_en_su_propio_inicializador(self):
        self.assertError(principal("grano x = x + 1;"), "'x' no declarado")

    def test_parametro_visible_en_el_cuerpo(self):
        self.assertSinErrores(
            "barista f(grano a, grano b) { degustar a + b; } "
            + principal("grano r = f(1, 2);"))

    def test_parametro_no_sale_de_la_funcion(self):
        self.assertError(
            "barista f(grano a) { degustar a; } " + principal("a = 1;"),
            "'a' no declarado")

    def test_variable_de_recolar_solo_vive_en_el_ciclo(self):
        self.assertError(principal(
            "taza grano xs = [1]; recolar (grano n en xs) { servir(n); } "
            "servir(n);"),
            "'n' no declarado")

    def test_lista_de_recolar_debe_existir(self):
        self.assertError(principal("recolar (grano n en zz) { }"),
                         "'zz' no declarado")

    def test_qubit_no_sale_de_su_bloque(self):
        self.assertError(principal(
            "hierve (fuerte) { qubit q; H(q); } H(q);"),
            "'q' no declarado")


class TestDeclaracionesRepetidas(unittest.TestCase):

    def assertError(self, fuente, *fragmentos):
        mensajes = [e.mensaje for e in verificar(fuente)]
        self.assertEqual(len(mensajes), len(fragmentos), mensajes)
        for fragmento in fragmentos:
            self.assertTrue(any(fragmento in m for m in mensajes), mensajes)

    def test_misma_variable_en_el_mismo_ambito(self):
        self.assertError(principal("grano x = 1; grano x = 2;"),
                         "'x' ya declarado")

    def test_mismo_nombre_con_otro_tipo_tambien_es_repetido(self):
        self.assertError(principal("grano x = 1; poso x = 2.5;"),
                         "'x' ya declarado")

    def test_variable_y_qubit_con_el_mismo_nombre(self):
        self.assertError(principal("grano q = 1; qubit q;"),
                         "'q' ya declarado")

    def test_parametros_repetidos(self):
        self.assertError(
            "barista f(grano a, grano a) { } " + principal(""),
            "'a' ya declarado")

    def test_funciones_repetidas(self):
        self.assertError(
            "barista f() { } barista f() { } " + principal(""),
            "'f' ya declarado")

    def test_globales_repetidas(self):
        self.assertError(
            "cafeteria grano g = 1; cafeteria grano g = 2; " + principal(""),
            "'g' ya declarado")

    def test_global_y_funcion_con_el_mismo_nombre(self):
        self.assertError(
            "cafeteria grano f = 1; barista f() { } " + principal(""),
            "'f' ya declarado")

    def test_repetida_dentro_de_bloque_anidado(self):
        self.assertError(principal(
            "hierve (fuerte) { grano y = 1; grano y = 2; }"),
            "'y' ya declarado")


class TestSombreado(unittest.TestCase):

    def test_bloque_interno_puede_redeclarar_un_nombre_externo(self):
        errores = verificar(principal(
            "grano x = 1; hierve (fuerte) { grano x = 2; x = 3; } x = 4;"))
        self.assertEqual(errores, [])

    def test_sombra_de_otro_tipo_usa_el_tipo_interno(self):
        errores = verificar(principal(
            "grano x = 1; hierve (fuerte) { granoMolido x = \"a\"; }"))
        self.assertEqual(errores, [])

    def test_sombra_de_otro_tipo_revisa_con_el_tipo_interno(self):
        errores = verificar(principal(
            "grano x = 1; hierve (fuerte) { granoMolido x = 5; }"))
        self.assertEqual(len(errores), 1)
        self.assertIn("no se puede asignar", errores[0].mensaje)

    def test_local_puede_tener_el_nombre_de_una_global(self):
        errores = verificar(
            "cafeteria grano g = 1; " + principal("granoMolido g = \"a\";"))
        self.assertEqual(errores, [])

    def test_variable_de_recolar_puede_sombrear_una_externa(self):
        errores = verificar(principal(
            "grano n = 0; taza grano xs = [1]; "
            "recolar (grano n en xs) { servir(n); } n = 5;"))
        self.assertEqual(errores, [])

    def test_mismo_nombre_en_bloques_hermanos(self):
        errores = verificar(principal(
            "hierve (fuerte) { grano t = 1; } enfria { grano t = 2; } "
            "chorreando (ralo) { grano t = 3; }"))
        self.assertEqual(errores, [])

    def test_mismo_nombre_en_funciones_distintas(self):
        errores = verificar(
            "barista f(grano a) { degustar a; } "
            "barista g(grano a) { degustar a; } " + principal(""))
        self.assertEqual(errores, [])


class TestNiveles(unittest.TestCase):

    def test_cuatro_niveles_de_anidamiento(self):
        fuente = principal(
            "grano n1 = 1; "
            "hierve (fuerte) { grano n2 = n1; "
            " chorreando (ralo) { grano n3 = n2; "
            "  taza grano xs = [1]; "
            "  recolar (grano n4 en xs) { grano suma = n1 + n2 + n3 + n4; } "
            " } "
            "}")
        self.assertEqual(verificar(fuente), [])

    def test_nivel_exterior_no_ve_el_interior_en_cuatro_niveles(self):
        fuente = principal(
            "hierve (fuerte) { "
            " chorreando (ralo) { "
            "  hierve (fuerte) { grano hondo = 1; } "
            "  hondo = 2; "
            " } "
            "}")
        errores = verificar(fuente)
        self.assertEqual(len(errores), 1)
        self.assertIn("'hondo' no declarado", errores[0].mensaje)

    def test_niveles_se_abren_y_cierran_en_pareja(self):
        tabla = TablaEspia()
        verificar(
            "barista f(grano a) { hierve (fuerte) { grano b = a; } } "
            + principal(
                "taza grano xs = [1]; "
                "recolar (grano n en xs) { hierve (fuerte) { servir(n); } }"),
            tabla)
        self.assertEqual(tabla.entradas, tabla.salidas)
        self.assertEqual(tabla.nivel, 0)

    def test_nivel_maximo_de_una_funcion_con_bloques_anidados(self):
        # Funcion (1) -> bloque (2) -> hierve (3) -> chorreando (4).
        tabla = TablaEspia()
        verificar(
            "barista f(grano a) { hierve (fuerte) { "
            "chorreando (ralo) { grano b = a; } } } " + principal(""),
            tabla)
        self.assertEqual(tabla.nivel_maximo, 4)

    def test_nivel_maximo_de_recolar(self):
        # Principal (sin ambito) -> bloque (1) -> recolar (2) -> bloque (3).
        tabla = TablaEspia()
        verificar(principal(
            "taza grano xs = [1]; recolar (grano n en xs) { servir(n); }"),
            tabla)
        self.assertEqual(tabla.nivel_maximo, 3)

    def test_tabla_vuelve_al_nivel_global_aun_con_errores(self):
        tabla = TablaEspia()
        errores = verificar(principal(
            "hierve (fuerte) { grano a = 1; grano a = 2; w = 1; }"), tabla)
        self.assertEqual(len(errores), 2)
        self.assertEqual(tabla.nivel, 0)


class TestLimitesConocidos(unittest.TestCase):
    """Huecos detectados en la verificacion actual (ver Registro_de_defectos).

    Estan marcados como fallo esperado: cuando se corrijan, la suite avisara
    con un exito inesperado y habra que quitar el decorador.
    """

    @unittest.expectedFailure
    def test_funcion_usada_como_variable(self):
        errores = verificar(
            "barista f() { degustar 1; } " + principal("grano x = f;"))
        self.assertTrue(errores)

    @unittest.expectedFailure
    def test_asignar_a_una_funcion(self):
        errores = verificar(
            "barista f() { degustar 1; } " + principal("f = 3;"))
        self.assertTrue(errores)


class TestLimitesCorregidos(unittest.TestCase):
    """Antes era fallo esperado; lo corrige la tabla de simbolos (1.2.2)."""

    def test_parametro_redeclarado_en_el_cuerpo(self):
        errores = verificar(
            "barista f(grano a) { grano a = 1; } " + principal(""))
        self.assertEqual(len(errores), 1)
        self.assertIn("'a' ya declarado", errores[0].mensaje)


if __name__ == "__main__":
    unittest.main()
