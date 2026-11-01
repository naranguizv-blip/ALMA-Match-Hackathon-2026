"""Cliente de Meta Model API: secretos únicamente en el proceso del servidor."""
import base64
import json
import os
import re

import requests

API_URL = "https://api.meta.ai/v1/responses"

PROMPT = """Eres un extractor de condiciones CONTRACTUALES de un plan de salud de Chile.
Lee el PDF completo. No calcules precios, ahorros ni consejo médico.
No inventes datos. Si faltan, usa null y registra la duda.
Responde EXCLUSIVAMENTE con JSON válido y estas claves:
{
 "isapre": null, "codigo_plan": null, "nombre_plan": null, "modalidad": null,
 "cobertura_hospitalaria": [], "cobertura_ambulatoria": [], "urgencia": [],
 "clinicas_preferentes": [], "topes": [], "observaciones": []
}
En cada elemento de cobertura, urgencia, clínica o tope incluye un objeto con
descripcion, pagina_pdf (entero o null), texto_evidencia (cita breve o null).
Distingue tope por evento frente a tope anual.
No atribuyas a una clínica cobertura de otra y nunca declares los datos verificados.
"""

def extract_output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks = []
    for entry in response.get("output", []):
        if not isinstance(entry, dict):
            continue
        for item in entry.get("content", []):
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                chunks.append(item["text"])
    if chunks:
        return "\n".join(chunks)
    raise ValueError("Meta no devolvió texto utilizable")

def decode_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
        t = re.sub(r"\s*```$", "", t)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as exc:
        raise ValueError("La respuesta no contiene JSON válido") from exc
    if not isinstance(obj, dict):
        raise ValueError("Respuesta JSON debe ser un objeto")
    required = (
        "isapre", "codigo_plan", "nombre_plan", "modalidad",
        "cobertura_hospitalaria", "cobertura_ambulatoria", "urgencia",
        "clinicas_preferentes", "topes", "observaciones",
    )
    for key in required:
        if key not in obj:
            raise ValueError(f"Falta el campo {key}")
    for key in required[4:]:
        if not isinstance(obj[key], list):
            raise ValueError(f"Campo {key} debe ser lista")
    obj["estado_verificacion"] = "extraido_por_ia_pendiente_revision"
    return obj

def analyze_pdf(pdf_bytes: bytes) -> dict:
    key = os.getenv("MODEL_API_KEY", "").strip()
    if not key or key == "COLOCA_AQUI_TU_CLAVE_LOCALMENTE":
        raise RuntimeError("Falta configurar MODEL_API_KEY en el servidor")
    model = os.getenv("MODEL_NAME", "muse-spark-1.3")
    pdf_url = "data:application/pdf;base64," + base64.b64encode(pdf_bytes).decode("ascii")
    payload = {
        "model": model,
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": PROMPT},
            {"type": "input_file", "filename": "contrato_prueba.pdf", "file_data": pdf_url},
        ]}],
    }
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise RuntimeError("No se pudo conectar con Meta Model API") from exc
    if response.status_code != 200:
        raise RuntimeError(f"Meta devolvió HTTP {response.status_code}; revisar cuenta, modelo y créditos")
    try:
        raw = response.json()
    except ValueError as exc:
        raise RuntimeError("Meta devolvió una respuesta no JSON") from exc
    result = decode_json(extract_output_text(raw))
    result["modelo_utilizado"] = model
    return result
