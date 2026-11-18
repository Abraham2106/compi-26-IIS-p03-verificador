# Comandos a probar: puntos 1.3.4

Responsable: Justin Lacayo  
Todos los comandos se ejecutan desde la raiz del proyecto.  
En Windows PowerShell, usar `echo $LASTEXITCODE` en lugar de `echo $?`.

## 1.3.4 Reportar errores semanticos

| # | Comando | Resultado esperado |
| --- | --- | --- |
| 1 | `python -m unittest parser.verificacion.test_errores_semanticos -v` | 12 pruebas, `OK` |
| 2 | `python -m parser.semantica parser/ejemplos_semanticos/E01_no_declarado.qc` | 2 errores (4:21 y 5:5) con linea de codigo y `^`; resumen `2 errores semanticos` |
| 3 | `python -m parser.semantica parser/ejemplos_completos/07_ajustes.qc` | `verificacion semantica correcta` |
| 4 | `python -m parser.semantica parser/ejemplos_semanticos/E10_varios_errores.qc` | 5 errores ordenados por linea: 2, 5, 10, 11, 13 |

Prueba propia: un archivo con `grano x = "hola" ;` y `y = 1 ;` dentro de
`barista chorreador() { ... }` debe dar 2 errores (tipo e identificador).

Constantes en `parser/semantica/errores_semanticos.py`:
`MOSTRAR_FRAGMENTO = False` quita la linea de codigo y el `^`;
`LIMITE_ERRORES = 1` muestra solo el primer error. Restaurar a `True` y `None`.

## 1.5.2 Probar ambitos y niveles
 
| # | Comando | Resultado esperado |
| --- | --- | --- |
| 1 | `python -m unittest parser.verificacion.test_ambitos -v` | 39 pruebas, `OK (expected failures=3)` |
| 2 | `python -m parser.semantica parser/ejemplos_semanticos/E03_fuera_de_ambito.qc` | `'interna'` (7:5) y `'d'` (11:12) no declarados |
| 3 | `python -m parser.semantica parser/ejemplos_semanticos/E02_redeclarado.qc` | `'a'` (4:24) y `'x'` (10:5) ya declarados |
 
Las 3 pruebas `x` son huecos conocidos (funcion como valor, asignar a una
funcion, parametro redeclarado).