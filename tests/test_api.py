from io import BytesIO
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from backend.main import app
from backend.meta_client import decode_json, extract_output_text

client = TestClient(app)

def dummy_pdf():
    w = PdfWriter(); w.add_blank_page(width=400, height=600)
    buf = BytesIO(); w.write(buf); return buf.getvalue()

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_reject_text():
    r = client.post("/api/analizar", files={"pdf": ("a.txt", b"test", "text/plain")})
    assert r.status_code == 400

def test_missing_key(monkeypatch):
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    r = client.post("/api/analizar", files={"pdf": ("test.pdf",dummy_pdf(),"application/pdf")})
    assert r.status_code == 502

def test_decode_json():
    j='{"isapre":null,"codigo_plan":null,"nombre_plan":null,"modalidad":null,"cobertura_hospitalaria":[],"cobertura_ambulatoria":[],"urgencia":[],"clinicas_preferentes":[],"topes":[],"observaciones":[]}'
    assert decode_json(j)["estado_verificacion"] == "extraido_por_ia_pendiente_revision"

def test_output_text():
    assert extract_output_text({"output":[{"content":[{"text":"OK"}]}]}) == "OK"
