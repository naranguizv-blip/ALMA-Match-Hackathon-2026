"""Prueba sobre un contrato real público. No guarda ni publica el PDF."""
import base64, json, os, sys, re
from pathlib import Path
import requests

CODE = "CS50400826"
URL = "https://cotizadorsalud.cl/pdf/CS50400826.pdf"
API = "https://api.meta.ai/v1/responses"
KEYS = ("codigo_plan","isapre","nombre_plan","modalidad",
        "hospitalaria","ambulatoria","urgencia",
        "clinicas_preferentes","topes","observaciones")
PROMPT = """Lee SOLO el PDF adjunto de un contrato de isapre chilena.
Extrae isapre, codigo_plan, nombre_plan, modalidad, hospitalaria,
ambulatoria, urgencia, clinicas_preferentes, topes y observaciones.
Respuesta SOLO JSON válido, con esas 10 claves. Los últimos seis
campos deben ser listas de objetos: descripcion, pagina_pdf, evidencia.
Identifica porcentajes por clínica/prestación y la diferencia entre
topes por evento, prestación o año. Si no consta, usa null o [].
No inventes prestaciones ni precios; no consideres verificado ningún dato.
No calcules el 7%, precios, descuentos ni recomendaciones comerciales.
No uses fuentes externas al contrato.
"""
def abort(msg):
    sys.exit("ERROR: " + msg)
def main():
    key = os.getenv("MODEL_API_KEY","").strip()
    if not key: abort("Secreto MODEL_API_KEY ausente")
    try:
        r = requests.get(URL, timeout=30, headers={"Accept":"application/pdf"},
                         allow_redirects=True, stream=True)
    except requests.RequestException: abort("No se pudo acceder al PDF público. Sin gasto Meta.")
    if r.status_code != 200:
        abort(f"Descarga pública HTTP {r.status_code}. Sin gasto Meta.")
    chunks = []
    n = 0
    for chunk in r.iter_content(131072):
        n += len(chunk)
        if n > 15_000_000: abort("PDF supera 15 MB; sin gasto Meta.")
        chunks.append(chunk)
    pdf = b"".join(chunks)
    if not pdf.startswith(b"%PDF-"):
        abort("La fuente devolvió un archivo distinto de PDF; sin gasto Meta.")
    print(f"PDF público leído: {len(pdf)} bytes. No se guardará en GitHub.")
    payload = {
        "model": "muse-spark-1.3",
        "reasoning":{"effort":"low"},
        "max_output_tokens":8000,
        "input":[{"role":"user","content":[
            {"type":"input_text","text":PROMPT},
            {"type":"input_file","filename":"contrato_esencial.pdf",
             "file_data":"data:application/pdf;base64,"+
             base64.b64encode(pdf).decode("ascii")}
        ]}]
    }
    try:
        response=requests.post(API,json=payload,headers={
            "Authorization":"Bearer "+key,"Content-Type":"application/json"
        },timeout=150)
    except requests.RequestException: abort("Sin respuesta de Meta")
    if response.status_code!=200:
        abort(f"Meta HTTP {response.status_code}")
    try: reply=response.json()
    except ValueError: abort("Respuesta de Meta inválida")
    text=reply.get("output_text","")
    if not text:
        text="\n".join(part.get("text","")
          for obj in reply.get("output",[]) if isinstance(obj,dict)
          for part in obj.get("content",[]) if isinstance(part,dict))
    text=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",text.strip(),flags=re.I)
    try: result=json.loads(text)
    except (json.JSONDecodeError,TypeError):
        abort("Muse respondió pero falta JSON válido; ajustar formato.")
    if str(result.get("codigo_plan","")).upper().replace(" ","")!=CODE:
        abort("Muse no reconoció el código del plan; respuesta requiere revisión.")
    for field in KEYS[4:]:
        if not isinstance(result.get(field),list):
            abort(f"Respuesta sin lista {field}; esquema pendiente.")
    result["estado_verificacion"]="extraido_por_IA_pendiente_revision"
    result["url_origen"]=URL
    result["precio_final"]=None
    path=Path("resultados/extraccion_esencial_real.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("OK: Muse leyó contrato real y reconoció CS50400826.")
    for field in KEYS[4:]:
        print(f"{field}: {len(result[field])} datos extraídos (NO verificados)")
    print("Se guardó solamente el JSON temporal para revisión.")
if __name__=="__main__": main()
