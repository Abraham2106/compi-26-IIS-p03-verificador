"""Tabla de simbolos con ambitos anidados (1.2).

Cada simbolo guarda su nombre, categoria, tipo, el nodo del ASA que lo
declara y el ambito donde vive. Los ambitos forman una pila: el nivel 0 es
el global y cada `entrar` abre un nivel interior.

Interfaz que usa el Visitor (mismo contrato que la tabla provisional):

    declarar(nombre, nodo) -> bool      False si choca en el ambito actual.
    resolver(nombre) -> NodoASA | None  Declaracion visible mas cercana.
    entrar() / salir()                  Abre y cierra un ambito.

Interfaz completa, para el checker y la impresion:

    registrar(nombre, nodo) -> Simbolo | None
    buscar(nombre) -> Simbolo | None    Desde el ambito actual hacia afuera.
    buscar_local(nombre) -> Simbolo | None
    conflictos                          Declaraciones rechazadas.
    cambios                             Historial de entrar, registrar,
                                        conflicto y salir (1.4.1).
    simbolos()                          Todos los registrados, en orden.
    a_texto()                           Tabla legible por ambito.

Reglas de ambito:

- Un nombre no se repite dentro de un mismo ambito, sin importar la
  categoria (variable, qubit, funcion o parametro).
- Un ambito interior puede ocultar (sombrear) un nombre exterior.
- Los parametros de una funcion y la variable de `recolar` viven en un
  ambito de cabecera; el bloque que les sigue comparte su espacio de nombres,
  asi que redeclararlos en ese bloque es un conflicto. En bloques mas
  internos si se pueden sombrear.
- Las funciones incorporadas (servir, leer) se buscan al final, despues del
  ambito global, por lo que el programa puede ocultarlas.
"""

from dataclasses import dataclass, field
from enum import Enum

from parser.integracion import ClaseNodo, NodoASA, Posicion


class Categoria(str, Enum):
    VARIABLE_GLOBAL = "variable global"
    VARIABLE_LOCAL = "variable local"
    PARAMETRO = "parametro"
    VARIABLE_CICLO = "variable de recolar"
    QUBIT = "qubit"
    FUNCION = "funcion"
    INCORPORADA = "funcion incorporada"


CATEGORIA_POR_CLASE = {
    ClaseNodo.GLOBAL: Categoria.VARIABLE_GLOBAL,
    ClaseNodo.LOCAL: Categoria.VARIABLE_LOCAL,
    ClaseNodo.PARAMETRO: Categoria.PARAMETRO,
    ClaseNodo.PARA_CADA: Categoria.VARIABLE_CICLO,
    ClaseNodo.QUBIT: Categoria.QUBIT,
    ClaseNodo.FUNCION: Categoria.FUNCION,
}

# Categorias que se pueden leer o asignar como variables.
CATEGORIAS_VARIABLE = frozenset({
    Categoria.VARIABLE_GLOBAL, Categoria.VARIABLE_LOCAL,
    Categoria.PARAMETRO, Categoria.VARIABLE_CICLO, Categoria.QUBIT,
})
CATEGORIAS_FUNCION = frozenset({Categoria.FUNCION, Categoria.INCORPORADA})
# Simbolos que hacen de un ambito una cabecera (ver reglas arriba).
CATEGORIAS_CABECERA = frozenset({
    Categoria.PARAMETRO, Categoria.VARIABLE_CICLO,
})

# nombre -> (tipos de los parametros, tipo de retorno)
FIRMAS_INCORPORADAS = {
    "servir": (("valor",), "sin_valor"),
    "leer": ((), "granoMolido"),
}
FUNCIONES_INCORPORADAS = frozenset(FIRMAS_INCORPORADAS)


def categoria_de(nodo: NodoASA) -> Categoria:
    """Categoria que corresponde a un nodo de declaracion."""
    try:
        return CATEGORIA_POR_CLASE[nodo.clase]
    except KeyError:
        raise ValueError(
            f"{nodo.clase.value} no es un nodo de declaracion.") from None


