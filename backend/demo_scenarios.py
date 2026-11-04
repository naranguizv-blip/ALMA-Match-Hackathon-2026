"""Casos totalmente ficticios para demostrar el comparador; NUNCA oferta comercial.

No comparten catálogo con planes reales. No realizan llamadas a la API Meta.
Las referencias de comercialización son simuladas, solo para el circuito demo.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from .verification import verify_document_claims

CLINIC = "Clinica Davila Recoleta"
TEXT = (
    "Contrato ficticio ALMA Match: plan DEMO001 de Isapre Ficticia A",
    "Hospitalaria 80% Clinica Davila Recoleta tope 400 UF por beneficiario al ano",
    "Ambulatoria 70% Clinica Davila Recoleta tope 60 UF por beneficiario al ano",
    "Urgencia 60% Clinica Davila Recoleta tope 5 UF por evento",
    "Prestadores preferentes Clinica Davila Recoleta",
)
CURRENT = {
    'hospitalaria': {'porcentaje':80, 'tope_uf':400, 'periodo':'anual'},
    'ambulatoria': {'porcentaje':70, 'tope_uf':60, 'periodo':'anual'},
    'urgencia': {'porcentaje':60, 'tope_uf':5, 'periodo':'evento'},
}

def _pdf():
    out=BytesIO()
    c=canvas.Canvas(out,pagesize=(595,842))
    for index,line in enumerate(TEXT):
        c.drawString(38, 770-index*24,line)
    c.showPage()
    c.save()
    return out.getvalue()

def _claim(text):
    return [{'descripcion':text,'pagina_pdf':1,'evidencia':text}]

def _extraction():
    return {
        'codigo_plan':'DEMO001','isapre':'Ficticia A',
        'nombre_plan':'Plan de prueba A (totalmente ficticio)',
        'modalidad':'Red preferente de demostracion',
        'hospitalaria':_claim(TEXT[1]),
        'ambulatoria':_claim(TEXT[2]),
        'urgencia':_claim(TEXT[3]),
        'clinicas_preferentes':_claim(TEXT[4]),
        'topes':_claim(TEXT[3]),
        'observaciones':[{'descripcion':'Datos y entidades inventados; no son planes comercializados.',
                          'pagina_pdf':1,'evidencia':TEXT[0]}],
        'estado_verificacion':'simulacion_sintetica_documental',
        'precio_final':None,
    }

def _candidate(code, isapre, name, values, clinics=(CLINIC,)):
    return {'codigo':code,'isapre':isapre,'nombre':name,'red':clinics,
            'condiciones':values,'es_ficticio':True,
            'hospitalaria':f"{values['hospitalaria']['porcentaje']} % · tope {values['hospitalaria']['tope_uf']} UF {values['hospitalaria']['periodo']}",
            'ambulatoria':f"{values['ambulatoria']['porcentaje']} % · tope {values['ambulatoria']['tope_uf']} UF {values['ambulatoria']['periodo']}",
            'urgencia':f"{values['urgencia']['porcentaje']} % · tope {values['urgencia']['tope_uf']} UF por {values['urgencia']['periodo']}",
            'modalidad':'Red preferente ficticia','precio_final_uf':None,
            'precio_final_clp':None,'ahorro_verificado':False}

def _candidate_ok():
    return _candidate('DEMO002','Ficticia B','Plan de prueba B', {
        'hospitalaria':{'porcentaje':80,'tope_uf':450,'periodo':'anual'},
        'ambulatoria':{'porcentaje':70,'tope_uf':70,'periodo':'anual'},
        'urgencia':{'porcentaje':60,'tope_uf':6,'periodo':'evento'}})

def _candidate_wrong_limit():
    return _candidate('DEMO003','Ficticia C','Plan C: mismo porcentaje, peor tope', {
        'hospitalaria':{'porcentaje':80,'tope_uf':400,'periodo':'anual'},
        'ambulatoria':{'porcentaje':70,'tope_uf':60,'periodo':'anual'},
        'urgencia':{'porcentaje':60,'tope_uf':2,'periodo':'evento'}})

def _candidate_other_network():
    return _candidate('DEMO004','Ficticia D','Plan D: otra clinica', {
        'hospitalaria':{'porcentaje':90,'tope_uf':800,'periodo':'anual'},
        'ambulatoria':{'porcentaje':90,'tope_uf':90,'periodo':'anual'},
        'urgencia':{'porcentaje':80,'tope_uf':8,'periodo':'evento'}},clinics=('Clinica Davila Vespucio',))

def _candidate_same_isapre():
    return _candidate('DEMO005','Ficticia A','Plan E: misma isapre', {
        'hospitalaria':{'porcentaje':95,'tope_uf':900,'periodo':'anual'},
        'ambulatoria':{'porcentaje':95,'tope_uf':100,'periodo':'anual'},
        'urgencia':{'porcentaje':95,'tope_uf':9,'periodo':'evento'}})

def _comparison(scenario, verification):
    options = ([_candidate_ok(),_candidate_wrong_limit(),
                _candidate_other_network(),_candidate_same_isapre()]
               if scenario=='comparable'
               else [_candidate_wrong_limit(),_candidate_other_network(),_candidate_same_isapre()])
    valid=[]
    discarded=[]
    for item in options:
        issues=[]
        if item['isapre']=='Ficticia A':
            issues.append('misma isapre del contrato actual')
        if CLINIC not in item['red']:
            issues.append('clínica preferente distinta')
        for field in ('hospitalaria','ambulatoria','urgencia'):
            current=CURRENT[field]
            other=item['condiciones'][field]
            if current['periodo']!=other['periodo']:
                issues.append(f'{field}: periodo del tope diferente')
            elif other['tope_uf']<current['tope_uf']:
                issues.append(f'{field}: tope inferior')
            if other['porcentaje']<current['porcentaje']:
                issues.append(f'{field}: porcentaje inferior')
        if not verification['aprobado_para_comparacion']:
            issues.append('citas no verificadas')
        if issues:
            discarded.append({'codigo':item['codigo'],'nombre':item['nombre'],'motivos':issues})
        else:
            item['coincidencias']=[{'clinica':CLINIC,
                'hospitalaria':item['condiciones']['hospitalaria']['porcentaje'],
                'ambulatoria':item['condiciones']['ambulatoria']['porcentaje']}]
            item['hospitalaria_resumen']=item['hospitalaria']
            item['ambulatoria_resumen']=item['ambulatoria']
            item['fuente']='Condiciones totalmente ficticias del caso de prueba'
            item['estado']='Comparabilidad documental simulada, NO precio confirmado'
            valid.append(item)
    return {'alternativas':valid[:3],
        'rechazadas':discarded,
        'isapre_excluida':'Ficticia A',
        'catalogo_prueba':len(options),
        'estado':('Caso ficticio: alternativa compatible por porcentajes, red y topes de prueba.'
                  if valid else 'Caso ficticio: no existen alternativas comparables.'),
        'sin_precios':'Precios no disponibles, no se puede afirmar ahorro ni precio final.',
        'mensaje_ahorro':'Sin precios reales comprobados no se calcula ahorro.',
        'aviso':'Todos los nombres, planes, coberturas y valores son INVENTADOS para esta prueba.'}

def synthetic_case(scenario):
    if scenario not in ('comparable','no_comparable'):
        raise ValueError('Caso ficticio desconocido')
    verification=verify_document_claims(_extraction(),_pdf())
    comparison=_comparison(scenario,verification)
    comparison['topes_visuales'] = [
        {'tipo':'Hospitalaria','periodo':'anual','actual_uf':400,'alternativa_uf':450},
        {'tipo':'Ambulatoria','periodo':'anual','actual_uf':60,'alternativa_uf':70},
        {'tipo':'Urgencia','periodo':'evento','actual_uf':5,'alternativa_uf':6},
    ] if comparison['alternativas'] else []
    comparison['plan_actual'] = {'nombre':'Plan de prueba A','isapre':'Ficticia A','codigo':'DEMO001'}
    return {'resultado':_extraction(),'verificacion_documental':verification,
        'comparacion':comparison,'finanzas':{'pactado_uf':None,'pago_actual_clp':None,
                                            'cotizacion_legal_estimada':None},
        'demostracion_precargada':True,'demostracion_ficticia':True,
        'nota':'CASO 100% FICTICIO: sin Meta, sin datos personales, sin catálogo comercial ni cotización.'}
