"""ALMA Match demo local. No alojar públicamente sin seguridad y controles de costes."""
import json
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader
from .comparison import compare, legal_7_estimate, norm
from .meta_client import analyze_pdf
from .verification import verify_document_claims
from .demo_scenarios import synthetic_case
from .historical_case import historical_comparison
from .pricing import reference_parameters, illustrative_quote

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
MAX_BYTES=15*1024*1024
app=FastAPI(title='ALMA Match Hackathon — Demo',docs_url=None,redoc_url=None)


def build_response(extracted, isapre_actual, clinicas, objetivo, renta_imponible, pactado_uf, pago_actual, demo, verification=None):
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
    preliminary = compare(isapre_actual,clinicas,objetivo,payment,document_isapre=extracted.get('isapre'))
    if not verification or not verification.get('aprobado_para_comparacion'):
        preliminary['alternativas'] = []
        preliminary['error'] = ('Contrato no verificado documentalmente: ' +
            '; '.join((verification or {}).get('motivos', [])[:2])
            if verification else 'Ejemplo precargado sin validación independiente del PDF. No ofrece alternativas verificadas.')
        preliminary['estado'] = 'bloqueado_pendiente_revision'
    return {'resultado':extracted,
            'verificacion_documental':verification or {'estado':'revision_requerida','aprobado_para_comparacion':False,
                 'motivos':['Ejemplo sin PDF original en esta ejecución']},
            'comparacion':preliminary,
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




@app.get('/api/demo-caso/{scenario}')
def demo_case(scenario: str):
    """Sin claves ni créditos: escenarios plenamente inventados y separados del catálogo real."""
    try:
        return synthetic_case(scenario)
    except ValueError:
        raise HTTPException(404, 'Caso ficticio no disponible')

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
    verification=verify_document_claims(extracted,raw)
    result=build_response(extracted,isapre_actual,clinics,objetivo,renta_imponible,pactado_uf,pago_actual,False,verification)
    result['paginas_pdf']=pages
    return result


# Hackathon: recorrido verificable con documento sintético propio. No usa Meta.
@app.get('/presentacion')
def presenter():
    return FileResponse(ROOT/'frontend'/'presentacion.html', media_type='text/html')


@app.get('/api/contrato-ficticio.pdf')
def sample_contract():
    from fastapi.responses import Response
    from .demo_scenarios import _pdf
    return Response(content=_pdf(), media_type='application/pdf',
                    headers={'Content-Disposition': 'attachment; filename="ALMA_Contrato_FICTICIO_DEMO001.pdf"'})


@app.post('/api/demo-archivo')
async def demo_upload(pdf: UploadFile = File(...), escenario: str = Form('comparable')):
    """Verifica PDF realmente recibido contra el CASO SINTÉTICO de muestra.

    Las coberturas en esta ruta vienen de una plantilla declarada y NO de Muse.
    Muse se utiliza únicamente en /api/analizar, cuya llamada consume recursos.
    """
    from .demo_scenarios import _extraction, synthetic_case
    if escenario not in ('comparable', 'no_comparable'):
        raise HTTPException(400, 'Escenario no válido')
    if not (pdf.filename or '').lower().endswith('.pdf'):
        raise HTTPException(400, 'Selecciona el contrato PDF ficticio de la demostración.')
    raw = await pdf.read(2*1024*1024+1)
    await pdf.close()
    if not raw.startswith(b'%PDF-') or len(raw)>2*1024*1024:
        raise HTTPException(400, 'El documento no es un PDF de demostración válido.')
    from .verification import verify_document_claims
    extracted = _extraction()
    verification = verify_document_claims(extracted, raw)
    if not verification['aprobado_para_comparacion']:
        raise HTTPException(422, 'El PDF no coincide con las evidencias del contrato ficticio o está ilegible. No se puede comparar.')
    result = synthetic_case(escenario)
    result['verificacion_documental'] = verification
    result['archivo_procesado'] = pdf.filename
    result['paginas_pdf'] = verification['paginas_pdf']
    result['origen_extraccion'] = ('Plantilla sintética conocida comprobada contra el PDF cargado. '
                                   'Esta ruta NO invoca Meta Model API.')
    result['nota'] = ('Lectura real del PDF y comparación determinista con condiciones ficticias. '
                      'No es una extracción por IA en vivo ni una recomendación comercial.')
    return result


@app.get('/api/caso-historico')
def historical_demo():
    """Sin datos de clientes. No llama a Meta ni confirma oferta vigente."""
    return historical_comparison()


@app.get('/caso-historico')
def historic_presenter():
    return FileResponse(ROOT/'frontend'/'caso_historico.html', media_type='text/html')


@app.get('/api/parametros-precio')
def get_pricing_parameters():
    """UF fechada, TFU y GES 90 con fuentes, solo lectura."""
    return reference_parameters()


@app.post('/api/simular-precio')
def quote_example(payload: dict):
    """Simulación educativa. Precio BASE nunca precio FINAL previo."""
    try:
        return illustrative_quote(
            precio_base_uf=payload.get('precio_base_uf'),
            isapre=payload.get('isapre'),
            edad_titular=payload.get('edad_titular'),
            edades_cargas=payload.get('edades_cargas', []),
            renta_imponible_clp=payload.get('renta_imponible_clp')
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, str(exc))


@app.get('/cliente')
def client_demo():
    """Recorrido de principio a fin sin datos personales ni solicitudes de IA."""
    return FileResponse(ROOT/'docs'/'cliente.html',media_type='text/html')


# Recorrido del jurado: carga auténtica + Muse Spark + candidatos documentales.
# Impone un presupuesto operativo de llamadas por proceso, NO una garantía de
# límite de facturación. El despliegue debe tener controles adicionales.
from fastapi import Request
from threading import Lock
from .judge_demo import candidate_review_options
import os
from decimal import Decimal, InvalidOperation

_demo_calls=0
_demo_lock=Lock()


@app.get('/api/estado-jurado')
def judge_status():
    enabled=(os.environ.get('META_DEMO_ALLOWED')=='1' and bool(os.environ.get('MODEL_API_KEY')))
    return {
        'meta_disponible':enabled,
        'modo':'PDF real con Muse Spark' if enabled else 'Solo caso precargado y ficticio',
        'precio_de_otra_persona_no_es_cotizacion':True,
        'nota':'Para subir PDFs nuevos debe existir backend FastAPI, autorización y clave en el servidor.'
    }


@app.post('/api/comparar-pdf-jurado')
async def judge_pdf(
    request: Request,
    pdf: UploadFile=File(...),
    isapre_actual: str=Form(...),
    clinicas: str=Form(...),
    pago_actual_uf: str=Form(''),
):
    """Ejecuta Meta para un PDF nuevo: extrae, revisa citas y devuelve candidatos.

    No genera cotizaciones ni ahorros de una composición familiar desconocida.
    No guarda el documento en el disco y jamás devuelve contenido base64.
    """
    global _demo_calls
    if os.environ.get('META_DEMO_ALLOWED')!='1':
        raise HTTPException(503,'La lectura Meta no está activada en este servidor.')
    if not os.environ.get('MODEL_API_KEY'):
        raise HTTPException(503,'Falta la credencial Meta configurada en el servidor.')
    if not (pdf.filename or '').lower().endswith('.pdf'):
        raise HTTPException(400,'Solo se admiten contratos PDF.')
    try:
        target_clinics=json.loads(clinicas)
    except (TypeError,ValueError):
        raise HTTPException(400,'Clínicas no válidas.')
    if not isinstance(target_clinics,list) or not 1<=len(target_clinics)<=8:
        raise HTTPException(400,'Debes seleccionar entre una y ocho clínicas.')
    if not all(isinstance(x,str) and 2<=len(x)<=100 for x in target_clinics):
        raise HTTPException(400,'Nombre de clínica inválido.')
    if not isinstance(isapre_actual,str) or not 2<=len(isapre_actual)<=60:
        raise HTTPException(400,'Selecciona la isapre actual.')
    amount=None
    if pago_actual_uf.strip():
        try:
            amount=Decimal(pago_actual_uf.strip().replace(',','.'))
        except InvalidOperation:
            raise HTTPException(400,'Pago actual UF inválido.')
        if not amount.is_finite() or not Decimal('0')<amount<Decimal('150'):
            raise HTTPException(400,'Pago actual UF fuera de rango.')
    raw=await pdf.read(6*1024*1024+1)
    await pdf.close()
    if len(raw)>6*1024*1024:
        raise HTTPException(413,'El PDF supera el límite de 6 MB.')
    if not raw.startswith(b'%PDF-'):
        raise HTTPException(400,'El archivo no es un PDF válido.')
    try:
        reader=PdfReader(BytesIO(raw),strict=False)
        pages=len(reader.pages)
        if not 1<=pages<=15:
            raise ValueError('Cantidad de páginas fuera de rango')
    except Exception:
        raise HTTPException(400,'PDF ilegible o de más de 15 páginas.')
    # El control global reduce uso accidental, pero NO reemplaza cuotas del proveedor.
    try:
        cap=max(1,min(int(os.environ.get('META_DEMO_MAX_CALLS','8')),30))
    except ValueError:
        cap=8
    with _demo_lock:
        if _demo_calls>=cap:
            raise HTTPException(429,'Se alcanzó el máximo de análisis de esta demostración.')
        _demo_calls+=1
    try:
        extracted=analyze_pdf(raw)
    except (RuntimeError,ValueError):
        raise HTTPException(502,'Meta no pudo completar la lectura. No se han generado recomendaciones.')
    ver=verify_document_claims(extracted,raw)
    if norm(extracted.get('isapre'))!=norm(isapre_actual):
        ver['aprobado_para_comparacion']=False
        ver.setdefault('motivos',[]).append('La isapre del contrato no coincide con la seleccionada')
    candidates=candidate_review_options(isapre_actual,target_clinics)
    return {
        'modo':'analisis_meta_real',
        'modelo_meta':os.environ.get('MODEL_NAME','muse-spark-1.3'),
        'contrato':extracted,
        'verificacion_documental':ver,
        'paginas_pdf':pages,
        'opciones_para_revisar':candidates,
        'total_opciones':len(candidates),
        'pago_actual_uf_informado':str(amount) if amount is not None else None,
        'ahorro_verificado':False,
        'precios_personalizados_disponibles':False,
        'estado':'informativo_sin_equivalencia_certificada',
        'aviso':('Se leyó tu documento con Muse Spark. Las alternativas son referencias para revisar '
                'y NO están cotizadas para tus edades ni garantizan mejor cobertura. '
                'No calculamos ahorro hasta validar precios, red, factores, GES y topes.'),
        'privacidad':'El documento no se guarda en este servidor. Para analizarlo fue enviado a Meta Model API.'
    }


@app.get('/prueba.html')
def fictional_example_page():
    """Interfaz alternativa de caso ficticio sin llamada a Meta."""
    return FileResponse(ROOT/'docs'/'prueba.html',media_type='text/html')


@app.get('/api/catalogo-referencial')
def catalogo_referencial():
    """Veinte fichas identificadas, solo para exploración.

    NO mezcla inventario preliminar con recomendaciones certificadas.
    """
    return json.loads((HERE/'catalogo_referencial_20.json').read_text(encoding='utf-8'))
