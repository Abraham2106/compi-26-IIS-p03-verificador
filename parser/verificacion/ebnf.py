"""
Auditoria estricta de EBNF y reconocedor de pruebas, no parser de
produccion.
"""

import re
from functools import lru_cache
from pathlib import Path

from scanner.tokens import (
    PALABRAS_RESERVADAS,
    SIMBOLOS_DOBLES,
    SIMBOLOS_SIMPLES,
    TokenType,
)

LEXICOS = {
    "identificador": TokenType.IDENTIFICADOR,
    "numero_entero": TokenType.ENTERO,
    "numero_decimal": TokenType.DECIMAL,
    "cadena": TokenType.CADENA,
}
SOLO_LEXICOS = set(LEXICOS) | {
    "letra",
    "digito",
    "caracter_cadena",
    "comentario",
}
CATALOGO = {**PALABRAS_RESERVADAS, **SIMBOLOS_DOBLES, **SIMBOLOS_SIMPLES}


def tokenizar_ebnf(texto):
    patron = re.compile(r'\s+|"[^"\r\n]*"|[A-Za-z_][A-Za-z_0-9]*|[{}\[\]()|]')
    salida = []
    posicion = 0
    while posicion < len(texto):
        m = patron.match(texto, posicion)
        if not m:
            raise ValueError(
                f"EBNF invalida cerca de {texto[posicion : posicion + 30]!r}"
            )
        if not m[0].isspace():
            salida.append(m[0])
        posicion = m.end()
    return salida


def produccion(texto):
    tokens = tokenizar_ebnf(texto)
    posicion = 0

    def alternativa(cierre=None):
        nonlocal posicion
        ramas = [secuencia(cierre)]
        while posicion < len(tokens) and tokens[posicion] == "|":
            posicion += 1
            ramas.append(secuencia(cierre))
        return ("alt", ramas)

    def secuencia(cierre):
        nonlocal posicion
        nodos = []
        while posicion < len(tokens) and tokens[posicion] not in ("|", cierre):
            t = tokens[posicion]
            posicion += 1
            if t in ("{", "[", "("):
                fin = {"{": "}", "[": "]", "(": ")"}[t]
                contenido = alternativa(fin)
                if posicion >= len(tokens) or tokens[posicion] != fin:
                    raise ValueError(f"EBNF: falta cierre {fin}")
                posicion += 1
                nodos.append(
                    ({"{": "star", "[": "opt", "(": "group"}[t], contenido)
                )
            elif t.startswith('"'):
                nodos.append(("terminal", t[1:-1]))
            elif t in ("}", "]", ")"):
                raise ValueError(f"EBNF: cierre inesperado {t}")
            else:
                nodos.append(("ref", t))
        if not nodos:
            raise ValueError(
                "EBNF: alternativa vacia; usar una parte opcional explicita"
            )
        return ("seq", nodos)

    resultado = alternativa()
    if posicion != len(tokens):
        raise ValueError("EBNF: texto sobrante")
    return resultado


def referencias(nodo, clase="ref"):
    k, v = nodo
    if k in ("ref", "terminal"):
        return {v} if k == clase else set()
    if k in ("star", "opt", "group"):
        return referencias(v, clase)
    return set().union(*(referencias(h, clase) for h in v))


