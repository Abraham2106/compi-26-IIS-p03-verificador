# Gramatica oficial de Quantum Coffee

Esta version integra la gramatica del Proyecto 1 con el scanner del Proyecto 2.
Es la referencia vigente; reemplaza las producciones anteriores.

## Convenciones

- `::=` define una produccion; `|` indica alternativas.
- `{ ... }` indica cero o mas repeticiones; `[ ... ]` indica una parte opcional.
- Los terminales aparecen entre comillas. Las llaves y los corchetes entre
  comillas son caracteres del programa, no operadores de EBNF.
- Espacios y comentarios se ignoran entre tokens, no dentro de ellos.
- Las palabras reservadas no pueden ser identificadores. Se distinguen
  mayusculas y minusculas; se usa `cafeteria` y `enfria`, sin tildes.
- `servir` y `leer` son nombres del ambiente estandar, no palabras reservadas.
  Se reconocen mediante las mismas llamadas que las funciones del usuario.
- Las reglas sintacticas operan sobre tokens completos: un numero decimal no
  se interpreta como un entero seguido por un punto y otro entero.

## 1. Tipos

```ebnf
tipo ::= "grano" | "poso" | "granoMolido" | "cafe" | "taza" tipo
```

`grano` es entero, `poso` es flotante, `granoMolido` es texto y `cafe` es
booleano. `taza tipo` es una lista homogenea; `taza taza grano` es una lista
de listas. `fuerte`, `ralo`, `descafeinado` y `SeQuemoElCafe` son valores,
no nombres de tipos.

## 2. Programa y funciones

```ebnf
programa ::= { declaracion_global | declaracion_funcion } declaracion_chorreador
declaracion_global ::= "cafeteria" tipo identificador [ "=" expresion ] ";"
declaracion_funcion ::= "barista" identificador "(" [ parametros ] ")" bloque
declaracion_chorreador ::= "barista" "chorreador" "(" ")" bloque
parametros ::= parametro { "," parametro }
parametro ::= tipo identificador
argumentos ::= expresion { "," expresion }
```

Hay exactamente un `chorreador`, sin parametros y al final del programa.
Las funciones del usuario pueden ser recursivas. `chorreador` no es un
identificador y no puede llamarse como una funcion ordinaria.

## 3. Bloques y sentencias

```ebnf
bloque ::= "{" { sentencia } "}"
sentencia ::= declaracion_var_local
            | declaracion_qubit
            | sentencia_identificador
            | estructura_condicional
            | bucle_chorreando
            | bucle_recolar
            | operacion_cuantica ";"
            | medicion_cuantica ";"
            | retorno_degustar
declaracion_var_local ::= tipo identificador [ "=" expresion ] ";"
sentencia_identificador ::= identificador continuacion_sentencia ";"
continuacion_sentencia ::= "=" expresion | sufijo_llamada | sufijo_lista
sufijo_llamada ::= "(" [ argumentos ] ")"
sufijo_lista ::= "." metodo_lista "(" expresion ")"
metodo_lista ::= "insertar" | "extraer" | "buscar"
retorno_degustar ::= "degustar" [ expresion ] ";"
```

Una sentencia con identificador admite asignacion, llamada o metodo de lista.
Las llamadas usadas como sentencias pueden descartar el resultado.
`degustar;` termina una funcion sin devolver un valor util; `degustar expresion;`
devuelve el valor de la expresion. La asignacion no forma parte de una expresion.

## 4. Bifurcacion y ciclos

```ebnf
estructura_condicional ::= "hierve" "(" expresion ")" bloque [ "enfria" bloque ]
bucle_chorreando ::= "chorreando" "(" expresion ")" bloque
bucle_recolar ::= "recolar" "(" tipo identificador "en" identificador ")" bloque
```

`chorreando` evalua la condicion antes de cada vuelta, por lo que puede ejecutar
el bloque cero veces. `recolar` recorre los elementos de una lista en orden;
en una lista vacia no ejecuta el bloque. Se pueden anidar ciclos y condiciones.
Las llaves son obligatorias, incluso para un bloque vacio o de una sentencia.

## 5. Expresiones

