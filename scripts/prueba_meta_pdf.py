"""Prueba manual segura: documento inventado, sin datos reales ni secretos en logs."""
import base64
import io
import json
import os
import sys

import requests
from reportlab.pdfgen import canvas

PDF_CODE = "DEMOALMA2026"
api_key = os.environ.get("MODEL_API_KEY", "").strip()
if not api_key:
    sys.exit("ERROR: falta MODEL_API_KEY")

pdf = io.BytesIO()
p = canvas.Canvas(pdf, pagesize=(595, 842))
p.setFont("Helvetica-Bold", 17)
p.drawString(50, 785, "ALMA MATCH - CONTRATO FICTICIO DE PRUEBA")
p.setFont("Helvetica", 12)
for index, value in enumerate([
    "Documento inventado para probar la conexion con Muse Spark.",
    "Isapre ficticia: Ejemplo Salud.",
    "Codigo oficial ficticio: DEMOALMA2026.",
    "Hospitalaria: 90 por ciento en Clinica Inventada.",
    "Ambulatoria: 80 por ciento en Clinica Inventada.",
    "Urgencia: sin informacion suficiente en este documento.",
    "NO es un contrato comercial real, no es una cotizacion.",
]):
    p.drawString(50, 740 - index * 30, value)
p.save()
pdf_data = "data:application/pdf;base64," + base64.b64encode(pdf.getvalue()).decode("ascii")

payload = {
    "model": "muse-spark-1.3",
    "input": [{
        "role": "user",
        "content": [
            {"type": "input_text", "text": (
                "Este PDF es un caso inventado de prueba. "
                "Lee el documento e indica unicamente el codigo de plan que aparece. "
                "Si no lo puedes leer, escribe DESCONOCIDO. "
                "No agregues informacion externa."
            )},
            {"type": "input_file", "filename": "alma_demo_ficticia.pdf", "file_data": pdf_data},
        ],
    }],
    "max_output_tokens": 220,
}

try:
    response = requests.post(
        "https://api.meta.ai/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
except requests.RequestException as exc:
    sys.exit("ERROR: no se pudo contactar a la API de Meta")

if response.status_code != 200:
    sys.exit(f"ERROR: Meta respondió con HTTP {response.status_code}. Revisar clave, modelo y cuota.")

try:
    data = response.json()
    output = data.get("output_text", "")
    if not output:
        output = "\\n".join(
            part.get("text", "")
            for item in data.get("output", []) if isinstance(item, dict)
            for part in item.get("content", []) if isinstance(part, dict)
        )
except (ValueError, TypeError):
    sys.exit("ERROR: no se pudo interpretar la respuesta de Meta")

if PDF_CODE not in output.upper().replace("-", "").replace(" ", ""):
    sys.exit("ERROR: Muse respondió, pero no extrajo el código del PDF. Revisar formato de salida.")

print("OK: Muse Spark 1.3 leyó el PDF ficticio y reconoció el código esperado.")
print("La clave no fue mostrada; no se procesaron datos de clientes.")
