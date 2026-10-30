# Prueba 4: listas y estructuras de control
barista suma(grano a, grano b) {
    degustar a + b;
}

barista chorreador() {
    taza grano lista = [1, 2, 3];
    lista.insertar(4);
    lista.extraer(0);
    grano pos = lista.buscar(3);

    hierve (pos >= 0) {
        servir("encontrado");
    } enfria {
        servir("no esta");
    }

    grano i = 0;
    chorreando (i < 3) {
        i = i + 1;
    }

    recolar (grano n en lista) {
        servir(suma(n, 1));
    }

    grano dato = leer();
    degustar 0;
}
