"""Pruebas sin consumo de Meta para la experiencia del jurado."""
import io
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend import main
from backend.demo_scenarios import _pdf, _extraction
from backend.judge_demo import candidate_review_options

c=TestClient(app)

def test_judge_demo_fails_closed_when_not_enabled(monkeypatch):
    monkeypatch.delenv('META_DEMO_ALLOWED',raising=False)
    monkeypatch.delenv('MODEL_API_KEY',raising=False)
    r=c.post('/api/comparar-pdf-jurado',
        data={'isapre_actual':'Ficticia A','clinicas':'["Clínica Dávila"]'},
        files={'pdf':('ejemplo.pdf',_pdf(),'application/pdf')})
    assert r.status_code==503
    assert not c.get('/api/estado-jurado').json()['meta_disponible']

def test_judge_demo_with_meta_mock_and_synthetic_pdf(monkeypatch):
    monkeypatch.setenv('META_DEMO_ALLOWED','1')
    monkeypatch.setenv('MODEL_API_KEY','DEMO_NO_ES_UNA_CLAVE')
    monkeypatch.setenv('META_DEMO_MAX_CALLS','8')
    monkeypatch.setattr(main,'_demo_calls',0)
    monkeypatch.setattr(main,'analyze_pdf',lambda raw:_extraction())
    r=c.post('/api/comparar-pdf-jurado',
        data={'isapre_actual':'Ficticia A','clinicas':'["Clínica Dávila"]','pago_actual_uf':'7,5'},
        files={'pdf':('ejemplo.pdf',_pdf(),'application/pdf')})
    assert r.status_code==200, r.text
    j=r.json()
    assert j['modo']=='analisis_meta_real'
    assert j['verificacion_documental']['aprobado_para_comparacion']
    assert j['verificacion_documental']['citas_comprobadas']==5
    assert len(j['opciones_para_revisar'])==3
    assert all(x['isapre']!='Ficticia A' for x in j['opciones_para_revisar'])
    assert not j['ahorro_verificado']
    assert all(not x['precio_aplicable_cliente'] for x in j['opciones_para_revisar'])

def test_pdf_judge_rejects_invalid_type_without_api(monkeypatch):
    monkeypatch.setenv('META_DEMO_ALLOWED','1')
    monkeypatch.setenv('MODEL_API_KEY','MOCK')
    monkeypatch.setattr(main,'_demo_calls',0)
    r=c.post('/api/comparar-pdf-jurado',
        data={'isapre_actual':'Esencial','clinicas':'["Clínica Dávila"]'},
        files={'pdf':('bad.txt',b'no es pdf','text/plain')})
    assert r.status_code==400
    assert main._demo_calls==0

def test_pdf_judge_respects_global_limit(monkeypatch):
    monkeypatch.setenv('META_DEMO_ALLOWED','1')
    monkeypatch.setenv('MODEL_API_KEY','MOCK')
    monkeypatch.setenv('META_DEMO_MAX_CALLS','1')
    monkeypatch.setattr(main,'_demo_calls',1)
    r=c.post('/api/comparar-pdf-jurado',
        data={'isapre_actual':'Ficticia A','clinicas':'["Clínica Dávila"]'},
        files={'pdf':('ejemplo.pdf',_pdf(),'application/pdf')})
    assert r.status_code==429

def test_reference_candidates_no_same_isapre_and_no_price_promise():
    a=candidate_review_options('Consalud',['Clínica Dávila'])
    assert a and all(x['isapre']!='Consalud' for x in a)
    assert any(x['pdf_url'] and 'CS50400826.pdf' in x['pdf_url'] for x in a)
    assert all(x['ahorro_validado'] is False for x in a)
    b=candidate_review_options('Nueva Masvida',['Clínica Dávila'])
    assert b and all(x['isapre']!='Nueva Masvida' for x in b)
    assert all(x['precio_personalizado_uf'] is None for x in b)

def test_fictitious_presentation_page_works_without_meta():
    assert c.get('/prueba.html').status_code==200
    assert c.get('/api/contrato-ficticio.pdf').content.startswith(b'%PDF')

def test_optional_protesis_ortesis_extraida_no_auto_verified():
    from backend.meta_client import decode_json
    keys=['isapre','codigo_plan','nombre_plan','modalidad','hospitalaria','ambulatoria',
          'urgencia','clinicas_preferentes','topes','observaciones']
    obj={k:('Ejemplo' if k in keys[:4] else []) for k in keys}
    assert decode_json(json.dumps(obj))['protesis_ortesis']==[]
    obj['protesis_ortesis']=[{'descripcion':'Protesis, tope 10 UF',
                            'pagina_pdf':1,'evidencia':'Prótesis con tope 10 UF'}]
    got=decode_json(json.dumps(obj))
    assert got['protesis_ortesis'] and got['estado_verificacion']=='extraido_por_IA_pendiente_revision'

def test_client_page_provides_two_modes_and_download_link():
    page=c.get('/cliente')
    assert page.status_code==200
    h=page.text
    assert 'value="ficticio"' in h and 'value="upload"' in h
    assert '/api/comparar-pdf-jurado' in h
    assert 'CS50400826.pdf' in h
    assert 'id="agreeMeta"' in h
    assert '11,88 UF' in h
