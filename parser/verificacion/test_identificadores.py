
"""Pruebas de verificacion de identificadores."""

import unittest

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.verificador_identificadores import (
    VerificadorIdentificadores,
)


def analizar(fuente):
    entrada = explorar_para_parser(fuente)
    resultado = Analizador().analizar(
        entrada.tokens_para_parser()
    )
    if not resultado.correcto:
        raise AssertionError(resultado.errores)
    return resultado.arbol



class TablaDePrueba:
    """Simula ambitos para probar el visitante."""

    def __init__(self):
        self.ambitos = [{}]

    def entrar(self):
        self.ambitos.append({})

    def salir(self):
        self.ambitos.pop()

    def declarar(self, nombre, nodo):
        ambito_actual = self.ambitos[-1]

        if nombre in ambito_actual:
            return False

        ambito_actual[nombre] = nodo
        return True

    def resolver(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None




class TestIdentificadores(unittest.TestCase):

    def test_identificador_declarado(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano x = 10; "
            "x = x + 5; "
            "}"
        )

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]
        asignacion = bloque.hijos[1]

        simbolos = {"x": declaracion}
        verificador = VerificadorIdentificadores(
            simbolos.get
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(errores, [])
        self.assertIs(
            asignacion.semantica.definiciones["nombre"],
            declaracion,
        )

        identificador = asignacion.hijos[0].hijos[0]
        self.assertIs(
            identificador.semantica.definiciones["nombre"],
            declaracion,
        )

    def test_identificador_no_declarado(self):
        arbol = analizar(
            "barista chorreador() { "
            "y = 10; "
            "}"
        )

        verificador = VerificadorIdentificadores(
            lambda nombre: None
        )
        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn("'y' no declarado", errores[0])

    def test_funcion_no_declarada(self):
        arbol = analizar(
            "barista chorreador() { "
            "funcion_inexistente(); "
            "}"
        )

        verificador = VerificadorIdentificadores(
            lambda nombre: None
        )
        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'funcion_inexistente' no declarado",
            errores[0],
        )


    def test_visibilidad_entre_ambitos(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano x = 10; "
            "hierve (fuerte) { "
            "grano y = 20; "
            "x = x + y; "
            "} "
            "x = 30; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(errores, [])
        self.assertEqual(len(tabla.ambitos), 1)

        bloque = arbol.hijos[0].hijos[0]
        declaracion_x = bloque.hijos[0]
        condicional = bloque.hijos[1]

        bloque_interno = condicional.hijos[1]
        asignacion_interna = bloque_interno.hijos[1]

        self.assertIs(
            asignacion_interna.semantica.definiciones["nombre"],
            declaracion_x,
        )

    def test_variable_fuera_de_ambito(self):
        arbol = analizar(
            "barista chorreador() { "
            "hierve (fuerte) { "
            "grano temporal = 10; "
            "} "
            "temporal = 20; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'temporal' no declarado",
            errores[0],
        )
        self.assertEqual(len(tabla.ambitos), 1)

    def test_globales_funciones_y_parametros(self):
        arbol = analizar(
            "cafeteria grano limite = 100; "
            "barista sumar(grano a, grano b) { "
            "degustar a + b; "
            "} "
            "barista chorreador() { "
            "grano resultado = sumar(limite, 20); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(errores, [])

        global_limite = arbol.hijos[0]
        funcion_sumar = arbol.hijos[1]
        principal = arbol.hijos[2]

        llamada = principal.hijos[0].hijos[0].hijos[0]

        self.assertIs(
            llamada.semantica.definiciones["nombre"],
            funcion_sumar,
        )

        identificador_limite = llamada.hijos[0]

        self.assertIs(
            identificador_limite.semantica.definiciones["nombre"],
            global_limite,
        )

        parametro_a = funcion_sumar.hijos[0]
        parametro_b = funcion_sumar.hijos[1]

        retorno = funcion_sumar.hijos[-1].hijos[0]
        expresion = retorno.hijos[0]

        self.assertIs(
            expresion.hijos[0].semantica.definiciones["nombre"],
            parametro_a,
        )

        self.assertIs(
            expresion.hijos[1].semantica.definiciones["nombre"],
            parametro_b,
        )

    def test_funcion_declarada_posteriormente(self):
        arbol = analizar(
            "barista primera() { "
            "segunda(); "
            "} "
            "barista segunda() { "
            "} "
            "barista chorreador() { "
            "primera(); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(errores, [])

        funcion_segunda = arbol.hijos[1]
        llamada = arbol.hijos[0].hijos[-1].hijos[0]

        self.assertIs(
            llamada.semantica.definiciones["nombre"],
            funcion_segunda,
        )

    def test_parametro_fuera_de_funcion(self):
        arbol = analizar(
            "barista prueba(grano parametro) { "
            "degustar parametro; "
            "} "
            "barista chorreador() { "
            "parametro = 10; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'parametro' no declarado",
            errores[0],
        )

    def test_variable_del_ciclo_recolar(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza grano numeros = [1, 2, 3]; "
            "recolar (grano numero en numeros) { "
            "numero = numero + 1; "
            "} "
            "numero = 10; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn("'numero' no declarado", errores[0])

        bloque = arbol.hijos[0].hijos[0]
        declaracion_lista = bloque.hijos[0]
        ciclo = bloque.hijos[1]
        asignacion_interna = ciclo.hijos[0].hijos[0]


        self.assertIs(
            ciclo.semantica.definiciones["lista"],
            declaracion_lista,
        )
        self.assertIs(
            asignacion_interna.semantica.definiciones["nombre"],
            ciclo,
        )

        self.assertEqual(len(tabla.ambitos), 1)

    def test_recolar_con_lista_no_declarada(self):
        arbol = analizar(
            "barista chorreador() { "
            "recolar (grano elemento en inexistente) { "
            "elemento = 5; "
            "} "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            resolver=tabla.resolver,
            declarar=tabla.declarar,
            entrar_ambito=tabla.entrar,
            salir_ambito=tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'inexistente' no declarado",
            errores[0],
        )

    def test_variable_duplicada(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano x = 10; "
            "grano x = 20; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn("'x' ya declarado", errores[0])

    def test_funcion_duplicada(self):
        arbol = analizar(
            "barista calcular() {} "
            "barista calcular() {} "
            "barista chorreador() {}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'calcular' ya declarado",
            errores[0],
        )

    def test_sombreado_en_bloque_interno(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano x = 10; "
            "hierve (fuerte) { "
            "grano x = 20; "
            "x = 30; "
            "} "
            "x = 40; "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)
        self.assertEqual(errores, [])

        bloque = arbol.hijos[0].hijos[0]
        exterior = bloque.hijos[0]
        condicional = bloque.hijos[1]
        bloque_interno = condicional.hijos[1]
        interior = bloque_interno.hijos[0]

        asignacion_interna = bloque_interno.hijos[1]
        asignacion_externa = bloque.hijos[2]

        self.assertIs(
            asignacion_interna.semantica.definiciones["nombre"],
            interior,
        )

        self.assertIs(
            asignacion_externa.semantica.definiciones["nombre"],
            exterior,
        )

    def test_funciones_incorporadas(self):
        arbol = analizar(
            "barista chorreador() { "
            "granoMolido nombre = leer(); "
            "servir(nombre); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(errores, [])

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]
        llamada_servir = bloque.hijos[1]

        self.assertIs(
            llamada_servir.hijos[0].semantica.definiciones["nombre"],
            declaracion,
        )

    def test_argumento_no_declarado_en_servir(self):
        arbol = analizar(
            "barista chorreador() { "
            "servir(variable_inexistente); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'variable_inexistente' no declarado",
            errores[0],
        )

    def test_qubit_declarado(self):
        arbol = analizar(
            "barista chorreador() { "
            "qubit q0; "
            "H(q0); "
            "cafe resultado = medir(q0); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        self.assertEqual(verificador.verificar(arbol), [])

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]
        compuerta = bloque.hijos[1]
        medicion = bloque.hijos[2].hijos[0]

        self.assertIs(
            compuerta.hijos[0].semantica.definiciones["nombre"],
            declaracion,
        )
        self.assertIs(
            medicion.hijos[0].semantica.definiciones["nombre"],
            declaracion,
        )

    def test_qubit_fuera_de_ambito(self):
        arbol = analizar(
            "barista chorreador() { "
            "hierve (fuerte) { qubit q0; } "
            "H(q0); "
            "}"
        )

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores = verificador.verificar(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'q0' no declarado",
            errores[0],
        )



if __name__ == "__main__":
    unittest.main()
