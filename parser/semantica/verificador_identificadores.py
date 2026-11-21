
#Verificacion de identificadores mediante el patron Visitor.

from collections.abc import Callable

from parser.integracion import ClaseNodo, NodoASA
from parser.semantica.visitante import VisitanteASA
FUNCIONES_INCORPORADAS = frozenset({"servir", "leer"})
CLASES_VARIABLES = frozenset({
    ClaseNodo.GLOBAL, ClaseNodo.LOCAL, ClaseNodo.PARAMETRO,
    ClaseNodo.PARA_CADA, ClaseNodo.QUBIT,
})

class VerificadorIdentificadores(VisitanteASA):

    def __init__(
        self,
        resolver: Callable[[str], NodoASA | None],
        declarar: Callable[[str, NodoASA], None] | None = None,
        entrar_ambito: Callable[[], None] | None = None,
        salir_ambito: Callable[[], None] | None = None,
    ):
        self.resolver = resolver
        self.declarar = declarar
        self.entrar_ambito = entrar_ambito
        self.salir_ambito = salir_ambito
        self.errores: list[str] = []

        operaciones = (
            declarar,
            entrar_ambito,
            salir_ambito,
        )
        if any(op is not None for op in operaciones):
            if not all(op is not None for op in operaciones):
                raise ValueError(
                    "Debe proporcionar declarar, entrar_ambito "
                    "y salir_ambito juntos."
                )

    def verificar(self, arbol: NodoASA) -> list[str]:
        self.errores.clear()
        self.visitar(arbol)
        return list(self.errores)

    def _verificar_nombre(
        self,
        nodo: NodoASA,
        nombre: str,
        atributo: str = "nombre",
        exigir_variable: bool = False,
    ) -> None:
        definicion = self.resolver(nombre)

        if definicion is None:
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"identificador '{nombre}' no declarado"
            )
            return

        if exigir_variable and definicion.clase not in CLASES_VARIABLES:
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, columna {posicion.columna}: "
                f"'{nombre}' no es una variable"
            )
            return

        nodo.semantica.definiciones[atributo] = definicion


    def _registrar(self, nodo: NodoASA) -> None:
        if self.declarar is None:
            return

        nombre = nodo.atributos["nombre"]
        resultado = self.declarar(nombre, nodo)

        if resultado is False:
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"identificador '{nombre}' ya declarado "
                "en este ambito"
            )


    def visitar_bloque(self, nodo: NodoASA) -> None:
        if self.entrar_ambito is not None:
            self.entrar_ambito()

        try:
            self.visitar_hijos(nodo)
        finally:
            if self.salir_ambito is not None:
                self.salir_ambito()

    def visitar_local(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)
        self._registrar(nodo)


    def visitar_identificador(self, nodo: NodoASA) -> None:
        self._verificar_nombre(
            nodo,
            nodo.atributos["nombre"],
            exigir_variable=True,
        )

    def visitar_asignacion(self, nodo: NodoASA) -> None:
        self._verificar_nombre(
            nodo,
            nodo.atributos["nombre"],
            exigir_variable=True,
        )
        self.visitar_hijos(nodo)


    def visitar_llamada(self, nodo: NodoASA) -> None:
        """Verifica funciones declaradas o incorporadas."""
        nombre = nodo.atributos["nombre"]

        if nombre in FUNCIONES_INCORPORADAS:

            definicion = self.resolver(nombre)

            if definicion is not None:
                nodo.semantica.definiciones["nombre"] = definicion
        else:
            self._verificar_nombre(nodo, nombre)


        self.visitar_hijos(nodo)


    def visitar_operacion_lista(self, nodo: NodoASA) -> None:
        self._verificar_nombre(
            nodo,
            nodo.atributos["receptor"],
            "receptor",
            exigir_variable=True,
        )
        self.visitar_hijos(nodo)


    def visitar_para_cada(self, nodo: NodoASA) -> None:

        lista = nodo.atributos["lista"]
        self._verificar_nombre(nodo, lista, "lista", exigir_variable=True)

        if self.entrar_ambito is not None:
            self.entrar_ambito()

        try:
            self._registrar(nodo)
            self.visitar_hijos(nodo)
        finally:
            if self.salir_ambito is not None:
                self.salir_ambito()



    def visitar_programa(self, nodo: NodoASA) -> None:

        if self.declarar is not None:
            for hijo in nodo.hijos:
                if hijo.clase in (
                    ClaseNodo.GLOBAL,
                    ClaseNodo.FUNCION,
                ):
                    self._registrar(hijo)

        self.visitar_hijos(nodo)


    def visitar_funcion(self, nodo: NodoASA) -> None:

        if self.entrar_ambito is not None:
            self.entrar_ambito()

        try:
            self.visitar_hijos(nodo)
        finally:
            if self.salir_ambito is not None:
                self.salir_ambito()

    def visitar_parametro(self, nodo: NodoASA) -> None:
        self._registrar(nodo)

    def visitar_qubit(self, nodo: NodoASA) -> None:
        self._registrar(nodo)
