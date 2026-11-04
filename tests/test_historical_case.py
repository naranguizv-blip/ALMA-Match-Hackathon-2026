"""Ejercicio real anonimizado: cifras de una propuesta histórica, no un contrato nuevo."""
from backend.historical_case import historical_comparison
from backend.main import app
from fastapi.testclient import TestClient

def test_comparacion_historica_fiel_a_montos_documentados():
    data=historical_comparison()
    assert data["sin_datos_personales"] is True
    assert data["plan_actual"]["pago_informado_clp"] == 433000
    assert [x["precio_clp"] for x in data["alternativas"]] == [277372, 318549, 342078, 375902]
    assert [x["plan"] for x in data["alternativas"]] == [
        "EASY FOCUS 2 26","EASY FOCUS 8 26","LIFE FOCUS 6 26","LIFE FOCUS 215 7 26"]

def test_ahorro_es_calculo_no_afirmacion_de_contratacion():
    d=historical_comparison()
    assert [x["ahorro_mensual_potencial_clp"] for x in d["alternativas"]] == [155628,114451,90922,57098]
    assert [x["ahorro_anual_potencial_clp"] for x in d["alternativas"]] == [1867536,1373412,1091064,685176]
    assert all(not x["ahorro_confirmado"] for x in d["alternativas"])
    assert all(not x["equivalencia_coberturas_verificada"] for x in d["alternativas"])
    assert not d["hasta_tres_recomendaciones_verificadas"]

def test_davila_por_plan_no_es_equivalencia_generica():
    d=historical_comparison()
    assert [x["davila"]["hospitalaria_porcentaje"] for x in d["alternativas"]] == [60,80,80,70]
    assert [x["davila"]["ambulatoria_porcentaje"] for x in d["alternativas"]] == [50,50,60,60]
    assert "RedSalud" in d["alternativas"][0]["davila"]["urgencia"]
    assert "Dávila" in d["alternativas"][2]["davila"]["urgencia"]

def test_inconsistencia_de_pago_no_se_oculta():
    d=historical_comparison()
    assert d["plan_actual"]["suma_desglose_clp"]==433300
    assert any("$300" in x for x in d["observaciones"])

def test_no_se_publica_identidad_del_cliente_en_respuesta():
    import json
    txt=json.dumps(historical_comparison(),ensure_ascii=False).lower()
    assert "ricardo" not in txt
    assert "daza" not in txt
    assert "rut" not in txt
    assert "@" not in txt

def test_endpoint_caso_historico():
    r=TestClient(app).get("/api/caso-historico")
    assert r.status_code == 200
    assert len(r.json()["alternativas"])==4
