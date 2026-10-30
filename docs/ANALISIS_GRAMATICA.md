# Auditoria formal de la gramatica

Generado a partir de `gramatica/EBNF.md` y de los catalogos reales del scanner.
Los no terminales auxiliares de EBNF se expanden a BNF para calcular FIRST, FOLLOW y SELECT.
`EPSILON` significa entrada vacia. `FIN_ARCHIVO` pertenece al adaptador, no a las reglas lexicas.

Producciones sintacticas: **40**.
Terminales fijos: **51**. Categorias lexicas variables: **4**.
Comprobado: referencias definidas, producciones alcanzables y productivas,
ausencia de recursion izquierda y repeticiones que consumen entrada.

## Conflictos predictivos

Existe un solo conflicto LL(1), dentro de la repeticion inicial de `programa`:
BARISTA puede iniciar una funcion o la declaracion de chorreador.
El siguiente token resuelve la decision: IDENTIFICADOR continua la repeticion;
CHORREADOR termina la repeticion y comienza la funcion principal.
No se requiere retroceso ni una modificacion de las producciones existentes.
Estas comprobaciones no constituyen una demostracion general de no ambiguedad.

| Produccion | Alternativas BNF en conflicto | Tokens SELECT compartidos |
| --- | --- | --- |
| `programa` | `programa@9`, ramas 1 y 2 | `BARISTA` |

## FIRST y FOLLOW de las producciones originales

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

## Correspondencia exacta de terminales y tokens

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
FIN_ARCHIVO se agrega una sola vez en `integracion/entrada.py`.
