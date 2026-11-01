# Registro de defectos y repeticion de pruebas: punto 6.5

Proyecto: Quantum Coffee, etapa 3  
Fecha: 1 de noviembre de 2026  
Fuente de los defectos: ejecucion de los casos 6.2 y 6.3 (`docs/Evidencia/ejecucion.txt`) y la comparacion del ASA de 6.4.

## Resumen

| ID | Casos | Tipo | Estado |
| --- | --- | --- | --- |
| D01 | I13, I14, I15, I17 | Parser: error falso en cascada | Corregido y re-probado |
| D02 | Prueba de 6.4 | Prueba: mencion desactualizada al parser | Corregido |

Los 25 casos invalidos se rechazaban y los 13 validos se aceptaban desde la primera ejecucion; los defectos estan en la calidad de los mensajes, no en la aceptacion o el rechazo.

## D01. Segundo error falso despues de un error dentro de un bloque anidado

**Casos:** I13 (asignacion en condicion), I14 (comparacion encadenada), I15 (alternativa sin condicional), I17 (recolar sin `en`).

**Que paso.** Ademas del error real, el parser agregaba un segundo mensaje que no corresponde a ningun error del programa. Ejemplo con I13:

```qc
barista chorreador() {
    hierve(x=1) {}
}
```

```
Linea 2, columna 13: Se esperaba PARENTESIS_CIERRA, pero se encontro ASIGNACION ('=') al analizar condicional
Despues de 'barista chorreador' no puede haber mas codigo; se encontro '}'      <- falso
```

**Que se esperaba.** Un solo mensaje, el primero. El codigo restante (`{}` y la `}` final) esta bien escrito.

**Causa.** Despues de un error, `ControlSintactico.sincronizar` avanza hasta un punto seguro. Se detenia en la primera `}`, aunque fuera la de un bloque anidado cuya `{` ya habia saltado. El bloque de `chorreador` interpretaba esa `}` como la suya, se cerraba antes de tiempo y la `}` real quedaba como "codigo despues de chorreador".

**Correccion.** En `parser/errores_sintacticos.py`, `sincronizar` cuenta las llaves que va saltando. Solo se detiene en una `}` o un `;` del nivel donde empezo. No se cambio ninguna otra funcion.

**Re-prueba** (los mismos programas de `Casos_6.2_y_6.3.md`, antes y despues del cambio):

| Caso | Mensajes antes | Mensajes despues | Primer mensaje |
| --- | --- | --- | --- |
| I13 | 2 | 1 | Sin cambio |
| I14 | 2 | 1 | Sin cambio |
| I15 | 2 | 1 | Sin cambio |
| I17 | 2 | 1 | Sin cambio |

Los otros 34 casos dieron la misma cantidad de mensajes y la misma aceptacion o rechazo que antes. I25 sigue reportando sus dos errores reales. Las pruebas del proyecto se repitieron completas despues del cambio: todas pasan.

## D02. Mencion desactualizada al parser en la prueba de 6.4

La prueba que compara el ASA manual con el del parser decia que se ajustaria "cuando haya parser" y se saltaba si no podia importarlo. Ya existe el parser, asi que esa mencion estaba desactualizada. Se corrigio en `parser/verificacion/test_asa_manual.py`.

## Observaciones que no son defectos

- **I24 muestra el mismo mensaje dos veces** ("Se esperaba LLAVE_CIERRA ... fin de archivo"). Es correcto: el programa deja dos bloques sin cerrar (el de `chorreador` y el de `hierve`), y cada uno se reporta. Una mejora posible seria indicar cual bloque falta, pero no afecta la correccion.
- **I25 reporta dos errores a proposito** y conserva `grano c=3;` en el ASA parcial, como se espera.
- Estas pruebas cubren los casos listados y no aseguran el comportamiento con cualquier entrada.

## Como repetir la verificacion

Desde la raiz del proyecto:

```bash
python -m unittest discover -s . -t . -p "test_*.py"
```
