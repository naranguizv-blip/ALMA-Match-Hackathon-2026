from io import BytesIO
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
from backend.verification import verify_document_claims
from backend.comparison import compare


def sample_pdf():
    out = BytesIO()
    c = canvas.Canvas(out)
    c.drawString(50, 760, 'Plan CS50400826 Isapre Esencial')
    c.drawString(50, 730, 'Hospitalaria 80% en Clinica Central, con tope 400 UF anual')
    c.drawString(50, 710, 'Ambulatoria 70% en Clinica Central, con tope 60 UF anual')
    c.drawString(50, 690, 'Urgencia 60% en Clinica Central, tope 5 UF por evento')
    c.drawString(50, 670, 'Prestadores preferentes Clinica Central')
    c.showPage()
    c.save()
    return out.getvalue()


def extracted():
    def item(text): return [{'descripcion':text, 'pagina_pdf':1, 'evidencia':text}]
    return {'codigo_plan':'CS50400826','isapre':'Esencial',
        'hospitalaria':item('Hospitalaria 80% en Clinica Central, con tope 400 UF anual'),
        'ambulatoria':item('Ambulatoria 70% en Clinica Central, con tope 60 UF anual'),
        'urgencia':item('Urgencia 60% en Clinica Central, tope 5 UF por evento'),
        'clinicas_preferentes':item('Prestadores preferentes Clinica Central'),
        'topes':item('Urgencia 60% en Clinica Central, tope 5 UF por evento')}


def test_literal_citations_with_real_pdf_parser():
    result = verify_document_claims(extracted(), sample_pdf())
    assert result['aprobado_para_comparacion']
    assert result['citas_comprobadas']==5
    assert result['estado']=='citas_localizadas_pendiente_revision_semantica'


def test_fake_quote_fails_closed():
    e=extracted();e['hospitalaria'][0]['evidencia']='Hospitalaria 100% sin tope en Clinica Central'
    r=verify_document_claims(e,sample_pdf())
    assert not r['aprobado_para_comparacion']
    assert 'no aparece' in ' '.join(r['motivos'])


def test_missing_urgency_fails_closed():
    e=extracted();e['urgencia']=[]
    r=verify_document_claims(e,sample_pdf())
    assert not r['aprobado_para_comparacion']
    assert any('urgencia' in m for m in r['motivos'])


def test_wrong_page_fails_closed():
    e=extracted();e['topes'][0]['pagina_pdf']=2
    r=verify_document_claims(e,sample_pdf())
    assert not r['aprobado_para_comparacion']


def test_scanned_page_fails_closed_without_ocr():
    w=PdfWriter();w.add_blank_page(width=595,height=842); b=BytesIO();w.write(b)
    r=verify_document_claims(extracted(),b.getvalue())
    assert not r['aprobado_para_comparacion']


def test_corrupt_pdf_fails_closed():
    assert not verify_document_claims(extracted(),b'no-pdf')['aprobado_para_comparacion']


def test_invalid_page_type_fails_closed():
    e=extracted();e['hospitalaria'][0]['pagina_pdf']=True
    assert not verify_document_claims(e,sample_pdf())['aprobado_para_comparacion']


def test_catalogue_official_commercialization_does_not_certify_coverage():
    r=compare('Esencial',['Clínica Indisa'])
    assert r['alternativas']==[]
    assert r['estado']=='Sin alternativas documentales verificadas para mostrar.'


def test_validated_synthetic_candidate_can_appear_without_price():
    c={'codigo':'SIM-001','isapre':'Ficticia B','nombre':'Plan de prueba',
       'tipo_plan':'Individual','periodo_comercializacion':'202608',
       'comercializacion_verificada':True,'coberturas_verificadas':True,
       'topes_verificados':True,'revisado_para_comparacion':True,
       'modalidad':'Preferente','hospitalaria':'80% sin tope\nClínica Central',
       'ambulatoria':'70% sin tope\nClínica Central',
       'urgencia':'Copago variable, sujeto a condiciones','topes':'200 UF anual',
       'origen':'Caso sintético generado para pruebas'}
    r=compare('Ficticia A',['Clínica Central'],catalog=[c])
    assert len(r['alternativas'])==1
    assert r['alternativas'][0]['precio_final_uf'] is None


def test_noncommercial_candidate_rejected():
    c={'codigo':'SIM-001','isapre':'Ficticia B','nombre':'Plan de prueba',
       'tipo_plan':'Individual','periodo_comercializacion':'202608',
       'comercializacion_verificada':False,'coberturas_verificadas':True,
       'topes_verificados':True,'revisado_para_comparacion':True,
       'hospitalaria':'80% sin tope\nClínica Central',
       'ambulatoria':'70% sin tope\nClínica Central',
       'urgencia':'Urgencia variable','topes':'200 UF anual'}
    r=compare('Ficticia A',['Clínica Central'],catalog=[c])
    assert r['alternativas']==[]