class Gramatica:
    def __init__(self, ruta):
        texto = Path(ruta).read_text(encoding="utf-8")
        fuente = "\n".join(re.findall(r"```ebnf\n(.*?)```", texto, re.S))
        fuente = re.sub(r"\(\*.*?\*\)", "", fuente, flags=re.S)
        marcas = list(re.finditer(r"(?m)^([a-z_]+)\s*::=", fuente))
        self.reglas = {}
        nombres = set()
        for i, marca in enumerate(marcas):
            nombre = marca[1]
            if nombre in nombres:
                raise ValueError(f"Produccion duplicada: {nombre}")
            nombres.add(nombre)
            if nombre in SOLO_LEXICOS:
                continue
            limite = (
                marcas[i + 1].start() if i + 1 < len(marcas) else len(fuente)
            )
            self.reglas[nombre] = produccion(fuente[marca.end() : limite])
        if "programa" not in self.reglas:
            raise ValueError("Falta la produccion inicial programa")
        refs = set().union(*(referencias(n) for n in self.reglas.values()))
        faltantes = refs - set(self.reglas) - set(LEXICOS)
        if faltantes:
            raise ValueError(f"Producciones sin definir: {sorted(faltantes)}")
        self.terminales = set().union(
            *(referencias(n, "terminal") for n in self.reglas.values())
        )
        if self.terminales - set(CATALOGO):
            raise ValueError(
                f"Terminales sin token: {self.terminales - set(CATALOGO)}"
            )
        self.nullable = set()
        while True:
            nuevos = {k for k, n in self.reglas.items() if self.anulable(n)}
            if nuevos <= self.nullable:
                break
            self.nullable |= nuevos
        self.comprobar_estructura()
        self.construir_bnf()
        self.calcular_first_follow()

    def anulable(self, nodo):
        k, v = nodo
        if k in ("opt", "star"):
            return True
        if k == "group":
            return self.anulable(v)
        if k == "seq":
            return all(self.anulable(h) for h in v)
        if k == "alt":
            return any(self.anulable(h) for h in v)
        return k == "ref" and v in self.nullable

    def iniciales(self, nodo):
        k, v = nodo
        if k == "ref":
            return {v}
        if k == "terminal":
            return set()
        if k in ("group", "star", "opt"):
            return self.iniciales(v)
        resultado = set()
        for hijo in v:
            resultado |= self.iniciales(hijo)
            if k == "seq" and not self.anulable(hijo):
                break
        return resultado

    def comprobar_estructura(self):
        productivas = set(LEXICOS)

        def produce(n):
            k, v = n
            if k in ("terminal", "star", "opt"):
                return True
            if k == "ref":
                return v in productivas
            if k == "group":
                return produce(v)
            return (
                all(produce(h) for h in v)
                if k == "seq"
                else any(produce(h) for h in v)
            )

        while True:
            nuevas = {k for k, n in self.reglas.items() if produce(n)}
            if nuevas <= productivas:
                break
            productivas |= nuevas
        if set(self.reglas) - productivas:
            raise ValueError(
                "Producciones improductivas: "
                f"{sorted(set(self.reglas) - productivas)}"
            )

        def repetir(n):
            k, v = n
            if k == "star" and self.anulable(v):
                raise ValueError("Repeticion sin consumo de entrada")
            if k in ("group", "opt", "star"):
                repetir(v)
            elif k in ("seq", "alt"):
                for hijo in v:
                    repetir(hijo)

        grafo = {k: self.iniciales(n) for k, n in self.reglas.items()}
        for origen in self.reglas:
            pendientes = list(grafo[origen])
            vistos = set()
            while pendientes:
                actual = pendientes.pop()
                if actual == origen:
                    raise ValueError(f"Recursion por la izquierda en {origen}")
                if actual not in vistos:
                    vistos.add(actual)
                    pendientes.extend(grafo.get(actual, ()))
            repetir(self.reglas[origen])
        alcanzables = set()
        pendientes = ["programa"]
        while pendientes:
            actual = pendientes.pop()
            if actual not in alcanzables:
                alcanzables.add(actual)
                if actual in self.reglas:
                    pendientes.extend(referencias(self.reglas[actual]))
        sobrantes = set(self.reglas) - alcanzables
        if sobrantes:
            raise ValueError(
                f"Producciones inalcanzables: {sorted(sobrantes)}"
            )

    def construir_bnf(self):
        self.bnf = {}
        self.dueno = {}
        contador = 0

        def convertir(n, origen):
            nonlocal contador
            k, v = n
            if k == "terminal":
                return "T:" + CATALOGO[v].name
            if k == "ref":
                return "T:" + LEXICOS[v].name if v in LEXICOS else "N:" + v
            contador += 1
            nombre = f"{origen}@{contador}"
            simbolo = "N:" + nombre
            self.dueno[nombre] = origen
            if k == "seq":
                self.bnf[nombre] = [tuple(convertir(h, origen) for h in v)]
            elif k == "alt":
                self.bnf[nombre] = [(convertir(h, origen),) for h in v]
            else:
                hijo = convertir(v, origen)
                self.bnf[nombre] = {
                    "group": [(hijo,)],
                    "opt": [(hijo,), ()],
                    "star": [(hijo, simbolo), ()],
                }[k]
            return simbolo

        for nombre, nodo in self.reglas.items():
            self.dueno[nombre] = nombre
            self.bnf[nombre] = [(convertir(nodo, nombre),)]

    def first_secuencia(self, secuencia):
        resultado = set()
        for simbolo in secuencia:
            parte = (
                {simbolo[2:]}
                if simbolo.startswith("T:")
                else self.first[simbolo[2:]]
            )
            resultado |= parte - {"EPSILON"}
            if "EPSILON" not in parte:
                return resultado
        return resultado | {"EPSILON"}

    def calcular_first_follow(self):
        self.first = {k: set() for k in self.bnf}
        self.follow = {k: set() for k in self.bnf}
        self.follow["programa"].add("FIN_ARCHIVO")
        cambio = True
        while cambio:
            cambio = False
            for nombre, ramas in self.bnf.items():
                nuevos = set().union(*(self.first_secuencia(r) for r in ramas))
                if not nuevos <= self.first[nombre]:
                    self.first[nombre] |= nuevos
                    cambio = True
        cambio = True
        while cambio:
            cambio = False
            for nombre, ramas in self.bnf.items():
                for rama in ramas:
                    for i, simbolo in enumerate(rama):
                        if simbolo.startswith("N:"):
                            destino = simbolo[2:]
                            siguientes = self.first_secuencia(rama[i + 1 :])
                            nuevos = siguientes - {"EPSILON"}
                            if "EPSILON" in siguientes:
                                nuevos |= self.follow[nombre]
                            if not nuevos <= self.follow[destino]:
                                self.follow[destino] |= nuevos
                                cambio = True
        self.conflictos = []
        for nombre, ramas in self.bnf.items():
            predicciones = []
            for rama in ramas:
                f = self.first_secuencia(rama)
                predicciones.append(
                    (f - {"EPSILON"})
                    | (self.follow[nombre] if "EPSILON" in f else set())
                )
            for i, a in enumerate(predicciones):
                for j in range(i + 1, len(predicciones)):
                    compartidos = a & predicciones[j]
                    if compartidos:
                        self.conflictos.append(
                            (
                                self.dueno[nombre],
                                nombre,
                                i,
                                j,
                                sorted(compartidos),
                            )
                        )

    def acepta(self, tokens):
        tokens = tuple(tokens)
        if tokens and tokens[-1].tipo is TokenType.FIN_ARCHIVO:
            tokens = tokens[:-1]

        @lru_cache(None)
        def regla(nombre, posicion):
            if nombre in LEXICOS:
                return (
                    frozenset({posicion + 1})
                    if posicion < len(tokens)
                    and tokens[posicion].tipo is LEXICOS[nombre]
                    else frozenset()
                )
            return reconocer(self.reglas[nombre], posicion)

        def reconocer(n, posicion):
            k, v = n
            if k == "terminal":
                return (
                    frozenset({posicion + 1})
                    if posicion < len(tokens)
                    and tokens[posicion].tipo is CATALOGO[v]
                    else frozenset()
                )
            if k == "ref":
                return regla(v, posicion)
            if k == "group":
                return reconocer(v, posicion)
            if k == "alt":
                return frozenset().union(*(reconocer(h, posicion) for h in v))
            if k == "seq":
                finales = {posicion}
                for hijo in v:
                    finales = {
                        fin
                        for inicio in finales
                        for fin in reconocer(hijo, inicio)
                    }
                return frozenset(finales)
            if k == "opt":
                return frozenset({posicion}) | reconocer(v, posicion)
            finales = {posicion}
            pendientes = [posicion]
            while pendientes:
                for fin in reconocer(v, pendientes.pop()):
                    if fin not in finales:
                        finales.add(fin)
                        pendientes.append(fin)
            return frozenset(finales)

        return len(tokens) in regla("programa", 0)
