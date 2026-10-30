import re

PATRON_IDENTIFICADOR = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
PATRON_ENTERO = re.compile(r"[0-9]+")
PATRON_DECIMAL = re.compile(r"[0-9]+\.[0-9]+")
PATRON_CADENA = re.compile(r'"[^"\n]*"')
PATRON_COMENTARIO = re.compile(r"#[^\n]*")
