# Interfaz scanner - parser - ASA

Estado: contrato tecnico propuesto, implementado en `parser/integracion/` y probado.
Falta que las personas responsables del parser y del ASA lo acepten o acuerden
sus ajustes. No se afirma que ya hubo una reunion o un acuerdo del equipo.

## 1. Entrada real del explorador

Usar imports desde la raiz del proyecto, sin copiar el scanner ni crear otro enum:

```python
from scanner import Scanner, Token, TokenType, ErrorLexico
from parser.integracion import explorar_para_parser, FlujoTokens

entrada = explorar_para_parser(fuente)
if entrada.apta:
    tokens = entrada.tokens_para_parser()
    flujo = FlujoTokens(tokens)
else:
    for error in entrada.errores_lexicos:
        print(error)
```

`Scanner(fuente).escanear()` conserva la interfaz anterior:
`(list[Token], list[ErrorLexico])`, sin EOF. El adaptador usa ese mismo
explorador, conserva sus objetos y agrega solamente el fin de archivo.
No analiza la salida impresa de `main.py` ni vuelve a tokenizar texto.

| Campo de Token | Tipo | Significado |
| --- | --- | --- |
| `tipo` | `TokenType` compartido | Categoria para elegir producciones. Comparar miembros del enum, no sus numeros `.value`. |
| `lexema` | `str` | Texto original completo. Es el valor lexico disponible; no hay un campo `.valor` numerico. |
| `linea` | `int` | Linea inicial, desde 1. |
| `columna` | `int` | Columna inicial, desde 1, contada en caracteres de Python. |

Un tabulador cuenta como un caracter, no como cuatro u ocho espacios. LF,
CRLF y CR cuentan como un salto cada uno. El adaptador admite un BOM inicial,
que no ocupa columna; un BOM dentro del programa sigue siendo un error.

Ejemplo: `-12` entrega `RESTA("-")` y `ENTERO("12")`. Una cadena entrega
`CADENA` con sus comillas. `00012`, `01.50`, `fuerte`, `descafeinado` y
`SeQuemoElCafe` mantienen su escritura; no convertir con `int`, `float`,
`eval` ni decodificadores de escapes para construir el ASA de esta etapa.

`servir` y `leer` entregan `IDENTIFICADOR`. Los miembros antiguos `SERVIR`
y `LEER` permanecen por compatibilidad de imports, pero no se emiten.
`insertar`, `extraer` y `buscar` conservan tokens reservados, asi como las
construcciones cuanticas. El catalogo exacto se genera en
`ANALISIS_GRAMATICA.md` a partir de la EBNF y de los mapas reales del scanner.

## 2. Fin de archivo y errores lexicos

`explorar_para_parser(fuente)` retorna `EntradaParser`:

- `tokens`: tupla de tokens originales, seguida por exactamente un
  `Token(TokenType.FIN_ARCHIVO, "", linea_final, columna_final)`.
- `errores_lexicos`: tupla con los errores del scanner, sin esconderlos.
- `apta`: verdadero cuando no hay errores lexicos.
- `tokens_para_parser()`: entrega la tupla si esta limpia; lanza
  `EntradaConErroresLexicos` si el scanner detecto problemas.

El EOF se ubica despues de TODOS los caracteres, incluidos comentarios y
espacios finales; no se calcula a partir del ultimo token. En la fuente vacia
esta en `(1,1)`. No se modifica la salida del CLI antiguo para agregarlo.

Para esta integracion, una entrada con error lexico no debe llegar como entrada
limpia al parser: el scanner puede haber descartado caracteres o cadenas. El
equipo puede ampliar despues la politica de recuperacion, conservando siempre
el error lexico y evitando declarar exitoso ese programa.

## 3. Cursor para el analizador descendente

`FlujoTokens(tokens)` valida que exista un unico EOF final:

