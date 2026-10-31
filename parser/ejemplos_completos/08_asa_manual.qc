cafeteria grano limite = 90 ;

barista sumar(grano a, grano b) {
    degustar a + b ;
}

barista chorreador() {
    grano t = 20 ;
    chorreando (t < limite) {
        t = t + 10 ;
    }
    hierve (t >= limite) {
        servir("listo") ;
    } enfria {
        t = sumar(t, -1) ;
    }
}
