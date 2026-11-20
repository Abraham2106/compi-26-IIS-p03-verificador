"""Pruebas de la tabla de simbolos (1.2.1, 1.2.2, 1.2.3)."""

import unittest

from parser.analizador import Analizador
from parser.integracion import (
    ClaseNodo, NodoASA, Posicion, RangoFuente, explorar_para_parser,
)
from parser.semantica.analisis import verificar_semantica
from parser.semantica.tabla_simbolos import Categoria, TablaSimbolos


def nodo(clase, nombre, tipo=None, linea=1, columna=1):
    atributos = {"nombre": nombre}
    if tipo is not None:
        atributos["tipo"] = tipo
    rango = RangoFuente(Posicion(linea, columna), Posicion(linea, columna + 1))
    return NodoASA(clase, rango, atributos)


def local(nombre, tipo="grano", linea=1):
    return nodo(ClaseNodo.LOCAL, nombre, tipo, linea)


def parametro(nombre, tipo="grano", linea=1):
    return nodo(ClaseNodo.PARAMETRO, nombre, tipo, linea)


def analizar(fuente):
    entrada = explorar_para_parser(fuente)
    resultado = Analizador().analizar(entrada.tokens_para_parser())
    assert resultado.correcto, resultado.errores
    return resultado.arbol


def verificar(fuente):
    """Retorna (mensajes de error, tabla, arbol)."""
    arbol = analizar(fuente)
    tabla = TablaSimbolos()
    errores = verificar_semantica(arbol, tabla)
    return [e.mensaje for e in errores], tabla, arbol


def principal(cuerpo):
    return f"barista chorreador() {{ {cuerpo} }}"


class TestOperacionesBasicas(unittest.TestCase):
    """1.2.1: registrar, consultar y detectar conflictos."""

    def test_registrar_y_buscar(self):
        tabla = TablaSimbolos()
        x = local("x", "poso")
        simbolo = tabla.registrar("x", x)
        self.assertIs(tabla.buscar("x"), simbolo)
        self.assertIs(tabla.resolver("x"), x)
        self.assertEqual(simbolo.nombre, "x")
        self.assertEqual(simbolo.categoria, Categoria.VARIABLE_LOCAL)
        self.assertEqual(simbolo.tipo, "poso")
        self.assertIs(simbolo.definicion, x)
        self.assertIs(simbolo.ambito, tabla.global_)

    def test_nombre_inexistente(self):
        tabla = TablaSimbolos()
        self.assertIsNone(tabla.buscar("nada"))
        self.assertIsNone(tabla.resolver("nada"))

    def test_conflicto_queda_registrado(self):
        tabla = TablaSimbolos()
        primero, segundo = local("x", linea=1), local("x", "poso", linea=2)
        self.assertTrue(tabla.declarar("x", primero))
        self.assertFalse(tabla.declarar("x", segundo))
        self.assertIs(tabla.resolver("x"), primero)
        self.assertEqual(len(tabla.conflictos), 1)
        conflicto = tabla.conflictos[0]
        self.assertIs(conflicto.nuevo.definicion, segundo)
        self.assertIs(conflicto.existente.definicion, primero)

    def test_conflicto_entre_categorias_distintas(self):
        tabla = TablaSimbolos()
        tabla.declarar("q", local("q"))
        self.assertFalse(tabla.declarar("q", nodo(ClaseNodo.QUBIT, "q")))

    def test_nodo_que_no_declara_nada(self):
        tabla = TablaSimbolos()
        with self.assertRaises(ValueError):
            tabla.declarar("x", nodo(ClaseNodo.ASIGNACION, "x"))

    def test_no_se_sale_del_global(self):
        with self.assertRaises(RuntimeError):
            TablaSimbolos().salir()