def tipo_declarado(nodo: NodoASA) -> str | None:
    """Tipo escrito en la declaracion; None si el lenguaje no lo escribe."""
    if nodo.clase == ClaseNodo.QUBIT:
        return "qubit"
    if nodo.clase == ClaseNodo.FUNCION:
        return None    # El retorno no se escribe: lo calcula la inferencia.
    return nodo.atributos.get("tipo")


@dataclass(eq=False)
class Simbolo:
    nombre: str
    categoria: Categoria
    definicion: NodoASA | None    # None solo para funciones incorporadas.
    ambito: "Ambito | None"
    tipo_declarado: str | None = None
    parametros: tuple[str, ...] = ()    # Tipos de parametros (funciones).

    @classmethod
    def desde_nodo(cls, nombre: str, nodo: NodoASA,
                   ambito: "Ambito") -> "Simbolo":
        parametros = ()
        if nodo.clase == ClaseNodo.FUNCION:
            parametros = tuple(
                h.atributos["tipo"] for h in nodo.hijos
                if h.clase == ClaseNodo.PARAMETRO)
        return cls(nombre, categoria_de(nodo), nodo, ambito,
                   tipo_declarado(nodo), parametros)

    @property
    def tipo(self) -> str | None:
        """Tipo declarado o, si no hay, el que dejo la inferencia."""
        if self.tipo_declarado is not None:
            return self.tipo_declarado
        if self.definicion is not None:
            return self.definicion.semantica.tipo_inferido
        return None

    @property
    def posicion(self) -> Posicion | None:
        return (self.definicion.rango.inicio
                if self.definicion is not None else None)

    @property
    def es_variable(self) -> bool:
        return self.categoria in CATEGORIAS_VARIABLE

    @property
    def es_funcion(self) -> bool:
        return self.categoria in CATEGORIAS_FUNCION

    def describir_tipo(self) -> str:
        retorno = self.tipo or "?"
        if self.es_funcion:
            return f"({', '.join(self.parametros)}) -> {retorno}"
        return retorno


@dataclass(eq=False)
class Ambito:
    numero: int
    nivel: int
    padre: "Ambito | None"
    simbolos: dict[str, Simbolo] = field(default_factory=dict)

    @property
    def es_cabecera(self) -> bool:
        return any(s.categoria in CATEGORIAS_CABECERA
                   for s in self.simbolos.values())

    def describir(self) -> str:
        if self.padre is None:
            return "Ambito 0 (global)"
        return (f"Ambito {self.numero} (nivel {self.nivel}, "
                f"dentro de {self.padre.numero})")


@dataclass(frozen=True, eq=False)
class Conflicto:
    nuevo: Simbolo       # Declaracion rechazada.
    existente: Simbolo   # Declaracion previa con la que choca.


class TipoCambio(str, Enum):
    ENTRAR = "entrar"
    REGISTRAR = "registrar"
    CONFLICTO = "conflicto"
    SALIR = "salir"


@dataclass(frozen=True, eq=False)
class Cambio:
    """Una modificacion de la tabla, en el orden en que ocurrio (1.4.1)."""

    tipo: TipoCambio
    ambito: Ambito
    simbolo: Simbolo | None = None      # REGISTRAR y CONFLICTO.
    existente: Simbolo | None = None    # CONFLICTO: declaracion previa.
    contenido: tuple[Simbolo, ...] = ()  # SALIR: simbolos del ambito.


