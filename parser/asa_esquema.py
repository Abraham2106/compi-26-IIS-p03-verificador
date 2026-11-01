"""Esquema del ASA segun la gramatica.

`ClaseNodo` y `NodoASA` (en `integracion/contratos.py`) son los tipos de
nodo y la estructura del arbol. Este modulo documenta, para cada clase, los
atributos de texto que debe llevar y la forma exacta de sus hijos, y ofrece
`validar_arbol` para comprobar que un arbol construido (por el parser o a
mano) respeta esa forma. No evalua semantica: solo estructura.
"""

import re
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from parser.integracion import ClaseNodo as C, NodoASA
from scanner import TokenType

EXPRESIONES = frozenset(
    {
        C.BINARIA,
        C.UNARIA,
        C.IDENTIFICADOR,
        C.LITERAL,
        C.LISTA,
        C.LLAMADA,
        C.OPERACION_LISTA,
        C.MEDICION,
    }
)

SENTENCIAS = frozenset(
    {
        C.LOCAL,
        C.ASIGNACION,
        C.LLAMADA,
        C.OPERACION_LISTA,
        C.CONDICIONAL,
        C.MIENTRAS,
        C.PARA_CADA,
        C.RETORNO,
        C.QUBIT,
        C.COMPUERTA,
        C.MEDICION,
    }
)

DECLARACIONES = frozenset({C.GLOBAL, C.FUNCION})

# Un hueco del patron de hijos: clases admitidas, minimo y maximo
# (None = sin tope).
Hueco = Tuple[frozenset, int, "int | None"]


def _uno(clases) -> Hueco:
    return (frozenset(clases), 1, 1)


def _opcional(clases) -> Hueco:
    return (frozenset(clases), 0, 1)


def _muchos(clases) -> Hueco:
    return (frozenset(clases), 0, None)


@dataclass(frozen=True)
class EsquemaNodo:
    produccion: str  # produccion de la EBNF que lo origina
    atributos: frozenset  # claves de texto exactas
    hijos: Tuple[Hueco, ...] = ()  # patron ordenado de hijos


ESQUEMA = {
    C.PROGRAMA: EsquemaNodo(
        "programa", frozenset(), (_muchos(DECLARACIONES), _uno({C.PRINCIPAL}))
    ),
    C.GLOBAL: EsquemaNodo(
        "declaracion_global",
        frozenset({"nombre", "tipo"}),
        (_opcional(EXPRESIONES),),
    ),
    C.FUNCION: EsquemaNodo(
        "declaracion_funcion",
        frozenset({"nombre"}),
        (_muchos({C.PARAMETRO}), _uno({C.BLOQUE})),
    ),
    C.PRINCIPAL: EsquemaNodo(
        "declaracion_chorreador", frozenset({"nombre"}), (_uno({C.BLOQUE}),)
    ),
    C.PARAMETRO: EsquemaNodo("parametro", frozenset({"nombre", "tipo"})),
    C.BLOQUE: EsquemaNodo("bloque", frozenset(), (_muchos(SENTENCIAS),)),
    C.LOCAL: EsquemaNodo(
        "declaracion_var_local",
        frozenset({"nombre", "tipo"}),
        (_opcional(EXPRESIONES),),
    ),
    C.ASIGNACION: EsquemaNodo(
        "sentencia_identificador", frozenset({"nombre"}), (_uno(EXPRESIONES),)
    ),
    C.LLAMADA: EsquemaNodo(
        "sufijo_llamada", frozenset({"nombre"}), (_muchos(EXPRESIONES),)
    ),
    C.OPERACION_LISTA: EsquemaNodo(
        "sufijo_lista", frozenset({"receptor", "metodo"}), (_uno(EXPRESIONES),)
    ),
    C.CONDICIONAL: EsquemaNodo(
        "estructura_condicional",
        frozenset(),
        (_uno(EXPRESIONES), _uno({C.BLOQUE}), _opcional({C.BLOQUE})),
    ),
    C.MIENTRAS: EsquemaNodo(
        "bucle_chorreando", frozenset(), (_uno(EXPRESIONES), _uno({C.BLOQUE}))
    ),
    C.PARA_CADA: EsquemaNodo(
        "bucle_recolar",
        frozenset({"tipo", "nombre", "lista"}),
        (_uno({C.BLOQUE}),),
    ),
    C.RETORNO: EsquemaNodo(
        "retorno_degustar", frozenset(), (_opcional(EXPRESIONES),)
    ),
    C.QUBIT: EsquemaNodo("declaracion_qubit", frozenset({"nombre"})),
    C.COMPUERTA: EsquemaNodo(
        "operacion_cuantica",
        frozenset({"compuerta"}),
        (_uno({C.IDENTIFICADOR}), _opcional({C.IDENTIFICADOR})),
    ),
    C.MEDICION: EsquemaNodo(
        "medicion_cuantica", frozenset(), (_uno({C.IDENTIFICADOR}),)
    ),
    C.BINARIA: EsquemaNodo(
        "expresion_*",
        frozenset({"operador"}),
        (_uno(EXPRESIONES), _uno(EXPRESIONES)),
    ),
    C.UNARIA: EsquemaNodo(
        "expresion_not / unario", frozenset({"operador"}), (_uno(EXPRESIONES),)
    ),
    C.IDENTIFICADOR: EsquemaNodo("identificador", frozenset({"nombre"})),
    C.LITERAL: EsquemaNodo("literal", frozenset({"categoria", "lexema"})),
    C.LISTA: EsquemaNodo("arreglo", frozenset(), (_muchos(EXPRESIONES),)),
}

