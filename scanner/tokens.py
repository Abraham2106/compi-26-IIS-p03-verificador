"""Define los tipos de token y los lexemas fijos de Quantum Coffee.

Use estas definiciones compartidas. No cree catalogos paralelos.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    GRANO = auto()
    POSO = auto()
    GRANO_MOLIDO = auto()
    TAZA = auto()
    CAFE = auto()

    CAFETERIA = auto()
    BARISTA = auto()
    CHORREADOR = auto()
    DEGUSTAR = auto()
    HIERVE = auto()
    ENFRIA = auto()
    CHORREANDO = auto()
    RECOLAR = auto()
    EN = auto()

    SERVIR = auto()
    LEER = auto()
    INSERTAR = auto()
    EXTRAER = auto()
    BUSCAR = auto()

    SIN_AZUCAR = auto()
    CON_AZUCAR = auto()
    AMARGO = auto()

    FUERTE = auto()
    RALO = auto()
    DESCAFEINADO = auto()
    SE_QUEMO_EL_CAFE = auto()

    QUBIT = auto()
    COMPUERTA_H = auto()
    COMPUERTA_X = auto()
    COMPUERTA_Z = auto()
    CNOT = auto()
    MEDIR = auto()

    IDENTIFICADOR = auto()
    ENTERO = auto()
    DECIMAL = auto()
    CADENA = auto()

    ASIGNACION = auto()
    IGUALDAD = auto()
    DIFERENTE = auto()
    MENOR = auto()
    MENOR_IGUAL = auto()
    MAYOR = auto()
    MAYOR_IGUAL = auto()
    SUMA = auto()
    RESTA = auto()
    MULTIPLICACION = auto()
    DIVISION = auto()
    MODULO = auto()

    PARENTESIS_ABRE = auto()
    PARENTESIS_CIERRA = auto()
    LLAVE_ABRE = auto()
    LLAVE_CIERRA = auto()
    CORCHETE_ABRE = auto()
    CORCHETE_CIERRA = auto()
    COMA = auto()
    PUNTO_COMA = auto()
    PUNTO = auto()


# La EBNF es la base para las palabras reservadas
# La busqueda distingue entre mayusculas y minusculas
PALABRAS_RESERVADAS = {
    "grano": TokenType.GRANO,
    "poso": TokenType.POSO,
    "granoMolido": TokenType.GRANO_MOLIDO,
    "taza": TokenType.TAZA,
    "cafe": TokenType.CAFE,
    "cafeteria": TokenType.CAFETERIA,
    "barista": TokenType.BARISTA,
    "chorreador": TokenType.CHORREADOR,
    "degustar": TokenType.DEGUSTAR,
    "hierve": TokenType.HIERVE,
    "enfria": TokenType.ENFRIA,
    "chorreando": TokenType.CHORREANDO,
    "recolar": TokenType.RECOLAR,
    "en": TokenType.EN,
    # La EBNF dice que estas operaciones son  palabras reservadas
    # Quite estas entradas si la gramatica las define como llamadas
    # ordinarias a funciones
    "servir": TokenType.SERVIR,
    "leer": TokenType.LEER,
    "insertar": TokenType.INSERTAR,
    "extraer": TokenType.EXTRAER,
    "buscar": TokenType.BUSCAR,
    "SinAzucar": TokenType.SIN_AZUCAR,
    "ConAzucar": TokenType.CON_AZUCAR,
    "Amargo": TokenType.AMARGO,
    "fuerte": TokenType.FUERTE,
    "ralo": TokenType.RALO,
    "descafeinado": TokenType.DESCAFEINADO,
    "SeQuemoElCafe": TokenType.SE_QUEMO_EL_CAFE,
    "qubit": TokenType.QUBIT,
    "H": TokenType.COMPUERTA_H,
    "X": TokenType.COMPUERTA_X,
    "Z": TokenType.COMPUERTA_Z,
    "CNOT": TokenType.CNOT,
    "medir": TokenType.MEDIR,
}


# Comprueben los simbolos dobles antes de los simples
SIMBOLOS_DOBLES = {
    "==": TokenType.IGUALDAD,
    "!=": TokenType.DIFERENTE,
    "<=": TokenType.MENOR_IGUAL,
    ">=": TokenType.MAYOR_IGUAL,
}


SIMBOLOS_SIMPLES = {
    "=": TokenType.ASIGNACION,
    "<": TokenType.MENOR,
    ">": TokenType.MAYOR,
    "+": TokenType.SUMA,
    "-": TokenType.RESTA,
    "*": TokenType.MULTIPLICACION,
    "/": TokenType.DIVISION,
    "%": TokenType.MODULO,
    "(": TokenType.PARENTESIS_ABRE,
    ")": TokenType.PARENTESIS_CIERRA,
    "{": TokenType.LLAVE_ABRE,
    "}": TokenType.LLAVE_CIERRA,
    "[": TokenType.CORCHETE_ABRE,
    "]": TokenType.CORCHETE_CIERRA,
    ",": TokenType.COMA,
    ";": TokenType.PUNTO_COMA,
    ".": TokenType.PUNTO,
}


@dataclass(frozen=True)
class Token:
    """Conserva el lexema original y su posicion.
    linea y columna empiezan en 1.
    Ambas dicen la posicion del primer caracter del lexema.
    """

    tipo: TokenType
    lexema: str
    linea: int
    columna: int

    @property
    def atributos(self) -> str:
        return f"linea {self.linea}, columna {self.columna}"

    def __str__(self) -> str:
        return f'<"{self.tipo.name}", "{self.lexema}", "{self.atributos}">'