class TestAmbitos(unittest.TestCase):
    """1.2.2: entrada, salida y busqueda hacia los ambitos exteriores."""

    def test_entrar_y_salir_cambian_el_nivel(self):
        tabla = TablaSimbolos()
        self.assertEqual(tabla.nivel, 0)
        interno = tabla.entrar()
        self.assertEqual((tabla.nivel, interno.nivel), (1, 1))
        self.assertIs(interno.padre, tabla.global_)
        tabla.salir()
        self.assertEqual(tabla.nivel, 0)
        self.assertIs(tabla.actual, tabla.global_)

    def test_busqueda_hacia_afuera(self):
        tabla = TablaSimbolos()
        g = nodo(ClaseNodo.GLOBAL, "g", "grano")
        tabla.declarar("g", g)
        tabla.entrar()
        tabla.entrar()
        self.assertIs(tabla.resolver("g"), g)

    def test_interno_no_es_visible_al_salir(self):
        tabla = TablaSimbolos()
        tabla.entrar()
        tabla.declarar("y", local("y"))
        tabla.salir()
        self.assertIsNone(tabla.resolver("y"))

    def test_sombreado_y_recuperacion(self):
        tabla = TablaSimbolos()
        externo, interno = local("x"), local("x", "granoMolido")
        tabla.declarar("x", externo)
        tabla.entrar()
        self.assertTrue(tabla.declarar("x", interno))
        self.assertEqual(tabla.buscar("x").tipo, "granoMolido")
        tabla.salir()
        self.assertIs(tabla.resolver("x"), externo)

    def test_ambitos_hermanos_no_se_ven(self):
        tabla = TablaSimbolos()
        tabla.entrar()
        tabla.declarar("t", local("t"))
        tabla.salir()
        tabla.entrar()
        self.assertIsNone(tabla.resolver("t"))
        self.assertTrue(tabla.declarar("t", local("t")))

    def test_parametro_y_cuerpo_comparten_nombres(self):
        tabla = TablaSimbolos()
        tabla.entrar()                     # Ambito de la funcion.
        tabla.declarar("a", parametro("a"))
        tabla.entrar()                     # Bloque del cuerpo.
        self.assertFalse(tabla.declarar("a", local("a")))
        tabla.entrar()                     # Bloque mas interno.
        self.assertTrue(tabla.declarar("a", local("a")))

    def test_funciones_incorporadas_se_pueden_ocultar(self):
        tabla = TablaSimbolos()
        self.assertEqual(tabla.buscar("leer").categoria,
                         Categoria.INCORPORADA)
        self.assertIsNone(tabla.resolver("leer"))
        propia = nodo(ClaseNodo.FUNCION, "leer")
        self.assertTrue(tabla.declarar("leer", propia))
        self.assertIs(tabla.resolver("leer"), propia)

    def test_el_registro_conserva_ambitos_cerrados(self):
        tabla = TablaSimbolos()
        tabla.entrar()
        tabla.declarar("y", local("y"))
        tabla.salir()
        self.assertEqual([s.nombre for s in tabla.simbolos()], ["y"])
        self.assertEqual(len(tabla.ambitos), 2)


