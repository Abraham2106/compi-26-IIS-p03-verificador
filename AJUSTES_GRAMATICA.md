# Ajustes de gramatica de Quantum Coffee

Nota de version: este archivo explica la correccion previa. La nueva revision
para la tarea 1 de la etapa 3 esta en `docs/REVISION_WBS_1.md`. Ese informe y
la interfaz compartida prevalecen sobre los conteos y descripciones anteriores.

## Que se cambio

La base es el ZIP del scanner entregado para la revision. Se incorporo y
actualizo la EBNF del Proyecto 1 recuperada de `QuantumCoffee-main.zip`.
No habia un archivo de gramatica sintactica completa en el ZIP del scanner.

| Parte | Ajuste | Compatibilidad |
| --- | --- | --- |
| Gramatica oficial | `gramatica/EBNF.md` contiene la version completa y unificada. | Conserva tipos, globales, funciones, ciclos, listas y extension cuantica. |
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

## Que ya estaba correcto

- `chorreando` y `recolar` ya cubrian el requisito de repeticion.
- Las secuencias de sentencias, parametros, argumentos y operadores ya usaban
  repeticiones EBNF. Se conservaron.
- No se encontro recursion por la izquierda en la version de referencia.
  Se comprobo tambien que la version corregida no la introduce.
- `"taza" tipo` consume una palabra antes de recurrir: es recursion por la
  derecha y permite listas anidadas.
- Las llaves obligatorias mantienen una asociacion clara entre `hierve`
  y `enfria` cuando se anidan condiciones.

## Comprobaciones

Ejecutar desde la raiz:

```bash
python verificacion/verificar_gramatica.py
```

El verificador lee las producciones de `gramatica/EBNF.md`, usa el scanner
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
sintacticamente completos, usar `ejemplos_completos/`.

## Alcance

No se implemento una etapa nueva del compilador. El verificador es una
herramienta de validacion de la especificacion, no el parser de produccion.
El scanner sigue reconociendo tokens y errores lexicos. La inferencia de
retornos, el alcance de variables, los tipos, la biblioteca estandar y la
ejecucion cuantica son contratos documentados para las siguientes etapas;
todavia no se ejecutan ni validan semanticamente en el proyecto.

No se agregaron nuevas palabras para `for`, `break`, `continue`, tipos de
retorno o acceso por indice: no son necesarios para cumplir el PDF y
ampliarian la implementacion sin necesidad.
