# Quantum Coffee

Documento único para la documentación del scanner y del parser. La implementación del scanner está en `scanner/`; la integración y verificación del parser están en `parser/`. La especificación EBNF incluida aquí también es la entrada que consume el verificador.

El repositorio incluye el parser integrado y su ASA; no incluye análisis semántico ni generación de código. Los ejemplos completos permanecen como archivos `.qc` en `parser/ejemplos_completos/`.

Los cinco ejercicios originales y la corrección de la llave extra del ejercicio de textos se describen en la sección Programas de referencia; sus versiones ejecutables están en `parser/ejemplos_completos/`.

Para consultar el ejemplo JSON del ASA y el registro de una ejecución anterior, ver `docs/asa_referencia.json` y `docs/RESULTADOS_VERIFICACION.txt`.

## Estado y alcance de la revisión inicial

Esta sección registra la revisión previa a la integración. Para el estado actual,
ver la sección final de integración de las tareas 4.4 y 5.3.

### Objetivo y limite

Verificar que la gramatica y los tokens de Quantum Coffee permitan construir
el parser y representar el ASA reutilizando el explorador anterior. El alcance
es la etapa 3 de la imagen: sin analisis semantico ni generacion de codigo.
No se recibio aqui otra especificacion de la etapa 3 que imponga un algoritmo
de parser o una biblioteca concreta para representar el arbol.

### Evidencia por actividad

| WBS | Trabajo entregado | Estado |
| --- | --- | --- |
| 1.1 Revisar producciones | 40 producciones sintacticas: referencias, accesibilidad, consumo en repeticiones, recursion izquierda, terminales, FIRST/FOLLOW y casos validos/invalidos. | Verificado. |
| 1.2 Modificar solo si es necesario | No se agrego ni cambio sintaxis respecto del ZIP corregido anterior. Se delimito la documentacion para que la semantica no sea obligacion del parser. Se documenta la decision BARISTA + siguiente token. | Cumplido tecnicamente; no necesita otra ampliacion del lenguaje. |
| 1.3 Tokens, valores y posiciones | Campos reales y lexemas sin convertir; pruebas de todos los terminales, cadenas, signos, posiciones, LF/CRLF/CR, BOM, EOF y errores; imports y CLI compatibles. | Verificado y corregido donde fallaba. |
| 1.4 Interfaz con parser y ASA | Paquete integracion, protocolo del parser, tipos de resultado/error, esquema de nodos, ejemplo JSON y guia de conexion. | Contrato tecnico listo. Su acuerdo con las personas responsables sigue pendiente. |

### Problemas encontrados y solucion

1. **El scanner no se podia importar limpiamente como paquete.** Sus imports
   absolutos buscaban modulos sueltos. Ahora tiene `scanner/__init__.py` e
   imports relativos, conservando `python scanner/main.py archivo.qc`.
2. **Faltaba un EOF compartido.** Se agrego FIN_ARCHIVO al final del enum y
   se emite solo en el adaptador. No se altera la forma anterior de escanear.
3. **Las posiciones con CR eran incorrectas y los comentarios podian comerse
   la linea siguiente.** Se corrigio el conteo de CR y CRLF y el fin de
   comentario en ambos caracteres. LF y CRLF conservan sus posiciones.
4. **El reconocedor de pruebas anterior comparaba terminales por lexema.**
   Eso no demostraba la correspondencia exacta con TokenType. El nuevo
   reconocedor usa los tipos reales, detecta errores de escritura de EBNF y
   comprueba que todos sus terminales tienen token.
5. **No habia contrato para valores y posiciones del ASA.** Ahora se conservan
   los lexemas, se definen rangos y nodos, y se incluye un JSON de referencia.
6. **La especificacion mezclaba sintaxis con decisiones semanticas futuras.**
   Se sacaron esos requisitos de la referencia activa de esta tarea y se
   archivaron como antecedente no vinculante para el parser.

### Resultado de la gramatica