| Miembro | Contrato |
| --- | --- |
| `mirar()` | Token actual, sin avanzar. |
| `mirar(1)` | Siguiente token; permite resolver `barista`. |
| `avanzar()` | Devuelve el actual y avanza, salvo en EOF. |
| `en_fin` | Verdadero cuando el actual es FIN_ARCHIVO. |
| `indice` | Posicion del cursor en la secuencia. |

Mirar mas alla del final devuelve el mismo EOF. Avanzar en EOF no cambia el
indice. Mirar con adelanto negativo o construir un flujo sin EOF produce
`ValueError`: son errores de uso de la interfaz, no errores del lenguaje.

## 4. Firma que implementara el parser

El protocolo `AnalizadorSintactico` declara:

```python
def analizar(self, tokens: Sequence[Token]) -> ResultadoParseo:
    ...
```

El equipo proporciona la clase concreta. Uso cuando exista:

```python
entrada = explorar_para_parser(fuente)
if entrada.apta:
    resultado = parser.analizar(entrada.tokens_para_parser())
    if resultado.correcto:
        datos_para_renderer = resultado.arbol.a_dict()
    else:
        errores = resultado.errores
```

`ResultadoParseo` contiene `arbol: NodoASA | None` y una tupla de
`ErrorSintactico`. `correcto` requiere arbol y ausencia de errores. Un arbol
parcial con errores puede servir para depurar, pero no significa aceptacion.
El parser debe reconocer un programa completo y exigir FIN_ARCHIVO; no basta
con aceptar un prefijo e ignorar tokens sobrantes.

Cada `ErrorSintactico` contiene un mensaje, el token encontrado y una tupla de
`TokenType` esperados. La posicion procede del token encontrado, tambien en
EOF. No mezclar diagnosticos lexicos y sintacticos en una misma clase.

Para recuperarse, el parser puede sincronizar en `;`, `}` o EOF segun el
contexto. Debe consumir entrada o salir del nivel que fallo; no puede repetir
indefinidamente el mismo error. La `}` que cierra un bloque pertenece a ese
bloque y no debe descartarse a ciegas. Esta entrega define la entrada y salida;
no implementa ni impone un algoritmo concreto de recuperacion.

## 5. Decisiones de analisis

- En el nivel del programa, `CAFETERIA` inicia una global.
- `BARISTA` seguido por `IDENTIFICADOR` inicia una funcion del usuario.
- `BARISTA` seguido por `CHORREADOR` termina la lista de declaraciones y
  comienza la funcion principal. Otro token despues de BARISTA es un error.
- Tras un identificador de sentencia, `=` elige asignacion, `(` llamada y
  `.` metodo de lista. Un identificador aislado seguido de `;` no es sentencia.
- Tras un identificador dentro de factor, una llamada o un metodo son
  opcionales. Los demas tokens deben pertenecer al contexto que sigue.
- No existe retroceso necesario para esas decisiones. El unico conflicto
  LL(1) de FIRST/FOLLOW se resuelve con BARISTA y un token adicional; no se
  afirma que la gramatica completa sea estrictamente LL(1).

Las cadenas de operadores binarios se construyen con acumulacion izquierda:
`10 - 3 - 2` produce `Binaria(-, Binaria(-,10,3),2)`. En `2 + 3 * 4`, el hijo
derecho de la suma es la multiplicacion. Los prefijos se construyen de derecha
a izquierda; `-+x` produce `Unaria(-, Unaria(+,x))`. `Amargo` conserva su nivel
original: `Amargo a < b` agrupa como `Amargo (a < b)`, no como `(Amargo a) < b`.

## 6. Representacion compartida del ASA

`NodoASA` contiene `clase: ClaseNodo`, `rango: RangoFuente`,
`atributos: Mapping[str,str]` e `hijos: tuple[NodoASA,...]`.
Los atributos y los hijos se copian al construir el nodo y se conservan
inmutables. `a_dict()` produce JSON serializable, sin ejecutar expresiones.
Es un esquema estructural; no comprueba tipos o alcances.

