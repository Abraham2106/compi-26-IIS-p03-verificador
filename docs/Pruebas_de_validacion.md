# Pruebas y validacion: puntos 6.2 y 6.3

Responsable: Miguel Dario Soto Badilla  
Proyecto: Quantum Coffee, etapa 3  
Fecha de ejecucion: 31 de octubre de 2026 (Costa Rica)  
Entorno: Python 3.12.14

## Como se hicieron las pruebas

Se prepararon programas pequenos usando la gramatica de `docs/Documentacion.md`. Cada programa esta en un archivo `.qc` y tiene su resultado esperado en `casos.json`.

Primero se revisa que el scanner no encuentre errores lexicos. Despues se pasa el programa al parser. Si el caso es valido, debe aceptarlo y generar un ASA con la estructura correcta. Si tiene errores de sintaxis, debe rechazarlo y mostrar donde encontro el problema.

En los casos I06 a I25 tambien se revisa el primer token que causa el error. En I25 se comprueba que el parser pueda seguir leyendo despues de encontrar dos errores.

Estas pruebas corresponden a la etapa 3. Los puntos 6.4 y 6.5 quedan con el otro integrante.

## 6.2 Construcciones sintacticamente validas

Se hicieron 13 casos con construcciones permitidas por la gramatica. En todos se esperaba `correcto=True`, sin errores y con un ASA de estructura valida.

| Caso | Construccion | Resultado obtenido |
| --- | --- | --- |
| V01 | Principal minimo | Aceptado; ASA valido |
| V02 | Tipos y literales | Aceptado; ASA valido |
| V03 | Aritmetica y signos | Aceptado; ASA valido |
| V04 | Comparaciones y logica | Aceptado; ASA valido |
| V05 | Listas y metodos | Aceptado; ASA valido |
| V06 | Entrada salida y asignacion | Aceptado; ASA valido |
| V07 | Condicional con alternativa | Aceptado; ASA valido |
| V08 | Condicional sin alternativa | Aceptado; ASA valido |
| V09 | Ciclos anidados | Aceptado; ASA valido |
| V10 | Extension cuantica | Aceptado; ASA valido |
| V11 | Retornos | Aceptado; ASA valido |
| V12 | Sintaxis sin comprobacion semantica | Aceptado; ASA valido |
| V13 | Globales funciones parametros y llamadas | Aceptado; ASA valido |

En V12 se asigna un texto a una variable `grano` y se llama a una funcion que no esta declarada. Aunque eso tendria problemas semanticos, la sintaxis esta bien y el parser debe aceptarla. V11 prueba `degustar;` y `degustar 1;`; aqui no se revisa si el segundo retorno llegaria a ejecutarse.

## 6.3 Entradas con errores sintacticos

Se hicieron 25 casos con errores puestos a proposito. En todos se esperaba `correcto=False` y al menos un mensaje de error sintactico. Si queda un ASA parcial, eso no significa que el programa haya sido aceptado.

| Caso | Error introducido | Resultado obtenido |
| --- | --- | --- |
| I01 | Programa vacio | Rechazado; 1 mensaje de error |
| I02 | Falta principal | Rechazado; 1 mensaje de error |
| I03 | Principal duplicado | Rechazado; 1 mensaje de error |
| I04 | Parametros en principal | Rechazado; 1 mensaje de error |
| I05 | Codigo despues de principal | Rechazado; 1 mensaje de error |
| I06 | Falta punto y coma | Rechazado; 1 mensaje de error |
| I07 | Falta inicializador | Rechazado; 1 mensaje de error |
| I08 | Falta operando | Rechazado; 1 mensaje de error |
| I09 | Falta parentesis | Rechazado; 1 mensaje de error |
| I10 | Falta cierre de lista | Rechazado; 1 mensaje de error |
| I11 | Coma final en lista | Rechazado; 1 mensaje de error |
| I12 | Coma final en llamada | Rechazado; 1 mensaje de error |
| I13 | Asignacion en condicion | Rechazado; 2 mensajes de error |
| I14 | Comparacion encadenada | Rechazado; 2 mensajes de error |
| I15 | Alternativa sin condicional | Rechazado; 2 mensajes de error |
| I16 | Ciclo sin llaves | Rechazado; 1 mensaje de error |
| I17 | Recolar sin en | Rechazado; 2 mensajes de error |
| I18 | Metodo sin argumento | Rechazado; 1 mensaje de error |
| I19 | CNOT sin coma | Rechazado; 1 mensaje de error |
| I20 | Compuerta con literal | Rechazado; 1 mensaje de error |
| I21 | Medicion sin argumento | Rechazado; 1 mensaje de error |
| I22 | Tipo reemplazado por literal | Rechazado; 1 mensaje de error |
| I23 | Identificador aislado | Rechazado; 1 mensaje de error |
| I24 | Fin inesperado | Rechazado; 2 mensajes de error |
| I25 | Dos errores y recuperacion | Rechazado; 2 mensajes de error |

### Dos ejemplos

I07 contiene:

```qc
barista chorreador() {
    grano x=;
}
```

Falta el valor despues del `=`. El parser lo detecta al llegar al `;`, en la linea 2, columna 13. El mensaje completo esta en `ejecucion.txt`.

I25 contiene:

```qc
barista chorreador() {
    grano a=;
    grano b=;
    grano c=3;
}
```

El parser encontro los dos valores faltantes, en las lineas 2 y 3, columna 13. Luego pudo seguir y guardar `grano c=3;` en el ASA parcial.

## Como volver a ejecutarlas

Desde la raiz del proyecto:

```bash
python -m parser.verificacion.pruebas_6_2_6_3
```

Este comando corre los 38 casos y guarda los resultados en `docs/evidencia_6_2_6_3/ejecucion.txt` y `resultados.json`. Devuelve 0 si todos pasan y 1 si alguno falla.

Para correr tambien las demas pruebas del proyecto:

```bash
python -m unittest discover -s parser/verificacion -t . -v
```

## Resultados

Pasaron los **38 casos**: se aceptaron los 13 validos y se rechazaron los 25 invalidos. Ninguno tuvo errores lexicos. Las pruebas completas del proyecto tambien pasaron: **133 pruebas, OK**. Los 38 casos nuevos se cuentan como subcasos dentro de una de esas pruebas.

En algunos casos, como I13, I14 e I15, aparecen mensajes adicionales mientras el parser intenta continuar. Se dejo la salida tal como se obtuvo para poder revisarla. Estos resultados corresponden a los casos probados; no aseguran que el parser funcione para cualquier entrada.

## Que archivos subir

- `parser/pruebas_6_2_6_3/`: los programas `.qc` y sus resultados esperados.
- `parser/verificacion/pruebas_6_2_6_3.py`: corre los casos y guarda los resultados.
- `parser/verificacion/test_pruebas_6_2_6_3.py`: permite correrlos con unittest.
- `docs/Pruebas_6_2_y_6_3.md`: este documento.
- `docs/evidencia_6_2_6_3/`: las salidas de las pruebas.

Se deben copiar respetando esas carpetas. No se cambio la implementacion del parser.