class TestRegistroDesdeElPrograma(unittest.TestCase):
    """1.2.3: categorias, tipos y referencia a la definicion original."""

    FUENTE = (
        "cafeteria grano limite = 10; "
        "barista sumar(grano a, poso b) { degustar a + b; } "
        "barista chorreador() { "
        "taza grano xs = [1, 2]; "
        "recolar (grano n en xs) { servir(n); } "
        "qubit q; "
        "poso r = sumar(limite, 2.5); "
        "}"
    )

    def setUp(self):
        self.errores, self.tabla, self.arbol = verificar(self.FUENTE)
        self.simbolos = {s.nombre: s for s in self.tabla.simbolos()}

    def test_sin_errores(self):
        self.assertEqual(self.errores, [])

    def test_categorias(self):
        esperado = {
            "limite": Categoria.VARIABLE_GLOBAL,
            "sumar": Categoria.FUNCION,
            "a": Categoria.PARAMETRO,
            "b": Categoria.PARAMETRO,
            "xs": Categoria.VARIABLE_LOCAL,
            "n": Categoria.VARIABLE_CICLO,
            "q": Categoria.QUBIT,
            "r": Categoria.VARIABLE_LOCAL,
        }
        self.assertEqual(
            {k: s.categoria for k, s in self.simbolos.items()}, esperado)

    def test_tipos(self):
        tipos = {k: s.tipo for k, s in self.simbolos.items()}
        self.assertEqual(tipos["limite"], "grano")
        self.assertEqual(tipos["b"], "poso")
        self.assertEqual(tipos["xs"], "taza grano")
        self.assertEqual(tipos["n"], "grano")
        self.assertEqual(tipos["q"], "qubit")
        # El retorno de una funcion no se escribe: viene de la inferencia.
        self.assertEqual(tipos["sumar"], "poso")
        self.assertEqual(self.simbolos["sumar"].parametros,
                         ("grano", "poso"))
        self.assertEqual(self.simbolos["sumar"].describir_tipo(),
                         "(grano, poso) -> poso")

    def test_referencia_a_la_definicion(self):
        global_, funcion = self.arbol.hijos[0], self.arbol.hijos[1]
        self.assertIs(self.simbolos["limite"].definicion, global_)
        self.assertIs(self.simbolos["sumar"].definicion, funcion)
        self.assertIs(self.simbolos["a"].definicion, funcion.hijos[0])
        self.assertIs(self.tabla.simbolo_de(funcion), self.simbolos["sumar"])
        self.assertEqual(self.simbolos["limite"].posicion, Posicion(1, 1))

    def test_ambitos_de_cada_simbolo(self):
        niveles = {k: s.ambito.nivel for k, s in self.simbolos.items()}
        self.assertEqual(niveles["limite"], 0)
        self.assertEqual(niveles["sumar"], 0)
        self.assertEqual(niveles["a"], 1)      # Ambito de la funcion.
        self.assertEqual(niveles["xs"], 1)     # Bloque de chorreador.
        self.assertEqual(niveles["n"], 2)      # Ambito de recolar.
        self.assertIs(self.simbolos["n"].ambito.padre,
                      self.simbolos["xs"].ambito)

    def test_impresion(self):
        texto = self.tabla.a_texto()
        lineas = texto.splitlines()
        self.assertTrue(lineas[0].startswith("Ambito"))
        self.assertIn("sumar", texto)
        self.assertIn("(grano, poso) -> poso", texto)
        self.assertIn("variable de recolar", texto)
        self.assertIn("Ambito 0 (global)", texto)
        # Una fila por simbolo, mas encabezado y separador.
        filas = [linea for linea in lineas[2:] if linea and
                 not linea.startswith("Ambito ")]
        self.assertEqual(len(filas), len(self.simbolos))

    def test_conflictos_del_programa(self):
        errores, tabla, _ = verificar(
            "barista f(grano a, grano a) { } " + principal("grano x; poso x;"))
        self.assertEqual(len(errores), 2)
        self.assertEqual([c.nuevo.nombre for c in tabla.conflictos],
                         ["a", "x"])


class TestIntegracionConVerificador(unittest.TestCase):
    """La tabla conectada al verificador existente (analisis.py)."""

    def test_usos_en_atributos_se_enlazan(self):
        errores, _, arbol = verificar(principal(
            "taza grano xs = [1]; xs.insertar(2); "
            "recolar (grano n en xs) { } "
        ))
        self.assertEqual(errores, [])
        bloque = arbol.hijos[-1].hijos[0]
        declaracion, operacion, ciclo = bloque.hijos
        self.assertIs(operacion.semantica.definiciones["receptor"],
                      declaracion)
        self.assertIs(ciclo.semantica.definiciones["lista"], declaracion)

    def test_global_anterior_en_inicializador(self):
        errores, _, _ = verificar(
            "cafeteria grano a = 1; cafeteria grano b = a + 1; "
            + principal(""))
        self.assertEqual(errores, [])

    def test_funcion_ve_globales_declaradas_despues(self):
        errores, _, _ = verificar(
            "barista f() { degustar g; } cafeteria grano g = 1; "
            + principal("grano x = f();"))
        self.assertEqual(errores, [])

    def test_variable_de_recolar_redeclarada_en_su_cuerpo(self):
        errores, _, _ = verificar(principal(
            "taza grano xs = [1]; recolar (grano n en xs) { grano n = 2; }"))
        self.assertEqual(len(errores), 1)
        self.assertIn("'n' ya declarado", errores[0])

    def test_parametro_se_puede_sombrear_en_bloque_interno(self):
        errores, _, _ = verificar(
            "barista f(grano a) { hierve (fuerte) { granoMolido a = \"s\"; } "
            "degustar a; } " + principal(""))
        self.assertEqual(errores, [])

    def test_llamar_a_una_variable(self):
        errores, _, _ = verificar(principal("grano x = 1; x();"))
        self.assertEqual(errores, ["'x' no es una funcion"])


if __name__ == "__main__":
    unittest.main()
