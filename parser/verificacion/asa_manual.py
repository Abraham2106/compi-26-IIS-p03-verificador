from parser.integracion import ClaseNodo as C, NodoASA, Posicion, RangoFuente


def n(clase, l1, c1, l2, c2, atributos=None, *hijos):
    return NodoASA(clase, RangoFuente(Posicion(l1, c1), Posicion(l2, c2)),
                   atributos or {}, hijos)


def ident(l, c1, c2, nombre):
    return n(C.IDENTIFICADOR, l, c1, l, c2, {"nombre": nombre})


def lit(l, c1, c2, categoria, lexema):
    return n(C.LITERAL, l, c1, l, c2, {"categoria": categoria, "lexema": lexema})


def asa_manual() -> NodoASA:
    return n(C.PROGRAMA, 1, 1, 17, 2, {},
        n(C.GLOBAL, 1, 1, 1, 30, {"nombre": "limite", "tipo": "grano"},
            lit(1, 26, 28, "ENTERO", "90")),
        n(C.FUNCION, 3, 1, 5, 2, {"nombre": "sumar"},
            n(C.PARAMETRO, 3, 15, 3, 22, {"nombre": "a", "tipo": "grano"}),
            n(C.PARAMETRO, 3, 24, 3, 31, {"nombre": "b", "tipo": "grano"}),
            n(C.BLOQUE, 3, 33, 5, 2, {},
                n(C.RETORNO, 4, 5, 4, 21, {},
                    n(C.BINARIA, 4, 14, 4, 19, {"operador": "+"},
                        ident(4, 14, 15, "a"),
                        ident(4, 18, 19, "b"))))),
        n(C.PRINCIPAL, 7, 1, 17, 2, {"nombre": "chorreador"},
            n(C.BLOQUE, 7, 22, 17, 2, {},
                n(C.LOCAL, 8, 5, 8, 19, {"nombre": "t", "tipo": "grano"},
                    lit(8, 15, 17, "ENTERO", "20")),
                n(C.MIENTRAS, 9, 5, 11, 6, {},
                    n(C.BINARIA, 9, 17, 9, 27, {"operador": "<"},
                        ident(9, 17, 18, "t"),
                        ident(9, 21, 27, "limite")),
                    n(C.BLOQUE, 9, 29, 11, 6, {},
                        n(C.ASIGNACION, 10, 9, 10, 21, {"nombre": "t"},
                            n(C.BINARIA, 10, 13, 10, 19, {"operador": "+"},
                                ident(10, 13, 14, "t"),
                                lit(10, 17, 19, "ENTERO", "10"))))),
                n(C.CONDICIONAL, 12, 5, 16, 6, {},
                    n(C.BINARIA, 12, 13, 12, 24, {"operador": ">="},
                        ident(12, 13, 14, "t"),
                        ident(12, 18, 24, "limite")),
                    n(C.BLOQUE, 12, 26, 14, 6, {},
                        n(C.LLAMADA, 13, 9, 13, 26, {"nombre": "servir"},
                            lit(13, 16, 23, "CADENA", '"listo"'))),
                    n(C.BLOQUE, 14, 14, 16, 6, {},
                        n(C.ASIGNACION, 15, 9, 15, 27, {"nombre": "t"},
                            n(C.LLAMADA, 15, 13, 15, 25, {"nombre": "sumar"},
                                ident(15, 19, 20, "t"),
                                n(C.UNARIA, 15, 22, 15, 24, {"operador": "-"},
                                    lit(15, 23, 24, "ENTERO", "1"))))))))
    )
