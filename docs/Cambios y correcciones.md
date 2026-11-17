# Ajustes 1.1.1 y 1.1.2

## 1.1.1 Gramatica

Las funciones y chorreador empiezan con barista. Esto causaba un conflicto
LL(1) en la EBNF. Se separo ese prefijo usando continuacion_barista.

El parser ya distingue ambos casos con el siguiente token, asi que no hubo
que cambiarlo. Se mantiene la misma sintaxis: globales y funciones antes de
una unica principal al final. El chequeo ahora exige cero conflictos.

## 1.1.2 ASA

Se agrego semantica a cada NodoASA, con dos campos:

- tipo_inferido: empieza en None; el verificador colocara el tipo.
- definiciones: diccionario vacio para enlazar usos con sus declaraciones.

Cada nodo tiene sus propios datos. Se pueden completar sin modificar los
atributos ni los hijos del arbol.

Para usar las referencias, estas son las claves acordadas en este ajuste:

| Nodo | Clave | Referencia |
| --- | --- | --- |
| Identificador o Asignacion | nombre | Declaracion de la variable |
| Llamada | nombre | Declaracion de la funcion |
| OperacionLista | receptor | Declaracion de la lista |
| ParaCada | lista | Declaracion de la lista recorrida |

ParaCada tambien sirve como declaracion de su variable de ciclo. Los
parametros, globales, locales y qubits ya tienen sus propios nodos.

Las referencias no son hijos: pueden apuntar hacia atras y formar ciclos.
Por eso a_dict y la impresion actual siguen mostrando solo la sintaxis.
Los constructores y desde_dict crean datos semanticos vacios; se usan antes
del chequeo, no para copiar un arbol decorado.

La inferencia, los enlaces y la impresion decorada quedan para los siguientes
puntos. Las funciones siguen sin tipo de retorno escrito; su tratamiento se
resolvera al implementar la inferencia.

## Instalacion y pruebas

Copiar docs y parser sobre las carpetas del proyecto y reemplazar los
archivos correspondientes. Este ZIP contiene solo los cambios.

Desde la raiz:

```bash
python -m parser.verificacion.verificar_gramatica
python -m unittest discover -s parser/verificacion -t . -v
```

Resultado comprobado: 24 pruebas pasan y cero conflictos LL(1).
Ruff no se pudo ejecutar porque no estaba instalado.
