"""Cliente Meta Model API: solamente para servidor local, sin secretos en frontend."""
import base64
import json
import os
import re
import requests

API_URL = 'https://api.meta.ai/v1/responses'
REQUIRED = ('isapre','codigo_plan','nombre_plan','modalidad','hospitalaria','ambulatoria',
            'urgencia','clinicas_preferentes','topes','observaciones')
PROMPT = '''Lee cuidadosamente el PDF adjunto. Es un contrato de plan de salud chileno.
Extrae SOLO datos respaldados por este PDF, nunca inventes precios ni ahorros.
Responde EXCLUSIVAMENTE JSON válido con estas 11 claves:
"isapre", "codigo_plan", "nombre_plan", "modalidad", "hospitalaria", "ambulatoria", "urgencia", "clinicas_preferentes", "topes", "observaciones", "protesis_ortesis".
Las primeras cuatro claves son texto o null. Las otras siete son listas de objetos
{ "descripcion": texto, "pagina_pdf": entero o null, "evidencia": texto breve o null }.
Distingue porcentajes por red/clínica y por prestación; no atribuyas porcentajes a toda una red si no corresponde.
Distingue topes anuales frente a topes por evento/prestación. No inventes copagos fijos.
En "protesis_ortesis" extrae por separado prótesis, órtesis y elementos de osteosíntesis,
con porcentajes, tope UF, periodicidad y modalidad (preferente o libre elección),
sin trasladarles una cobertura hospitalaria general del mismo documento.
Cuando no aparezca esta prestación: usa [], y nunca completes datos inventados.
IMPORTANTE: el campo evidencia debe ser una CITA LITERAL copiada sin cambiar palabras
desde la página_pdf indicada, preferentemente entre 20 y 80 caracteres continuos.
No uses paráfrasis, explicaciones, símbolos añadidos ni puntos suspensivos como cita.
Si no puedes identificar una frase literal y su página, usa evidencia null y
pagina_pdf null: el verificador externo detendrá la comparación.
Si falta un dato, usa null o [] y señala incertidumbre en observaciones.
No incluyas instrucciones para cambiar de isapre ni consejo médico.''' 


def output_text(response):
    if isinstance(response.get('output_text'),str) and response['output_text']:
        return response['output_text']
    chunks=[]
    for x in response.get('output',[]):
        if not isinstance(x,dict):
            continue
        for part in x.get('content',[]):
            if isinstance(part,dict) and isinstance(part.get('text'),str):
                chunks.append(part['text'])
    if chunks:
        return '\n'.join(chunks)
    raise ValueError('Meta no entregó texto utilizable')


def decode_json(raw):
    text = re.sub(r'^```(?:json)?\s*|\s*```$', '',raw.strip(), flags=re.I)
    try:
        obj=json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError('Meta respondió, pero su JSON está incompleto') from exc
    if not isinstance(obj,dict):
        raise ValueError('Respuesta JSON no es un objeto')
    for key in REQUIRED:
        if key not in obj:
            raise ValueError(f'Falta el campo {key}')
    for key in REQUIRED[4:]:
        if not isinstance(obj[key],list):
            raise ValueError(f'Campo {key} no es una lista')
    if 'protesis_ortesis' not in obj:
        obj['protesis_ortesis']=[]
    if not isinstance(obj['protesis_ortesis'],list):
        raise ValueError('Campo protesis_ortesis no es una lista')
    # El modelo nunca puede acreditarse por sí mismo como "verificado".
    obj['estado_verificacion']='extraido_por_IA_pendiente_revision'
    obj['precio_final']=None
    return obj


def analyze_pdf(raw):
    key=os.environ.get('MODEL_API_KEY','').strip()
    if not key:
        raise RuntimeError('La clave Meta no está configurada en el servidor')
    body={
       'model':os.environ.get('MODEL_NAME','muse-spark-1.3'),
       'reasoning':{'effort':'low'},
       'max_output_tokens':8000,
       'input':[{'role':'user','content':[
          {'type':'input_text','text':PROMPT},
          {'type':'input_file','filename':'contrato_prueba.pdf',
           'file_data':'data:application/pdf;base64,'+base64.b64encode(raw).decode('ascii')}
       ]}]
    }
    try:
        r=requests.post(API_URL,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=body,timeout=160)
    except requests.RequestException as exc:
        raise RuntimeError('No se pudo consultar la API de Meta') from exc
    if r.status_code != 200:
        raise RuntimeError(f'Meta respondió HTTP {r.status_code}; revisa credencial y disponibilidad del modelo')
    try:
        data=r.json()
    except ValueError as exc:
        raise RuntimeError('Meta no entregó una respuesta JSON de API') from exc
    return decode_json(output_text(data))
