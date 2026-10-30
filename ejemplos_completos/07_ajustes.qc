# Globales, negativos, llamadas, negacion repetida y ciclos anidados.
cafeteria grano limite = 2;

barista negativo(grano valor) {
    degustar -valor;
}

barista saludar(granoMolido nombre) {
    servir("Hola " + nombre);
    degustar;
}

barista chorreador() {
    grano deuda = -5;
    poso ajuste = -2.5;
    grano resultado = -(2 + 3) * -2;
    grano diferencia = 10 - 3 - 2;
    granoMolido nombre = leer();
    saludar(nombre);
    taza grano datos = [];
    servir(datos);
    datos.insertar(negativo(deuda));
    cafe existe = datos.buscar(5);
    hierve (Amargo Amargo existe) {
        grano i = 0;
        chorreando (i < limite) {
            recolar (grano dato en datos) {
                servir(dato);
            }
            i = i + 1;
        }
    } enfria {
        servir("No encontrado");
    }
    grano primero = datos.extraer(0);
    servir(primero);
    degustar 0;
}
