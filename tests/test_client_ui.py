"""Controles de regresión para el flujo comercial visible del cliente."""
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/'docs'/'cliente.html').read_text(encoding='utf-8')

def test_solo_cuatro_etapas_visibles_y_sin_cotizacion_tecnica():
    assert HTML.count('class="panel step')==4
    assert '5 · Precio nuevo' not in HTML
    assert 'id="step4"' not in HTML
    assert 'id="base"' not in HTML
    assert 'Consultar tabla de factores completa' not in HTML

def test_cargas_se_piden_una_a_una_y_pesos_se_formatean():
    assert 'id="loadCount"' in HTML
    assert 'id="loadAges"' in HTML
    assert 'Edad de la carga ' in HTML
    assert 'className="loadAgeInput"' in HTML
    assert 'id="income"' in HTML
    assert "fmtThousands(digits)" in HTML
    assert "2.000.000" in HTML
    assert 'ingresa la edad de cada carga' in HTML.lower()

def test_ahorro_visible_y_no_se_inventa_equivalencia():
    assert 'id="heroSavingUF"' in HTML
    assert 'id="heroSavingCLP"' in HTML
    assert 'id="featuredHos"' in HTML
    assert 'id="featuredAmb"' in HTML
    assert '100 % hospitalario' in HTML
    assert '7,4 UF' in HTML
    assert '15 UF' in HTML
    assert 'sin tope para prestaciones' in HTML.lower()
    assert '80 % preferente' in HTML

def test_las_cuatro_tarifas_historicas_no_se_recalculan_por_factores():
    for plan in ("Easy Focus 2 26","Easy Focus 8 26",
                 "Life Focus 6 26","Life Focus 215 7 26"):
        assert plan in HTML
    assert 'uf:6.790' in HTML and 'uf:7.798' in HTML
    assert 'uf:8.374' in HTML and 'uf:9.202' in HTML
    assert 'uf:9.202,clp:375902,h:70,a:60' in HTML
    assert "433000-q.clp" in HTML
    assert 'no modifica los precios finales cotizados' in HTML.lower()

def test_whatsapp_requiere_consentimiento_y_no_transmite_salud():
    assert 'id="consent"' in HTML
    assert 'id="contact"' in HTML
    assert "if(!$('consent').checked" in HTML
    assert 'wa.me/' in HTML
    assert 'no mis datos de salud ni mi renta' in HTML.lower()

def test_carga_pdf_no_finge_analisis_meta():
    assert 'Subir un contrato PDF y analizarlo con Muse Spark' in HTML
    assert '/api/comparar-pdf-jurado' in HTML
    assert 'no se hará pasar una carga local por un análisis real' in HTML
    assert 'sin tope' in HTML.lower()
