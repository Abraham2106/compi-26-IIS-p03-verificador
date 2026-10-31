"""Pruebas de los bloques sintacticos de Quantum Coffee."""

import unittest

from parser.errores_sintacticos import ControlSintactico, FalloSintactico
from parser.integracion import (
    ClaseNodo,
    FlujoTokens,
    NodoASA,
    RangoFuente,
    ResultadoParseo,
    explorar_para_parser,
)
from parser.producciones_control import ProduccionesControl
from scanner import TokenType
from parser.producciones_cuanticas import ProduccionesCuanticas

def crear_control(fuente):
    entrada = explorar_para_parser(fuente)
    return ControlSintactico(FlujoTokens(entrada.tokens_para_parser()))


class TestBloques(unittest.TestCase):
    def test_bloque_vacio(self):
        control = crear_control("{}")
        producciones = ProduccionesControl(control, lambda: None)

        nodo = producciones.bloque()

        self.assertEqual(nodo.clase, ClaseNodo.BLOQUE)
        self.assertEqual(nodo.hijos, ())
        self.assertEqual(nodo.rango.fin.columna, 3)
        self.assertEqual(control.flujo.mirar().tipo, TokenType.FIN_ARCHIVO)

    def test_bloque_con_sentencia(self):
        control = crear_control("{ x = 1; }")

        # Simula una sentencia hasta integrar el parser del punto 3.
        def analizar_sentencia():
            inicio = control.esperar(TokenType.IDENTIFICADOR)
            control.esperar(TokenType.ASIGNACION)
            control.esperar(TokenType.ENTERO)
            fin = control.esperar(TokenType.PUNTO_COMA)

            rango = RangoFuente(
                RangoFuente.de_token(inicio).inicio,
                RangoFuente.de_token(fin).fin,
            )
            return NodoASA(ClaseNodo.ASIGNACION, rango)

        nodo = ProduccionesControl(control, analizar_sentencia).bloque()

        self.assertEqual(len(nodo.hijos), 1)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.ASIGNACION)

    def test_llave_final_faltante(self):
        control = crear_control("{")
        producciones = ProduccionesControl(control, lambda: None)

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.bloque()

        self.assertIn(
            "fin de archivo",
            resultado.exception.error.mensaje,
        )

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.LLAVE_CIERRA,),
        )

    def test_bloque_con_sentencias_cuanticas(self):
        fuente = """
        {
            qubit q0;
            qubit q1;
            H(q0);
            CNOT(q0, q1);
            medir(q0);
        }
        """

        control = crear_control(fuente)

        # Las producciones comparten el mismo flujo de tokens.
        cuanticas = ProduccionesCuanticas(control)

        producciones = ProduccionesControl(
            control,
            cuanticas.sentencia_cuantica,
        )

        nodo = producciones.bloque()

        self.assertEqual(nodo.clase, ClaseNodo.BLOQUE)
        self.assertEqual(len(nodo.hijos), 5)

        self.assertEqual(
            tuple(hijo.clase for hijo in nodo.hijos),
            (
                ClaseNodo.QUBIT,
                ClaseNodo.QUBIT,
                ClaseNodo.COMPUERTA,
                ClaseNodo.COMPUERTA,
                ClaseNodo.MEDICION,
            ),
        )

        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_error_punto_coma_en_bloque(self):
        fuente = "{ H(q0) }"

        control = crear_control(fuente)
        cuanticas = ProduccionesCuanticas(control)

        producciones = ProduccionesControl(
            control,
            cuanticas.sentencia_cuantica,
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.bloque()

        error = resultado.exception.error

        self.assertEqual(
            error.esperados,
            (TokenType.PUNTO_COMA,),
        )

        self.assertEqual(
            error.encontrado.tipo,
            TokenType.LLAVE_CIERRA,
        )

        self.assertEqual(error.encontrado.linea, 1)

    def test_error_llave_faltante_en_bloque(self):
        fuente = "{ qubit q0;"

        control = crear_control(fuente)
        cuanticas = ProduccionesCuanticas(control)

        producciones = ProduccionesControl(
            control,
            cuanticas.sentencia_cuantica,
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.bloque()

        error = resultado.exception.error

        self.assertEqual(
            error.esperados,
            (TokenType.LLAVE_CIERRA,),
        )

        self.assertEqual(
            error.encontrado.tipo,
            TokenType.FIN_ARCHIVO,
        )

        self.assertIn("fin de archivo", error.mensaje)

    def test_recuperacion_dentro_de_bloque(self):
        fuente = "{ qubit q0; H(10); qubit q1; }"

        control = crear_control(fuente)
        cuanticas = ProduccionesCuanticas(control)

        producciones = ProduccionesControl(
            control,
            cuanticas.sentencia_cuantica,
            recuperar_errores=True,
        )

        nodo = producciones.bloque()

        # Las dos declaraciones validas se conservaron.
        self.assertEqual(len(nodo.hijos), 2)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.QUBIT)
        self.assertEqual(nodo.hijos[1].clase, ClaseNodo.QUBIT)

        # El error de H(10) quedo registrado.
        self.assertEqual(len(control.errores), 1)
        self.assertEqual(
            control.errores[0].encontrado.tipo,
            TokenType.ENTERO,
        )

        # Un arbol parcial con errores no es valido.
        resultado = ResultadoParseo(
            arbol=nodo,
            errores=tuple(control.errores),
        )

        self.assertFalse(resultado.correcto)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )


