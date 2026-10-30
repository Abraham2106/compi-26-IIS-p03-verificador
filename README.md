# Quantum Coffee

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
python scanner/main.py scanner/ejemplos/lista_control.qc
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