"""Comparación documentaria de muestra, SIN precios, rankings comerciales ni recomendación definitiva."""
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
UF_REFERENCE_CLP = 41252.94  # Referencia de demostración, 01/11/2026; NO usar para cotizaciones reales
UF_REFERENCE_DATE = '2026-11-01'


def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value or '').casefold())
                   if not unicodedata.combining(c)).strip()


def parse_groups(text):
    """Índice determinista: % de la cabecera corresponde solo a las líneas siguientes.

    No inferir clínicas, establecimientos o porcentajes que no figuren literalmente.
    """
    percent = None
    index = {}
    for raw in str(text or '').splitlines():
        line = raw.strip()
        if not line:
            continue
        header = re.fullmatch(r'(\d{1,3})\s*%\s*(?:sin tope)?', line, flags=re.I)
        if header:
            percent = int(header.group(1))
            if not 0 <= percent <= 100:
                percent = None
            continue
        if re.match(r'^\d{1,3}\s*%', line):
            percent = None  # Condición compleja; no asumir porcentaje general.
            continue
        if re.match(r'^(cobertura|otras|fuera|urgencia)', norm(line)):
            percent = None
            continue
        if percent is not None and ('clinica' in norm(line) or 'centro' in norm(line) or 'hospital' in norm(line) or 'integramedica' in norm(line) or 'vidaintegra' in norm(line) or 'meds' == norm(line)):
            # Condición por prestación entre paréntesis debe seguir visible en el detalle.
            clean = re.sub(r'\s*\(.*$', '', line).strip()
            if clean:
                index[norm(clean)] = {'clinica': clean, 'porcentaje':percent, 'texto_original':line}
    return index


def compare(current_isapre, requested_clinics, goal='ambas', actual_payment=None,
            document_isapre=None, catalog=None):
    if catalog is None:
        catalog = json.loads((HERE / 'catalogo_demo.json').read_text(encoding='utf-8'))
    current = norm(current_isapre)
    if not current:
        return {'alternativas':[], 'error':'Indica tu isapre actual para excluirla de las alternativas.'}
    if document_isapre and norm(document_isapre).replace('isapre ','') != current.replace('isapre ',''):
        return {'alternativas':[], 'error':'La isapre del PDF no coincide con la seleccionada. Confirma la isapre actual antes de comparar.'}
    clinics = [str(x).strip() for x in requested_clinics if str(x).strip()][:10]
    if not clinics:
        return {'alternativas':[], 'error':'Indica al menos una clínica para identificar redes comparables.'}
    options = []
    for candidate in catalog:
        if norm(candidate['isapre']) == current:
            continue
        # Figurar en catálogo oficial no implica coberturas y topes comprobados.
        if not (candidate.get('comercializacion_verificada') is True
                and candidate.get('coberturas_verificadas') is True
                and candidate.get('topes_verificados') is True
                and candidate.get('revisado_para_comparacion') is True):
            continue
        if candidate.get('tipo_plan') != 'Individual' or not candidate.get('periodo_comercializacion'):
            continue
        if not all(str(candidate.get(k) or '').strip() for k in
                   ('hospitalaria','ambulatoria','urgencia','topes')):
            continue
        h = parse_groups(candidate['hospitalaria'])
        a = parse_groups(candidate['ambulatoria'])
        matches = []
        for clinic in clinics:
            k=norm(clinic)
            if k in h or k in a:
                matches.append({'clinica':clinic,
                                'hospitalaria':h.get(k,{}).get('porcentaje'),
                                'ambulatoria':a.get(k,{}).get('porcentaje'),
                                'nota':'Los porcentajes corresponden a los extractos de cobertura y requieren validación de topes y condiciones.'})
        if not matches:
            continue
        weight = sum((3 if m['hospitalaria'] is not None else 0)+(2 if m['ambulatoria'] is not None else 0)
                     for m in matches)
        options.append({
            'codigo':candidate['codigo'],'isapre':candidate['isapre'],
            'nombre':candidate['nombre'],'modalidad':candidate['modalidad'],
            'coincidencias': matches,'urgencia':candidate['urgencia'],
            'hospitalaria_resumen':candidate['hospitalaria'],
            'ambulatoria_resumen':candidate['ambulatoria'],
            'precio_final_uf':None,'precio_final_clp':None,'ahorro_verificado':False,
            'estado':'Coberturas extraídas, pendientes de validación contractual',
            'fuente':candidate['origen'],'_peso':weight})
    options.sort(key=lambda x:(-x['_peso'],x['codigo']))
    for option in options:
        option.pop('_peso',None)
    result = {'alternativas':options[:3],
        'sin_precios':'No se calcularon precios finales ni ahorros. Faltan precio base, factores, GES, vigencias y UF aplicables.',
        'mensaje_ahorro':'Sin precios finales verificados no se puede asegurar que una alternativa cueste menos de lo que pagas.' if goal in ('ahorro','ambas') else None,
        'isapre_excluida':current_isapre,
        'catalogo_prueba':len(catalog),
        'estado':('Comparación documental preliminar, no cotización ni equivalencia acreditada.' if options else 'Sin alternativas documentales verificadas para mostrar.'),
        'candidatos_rechazados_por_verificacion': len(catalog)-len([x for x in catalog if norm(x.get('isapre'))==current]) - len(options)}
    return result


def legal_7_estimate(renta_imponible):
    if renta_imponible is None:
        return None
    try:
        n=float(renta_imponible)
    except (TypeError,ValueError):
        return None
    if n <= 0 or n > 100_000_000:
        return None
    return {'monto_clp_estimado':round(min(n*.07,6.3*UF_REFERENCE_CLP)),
            'valor_uf_referencia':UF_REFERENCE_CLP,
            'fecha_uf_referencia':UF_REFERENCE_DATE,
            'nota':'Estimación general del 7 % de la renta imponible con tope de 90 UF. No reemplaza liquidación o cotización efectiva.'}
