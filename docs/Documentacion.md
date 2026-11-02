# Quantum Coffee

## Gramatica

EBNF del parser y entrada del verificador de gramatica.

```ebnf
tipo ::= "grano" | "poso" | "granoMolido" | "cafe" | "taza" tipo
programa ::= { declaracion_global | declaracion_funcion } declaracion_chorreador
declaracion_global ::= "cafeteria" tipo identificador [ "=" expresion ] ";"
declaracion_funcion ::= "barista" identificador "(" [ parametros ] ")" bloque
declaracion_chorreador ::= "barista" "chorreador" "(" ")" bloque
parametros ::= parametro { "," parametro }
parametro ::= tipo identificador
argumentos ::= expresion { "," expresion }
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
estructura_condicional ::= "hierve" "(" expresion ")" bloque [ "enfria" bloque ]
bucle_chorreando ::= "chorreando" "(" expresion ")" bloque
bucle_recolar ::= "recolar" "(" tipo identificador "en" identificador ")" bloque
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
declaracion_qubit ::= "qubit" identificador ";"
operacion_cuantica ::= compuerta_unaria | compuerta_binaria
compuerta_unaria ::= ( "H" | "X" | "Z" ) "(" identificador ")"
compuerta_binaria ::= "CNOT" "(" identificador "," identificador ")"
medicion_cuantica ::= "medir" "(" identificador ")"
```
