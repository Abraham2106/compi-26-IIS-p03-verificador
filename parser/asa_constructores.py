from typing import Iterable, Optional, Sequence, Union

from parser.integracion import ClaseNodo, NodoASA, Posicion, RangoFuente
from scanner import Token

Ubicable = Union[Token, NodoASA, RangoFuente]


def a_rango(elemento: Ubicable) -> RangoFuente:
    """Rango de un token, de un nodo o de un rango ya construido."""
    if isinstance(elemento, Token):
        return RangoFuente.de_token(elemento)
    if isinstance(elemento, NodoASA):
        return elemento.rango
    if isinstance(elemento, RangoFuente):
        return elemento
    raise TypeError("Se esperaba Token, NodoASA o RangoFuente.")


def rango_entre(primero: Ubicable, ultimo: Ubicable) -> RangoFuente:
    """Rango desde el inicio de `primero` hasta el fin de `ultimo`."""
    return RangoFuente(a_rango(primero).inicio, a_rango(ultimo).fin)


# hojas

def crear_identificador(token: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.IDENTIFICADOR, a_rango(token), {
            "nombre": token.lexema})


def crear_literal(token: Token) -> NodoASA:
    """Conserva el lexema original (con comillas en las cadenas)."""
    return NodoASA(
        ClaseNodo.LITERAL,
        a_rango(token),
        {"categoria": token.tipo.name, "lexema": token.lexema},
    )


# expresiones

def crear_binaria(
        izquierdo: NodoASA,
        operador: Token,
        derecho: NodoASA) -> NodoASA:
    return NodoASA(
        ClaseNodo.BINARIA,
        rango_entre(izquierdo, derecho),
        {"operador": operador.lexema},
        (izquierdo, derecho),
    )


def crear_unaria(operador: Token, operando: NodoASA) -> NodoASA:
    return NodoASA(
        ClaseNodo.UNARIA,
        rango_entre(operador, operando),
        {"operador": operador.lexema},
        (operando,),
    )


def crear_lista(
        abre: Token,
        elementos: Sequence[NodoASA],
        cierra: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.LISTA,
        rango_entre(
            abre,
            cierra),
        {},
        tuple(elementos))


def crear_llamada(
        nombre: Token,
        argumentos: Sequence[NodoASA],
        cierra: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.LLAMADA,
        rango_entre(nombre, cierra),
        {"nombre": nombre.lexema},
        tuple(argumentos),
    )


def crear_operacion_lista(receptor: Token, metodo: Token, argumento: NodoASA,
                          cierra: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.OPERACION_LISTA,
        rango_entre(receptor, cierra),
        {"receptor": receptor.lexema, "metodo": metodo.lexema},
        (argumento,),
    )


def agrupar(nodo: NodoASA, abre: Token, cierra: Token) -> NodoASA:
    """Los parentesis no crean nodo: solo amplian el rango del agrupado."""
    return NodoASA(
        nodo.clase,
        rango_entre(
            abre,
            cierra),
        nodo.atributos,
        nodo.hijos)


# sentencias

def crear_declaracion(clase: ClaseNodo, tipo: str, nombre: Token,
                      inicial: Optional[NodoASA], inicio: Token,
                      punto_coma: Token) -> NodoASA:
    """DeclaracionGlobal o DeclaracionLocal; `tipo` es el texto escrito."""
    if clase not in (ClaseNodo.GLOBAL, ClaseNodo.LOCAL):
        raise ValueError("clase debe ser GLOBAL o LOCAL.")
    return NodoASA(
        clase,
        rango_entre(inicio, punto_coma),
        {"nombre": nombre.lexema, "tipo": tipo},
        (inicial,) if inicial is not None else (),
    )


def crear_asignacion(
        nombre: Token,
        valor: NodoASA,
        punto_coma: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.ASIGNACION,
        rango_entre(nombre, punto_coma),
        {"nombre": nombre.lexema},
        (valor,),
    )


def crear_retorno(
        degustar: Token,
        valor: Optional[NodoASA],
        punto_coma: Token) -> NodoASA:
    return NodoASA(
        ClaseNodo.RETORNO,
        rango_entre(degustar, punto_coma),
        {},
        (valor,) if valor is not None else (),
    )


def como_sentencia(expresion: NodoASA, punto_coma: Token) -> NodoASA:
    """Llamada u OperacionLista usada como sentencia: el rango incluye `;`."""
    return NodoASA(expresion.clase, rango_entre(expresion, punto_coma),
                   expresion.atributos, expresion.hijos)


def crear_programa(
        declaraciones: Iterable[NodoASA],
        principal: NodoASA) -> NodoASA:
    """Globales y funciones en orden fuente; FuncionPrincipal al final."""
    hijos = tuple(declaraciones) + (principal,)
    return NodoASA(
        ClaseNodo.PROGRAMA,
        rango_entre(
            hijos[0],
            principal),
        {},
        hijos)


# insercion

def con_hijo(
        padre: NodoASA,
        hijo: NodoASA,
        posicion: Optional[int] = None) -> NodoASA:
    """Devuelve un nodo nuevo con `hijo` insertado (al final por omision).

    NodoASA es inmutable, asi que insertar crea una copia y ajusta el rango
    para que cubra al hijo cuando este queda fuera del rango del padre.
    """
    hijos = list(padre.hijos)
    hijos.insert(len(hijos) if posicion is None else posicion, hijo)
    inicio = min(padre.rango.inicio, hijo.rango.inicio)
    fin = max(padre.rango.fin, hijo.rango.fin)
    return NodoASA(
        padre.clase,
        RangoFuente(
            inicio,
            fin),
        padre.atributos,
        tuple(hijos))


def desde_dict(datos: dict) -> NodoASA:
    def posicion(d: dict) -> Posicion:
        return Posicion(d["linea"], d["columna"])

    return NodoASA(
        ClaseNodo(datos["clase"]),
        RangoFuente(posicion(datos["rango"]["inicio"]),
                    posicion(datos["rango"]["fin"])),
        dict(datos["atributos"]),
        tuple(desde_dict(h) for h in datos["hijos"]),
    )
