"""Verifica la gramatica EBNF con los tokens reales del scanner."""
from pathlib import Path
from parser.integracion import explorar_para_parser
from parser.verificacion.ebnf import Gramatica
from parser.verificacion.casos import VALIDOS, INVALIDOS

ROOT = Path(__file__).resolve().parents[2]


def main():
    gramatica = Gramatica(ROOT / 'docs/Documentacion.md')
    print('Producciones sintacticas:', len(gramatica.reglas))
    print(
        "Referencias, alcance de producciones, terminales "
        "y recursion izquierda: OK"
    )
    print('Conflictos LL(1):', gramatica.conflictos)
    assert len(gramatica.conflictos) == 1, gramatica.conflictos
    assert gramatica.conflictos[0][0] == 'programa'
    assert gramatica.conflictos[0][4] == ['BARISTA']
    for path in sorted((ROOT / 'parser/ejemplos_completos').glob('*.qc')):
        entrada = explorar_para_parser(path.read_text(encoding='utf-8-sig'))
        assert entrada.apta and gramatica.acepta(entrada.tokens), path.name
        print('ACEPTADO:', path.name)
    for texto in VALIDOS:
        entrada = explorar_para_parser(texto)
        assert entrada.apta and gramatica.acepta(entrada.tokens), texto
    for texto in INVALIDOS:
        entrada = explorar_para_parser(texto)
        assert not entrada.apta or not gramatica.acepta(entrada.tokens), texto
    # Comprobar sintaxis sin agregar comprobaciones semanticas.
    for texto in [
        'hierve(5) {}',
        'grano x="texto";',
        'servir(); leer(1);',
            'desconocida(1, 2);']:
        entrada = explorar_para_parser('barista chorreador() {' + texto + '}')
        assert entrada.apta and gramatica.acepta(entrada.tokens), texto
    print(
        "8 programas, 10 validos, 17 invalidos "
        "y 4 casos fuera del analisis semantico: OK"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
