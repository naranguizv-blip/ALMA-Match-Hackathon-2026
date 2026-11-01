"""MVP local para el Hackathon. No apto para exponer sin autenticación."""
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader

from .meta_client import analyze_pdf

ROOT = Path(__file__).resolve().parent.parent
MAX_PDF_BYTES = 15 * 1024 * 1024
app = FastAPI(title="ALMA Match Hackathon — PDF", docs_url=None, redoc_url=None)

@app.get("/")
def homepage():
    return FileResponse(ROOT / "frontend/index.html", media_type="text/html")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Servidor local activo; no confirma conexión con Meta"}

@app.post("/api/analizar")
async def analizar(pdf: UploadFile = File(...)):
    filename = (pdf.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(400, "Solo se admiten PDF")
    raw = await pdf.read(MAX_PDF_BYTES + 1)
    await pdf.close()
    if len(raw) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF demasiado grande; máximo 15 MB")
    if not raw.startswith(b"%PDF-"):
        raise HTTPException(400, "El archivo no tiene cabecera PDF válida")
    try:
        pages = len(PdfReader(BytesIO(raw), strict=False).pages)
    except Exception:
        raise HTTPException(400, "PDF dañado o no legible")
    if pages < 1 or pages > 50:
        raise HTTPException(400, "La demo admite PDF de 1 a 50 páginas")
    try:
        result = analyze_pdf(raw)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(502, str(exc))
    return {
        "paginas_pdf": pages,
        "resultado": result,
        "precio_final": None,
        "nota": "Extracción de IA pendiente de revisión; no es cotización.",
    }