- Sin producciones sintacticas sin definir o inalcanzables.
- Sin recursion directa o indirecta por la izquierda.
- Ningun cuerpo de repeticion puede reconocer una entrada vacia.
- Correspondencia completa entre terminales y tokens existentes.
- Un unico conflicto predictivo LL(1), en `programa`, por BARISTA.
  Se resuelve mirando CHORREADOR o IDENTIFICADOR como siguiente token.
  No es una afirmacion de LL(1) estricto ni una demostracion general de
  ausencia de ambiguedad; la decision concreta esta especificada y probada.
- Los siete programas completos de la entrega anterior siguen reconocidos.
- Las restricciones de tipos, nombres, aridad de funciones normales y retornos
  NO se usan para rechazar sintaxis. La extension cuantica sigue reconocida.

Los FIRST/FOLLOW y el catalogo de tokens estan en `sección Análisis formal de la gramática`.

### Como repetir la revision

Desde la raiz del proyecto, con Python 3.9 o posterior y sin instalar paquetes:

```bash
python -m parser.verificacion.verificar_gramatica
python -m unittest parser.verificacion.test_integracion -v
```

Las salidas de la ultima ejecucion estan en `docs/RESULTADOS_VERIFICACION.txt`.
El reconocimiento de pruebas no es el parser del proyecto, y el JSON es un
ejemplo de contrato construido expresamente, no un ASA extraido por ese parser.
No se afirma que ya se ejecuto una integracion con los componentes de los
companeros, porque esos componentes no estan en los archivos disponibles.

### Criterio de finalizacion

La base tecnica queda lista: existe una gramatica de referencia y una entrada
de tokens que usa el mismo explorador, sin sustituirlo. Hay pruebas y contrato
para que las tareas 2.0, 3.0, 4.0 y 5.0 partan del mismo formato.

Para cerrar literalmente el punto 1.4 hace falta que las personas responsables
del parser y del ASA confirmen el contrato. Esta entrega deja todo preparado
para esa coordinacion, pero no inventa su aprobacion ni envia mensajes al equipo.

### Archivos de inicio para cada responsable

- Parser: `la sección Gramática EBNF de este documento`, `sección Análisis formal de la gramática`, `parser/integracion/entrada.py`
  y `parser/integracion/contratos.py`.
- ASA/representacion: `sección Interfaz scanner parser ASA`,
  `parser/integracion/contratos.py` y `docs/asa_referencia.json`.
- Integracion y pruebas: `parser/verificacion/test_integracion.py` y los siete
  archivos de `parser/ejemplos_completos/`.

## Gramática EBNF

Esta version integra la gramatica del Proyecto 1 con el scanner del Proyecto 2.
Es la referencia vigente; reemplaza las producciones anteriores.

### Convenciones

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

### 1. Tipos

```ebnf
tipo ::= "grano" | "poso" | "granoMolido" | "cafe" | "taza" tipo
```

`grano` es entero, `poso` es flotante, `granoMolido` es texto y `cafe` es
booleano. `taza tipo` es una lista homogenea; `taza taza grano` es una lista
de listas. `fuerte`, `ralo`, `descafeinado` y `SeQuemoElCafe` son valores,
no nombres de tipos.

### 2. Programa y funciones

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

### 3. Bloques y sentencias

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

### 4. Bifurcacion y ciclos

```ebnf
estructura_condicional ::= "hierve" "(" expresion ")" bloque [ "enfria" bloque ]
bucle_chorreando ::= "chorreando" "(" expresion ")" bloque
bucle_recolar ::= "recolar" "(" tipo identificador "en" identificador ")" bloque
```

`chorreando` evalua la condicion antes de cada vuelta, por lo que puede ejecutar
el bloque cero veces. `recolar` recorre los elementos de una lista en orden;
en una lista vacia no ejecuta el bloque. Se pueden anidar ciclos y condiciones.
Las llaves son obligatorias, incluso para un bloque vacio o de una sentencia.

### 5. Expresiones

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

### 6. Literales y reglas lexicas

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

### 7. Extension cuantica