Los rangos usan inicio inclusivo y fin exclusivo. Para un token, el fin es
`columna + len(lexema)`; un EOF tiene longitud cero. Para una construccion,
abarca desde el primer token hasta el final del ultimo, incluyendo sus
delimitadores y `;` cuando correspondan. No incluir espacios o comentarios
posteriores. La raiz abarca desde el primer token del programa hasta el final
de la llave de chorreador. Las posiciones se refieren a la fuente sin BOM.

| Clase | Atributos de texto | Hijos en orden |
| --- | --- | --- |
| Programa | ninguno | Globales/funciones en orden fuente; al final FuncionPrincipal. |
| DeclaracionGlobal / DeclaracionLocal | `nombre`, `tipo` | Cero o una expresion inicial. |
| Funcion | `nombre` | Parametros en orden y, al final, Bloque. |
| FuncionPrincipal | `nombre=chorreador` | Un Bloque. |
| Parametro | `nombre`, `tipo` | Ninguno. |
| Bloque | ninguno | Sentencias en orden. |
| Asignacion | `nombre` | Una expresion. |
| Llamada | `nombre` | Argumentos en orden, incluso cero. Sirve como expresion o sentencia. |
| OperacionLista | `receptor`, `metodo` | Una expresion argumento. Sirve como expresion o sentencia. |
| Condicional | ninguno | Condicion, Bloque verdadero y Bloque falso opcional. |
| Mientras | ninguno | Condicion, Bloque. |
| ParaCada | `tipo`, `nombre`, `lista` | Un Bloque. |
| Retorno | ninguno | Cero o una expresion. |
| DeclaracionQubit | `nombre` | Ninguno. |
| Compuerta | `compuerta` | Uno o dos Identificador segun la sintaxis de la compuerta. |
| Medicion | ninguno | Un Identificador. |
| Binaria | `operador` | Izquierdo, derecho. |
| Unaria | `operador` | Operando. |
| Identificador | `nombre` | Ninguno. |
| Literal | `categoria` (nombre de TokenType), `lexema` | Ninguno. |
| Lista | ninguno | Expresiones en orden, incluso cero. |

`tipo` conserva la forma canonica textual: `grano`, `taza grano`,
`taza taza grano`, etc.; es el tipo escrito, no un tipo inferido. Los nombres
de clase se toman de `ClaseNodo`, no se inventa otro catalogo en el renderer.
Los operadores conservan su lexema, como `ConAzucar`, `+` o `>=`.

Las producciones auxiliares (`factor`, `termino`, etc.) no crean nodos extra.
Los parentesis agrupan pero no crean un nodo Parentesis; puede ampliarse el
rango del nodo agrupado para incluirlos. Signos y conectores SI generan
Unaria/Binaria. Las llaves, comas, punto y coma y EOF no son hojas del ASA.
Un Bloque vacio y una Lista vacia si son nodos, con hijos vacios.

`asa_referencia.json` es un ejemplo esperado construido para documentar el
contrato de `barista chorreador() { grano x = 2 + 3 * 4; }`. No es salida
de un parser ya implementado. El renderer puede usarlo para comenzar su trabajo.

## 7. Acuerdo del equipo pendiente

Antes de integrar los componentes, confirmar con sus responsables:

1. Uso del TokenType y de las clases de este paquete, con EOF solo en el adaptador.
2. Firma `analizar(tokens)` y formato de errores/ResultadoParseo.
3. Nombres, atributos, orden de hijos y rangos de NodoASA.
4. Politica ante errores lexicos y forma de mostrar arboles parciales.

No se necesitan cambios de sintaxis para aceptar este contrato. Si el equipo
prefiere otro esquema, actualizar contrato y pruebas juntos antes de duplicar
clases incompatibles. Esta lista documenta una coordinacion pendiente; no
equivale a un acuerdo ya confirmado con las otras personas.
