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

Pruebas: `python -m unittest discover -s parser/verificacion -t . -v`

Estilo: `python -m ruff check parser scanner`
