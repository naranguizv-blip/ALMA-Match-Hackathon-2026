from backend.comparison import compare, legal_7_estimate, parse_groups

def test_exact_clinic_percentage():
    x=parse_groups('100% sin tope\nClínica Dávila\nClínica Indisa\n\n70% sin tope\nClínica Santa María')
    assert x['clinica indisa']['porcentaje']==100
    assert x['clinica santa maria']['porcentaje']==70
    assert 'clinica davila vespucio' not in x

def test_excludes_same_isapre():
    result=compare('Banmédica',['Clínica Indisa'])
    assert result['alternativas']==[]


def test_real_network_matches_are_limited():
    result=compare('Esencial',['Clínica Indisa'],'ahorro',120000)
    assert result['alternativas']
    assert len(result['alternativas'])<=3
    assert all(x['isapre']=='Banmédica' for x in result['alternativas'])
    assert all(x['precio_final_uf'] is None and not x['ahorro_verificado'] for x in result['alternativas'])
    assert 'no se puede asegurar' in result['mensaje_ahorro']


def test_isapre_pdf_mismatch_blocks():
    r=compare('Colmena',['Clínica Dávila'], document_isapre='Esencial')
    assert r['alternativas']==[] and 'no coincide' in r['error']


def test_7_percent_is_from_renta():
    assert legal_7_estimate(1_500_000)['monto_clp_estimado']==105000
    assert legal_7_estimate(100_000_000) is not None
    assert legal_7_estimate(-1) is None
