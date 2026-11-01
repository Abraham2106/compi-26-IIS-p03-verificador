"""Pruebas del nucleo del parser, sin las producciones de 4.0.

`conectar_prueba` reemplaza a las producciones de la tarea 4.0 con versiones
minimas, solo para poder analizar programas completos. La conexion real con
`ProduccionesControl` y `ProduccionesCuanticas` es la actividad 4.4.
"""

import unittest

from parser.analizador import Analisis, Analizador
from parser.asa_constructores import rango_entre
from parser.errores_sintacticos import FalloSintactico
from parser.integracion import ClaseNodo, NodoASA, explorar_para_parser
from scanner import TokenType as T


def conectar_prueba(analisis: Analisis) -> None:
    control = analisis.control

    def bloque():
        abre = control.esperar(T.LLAVE_ABRE, contexto="bloque")
        hijos = []
        while control.flujo.mirar().tipo not in (T.LLAVE_CIERRA,
                                                 T.FIN_ARCHIVO):
            try:
                hijos.append(analisis.sentencia())
            except FalloSintactico:
                control.sincronizar(consumir_punto_coma=True)
        cierra = control.esperar(T.LLAVE_CIERRA, contexto="bloque")
        return NodoASA(ClaseNodo.BLOQUE, rango_entre(abre, cierra), {},
                       tuple(hijos))

    def principal():
        abre = control.esperar(T.BARISTA)
        control.esperar(T.CHORREADOR)
        control.esperar(T.PARENTESIS_ABRE)
        control.esperar(T.PARENTESIS_CIERRA)
        cuerpo = bloque()
        return NodoASA(ClaseNodo.PRINCIPAL, rango_entre(abre, cuerpo),
                       {"nombre": "chorreador"}, (cuerpo,))

    def funcion():
        abre = control.esperar(T.BARISTA)
        nombre = control.esperar(T.IDENTIFICADOR)
        control.esperar(T.PARENTESIS_ABRE)
        parametros = []
        while control.flujo.mirar().tipo != T.PARENTESIS_CIERRA:
            inicio = control.flujo.mirar()
            tipo = analisis.tipo()
            ident = control.esperar(T.IDENTIFICADOR)
            parametros.append(NodoASA(
                ClaseNodo.PARAMETRO, rango_entre(inicio, ident),
                {"nombre": ident.lexema, "tipo": tipo}))
            if control.flujo.mirar().tipo == T.COMA:
                control.flujo.avanzar()
        control.esperar(T.PARENTESIS_CIERRA)
        cuerpo = bloque()
        return NodoASA(ClaseNodo.FUNCION, rango_entre(abre, cuerpo),
                       {"nombre": nombre.lexema},
                       tuple(parametros) + (cuerpo,))

    def medicion():
        abre = control.esperar(T.MEDIR)
        control.esperar(T.PARENTESIS_ABRE)
        q = control.esperar(T.IDENTIFICADOR)
        cierra = control.esperar(T.PARENTESIS_CIERRA)
        hoja = NodoASA(ClaseNodo.IDENTIFICADOR, rango_entre(q, q),
                       {"nombre": q.lexema})
        return NodoASA(ClaseNodo.MEDICION, rango_entre(abre, cierra), {},
                       (hoja,))

    analisis.registrar_principal(principal)
    analisis.registrar_funcion(funcion)
    analisis.registrar_medicion(medicion)


def analizador():
    return Analizador(conectar_prueba)


def parsear(fuente):
    entrada = explorar_para_parser(fuente)
    assert entrada.apta, entrada.errores_lexicos
    return analizador().analizar(entrada.tokens_para_parser())


def en_main(cuerpo):
    return "barista chorreador() {\n" + cuerpo + "\n}"


def sexp(nodo):
    """Forma compacta: (Clase contenido hijos...)."""
    a = nodo.atributos
    if nodo.clase == ClaseNodo.LITERAL:
        return a["lexema"]
    if nodo.clase == ClaseNodo.IDENTIFICADOR:
        return a["nombre"]
    clave = a.get("operador") or a.get("nombre") or a.get("metodo") \
        or a.get("compuerta") or ""
    partes = [nodo.clase.value + (f":{clave}" if clave else "")]
    partes += [sexp(h) for h in nodo.hijos]
    return "(" + " ".join(partes) + ")"


