# Quantum Coffee

Compilador Quantum Coffee: parser / analizador sintactico y ASA.

Participantes:
- Abraham Solano Parrales
- Andres Baldi
- Justin Lacayo
- Miguel Dario Soto Badilla
- Tomas Blando

Scanner: `python scanner/main.py archivo.qc`

Parser y ASA: `python -m parser archivo.qc`

Tabla de simbolos y sus cambios: `python -m parser.semantica archivo.qc --tabla`
(detalle en `docs/Tabla_de_simbolos.md`)

Pruebas: `python -m unittest discover -s parser/verificacion -t . -v`

Estilo: `python -m ruff check parser scanner`
