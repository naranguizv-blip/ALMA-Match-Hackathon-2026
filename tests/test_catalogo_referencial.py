"""Asegura que el catálogo del concurso no genere recomendaciones sin respaldo."""
import json
from pathlib import Path
from collections import Counter
from fastapi.testclient import TestClient
from backend.main import app

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'backend'/'catalogo_referencial_20.json').read_text(encoding='utf-8'))
plans=data['planes']

def test_20_codes_from_four_insurers():
    assert data['cantidad']==20
    assert len(plans)==20
    assert len(set(p['codigo'] for p in plans))==20
    assert Counter(p['isapre'] for p in plans)=={'Banmédica':5,'Consalud':5,'Esencial':5,'Vida Tres':5}

def test_preliminary_catalog_is_not_approved_to_recommend():
    assert all(not p['apto_recomendacion'] for p in plans)
    assert all(not p['coberturas_completas_verificadas'] for p in plans)
    assert all(not p['topes_verificados'] for p in plans)
    assert all(p['precio_final_uf'] is None for p in plans)
    assert all(p['periodo']=='202608' for p in plans)
    for p in plans:
        assert p['origen'] and p['codigo'] and p['nombre']

def test_base_price_is_not_final_price():
    consalud=[p for p in plans if p['isapre']=='Consalud']
    assert all(p['precio_base_uf'] is not None for p in consalud)
    assert all(p['precio_final_uf'] is None for p in consalud)

def test_catalog_read_only_endpoint_and_demo_page():
    response=TestClient(app).get('/api/catalogo-referencial')
    assert response.status_code==200
    assert len(response.json()['planes'])==20
    page=(ROOT/'docs'/'catalogo.html').read_text(encoding='utf-8')
    assert '20 planes identificados de cuatro isapres' in page
    assert 'No son 20 recomendaciones listas para contratar' in page
    assert 'catalogo.html' in (ROOT/'docs'/'index.html').read_text(encoding='utf-8')
