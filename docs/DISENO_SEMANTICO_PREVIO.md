# Antecedente fuera del alcance de la etapa 3

Este texto procede de la revision anterior. No es criterio de aceptacion del
parser ni del ASA y no se implementa en esta entrega. La presente tarea no
confirma ni amplía estas decisiones semanticas; su revision corresponde a una
etapa posterior.

## 8. Ambiente estandar y reglas de coherencia

Las firmas siguientes documentan el ambiente; no son producciones especiales.

| Operacion | Contrato |
| --- | --- |
| `servir(valor)` | Imprime un valor; si es una lista, imprime sus elementos en orden, entre corchetes. No devuelve un valor util. |
| `leer()` | Lee una linea y devuelve `granoMolido`. |
| `lista.insertar(valor)` | Agrega al final un valor del tipo de la lista. No devuelve un valor util. |
| `lista.extraer(indice)` | Elimina y devuelve el elemento en el indice entero, contado desde cero. |
| `lista.buscar(valor)` | Devuelve `fuerte` si existe el valor, o `ralo` si no existe. |

Estas comprobaciones corresponden al analisis semantico o a la ejecucion, no
se intentan expresar mediante mas producciones:

- Las condiciones y los operadores logicos requieren `cafe`; `fuerte` es
  verdadero y `ralo` es falso. `medir` devuelve `cafe`.
- `+` suma numeros o concatena dos textos. Los otros operadores aritmeticos
  requieren numeros y `%` requiere enteros. Se permite promocion de `grano`
  a `poso`, no conversion automatica de texto a numero.
- `leer()` no produce enteros directamente. Una conversion de texto a numero
  necesita una funcion de biblioteca definida para ese fin; no se inventa una
  conversion implicita que el proyecto no ha especificado.
- No se puede usar el resultado de `servir` o `insertar` como un valor.
- Cada bloque crea un alcance. Las globales pertenecen al programa; los
  parametros pertenecen a su funcion. La variable de `recolar` es local al ciclo.
  Se rechazan declaraciones duplicadas en el mismo alcance y lecturas de
  variables sin inicializar. Una asignacion busca el nombre desde el alcance
  mas cercano hacia el global.
- Las listas son homogeneas, incluso cuando se anidan. `recolar` requiere una
  lista cuyo tipo de elemento corresponda al tipo declarado para la variable.
  No se permite insertar o extraer elementos de la lista recorrida durante
  `recolar`, ni directamente ni a traves de otra referencia.
- Las funciones conservan su firma original, sin tipo de retorno escrito.
  El analizador debe inferir y comprobar un tipo de retorno consistente antes
  de validar las llamadas, considerando conjuntamente las funciones recursivas.
  Una funcion que devuelve valores debe devolverlos en todos sus caminos de
  terminacion normal. No se mezclan retornos con valor y sin valor.
  Una funcion sin valor termina con `degustar;` o al llegar al final del bloque.
- Para mantener los ejemplos del scanner, `chorreador` puede terminar sin
  retorno, con `degustar;` o con un estado `grano`, como `degustar 0;`.
- `descafeinado` y `SeQuemoElCafe` son valores especiales comprobables con
  `==` y `!=`. Se pueden almacenar como estados excepcionales de una variable;
  no son operandos aritmeticos, condiciones booleanas ni listas utilizables.
- Se rechazan indices negativos o fuera de rango y operaciones numericas
  invalidas. Los argumentos cuanticos deben ser qubits declarados; `CNOT`
  requiere dos qubits distintos.
- Los nombres globales de variables y funciones no se duplican. `servir` y
  `leer` se enlazan con la biblioteca y se protegen de redeclaraciones mediante
  la tabla de simbolos, sin convertirlos en palabras reservadas.

Estos contratos son especificacion para las siguientes etapas; el scanner
actual solo reconoce tokens y errores lexicos. No ejecuta estos comportamientos.