class TestCondicionales(unittest.TestCase):
    """Pruebas de las estructuras hierve y enfria."""

    def crear_producciones(self, fuente):
        control = crear_control(fuente)

        # Simulamos el analizador de expresiones del punto 3.
        def analizar_expresion():
            token = control.esperar(TokenType.FUERTE)

            return NodoASA(
                clase=ClaseNodo.LITERAL,
                rango=RangoFuente.de_token(token),
                atributos={
                    "categoria": token.tipo.name,
                    "lexema": token.lexema,
                },
            )

        producciones = ProduccionesControl(
            control,
            lambda: None,
            analizar_expresion,
        )

        return control, producciones

    def test_hierve_sin_enfria(self):
        control, producciones = self.crear_producciones("hierve (fuerte) {}")

        nodo = producciones.condicional()

        self.assertEqual(nodo.clase, ClaseNodo.CONDICIONAL)
        self.assertEqual(len(nodo.hijos), 2)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.LITERAL)
        self.assertEqual(nodo.hijos[1].clase, ClaseNodo.BLOQUE)
        self.assertEqual(control.flujo.mirar().tipo, TokenType.FIN_ARCHIVO)

    def test_hierve_con_enfria(self):
        control, producciones = self.crear_producciones("hierve (fuerte) {} enfria {}")

        nodo = producciones.condicional()

        self.assertEqual(nodo.clase, ClaseNodo.CONDICIONAL)
        self.assertEqual(len(nodo.hijos), 3)
        self.assertEqual(nodo.hijos[2].clase, ClaseNodo.BLOQUE)
        self.assertEqual(control.flujo.mirar().tipo, TokenType.FIN_ARCHIVO)

    def test_parentesis_faltante(self):
        control, producciones = self.crear_producciones("hierve (fuerte {}")

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.condicional()

        error = resultado.exception.error

        self.assertEqual(
            error.esperados,
            (TokenType.PARENTESIS_CIERRA,),
        )
        self.assertEqual(
            error.encontrado.tipo,
            TokenType.LLAVE_ABRE,
        )

    def test_estructuras_anidadas(self):
        fuente = """
        barista chorreador() {
            qubit q0;
            hierve (fuerte) {
                H(q0);
            }
            chorreando (fuerte) {
                X(q0);
            }
        }
        """

        control = crear_control(fuente)
        cuanticas = ProduccionesCuanticas(control)

        # Simulacion de expresiones del punto 3.
        def analizar_expresion():
            token = control.esperar(TokenType.FUERTE)
            return NodoASA(
                clase=ClaseNodo.LITERAL,
                rango=RangoFuente.de_token(token),
                atributos={
                    "categoria": token.tipo.name,
                    "lexema": token.lexema,
                },
            )

        # Seleccionar la produccion segun el token actual.
        def analizar_sentencia():
            tipo = control.flujo.mirar().tipo

            if tipo == TokenType.HIERVE:
                return estructuras.condicional()

            if tipo == TokenType.CHORREANDO:
                return estructuras.chorreando()

            return cuanticas.sentencia_cuantica()

        estructuras = ProduccionesControl(
            control,
            analizar_sentencia,
            analizar_expresion,
        )

        nodo = estructuras.chorreador()

        self.assertEqual(nodo.clase, ClaseNodo.PRINCIPAL)

        cuerpo = nodo.hijos[0]
        self.assertEqual(cuerpo.clase, ClaseNodo.BLOQUE)
        self.assertEqual(len(cuerpo.hijos), 3)

        self.assertEqual(cuerpo.hijos[0].clase, ClaseNodo.QUBIT)
        self.assertEqual(cuerpo.hijos[1].clase, ClaseNodo.CONDICIONAL)
        self.assertEqual(cuerpo.hijos[2].clase, ClaseNodo.MIENTRAS)

        self.assertEqual(
            cuerpo.hijos[1].hijos[1].hijos[0].clase,
            ClaseNodo.COMPUERTA,
        )
        self.assertEqual(
            cuerpo.hijos[2].hijos[1].hijos[0].clase,
            ClaseNodo.COMPUERTA,
        )

        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )


