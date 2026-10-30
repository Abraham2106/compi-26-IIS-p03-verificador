# Quantum Coffee

Repositorio organizado por tema en tres carpetas principales:

- `scanner/`: analizador lexico, CLI, ejemplos lexicos y salidas esperadas.
- `parser/`: integracion scanner-parser-ASA, verificacion y programas completos.
- `docs/`: EBNF, analisis y decisiones de gramatica, interfaz ASA, antecedentes y resultados.

## Estado del proyecto

El scanner y el contrato tecnico de integracion estan implementados. La gramatica cuenta con una herramienta de verificacion y casos de referencia. Este repositorio aun no contiene un parser de produccion, analisis semantico ni generacion de codigo.

La EBNF esta en [`docs/EBNF.md`](docs/EBNF.md), que es la fuente que consume el verificador. El documento ODT que permanece dentro de `scanner/` es la entrega historica del Proyecto 2.

## Ejecutar

Requiere Python 3.9 o posterior. Desde la raiz del repositorio:

```bash
python scanner/main.py ruta/al/archivo.qc
```

Para revisar la gramatica y la interfaz:

```bash
python -m parser.verificacion.verificar_gramatica
python -m unittest parser.verificacion.test_integracion -v
python scanner/main.py parser/ejemplos_completos/07_ajustes.qc
```

Los ejemplos lexicos estan en `scanner/ejemplos/`. Los programas completos de referencia estan en `parser/ejemplos_completos/`.
