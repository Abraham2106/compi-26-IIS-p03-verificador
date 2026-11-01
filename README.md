# Quantum Coffee

Repositorio organizado por tema en tres carpetas principales:

- `scanner/`: analizador lexico, CLI, ejemplos lexicos y salidas esperadas.
- `parser/`: integracion scanner-parser-ASA, verificacion y programas completos.
- `docs/`: documentacion consolidada, ejemplo JSON del ASA y resultados de verificacion.

## Estado del proyecto

El scanner y el contrato tecnico de integracion estan implementados. La gramatica cuenta con una herramienta de verificacion y casos de referencia. El parser descendente integra expresiones, declaraciones, control y construcciones cuanticas; genera el ASA y reporta errores sintacticos. No incluye analisis semantico ni generacion de codigo.

La documentacion, incluida la EBNF que consume el verificador, esta en [`docs/Documentacion.md`](docs/Documentacion.md). El documento ODT que permanece dentro de `scanner/` es la entrega historica del Proyecto 2.

## Ejecutar

Requiere Python 3.10 o posterior. Desde la raiz del repositorio:

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

Para analizar un programa e imprimir el ASA en preorden:

```bash
python -m parser parser/ejemplos_completos/08_asa_manual.qc
python -m unittest discover -s parser/verificacion -t . -v
```

El parser requiere Python 3.10 o posterior.