```ebnf
declaracion_qubit ::= "qubit" identificador ";"
operacion_cuantica ::= compuerta_unaria | compuerta_binaria
compuerta_unaria ::= ( "H" | "X" | "Z" ) "(" identificador ")"
compuerta_binaria ::= "CNOT" "(" identificador "," identificador ")"
medicion_cuantica ::= "medir" "(" identificador ")"
```

Se conserva la extension original. Qubits, compuertas y mediciones siguen
siendo construcciones propias del lenguaje y conservan sus tokens.

### 8. Alcance del parser y del ASA

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
sección Interfaz scanner parser ASA. Las decisiones semanticas de
la revision anterior quedan archivadas como antecedentes en
`sección Antecedentes semánticos previos`, fuera de los criterios de esta tarea.

### 9. Repeticiones y analisis descendente

No hay recursion directa ni indirecta por la izquierda. Las repeticiones
EBNF generan secuencias de sentencias, argumentos, parametros y operadores.
Cada vuelta de esas repeticiones debe consumir tokens.

Las alternativas que comienzan con identificador estan factorizadas tanto en
sentencias como en factores. En el nivel del programa se conservan las
declaraciones originales: despues de `barista`, el analizador mira el siguiente
token (`chorreador` o identificador). La decision se toma con `BARISTA` y el token siguiente. El informe de
FIRST/FOLLOW identifica el conflicto LL(1) y documenta esta resolucion
determinista sin retroceso; no hace falta cambiar la sintaxis existente.

## Análisis formal de la gramática

Generado a partir de `la sección Gramática EBNF de este documento` y de los catalogos reales del scanner.
Los no terminales auxiliares de EBNF se expanden a BNF para calcular FIRST, FOLLOW y SELECT.
`EPSILON` significa entrada vacia. `FIN_ARCHIVO` pertenece al adaptador, no a las reglas lexicas.

Producciones sintacticas: **40**.
Terminales fijos: **51**. Categorias lexicas variables: **4**.
Comprobado: referencias definidas, producciones alcanzables y productivas,
ausencia de recursion izquierda y repeticiones que consumen entrada.

### Conflictos predictivos

Existe un solo conflicto LL(1), dentro de la repeticion inicial de `programa`:
BARISTA puede iniciar una funcion o la declaracion de chorreador.
El siguiente token resuelve la decision: IDENTIFICADOR continua la repeticion;
CHORREADOR termina la repeticion y comienza la funcion principal.
No se requiere retroceso ni una modificacion de las producciones existentes.
Estas comprobaciones no constituyen una demostracion general de no ambiguedad.

| Produccion | Alternativas BNF en conflicto | Tokens SELECT compartidos |
| --- | --- | --- |
| `programa` | `programa@9`, ramas 1 y 2 | `BARISTA` |

### FIRST y FOLLOW de las producciones originales

