# Verificador semántico de Quantum Coffee

Compilador Quantum Coffee: verificador. Proyecto 4 del curso Compiladores e
Intérpretes. Integra el scanner y el parser
del lenguaje Quantum Coffee con un verificador semántico que recorre el ASA de
arriba hacia abajo mediante el patrón Visitante.

El verificador administra ámbitos y una tabla de símbolos, valida identificadores
y tipos, infiere tipos de retorno, y decora el ASA con referencias a las
declaraciones. La salida del verificador imprime el ASA decorado en preorden.

## Requisitos

- Python 3.10 o posterior.
- Ruff para ejecutar el análisis de estilo.

Ejecuta los comandos desde la raíz del repositorio. El proyecto no requiere
dependencias externas para correr el verificador.

## Uso

Verificar un programa `.qc`:

```bash
python -m parser.semantica parser/ejemplos_completos/07_ajustes.qc
```

Verificarlo e imprimir los cambios parciales y la tabla final de símbolos:

```bash
python -m parser.semantica parser/ejemplos_completos/07_ajustes.qc --tabla
```

El comando termina con código `0` si el programa pasa la verificación y con
`1` si encuentra errores léxicos, sintácticos o semánticos. Los diagnósticos
indican archivo, línea, columna y el fragmento de código cuando corresponde.

Para ejecutar solo el scanner o el parser:

```bash
python scanner/main.py parser/ejemplos_completos/07_ajustes.qc
python -m parser parser/ejemplos_completos/07_ajustes.qc
```

## Desarrollo y validación

Ejecutar las pruebas:

```bash
python -m unittest discover -s parser/verificacion -t . -v
```

Revisar el estilo:

```bash
python -m ruff check parser scanner
```

## Estructura

- `scanner/`: análisis léxico.
- `parser/`: análisis sintáctico, integración del ASA y ejemplos `.qc`.
- `parser/semantica/`: tabla de símbolos, verificación de identificadores,
  inferencia de tipos, diagnósticos e interfaz de línea de comandos.
- `parser/verificacion/`: pruebas automatizadas.
- `docs/Tabla_de_simbolos.md`: diseño e impresión de la tabla de símbolos.
- `docs/Errores_y_pruebas/Demostracion.md`: guía para demostrar el verificador.

## Equipo

- Abraham Solano Parrales
- Andrés Baldi
- Justin Lacayo
- Miguel Darío Soto Badilla
- Tomás Blando
