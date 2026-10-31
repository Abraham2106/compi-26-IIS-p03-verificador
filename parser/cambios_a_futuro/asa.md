# Pruebas:

1. python -m unittest parser.verificacion.test_asa_impresion parser.verificacion.test_asa_manual -v

2. python -c "from parser.asa_impresion import imprimir_preorden; from parser.verificacion.asa_manual import asa_manual; imprimir_preorden(asa_manual())"

# Cuando exista el parser:

Se debe ajustar MODULO_PARSER y CLASE_PARSER en test_asa_manual.py, se debe correr la prueba 1, y no debe salir salteada la comprobacion con el parser

Por lo que el punto 6.4 esta a medias