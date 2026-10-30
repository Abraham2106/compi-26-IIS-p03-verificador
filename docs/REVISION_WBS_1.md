# Entrega de la tarea 1: gramatica e interfaz del scanner

## Objetivo y limite

Verificar que la gramatica y los tokens de Quantum Coffee permitan construir
el parser y representar el ASA reutilizando el explorador anterior. El alcance
es la etapa 3 de la imagen: sin analisis semantico ni generacion de codigo.
No se recibio aqui otra especificacion de la etapa 3 que imponga un algoritmo
de parser o una biblioteca concreta para representar el arbol.

## Evidencia por actividad

| WBS | Trabajo entregado | Estado |
| --- | --- | --- |
| 1.1 Revisar producciones | 40 producciones sintacticas: referencias, accesibilidad, consumo en repeticiones, recursion izquierda, terminales, FIRST/FOLLOW y casos validos/invalidos. | Verificado. |
| 1.2 Modificar solo si es necesario | No se agrego ni cambio sintaxis respecto del ZIP corregido anterior. Se delimito la documentacion para que la semantica no sea obligacion del parser. Se documenta la decision BARISTA + siguiente token. | Cumplido tecnicamente; no necesita otra ampliacion del lenguaje. |
| 1.3 Tokens, valores y posiciones | Campos reales y lexemas sin convertir; pruebas de todos los terminales, cadenas, signos, posiciones, LF/CRLF/CR, BOM, EOF y errores; imports y CLI compatibles. | Verificado y corregido donde fallaba. |
| 1.4 Interfaz con parser y ASA | Paquete integracion, protocolo del parser, tipos de resultado/error, esquema de nodos, ejemplo JSON y guia de conexion. | Contrato tecnico listo. Su acuerdo con las personas responsables sigue pendiente. |

## Problemas encontrados y solucion

1. **El scanner no se podia importar limpiamente como paquete.** Sus imports
   absolutos buscaban modulos sueltos. Ahora tiene `scanner/__init__.py` e
   imports relativos, conservando `python scanner/main.py archivo.qc`.
2. **Faltaba un EOF compartido.** Se agrego FIN_ARCHIVO al final del enum y
   se emite solo en el adaptador. No se altera la forma anterior de escanear.
3. **Las posiciones con CR eran incorrectas y los comentarios podian comerse
   la linea siguiente.** Se corrigio el conteo de CR y CRLF y el fin de
   comentario en ambos caracteres. LF y CRLF conservan sus posiciones.
4. **El reconocedor de pruebas anterior comparaba terminales por lexema.**
   Eso no demostraba la correspondencia exacta con TokenType. El nuevo
   reconocedor usa los tipos reales, detecta errores de escritura de EBNF y
   comprueba que todos sus terminales tienen token.
5. **No habia contrato para valores y posiciones del ASA.** Ahora se conservan
   los lexemas, se definen rangos y nodos, y se incluye un JSON de referencia.
6. **La especificacion mezclaba sintaxis con decisiones semanticas futuras.**
   Se sacaron esos requisitos de la referencia activa de esta tarea y se
   archivaron como antecedente no vinculante para el parser.

## Resultado de la gramatica

- Sin producciones sintacticas sin definir o inalcanzables.
- Sin recursion directa o indirecta por la izquierda.
- Ningun cuerpo de repeticion puede reconocer una entrada vacia.
- Correspondencia completa entre terminales y tokens existentes.
- Un unico conflicto predictivo LL(1), en `programa`, por BARISTA.
  Se resuelve mirando CHORREADOR o IDENTIFICADOR como siguiente token.
  No es una afirmacion de LL(1) estricto ni una demostracion general de
  ausencia de ambiguedad; la decision concreta esta especificada y probada.
- Los siete programas completos de la entrega anterior siguen reconocidos.
- Las restricciones de tipos, nombres, aridad de funciones normales y retornos
  NO se usan para rechazar sintaxis. La extension cuantica sigue reconocida.

Los FIRST/FOLLOW y el catalogo de tokens estan en `ANALISIS_GRAMATICA.md`.

## Como repetir la revision

Desde la raiz del proyecto, con Python 3.9 o posterior y sin instalar paquetes:

```bash
python verificacion/verificar_gramatica.py
python -m unittest verificacion.test_integracion -v
```

Las salidas de la ultima ejecucion estan en `verificacion/RESULTADOS.txt`.
El reconocimiento de pruebas no es el parser del proyecto, y el JSON es un
ejemplo de contrato construido expresamente, no un ASA extraido por ese parser.
No se afirma que ya se ejecuto una integracion con los componentes de los
companeros, porque esos componentes no estan en los archivos disponibles.

## Criterio de finalizacion

La base tecnica queda lista: existe una gramatica de referencia y una entrada
de tokens que usa el mismo explorador, sin sustituirlo. Hay pruebas y contrato
para que las tareas 2.0, 3.0, 4.0 y 5.0 partan del mismo formato.

Para cerrar literalmente el punto 1.4 hace falta que las personas responsables
del parser y del ASA confirmen el contrato. Esta entrega deja todo preparado
para esa coordinacion, pero no inventa su aprobacion ni envia mensajes al equipo.

## Archivos de inicio para cada responsable

- Parser: `gramatica/EBNF.md`, `docs/ANALISIS_GRAMATICA.md`,
  `integracion/entrada.py` y `integracion/contratos.py`.
- ASA/representacion: `docs/INTERFAZ_PARSER_ASA.md`,
  `integracion/contratos.py` y `docs/asa_referencia.json`.
- Integracion y pruebas: `verificacion/test_integracion.py` y los siete
  archivos de `ejemplos_completos/`.
