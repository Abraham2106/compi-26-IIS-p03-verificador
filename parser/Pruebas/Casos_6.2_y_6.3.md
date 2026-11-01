# Casos de prueba: 6.2 y 6.3

Quantum Coffee — Miguel Dario Soto Badilla

Se probaron 38 casos: 13 validos y 25 invalidos. Todos dieron el resultado esperado y ninguno tuvo errores lexicos. Entorno: Python 3.12.14.

Los casos validos deben ser aceptados y generar un ASA con estructura correcta. Los invalidos deben ser rechazados con mensajes de error. Aqui solo se revisa sintaxis, sin analisis semantico ni ejecucion del programa.

## 6.2 Casos validos

### V01 — Principal minimo

```qc
barista chorreador() {
    
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V02 — Tipos y literales

```qc
barista chorreador() {
    grano a; poso b=2.5; granoMolido c="cafe"; cafe d=fuerte; cafe e=ralo; grano f=descafeinado; grano g=SeQuemoElCafe;
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V03 — Aritmetica y signos

```qc
barista chorreador() {
    grano x=-(2+3)*-2/1%3; grano y=10-3-2;
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V04 — Comparaciones y logica

```qc
barista chorreador() {
    cafe x=Amargo 1<2 ConAzucar 3>=2 SinAzucar ralo; cafe y=1==1; cafe z=1!=2; cafe w=2<=3;
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V05 — Listas y metodos

```qc
barista chorreador() {
    taza grano a=[]; taza taza grano b=[[1,2],[]]; a.insertar(2); grano x=a.extraer(0); cafe y=a.buscar(2);
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V06 — Entrada salida y asignacion

```qc
barista chorreador() {
    granoMolido x=leer(); x="hola"; servir(x);
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V07 — Condicional con alternativa

```qc
barista chorreador() {
    hierve(fuerte) {servir(1);} enfria {servir(0);}
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V08 — Condicional sin alternativa

```qc
barista chorreador() {
    hierve(ralo) {}
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V09 — Ciclos anidados

```qc
barista chorreador() {
    taza grano a=[1,2]; chorreando(fuerte) {recolar(grano x en a) {hierve(x>0) {servir(x);}}}
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V10 — Extension cuantica

```qc
barista chorreador() {
    qubit q; qubit r; H(q); X(q); Z(q); CNOT(q,r); cafe x=medir(q); medir(r);
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

### V11 — Retornos

```qc
barista chorreador() {
    degustar; degustar 1;
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

Este caso prueba las dos formas de `degustar`. No se comprueba si el segundo retorno llegaria a ejecutarse.

**Resultado de la prueba:** Pasa.

### V12 — Sintaxis sin comprobacion semantica

```qc
barista chorreador() {
    grano x="texto"; desconocida(x);
}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

La asignacion de texto a `grano` y la llamada a una funcion no declarada se aceptan porque sus problemas son semanticos, fuera de esta etapa.

**Resultado de la prueba:** Pasa.

### V13 — Globales funciones parametros y llamadas

```qc
cafeteria grano limite=2;
barista sumar(grano a, grano b) {degustar a+b;}
barista chorreador() {grano x=sumar(limite,3);}
```

**Se esperaba:** Aceptar el programa, sin errores sintacticos y con un ASA de estructura valida.

**Se obtuvo:** Aceptado; ASA con estructura valida.

**Resultado de la prueba:** Pasa.

## 6.3 Casos invalidos

### I01 — Programa vacio

```qc
# Archivo vacio
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Falta la funcion principal 'barista chorreador()' al final del programa
```

**Resultado de la prueba:** Pasa.

### I02 — Falta principal

```qc
barista f() {}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Falta la funcion principal 'barista chorreador()' al final del programa
```

**Resultado de la prueba:** Pasa.

### I03 — Principal duplicado

```qc
barista chorreador() {} barista chorreador() {}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Despues de 'barista chorreador' no puede haber mas codigo; se encontro 'barista'
```

**Resultado de la prueba:** Pasa.

### I04 — Parametros en principal

```qc
barista chorreador(grano x) {}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 1, columna 20: Se esperaba PARENTESIS_CIERRA, pero se encontro GRANO ('grano') al analizar funcion principal
```

**Resultado de la prueba:** Pasa.

### I05 — Codigo despues de principal

```qc
barista chorreador() {} cafeteria grano x;
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Despues de 'barista chorreador' no puede haber mas codigo; se encontro 'cafeteria'
```

**Resultado de la prueba:** Pasa.

### I06 — Falta punto y coma

```qc
barista chorreador() {
    grano x=1
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `LLAVE_CIERRA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 3, columna 1: Se esperaba PUNTO_COMA, pero se encontro LLAVE_CIERRA ('}') al analizar declaracion de variable
```

**Resultado de la prueba:** Pasa.

### I07 — Falta inicializador

```qc
barista chorreador() {
    grano x=;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 13: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PUNTO_COMA (';') al analizar expresion
```

**Resultado de la prueba:** Pasa.

### I08 — Falta operando

```qc
barista chorreador() {
    grano x=2+;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 15: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PUNTO_COMA (';') al analizar expresion
```

**Resultado de la prueba:** Pasa.

### I09 — Falta parentesis

```qc
barista chorreador() {
    servir(1;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 13: Se esperaba PARENTESIS_CIERRA o COMA, pero se encontro PUNTO_COMA (';') al analizar argumentos de llamada
```

**Resultado de la prueba:** Pasa.

### I10 — Falta cierre de lista

```qc
barista chorreador() {
    taza grano a=[1,2;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 22: Se esperaba CORCHETE_CIERRA o COMA, pero se encontro PUNTO_COMA (';') al analizar arreglo
```

**Resultado de la prueba:** Pasa.

### I11 — Coma final en lista

```qc
barista chorreador() {
    taza grano a=[1,];
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `CORCHETE_CIERRA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 21: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro CORCHETE_CIERRA (']') al analizar expresion
```

**Resultado de la prueba:** Pasa.

### I12 — Coma final en llamada

```qc
barista chorreador() {
    f(1,);
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PARENTESIS_CIERRA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 9: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PARENTESIS_CIERRA (')') al analizar expresion
```

**Resultado de la prueba:** Pasa.

### I13 — Asignacion en condicion

```qc
barista chorreador() {
    hierve(x=1) {}
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `ASIGNACION`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 13: Se esperaba PARENTESIS_CIERRA, pero se encontro ASIGNACION ('=') al analizar condicional
Despues de 'barista chorreador' no puede haber mas codigo; se encontro '}'
```

**Resultado de la prueba:** Pasa.

### I14 — Comparacion encadenada

```qc
barista chorreador() {
    hierve(a<b<c) {}
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `MENOR`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
No se admiten comparaciones encadenadas; use 'a < b ConAzucar b < c'
Despues de 'barista chorreador' no puede haber mas codigo; se encontro '}'
```

**Resultado de la prueba:** Pasa.

### I15 — Alternativa sin condicional

```qc
barista chorreador() {
    enfria {}
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `ENFRIA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 5: Se esperaba GRANO o POSO o GRANO_MOLIDO o CAFE o TAZA o QUBIT o COMPUERTA_H o COMPUERTA_X o COMPUERTA_Z o CNOT o MEDIR o IDENTIFICADOR o HIERVE o CHORREANDO o RECOLAR o DEGUSTAR, pero se encontro ENFRIA ('enfria') al analizar sentencia
Despues de 'barista chorreador' no puede haber mas codigo; se encontro '}'
```

**Resultado de la prueba:** Pasa.

### I16 — Ciclo sin llaves

```qc
barista chorreador() {
    chorreando(fuerte) servir(1);
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `IDENTIFICADOR`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 24: Se esperaba LLAVE_ABRE, pero se encontro IDENTIFICADOR ('servir') al analizar bloque
```

**Resultado de la prueba:** Pasa.

### I17 — Recolar sin en

```qc
barista chorreador() {
    recolar(grano x datos) {}
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `IDENTIFICADOR`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 21: Se esperaba EN, pero se encontro IDENTIFICADOR ('datos') al analizar ciclo recolar
Despues de 'barista chorreador' no puede haber mas codigo; se encontro '}'
```

**Resultado de la prueba:** Pasa.

### I18 — Metodo sin argumento

```qc
barista chorreador() {
    a.extraer();
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PARENTESIS_CIERRA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 15: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PARENTESIS_CIERRA (')') al analizar expresion
```

**Resultado de la prueba:** Pasa.

### I19 — CNOT sin coma

```qc
barista chorreador() {
    CNOT(q r);
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `IDENTIFICADOR`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 12: Se esperaba COMA, pero se encontro IDENTIFICADOR ('r') al analizar compuerta CNOT
```

**Resultado de la prueba:** Pasa.

### I20 — Compuerta con literal

```qc
barista chorreador() {
    H(1);
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `ENTERO`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 7: Se esperaba IDENTIFICADOR, pero se encontro ENTERO ('1') al analizar qubit de compuerta unaria
```

**Resultado de la prueba:** Pasa.

### I21 — Medicion sin argumento

```qc
barista chorreador() {
    medir();
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PARENTESIS_CIERRA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 11: Se esperaba IDENTIFICADOR, pero se encontro PARENTESIS_CIERRA (')') al analizar qubit de medicion
```

**Resultado de la prueba:** Pasa.

### I22 — Tipo reemplazado por literal

```qc
barista chorreador() {
    fuerte x;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `FUERTE`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 5: Se esperaba GRANO o POSO o GRANO_MOLIDO o CAFE o TAZA o QUBIT o COMPUERTA_H o COMPUERTA_X o COMPUERTA_Z o CNOT o MEDIR o IDENTIFICADOR o HIERVE o CHORREANDO o RECOLAR o DEGUSTAR, pero se encontro FUERTE ('fuerte') al analizar sentencia
```

**Resultado de la prueba:** Pasa.

### I23 — Identificador aislado

```qc
barista chorreador() {
    x;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 6: Se esperaba ASIGNACION o PARENTESIS_ABRE o PUNTO, pero se encontro PUNTO_COMA (';') al analizar sentencia que inicia con 'x'
```

**Resultado de la prueba:** Pasa.

### I24 — Fin inesperado

```qc
barista chorreador() {
    hierve(fuerte) {
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `FIN_ARCHIVO`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 3, columna 1: Se esperaba LLAVE_CIERRA, pero se encontro fin de archivo al analizar bloque
Linea 3, columna 1: Se esperaba LLAVE_CIERRA, pero se encontro fin de archivo al analizar bloque
```

**Resultado de la prueba:** Pasa.

### I25 — Dos errores y recuperacion

```qc
barista chorreador() {
    grano a=;
    grano b=;
    grano c=3;
}
```

**Se esperaba:** Rechazar el programa y reportar al menos un error sintactico.

Primer token de error esperado: `PUNTO_COMA`.

**Se obtuvo:** Rechazado.

Mensajes del parser:

```text
Linea 2, columna 13: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PUNTO_COMA (';') al analizar expresion
Linea 3, columna 13: Se esperaba ENTERO o DECIMAL o CADENA o FUERTE o RALO o DESCAFEINADO o SE_QUEMO_EL_CAFE o CORCHETE_ABRE o IDENTIFICADOR o MEDIR o PARENTESIS_ABRE o AMARGO o SUMA o RESTA, pero se encontro PUNTO_COMA (';') al analizar expresion
```

Tambien se comprobo que aparecieran exactamente dos errores y que `grano c=3;` quedara en el ASA parcial. Esta comprobacion paso.

**Resultado de la prueba:** Pasa.

## Como ejecutar las pruebas

Desde la raiz del proyecto, con los archivos de pruebas instalados:

```bash
python -m parser.verificacion.pruebas_6_2_6_3
```

Para correr todas las pruebas del proyecto:

```bash
python -m unittest discover -s parser/verificacion -t . -v
```

La ejecucion completa dio 133 pruebas, OK. Los 38 casos de este documento se ejecutan como subcasos de una de esas pruebas. Algunos casos invalidos producen mensajes adicionales durante la recuperacion; arriba se muestran tal como los devolvio el parser. Un ASA parcial no significa que el programa fue aceptado.