class TablaSimbolos:
    def __init__(self):
        self.global_ = Ambito(0, 0, None)
        self.actual = self.global_
        self.ambitos: list[Ambito] = [self.global_]   # Todos, en orden.
        self.conflictos: list[Conflicto] = []
        self.cambios: list[Cambio] = []
        self.incorporadas = {
            nombre: Simbolo(nombre, Categoria.INCORPORADA, None, None,
                            retorno, parametros)
            for nombre, (parametros, retorno) in FIRMAS_INCORPORADAS.items()
        }

    # Ambitos

    @property
    def nivel(self) -> int:
        return self.actual.nivel

    def entrar(self) -> Ambito:
        self.actual = Ambito(len(self.ambitos), self.nivel + 1, self.actual)
        self.ambitos.append(self.actual)
        self.cambios.append(Cambio(TipoCambio.ENTRAR, self.actual))
        return self.actual

    def salir(self) -> None:
        if self.actual.padre is None:
            raise RuntimeError("No se puede salir del ambito global.")
        self.cambios.append(Cambio(
            TipoCambio.SALIR, self.actual,
            contenido=tuple(self.actual.simbolos.values())))
        self.actual = self.actual.padre

    # Registro

    def buscar_local(self, nombre: str) -> Simbolo | None:
        """Declaracion de `nombre` en el espacio de nombres actual."""
        simbolo = self.actual.simbolos.get(nombre)
        if simbolo is None:
            padre = self.actual.padre
            if padre is not None and padre.es_cabecera:
                simbolo = padre.simbolos.get(nombre)
        return simbolo

    def registrar(self, nombre: str, nodo: NodoASA) -> Simbolo | None:
        """Registra la declaracion; None si choca con otra del ambito."""
        nuevo = Simbolo.desde_nodo(nombre, nodo, self.actual)
        existente = self.buscar_local(nombre)
        if existente is not None:
            self.conflictos.append(Conflicto(nuevo, existente))
            self.cambios.append(Cambio(
                TipoCambio.CONFLICTO, self.actual, nuevo, existente))
            return None
        self.actual.simbolos[nombre] = nuevo
        self.cambios.append(Cambio(TipoCambio.REGISTRAR, self.actual, nuevo))
        return nuevo

    def declarar(self, nombre: str, nodo: NodoASA) -> bool:
        return self.registrar(nombre, nodo) is not None

    # Consulta

    def buscar(self, nombre: str) -> Simbolo | None:
        """Busca desde el ambito actual hacia el global y las incorporadas."""
        ambito = self.actual
        while ambito is not None:
            if nombre in ambito.simbolos:
                return ambito.simbolos[nombre]
            ambito = ambito.padre
        return self.incorporadas.get(nombre)

    def resolver(self, nombre: str) -> NodoASA | None:
        simbolo = self.buscar(nombre)
        return simbolo.definicion if simbolo is not None else None

    def simbolos(self) -> list[Simbolo]:
        """Todos los simbolos registrados, por ambito y en orden."""
        return [s for a in self.ambitos for s in a.simbolos.values()]

    def simbolo_de(self, nodo: NodoASA) -> Simbolo | None:
        """Simbolo cuya definicion es `nodo` (identidad, no igualdad)."""
        for simbolo in self.simbolos():
            if simbolo.definicion is nodo:
                return simbolo
        return None

    # Impresion

    def filas(self) -> list[tuple[str, str, str, str, str]]:
        """(ambito, nombre, categoria, tipo, linea:columna) por simbolo."""
        filas = []
        for simbolo in self.simbolos():
            p = simbolo.posicion
            filas.append((
                str(simbolo.ambito.numero), simbolo.nombre,
                simbolo.categoria.value, simbolo.describir_tipo(),
                f"{p.linea}:{p.columna}" if p else "-",
            ))
        return filas

    def a_texto(self) -> str:
        encabezado = ("Ambito", "Nombre", "Categoria", "Tipo", "Definicion")
        filas = self.filas()
        anchos = [max(len(f[i]) for f in [encabezado, *filas])
                  for i in range(len(encabezado))]

        def linea(fila):
            return "  ".join(c.ljust(a) for c, a in zip(fila, anchos)).rstrip()

        texto = [linea(encabezado), linea(tuple("-" * a for a in anchos))]
        texto += [linea(f) for f in filas]
        texto.append("")
        texto += [a.describir() for a in self.ambitos]
        return "\n".join(texto) + "\n"
