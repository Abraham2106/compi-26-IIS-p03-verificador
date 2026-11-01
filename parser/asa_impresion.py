from typing import Iterator, List, Optional, TextIO, Tuple

from parser.integracion import ClaseNodo, NodoASA

# Atributo que se usa como "Contenido" segun la clase del nodo.
CLAVE_CONTENIDO = {
    ClaseNodo.LITERAL: "lexema",
    ClaseNodo.BINARIA: "operador",
    ClaseNodo.UNARIA: "operador",
    ClaseNodo.COMPUERTA: "compuerta",
    ClaseNodo.OPERACION_LISTA: "metodo",
}
CLAVE_CONTENIDO_POR_DEFECTO = "nombre"


def recorrer_preorden(
        raiz: NodoASA, profundidad: int = 0) -> Iterator[Tuple[int, NodoASA]]:
    pila: List[Tuple[int, NodoASA]] = [(profundidad, raiz)]
    while pila:
        nivel, nodo = pila.pop()
        yield nivel, nodo
        for hijo in reversed(nodo.hijos):
            pila.append((nivel + 1, hijo))


def _escapar(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace('"', '\\"')


def contenido_y_atributos(nodo: NodoASA) -> Tuple[str, str]:
    clave = CLAVE_CONTENIDO.get(nodo.clase, CLAVE_CONTENIDO_POR_DEFECTO)
    contenido = nodo.atributos.get(clave, "")
    resto = [f"{k}={v}" for k, v in nodo.atributos.items() if k != clave]
    return contenido, ", ".join(resto)


def formatear_nodo(nodo: NodoASA, con_rango: bool = False) -> str:
    contenido, atributos = contenido_y_atributos(nodo)
    if con_rango:
        r = nodo.rango
        extra = f"rango={
            r.inicio.linea}:{
            r.inicio.columna}-{
            r.fin.linea}:{
                r.fin.columna}"
        atributos = f"{atributos}, {extra}" if atributos else extra
    return (f'<"{_escapar(nodo.clase.value)}", '
            f'"{_escapar(contenido)}", "{_escapar(atributos)}">')


def lineas_preorden(raiz: NodoASA, sangria: Optional[int] = 2,
                    con_rango: bool = False) -> List[str]:
    """
    Una linea por nodo. `sangria` = espacios por nivel; None o 0 = sin
    sangria.
    """
    paso = sangria or 0
    return [" " * (paso * nivel) + formatear_nodo(nodo, con_rango)
            for nivel, nodo in recorrer_preorden(raiz)]


def a_texto(
        raiz: NodoASA,
        sangria: Optional[int] = 2,
        con_rango: bool = False) -> str:
    return "\n".join(lineas_preorden(raiz, sangria, con_rango)) + "\n"


def imprimir_preorden(
        raiz: NodoASA,
        salida: Optional[TextIO] = None,
        sangria: Optional[int] = 2,
        con_rango: bool = False) -> None:
    import sys
    (salida or sys.stdout).write(a_texto(raiz, sangria, con_rango))