```ebnf
expresion ::= expresion_or
expresion_or ::= expresion_and { op_or expresion_and }
expresion_and ::= expresion_not { op_and expresion_not }
expresion_not ::= { op_not } expresion_relacional
expresion_relacional ::= expresion_aritmetica [ op_relacional expresion_aritmetica ]
expresion_aritmetica ::= termino { ( "+" | "-" ) termino }
termino ::= unario { ( "*" | "/" | "%" ) unario }
unario ::= { "+" | "-" } factor
factor ::= literal
         | identificador [ sufijo_llamada | sufijo_lista ]
         | medicion_cuantica
         | "(" expresion ")"
op_or ::= "SinAzucar"
op_and ::= "ConAzucar"
op_not ::= "Amargo"
op_relacional ::= "==" | "!=" | "<" | "<=" | ">" | ">="
```

Precedencia de mayor a menor: agrupacion/llamadas, signos unarios, `* / %`,
`+ -`, comparaciones, `Amargo`, `ConAzucar`, `SinAzucar`.
Los operadores binarios repetidos en un mismo nivel se evaluan de izquierda a
derecha: `10 - 3 - 2` equivale a `(10 - 3) - 2`. Los operadores unarios se
aplican desde el mas cercano al operando hacia afuera. El ASA conserva los conectores logicos sin evaluarlos. No se admiten comparaciones encadenadas como `a < b < c`;
se escribe `a < b ConAzucar b < c`.

## 6. Literales y reglas lexicas

```ebnf
literal ::= numero_entero | numero_decimal | cadena
          | "fuerte" | "ralo" | "descafeinado" | "SeQuemoElCafe" | arreglo
arreglo ::= "[" [ expresion { "," expresion } ] "]"
identificador ::= letra { letra | digito | "_" }
numero_entero ::= digito { digito }
numero_decimal ::= digito { digito } "." digito { digito }
cadena ::= '"' { caracter_cadena } '"'
letra ::= "A".."Z" | "a".."z"
digito ::= "0".."9"
caracter_cadena ::= ? cualquier caracter excepto comillas dobles, CR y LF ?
comentario ::= "#" { ? cualquier caracter excepto CR y LF ? }
```

Los signos son operadores, no parte del token numerico. Se admiten `-5`, `+2`
y `-(a + b)`. Los decimales conservan digitos a ambos lados del punto.
Las cadenas conservan el comportamiento actual del scanner: sin escapes ni
saltos de linea. `#` dentro de una cadena es texto, no un comentario.

## 7. Extension cuantica

```ebnf
declaracion_qubit ::= "qubit" identificador ";"
operacion_cuantica ::= compuerta_unaria | compuerta_binaria
compuerta_unaria ::= ( "H" | "X" | "Z" ) "(" identificador ")"
compuerta_binaria ::= "CNOT" "(" identificador "," identificador ")"
medicion_cuantica ::= "medir" "(" identificador ")"
```

Se conserva la extension original. Qubits, compuertas y mediciones siguen
siendo construcciones propias del lenguaje y conservan sus tokens.

## 8. Alcance del parser y del ASA

Esta entrega corresponde solamente al analisis sintactico y al contrato de
representacion del ASA. El parser reconoce formas, precedencia y estructura;
no ejecuta ciclos o funciones ni comprueba tipos, alcances, nombres declarados,
aridad de funciones ordinarias o compatibilidad de retornos. Los literales
conservan el lexema original, incluidas las comillas de las cadenas.

Por ejemplo, `hierve (5) {}` y `grano x = "texto";` son sintacticamente
reconocibles. Que sean semanticamente admisibles queda fuera de esta etapa.
`servir()` y `leer(1)` tambien se reconocen como llamadas ordinarias: sus
contratos de biblioteca no se codifican como producciones especiales.

La interfaz de entrada y el esquema de nodos se describen en
[INTERFAZ_PARSER_ASA.md](INTERFAZ_PARSER_ASA.md). Las decisiones semanticas de
la revision anterior quedan archivadas como antecedentes en
`DISENO_SEMANTICO_PREVIO.md`, fuera de los criterios de esta tarea.

## 9. Repeticiones y analisis descendente

No hay recursion directa ni indirecta por la izquierda. Las repeticiones
EBNF generan secuencias de sentencias, argumentos, parametros y operadores.
Cada vuelta de esas repeticiones debe consumir tokens.

Las alternativas que comienzan con identificador estan factorizadas tanto en
sentencias como en factores. En el nivel del programa se conservan las
declaraciones originales: despues de `barista`, el analizador mira el siguiente
token (`chorreador` o identificador). La decision se toma con `BARISTA` y el token siguiente. El informe de
FIRST/FOLLOW identifica el conflicto LL(1) y documenta esta resolucion
determinista sin retroceso; no hace falta cambiar la sintaxis existente.
