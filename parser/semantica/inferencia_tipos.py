"""Inferencia y validacion de tipos del ASA de Quantum Coffee."""

from parser.integracion import ClaseNodo, NodoASA
from parser.semantica.visitante import VisitanteASA

C = ClaseNodo

TIPOS_LITERALES = {
    "ENTERO": "grano", "DECIMAL": "poso", "CADENA": "granoMolido",
    "FUERTE": "cafe", "RALO": "cafe", "DESCAFEINADO": "descafeinado",
    "SE_QUEMO_EL_CAFE": "SeQuemoElCafe",
}
NUMERICOS = {"grano", "poso"}
LOGICOS = {"ConAzucar", "SinAzucar"}
ORDEN = {"<", "<=", ">", ">="}
IGUALDAD = {"==", "!="}
ARITMETICOS = {"+", "-", "*", "/", "%"}


class InferidorTipos(VisitanteASA):
    def __init__(self):
        self.errores: list[str] = []
        self._funciones_analizadas: set[int] = set()
        self._funciones_en_proceso: set[int] = set()
        self._llamadas_recursivas: list[NodoASA] = []

    def _error(self, nodo: NodoASA, mensaje: str) -> None:
        p = nodo.rango.inicio
        self.errores.append(
            f"Linea {p.linea}, columna {p.columna}: {mensaje}")

    @staticmethod
    def _tipo(nodo: NodoASA | None) -> str | None:
        if nodo is None:
            return None
        return nodo.semantica.tipo_inferido or nodo.atributos.get("tipo")

    @staticmethod
    def _compatible(esperado: str, recibido: str) -> bool:
        return (esperado == recibido or
                (esperado == "poso" and recibido == "grano"))

    def _verificar_compatibilidad(self, nodo, esperado, expresion) -> None:
        recibido = self._tipo(expresion)
        if esperado is not None and recibido is not None:
            if not self._compatible(esperado, recibido):
                self._error(nodo, "no se puede asignar un valor de tipo "
                            f"{recibido} a una variable de tipo {esperado}")

    def inferir(self, arbol: NodoASA) -> list[str]:
        self.errores.clear()
        self._funciones_analizadas.clear()
        self._funciones_en_proceso.clear()
        self._llamadas_recursivas.clear()
        self.visitar(arbol)
        if not self.errores:
            reportadas = set()
            for llamada in self._llamadas_recursivas:
                definicion = llamada.semantica.definiciones.get("nombre")
                if definicion is None:
                    continue
                tipo = self._tipo(definicion)
                if tipo is not None:
                    llamada.semantica.tipo_inferido = tipo
                elif id(definicion) not in reportadas:
                    mensaje = "no se pudo inferir el tipo de retorno "
                    self._error(llamada, mensaje + "de la llamada recursiva "
                                f"a '{llamada.atributos['nombre']}'")
                    reportadas.add(id(definicion))
        return list(self.errores)

    def visitar_literal(self, nodo):
        nodo.semantica.tipo_inferido = TIPOS_LITERALES.get(
            nodo.atributos["categoria"])

    def visitar_parametro(self, nodo):
        nodo.semantica.tipo_inferido = nodo.atributos["tipo"]

    def visitar_qubit(self, nodo):
        nodo.semantica.tipo_inferido = "qubit"

    def visitar_local(self, nodo):
        tipo = nodo.atributos["tipo"]
        nodo.semantica.tipo_inferido = tipo
        if nodo.hijos:
            self._completar_listas_vacias(nodo.hijos[0], tipo)
            self.visitar_hijos(nodo)
            self._verificar_compatibilidad(nodo, tipo, nodo.hijos[0])

    visitar_global = visitar_local

    def visitar_identificador(self, nodo):
        nodo.semantica.tipo_inferido = self._tipo(
            nodo.semantica.definiciones.get("nombre"))

    def visitar_asignacion(self, nodo):
        definicion = nodo.semantica.definiciones.get("nombre")
        tipo = (definicion.atributos.get("tipo") or self._tipo(definicion)
                if definicion is not None else None)
        if tipo is not None:
            self._completar_listas_vacias(nodo.hijos[0], tipo)
        self.visitar_hijos(nodo)
        self._verificar_compatibilidad(nodo, tipo, nodo.hijos[0])

    def visitar_binaria(self, nodo):
        self.visitar_hijos(nodo)
        izq, der = map(self._tipo, nodo.hijos)
        op = nodo.atributos["operador"]
        if izq is None or der is None:
            return
        ambos_numeros = izq in NUMERICOS and der in NUMERICOS
        if op in LOGICOS | ORDEN | IGUALDAD:
            valido = ((op in LOGICOS and izq == der == "cafe")
                      or (op in ORDEN and ambos_numeros)
                      or (op in IGUALDAD and (ambos_numeros or
                          (izq == der and izq in {"granoMolido", "cafe"}))))
            if valido:
                nodo.semantica.tipo_inferido = "cafe"
            else:
                self._error(nodo, f"no se puede aplicar '{op}' "
                            f"a los tipos {izq} y {der}")
        elif op in ARITMETICOS:
            if op == "+" and izq == der == "granoMolido":
                nodo.semantica.tipo_inferido = "granoMolido"
            elif ambos_numeros:
                nodo.semantica.tipo_inferido = (
                    "poso" if op == "/" or "poso" in (izq, der) else "grano")
            else:
                self._error(nodo, f"no se puede aplicar '{op}' "
                            f"a los tipos {izq} y {der}")

    def visitar_unaria(self, nodo):
        self.visitar_hijos(nodo)
        tipo = self._tipo(nodo.hijos[0])
        op = nodo.atributos["operador"]
        if tipo is None:
            return
        if (op == "Amargo" and tipo == "cafe") or (
                op in {"+", "-"} and tipo in NUMERICOS):
            nodo.semantica.tipo_inferido = tipo
        else:
            self._error(nodo, f"no se puede aplicar '{op}' al tipo {tipo}")

    def visitar_lista(self, nodo):
        self.visitar_hijos(nodo)
        if not nodo.hijos:
            return
        tipos = [self._tipo(hijo) for hijo in nodo.hijos]
        if any(tipo is None for tipo in tipos):
            return
        resultado = tipos[0]
        for tipo in tipos[1:]:
            if tipo == resultado:
                continue
            if {resultado, tipo} <= NUMERICOS:
                resultado = "poso"
            else:
                self._error(nodo, "elementos de lista incompatibles: "
                            f"{resultado} y {tipo}")
                return
        nodo.semantica.tipo_inferido = f"taza {resultado}"

    def _completar_listas_vacias(self, nodo, esperado):
        if nodo.clase != C.LISTA:
            return
        if not nodo.hijos:
            if esperado.startswith("taza "):
                nodo.semantica.tipo_inferido = esperado
            else:
                self._error(nodo, "no se puede asignar una lista vacia "
                            f"a una variable de tipo {esperado}")
        elif esperado.startswith("taza "):
            for hijo in nodo.hijos:
                self._completar_listas_vacias(hijo, esperado[5:])

    def visitar_operacion_lista(self, nodo):
        metodo, receptor = nodo.atributos["metodo"], nodo.atributos["receptor"]
        definicion = nodo.semantica.definiciones.get("receptor")
        tipo_lista = None
        if definicion is not None:
            tipo_lista = (definicion.atributos.get("tipo") or
                          self._tipo(definicion))
        argumento = nodo.hijos[0]
        if tipo_lista and tipo_lista.startswith("taza "):
            if metodo in {"insertar", "buscar"}:
                self._completar_listas_vacias(argumento, tipo_lista[5:])
        self.visitar_hijos(nodo)
        if tipo_lista is None:
            return
        if not tipo_lista.startswith("taza "):
            self._error(nodo, f"'{receptor}' no es una lista "
                        f"(tipo {tipo_lista})")
            return
        elemento, recibido = tipo_lista[5:], self._tipo(argumento)
        if recibido is None:
            return
        if metodo == "extraer":
            if recibido == "grano":
                nodo.semantica.tipo_inferido = elemento
            else:
                self._error(nodo, "extraer requiere un indice de tipo grano, "
                            f"pero recibio {recibido}")
        elif metodo in {"insertar", "buscar"}:
            if not self._compatible(elemento, recibido):
                self._error(nodo, f"no se puede usar {recibido} en {metodo} "
                            f"de una lista de {elemento}")
            else:
                nodo.semantica.tipo_inferido = (
                    "cafe" if metodo == "buscar" else "sin_valor")

    def visitar_llamada(self, nodo):
        anteriores = len(self.errores)
        nombre = nodo.atributos["nombre"]
        funcion = nodo.semantica.definiciones.get("nombre")
        if funcion is not None and funcion.clase == C.FUNCION:
            identidad = id(funcion)
            if (identidad in self._funciones_en_proceso and
                    self._tipo(funcion) is None):
                self._llamadas_recursivas.append(nodo)
            elif (identidad not in self._funciones_en_proceso and
                  identidad not in self._funciones_analizadas):
                self.visitar(funcion)
            parametros = [h for h in funcion.hijos if h.clase == C.PARAMETRO]
            for argumento, parametro in zip(nodo.hijos, parametros):
                self._completar_listas_vacias(
                    argumento, parametro.atributos["tipo"])
        else:
            parametros = []
        if funcion is not None and len(self.errores) == anteriores:
            nodo.semantica.tipo_inferido = self._tipo(funcion)
        self.visitar_hijos(nodo)
        if funcion is None:
            if nombre == "leer":
                if nodo.hijos:
                    self._error(nodo, "leer no recibe argumentos")
                elif len(self.errores) == anteriores:
                    nodo.semantica.tipo_inferido = "granoMolido"
            elif nombre == "servir":
                if len(nodo.hijos) != 1:
                    self._error(nodo, "servir requiere exactamente "
                                "un argumento")
                elif self._tipo(nodo.hijos[0]) == "sin_valor":
                    self._error(nodo, "servir requiere un argumento "
                                "con valor")
                elif len(self.errores) == anteriores:
                    nodo.semantica.tipo_inferido = "sin_valor"
            return
        if funcion.clase != C.FUNCION:
            self._error(nodo, f"'{nombre}' no es una funcion")
        elif len(nodo.hijos) != len(parametros):
            self._error(nodo, f"la funcion '{nombre}' requiere "
                        f"{len(parametros)} argumento(s), "
                        f"pero recibio {len(nodo.hijos)}")
        else:
            for i, (argumento, parametro) in enumerate(
                    zip(nodo.hijos, parametros), 1):
                esperado = parametro.atributos["tipo"]
                recibido = self._tipo(argumento)
                if (recibido is not None and
                        not self._compatible(esperado, recibido)):
                    self._error(nodo, f"argumento {i} de '{nombre}': "
                                f"se esperaba {esperado}, "
                                f"pero se recibio {recibido}")

    def visitar_retorno(self, nodo):
        self.visitar_hijos(nodo)
        nodo.semantica.tipo_inferido = (
            self._tipo(nodo.hijos[0]) if nodo.hijos else "sin_valor")

    def _obtener_retornos(self, nodo):
        if nodo.clase == C.RETORNO:
            return [nodo]
        return [r for hijo in nodo.hijos for r in self._obtener_retornos(hijo)]

    def _depende_de_recursion_directa(self, expresion, funcion):
        if self._tipo(expresion) is not None:
            return True
        if expresion.clase == C.LLAMADA:
            return expresion.semantica.definiciones.get("nombre") is funcion
        if expresion.clase in (C.BINARIA, C.UNARIA):
            return all(self._depende_de_recursion_directa(h, funcion)
                       for h in expresion.hijos)
        return False

    def _resolver_recursion_directa(self, funcion, retornos):
        conocidos = [self._tipo(r) for r in retornos
                     if self._tipo(r) is not None]
        pendientes = [r for r in retornos if self._tipo(r) is None]
        if not conocidos or not pendientes:
            return
        if not all(r.hijos and self._depende_de_recursion_directa(
                r.hijos[0], funcion) for r in pendientes):
            return
        tipos = set(conocidos)
        if tipos <= NUMERICOS:
            base = "poso" if "poso" in tipos else "grano"
        elif len(tipos) == 1:
            base = conocidos[0]
        else:
            return
        funcion.semantica.tipo_inferido = base
        self.visitar_hijos(funcion)

    def visitar_funcion(self, nodo):
        identidad = id(nodo)
        if (identidad in self._funciones_analizadas or
                identidad in self._funciones_en_proceso):
            return
        self._funciones_en_proceso.add(identidad)
        try:
            anteriores = len(self.errores)
            self.visitar_hijos(nodo)
            retornos = self._obtener_retornos(nodo.hijos[-1])
            if not retornos:
                nodo.semantica.tipo_inferido = "sin_valor"
                return
            tipos = [self._tipo(r) for r in retornos]
            if (any(t is None for t in tipos)
                    and len(self.errores) == anteriores):
                self._resolver_recursion_directa(nodo, retornos)
                tipos = [self._tipo(r) for r in retornos]
            if any(t is None for t in tipos):
                nodo.semantica.tipo_inferido = None
                return
            resultado = tipos[0]
            for retorno, tipo in zip(retornos[1:], tipos[1:]):
                if tipo == resultado:
                    continue
                if {resultado, tipo} == NUMERICOS:
                    resultado = "poso"
                else:
                    self._error(retorno, "retornos incompatibles en la "
                                "funcion "
                                f"'{nodo.atributos['nombre']}': "
                                f"{resultado} y {tipo}")
                    return
            nodo.semantica.tipo_inferido = resultado
        finally:
            self._funciones_en_proceso.remove(identidad)
            self._funciones_analizadas.add(identidad)

    def _condicion(self, nodo, nombre):
        self.visitar_hijos(nodo)
        tipo = self._tipo(nodo.hijos[0])
        if tipo is not None and tipo != "cafe":
            self._error(nodo, f"{nombre} requiere una condicion de tipo cafe, "
                        f"pero recibio {tipo}")

    def visitar_condicional(self, nodo):
        self._condicion(nodo, "hierve")

    def visitar_mientras(self, nodo):
        self._condicion(nodo, "chorreando")

    def visitar_para_cada(self, nodo):
        variable = nodo.atributos["tipo"]
        nodo.semantica.tipo_inferido = variable
        lista = self._tipo(nodo.semantica.definiciones.get("lista"))
        if lista is not None:
            if not lista.startswith("taza "):
                self._error(nodo, "recolar requiere una lista, "
                            f"pero recibio {lista}")
            elif not self._compatible(variable, lista[5:]):
                self._error(nodo, "tipo incompatible en recolar: "
                            f"la lista contiene {lista[5:]}, "
                            f"pero la variable es {variable}")
        self.visitar_hijos(nodo)

    def visitar_compuerta(self, nodo):
        self.visitar_hijos(nodo)
        valido = True
        for operando in nodo.hijos:
            tipo = self._tipo(operando)
            if tipo is None:
                valido = False
            elif tipo != "qubit":
                self._error(operando, "la compuerta "
                            f"{nodo.atributos['compuerta']} requiere "
                            f"un qubit, pero recibio {tipo}")
                valido = False
        if valido:
            nodo.semantica.tipo_inferido = "sin_valor"

    def visitar_medicion(self, nodo):
        self.visitar_hijos(nodo)
        tipo = self._tipo(nodo.hijos[0])
        if tipo == "qubit":
            nodo.semantica.tipo_inferido = "cafe"
        elif tipo is not None:
            self._error(nodo, f"medir requiere un qubit, pero recibio {tipo}")