def expresion(texto):
    """Parsea `grano x = <texto>;` y devuelve el sexp de la expresion."""
    resultado = parsear(en_main(f"grano x = {texto};"))
    assert resultado.correcto, resultado.errores
    local = resultado.arbol.hijos[-1].hijos[0].hijos[0]
    return sexp(local.hijos[0])


class TestPrograma(unittest.TestCase):
    def test_programa_minimo(self):
        resultado = parsear("barista chorreador() {}")
        self.assertTrue(resultado.correcto)
        self.assertEqual(
            sexp(resultado.arbol),
            "(Programa (FuncionPrincipal:chorreador (Bloque)))")

    def test_rango_de_la_raiz(self):
        fuente = "cafeteria grano a;\nbarista chorreador() {\n}"
        r = parsear(fuente).arbol.rango
        self.assertEqual((r.inicio.linea, r.inicio.columna), (1, 1))
        self.assertEqual((r.fin.linea, r.fin.columna), (3, 2))


class TestExpresiones(unittest.TestCase):
    def test_precedencia_multiplicacion_sobre_suma(self):
        self.assertEqual(
            expresion("2 + 3 * 4"), "(Binaria:+ 2 (Binaria:* 3 4))")

    def test_asociatividad_izquierda(self):
        self.assertEqual(
            expresion("10 - 3 - 2"), "(Binaria:- (Binaria:- 10 3) 2)")
        self.assertEqual(
            expresion("8 / 4 % 3"), "(Binaria:% (Binaria:/ 8 4) 3)")

    def test_parentesis_agrupan_sin_crear_nodo(self):
        self.assertEqual(
            expresion("(2 + 3) * 4"), "(Binaria:* (Binaria:+ 2 3) 4)")

    def test_parentesis_amplian_el_rango(self):
        resultado = parsear(en_main("grano x = (1 + 2);"))
        binaria = resultado.arbol.hijos[0].hijos[0].hijos[0].hijos[0]
        self.assertEqual(binaria.rango.inicio.columna, 11)
        self.assertEqual(binaria.rango.fin.columna, 18)

    def test_signos_unarios_de_derecha_a_izquierda(self):
        self.assertEqual(expresion("-+5"), "(Unaria:- (Unaria:+ 5))")
        self.assertEqual(
            expresion("-(a + b)"), "(Unaria:- (Binaria:+ a b))")

    def test_amargo_tiene_menor_precedencia_que_comparacion(self):
        self.assertEqual(
            expresion("Amargo a < b"), "(Unaria:Amargo (Binaria:< a b))")
        self.assertEqual(
            expresion("Amargo Amargo a"),
            "(Unaria:Amargo (Unaria:Amargo a))")

    def test_conectores_logicos(self):
        self.assertEqual(
            expresion("a SinAzucar b ConAzucar c"),
            "(Binaria:SinAzucar a (Binaria:ConAzucar b c))")
        self.assertEqual(
            expresion("a ConAzucar b ConAzucar c"),
            "(Binaria:ConAzucar (Binaria:ConAzucar a b) c)")

    def test_relacional_entre_aritmeticas(self):
        self.assertEqual(
            expresion("a + 1 >= b * 2"),
            "(Binaria:>= (Binaria:+ a 1) (Binaria:* b 2))")

    def test_literales_conservan_su_lexema(self):
        self.assertEqual(expresion("00012"), "00012")
        self.assertEqual(expresion("01.50"), "01.50")
        self.assertEqual(expresion('"hola # no"'), '"hola # no"')
        for lexema in ("fuerte", "ralo", "descafeinado", "SeQuemoElCafe"):
            self.assertEqual(expresion(lexema), lexema)

    def test_llamadas_y_listas(self):
        self.assertEqual(expresion("f()"), "(Llamada:f)")
        self.assertEqual(
            expresion("f(1, g(2), [])"),
            "(Llamada:f 1 (Llamada:g 2) (Lista))")
        self.assertEqual(expresion("[1, [2, 3]]"), "(Lista 1 (Lista 2 3))")
        self.assertEqual(expresion("m.buscar(1 + 2)"),
                         "(OperacionLista:buscar (Binaria:+ 1 2))")

    def test_medicion_como_factor(self):
        self.assertEqual(expresion("medir(q)"), "(Medicion q)")

    def test_comparacion_encadenada_es_error(self):
        resultado = parsear(en_main("grano x = a < b < c;"))
        self.assertFalse(resultado.correcto)
        self.assertIn("encadenadas", resultado.errores[0].mensaje)