class TestCiclos(unittest.TestCase):
    """Pruebas de ciclos de Quantum Coffee."""

    def test_chorreando(self):
        control = crear_control("chorreando (fuerte) {}")

        def analizar_expresion():
            token = control.esperar(TokenType.FUERTE)

            return NodoASA(
                clase=ClaseNodo.LITERAL,
                rango=RangoFuente.de_token(token),
                atributos={
                    "categoria": token.tipo.name,
                    "lexema": token.lexema,
                },
            )

        producciones = ProduccionesControl(
            control,
            lambda: None,
            analizar_expresion,
        )

        nodo = producciones.chorreando()

        self.assertEqual(nodo.clase, ClaseNodo.MIENTRAS)
        self.assertEqual(len(nodo.hijos), 2)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.LITERAL)
        self.assertEqual(nodo.hijos[1].clase, ClaseNodo.BLOQUE)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_recolar(self):
        control = crear_control("recolar (grano cantidad en inventario) {}")

        def analizar_tipo():
            token = control.esperar(TokenType.GRANO)
            return token.lexema

        producciones = ProduccionesControl(
            control,
            lambda: None,
            analizar_tipo=analizar_tipo,
        )

        nodo = producciones.recolar()

        self.assertEqual(nodo.clase, ClaseNodo.PARA_CADA)
        self.assertEqual(nodo.atributos["tipo"], "grano")
        self.assertEqual(nodo.atributos["nombre"], "cantidad")
        self.assertEqual(nodo.atributos["lista"], "inventario")
        self.assertEqual(len(nodo.hijos), 1)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.BLOQUE)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )


class TestFunciones(unittest.TestCase):
    """Pruebas de declaraciones de funciones barista."""

    def test_funcion_sin_parametros(self):
        control = crear_control("barista preparar() {}")

        producciones = ProduccionesControl(
            control,
            lambda: None,
        )

        nodo = producciones.funcion()

        self.assertEqual(nodo.clase, ClaseNodo.FUNCION)
        self.assertEqual(nodo.atributos["nombre"], "preparar")
        self.assertEqual(len(nodo.hijos), 1)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.BLOQUE)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_funcion_con_parametros(self):
        control = crear_control("barista preparar(grano cantidad, cafe listo) {}")

        def analizar_tipo():
            token = control.esperar(
                TokenType.GRANO,
                TokenType.CAFE,
            )
            return token.lexema

        producciones = ProduccionesControl(
            control,
            lambda: None,
            analizar_tipo=analizar_tipo,
        )

        nodo = producciones.funcion()

        self.assertEqual(nodo.clase, ClaseNodo.FUNCION)
        self.assertEqual(len(nodo.hijos), 3)

        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.PARAMETRO)
        self.assertEqual(
            nodo.hijos[0].atributos["nombre"],
            "cantidad",
        )
        self.assertEqual(
            nodo.hijos[0].atributos["tipo"],
            "grano",
        )

        self.assertEqual(nodo.hijos[1].clase, ClaseNodo.PARAMETRO)
        self.assertEqual(
            nodo.hijos[1].atributos["tipo"],
            "cafe",
        )

        self.assertEqual(nodo.hijos[2].clase, ClaseNodo.BLOQUE)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_chorreador(self):
        control = crear_control("barista chorreador() {}")

        producciones = ProduccionesControl(
            control,
            lambda: None,
        )

        nodo = producciones.chorreador()

        self.assertEqual(nodo.clase, ClaseNodo.PRINCIPAL)
        self.assertEqual(nodo.atributos["nombre"], "chorreador")
        self.assertEqual(len(nodo.hijos), 1)
        self.assertEqual(nodo.hijos[0].clase, ClaseNodo.BLOQUE)
        self.assertEqual(
            control.flujo.mirar().tipo,
            TokenType.FIN_ARCHIVO,
        )

    def test_chorreador_con_parametros(self):
        control = crear_control("barista chorreador(grano cantidad) {}")

        producciones = ProduccionesControl(
            control,
            lambda: None,
        )

        with self.assertRaises(FalloSintactico) as resultado:
            producciones.chorreador()

        self.assertEqual(
            resultado.exception.error.esperados,
            (TokenType.PARENTESIS_CIERRA,),
        )


if __name__ == "__main__":
    unittest.main()
