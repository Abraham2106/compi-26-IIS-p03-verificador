# Quantum Coffee

Compilador Quantum Coffee: verificador

Participantes:
- Abraham Solano Parrales
- Andres Baldi
- Justin Lacayo
- Miguel Dario Soto Badilla
- Tomas Blando

Scanner: `python scanner/main.py archivo.qc`

Parser y ASA: `python -m parser archivo.qc`

Verificador, ASA decorado y tabla de simbolos:
`python -m parser.semantica archivo.qc --tabla`
(detalle en `docs/Tabla_de_simbolos.md`)

Pruebas: `python -m unittest discover -s parser/verificacion -t . -v`

Estilo: `python -m ruff check parser scanner`
