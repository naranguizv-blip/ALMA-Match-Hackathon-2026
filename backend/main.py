"""ALMA Match demo local. No alojar públicamente sin seguridad y controles de costes."""
import json
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader
from .comparison import compare, legal_7_estimate
from .meta_client import analyze_pdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
MAX_BYTES=15*1024*1024
app=FastAPI(title='ALMA Match Hackathon — Demo',docs_url=None,redoc_url=None)


def build_response(extracted, isapre_actual, clinicas, objetivo, renta_imponible, pactado_uf, pago_actual, demo):
    if not isinstance(clinicas,list) or len(clinicas)>10 or any(not isinstance(x,str) or len(x)>120 for x in clinicas):
        raise HTTPException(400,'Lista de clínicas inválida')
    if not isinstance(isapre_actual,str) or len(isapre_actual)>60:
        raise HTTPException(400,'Isapre actual no válida')
    if objetivo not in ('ahorro','cobertura','ambas','clinicas'):
        objetivo='ambas'
    try:
        p=float(pactado_uf) if pactado_uf else None
    except (ValueError,TypeError):
        p=None
    if p is not None and not (0<p<=200):
        p=None
    try:
        payment=int(pago_actual) if pago_actual else None
    except (ValueError,TypeError):
        payment=None
    if payment is not None and not (0<payment<100_000_000):
        payment=None
    return {'resultado':extracted,
            'comparacion':compare(isapre_actual,clinicas,objetivo,payment,document_isapre=extracted.get('isapre')),
            'finanzas':{'pactado_uf':p,'pago_actual_clp':payment,
                        'cotizacion_legal_estimada':legal_7_estimate(renta_imponible)},
            'demostracion_precargada':demo,
            'nota':'Sin precios finales validados; no se envió ninguna solicitud de contacto.'}


@app.get('/')
def home():
    return FileResponse(ROOT/'frontend'/'index.html',media_type='text/html')


@app.get('/health')
def health():
    return {'status':'ok','muse_conectado':None,'nota':'No se ha consultado Meta en esta solicitud'}


@app.post('/api/demo')
async def demo(isapre_actual:str=Form(...),clinicas:str=Form(...),objetivo:str=Form('ambas'),
               renta_imponible:str=Form(''),pactado_uf:str=Form(''),pago_actual:str=Form('')):
    try:
        clinics=json.loads(clinicas)
    except json.JSONDecodeError:
        raise HTTPException(400,'Formato inválido de clínicas')
    example=json.loads((HERE/'extraccion_demo.json').read_text(encoding='utf-8'))
    return build_response(example,isapre_actual,clinics,objetivo,renta_imponible,pactado_uf,pago_actual,True)


@app.post('/api/analizar')
async def analizar(pdf:UploadFile=File(...),isapre_actual:str=Form(...),clinicas:str=Form(...),
                  objetivo:str=Form('ambas'),renta_imponible:str=Form(''),
                  pactado_uf:str=Form(''),pago_actual:str=Form('')):
    if not (pdf.filename or '').lower().endswith('.pdf'):
        raise HTTPException(400,'Solo puedes cargar archivos PDF')
    raw=await pdf.read(MAX_BYTES+1)
    await pdf.close()
    if len(raw)>MAX_BYTES:
        raise HTTPException(413,'PDF supera 15 MB')
    if not raw.startswith(b'%PDF-'):
        raise HTTPException(400,'El archivo no es un PDF válido')
    try:
        pages=len(PdfReader(BytesIO(raw),strict=False).pages)
    except Exception:
        raise HTTPException(400,'PDF dañado o ilegible')
    if pages<1 or pages>50:
        raise HTTPException(400,'La demostración admite entre 1 y 50 páginas')
    try:
        clinics=json.loads(clinicas)
    except json.JSONDecodeError:
        raise HTTPException(400,'Formato inválido de clínicas')
    try:
        extracted=analyze_pdf(raw)
    except (RuntimeError,ValueError) as exc:
        raise HTTPException(502,str(exc))
    result=build_response(extracted,isapre_actual,clinics,objetivo,renta_imponible,pactado_uf,pago_actual,False)
    result['paginas_pdf']=pages
    return result