_TIPO = re.compile(r"^(taza )*(grano|poso|granoMolido|cafe)$")
_OPERADORES_BINARIOS = frozenset(
    {
        "SinAzucar",
        "ConAzucar",
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "+",
        "-",
        "*",
        "/",
        "%",
    }
)
_OPERADORES_UNARIOS = frozenset({"Amargo", "+", "-"})
_CATEGORIAS_LITERAL = frozenset(
    t.name
    for t in (
        TokenType.ENTERO,
        TokenType.DECIMAL,
        TokenType.CADENA,
        TokenType.FUERTE,
        TokenType.RALO,
        TokenType.DESCAFEINADO,
        TokenType.SE_QUEMO_EL_CAFE,
    )
)
_METODOS_LISTA = frozenset({"insertar", "extraer", "buscar"})


def _coincide_patron(clases: List[C], patron: Tuple[Hueco, ...]) -> bool:
    """Empareja la secuencia de clases con el patron, sin retroceso."""
    posicion = 0
    for admitidas, minimo, maximo in patron:
        cuenta = 0
        while (
            posicion < len(clases)
            and clases[posicion] in admitidas
            and (maximo is None or cuenta < maximo)
        ):
            posicion += 1
            cuenta += 1
        if cuenta < minimo:
            return False
    return posicion == len(clases)


def _problemas_de_valores(nodo: NodoASA) -> Iterator[str]:
    a = nodo.atributos
    if "tipo" in a and not _TIPO.match(a["tipo"]):
        yield f"tipo invalido: {a['tipo']!r}"
    if nodo.clase == C.BINARIA and a["operador"] not in _OPERADORES_BINARIOS:
        yield f"operador binario invalido: {a['operador']!r}"
    if nodo.clase == C.UNARIA and a["operador"] not in _OPERADORES_UNARIOS:
        yield f"operador unario invalido: {a['operador']!r}"
    if nodo.clase == C.LITERAL and a["categoria"] not in _CATEGORIAS_LITERAL:
        yield f"categoria de literal invalida: {a['categoria']!r}"
    if nodo.clase == C.OPERACION_LISTA and a["metodo"] not in _METODOS_LISTA:
        yield f"metodo de lista invalido: {a['metodo']!r}"
    if nodo.clase == C.COMPUERTA:
        esperadas = {"H": 1, "X": 1, "Z": 1, "CNOT": 2}
        if a["compuerta"] not in esperadas:
            yield f"compuerta invalida: {a['compuerta']!r}"
        elif len(nodo.hijos) != esperadas[a["compuerta"]]:
            yield (
                f"{a['compuerta']} requiere {esperadas[a['compuerta']]} "
                f"qubit(s), tiene {len(nodo.hijos)}"
            )
    if nodo.clase == C.PRINCIPAL and a["nombre"] != "chorreador":
        yield "FuncionPrincipal debe llamarse 'chorreador'"


def problemas_nodo(nodo: NodoASA) -> List[str]:
    """Problemas de forma de un nodo (sin revisar a sus descendientes)."""
    esquema = ESQUEMA[nodo.clase]
    problemas: List[str] = []
    if set(nodo.atributos) != esquema.atributos:
        problemas.append(
            f"atributos {sorted(nodo.atributos)} en lugar de "
            f"{sorted(esquema.atributos)}"
        )
    if not _coincide_patron([h.clase for h in nodo.hijos], esquema.hijos):
        problemas.append(
            "hijos "
            + str([h.clase.value for h in nodo.hijos])
            + " no corresponden a "
            + esquema.produccion
        )
    if set(nodo.atributos) == esquema.atributos:
        problemas.extend(_problemas_de_valores(nodo))
    return problemas


def validar_arbol(raiz: NodoASA) -> List[str]:
    """Lista de problemas del arbol completo; vacia si respeta el esquema."""
    if raiz.clase != C.PROGRAMA:
        return [f"la raiz debe ser Programa, no {raiz.clase.value}"]
    problemas: List[str] = []
    pila = [(raiz, "Programa")]
    while pila:
        nodo, ruta = pila.pop()
        problemas.extend(f"{ruta}: {p}" for p in problemas_nodo(nodo))
        for i, hijo in enumerate(nodo.hijos):
            pila.append((hijo, f"{ruta}/{hijo.clase.value}[{i}]"))
    return problemas
