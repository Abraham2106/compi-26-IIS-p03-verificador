import unittest
from io import StringIO
from pathlib import Path

from parser.analizador import Analizador
from parser.asa_esquema import validar_arbol
from parser.asa_impresion import a_texto, imprimir_preorden
from parser.integracion import explorar_para_parser
from parser.verificacion.asa_manual import asa_manual

BASE = Path(__file__).resolve().parent


def programa(cuerpo):
    return 'barista chorreador() {\n' + cuerpo + '\n}'


class TestParser(unittest.TestCase):
    def analizar(self, fuente):
        entrada = explorar_para_parser(fuente)
        self.assertTrue(entrada.apta, entrada.errores_lexicos)
        return Analizador().analizar(entrada.tokens_para_parser())

    def valido(self, fuente):
        resultado = self.analizar(fuente)
        self.assertTrue(resultado.correcto, resultado.errores)
        self.assertEqual(validar_arbol(resultado.arbol), [])
        return resultado.arbol

    def error(self, fuente, mensaje, posicion):
        resultado = self.analizar(fuente)
        self.assertFalse(resultado.correcto)
        self.assertTrue(resultado.errores)
        error = resultado.errores[0]
        self.assertIn(mensaje, error.mensaje)
        token = error.encontrado
        self.assertEqual((token.linea, token.columna), posicion)

    def expresion(self, texto):
        arbol = self.valido(programa(f'grano x = {texto};'))
        return arbol.hijos[-1].hijos[0].hijos[0].hijos[0]

    def manual(self):
        fuente = BASE.parent / 'ejemplos_completos/08_asa_manual.qc'
        return self.valido(fuente.read_text(encoding='utf-8'))

    def test_declaraciones(self):
        arbol = self.valido(
            'cafeteria grano g = 1;\ncafeteria poso p;\n'
            + programa('grano x; taza taza grano m = [[1], [2]];')
        )
        self.assertEqual(len(arbol.hijos), 3)
        locales = arbol.hijos[-1].hijos[0].hijos
        self.assertEqual(locales[0].hijos, ())
        self.assertEqual(locales[1].atributos['tipo'], 'taza taza grano')

    def test_funciones(self):
        arbol = self.valido(
            'barista f(grano a, cafe b) { degustar a; }\n'
            'barista g() { degustar; }\n' + programa('')
        )
        self.assertEqual(len(arbol.hijos[0].hijos), 3)
        self.assertEqual(arbol.hijos[-1].atributos['nombre'], 'chorreador')

    def test_llamadas(self):
        arbol = self.valido(programa('f(); f(1, g(2));'))
        llamadas = arbol.hijos[-1].hijos[0].hijos
        self.assertEqual(llamadas[0].hijos, ())
        self.assertEqual(llamadas[1].hijos[1].atributos['nombre'], 'g')

    def test_condiciones(self):
        arbol = self.valido(programa(
            'hierve (fuerte) { hierve (ralo) {} } enfria {}'
        ))
        condicion = arbol.hijos[-1].hijos[0].hijos[0]
        self.assertEqual(len(condicion.hijos), 3)
        self.assertEqual(len(condicion.hijos[1].hijos[0].hijos), 2)

    def test_ciclos(self):
        arbol = self.valido(programa(
            'chorreando (fuerte) { recolar (grano x en lista) {} }'
        ))
        ciclo = arbol.hijos[-1].hijos[0].hijos[0]
        self.assertEqual(ciclo.clase.value, 'Mientras')
        self.assertEqual(ciclo.hijos[1].hijos[0].clase.value, 'ParaCada')

    def test_listas(self):
        arbol = self.valido(programa(
            'taza grano l = []; taza taza grano m = [[1], [2]];'
            'l.insertar(1); l.extraer(0); cafe b = l.buscar(1);'
        ))
        sentencias = arbol.hijos[-1].hijos[0].hijos
        self.assertEqual(sentencias[0].hijos[0].hijos, ())
        self.assertEqual(sentencias[2].atributos['metodo'], 'insertar')

    def test_cuantica(self):
        fuente = BASE.parent / 'ejemplos_completos/06_cuantica.qc'
        arbol = self.valido(fuente.read_text(encoding='utf-8'))
        sentencias = arbol.hijos[-1].hijos[0].hijos
        self.assertEqual(
            [n.atributos['compuerta'] for n in sentencias[2:6]],
            ['X', 'H', 'Z', 'CNOT'],
        )
        self.assertEqual(sentencias[6].hijos[0].clase.value, 'Medicion')

    def test_precedencia(self):
        for texto, operador, derecho in (
            ('2 + 3 * 4', '+', '*'),
            ('a SinAzucar b ConAzucar c', 'SinAzucar', 'ConAzucar'),
            ('Amargo a < b', 'Amargo', '<'),
        ):
            with self.subTest(expresion=texto):
                nodo = self.expresion(texto)
                self.assertEqual(nodo.atributos['operador'], operador)
                self.assertEqual(nodo.hijos[-1].atributos['operador'], derecho)

    def test_asociatividad(self):
        nodo = self.expresion('10 - 3 - 2')
        self.assertEqual(nodo.atributos['operador'], '-')
        self.assertEqual(nodo.hijos[0].atributos['operador'], '-')
        self.assertEqual(nodo.hijos[1].atributos['lexema'], '2')
        unaria = self.expresion('-+5')
        self.assertEqual(unaria.atributos['operador'], '-')
        self.assertEqual(unaria.hijos[0].atributos['operador'], '+')

    def test_parentesis(self):
        nodo = self.expresion('(2 + 3) * 4')
        self.assertEqual(nodo.atributos['operador'], '*')
        self.assertEqual(nodo.hijos[0].atributos['operador'], '+')

    def test_falta_punto_coma(self):
        self.error(programa('grano x = 1'), 'PUNTO_COMA', (3, 1))

    def test_falta_expresion(self):
        self.error(programa('grano x = ;'), 'expresion', (2, 11))

    def test_parentesis_sin_cerrar(self):
        self.error(programa('grano x = (1 + 2;'), 'PARENTESIS_CIERRA', (2, 17))

    def test_bloque_sin_cerrar(self):
        self.error('barista chorreador() {\n', 'LLAVE_CIERRA', (2, 1))

    def test_falta_principal(self):
        self.error(
            'cafeteria grano x;\n', 'Falta la funcion principal', (2, 1)
        )

    def test_codigo_despues_del_principal(self):
        self.error(programa('') + '\nqubit q;', 'mas codigo', (4, 1))

    def test_asa_manual(self):
        self.assertEqual(self.manual().a_dict(), asa_manual().a_dict())

    def test_preorden_esperado(self):
        esperado = BASE / 'esperados/08_asa_manual.preorden.txt'
        self.assertEqual(a_texto(self.manual()), esperado.read_text('utf-8'))
        self.assertEqual(a_texto(asa_manual()), esperado.read_text('utf-8'))

    def test_impresion(self):
        arbol = self.valido(programa('grano x = 1;'))
        salida = StringIO()
        imprimir_preorden(arbol, salida=salida)
        self.assertEqual(salida.getvalue(), (
            '<"Programa", "", "">\n'
            '  <"FuncionPrincipal", "chorreador", "">\n'
            '    <"Bloque", "", "">\n'
            '      <"DeclaracionLocal", "x", "tipo=grano">\n'
            '        <"Literal", "1", "categoria=ENTERO">\n'
        ))

    def test_recuperacion(self):
        resultado = self.analizar(programa('grano a = ; grano b = 2;'))
        self.assertFalse(resultado.correcto)
        self.assertEqual(len(resultado.errores), 1)
        bloque = resultado.arbol.hijos[-1].hijos[0]
        self.assertEqual(len(bloque.hijos), 1)
        self.assertEqual(bloque.hijos[0].atributos['nombre'], 'b')
        self.assertEqual(bloque.hijos[0].hijos[0].atributos['lexema'], '2')


if __name__ == '__main__':
    unittest.main()
