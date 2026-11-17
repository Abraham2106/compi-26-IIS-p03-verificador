
"""Pruebas de inferencia de tipos."""

import unittest

from parser.analizador import Analizador
from parser.integracion import explorar_para_parser
from parser.semantica.inferencia_tipos import InferidorTipos
from parser.semantica.verificador_identificadores import (
    VerificadorIdentificadores,
)
from parser.verificacion.test_identificadores import TablaDePrueba
from pathlib import Path

def analizar(fuente):
    entrada = explorar_para_parser(fuente)
    resultado = Analizador().analizar(
        entrada.tokens_para_parser()
    )
    if not resultado.correcto:
        raise AssertionError(resultado.errores)
    return resultado.arbol



class TestInferenciaTipos(unittest.TestCase):


    def _verificar_ejemplo_completo(self, nombre_archivo):
        ruta = (
            Path(__file__).resolve().parents[1]
            / "ejemplos_completos"
            / nombre_archivo
        )

        fuente = ruta.read_text(encoding="utf-8")
        arbol = analizar(fuente)

        tabla = TablaDePrueba()

        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        errores_identificadores = verificador.verificar(arbol)

        self.assertEqual(
            errores_identificadores,
            [],
            f"Errores de identificadores en {nombre_archivo}",
        )

        inferidor = InferidorTipos()
        errores_tipos = inferidor.inferir(arbol)

        self.assertEqual(
            errores_tipos,
            [],
            f"Errores de tipos en {nombre_archivo}: {errores_tipos}",
        )

        return arbol

    def _inferir_cuantico(self, fuente):
        arbol = analizar(fuente)

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        return arbol, errores


    def _inferir_recursion(self, fuente):
        arbol = analizar(fuente)

        tabla = TablaDePrueba()
        verificador = VerificadorIdentificadores(
            tabla.resolver,
            tabla.declarar,
            tabla.entrar,
            tabla.salir,
        )

        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        return arbol, errores

    def test_tipos_de_literales(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano a = 5; "
            "poso b = 2.5; "
            'granoMolido c = "hola"; '
            "cafe d = fuerte; "
            "cafe e = ralo; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaraciones = arbol.hijos[0].hijos[0].hijos
        tipos = [
            "grano",
            "poso",
            "granoMolido",
            "cafe",
            "cafe",
        ]

        for declaracion, tipo in zip(declaraciones, tipos):
            with self.subTest(tipo=tipo):
                self.assertEqual(
                    declaracion.semantica.tipo_inferido,
                    tipo,
                )
                self.assertEqual(
                    declaracion.hijos[0].semantica.tipo_inferido,
                    tipo,
                )

    def test_tipo_de_identificador(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano base = 10; "
            "grano copia = base; "
            "}"
        )

        bloque = arbol.hijos[0].hijos[0]
        declaracion_base = bloque.hijos[0]
        declaracion_copia = bloque.hijos[1]
        identificador = declaracion_copia.hijos[0]

        def resolver(nombre):
            if nombre == "base":
                return declaracion_base
            return None

        verificador = VerificadorIdentificadores(resolver)
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        self.assertEqual(inferidor.inferir(arbol), [])

        self.assertIs(
            identificador.semantica.definiciones["nombre"],
            declaracion_base,
        )
        self.assertEqual(
            identificador.semantica.tipo_inferido,
            "grano",
        )
        self.assertEqual(
            declaracion_copia.semantica.tipo_inferido,
            "grano",
        )

    def test_tipo_de_global_y_parametro(self):
        arbol = analizar(
            "cafeteria poso tasa = 2.5; "
            "barista calcular(grano numero) { "
            "degustar numero; "
            "} "
            "barista chorreador() { "
            "poso resultado = tasa; "
            "}"
        )

        global_tasa = arbol.hijos[0]
        funcion = arbol.hijos[1]
        parametro = funcion.hijos[0]

        definiciones = {
            "tasa": global_tasa,
            "numero": parametro,
        }

        verificador = VerificadorIdentificadores(
            definiciones.get
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        self.assertEqual(inferidor.inferir(arbol), [])

        self.assertEqual(
            global_tasa.semantica.tipo_inferido,
            "poso",
        )
        self.assertEqual(
            parametro.semantica.tipo_inferido,
            "grano",
        )

        retorno = funcion.hijos[-1].hijos[0]
        self.assertEqual(
            retorno.hijos[0].semantica.tipo_inferido,
            "grano",
        )

        principal = arbol.hijos[-1]
        declaracion = principal.hijos[0].hijos[0]
        identificador = declaracion.hijos[0]

        self.assertEqual(
            identificador.semantica.tipo_inferido,
            "poso",
        )

    def test_suma_de_enteros(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano resultado = 5 + 3; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "grano",
        )

    def test_suma_de_entero_y_decimal(self):
        arbol = analizar(
            "barista chorreador() { "
            "poso resultado = 5 + 2.5; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "poso",
        )

    def test_concatenacion_de_cadenas(self):
        arbol = analizar(
            'barista chorreador() { '
            'granoMolido saludo = "Hola " + "mundo"; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "granoMolido",
        )

    def test_error_al_sumar_texto_y_numero(self):
        arbol = analizar(
            'barista chorreador() { '
            'granoMolido resultado = "Hola" + 5; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)

        self.assertIn(
            "no se puede aplicar '+'",
            errores[0],
        )

        self.assertIn(
            "granoMolido y grano",
            errores[0],
        )

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertIsNone(
            expresion.semantica.tipo_inferido
        )

    def test_comparacion_numerica(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe resultado = 5 < 10; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "cafe",
        )

    def test_operacion_logica(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe resultado = (5 < 10) ConAzucar fuerte; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "cafe",
        )

        self.assertEqual(
            expresion.hijos[0].semantica.tipo_inferido,
            "cafe",
        )

    def test_igualdad_de_cadenas(self):
        arbol = analizar(
            'barista chorreador() { '
            'cafe iguales = "hola" == "hola"; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "cafe",
        )

    def test_error_operacion_logica_con_numero(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe resultado = fuerte SinAzucar 5; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede aplicar 'SinAzucar'",
            errores[0],
        )
        self.assertIn(
            "cafe y grano",
            errores[0],
        )

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertIsNone(
            expresion.semantica.tipo_inferido
        )

    def test_negativo_entero(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano resultado = -5; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "grano",
        )

    def test_positivo_decimal(self):
        arbol = analizar(
            "barista chorreador() { "
            "poso resultado = +2.5; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "poso",
        )

    def test_negacion_logica(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe resultado = Amargo fuerte; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertEqual(
            expresion.semantica.tipo_inferido,
            "cafe",
        )

    def test_error_negacion_logica_de_numero(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe resultado = Amargo 5; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede aplicar 'Amargo'",
            errores[0],
        )
        self.assertIn("al tipo grano", errores[0])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertIsNone(
            expresion.semantica.tipo_inferido
        )

    def test_error_negativo_de_cadena(self):
        arbol = analizar(
            'barista chorreador() { '
            'granoMolido resultado = -"hola"; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede aplicar '-'",
            errores[0],
        )
        self.assertIn("al tipo granoMolido", errores[0])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        expresion = declaracion.hijos[0]

        self.assertIsNone(
            expresion.semantica.tipo_inferido
        )

    def test_conversion_entero_a_decimal(self):
        arbol = analizar(
            "barista chorreador() { "
            "poso precio = 15; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]

        self.assertEqual(
            declaracion.semantica.tipo_inferido,
            "poso",
        )
        self.assertEqual(
            declaracion.hijos[0].semantica.tipo_inferido,
            "grano",
        )

    def test_error_declaracion_texto_en_entero(self):
        arbol = analizar(
            'barista chorreador() { '
            'grano edad = "hola"; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede asignar",
            errores[0],
        )
        self.assertIn(
            "granoMolido",
            errores[0],
        )
        self.assertIn(
            "grano",
            errores[0],
        )

    def test_error_declaracion_numero_en_booleano(self):
        arbol = analizar(
            "barista chorreador() { "
            "cafe activo = 10; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "tipo grano",
            errores[0],
        )
        self.assertIn(
            "tipo cafe",
            errores[0],
        )

    def test_error_reasignacion_incompatible(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano edad = 20; "
            "edad = 2.5; "
            "}"
        )

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]

        verificador = VerificadorIdentificadores(
            lambda nombre: declaracion if nombre == "edad" else None
        )

        self.assertEqual(
            verificador.verificar(arbol),
            [],
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "tipo poso",
            errores[0],
        )
        self.assertIn(
            "tipo grano",
            errores[0],
        )


    def test_lista_de_enteros(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza grano numeros = [1, 2, 3]; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        lista = declaracion.hijos[0]

        self.assertEqual(
            lista.semantica.tipo_inferido,
            "taza grano",
        )

    def test_lista_con_enteros_y_decimales(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza poso numeros = [1, 2.5, 3]; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        lista = declaracion.hijos[0]

        self.assertEqual(
            lista.semantica.tipo_inferido,
            "taza poso",
        )

    def test_lista_con_tipos_incompatibles(self):
        arbol = analizar(
            'barista chorreador() { '
            'taza grano numeros = [1, "hola"]; '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "elementos de lista incompatibles",
            errores[0],
        )

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        lista = declaracion.hijos[0]

        self.assertIsNone(
            lista.semantica.tipo_inferido
        )

    def test_lista_anidada(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza taza grano matriz = [[1, 2], [3, 4]]; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        matriz = declaracion.hijos[0]

        self.assertEqual(
            matriz.semantica.tipo_inferido,
            "taza taza grano",
        )

        for fila in matriz.hijos:
            self.assertEqual(
                fila.semantica.tipo_inferido,
                "taza grano",
            )

    def test_lista_vacia_con_tipo_declarado(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza grano numeros = []; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        lista = declaracion.hijos[0]

        self.assertEqual(
            lista.semantica.tipo_inferido,
            "taza grano",
        )

    def test_lista_vacia_anidada(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza taza grano matriz = [[], [1, 2]]; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        matriz = declaracion.hijos[0]

        self.assertEqual(
            matriz.semantica.tipo_inferido,
            "taza taza grano",
        )

        self.assertEqual(
            matriz.hijos[0].semantica.tipo_inferido,
            "taza grano",
        )

    def test_reasignacion_de_lista_vacia(self):
        arbol = analizar(
            "barista chorreador() { "
            "taza grano numeros = [1, 2]; "
            "numeros = []; "
            "}"
        )

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]
        asignacion = bloque.hijos[1]

        verificador = VerificadorIdentificadores(
            lambda nombre: (
                declaracion if nombre == "numeros" else None
            )
        )

        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        self.assertEqual(
            asignacion.hijos[0].semantica.tipo_inferido,
            "taza grano",
        )

    def test_error_lista_vacia_en_variable_escalar(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano numero = []; "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede asignar una lista vacia",
            errores[0],
        )

    def _inferir_con_receptor(self, fuente):
        """Prepara una variable receptora y comprueba sus operaciones."""
        arbol = analizar(fuente)
        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]

        def resolver(nombre):
            if nombre == declaracion.atributos["nombre"]:
                return declaracion
            return None

        verificador = VerificadorIdentificadores(resolver)
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        return bloque, errores

    def test_insertar_elemento_compatible(self):
        bloque, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "taza poso datos = [1.5]; "
            "datos.insertar(2); "
            "}"
        )

        self.assertEqual(errores, [])
        self.assertEqual(
            bloque.hijos[1].semantica.tipo_inferido,
            "sin_valor",
        )

    def test_buscar_devuelve_booleano(self):
        bloque, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "taza grano datos = [1, 2]; "
            "cafe existe = datos.buscar(2); "
            "}"
        )

        self.assertEqual(errores, [])

        operacion = bloque.hijos[1].hijos[0]
        self.assertEqual(
            operacion.semantica.tipo_inferido,
            "cafe",
        )

    def test_extraer_devuelve_tipo_elemento(self):
        bloque, errores = self._inferir_con_receptor(
            'barista chorreador() { '
            'taza granoMolido menu = ["Espresso"]; '
            'granoMolido bebida = menu.extraer(0); '
            '}'
        )

        self.assertEqual(errores, [])

        operacion = bloque.hijos[1].hijos[0]
        self.assertEqual(
            operacion.semantica.tipo_inferido,
            "granoMolido",
        )

    def test_error_insertar_tipo_incompatible(self):
        _, errores = self._inferir_con_receptor(
            'barista chorreador() { '
            'taza grano datos = [1]; '
            'datos.insertar("hola"); '
            '}'
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("insertar", errores[0])
        self.assertIn("granoMolido", errores[0])

    def test_error_extraer_indice_decimal(self):
        _, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "taza grano datos = [1]; "
            "grano numero = datos.extraer(1.5); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "extraer requiere un indice de tipo grano",
            errores[0],
        )

    def test_error_receptor_no_es_lista(self):
        _, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "grano numero = 5; "
            "numero.buscar(5); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'numero' no es una lista",
            errores[0],
        )

    def test_insertar_no_devuelve_valor(self):
        _, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "taza grano datos = [1]; "
            "grano resultado = datos.insertar(3); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("sin_valor", errores[0])

    def _evaluar_llamada(self, fuente):
        """Verifica identificadores y tipos de una llamada."""
        arbol = analizar(fuente)
        funcion = arbol.hijos[0]
        nombre_funcion = funcion.atributos["nombre"]

        def resolver(nombre):
            if nombre == nombre_funcion:
                return funcion
            return None

        verificador = VerificadorIdentificadores(resolver)
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        return arbol, errores

    def test_llamada_con_argumentos_correctos(self):
        _, errores = self._evaluar_llamada(
            "barista preparar(grano cantidad, poso precio) {} "
            "barista chorreador() { "
            "preparar(3, 2.5); "
            "}"
        )

        self.assertEqual(errores, [])

    def test_llamada_con_promocion_numerica(self):
        _, errores = self._evaluar_llamada(
            "barista preparar(poso precio) {} "
            "barista chorreador() { "
            "preparar(5); "
            "}"
        )

        self.assertEqual(errores, [])

    def test_error_tipo_de_argumento(self):
        _, errores = self._evaluar_llamada(
            "barista preparar(grano cantidad) {} "
            "barista chorreador() { "
            'preparar("hola"); '
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("argumento 1", errores[0])
        self.assertIn("se esperaba grano", errores[0])
        self.assertIn("se recibio granoMolido", errores[0])

    def test_error_argumentos_insuficientes(self):
        _, errores = self._evaluar_llamada(
            "barista preparar(grano a, grano b) {} "
            "barista chorreador() { "
            "preparar(3); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("requiere 2 argumento(s)", errores[0])
        self.assertIn("recibio 1", errores[0])

    def test_error_argumentos_adicionales(self):
        _, errores = self._evaluar_llamada(
            "barista preparar(grano cantidad) {} "
            "barista chorreador() { "
            "preparar(1, 2); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("requiere 1 argumento(s)", errores[0])
        self.assertIn("recibio 2", errores[0])

    def test_llamada_con_lista_vacia(self):
        arbol, errores = self._evaluar_llamada(
            "barista procesar(taza grano datos) {} "
            "barista chorreador() { "
            "procesar([]); "
            "}"
        )

        self.assertEqual(errores, [])

        principal = arbol.hijos[-1]
        llamada = principal.hijos[0].hijos[0]
        argumento = llamada.hijos[0]

        self.assertEqual(
            argumento.semantica.tipo_inferido,
            "taza grano",
        )

    def test_error_variable_usada_como_funcion(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano numero = 5; "
            "numero(3); "
            "}"
        )

        bloque = arbol.hijos[0].hijos[0]
        declaracion = bloque.hijos[0]

        verificador = VerificadorIdentificadores(
            lambda nombre: (
                declaracion if nombre == "numero" else None
            )
        )

        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "'numero' no es una funcion",
            errores[0],
        )

    def test_retorno_entero_en_llamada(self):
        arbol, errores = self._evaluar_llamada(
            "barista obtenerNumero() { degustar 10; } "
            "barista chorreador() { "
            "grano numero = obtenerNumero(); "
            "}"
        )

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "grano",
        )

        declaracion = arbol.hijos[-1].hijos[0].hijos[0]
        llamada = declaracion.hijos[0]

        self.assertEqual(
            llamada.semantica.tipo_inferido,
            "grano",
        )

    def test_retornos_numericos_promovidos(self):
        arbol, errores = self._evaluar_llamada(
            "barista calcular() { "
            "hierve (fuerte) { degustar 1; } "
            "enfria { degustar 2.5; } "
            "} "
            "barista chorreador() { "
            "poso resultado = calcular(); "
            "}"
        )

        self.assertEqual(errores, [])

        self.assertEqual(
            arbol.hijos[0].semantica.tipo_inferido,
            "poso",
        )

    def test_error_retornos_incompatibles(self):
        arbol, errores = self._evaluar_llamada(
            "barista calcular() { "
            "hierve (fuerte) { degustar 10; } "
            'enfria { degustar "hola"; } '
            "} "
            "barista chorreador() { "
            "grano resultado = calcular(); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "retornos incompatibles",
            errores[0],
        )
        self.assertIn("grano", errores[0])
        self.assertIn("granoMolido", errores[0])

        self.assertIsNone(
            arbol.hijos[0].semantica.tipo_inferido
        )

    def test_funcion_sin_retorno_no_puede_asignarse(self):
        _, errores = self._evaluar_llamada(
            "barista ejecutar() {} "
            "barista chorreador() { "
            "grano resultado = ejecutar(); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("sin_valor", errores[0])

    def test_retorno_vacio(self):
        arbol, errores = self._evaluar_llamada(
            "barista terminar() { degustar; } "
            "barista chorreador() { terminar(); }"
        )

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "sin_valor",
        )

        llamada = arbol.hijos[-1].hijos[0].hijos[0]
        self.assertEqual(
            llamada.semantica.tipo_inferido,
            "sin_valor",
        )

    def test_hierve_condicion_booleana(self):
        arbol = analizar(
            "barista chorreador() { "
            "hierve (5 < 10) {} "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

    def test_error_hierve_condicion_numerica(self):
        arbol = analizar(
            "barista chorreador() { "
            "hierve (5) {} "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "hierve requiere una condicion de tipo cafe",
            errores[0],
        )
        self.assertIn("recibio grano", errores[0])

    def test_chorreando_condicion_booleana(self):
        arbol = analizar(
            "barista chorreador() { "
            "chorreando (fuerte) {} "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

    def test_error_chorreando_condicion_texto(self):
        arbol = analizar(
            'barista chorreador() { '
            'chorreando ("hola") {} '
            '}'
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "chorreando requiere una condicion de tipo cafe",
            errores[0],
        )
        self.assertIn("recibio granoMolido", errores[0])

    def test_recolar_lista_compatible(self):
        bloque, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "taza grano numeros = [1, 2, 3]; "
            "recolar (grano numero en numeros) {} "
            "}"
        )

        self.assertEqual(errores, [])

        ciclo = bloque.hijos[1]
        self.assertEqual(
            ciclo.semantica.tipo_inferido,
            "grano",
        )

    def test_error_recolar_tipo_incompatible(self):
        _, errores = self._inferir_con_receptor(
            'barista chorreador() { '
            'taza granoMolido nombres = ["Ana", "Luis"]; '
            'recolar (grano numero en nombres) {} '
            '}'
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "tipo incompatible en recolar",
            errores[0],
        )
        self.assertIn("granoMolido", errores[0])

    def test_error_recolar_receptor_no_lista(self):
        _, errores = self._inferir_con_receptor(
            "barista chorreador() { "
            "grano numero = 5; "
            "recolar (grano elemento en numero) {} "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "recolar requiere una lista",
            errores[0],
        )
        self.assertIn("recibio grano", errores[0])

    def test_retorno_de_funcion_declarada_despues(self):
        arbol = analizar(
            "barista primera() { degustar segunda(); } "
            "barista segunda() { degustar 10; } "
            "barista chorreador() { "
            "grano resultado = primera(); "
            "}"
        )

        funciones = {
            nodo.atributos["nombre"]: nodo
            for nodo in arbol.hijos[:-1]
        }

        verificador = VerificadorIdentificadores(
            funciones.get
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        primera = arbol.hijos[0]
        segunda = arbol.hijos[1]

        self.assertEqual(
            primera.semantica.tipo_inferido,
            "grano",
        )
        self.assertEqual(
            segunda.semantica.tipo_inferido,
            "grano",
        )

        declaracion = arbol.hijos[-1].hijos[0].hijos[0]
        llamada = declaracion.hijos[0]

        self.assertEqual(
            llamada.semantica.tipo_inferido,
            "grano",
        )

    def test_error_en_funcion_adelantada_no_se_duplica(self):
        arbol = analizar(
            "barista primera() { degustar segunda(); } "
            'barista segunda() { degustar "hola" + 2; } '
            "barista chorreador() { primera(); }"
        )

        funciones = {
            nodo.atributos["nombre"]: nodo
            for nodo in arbol.hijos[:-1]
        }

        verificador = VerificadorIdentificadores(
            funciones.get
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se puede aplicar '+'",
            errores[0],
        )

    def test_error_recursion_sin_tipo_determinable(self):
        arbol, errores = self._evaluar_llamada(
            "barista repetir() { "
            "degustar repetir(); "
            "} "
            "barista chorreador() { "
            "grano resultado = repetir(); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se pudo inferir el tipo de retorno",
            errores[0],
        )
        self.assertIn("'repetir'", errores[0])

        self.assertIsNone(
            arbol.hijos[0].semantica.tipo_inferido
        )

    def test_recursion_como_sentencia_con_retorno_conocido(self):
        arbol, errores = self._evaluar_llamada(
            "barista repetir() { "
            "repetir(); "
            "degustar 1; "
            "} "
            "barista chorreador() { "
            "grano resultado = repetir(); "
            "}"
        )

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "grano",
        )

        llamada_recursiva = funcion.hijos[-1].hijos[0]

        self.assertEqual(
            llamada_recursiva.semantica.tipo_inferido,
            "grano",
        )

    def test_error_recursion_mutua_sin_tipo(self):
        arbol = analizar(
            "barista primera() { degustar segunda(); } "
            "barista segunda() { degustar primera(); } "
            "barista chorreador() { "
            "grano resultado = primera(); "
            "}"
        )

        funciones = {
            nodo.atributos["nombre"]: nodo
            for nodo in arbol.hijos[:-1]
        }

        verificador = VerificadorIdentificadores(
            funciones.get
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "no se pudo inferir el tipo de retorno",
            errores[0],
        )

        self.assertIsNone(
            arbol.hijos[0].semantica.tipo_inferido
        )
        self.assertIsNone(
            arbol.hijos[1].semantica.tipo_inferido
        )

    def test_leer_devuelve_cadena(self):
        arbol = analizar(
            "barista chorreador() { "
            "granoMolido nombre = leer(); "
            "}"
        )

        verificador = VerificadorIdentificadores(
            lambda nombre: None
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        self.assertEqual(inferidor.inferir(arbol), [])

        declaracion = arbol.hijos[0].hijos[0].hijos[0]
        llamada = declaracion.hijos[0]

        self.assertEqual(
            llamada.semantica.tipo_inferido,
            "granoMolido",
        )

    def test_servir_no_devuelve_valor(self):
        arbol = analizar(
            'barista chorreador() { servir("hola"); }'
        )

        verificador = VerificadorIdentificadores(
            lambda nombre: None
        )
        self.assertEqual(verificador.verificar(arbol), [])

        inferidor = InferidorTipos()
        self.assertEqual(inferidor.inferir(arbol), [])

        llamada = arbol.hijos[0].hijos[0].hijos[0]

        self.assertEqual(
            llamada.semantica.tipo_inferido,
            "sin_valor",
        )

    def test_error_leer_con_argumentos(self):
        arbol = analizar(
            "barista chorreador() { leer(10); }"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "leer no recibe argumentos",
            errores[0],
        )

    def test_error_servir_sin_argumentos(self):
        arbol = analizar(
            "barista chorreador() { servir(); }"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "servir requiere exactamente un argumento",
            errores[0],
        )

    def test_error_leer_asignado_a_entero(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano numero = leer(); "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn("granoMolido", errores[0])
        self.assertIn("tipo grano", errores[0])

    def test_error_asignar_resultado_de_servir(self):
        arbol = analizar(
            "barista chorreador() { "
            "grano resultado = servir(10); "
            "}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(len(errores), 1)
        self.assertIn("sin_valor", errores[0])

    def test_medicion_devuelve_cafe(self):
        arbol, errores = self._inferir_cuantico(
            "barista chorreador() { "
            "qubit q0; "
            "cafe resultado = medir(q0); "
            "}"
        )

        self.assertEqual(errores, [])

        bloque = arbol.hijos[0].hijos[0]
        qubit = bloque.hijos[0]
        medicion = bloque.hijos[1].hijos[0]

        self.assertEqual(
            qubit.semantica.tipo_inferido,
            "qubit",
        )
        self.assertEqual(
            medicion.semantica.tipo_inferido,
            "cafe",
        )

    def test_compuertas_cuanticas_validas(self):
        arbol, errores = self._inferir_cuantico(
            "barista chorreador() { "
            "qubit q0; "
            "qubit q1; "
            "H(q0); "
            "X(q1); "
            "Z(q0); "
            "CNOT(q0, q1); "
            "}"
        )

        self.assertEqual(errores, [])

        bloque = arbol.hijos[0].hijos[0]

        for compuerta in bloque.hijos[2:]:
            self.assertEqual(
                compuerta.semantica.tipo_inferido,
                "sin_valor",
            )

    def test_error_medicion_de_numero(self):
        _, errores = self._inferir_cuantico(
            "barista chorreador() { "
            "grano numero = 5; "
            "cafe resultado = medir(numero); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "medir requiere un qubit",
            errores[0],
        )
        self.assertIn("recibio grano", errores[0])

    def test_error_compuerta_con_numero(self):
        _, errores = self._inferir_cuantico(
            "barista chorreador() { "
            "grano numero = 5; "
            "H(numero); "
            "}"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn(
            "la compuerta H requiere un qubit",
            errores[0],
        )
        self.assertIn("recibio grano", errores[0])

    def test_recursion_directa_con_caso_base(self):
        arbol, errores = self._inferir_recursion(
            "barista contar(grano n) { "
            "hierve (n <= 0) { degustar 0; } "
            "enfria { degustar contar(n - 1); } "
            "} "
            "barista chorreador() { "
            "grano resultado = contar(3); "
            "}"
        )

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "grano",
        )

        declaracion = arbol.hijos[-1].hijos[0].hijos[0]
        self.assertEqual(
            declaracion.hijos[0].semantica.tipo_inferido,
            "grano",
        )

    def test_recursion_directa_en_expresion(self):
        arbol, errores = self._inferir_recursion(
            "barista contar(grano n) { "
            "hierve (n <= 0) { degustar 0; } "
            "enfria { degustar 1 + contar(n - 1); } "
            "} "
            "barista chorreador() { "
            "grano resultado = contar(3); "
            "}"
        )

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "grano",
        )

        condicional = funcion.hijos[-1].hijos[0]
        bloque_alternativo = condicional.hijos[2]
        retorno = bloque_alternativo.hijos[0]

        self.assertEqual(
            retorno.hijos[0].semantica.tipo_inferido,
            "grano",
        )

    def test_integracion_ejemplo_04_listas(self):
        arbol = self._verificar_ejemplo_completo(
            "04_ejercicio.qc"
        )

        bloque = arbol.hijos[-1].hijos[0]

        self.assertEqual(
            bloque.hijos[2].hijos[0].semantica.tipo_inferido,
            "cafe",
        )

        self.assertEqual(
            bloque.hijos[3].hijos[0].semantica.tipo_inferido,
            "granoMolido",
        )

    def test_integracion_ejemplo_05_funciones(self):
        arbol = self._verificar_ejemplo_completo(
            "05_ejercicio.qc"
        )

        funcion = arbol.hijos[0]

        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "cafe",
        )

    def test_integracion_ejemplo_06_cuantica(self):
        arbol = self._verificar_ejemplo_completo(
            "06_cuantica.qc"
        )

        bloque = arbol.hijos[-1].hijos[0]
        declaracion_resultado = bloque.hijos[6]
        medicion = declaracion_resultado.hijos[0]

        self.assertEqual(
            medicion.semantica.tipo_inferido,
            "cafe",
        )

    def test_integracion_ejemplo_07_completo(self):
        arbol = self._verificar_ejemplo_completo(
            "07_ajustes.qc"
        )

        funcion_negativo = arbol.hijos[1]
        funcion_saludar = arbol.hijos[2]

        self.assertEqual(
            funcion_negativo.semantica.tipo_inferido,
            "grano",
        )

        self.assertEqual(
            funcion_saludar.semantica.tipo_inferido,
            "sin_valor",
        )

    def test_literal_descafeinado(self):
        arbol = analizar(
            "barista devolverNulo() { "
            "degustar descafeinado; "
            "} "
            "barista chorreador() {}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        retorno = funcion.hijos[-1].hijos[0]
        literal = retorno.hijos[0]

        self.assertEqual(
            literal.semantica.tipo_inferido,
            "descafeinado",
        )
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "descafeinado",
        )

    def test_literal_se_quemo_el_cafe(self):
        arbol = analizar(
            "barista devolverError() { "
            "degustar SeQuemoElCafe; "
            "} "
            "barista chorreador() {}"
        )

        inferidor = InferidorTipos()
        errores = inferidor.inferir(arbol)

        self.assertEqual(errores, [])

        funcion = arbol.hijos[0]
        retorno = funcion.hijos[-1].hijos[0]
        literal = retorno.hijos[0]

        self.assertEqual(
            literal.semantica.tipo_inferido,
            "SeQuemoElCafe",
        )
        self.assertEqual(
            funcion.semantica.tipo_inferido,
            "SeQuemoElCafe",
        )


if __name__ == "__main__":
    unittest.main()
