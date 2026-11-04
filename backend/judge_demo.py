"""Opciones documentales para que el jurado explore un contrato nuevo.

Una extracción Muse no convierte cotizaciones hechas a otra persona en ofertas
personales. Esta capa devuelve candidatos únicamente para revisión, no
equivalencias ni ahorros garantizados.
"""
from .historical_case import PROPOSALS
from .comparison import norm
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
PDF_PUBLICO_ESENCIAL="https://www.planisapre.com/cotizador/pdf/CS50400826.pdf"


def candidate_review_options(isapre_actual, clinicas):
    origin=norm(isapre_actual)
    requested=" ".join(norm(x) for x in clinicas)
    if not origin or not isinstance(clinicas,list):
        return []
    result=[]
    if origin!=norm("Consalud"):
        for item in PROPOSALS:
            if "davila" not in requested:
                continue
            result.append({
                "isapre":"Consalud","nombre":item["plan"],
                "codigo":"Código comercial no validado en este prototipo",
                "precio_uf_historico":item["precio_uf"],
                "precio_personalizado_uf":None,
                "precio_aplicable_cliente":False,
                "ahorro_validado":False,
                "hospitalaria_davila":item["davila"]["hospitalaria_porcentaje"],
                "ambulatoria_davila":item["davila"]["ambulatoria_porcentaje"],
                "urgencia":item["davila"]["urgencia"],
                "evidencia":"Propuesta histórica de otro grupo familiar, pág. "+str(item["pagina_cobertura"]),
                "advertencia":"Precio y prestaciones corresponden a otra persona y fecha; requieren cotización propia y comprobación de topes.",
                "pdf_url":None,"clasificacion":"Opción referencial no certificada"
            })
            if len(result)==3:
                return result

    if origin!=norm("Esencial") and "davila" in requested:
        result.append({
            "isapre":"Esencial","nombre":"Centro Sur 50H40A",
            "codigo":"CS50400826","precio_uf_historico":None,
            "precio_personalizado_uf":None,"precio_aplicable_cliente":False,
            "ahorro_validado":False,"hospitalaria_davila":60,"ambulatoria_davila":50,
            "urgencia":"Requiere revisar condiciones exactas del contrato",
            "evidencia":"Contrato público Esencial CS50400826; porcentajes por prestador citados en plan público",
            "advertencia":"No se ha verificado que sea equivalente o más económico para tu situación.",
            "pdf_url":PDF_PUBLICO_ESENCIAL,"clasificacion":"Contrato público para evaluar"
        })

    if origin!=norm("Banmédica"):
        catalog=json.loads((ROOT/"catalogo_demo.json").read_text(encoding="utf-8"))
        for item in catalog:
            if len(result)>=3:
                break
            h=norm(item.get("hospitalaria",""))
            if "davila" not in requested or "davila" not in h:
                continue
            result.append({
                "isapre":"Banmédica","nombre":item.get("nombre","Plan del catálogo"),
                "codigo":item["codigo"],"precio_uf_historico":None,
                "precio_personalizado_uf":None,"precio_aplicable_cliente":False,
                "ahorro_validado":False,
                "hospitalaria_davila":None,"ambulatoria_davila":None,
                "urgencia":"Requiere cotejo con contrato original",
                "evidencia":"Extracto comercializado agosto 2026; coberturas/topes pendientes de verificación",
                "advertencia":"Plan solo para exploración documental. No recomendado ni cotizado.",
                "pdf_url":None,"clasificacion":"Revisión documental pendiente"
            })
    return result[:3]
