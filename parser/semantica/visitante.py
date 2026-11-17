
#Recorrido descendente del ASA mediante el patron Visitor.

from parser.integracion import NodoASA


class VisitanteASA:


    def visitar(self, nodo: NodoASA):

        nombre_metodo = f"visitar_{nodo.clase.name.lower()}"
        metodo = getattr(self, nombre_metodo, self.visitar_generico)
        return metodo(nodo)

    def visitar_generico(self, nodo: NodoASA):

        self.visitar_hijos(nodo)

    def visitar_hijos(self, nodo: NodoASA):

        for hijo in nodo.hijos:
            self.visitar(hijo)