| Produccion | FIRST | FOLLOW |
| --- | --- | --- |
| `tipo` | `CAFE`, `GRANO`, `GRANO_MOLIDO`, `POSO`, `TAZA` | `IDENTIFICADOR` |
| `programa` | `BARISTA`, `CAFETERIA` | `FIN_ARCHIVO` |
| `declaracion_global` | `CAFETERIA` | `BARISTA`, `CAFETERIA` |
| `declaracion_funcion` | `BARISTA` | `BARISTA`, `CAFETERIA` |
| `declaracion_chorreador` | `BARISTA` | `FIN_ARCHIVO` |
| `parametros` | `CAFE`, `GRANO`, `GRANO_MOLIDO`, `POSO`, `TAZA` | `PARENTESIS_CIERRA` |
| `parametro` | `CAFE`, `GRANO`, `GRANO_MOLIDO`, `POSO`, `TAZA` | `COMA`, `PARENTESIS_CIERRA` |
| `argumentos` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `PARENTESIS_CIERRA` |
| `bloque` | `LLAVE_ABRE` | `BARISTA`, `CAFE`, `CAFETERIA`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `ENFRIA`, `FIN_ARCHIVO`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `sentencia` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `declaracion_var_local` | `CAFE`, `GRANO`, `GRANO_MOLIDO`, `POSO`, `TAZA` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `sentencia_identificador` | `IDENTIFICADOR` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `continuacion_sentencia` | `ASIGNACION`, `PARENTESIS_ABRE`, `PUNTO` | `PUNTO_COMA` |
| `sufijo_llamada` | `PARENTESIS_ABRE` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `sufijo_lista` | `PUNTO` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `metodo_lista` | `BUSCAR`, `EXTRAER`, `INSERTAR` | `PARENTESIS_ABRE` |
| `retorno_degustar` | `DEGUSTAR` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `estructura_condicional` | `HIERVE` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `bucle_chorreando` | `CHORREANDO` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `bucle_recolar` | `RECOLAR` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `expresion` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CORCHETE_CIERRA`, `PARENTESIS_CIERRA`, `PUNTO_COMA` |
| `expresion_or` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CORCHETE_CIERRA`, `PARENTESIS_CIERRA`, `PUNTO_COMA` |
| `expresion_and` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CORCHETE_CIERRA`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `SIN_AZUCAR` |
| `expresion_not` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `SIN_AZUCAR` |
| `expresion_relacional` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `SIN_AZUCAR` |
| `expresion_aritmetica` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `SIN_AZUCAR` |
| `termino` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `unario` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `factor` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `SE_QUEMO_EL_CAFE` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `op_or` | `SIN_AZUCAR` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` |
| `op_and` | `CON_AZUCAR` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` |
| `op_not` | `AMARGO` | `AMARGO`, `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` |
| `op_relacional` | `DIFERENTE`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `IDENTIFICADOR`, `MEDIR`, `PARENTESIS_ABRE`, `RALO`, `RESTA`, `SE_QUEMO_EL_CAFE`, `SUMA` |
| `literal` | `CADENA`, `CORCHETE_ABRE`, `DECIMAL`, `DESCAFEINADO`, `ENTERO`, `FUERTE`, `RALO`, `SE_QUEMO_EL_CAFE` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `arreglo` | `CORCHETE_ABRE` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |
| `declaracion_qubit` | `QUBIT` | `CAFE`, `CHORREANDO`, `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z`, `DEGUSTAR`, `GRANO`, `GRANO_MOLIDO`, `HIERVE`, `IDENTIFICADOR`, `LLAVE_CIERRA`, `MEDIR`, `POSO`, `QUBIT`, `RECOLAR`, `TAZA` |
| `operacion_cuantica` | `CNOT`, `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z` | `PUNTO_COMA` |
| `compuerta_unaria` | `COMPUERTA_H`, `COMPUERTA_X`, `COMPUERTA_Z` | `PUNTO_COMA` |
| `compuerta_binaria` | `CNOT` | `PUNTO_COMA` |
| `medicion_cuantica` | `MEDIR` | `COMA`, `CON_AZUCAR`, `CORCHETE_CIERRA`, `DIFERENTE`, `DIVISION`, `IGUALDAD`, `MAYOR`, `MAYOR_IGUAL`, `MENOR`, `MENOR_IGUAL`, `MODULO`, `MULTIPLICACION`, `PARENTESIS_CIERRA`, `PUNTO_COMA`, `RESTA`, `SIN_AZUCAR`, `SUMA` |

### Correspondencia exacta de terminales y tokens

| Terminal fijo | TokenType |
| --- | --- |
| `!=` | `DIFERENTE` |
| `%` | `MODULO` |
| `(` | `PARENTESIS_ABRE` |
| `)` | `PARENTESIS_CIERRA` |
| `*` | `MULTIPLICACION` |
| `+` | `SUMA` |
| `,` | `COMA` |
| `-` | `RESTA` |
| `.` | `PUNTO` |
| `/` | `DIVISION` |
| `;` | `PUNTO_COMA` |
| `<` | `MENOR` |
| `<=` | `MENOR_IGUAL` |
| `=` | `ASIGNACION` |
| `==` | `IGUALDAD` |
| `>` | `MAYOR` |
| `>=` | `MAYOR_IGUAL` |
| `Amargo` | `AMARGO` |
| `CNOT` | `CNOT` |
| `ConAzucar` | `CON_AZUCAR` |
| `H` | `COMPUERTA_H` |
| `SeQuemoElCafe` | `SE_QUEMO_EL_CAFE` |
| `SinAzucar` | `SIN_AZUCAR` |
| `X` | `COMPUERTA_X` |
| `Z` | `COMPUERTA_Z` |
| `[` | `CORCHETE_ABRE` |
| `]` | `CORCHETE_CIERRA` |
| `barista` | `BARISTA` |
| `buscar` | `BUSCAR` |
| `cafe` | `CAFE` |
| `cafeteria` | `CAFETERIA` |
| `chorreador` | `CHORREADOR` |
| `chorreando` | `CHORREANDO` |
| `degustar` | `DEGUSTAR` |
| `descafeinado` | `DESCAFEINADO` |
| `en` | `EN` |
| `enfria` | `ENFRIA` |
| `extraer` | `EXTRAER` |
| `fuerte` | `FUERTE` |
| `grano` | `GRANO` |
| `granoMolido` | `GRANO_MOLIDO` |
| `hierve` | `HIERVE` |
| `insertar` | `INSERTAR` |
| `medir` | `MEDIR` |
| `poso` | `POSO` |
| `qubit` | `QUBIT` |
| `ralo` | `RALO` |
| `recolar` | `RECOLAR` |
| `taza` | `TAZA` |
| `{` | `LLAVE_ABRE` |
| `}` | `LLAVE_CIERRA` |

| Regla lexica | TokenType |
| --- | --- |
| `identificador` | `IDENTIFICADOR` |
| `numero_entero` | `ENTERO` |
| `numero_decimal` | `DECIMAL` |
| `cadena` | `CADENA` |

`servir` y `leer` se reconocen como IDENTIFICADOR. Los miembros SERVIR y LEER
del enum son heredados y no deben esperarse en la salida actual.
FIN_ARCHIVO se agrega una sola vez en `parser/integracion/entrada.py`.

## Interfaz scanner parser ASA

Estado: contrato tecnico propuesto, implementado en `parser/integracion/` y probado.
Falta que las personas responsables del parser y del ASA lo acepten o acuerden
sus ajustes. No se afirma que ya hubo una reunion o un acuerdo del equipo.

### 1. Entrada real del explorador

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
`sección Análisis formal de la gramática` a partir de la EBNF y de los mapas reales del scanner.

### 2. Fin de archivo y errores lexicos

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

### 3. Cursor para el analizador descendente

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

### 4. Firma que implementara el parser

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

### 5. Decisiones de analisis

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

### 6. Representacion compartida del ASA

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

`docs/asa_referencia.json` es un ejemplo esperado construido para documentar el
contrato de `barista chorreador() { grano x = 2 + 3 * 4; }`. No es salida
de un parser ya implementado. El renderer puede usarlo para comenzar su trabajo.

### 7. Acuerdo del equipo pendiente

Antes de integrar los componentes, confirmar con sus responsables:

1. Uso del TokenType y de las clases de este paquete, con EOF solo en el adaptador.
2. Firma `analizar(tokens)` y formato de errores/ResultadoParseo.
3. Nombres, atributos, orden de hijos y rangos de NodoASA.
4. Politica ante errores lexicos y forma de mostrar arboles parciales.

No se necesitan cambios de sintaxis para aceptar este contrato. Si el equipo
prefiere otro esquema, actualizar contrato y pruebas juntos antes de duplicar
clases incompatibles. Esta lista documenta una coordinacion pendiente; no
equivale a un acuerdo ya confirmado con las otras personas.

## Programas de referencia

### 1. Ejercicio de números

```text
barista chorreador() {
    grano sacos_bodega = 15 ;
    poso peso_por_saco = 45.5 ;
    poso peso_total = sacos_bodega * peso_por_saco ;

    servir(peso_total) ;
}
```
### 2. Ejercicio de textos
```text
barista chorreador() {
    granoMolido cliente = "Don Juan" ;
    granoMolido pedido = "Capuchino doble" ;

    servir("Orden lista para: " + cliente) ;
    servir("Bebida: " + pedido) ;
}
```
### 3. Ejercicio de control de flujo
```text
# Uso de repeticion (chorreando) y bifurcacion (hierve/enfria)
barista chorreador() {
    grano temperatura = 20 ;

    chorreando (temperatura < 90) {
        temperatura = temperatura + 10 ;
    }

    hierve (temperatura >= 90) {
        servir("Agua al punto ideal para chorrear") ;
    } enfria {
        servir("Falta fuego, el agua esta fria") ;
    }
}
```

### 4. Ejercicio de listas
```text
# Manejo de arreglos e invocacion de metodos nativos
barista chorreador() {
    taza granoMolido menu = ["Espresso", "Americano"] ;

    menu.insertar("Latte") ;
    cafe hay_latte = menu.buscar("Latte") ;
    granoMolido servido = menu.extraer(0) ;

    servir("Bebida servida al cliente:") ;
    servir(servido) ;

    servir("Restante en el menu:") ;
    recolar (granoMolido bebida en menu) {
        servir(bebida) ;
    }
}
```

### 5. Ejercicio integrado
```text
# Uniendo tipos, funciones, booleanos, ciclos y condicionales complejos
barista auditarInventario(taza grano inventario) {
    grano total_granos = 0 ;
    cafe falta_cafe = ralo ;

    recolar (grano cantidad en inventario) {
        hierve (cantidad <= 5) {
            falta_cafe = fuerte ;
        }
        total_granos = total_granos + cantidad ;
    }

    hierve (falta_cafe == fuerte ConAzucar total_granos < 50) {
        servir("Alerta critica: Hay que tostar mas cafe urgente") ;
        degustar ralo ;
    } enfria {
        servir("Inventario de la cafeteria saludable") ;
        degustar fuerte ;
    }
}