class TestDeclaracionesYSentencias(unittest.TestCase):
    def test_tipos_anidados(self):
        resultado = parsear(en_main("taza taza grano m = [[1], [2]];"))
        local = resultado.arbol.hijos[0].hijos[0].hijos[0]
        self.assertEqual(local.atributos["tipo"], "taza taza grano")

    def test_declaracion_sin_valor(self):
        resultado = parsear("cafeteria poso p;\nbarista chorreador() {}")
        self.assertTrue(resultado.correcto)
        self.assertEqual(resultado.arbol.hijos[0].hijos, ())

    def test_asignacion_llamada_y_metodo_como_sentencia(self):
        resultado = parsear(en_main("x = 1; servir(x); l.insertar(3);"))
        self.assertTrue(resultado.correcto, resultado.errores)
        clases = [h.clase for h in resultado.arbol.hijos[0].hijos[0].hijos]
        self.assertEqual(clases, [ClaseNodo.ASIGNACION, ClaseNodo.LLAMADA,
                                  ClaseNodo.OPERACION_LISTA])

    def test_rango_de_sentencia_incluye_punto_y_coma(self):
        resultado = parsear(en_main("servir(1);"))
        llamada = resultado.arbol.hijos[0].hijos[0].hijos[0]
        self.assertEqual(llamada.rango.fin.columna, 11)

    def test_retorno_con_y_sin_valor(self):
        resultado = parsear(
            "barista f() { degustar; degustar 1 + 2; }\n"
            "barista chorreador() {}")
        self.assertTrue(resultado.correcto, resultado.errores)
        bloque = resultado.arbol.hijos[0].hijos[0]
        self.assertEqual([len(h.hijos) for h in bloque.hijos], [0, 1])

    def test_funcion_con_parametros_y_funciones_antes_de_main(self):
        resultado = parsear(
            "barista f(taza grano a, cafe b) { }\n"
            "cafeteria grano g = 1;\n"
            "barista h() { }\n"
            "barista chorreador() { }")
        self.assertTrue(resultado.correcto, resultado.errores)
        clases = [h.clase for h in resultado.arbol.hijos]
        self.assertEqual(clases, [ClaseNodo.FUNCION, ClaseNodo.GLOBAL,
                                  ClaseNodo.FUNCION, ClaseNodo.PRINCIPAL])
        params = resultado.arbol.hijos[0].hijos[:2]
        tipos = [p.atributos["tipo"] for p in params]
        self.assertEqual(tipos, ["taza grano", "cafe"])


class TestErrores(unittest.TestCase):
    def errores(self, fuente):
        resultado = parsear(fuente)
        self.assertFalse(resultado.correcto)
        return resultado.errores

    def test_falta_punto_y_coma(self):
        err = self.errores(en_main("grano x = 1\ngrano y = 2;"))[0]
        self.assertEqual(err.encontrado.lexema, "grano")
        self.assertEqual(err.encontrado.linea, 3)
        self.assertEqual(err.esperados, (T.PUNTO_COMA,))

    def test_declaracion_sin_valor_sugiere_asignacion(self):
        err = self.errores(en_main("grano x grano y;"))[0]
        self.assertIn(T.ASIGNACION, err.esperados)

    def test_falta_la_funcion_principal(self):
        err = self.errores("cafeteria grano a = 1;")[0]
        self.assertIn("chorreador", err.mensaje)
        self.assertEqual(err.encontrado.tipo, T.FIN_ARCHIVO)

    def test_programa_vacio(self):
        err = self.errores("")[0]
        self.assertIn("chorreador", err.mensaje)

    def test_codigo_despues_del_main(self):
        err = self.errores(
            "barista chorreador() {}\ncafeteria grano a;")[0]
        self.assertIn("no puede haber mas codigo", err.mensaje)
        self.assertEqual(err.encontrado.linea, 2)

    def test_dos_main(self):
        self.errores("barista chorreador() {}\nbarista chorreador() {}")

    def test_barista_sin_nombre(self):
        err = self.errores("barista 5() {}\nbarista chorreador() {}")[0]
        self.assertEqual(err.encontrado.lexema, "5")

    def test_main_con_parametros_es_error(self):
        err = self.errores("barista chorreador(grano a) {}")[0]
        self.assertEqual(err.esperados, (T.PARENTESIS_CIERRA,))

    def test_identificador_aislado_no_es_sentencia(self):
        err = self.errores(en_main("x;"))[0]
        self.assertEqual(
            err.esperados,
            (T.ASIGNACION, T.PARENTESIS_ABRE, T.PUNTO))

    def test_asignacion_no_es_expresion(self):
        self.errores(en_main("grano y = x = 1;"))

    def test_parentesis_sin_cerrar(self):
        err = self.errores(en_main("grano x = (1 + 2;"))[0]
        self.assertEqual(err.esperados, (T.PARENTESIS_CIERRA,))

    def test_expresion_faltante(self):
        err = self.errores(en_main("grano x = ;"))[0]
        self.assertEqual(err.encontrado.tipo, T.PUNTO_COMA)
        self.assertIn(T.ENTERO, err.esperados)

    def test_bloque_sin_cerrar(self):
        err = self.errores("barista chorreador() { grano x = 1;")[0]
        self.assertEqual(err.encontrado.tipo, T.FIN_ARCHIVO)

    def test_metodo_de_lista_desconocido(self):
        err = self.errores(en_main("l.borrar(1);"))[0]
        self.assertIn(T.INSERTAR, err.esperados)

    def test_varios_errores_en_una_pasada(self):
        fuente = en_main("grano a = ;\ngrano b = 2;\nx;\nservir(b);")
        errores = self.errores(fuente)
        self.assertEqual([e.encontrado.linea for e in errores], [2, 4])

    def test_recuperacion_en_funciones_de_nivel_superior(self):
        fuente = ("barista f( { }\n"
                  "barista g() { grano x = ; }\n"
                  "barista chorreador() {}")
        errores = self.errores(fuente)
        self.assertEqual([e.encontrado.linea for e in errores], [1, 2])

    def test_un_arbol_con_errores_nunca_es_correcto(self):
        entrada = explorar_para_parser(en_main("grano a = ;"))
        resultado = analizador().analizar(entrada.tokens_para_parser())
        self.assertFalse(resultado.correcto)


