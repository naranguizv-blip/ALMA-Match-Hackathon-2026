"""Verificación independiente de evidencias antes de comparar contratos.

Validar una cita como texto extraído NO demuestra por sí solo que la
interpretación de la cobertura sea semánticamente correcta. Aquí se bloquea
todo caso sin página, sin cita o sin alguna categoría crítica.
"""
import re
import unicodedata
from io import BytesIO
from pypdf import PdfReader

CRITICAL = ('hospitalaria', 'ambulatoria', 'urgencia', 'topes', 'clinicas_preferentes')


def _clean(value):
    normalized = unicodedata.normalize('NFKD', str(value or ''))
    without_accents = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', without_accents).casefold().strip()


def verify_document_claims(extracted, document_pdf):
    """Comprueba citas literales contra texto del PDF y categorías completas.

    Para PDF escaneado o páginas no extraíbles bloquea (fail-closed), sin OCR
    automático ni segunda consulta de pago. No certifica equivalencia clínica.
    """
    if not isinstance(extracted, dict):
        return {'aprobado_para_comparacion': False, 'estado': 'revision_requerida',
                'motivos': ['La extracción no es un objeto válido'], 'citas_comprobadas': 0,
                'citas_rechazadas': 0, 'comprobacion': 'texto_literal_por_pagina'}
    try:
        reader = PdfReader(BytesIO(document_pdf), strict=False)
        page_texts = [_clean(page.extract_text() or '') for page in reader.pages]
    except Exception:
        return {'aprobado_para_comparacion': False, 'estado': 'revision_requerida',
                'motivos': ['PDF ilegible: no se pueden comprobar las citas'],
                'citas_comprobadas': 0, 'citas_rechazadas': 0,
                'comprobacion': 'texto_literal_por_pagina'}
    issues = []
    success = 0
    rejected = 0
    if not page_texts or not all(page_texts):
        issues.append('Hay páginas sin texto legible; requiere revisión visual')
    if not extracted.get('codigo_plan') or not extracted.get('isapre'):
        issues.append('No está identificado el código y la isapre del plan')
    for category in CRITICAL:
        items = extracted.get(category)
        if not isinstance(items, list) or not items:
            issues.append(f'Falta información crítica de {category}')
            continue
        for i, item in enumerate(items):
            prefix = f'{category}[{i}]'
            if not isinstance(item, dict):
                rejected += 1
                issues.append(f'{prefix}: estructura inválida')
                continue
            page = item.get('pagina_pdf')
            quote = item.get('evidencia')
            if not isinstance(page, int) or isinstance(page, bool) or page < 1 or page > len(page_texts):
                rejected += 1
                issues.append(f'{prefix}: página inválida o inexistente')
            elif not isinstance(quote, str) or len(_clean(quote)) < 12:
                rejected += 1
                issues.append(f'{prefix}: falta cita literal suficientemente precisa')
            elif _clean(quote) not in page_texts[page-1]:
                rejected += 1
                issues.append(f'{prefix}: la cita no aparece en la página indicada')
            elif not isinstance(item.get('descripcion'), str) or not item['descripcion'].strip():
                rejected += 1
                issues.append(f'{prefix}: descripción sin contenido')
            else:
                success += 1
    return {'aprobado_para_comparacion': not issues,
            'estado': 'citas_localizadas_pendiente_revision_semantica' if not issues else 'revision_requerida',
            'motivos': issues[:24], 'citas_comprobadas': success, 'citas_rechazadas': rejected,
            'paginas_pdf': len(page_texts), 'comprobacion': 'texto_literal_por_pagina',
            'advertencia': 'Coincidencia literal no certifica interpretación, precios ni equivalencia.'}
