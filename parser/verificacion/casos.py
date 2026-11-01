# Casos de regresion conservados de la revision anterior.
VALIDOS = [
    "barista chorreador() {}",
    "barista f() { degustar; } barista chorreador() {f();}",
    "barista chorreador() {grano x=-5; poso y=+2.5; grano z=-(x+2);}",
    "barista chorreador() {cafe x=Amargo Amargo fuerte;}",
    (
        "barista chorreador() {granoMolido nombre=leer(); "
        "nombre=leer(); servir(nombre);}"
    ),
    (
        "barista chorreador() {taza grano a=[]; servir(a); "
        "a.insertar(2); cafe b=a.buscar(2); grano x=a.extraer(0);}"
    ),
    "barista chorreador() {chorreando(ralo) {} recolar(grano x en lista) {}}",
    "barista chorreador() {hierve(fuerte) {hierve(ralo) {}} enfria {}}",
    (
        "cafeteria grano x=1; barista f(grano a, poso b) "
        "{degustar a+b;} cafeteria poso y=2.0; "
        "barista chorreador() {poso z=f(x,y);}"
    ),
    "barista chorreador() {taza taza grano m=[[1,2],[]];}",
]
INVALIDOS = [
    "",
    "grano x=1;",
    "barista chorreador() {} }",
    "barista chorreador() {} barista chorreador() {}",
    "barista chorreador(grano x) {}",
    "barista chorreador() {} cafeteria grano x=1;",
    "barista chorreador() {grano x=;}",
    "barista chorreador() {grano x=1}",
    "barista chorreador() {fuerte x;}",
    "barista chorreador() {hierve(x=1) {}}",
    "barista chorreador() {hierve(a<b<c) {}}",
    "barista chorreador() {enfria {}}",
    "barista chorreador() {chorreando(fuerte) servir(1);}",
    "barista chorreador() {lista.extraer();}",
    "barista chorreador() {f(1,);}",
    "barista chorreador() {taza grano a=[1,];}",
    "barista chorreador() {grano x=2+;}",
]
