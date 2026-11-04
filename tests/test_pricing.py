from decimal import Decimal
from fastapi.testclient import TestClient
from backend.main import app
from backend.pricing import (
    UF_DATE, UF_CLP, factor_for_age, illustrative_quote, reference_parameters
)

def test_uf_is_dated_sii():
    p=reference_parameters()
    assert p['fecha_uf']=='2026-11-04'
    assert p['uf_clp']=='41268.88'
    assert 'sii.cl' in p['fuentes']['uf']

def test_ges_90_por_isapre_aprobados():
    d=reference_parameters()['GES_mensual_por_beneficiario_uf']
    assert d['Consalud']=='0.731'
    assert d['Nueva Masvida']=='0.854'
    assert d['Colmena']=='1.036'
    assert d['Cruz Blanca']=='0.971'
    assert d['Esencial']=='0.910'
    assert d['Banmédica']=='0.778'
    assert d['Vida Tres']=='0.712'

def test_tfu_titular_y_cargas_distintos():
    assert factor_for_age(40)==Decimal('1.30')
    assert factor_for_age(40,True)==Decimal('0.90')
    assert factor_for_age(25)==Decimal('1.00')
    assert factor_for_age(25,True)==Decimal('0.70')

def test_carga_menor_de_dos_no_paga_factor_pero_si_ges():
    quote=illustrative_quote('2.5','Consalud',40,[1,13],2000000)
    assert quote['factores']==['1.30','0','0.60']
    assert quote['ges_total_uf']=='2.193'
    assert quote['precio_plan_complementario_uf']=='4.750'
    assert quote['subtotal_uf']=='6.943'
    assert quote['precio_final_asegurado'] is False

def test_ejemplo_precio_base_y_renta():
    quote=illustrative_quote('3.50','Consalud',40,[15],2000000)
    assert quote['suma_factores']=='1.90'
    assert quote['ges_total_uf']=='1.462'
    assert quote['precio_plan_complementario_uf']=='6.650'
    assert quote['subtotal_uf']=='8.112'
    assert quote['fecha_uf']=='2026-11-04'
    assert quote['cotizacion_legal_7pct_uf']=='3.392'

def test_tope_de_cotizacion_legal_uf_6_3():
    quote=illustrative_quote('2.0','Banmédica',45,[],10000000)
    assert quote['cotizacion_legal_7pct_uf']=='6.300'

def test_bad_data_fail_closed():
    import pytest
    for base in ('-1','NaN',None,'abc','0','800'):
        with pytest.raises(ValueError):
            illustrative_quote(base,'Consalud',40,[])
    with pytest.raises(ValueError):
        illustrative_quote('3.5','Isapre Inventada',40,[])
    with pytest.raises(ValueError):
        illustrative_quote('3.5','Consalud',40,[-3])
    with pytest.raises(ValueError):
        illustrative_quote('3.5','Consalud',40,[99]*13)

def test_api_pricing_reference():
    c=TestClient(app)
    out=c.get('/api/parametros-precio')
    assert out.status_code==200
    assert out.json()['GES_mensual_por_beneficiario_uf']['Consalud']=='0.731'
    out=c.post('/api/simular-precio',json={
        'precio_base_uf':'3.50','isapre':'Consalud','edad_titular':40,'edades_cargas':[15],
        'renta_imponible_clp':'2000000'
    })
    assert out.status_code==200
    assert out.json()['subtotal_uf']=='8.112'
    assert not out.json()['precio_final_asegurado']
    invalid=c.post('/api/simular-precio',json={'precio_base_uf':'8.374',
                      'isapre':'Desconocida','edad_titular':45,'edades_cargas':[]})
    assert invalid.status_code==400

def test_historical_quote_not_recalculated_with_ges():
    # Los 8,374 UF del Life Focus 6 26 fueron informados en una
    # propuesta de precio mensual FINAL, no un precio base.
    from backend.historical_case import historical_comparison
    data=historical_comparison()
    quote=next(x for x in data['alternativas'] if x['plan']=='LIFE FOCUS 6 26')
    assert quote['precio_uf']=='8.374'
    assert quote['ahorro_mensual_potencial_uf']=='2.226'
