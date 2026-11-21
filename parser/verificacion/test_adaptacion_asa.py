"""Pruebas de los nuevos campos del ASA."""
import json
import unittest
from dataclasses import FrozenInstanceError

from parser.analizador import Analizador
from parser.asa_esquema import validar_arbol
from parser.asa_impresion import a_texto
from parser.integracion import explorar_para_parser


class TestAdaptacionASA(unittest.TestCase):
    def setUp(self):
        entrada = explorar_para_parser(
            'barista f() { f(); } '
            'barista chorreador() { grano x; grano y; x = y; }'
        )
        resultado = Analizador().analizar(entrada.tokens_para_parser())
        self.assertTrue(resultado.correcto)
        self.arbol = resultado.arbol
        self.funcion = self.arbol.hijos[0]
        self.locales = self.arbol.hijos[-1].hijos[0].hijos

    def test_campos_vacios_e_independientes(self):
        x, y, asignacion = self.locales
        self.assertIsNone(x.semantica.tipo_inferido)
        self.assertEqual(x.semantica.definiciones, {})
        x.semantica.tipo_inferido = 'grano'
        asignacion.semantica.definiciones['nombre'] = x
        self.assertIsNone(y.semantica.tipo_inferido)
        self.assertEqual(y.semantica.definiciones, {})
        self.assertIs(asignacion.semantica.definiciones['nombre'], x)

    def test_estructura_sigue_protegida(self):
        with self.assertRaises(FrozenInstanceError):
            self.funcion.hijos = ()
        with self.assertRaises(TypeError):
            self.funcion.atributos['nombre'] = 'otra'

    def test_referencia_recursiva_no_afecta_salida_sintactica(self):
        antes = self.arbol.a_dict()
        texto = a_texto(self.arbol)
        llamada = self.funcion.hijos[-1].hijos[0]
        llamada.semantica.definiciones['nombre'] = self.funcion
        self.assertEqual(self.arbol.a_dict(), antes)
        self.assertEqual(a_texto(self.arbol), texto)
        self.assertTrue(json.dumps(self.arbol.a_dict()))
        self.assertEqual(validar_arbol(self.arbol), [])

    def test_varios_papeles_en_un_nodo(self):
        x, y, asignacion = self.locales
        asignacion.semantica.definiciones.update(nombre=x, lista=y)
        self.assertIs(asignacion.semantica.definiciones['nombre'], x)
        self.assertIs(asignacion.semantica.definiciones['lista'], y)

    def test_impresion_decorada_incluye_tipo_y_definicion(self):
        x, _, asignacion = self.locales
        x.semantica.tipo_inferido = "grano"
        asignacion.semantica.tipo_inferido = "grano"
        asignacion.semantica.definiciones["nombre"] = x

        texto = a_texto(self.arbol, con_semantica=True)

        self.assertIn("decorado=[tipo=grano;", texto)
        self.assertIn("nombre=def:DeclaracionLocal:x@", texto)
