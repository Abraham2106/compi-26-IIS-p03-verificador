# Manejo de arreglos e invocacion de metodos nativos
barista chorreador() {
    taza granoMolido menu = ["Espresso", "Americano"] ;
    
    menu.insertar("Latte") ;
    cafe hay_latte = menu.buscar("Latte") ;
    granoMolido servido = menu.extraer(0) ;
    
    servir("Bebida servida al cliente:") ;
    servir(servido) ;
    
    servir("Restante en el menu:") ;
    recolar (granoMolido bebida en menu) {
        servir(bebida) ;
    }
}
