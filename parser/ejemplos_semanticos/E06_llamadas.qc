# Llamadas con cantidad o tipo de argumentos incorrecto.
barista doble(grano n) {
    degustar n * 2 ;
}

barista chorreador() {
    grano a = doble() ;
    grano b = doble("tres") ;
    grano c = doble(1, 2) ;
    leer(5) ;
    servir() ;
}
