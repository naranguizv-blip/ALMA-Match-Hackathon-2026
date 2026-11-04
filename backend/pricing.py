"""Parámetros de cotización demostrativa CL, verificados para 04-11-2026.

No confundir el precio final YA COTIZADO en una propuesta histórica
con un PRECIO BASE: sumarle factores o GES otra vez duplicaría componentes.

Fuentes:
- UF SII: https://www.sii.cl/valores_y_fechas/uf/uf2026.htm
- Tabla factores: https://www.superdesalud.gob.cl/normativa/circular-if-n-343/
- Tabla publicada Nueva Masvida: https://www.nuevamasvida.cl/leycorta-2/
- GES90: https://www.superdesalud.gob.cl/noticias/2025/12/por-primera-vez-la-superintendencia-de-salud-verifica-lo-que-las-isapres-quieren-cobrar-por-el-ges-y-corrige-excesos/
- Tope 7%: https://www.superdesalud.gob.cl/preguntas-frecuentes/cual-es-la-cotizacion-legal-para-salud-y-en-que-plazo-deben-ser-declaradas-y-pagadas/
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

UF_DATE="2026-11-04"
UF_CLP=Decimal("41268.88")
MAX_RENTA_IMPONIBLE_UF=Decimal("90")
GES_90_UF={
    "Banmédica":Decimal("0.778"),
    "Vida Tres":Decimal("0.712"),
    "Nueva Masvida":Decimal("0.854"),
    "Colmena":Decimal("1.036"),
    "Consalud":Decimal("0.731"),
    "Cruz Blanca":Decimal("0.971"),
    "Esencial":Decimal("0.910"),
}
TFU=[
    (0,20,Decimal("0.60"),Decimal("0.60")),
    (20,25,Decimal("0.90"),Decimal("0.70")),
    (25,35,Decimal("1.00"),Decimal("0.70")),
    (35,45,Decimal("1.30"),Decimal("0.90")),
    (45,55,Decimal("1.40"),Decimal("1.00")),
    (55,65,Decimal("2.00"),Decimal("1.40")),
    (65,111,Decimal("2.40"),Decimal("2.20")),
]
SOURCE_UF="https://www.sii.cl/valores_y_fechas/uf/uf2026.htm"
SOURCE_FACTOR="https://www.nuevamasvida.cl/leycorta-2/"
SOURCE_GES="https://www.superdesalud.gob.cl/noticias/2025/12/por-primera-vez-la-superintendencia-de-salud-verifica-lo-que-las-isapres-quieren-cobrar-por-el-ges-y-corrige-excesos/"


def as_decimal(value, label):
    try:
        x=Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError, AttributeError):
        raise ValueError(f"{label}: valor inválido")
    if not x.is_finite() or x<0:
        raise ValueError(f"{label}: valor inválido")
    return x


def factor_for_age(age, carga=False):
    if isinstance(age,bool) or not isinstance(age,int) or not 0<=age<=110:
        raise ValueError("La edad debe ser entera entre 0 y 110")
    # La TFU exime las cargas menores de dos años del componente de plan.
    if carga and age<2:
        return Decimal("0")
    for lower,upper,holder,dependent in TFU:
        if lower<=age<upper:
            return dependent if carga else holder
    raise ValueError("Edad fuera de rango")


def reference_parameters():
    return {
        "fecha_uf":UF_DATE,"uf_clp":str(UF_CLP),
        "GES_mensual_por_beneficiario_uf":{k:str(v) for k,v in GES_90_UF.items()},
        "tabla_factores":[{"edad_desde":lo,"edad_hasta_exclusiva":hi,
                           "cotizante":str(h),"carga":str(c)}
                           for lo,hi,h,c in TFU],
        "carga_menor_2_factor_plan":"0.00",
        "maximo_renta_imponible_uf":str(MAX_RENTA_IMPONIBLE_UF),
        "fuentes":{"uf":SOURCE_UF,"ges":SOURCE_GES,"factores":SOURCE_FACTOR},
        "advertencia":"Parámetros fechados. No se actualizan automáticamente ni certifican una cotización comercial."
    }


def illustrative_quote(precio_base_uf, isapre, edad_titular, edades_cargas, renta_imponible_clp=None):
    """Simula SOLO un contrato NUEVO con precio BASE en UF demostrado.

    No usar con el precio mensual final documentado de una propuesta histórica.
    Es necesario revisar tarifa base, vigencia, composición y adiciones comerciales.
    """
    if isapre not in GES_90_UF:
        raise ValueError("Isapre no admitida o sin GES verificado")
    if not isinstance(edades_cargas,list) or len(edades_cargas)>12:
        raise ValueError("Las edades de cargas deben ser una lista de hasta 12")
    base=as_decimal(precio_base_uf,"Precio base")
    if not Decimal("0.001")<=base<=Decimal("100"):
        raise ValueError("Precio base fuera del rango de simulación")
    factors=[factor_for_age(edad_titular)]+[factor_for_age(x,True) for x in edades_cargas]
    total_factor=sum(factors,Decimal("0"))
    beneficiaries=len(factors)
    complement=base*total_factor
    ges=GES_90_UF[isapre]*beneficiaries
    subtotal=complement+ges
    out={
      "tipo":"simulacion_no_cotizacion",
      "isapre":isapre,"edad_titular":edad_titular,"edades_cargas":edades_cargas,
      "beneficiarios":beneficiaries,"precio_base_uf":str(base),
      "factores":[str(x) for x in factors],"suma_factores":str(total_factor),
      "precio_plan_complementario_uf":str(complement.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP)),
      "ges_unitario_uf":str(GES_90_UF[isapre]),
      "ges_total_uf":str(ges.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP)),
      "subtotal_uf":str(subtotal.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP)),
      "subtotal_clp_aproximado":int((subtotal*UF_CLP).quantize(Decimal("1"),rounding=ROUND_HALF_UP)),
      "fecha_uf":UF_DATE,"uf_clp":str(UF_CLP),
      "precio_final_asegurado":False,
      "fuentes":reference_parameters()["fuentes"],
      "advertencias":[
        "Solo simula precio base×factores + GES. CAEC y beneficios adicionales no incluidos si se cobran por separado.",
        "No sumar nuevamente el GES ni los factores a un precio FINAL mensual ya cotizado.",
        "El precio base y la comercialización del plan deben acreditarse con documentación vigente."
      ]
    }
    if renta_imponible_clp not in (None,""):
        renta=as_decimal(renta_imponible_clp,"Renta imponible")
        if renta>Decimal("1000000000"):
            raise ValueError("Renta imponible fuera del rango")
        seven_uf=min(renta/UF_CLP,MAX_RENTA_IMPONIBLE_UF)*Decimal("0.07")
        out["cotizacion_legal_7pct_uf"]=str(seven_uf.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP))
        out["diferencia_sobre_7pct_uf"]=str(max(Decimal("0"),subtotal-seven_uf).quantize(Decimal("0.001"),rounding=ROUND_HALF_UP))
    return out
