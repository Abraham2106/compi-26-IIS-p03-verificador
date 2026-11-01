# Pruebas:

1. python -m unittest parser.verificacion.test_asa_impresion parser.verificacion.test_asa_manual -v

2. python -c "from parser.asa_impresion import imprimir_preorden; from parser.verificacion.asa_manual import asa_manual; imprimir_preorden(asa_manual())"