class TestConexionPendiente(unittest.TestCase):
    """Sin las producciones de 4.0 el nucleo lo dice, no falla en silencio."""

    def test_construccion_sin_conectar_se_informa(self):
        entrada = explorar_para_parser(
            "barista chorreador() { hierve (fuerte) { } }")
        resultado = Analizador(lambda analisis: None).analizar(
            entrada.tokens_para_parser())
        self.assertFalse(resultado.correcto)
        self.assertIn("no esta conectada", resultado.errores[0].mensaje)

    def test_una_sentencia_registrada_se_usa(self):
        def conectar(analisis):
            conectar_prueba(analisis)

            def hierve():
                token = analisis.control.esperar(T.HIERVE)
                analisis.control.esperar(T.PUNTO_COMA)
                return NodoASA(ClaseNodo.BLOQUE, rango_entre(token, token))

            analisis.registrar_sentencia(T.HIERVE, hierve)

        entrada = explorar_para_parser("barista chorreador() { hierve; }")
        resultado = Analizador(conectar).analizar(
            entrada.tokens_para_parser())
        self.assertTrue(resultado.correcto, resultado.errores)


class TestRobustez(unittest.TestCase):
    """Ninguna entrada rota debe colgar el parser ni lanzar excepciones."""

    FUENTE = (
        "cafeteria grano g = 1;\n"
        "barista f(taza grano a, cafe b) { degustar a.buscar(1); }\n"
        "barista chorreador() {\n"
        "    taza grano l = [1, -2 * (3 + g)];\n"
        "    l.insertar(f(l, Amargo b SinAzucar b ConAzucar fuerte));\n"
        "    x = medir(q) >= 2;\n"
        "}\n"
    )

    def analizar(self, tokens):
        return analizador().analizar(tokens)

    def test_cualquier_prefijo_termina_y_es_rechazado(self):
        entrada = explorar_para_parser(self.FUENTE)
        tokens = list(entrada.tokens_para_parser())
        eof = tokens[-1]
        for n in range(len(tokens) - 1):
            with self.subTest(n=n):
                resultado = self.analizar(tuple(tokens[:n]) + (eof,))
                self.assertFalse(resultado.correcto)

    def test_borrar_un_token_termina_sin_excepciones(self):
        entrada = explorar_para_parser(self.FUENTE)
        tokens = list(entrada.tokens_para_parser())
        for i in range(len(tokens) - 1):
            with self.subTest(i=i):
                self.analizar(tuple(tokens[:i] + tokens[i + 1:]))


if __name__ == "__main__":
    unittest.main()
