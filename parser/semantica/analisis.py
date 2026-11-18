"""Analisis semantico completo: identificadores + tipos + reporte.

La tabla de simbolos real es el punto 1.2. Mientras no este
integrada, TablaAmbitos cumple el mismo contrato de cuatro operaciones
(resolver, declarar, entrar, salir); para cambiarla, basta pasar otra tabla
a verificar_semantica o cambiar FABRICA_TABLA.
"""

from parser.integracion import NodoASA
from parser.semantica.errores_semanticos import ErrorSemantico, recolectar
from parser.semantica.inferencia_tipos import InferidorTipos
from parser.semantica.verificador_identificadores import (
    VerificadorIdentificadores,
)


class TablaAmbitos:
    """Pila de ambitos. El nivel 0 es el global."""

    def __init__(self):
        self.ambitos: list[dict[str, NodoASA]] = [{}]

    @property
    def nivel(self) -> int:
        return len(self.ambitos) - 1

    def entrar(self) -> None:
        self.ambitos.append({})

    def salir(self) -> None:
        self.ambitos.pop()

    def declarar(self, nombre: str, nodo: NodoASA) -> bool:
        if nombre in self.ambitos[-1]:
            return False
        self.ambitos[-1][nombre] = nodo
        return True

    def resolver(self, nombre: str) -> NodoASA | None:
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None


FABRICA_TABLA = TablaAmbitos    # Cambiar por la tabla de 1.2 al integrarla.


def verificar_semantica(arbol: NodoASA, tabla=None) -> list[ErrorSemantico]:
    """Corre identificadores y tipos; retorna los errores ordenados."""
    tabla = tabla if tabla is not None else FABRICA_TABLA()
    identificadores = VerificadorIdentificadores(
        tabla.resolver, tabla.declarar, tabla.entrar, tabla.salir
    ).verificar(arbol)
    # Un nombre sin declarar deja su tipo en None y la inferencia no lo
    # usa, asi que correr ambas fases no genera errores en cascada.
    tipos = InferidorTipos().inferir(arbol)
    return recolectar(("identificadores", identificadores), ("tipos", tipos))
