# Demostracion del verificador semantico (1.6.3)

Proyecto: Quantum Coffee 
Responsable: Justin Lacayo (errores semanticos y pruebas)

## Antes de empezar

Desde la raiz del proyecto:

```bash
python -m unittest discover -s parser/verificacion -t .
```

Debe terminar con `OK (expected failures=3)` (102 pruebas). Si falla, no
hacer la demo hasta revisar.

## Pasos

| # | Que mostrar | Comando | Que decir |
| --- | --- | --- | --- |
| 1 | Programa correcto | `python -m parser.semantica parser/ejemplos_completos/07_ajustes.qc` | Globales, funciones, listas y ciclos anidados pasan las dos fases. |
| 2 | Identificador no declarado | `python -m parser.semantica parser/ejemplos_semanticos/E01_no_declarado.qc` | Variable y funcion inexistentes; el error apunta a linea, columna y codigo. |
| 3 | Ambitos | `python -m parser.semantica parser/ejemplos_semanticos/E03_fuera_de_ambito.qc` | Una variable muere con su bloque; la del `recolar` muere con el ciclo. |
| 4 | Repetidos | `python -m parser.semantica parser/ejemplos_semanticos/E02_redeclarado.qc` | Mismo nombre en el mismo ambito, incluidos parametros. |
| 5 | Tipos | `python -m parser.semantica parser/ejemplos_semanticos/E04_tipo_asignacion.qc` | Asignaciones incompatibles; `grano` si cabe en `poso`, al reves no. |
| 6 | Llamadas | `python -m parser.semantica parser/ejemplos_semanticos/E06_llamadas.qc` | Cantidad y tipo de argumentos, `leer` y `servir`. |
| 7 | Varios errores | `python -m parser.semantica parser/ejemplos_semanticos/E10_varios_errores.qc` | Errores de las dos fases, unidos y ordenados por posicion, sin duplicados. |
| 8 | Pruebas | `python -m unittest parser.verificacion.test_ambitos -v` | 39 pruebas de ambitos y niveles de anidamiento. |

Tambien estan: `E05` (operadores), `E07` (condiciones), `E08` (listas) y
`E09` (cuantica).

### Salida esperada del paso 2

```
parser/ejemplos_semanticos/E01_no_declarado.qc:4:21: error semantico: identificador 'extra' no declarado
        total = total + extra ;
                        ^
parser/ejemplos_semanticos/E01_no_declarado.qc:5:5: error semantico: identificador 'calcular' no declarado
        calcular(total) ;
        ^
2 errores semanticos
```

El codigo de salida es 1 cuando hay errores y 0 cuando el programa es
correcto. La salida completa de los 18 ejemplos esta en
`docs/Evidencia/semantica_ejemplos.txt`.

## Como se conecta todo

1. `parser/analizador.py` produce el ASA (errores sintacticos se detienen aqui).
2. `VerificadorIdentificadores` recorre el ASA con la tabla de ambitos y enlaza
   cada uso con su declaracion.
3. `InferidorTipos` calcula el tipo de cada nodo y valida compatibilidades.
4. `errores_semanticos.py` une los errores de 2 y 3, los ordena y los imprime.

Codigo: `parser/semantica/analisis.py` (`verificar_semantica`) y
`parser/semantica/__main__.py` (linea de comandos).

## Pendientes de integracion

- Por el momento se usa `TablaAmbitos` (`parser/semantica/analisis.py`), que cumple el
  mismo contrato que la tabla de simbolos. Al integrar la real, cambiar
  `FABRICA_TABLA` y repetir `test_ambitos.py`.