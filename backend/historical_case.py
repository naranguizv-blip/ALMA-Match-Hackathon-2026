"""Caso histórico ANONIMIZADO: transcripción de una propuesta privada revisada.

Valores del presupuesto comercial, NO pagos posteriores comprobados. La
información fue extraída y revisada manualmente: NO afirmar que Muse leyó este
documento ni publicar el original o identificadores de la persona.
Las coberturas se describen con el alcance mostrado en la propuesta, sin
certificar equivalencia, contratación o disponibilidad actual.
"""
from decimal import Decimal

MONTO_PAGADO_DECLARADO_CLP = 433_000
# Valor UF inferido SOLO para la conversión ilustrativa desde los pares UF/CLP
# de la propuesta, no valor oficial ni valor contractual del plan de origen.
UF_IMPLÍCITA_EN_PROPUESTA_CLP = Decimal('40850')
DESGLOSE_CLP = (377_000, 56_300)
PROPOSALS = (
    {
        "plan": "EASY FOCUS 2 26",
        "isapre": "Consalud",
        "precio_uf": "6.790",
        "precio_clp": 277_372,
        "pagina_precio": 2,
        "pagina_cobertura": 3,
        "davila": {
            "hospitalaria_porcentaje": 60,
            "ambulatoria_porcentaje": 50,
            "urgencia": "La imagen detalla urgencia integral en RedSalud, no acredita urgencia integral en Dávila para esta opción.",
            "condicion": "Prestadores indicados en anexo; médicos staff y habitación individual según condiciones de la propuesta.",
        },
    },
    {
        "plan": "EASY FOCUS 8 26",
        "isapre": "Consalud",
        "precio_uf": "7.798",
        "precio_clp": 318_549,
        "pagina_precio": 3,
        "pagina_cobertura": 4,
        "davila": {
            "hospitalaria_porcentaje": 80,
            "ambulatoria_porcentaje": 50,
            "urgencia": "La imagen detalla urgencia integral en RedSalud, no acredita urgencia integral en Dávila para esta opción.",
            "condicion": "Prestadores indicados en anexo; médicos staff y habitación individual según condiciones de la propuesta.",
        },
    },
    {
        "plan": "LIFE FOCUS 6 26",
        "isapre": "Consalud",
        "precio_uf": "8.374",
        "precio_clp": 342_078,
        "pagina_precio": 4,
        "pagina_cobertura": 5,
        "davila": {
            "hospitalaria_porcentaje": 80,
            "ambulatoria_porcentaje": 60,
            "urgencia": "La propuesta muestra un cuadro de urgencia integral con Clínica Dávila y Dávila Vespucio; copagos sujetos a tipo de urgencia y reglas del documento.",
            "condicion": "Prestadores indicados en anexo; médicos staff y habitación individual según condiciones de la propuesta.",
        },
    },
    {
        "plan": "LIFE FOCUS 215 7 26",
        "isapre": "Consalud",
        "precio_uf": "9.202",
        "precio_clp": 375_902,
        "pagina_precio": 5,
        "pagina_cobertura": 6,
        "davila": {
            "hospitalaria_porcentaje": 70,
            "ambulatoria_porcentaje": 60,
            "urgencia": "La propuesta muestra atención integral de urgencia en otros prestadores; Dávila no figura como urgencia integral en esa tabla.",
            "condicion": "Prestadores indicados en anexo; médicos staff y habitación individual según condiciones de la propuesta.",
        },
    },
)

def historical_comparison():
    alternativas = []
    for source in PROPOSALS:
        delta = MONTO_PAGADO_DECLARADO_CLP - source["precio_clp"]
        pago_actual_uf_estimado = Decimal(MONTO_PAGADO_DECLARADO_CLP) / UF_IMPLÍCITA_EN_PROPUESTA_CLP
        ahorro_uf = pago_actual_uf_estimado - Decimal(source["precio_uf"])
        alternativas.append({
            **source,
            "ahorro_mensual_potencial_clp": delta,
            "ahorro_mensual_potencial_uf": format(ahorro_uf.quantize(Decimal("0.001")), ".3f"),
            "ahorro_anual_potencial_uf": format((ahorro_uf * 12).quantize(Decimal("0.001")), ".3f"),
            "ahorro_anual_potencial_clp": delta * 12,
            "porcentaje_ahorro_potencial": round(delta * 100 / MONTO_PAGADO_DECLARADO_CLP, 1),
            "ahorro_confirmado": False,
            "equivalencia_coberturas_verificada": False,
            "comercializacion_vigente_verificada": False,
            "evidencia": ("Propuesta comercial histórica anonimizada, precio pág. "
                          + str(source["pagina_precio"])
                          + ", coberturas pág. " + str(source["pagina_cobertura"])),
        })
    return {
        "tipo": "caso_comercial_historico_anonimizado",
        "sin_datos_personales": True,
        "origen_datos": "Propuesta comercial histórica suministrada por la fundadora; transcripción y revisión manual del PDF, NO extracción en vivo por Muse.",
        "plan_actual": {
            "isapre": "Nueva Masvida",
            "pago_informado_clp": MONTO_PAGADO_DECLARADO_CLP,
            "pago_mensual_uf_aproximado": format((Decimal(MONTO_PAGADO_DECLARADO_CLP) / UF_IMPLÍCITA_EN_PROPUESTA_CLP).quantize(Decimal("0.001")), ".3f"),
            "uf_referencial_clp": str(UF_IMPLÍCITA_EN_PROPUESTA_CLP),
            "uf_referencial_origen": "Valor deducido de los pares UF/CLP de la propuesta histórica, no valor oficial fechado.",
            "pago_pactado_uf_exactamente_documentado": None,
            "desglose_informado_clp": list(DESGLOSE_CLP),
            "suma_desglose_clp": sum(DESGLOSE_CLP),
            "tope_dia_cama_uf": "7.40",
            "tope_medicamentos_hospitalarios_uf": "15.00",
            "tope_materiales_insumos_uf": "18.00",
            "tope_protesis_ortesis_anual_uf": "11.88",
            "fuente_protesis_ortesis": "Propuesta original, página 1: prótesis, órtesis y osteosíntesis, tope máximo por beneficiario/año.",
            "fuente": "Propuesta histórica, página 1; corresponde a la descripción del plan de origen, no a una certificación vigente.",
        },
        "alternativas": alternativas,
        "observaciones": [
            "El documento declara un pago total de $433.000, aunque 377.000 + 56.300 = 433.300. Se usa el total declarado para los cálculos, y debe revisarse la diferencia de $300.",
            "Estos precios y ahorros son de una propuesta histórica, NO una oferta vigente ni prueba de cambio o ahorro efectivamente obtenido.",
            "Las coberturas hospitalarias, ambulatorias y de urgencia varían entre los planes. No se ha demostrado que sean idénticas al plan actual.",
            "El índice por Clínica Dávila no garantiza la red, los topes por prestación, médicos staff ni los convenios vigentes.",
            "Pago actual en UF estimado usando 40.850 CLP/UF implícitos en esta propuesta; el contrato de origen no acredita UF pactadas exactas.",
            "Tope de medicamentos hospitalarios del plan de origen: 15 UF por evento en el PDF de este caso; no confundir con otro contrato que mencionaba 45 UF.",
            "Meta Muse Spark se probó en otro contrato por separado; este caso demuestra cálculo y presentación usando datos transcritos del PDF.",
        ],
        "hasta_tres_recomendaciones_verificadas": [],
        "estado": "Comparación histórica de precios verificables en el documento; equivalencia y vigencia comercial pendientes.",
    }
