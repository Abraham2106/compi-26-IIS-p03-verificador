# Uso de repeticion (chorreando) y bifurcacion (hierve/enfria)
barista chorreador() {
    grano temperatura = 20 ;
    
    chorreando (temperatura < 90) {
        temperatura = temperatura + 10 ;
    }
    
    hierve (temperatura >= 90) {
        servir("Agua al punto ideal para chorrear") ;
    } enfria {
        servir("Falta fuego, el agua esta fria") ;
    }
}
