# Quantum Coffee

## Entrega de la tarea 1 de la etapa 3

Leer primero [docs/REVISION_WBS_1.md](docs/REVISION_WBS_1.md).
La interfaz para los responsables del parser y del ASA esta en
[docs/INTERFAZ_PARSER_ASA.md](docs/INTERFAZ_PARSER_ASA.md).
La gramatica de esta revision conserva las producciones del ZIP corregido;
no amplia la sintaxis para esta tarea. El contrato tecnico queda listo y
probado; su acuerdo entre los responsables del equipo sigue pendiente.

```bash
python verificacion/verificar_gramatica.py
python -m unittest verificacion.test_integracion -v
```

Se reutiliza `Scanner`; `integracion.explorar_para_parser` conserva sus tokens
y errores y agrega un FIN_ARCHIVO. El scanner sigue funcionando por terminal
y ahora tambien por imports de paquete. Las comprobaciones se limitan a
sintaxis e interfaz, sin analisis semantico ni generacion de codigo.

## Gramatica vigente

La especificacion actual esta en [gramatica/EBNF.md](gramatica/EBNF.md).
Los cambios de la revision anterior estan en [AJUSTES_GRAMATICA.md](AJUSTES_GRAMATICA.md).
Para el alcance actual prevalece `docs/REVISION_WBS_1.md`; las decisiones
semanticas anteriores no son requisitos de la etapa 3.
`servir` y `leer` se reconocen como `IDENTIFICADOR`: son llamadas normales
del ambiente estandar. Su escritura en los programas no cambia.

La documentacion ODT del scanner se conserva como entrega historica del
Proyecto 2. Sus tablas de `SERVIR`/`LEER`, conteos y el apartado que afirma
que no hubo cambios en la gramatica quedan sustituidos por este ajuste.

Para comprobar la gramatica y los programas completos:

```bash
python verificacion/verificar_gramatica.py
python scanner/main.py ejemplos_completos/07_ajustes.qc
```

El verificador es una herramienta de comprobacion de la EBNF. El proyecto
sigue en la etapa de scanner: no incluye un parser de produccion, un
analizador semantico ni un interprete.

## Cómo correrlo

Requiere Python 3.9 o posterior. Desde la raíz del repositorio:

```bash
python scanner/main.py ruta/al/archivo.qc
```

El archivo debe tener extensión `.qc` y estar en UTF-8. Si tu sistema usa `python3`, reemplazá `python` por `python3`.

## Cómo probarlo

Ejecutá los ejemplos incluidos:

```bash
python scanner/main.py scanner/bom.qc
python scanner/main.py scanner/prueba.qc
python scanner/main.py scanner/ejemplos/tipos_variables.qc
python scanner/main.py scanner/ejemplos/numeros_operadores.qc
python scanner/main.py scanner/ejemplos/cadenas_comentarios.qc
python scanner/main.py scanner/ejemplos/cuantica.qc
python scanner/main.py scanner/ejemplos/listas_control.qc
```

Resultados esperados:

- `bom.qc`: imprime los tokens de `grano x = 1;`, sin errores.
- `prueba.qc`: reporta el símbolo desconocido `@` y una cadena sin cerrar.
- `tipos_variables.qc`: compará la salida con `scanner/ejemplos/tipos_variables.esperado.txt`. Reporta `_` como símbolo desconocido porque los identificadores deben comenzar con una letra.

Los dos últimos ejemplos contienen errores intencionales.

Códigos de salida:

- `0`: sin errores léxicos.
- `1`: con errores léxicos.
- `2`: problema de uso o lectura del archivo.
