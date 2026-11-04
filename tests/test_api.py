import json
from io import BytesIO
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from backend.main import app
from backend.meta_client import decode_json

client=TestClient(app)

def test_health():
    assert client.get('/health').json()['status']=='ok'

def test_demo_end_to_end():
    res=client.post('/api/demo',data={'isapre_actual':'Esencial','clinicas':json.dumps(['Clínica Dávila','Clínica Indisa']),'renta_imponible':'1500000','objetivo':'ahorro','pactado_uf':'6.8'})
    assert res.status_code==200
    j=res.json()
    assert j['resultado']['codigo_plan']=='CS50400826'
    assert j['finanzas']['cotizacion_legal_estimada']['monto_clp_estimado']==105000
    assert j['comparacion']['alternativas']==[]
    assert j['verificacion_documental']['aprobado_para_comparacion'] is False

def test_demo_mismatch_is_blocked():
    r=client.post('/api/demo',data={'isapre_actual':'Banmédica','clinicas':json.dumps(['Clínica Indisa'])})
    assert r.status_code==200 and not r.json()['comparacion']['alternativas']

def test_file_validation():
    r=client.post('/api/analizar',data={'isapre_actual':'Esencial','clinicas':'[]'},files={'pdf':('a.txt',b'bad','text/plain')})
    assert r.status_code==400

def test_real_pdf_with_mock_meta(monkeypatch):
    from backend import main
    monkeypatch.setattr(main,'analyze_pdf',lambda _:json.loads((main.HERE/'extraccion_demo.json').read_text()))
    writer=PdfWriter();writer.add_blank_page(width=595,height=842)
    buf=BytesIO();writer.write(buf)
    response=client.post('/api/analizar',data={'isapre_actual':'Esencial','clinicas':json.dumps(['Clínica Dávila'])},files={'pdf':('contrato.pdf',buf.getvalue(),'application/pdf')})
    assert response.status_code==200
    assert not response.json()['demostracion_precargada']
    assert response.json()['comparacion']['alternativas']==[]
    assert response.json()['verificacion_documental']['aprobado_para_comparacion'] is False
    assert response.json()['paginas_pdf']==1

def test_ai_verification_never_assumed():
    keys=['isapre','codigo_plan','nombre_plan','modalidad','hospitalaria','ambulatoria','urgencia','clinicas_preferentes','topes','observaciones']
    obj={k:([] if k in keys[4:] else None) for k in keys}
    assert decode_json(json.dumps(obj))['estado_verificacion']=='extraido_por_IA_pendiente_revision'
