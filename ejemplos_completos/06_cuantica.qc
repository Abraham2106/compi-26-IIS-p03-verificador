# Extension cuantica original dentro de un programa completo.
barista chorreador() {
    qubit q0;
    qubit q1;
    X(q0);
    H(q0);
    Z(q0);
    CNOT(q0, q1);
    cafe resultado = medir(q0);
    servir(resultado);
}
