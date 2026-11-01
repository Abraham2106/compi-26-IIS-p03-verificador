"""Ejecuta los casos de 6.2 y 6.3 y conserva evidencia reproducible."""
import json
import platform
from pathlib import Path

from parser.analizador import Analizador
from parser.asa_esquema import validar_arbol
from parser.integracion import explorar_para_parser

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / 'parser/pruebas_6_2_6_3'


def ejecutar():
    resultados = []
    for caso in json.loads((BASE / 'casos.json').read_text('utf-8')):
        ruta = BASE / caso['grupo'] / (caso['id'] + '.qc')
        entrada = explorar_para_parser(ruta.read_text('utf-8'))
        resultado = None
        problemas = []
        if not entrada.apta:
            problemas.append('El caso contiene errores lexicos.')
        else:
            resultado = Analizador().analizar(entrada.tokens_para_parser())
            if resultado.correcto != caso['aceptar']:
                problemas.append('Aceptacion distinta de la esperada.')
            if caso['aceptar']:
                problemas.extend(validar_arbol(resultado.arbol)
                                 if resultado.arbol else ['No hay ASA.'])
            elif not resultado.errores:
                problemas.append('No se reportaron errores sintacticos.')
            if any(e.encontrado.linea < 1 or e.encontrado.columna < 1
                   or not e.mensaje for e in resultado.errores):
                problemas.append('Diagnostico sin mensaje o posicion valida.')
            if caso.get('token_error') and (not resultado.errores or
                    resultado.errores[0].encontrado.tipo.name
                    != caso['token_error']):
                problemas.append('Primer token de error distinto al esperado.')
            if caso['id'] == 'I25':
                if len(resultado.errores) != 2:
                    problemas.append('Se esperaban dos errores.')
                bloque = resultado.arbol.hijos[-1].hijos[0]
                if not any(n.atributos.get('nombre') == 'c'
                           for n in bloque.hijos):
                    problemas.append('No se conservo la sentencia posterior.')
        resultados.append({**caso, 'archivo': str(ruta.relative_to(RAIZ)),
                           'correcto_obtenido': resultado.correcto
                           if resultado else None,
                           'errores_lexicos': [str(e) for e in entrada.errores_lexicos],
                           'diagnosticos': [e.mensaje for e in resultado.errores]
                           if resultado else [],
                           'problemas': problemas, 'pasa': not problemas})
    return resultados


def main():
    resultados = ejecutar()
    destino = RAIZ / 'docs/evidencia_6_2_6_3'
    destino.mkdir(exist_ok=True)
    (destino / 'resultados.json').write_text(
        json.dumps({'python': platform.python_version(),
                    'resultados': resultados}, ensure_ascii=False, indent=2)
        + '\n', encoding='utf-8')
    lineas = ['Pruebas 6.2 y 6.3', 'Python ' + platform.python_version()]
    for r in resultados:
        lineas.append(f"{'PASA' if r['pasa'] else 'FALLA'} {r['id']}: "
                      f"{r['objetivo']} | aceptar={r['aceptar']} | "
                      f"correcto={r['correcto_obtenido']}")
        lineas.extend('  ' + d for d in r['diagnosticos'] + r['problemas'])
    fallos = sum(not r['pasa'] for r in resultados)
    lineas.append(f'Total: {len(resultados)}; fallos: {fallos}')
    texto = '\n'.join(lineas) + '\n'
    (destino / 'ejecucion.txt').write_text(texto, encoding='utf-8')
    print(texto, end='')
    return bool(fallos)


if __name__ == '__main__':
    raise SystemExit(main())