barista chorreador() {
    taza grano bodega = [10, 4, 20, 15] ;
    cafe estado_tienda = auditarInventario(bodega) ;
}
```

## Ajustes de gramática

Nota de version: este archivo explica la correccion previa. La nueva revision
para la tarea 1 de la etapa 3 esta en `sección Estado y alcance del proyecto`. Ese informe y
la interfaz compartida prevalecen sobre los conteos y descripciones anteriores.

### Que se cambio

La base es el ZIP del scanner entregado para la revision. Se incorporo y
actualizo la EBNF del Proyecto 1 recuperada de `QuantumCoffee-main.zip`.
No habia un archivo de gramatica sintactica completa en el ZIP del scanner.

| Parte | Ajuste | Compatibilidad |
| --- | --- | --- |
| Gramatica oficial | `la sección Gramática EBNF de este documento` contiene la version completa y unificada. | Conserva tipos, globales, funciones, ciclos, listas y extension cuantica. |
| Ambiente estandar | `servir` y `leer` pasan a ser identificadores y llamadas regulares. | Los programas se escriben igual; cambian los nombres de esos dos tokens. |
| Numeros | Se agregan signos unarios antes de un factor. | Acepta negativos y expresiones como `-(a+b)` sin cambiar el reconocimiento numerico. |
| Logica | Se permite repetir `Amargo`. | Los casos con cero o una negacion siguen siendo validos. |
| Sentencias y factores | Se agrupan las alternativas que comienzan con identificador. | Se conserva la forma de asignar, llamar funciones y operar listas. |
| Retorno | Se permite `degustar;`, ademas del retorno con expresion. | Las funciones existentes mantienen sus firmas y retornos. |
| Listas | Se documentan los contratos de imprimir, insertar, extraer y buscar. | Se mantienen los tres metodos y sus tokens. |
| Ejercicios | Se corrige la llave extra del ejercicio 2 de Markdown. | Los otros cuatro ejercicios originales conservan su codigo. |
| Ejemplo del scanner | `buscar` se guarda en `cafe`; `leer` se guarda en `granoMolido`. | Corrige usos de tipos incoherentes; el scanner sigue sin comprobar tipos. |
| Resultados esperados | Se regeneran las cinco salidas del scanner. | Reflejan los tokens actuales, posiciones y errores. |

`TokenType.SERVIR` y `TokenType.LEER` se mantienen como miembros heredados
para no romper posibles imports del enum, pero el scanner ya no los emite.
Un futuro parser debe tratar esas llamadas como cualquier identificador con
parentesis, no depender de esos dos miembros.

### Que ya estaba correcto

- `chorreando` y `recolar` ya cubrian el requisito de repeticion.
- Las secuencias de sentencias, parametros, argumentos y operadores ya usaban
  repeticiones EBNF. Se conservaron.
- No se encontro recursion por la izquierda en la version de referencia.
  Se comprobo tambien que la version corregida no la introduce.
- `"taza" tipo` consume una palabra antes de recurrir: es recursion por la
  derecha y permite listas anidadas.
- Las llaves obligatorias mantienen una asociacion clara entre `hierve`
  y `enfria` cuando se anidan condiciones.

### Comprobaciones

Ejecutar desde la raiz:

```bash
python -m parser.verificacion.verificar_gramatica
```

El verificador lee las producciones de `la sección Gramática EBNF de este documento`, usa el scanner
real y comprueba:

- Referencias a producciones definidas y ausencia de recursion por la izquierda.
- Que los cuerpos de las repeticiones no puedan aceptar la cadena vacia.
- Los cinco ejercicios originales corregidos, un programa cuantico y un
  programa con las nuevas posibilidades: siete programas completos.
- Diez casos validos adicionales y diecisiete casos invalidos.
- La clasificacion de `servir` y `leer` como identificadores y la permanencia
  de los tokens de los metodos de lista y de las construcciones cuanticas.

Ademas se verifico la entrada por `scanner/main.py` de los siete programas,
sin errores lexicos. En los otros seis archivos `.qc` originales que no
requirieron corregir tipos, la comparacion con el scanner anterior mantuvo
lexemas, posiciones y errores; solo cambio la clasificacion de servir/leer.

Los archivos de `scanner/ejemplos/` son pruebas lexicas; algunos contienen
fragmentos de programa o errores intencionales. Para probar programas
sintacticamente completos, usar `parser/ejemplos_completos/`.

### Alcance

No se implemento una etapa nueva del compilador. El verificador es una
herramienta de validacion de la especificacion, no el parser de produccion.
El scanner sigue reconociendo tokens y errores lexicos. La inferencia de
retornos, el alcance de variables, los tipos, la biblioteca estandar y la
ejecucion cuantica son contratos documentados para las siguientes etapas;
todavia no se ejecutan ni validan semanticamente en el proyecto.

No se agregaron nuevas palabras para `for`, `break`, `continue`, tipos de
retorno o acceso por indice: no son necesarios para cumplir el PDF y
ampliarian la implementacion sin necesidad.

## Antecedentes semánticos previos

Este texto procede de la revision anterior. No es criterio de aceptacion del
parser ni del ASA y no se implementa en esta entrega. La presente tarea no
confirma ni amplía estas decisiones semanticas; su revision corresponde a una
etapa posterior.

### 8. Ambiente estandar y reglas de coherencia

Las firmas siguientes documentan el ambiente; no son producciones especiales.

| Operacion | Contrato |
| --- | --- |
| `servir(valor)` | Imprime un valor; si es una lista, imprime sus elementos en orden, entre corchetes. No devuelve un valor util. |
| `leer()` | Lee una linea y devuelve `granoMolido`. |
| `lista.insertar(valor)` | Agrega al final un valor del tipo de la lista. No devuelve un valor util. |
| `lista.extraer(indice)` | Elimina y devuelve el elemento en el indice entero, contado desde cero. |
| `lista.buscar(valor)` | Devuelve `fuerte` si existe el valor, o `ralo` si no existe. |

Estas comprobaciones corresponden al analisis semantico o a la ejecucion, no
se intentan expresar mediante mas producciones:

- Las condiciones y los operadores logicos requieren `cafe`; `fuerte` es
  verdadero y `ralo` es falso. `medir` devuelve `cafe`.
- `+` suma numeros o concatena dos textos. Los otros operadores aritmeticos
  requieren numeros y `%` requiere enteros. Se permite promocion de `grano`
  a `poso`, no conversion automatica de texto a numero.
- `leer()` no produce enteros directamente. Una conversion de texto a numero
  necesita una funcion de biblioteca definida para ese fin; no se inventa una
  conversion implicita que el proyecto no ha especificado.
- No se puede usar el resultado de `servir` o `insertar` como un valor.
- Cada bloque crea un alcance. Las globales pertenecen al programa; los
  parametros pertenecen a su funcion. La variable de `recolar` es local al ciclo.
  Se rechazan declaraciones duplicadas en el mismo alcance y lecturas de
  variables sin inicializar. Una asignacion busca el nombre desde el alcance
  mas cercano hacia el global.
- Las listas son homogeneas, incluso cuando se anidan. `recolar` requiere una
  lista cuyo tipo de elemento corresponda al tipo declarado para la variable.
  No se permite insertar o extraer elementos de la lista recorrida durante
  `recolar`, ni directamente ni a traves de otra referencia.
- Las funciones conservan su firma original, sin tipo de retorno escrito.
  El analizador debe inferir y comprobar un tipo de retorno consistente antes
  de validar las llamadas, considerando conjuntamente las funciones recursivas.
  Una funcion que devuelve valores debe devolverlos en todos sus caminos de
  terminacion normal. No se mezclan retornos con valor y sin valor.
  Una funcion sin valor termina con `degustar;` o al llegar al final del bloque.
- Para mantener los ejemplos del scanner, `chorreador` puede terminar sin
  retorno, con `degustar;` o con un estado `grano`, como `degustar 0;`.
- `descafeinado` y `SeQuemoElCafe` son valores especiales comprobables con
  `==` y `!=`. Se pueden almacenar como estados excepcionales de una variable;
  no son operandos aritmeticos, condiciones booleanas ni listas utilizables.
- Se rechazan indices negativos o fuera de rango y operaciones numericas
  invalidas. Los argumentos cuanticos deben ser qubits declarados; `CNOT`
  requiere dos qubits distintos.
- Los nombres globales de variables y funciones no se duplican. `servir` y
  `leer` se enlazan con la biblioteca y se protegen de redeclaraciones mediante
  la tabla de simbolos, sin convertirlos en palabras reservadas.

Estos contratos son especificacion para las siguientes etapas; el scanner
actual solo reconoce tokens y errores lexicos. No ejecuta estos comportamientos.


## Integración final de las tareas 4.4 y 5.3

El analizador conecta por defecto las producciones de control, funciones y
extensión cuántica. Todas comparten el cursor y el registro de errores; las
expresiones y los tipos se delegan al núcleo. Es posible inyectar otra conexión
para pruebas aisladas.

Se conserva el análisis descendente por producciones y los niveles de
precedencia de la EBNF. La decisión BARISTA usa el siguiente token para
distinguir una función de chorreador; no se afirma que sea LL(1) estricto.
La recuperación en modo pánico sincroniza en punto y coma, cierre de bloque o
fin de archivo. El bloque conserva su cierre y el cursor avanza al descartar
entrada; un árbol parcial con errores nunca se considera un parseo correcto.
La construcción del ASA conserva posiciones y lexemas, sin evaluar semántica.
Estas decisiones corresponden a los capítulos 4 y 5 de Aho, Lam, Sethi y
Ullman, Compilers: Principles, Techniques, and Tools, segunda edición.
Referencia: https://suif.stanford.edu/dragonbook/lecture-notes.html

La revisión técnica de 7.0 cubre lint y pruebas automatizadas de integración.
La defensa de cada integrante, sus reflexiones individuales y la presentación
por el medio exigido por el profesor deben completarse por el equipo.
