# Tabla de simbolos (1.2.1, 1.2.2, 1.2.3, 1.4.1)

Codigo: `parser/semantica/tabla_simbolos.py`, conectada al verificador en
`parser/semantica/analisis.py` (`FABRICA_TABLA`), e impresion en
`parser/semantica/impresion_tabla.py`.
Pruebas: `parser/verificacion/test_tabla_simbolos.py`,
`test_impresion_tabla.py` y `test_ambitos.py`.

## 1.2.1 Diseno

### Datos de cada simbolo (`Simbolo`)

| Campo | Contenido |
| --- | --- |
| `nombre` | Texto del identificador. |
| `categoria` | `Categoria`: variable global, variable local, parametro, variable de recolar, qubit, funcion o funcion incorporada. |
| `tipo` | Tipo declarado; si el lenguaje no lo escribe (retorno de funciones), el que dejo la inferencia. |
| `definicion` | Nodo del ASA que lo declara (referencia, no copia). `None` solo en funciones incorporadas. |
| `ambito` | `Ambito` donde se registro (numero, nivel y ambito padre). |
| `parametros` | Solo funciones: tipos de sus parametros, en orden. |
| `posicion` | Linea y columna de la definicion. |

### Operaciones (`TablaSimbolos`)

Contrato que usa el Visitor (el mismo de la tabla provisional, por eso el
verificador no cambio su forma de llamarla):

| Operacion | Resultado |
| --- | --- |
| `declarar(nombre, nodo)` | `True` si se registro; `False` si choca en el ambito actual. |
| `resolver(nombre)` | Nodo de la declaracion visible mas cercana, o `None`. |
| `entrar()` / `salir()` | Abre o cierra un ambito. No se puede salir del global. |

Operaciones adicionales para el checker y la impresion:

| Operacion | Resultado |
| --- | --- |
| `registrar(nombre, nodo)` | `Simbolo` registrado, o `None` si hubo conflicto. |
| `buscar(nombre)` | `Simbolo` visible mas cercano (incluye incorporadas). |
| `buscar_local(nombre)` | `Simbolo` del espacio de nombres actual. |
| `conflictos` | Lista de `Conflicto(nuevo, existente)` rechazados. |
| `simbolos()` | Todos los simbolos registrados, incluso de ambitos ya cerrados. |
| `simbolo_de(nodo)` | Simbolo cuya definicion es ese nodo. |
| `filas()` / `a_texto()` | Datos y texto de la tabla para imprimir. |

## 1.2.2 Ambitos

- El nivel 0 es el global. Se abre un ambito por cada funcion (parametros),
  cada bloque `{ }` y cada `recolar` (variable del ciclo).
- La busqueda va del ambito actual hacia afuera; al final se consultan las
  funciones incorporadas `servir` y `leer`, que el programa puede ocultar.
- Un nombre no se puede repetir en el mismo ambito, sea cual sea su
  categoria.
- Un ambito interno puede sombrear un nombre externo.
- Los parametros y el bloque del cuerpo de la funcion forman un solo espacio
  de nombres; lo mismo la variable de `recolar` y su bloque. Redeclararlos
  ahi es un error. En bloques mas internos si se pueden sombrear.
- Globales y funciones se registran antes de recorrer el programa (lo hace
  el verificador), asi que se pueden usar antes de su declaracion.

## 1.2.3 Registro

El verificador registra cada declaracion al visitarla: globales y funciones
al inicio del programa; parametros, locales, qubits y la variable de
`recolar` en su ambito. Una local se registra despues de visitar su
inicializador, asi `grano x = x;` es un error.

Despues de `verificar_semantica(arbol, tabla)`, la tabla conserva todo lo
registrado y los tipos de retorno inferidos. Ejemplo con
`parser/ejemplos_semanticos/E02_redeclarado.qc`:

```python
tabla = TablaSimbolos()
verificar_semantica(arbol, tabla)
print(tabla.a_texto())
```

```
Ambito  Nombre  Categoria        Tipo                     Definicion
------  ------  ---------------  -----------------------  ----------
0       limite  variable global  grano                    2:1
0       sumar   funcion          (grano, grano) -> grano  4:1
1       a       parametro        grano                    4:15
3       x       variable local   grano                    9:5
```

Las declaraciones rechazadas no aparecen en la tabla; quedan en
`tabla.conflictos` y el verificador las reporta como
`identificador 'x' ya declarado en este ambito`.

## 1.4.1 Imprimir cambios de tabla

La tabla anota en `tabla.cambios` cada operacion, en el orden en que ocurre
durante el recorrido: `entrar`, `registrar`, `conflicto` (con la declaracion
previa) y `salir` (con los simbolos que tenia el ambito al cerrarse). Con
`--tabla`, el verificador imprime cada cambio en el momento en que sucede,
junto con el estado parcial visible de los ambitos; al terminar imprime la
tabla final.

```
python -m parser.semantica parser/ejemplos_semanticos/E02_redeclarado.qc --tabla
```

```
Cambios de la tabla de simbolos
 1  registrar  limite: variable global grano (2:1) en ambito 0
 2  registrar  sumar: funcion (grano, grano) -> grano (4:1) en ambito 0
 3  entrar     Ambito 1 (nivel 1, dentro de 0)
 4    registrar  a: parametro grano (4:15) en ambito 1
 5    conflicto  a: parametro grano (4:24) ya declarado en 4:15 como parametro
 6    entrar     Ambito 2 (nivel 2, dentro de 1)
 7    salir      Ambito 2: (vacio)
 8  salir      Ambito 1: a
 9  entrar     Ambito 3 (nivel 1, dentro de 0)
10    registrar  x: variable local grano (9:5) en ambito 3
11    conflicto  x: variable local grano (10:5) ya declarado en 9:5 como variable local
12  salir      Ambito 3: x

Tabla de simbolos final
...
```

Los tipos se escriben al imprimir: por eso las funciones ya muestran el tipo
de retorno que calculo la inferencia. Si la verificacion semantica termina sin
errores, la salida cierra con el ASA decorado en preorden, incluyendo los
tipos inferidos y las referencias a las declaraciones. Sin `--tabla` se omite
el historial de cambios y la tabla final. El callback `al_cambiar` permite
consumir los eventos mientras se construye la tabla.

## Casos de test_ambitos.py

`test_ambitos.py` verifica que se rechacen parametros redeclarados, funciones
usadas como variables y asignaciones a nombres de funcion. El verificador
tambien exige que los nombres usados como lista o destino de asignacion
resuelvan a una variable.
