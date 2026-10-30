# Uniendo tipos, funciones, booleanos, ciclos y condicionales complejos
barista auditarInventario(taza grano inventario) {
    grano total_granos = 0 ;
    cafe falta_cafe = ralo ;

    recolar (grano cantidad en inventario) {
        hierve (cantidad <= 5) {
            falta_cafe = fuerte ;
        }
        total_granos = total_granos + cantidad ;
    }

    hierve (falta_cafe == fuerte ConAzucar total_granos < 50) {
        servir("Alerta critica: Hay que tostar mas cafe urgente") ;
        degustar ralo ;
    } enfria {
        servir("Inventario de la cafeteria saludable") ;
        degustar fuerte ;
    }
}

barista chorreador() {
    taza grano bodega = [10, 4, 20, 15] ;
    cafe estado_tienda = auditarInventario(bodega) ;
}
