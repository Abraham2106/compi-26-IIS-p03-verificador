# Prueba 5: extension cuantica
qubit q0;
qubit q1;
H(q0);
X(q1);
Z(q0);
CNOT(q0, q1);
cafe resultado = medir(q0);
medir(q1);