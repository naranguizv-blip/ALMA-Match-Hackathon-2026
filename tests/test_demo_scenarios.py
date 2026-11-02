"""Pruebas de los dos recorridos de demo sin llamadas a Meta ni planes reales."""
from fastapi.testclient import TestClient
from backend.main import app
from backend.demo_scenarios import synthetic_case

client=TestClient(app)

def test_synthetic_positive():
    obj=synthetic_case('comparable')
    assert obj['demostracion_ficticia'] is True
    assert obj['verificacion_documental']['aprobado_para_comparacion']
    assert obj['verificacion_documental']['citas_comprobadas']==5
    assert [c['codigo'] for c in obj['comparacion']['alternativas']]==['DEMO002']
    assert obj['comparacion']['alternativas'][0]['precio_final_uf'] is None
    assert len(obj['comparacion']['rechazadas'])==3

def test_same_percent_but_smaller_urgency_limit_rejected():
    obj=synthetic_case('comparable')
    bad=next(r for r in obj['comparacion']['rechazadas'] if r['codigo']=='DEMO003')
    assert any('urgencia: tope inferior' in m for m in bad['motivos'])
    assert 'DEMO003' not in [x['codigo'] for x in obj['comparacion']['alternativas']]

def test_different_network_rejected():
    obj=synthetic_case('comparable')
    bad=next(r for r in obj['comparacion']['rechazadas'] if r['codigo']=='DEMO004')
    assert 'clínica preferente distinta' in bad['motivos']

def test_same_isapre_rejected():
    obj=synthetic_case('comparable')
    bad=next(r for r in obj['comparacion']['rechazadas'] if r['codigo']=='DEMO005')
    assert 'misma isapre del contrato actual' in bad['motivos']

def test_no_comparable():
    obj=synthetic_case('no_comparable')
    assert obj['verificacion_documental']['aprobado_para_comparacion']
    assert obj['comparacion']['alternativas']==[]
    assert 'no existen alternativas comparables' in obj['comparacion']['estado']

def test_synthetic_api_works():
    r=client.get('/api/demo-caso/comparable')
    assert r.status_code==200
    assert r.json()['comparacion']['alternativas'][0]['codigo']=='DEMO002'

def test_invalid_scenario_no_crash():
    r=client.get('/api/demo-caso/no-existe')
    assert r.status_code==404
