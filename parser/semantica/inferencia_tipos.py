
#Inferencia de tipos para los nodos del ASA.

from parser.integracion import ClaseNodo, NodoASA
from parser.semantica.visitante import VisitanteASA


TIPOS_LITERALES = {
    "ENTERO": "grano",
    "DECIMAL": "poso",
    "CADENA": "granoMolido",
    "FUERTE": "cafe",
    "RALO": "cafe",
    "DESCAFEINADO": "descafeinado",
    "SE_QUEMO_EL_CAFE": "SeQuemoElCafe",
}


class InferidorTipos(VisitanteASA):

    def __init__(self):
        self.errores: list[str] = []
        self._funciones_analizadas: set[int] = set()
        self._funciones_en_proceso: set[int] = set()
        self._llamadas_recursivas: list[NodoASA] = []



    def inferir(self, arbol: NodoASA) -> list[str]:
        self.errores.clear()
        self._funciones_analizadas.clear()
        self._funciones_en_proceso.clear()
        self._llamadas_recursivas.clear()

        self.visitar(arbol)
        if not self.errores:
            reportadas = set()

            for llamada in self._llamadas_recursivas:
                definicion = (
                    llamada.semantica.definiciones.get("nombre")
                )

                if definicion is None:
                    continue

                tipo = definicion.semantica.tipo_inferido

                if tipo is not None:
                    llamada.semantica.tipo_inferido = tipo
                    continue

                identidad = id(definicion)

                if identidad in reportadas:
                    continue

                posicion = llamada.rango.inicio
                nombre = llamada.atributos["nombre"]

                self.errores.append(
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                    "no se pudo inferir el tipo de retorno "
                    f"de la llamada recursiva a '{nombre}'"
                )

                reportadas.add(identidad)

        return list(self.errores)




    def _verificar_compatibilidad(
        self,
        nodo: NodoASA,
        tipo_esperado: str | None,
        expresion: NodoASA,
    ) -> None:
        tipo_recibido = expresion.semantica.tipo_inferido


        if tipo_esperado is None or tipo_recibido is None:
            return


        if tipo_esperado == tipo_recibido:
            return


        if tipo_esperado == "poso" and tipo_recibido == "grano":
            return

        posicion = nodo.rango.inicio
        self.errores.append(
            f"Linea {posicion.linea}, "
            f"columna {posicion.columna}: "
            f"no se puede asignar un valor de tipo "
            f"{tipo_recibido} a una variable "
            f"de tipo {tipo_esperado}"
        )



    def visitar_literal(self, nodo: NodoASA) -> None:
        categoria = nodo.atributos["categoria"]
        nodo.semantica.tipo_inferido = TIPOS_LITERALES.get(
            categoria
        )



    def visitar_global(self, nodo: NodoASA) -> None:
        tipo = nodo.atributos["tipo"]
        nodo.semantica.tipo_inferido = tipo

        if nodo.hijos:
            self._completar_listas_vacias(
                nodo.hijos[0],
                tipo,
            )

        self.visitar_hijos(nodo)

        if nodo.hijos:
            self._verificar_compatibilidad(
                nodo, tipo, nodo.hijos[0]
            )

    def visitar_local(self, nodo: NodoASA) -> None:
        tipo = nodo.atributos["tipo"]
        nodo.semantica.tipo_inferido = tipo

        if nodo.hijos:
            self._completar_listas_vacias(
                nodo.hijos[0],
                tipo,
            )

        self.visitar_hijos(nodo)

        if nodo.hijos:
            self._verificar_compatibilidad(
                nodo, tipo, nodo.hijos[0]
            )



    def visitar_parametro(self, nodo: NodoASA) -> None:
        nodo.semantica.tipo_inferido = nodo.atributos["tipo"]


    def visitar_para_cada(self, nodo: NodoASA) -> None:
        tipo_variable = nodo.atributos["tipo"]
        nodo.semantica.tipo_inferido = tipo_variable

        definicion = nodo.semantica.definiciones.get("lista")

        if definicion is not None:
            tipo_lista = definicion.semantica.tipo_inferido

            if tipo_lista is None:
                tipo_lista = definicion.atributos.get("tipo")

            if tipo_lista is not None:
                posicion = nodo.rango.inicio
                ubicacion = (
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                )

                if not tipo_lista.startswith("taza "):
                    self.errores.append(
                        ubicacion
                        + "recolar requiere una lista, "
                        + f"pero recibio {tipo_lista}"
                    )
                else:
                    tipo_elemento = tipo_lista.removeprefix("taza ")

                    compatible = (
                        tipo_variable == tipo_elemento
                        or (
                            tipo_variable == "poso"
                            and tipo_elemento == "grano"
                        )
                    )

                    if not compatible:
                        self.errores.append(
                            ubicacion
                            + "tipo incompatible en recolar: "
                            + f"la lista contiene {tipo_elemento}, "
                            + f"pero la variable es {tipo_variable}"
                        )

        self.visitar_hijos(nodo)


    def visitar_identificador(self, nodo: NodoASA) -> None:
        definicion = nodo.semantica.definiciones.get("nombre")

        if definicion is None:
            return

        tipo = definicion.semantica.tipo_inferido

        if tipo is None:
            tipo = definicion.atributos.get("tipo")

        nodo.semantica.tipo_inferido = tipo

    def visitar_binaria(self, nodo: NodoASA) -> None:


        self.visitar_hijos(nodo)

        izquierdo, derecho = nodo.hijos

        tipo_izquierdo = izquierdo.semantica.tipo_inferido
        tipo_derecho = derecho.semantica.tipo_inferido

        operador = nodo.atributos["operador"]


        operadores_aritmeticos = {"+", "-", "*", "/", "%"}
        operadores_orden = {"<", "<=", ">", ">="}
        operadores_igualdad = {"==", "!="}
        operadores_logicos = {"ConAzucar", "SinAzucar"}

        numericos = {"grano", "poso"}

        if operador in (
            operadores_orden
            | operadores_igualdad
            | operadores_logicos
        ):

            if tipo_izquierdo is None or tipo_derecho is None:
                return

            if operador in operadores_logicos:
                compatibles = (
                    tipo_izquierdo == "cafe"
                    and tipo_derecho == "cafe"
                )

            elif operador in operadores_orden:
                compatibles = (
                    tipo_izquierdo in numericos
                    and tipo_derecho in numericos
                )

            else:

                compatibles = (
                    (
                        tipo_izquierdo in numericos
                        and tipo_derecho in numericos
                    )
                    or (
                        tipo_izquierdo == tipo_derecho
                        and tipo_izquierdo in {"granoMolido", "cafe"}
                    )
                )

            if compatibles:
                nodo.semantica.tipo_inferido = "cafe"
            else:
                posicion = nodo.rango.inicio
                self.errores.append(
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                    f"no se puede aplicar '{operador}' "
                    f"a los tipos {tipo_izquierdo} "
                    f"y {tipo_derecho}"
                )

            return

        if operador not in operadores_aritmeticos:
            return



        if tipo_izquierdo is None or tipo_derecho is None:
            return


        if (
            operador == "+"
            and tipo_izquierdo == "granoMolido"
            and tipo_derecho == "granoMolido"
        ):
            nodo.semantica.tipo_inferido = "granoMolido"
            return

        tipos_numericos = {"grano", "poso"}

        if (
            tipo_izquierdo in tipos_numericos
            and tipo_derecho in tipos_numericos
        ):
            if operador == "/":
                nodo.semantica.tipo_inferido = "poso"
            elif "poso" in (tipo_izquierdo, tipo_derecho):
                nodo.semantica.tipo_inferido = "poso"
            else:
                nodo.semantica.tipo_inferido = "grano"

            return


        posicion = nodo.rango.inicio

        self.errores.append(
            f"Linea {posicion.linea}, "
            f"columna {posicion.columna}: "
            f"no se puede aplicar '{operador}' "
            f"a los tipos {tipo_izquierdo} y {tipo_derecho}"
        )

    def visitar_unaria(self, nodo: NodoASA) -> None:

        self.visitar_hijos(nodo)

        operando = nodo.hijos[0]
        tipo = operando.semantica.tipo_inferido
        operador = nodo.atributos["operador"]

        if tipo is None:
            return
        if operador == "Amargo" and tipo == "cafe":
            nodo.semantica.tipo_inferido = "cafe"
            return

        if operador in {"+", "-"} and tipo in {"grano", "poso"}:
            nodo.semantica.tipo_inferido = tipo
            return

        posicion = nodo.rango.inicio

        self.errores.append(
            f"Linea {posicion.linea}, "
            f"columna {posicion.columna}: "
            f"no se puede aplicar '{operador}' "
            f"al tipo {tipo}"
        )


    def visitar_asignacion(self, nodo: NodoASA) -> None:


        definicion = nodo.semantica.definiciones.get("nombre")

        tipo_esperado = None

        if definicion is not None:
            tipo_esperado = definicion.atributos.get("tipo")

            if tipo_esperado is None:
                tipo_esperado = definicion.semantica.tipo_inferido

        expresion = nodo.hijos[0]

        if tipo_esperado is not None:
            self._completar_listas_vacias(
                expresion,
                tipo_esperado,
            )

        self.visitar_hijos(nodo)

        self._verificar_compatibilidad(
            nodo,
            tipo_esperado,
            expresion,
        )


    def visitar_lista(self, nodo: NodoASA) -> None:



        self.visitar_hijos(nodo)


        if not nodo.hijos:
            return

        tipos = [
            hijo.semantica.tipo_inferido
            for hijo in nodo.hijos
        ]

        if any(tipo is None for tipo in tipos):
            return

        tipo_elemento = tipos[0]

        for tipo in tipos[1:]:

            if tipo == tipo_elemento:
                continue

            if {tipo_elemento, tipo} <= {"grano", "poso"}:
                tipo_elemento = "poso"
                continue
            posicion = nodo.rango.inicio

            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"elementos de lista incompatibles: "
                f"{tipo_elemento} y {tipo}"
            )
            return

        nodo.semantica.tipo_inferido = f"taza {tipo_elemento}"

    def _completar_listas_vacias(
        self,
        nodo: NodoASA,
        tipo_esperado: str,
    ) -> None:


        if nodo.clase != ClaseNodo.LISTA:
            return

        if not nodo.hijos:
            if tipo_esperado.startswith("taza "):
                nodo.semantica.tipo_inferido = tipo_esperado
            else:
                posicion = nodo.rango.inicio
                self.errores.append(
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                    f"no se puede asignar una lista vacia "
                    f"a una variable de tipo {tipo_esperado}"
                )
            return

        if tipo_esperado.startswith("taza "):
            tipo_elemento = tipo_esperado.removeprefix("taza ")

            for hijo in nodo.hijos:
                self._completar_listas_vacias(
                    hijo,
                    tipo_elemento,
                )

    def visitar_operacion_lista(self, nodo: NodoASA) -> None:

        metodo = nodo.atributos["metodo"]
        receptor = nodo.atributos["receptor"]
        definicion = nodo.semantica.definiciones.get("receptor")

        tipo_lista = None

        if definicion is not None:
            tipo_lista = definicion.atributos.get("tipo")

            if tipo_lista is None:
                tipo_lista = definicion.semantica.tipo_inferido

        argumento = nodo.hijos[0]
        if tipo_lista is not None and tipo_lista.startswith("taza "):
            tipo_elemento = tipo_lista.removeprefix("taza ")

            if metodo in {"insertar", "buscar"}:
                self._completar_listas_vacias(
                    argumento,
                    tipo_elemento,
                )

        self.visitar_hijos(nodo)

        if tipo_lista is None:
            return

        posicion = nodo.rango.inicio
        ubicacion = (
            f"Linea {posicion.linea}, "
            f"columna {posicion.columna}: "
        )

        if not tipo_lista.startswith("taza "):
            self.errores.append(
                ubicacion
                + f"'{receptor}' no es una lista "
                + f"(tipo {tipo_lista})"
            )
            return

        tipo_elemento = tipo_lista.removeprefix("taza ")
        tipo_argumento = argumento.semantica.tipo_inferido

        if tipo_argumento is None:
            return

        if metodo == "extraer":
            if tipo_argumento != "grano":
                self.errores.append(
                    ubicacion
                    + "extraer requiere un indice de tipo grano, "
                    + f"pero recibio {tipo_argumento}"
                )
                return

            nodo.semantica.tipo_inferido = tipo_elemento
            return

        if metodo in {"insertar", "buscar"}:
            compatible = (
                tipo_argumento == tipo_elemento
                or (
                    tipo_elemento == "poso"
                    and tipo_argumento == "grano"
                )
            )

            if not compatible:
                self.errores.append(
                    ubicacion
                    + f"no se puede usar {tipo_argumento} "
                    + f"en {metodo} de una lista "
                    + f"de {tipo_elemento}"
                )
                return

            if metodo == "buscar":
                nodo.semantica.tipo_inferido = "cafe"
            else:
                nodo.semantica.tipo_inferido = "sin_valor"


    def visitar_llamada(self, nodo: NodoASA) -> None:
        errores_previos = len(self.errores)
        nombre = nodo.atributos["nombre"]
        definicion = nodo.semantica.definiciones.get("nombre")
        if (
            definicion is not None
            and definicion.clase == ClaseNodo.FUNCION
            and id(definicion) in self._funciones_en_proceso
            and definicion.semantica.tipo_inferido is None
        ):
            self._llamadas_recursivas.append(nodo)
        if (
            definicion is not None
            and definicion.clase == ClaseNodo.FUNCION
            and id(definicion) not in self._funciones_analizadas
            and id(definicion) not in self._funciones_en_proceso
        ):
            self.visitar(definicion)

        parametros = []


        if definicion is not None:
            if definicion.clase == ClaseNodo.FUNCION:
                parametros = [
                    hijo
                    for hijo in definicion.hijos
                    if hijo.clase == ClaseNodo.PARAMETRO
                ]

                for argumento, parametro in zip(
                    nodo.hijos, parametros
                ):
                    self._completar_listas_vacias(
                        argumento,
                        parametro.atributos["tipo"],
                    )

        if (
            definicion is not None
            and len(self.errores) == errores_previos
        ):
            nodo.semantica.tipo_inferido = (
                definicion.semantica.tipo_inferido
            )


        self.visitar_hijos(nodo)



        if definicion is None:
            posicion = nodo.rango.inicio
            ubicacion = (
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
            )

            if nombre == "leer":
                if nodo.hijos:
                    self.errores.append(
                        ubicacion
                        + "leer no recibe argumentos"
                    )
                elif len(self.errores) == errores_previos:
                    nodo.semantica.tipo_inferido = "granoMolido"

            elif nombre == "servir":
                if len(nodo.hijos) != 1:
                    self.errores.append(
                        ubicacion
                        + "servir requiere exactamente un argumento"
                    )
                elif (
                    nodo.hijos[0].semantica.tipo_inferido
                    == "sin_valor"
                ):
                    self.errores.append(
                        ubicacion
                        + "servir requiere un argumento con valor"
                    )
                elif len(self.errores) == errores_previos:
                    nodo.semantica.tipo_inferido = "sin_valor"

            return


        posicion = nodo.rango.inicio
        ubicacion = (
            f"Linea {posicion.linea}, "
            f"columna {posicion.columna}: "
        )

        if definicion.clase != ClaseNodo.FUNCION:
            self.errores.append(
                ubicacion + f"'{nombre}' no es una funcion"
            )
            return

        if len(nodo.hijos) != len(parametros):
            self.errores.append(
                ubicacion
                + f"la funcion '{nombre}' requiere "
                + f"{len(parametros)} argumento(s), "
                + f"pero recibio {len(nodo.hijos)}"
            )
            return

        for indice, (argumento, parametro) in enumerate(
            zip(nodo.hijos, parametros),
            start=1,
        ):
            esperado = parametro.atributos["tipo"]
            recibido = argumento.semantica.tipo_inferido

            if recibido is None:
                continue

            compatible = (
                esperado == recibido
                or (
                    esperado == "poso"
                    and recibido == "grano"
                )
            )

            if not compatible:
                self.errores.append(
                    ubicacion
                    + f"argumento {indice} de '{nombre}': "
                    + f"se esperaba {esperado}, "
                    + f"pero se recibio {recibido}"
                )

    def visitar_retorno(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)

        if not nodo.hijos:
            nodo.semantica.tipo_inferido = "sin_valor"
        else:
            nodo.semantica.tipo_inferido = (
                nodo.hijos[0].semantica.tipo_inferido
            )

    def _obtener_retornos(self, nodo: NodoASA) -> list[NodoASA]:
        if nodo.clase == ClaseNodo.RETORNO:
            return [nodo]

        retornos = []

        for hijo in nodo.hijos:
            retornos.extend(self._obtener_retornos(hijo))

        return retornos


    def visitar_funcion(self, nodo: NodoASA) -> None:
        identidad = id(nodo)

        if identidad in self._funciones_analizadas:
            return

        if identidad in self._funciones_en_proceso:
            return

        self._funciones_en_proceso.add(identidad)

        try:
            errores_antes = len(self.errores)
            self.visitar_hijos(nodo)

            bloque = nodo.hijos[-1]
            retornos = self._obtener_retornos(bloque)

            if not retornos:
                nodo.semantica.tipo_inferido = "sin_valor"
                return


            tipos = [
                retorno.semantica.tipo_inferido
                for retorno in retornos
            ]

            if (
                any(tipo is None for tipo in tipos)
                and len(self.errores) == errores_antes
            ):
                self._resolver_recursion_directa(nodo, retornos)

                tipos = [
                    retorno.semantica.tipo_inferido
                    for retorno in retornos
                ]

            if any(tipo is None for tipo in tipos):
                nodo.semantica.tipo_inferido = None
                return


            tipo_resultado = tipos[0]

            for retorno, tipo in zip(
                retornos[1:], tipos[1:]
            ):
                if tipo == tipo_resultado:
                    continue

                if {tipo_resultado, tipo} == {"grano", "poso"}:
                    tipo_resultado = "poso"
                    continue

                posicion = retorno.rango.inicio
                self.errores.append(
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                    f"retornos incompatibles en la funcion "
                    f"'{nodo.atributos['nombre']}': "
                    f"{tipo_resultado} y {tipo}"
                )
                return

            nodo.semantica.tipo_inferido = tipo_resultado

        finally:
            self._funciones_en_proceso.remove(identidad)
            self._funciones_analizadas.add(identidad)


    def visitar_condicional(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)

        condicion = nodo.hijos[0]
        tipo = condicion.semantica.tipo_inferido

        if tipo is not None and tipo != "cafe":
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"hierve requiere una condicion de tipo cafe, "
                f"pero recibio {tipo}"
            )

    def visitar_mientras(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)

        condicion = nodo.hijos[0]
        tipo = condicion.semantica.tipo_inferido

        if tipo is not None and tipo != "cafe":
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"chorreando requiere una condicion de tipo cafe, "
                f"pero recibio {tipo}"
            )

    def visitar_qubit(self, nodo: NodoASA) -> None:
        nodo.semantica.tipo_inferido = "qubit"

    def visitar_compuerta(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)

        compuerta = nodo.atributos["compuerta"]
        valido = True

        for operando in nodo.hijos:
            tipo = operando.semantica.tipo_inferido

            if tipo is None:
                valido = False
                continue

            if tipo != "qubit":
                posicion = operando.rango.inicio
                self.errores.append(
                    f"Linea {posicion.linea}, "
                    f"columna {posicion.columna}: "
                    f"la compuerta {compuerta} requiere "
                    f"un qubit, pero recibio {tipo}"
                )
                valido = False

        if valido:
            nodo.semantica.tipo_inferido = "sin_valor"

    def visitar_medicion(self, nodo: NodoASA) -> None:
        self.visitar_hijos(nodo)

        operando = nodo.hijos[0]
        tipo = operando.semantica.tipo_inferido

        if tipo is None:
            return

        if tipo != "qubit":
            posicion = nodo.rango.inicio
            self.errores.append(
                f"Linea {posicion.linea}, "
                f"columna {posicion.columna}: "
                f"medir requiere un qubit, "
                f"pero recibio {tipo}"
            )
            return

        nodo.semantica.tipo_inferido = "cafe"

    def _depende_de_recursion_directa(
        self,
        expresion: NodoASA,
        funcion: NodoASA,
    ) -> bool:
        if expresion.semantica.tipo_inferido is not None:
            return True

        if expresion.clase == ClaseNodo.LLAMADA:
            definicion = expresion.semantica.definiciones.get("nombre")
            return definicion is funcion

        if expresion.clase in (ClaseNodo.BINARIA, ClaseNodo.UNARIA):
            return all(
                self._depende_de_recursion_directa(hijo, funcion)
                for hijo in expresion.hijos
            )

        return False

    def _resolver_recursion_directa(
        self,
        funcion: NodoASA,
        retornos: list[NodoASA],
    ) -> None:
        conocidos = [
            retorno.semantica.tipo_inferido
            for retorno in retornos
            if retorno.semantica.tipo_inferido is not None
        ]

        pendientes = [
            retorno
            for retorno in retornos
            if retorno.semantica.tipo_inferido is None
        ]

        if not conocidos or not pendientes:
            return

        if not all(
            retorno.hijos
            and self._depende_de_recursion_directa(
                retorno.hijos[0], funcion
            )
            for retorno in pendientes
        ):
            return
        tipos = set(conocidos)

        if tipos <= {"grano", "poso"}:
            tipo_base = "poso" if "poso" in tipos else "grano"
        elif len(tipos) == 1:
            tipo_base = conocidos[0]
        else:
            return
        funcion.semantica.tipo_inferido = tipo_base
        self.visitar_hijos(funcion)
