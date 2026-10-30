"""Pruebas del limite scanner/parser/ASA. No ejecutan un parser de produccion."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from parser.integracion import (
    ClaseNodo, ErrorSintactico, FlujoTokens, NodoASA, Posicion,
    RangoFuente, ResultadoParseo, explorar_para_parser,
)
from parser.integracion.entrada import EntradaConErroresLexicos
from scanner import Scanner, Token, TokenType
from scanner.tokens import PALABRAS_RESERVADAS, SIMBOLOS_DOBLES, SIMBOLOS_SIMPLES
from parser.verificacion.ebnf import Gramatica, produccion

ROOT = Path(__file__).resolve().parents[2]


class TestScannerEntrada(unittest.TestCase):
    def test_valores_originales_y_posiciones(self):
        tokens, errores = Scanner('grano x = -12;\n\tservir("café # 01");').escanear()
        self.assertFalse(errores)
        self.assertEqual([(t.tipo.name, t.lexema, t.linea, t.columna) for t in tokens], [
            ('GRANO', 'grano', 1, 1), ('IDENTIFICADOR', 'x', 1, 7),
            ('ASIGNACION', '=', 1, 9), ('RESTA', '-', 1, 11),
            ('ENTERO', '12', 1, 12), ('PUNTO_COMA', ';', 1, 14),
            ('IDENTIFICADOR', 'servir', 2, 2), ('PARENTESIS_ABRE', '(', 2, 8),
            ('CADENA', '"café # 01"', 2, 9), ('PARENTESIS_CIERRA', ')', 2, 20),
            ('PUNTO_COMA', ';', 2, 21),
        ])

    def test_todos_los_terminales_y_maxima_coincidencia(self):
        for lexema, tipo in {**PALABRAS_RESERVADAS, **SIMBOLOS_DOBLES, **SIMBOLOS_SIMPLES}.items():
            with self.subTest(lexema=lexema):
                tokens, errores = Scanner(lexema).escanear()
                self.assertFalse(errores)
                self.assertEqual(len(tokens), 1)
                self.assertIs(tokens[0].tipo, tipo)
        t, e = Scanner('<= >= == != < > =').escanear()
        self.assertFalse(e)
        self.assertEqual([x.lexema for x in t], ['<=', '>=', '==', '!=', '<', '>', '='])

    def test_lf_crlf_y_cr_con_comentarios(self):
        for salto in ['\n', '\r\n', '\r']:
            with self.subTest(salto=repr(salto)):
                e = explorar_para_parser('# inicio' + salto + 'grano x;' + salto + '# final' + salto)
                self.assertTrue(e.apta)
                self.assertEqual([(t.lexema, t.linea, t.columna) for t in e.tokens],
                                 [('grano', 2, 1), ('x', 2, 7), (';', 2, 8), ('', 4, 1)])

    def test_saltos_mezclados(self):
        e = explorar_para_parser('a\r\nb\rc\nd')
        self.assertEqual([(t.linea, t.columna) for t in e.tokens], [(1,1),(2,1),(3,1),(4,1),(4,2)])

    def test_eof_despues_de_ignorables(self):
        e = explorar_para_parser('x;\n  # cola')
        self.assertEqual(e.tokens[-1], Token(TokenType.FIN_ARCHIVO, '', 2, 9))
        self.assertEqual(sum(t.tipo is TokenType.FIN_ARCHIVO for t in e.tokens), 1)
        self.assertFalse(any(t.tipo is TokenType.FIN_ARCHIVO for t in Scanner('x;').escanear()[0]))

    def test_entrada_vacia_y_bom(self):
        for texto in ['', '\ufeff']:
            self.assertEqual(explorar_para_parser(texto).tokens, (Token(TokenType.FIN_ARCHIVO, '', 1, 1),))
        e = explorar_para_parser('\ufeffgrano x;')
        self.assertTrue(e.apta)
        self.assertEqual(e.tokens[0].columna, 1)
        self.assertFalse(explorar_para_parser('grano\ufeff x;').apta)

    def test_error_no_desaparece_antes_del_parser(self):
        e = explorar_para_parser('grano x = @5;')
        self.assertFalse(e.apta)
        self.assertEqual((e.errores_lexicos[0].lexema, e.errores_lexicos[0].linea,
                          e.errores_lexicos[0].columna), ('@', 1, 11))
        self.assertEqual([t.lexema for t in e.tokens], ['grano','x','=','5',';',''])
        with self.assertRaises(EntradaConErroresLexicos):
            e.tokens_para_parser()

    def test_cadena_sin_cerrar_recupera_en_siguiente_linea(self):
        for salto in ['\n', '\r', '\r\n']:
            e = explorar_para_parser('"sin cerrar' + salto + 'grano x;')
            self.assertFalse(e.apta)
            self.assertEqual(len(e.errores_lexicos), 1)
            self.assertEqual(e.tokens[0].linea, 2)

    def test_valores_no_se_convierten(self):
        numero = '9' * 5000
        e = explorar_para_parser('00012 01.50 "" "a\\n" ' + numero)
        self.assertTrue(e.apta)
        self.assertEqual([t.lexema for t in e.tokens[:-1]], ['00012','01.50','""','"a\\n"',numero])

    def test_errores_y_tokens_originales(self):
        fuente = 'grano x; @ "sin cerrar'
        t, err = Scanner(fuente).escanear()
        e = explorar_para_parser(fuente)
        self.assertEqual(tuple(t), e.tokens[:-1])
        self.assertEqual(tuple(err), e.errores_lexicos)

    def test_identificadores_y_tipos_heredados(self):
        t, _ = Scanner('servir leer servirX Grano insertar').escanear()
        self.assertEqual([x.tipo for x in t], [TokenType.IDENTIFICADOR]*4 + [TokenType.INSERTAR])
        self.assertFalse(any(x.tipo in (TokenType.SERVIR, TokenType.LEER) for x in t))

    def test_cli_directo_y_modulo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p = Path(carpeta) / 'ejemplo.qc'
            p.write_bytes(b'\xef\xbb\xbfgrano x;\r\n')
            a = subprocess.run([sys.executable, 'scanner/main.py', str(p)], cwd=ROOT, capture_output=True)
            b = subprocess.run([sys.executable, '-m', 'scanner.main', str(p)], cwd=ROOT, capture_output=True)
            self.assertEqual(a.returncode, 0, a.stderr)
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertEqual(a.stdout, b.stdout)

    def test_resultados_esperados(self):
        archivos = {
            'cadenas_comentarios.qc': 'cadena_cometarios_esperado.txt',
            'cuantica.qc': 'cuantica.esperado.txt',
            'listas_control.qc': 'lista_control_esperado.txt',
            'numeros_operadores.qc': 'numeros_operadores_esperado.txt',
            'tipos_variables.qc': 'tipos_variables.esperado.txt',
        }
        for archivo, esperado in archivos.items():
            with self.subTest(archivo=archivo):
                base = ROOT / 'scanner/ejemplos'
                t, e = Scanner((base/archivo).read_text(encoding='utf-8-sig')).escanear()
                actual = ''.join(str(x)+'\n' for x in [*t, *e])
                self.assertEqual(actual, (base/esperado).read_text(encoding='utf-8'))


class TestFlujoYASA(unittest.TestCase):
    def test_cursor_y_eof_estable(self):
        entrada = explorar_para_parser('x = 1;')
        flujo = FlujoTokens(entrada.tokens_para_parser())
        self.assertIs(flujo.mirar(), entrada.tokens[0])
        self.assertIs(flujo.mirar(1), entrada.tokens[1])
        self.assertIs(flujo.avanzar(), entrada.tokens[0])
        while not flujo.en_fin:
            flujo.avanzar()
        i = flujo.indice
        for _ in range(5):
            self.assertIs(flujo.avanzar(), entrada.tokens[-1])
            self.assertIs(flujo.mirar(100), entrada.tokens[-1])
        self.assertEqual(i, flujo.indice)
        with self.assertRaises(ValueError):
            flujo.mirar(-1)

    def test_secuencia_sin_fin_o_con_fin_duplicado(self):
        fin = Token(TokenType.FIN_ARCHIVO, '', 1, 1)
        for tokens in [[], [Token(TokenType.ENTERO,'1',1,1)], [fin,fin]]:
            with self.assertRaises(ValueError):
                FlujoTokens(tokens)

    def test_rangos_y_serializacion_sin_evaluar(self):
        token = Token(TokenType.CADENA, '"hola"', 2, 4)
        rango = RangoFuente.de_token(token)
        self.assertEqual(rango.fin, Posicion(2,10))
        atributos = {'categoria':'CADENA', 'lexema':token.lexema}
        nodo = NodoASA(ClaseNodo.LITERAL, rango, atributos)
        atributos['lexema'] = 'alterado'
        self.assertEqual(nodo.atributos['lexema'], '"hola"')
        datos = json.loads(json.dumps(nodo.a_dict(), ensure_ascii=False))
        self.assertEqual(datos['atributos']['lexema'], '"hola"')
        with self.assertRaises(TypeError):
            nodo.atributos['lexema'] = 'otro'
        with self.assertRaises(ValueError):
            Posicion(0,1)
        with self.assertRaises(ValueError):
            RangoFuente(Posicion(2,1), Posicion(1,1))

    def test_resultado_y_diagnostico(self):
        t = Token(TokenType.FIN_ARCHIVO,'',1,1)
        err = ErrorSintactico('Se esperaba barista',t,(TokenType.BARISTA,))
        self.assertFalse(ResultadoParseo(None,(err,)).correcto)
        nodo = NodoASA(ClaseNodo.PROGRAMA,RangoFuente.de_token(t))
        self.assertTrue(ResultadoParseo(nodo).correcto)
        self.assertFalse(ResultadoParseo(nodo,(err,)).correcto)

    def test_traspaso_a_receptor_sin_sustituir_scanner(self):
        entrada = explorar_para_parser('barista chorreador() {}')
        recibido = []
        # Solo receptor de prueba de la interfaz, no implementacion del parser.
        def receptor(tokens):
            recibido.extend(tokens)
            return ResultadoParseo(None)
        receptor(entrada.tokens_para_parser())
        self.assertTrue(all(a is b for a,b in zip(recibido, entrada.tokens)))


class TestAuditoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Gramatica(ROOT/'docs/Documentacion.md')

    def test_unico_conflicto_resoluble_con_barista_y_siguiente(self):
        self.assertEqual(len(self.g.conflictos),1)
        self.assertEqual(self.g.conflictos[0][0],'programa')
        self.assertEqual(self.g.conflictos[0][4],['BARISTA'])
        self.assertEqual(self.g.first['declaracion_funcion'],{'BARISTA'})
        self.assertEqual(self.g.first['declaracion_chorreador'],{'BARISTA'})

    def test_no_confundir_categoria_y_lexema(self):
        # El reconocedor previo comparaba terminales por texto, no por TokenType.
        falsos = [Token(TokenType.IDENTIFICADOR,'barista',1,1)]
        reales = explorar_para_parser('barista chorreador() {}').tokens
        self.assertFalse(self.g.acepta(falsos + list(reales[1:])))

    def test_sintaxis_sin_semantica(self):
        for cuerpo in ['grano x="texto";', 'hierve(5) {}', 'desconocida();', 'leer(1); servir();']:
            self.assertTrue(self.g.acepta(explorar_para_parser('barista chorreador(){'+cuerpo+'}').tokens))

    def test_ebnf_mal_formada_no_se_ignora(self):
        for texto in ['"x" @', '"x" |', '{ "x"', '"x" )']:
            with self.assertRaises(ValueError):
                produccion(texto)

    def test_rechazar_gramatica_con_problemas(self):
        for texto in [
            'programa ::= programa "x"',
            'programa ::= otro\notro ::= programa',
            'programa ::= inexistente',
            'programa ::= "@"',
            'programa ::= "barista"\nsobra ::= "grano"',
            'programa ::= { [ "grano" ] }',
            'programa ::= "barista"\nprograma ::= "grano"',
            'programa ::= "barista" programa',
        ]:
            with self.subTest(texto=texto), tempfile.TemporaryDirectory() as carpeta:
                p = Path(carpeta)/'g.md'
                p.write_text('```ebnf\n'+texto+'\n```',encoding='utf-8')
                with self.assertRaises(ValueError):
                    Gramatica(p)


if __name__ == '__main__':
    unittest.main()
