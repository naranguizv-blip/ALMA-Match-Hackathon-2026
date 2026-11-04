"""Genera la vista estática que puede abrirse sin servidor ni gastos de IA.

La fuente única de los números del caso está en backend/historical_case.py.
No incluye contratos de terceros, datos personales ni claves.
"""
import json
from pathlib import Path
from backend.historical_case import historical_comparison
from backend.demo_scenarios import synthetic_case

ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/"docs"
DEST.mkdir(exist_ok=True)

historical=historical_comparison()
source=(ROOT/"frontend"/"caso_historico.html").read_text(encoding="utf-8")
anchor="fetch('/api/caso-historico')"
assert source.count(anchor)==1
inline='Promise.resolve({ok:true,json:()=>Promise.resolve('+json.dumps(historical,ensure_ascii=False,sort_keys=True)+')})'
offline=source.replace(anchor,inline)
offline=offline.replace(
    '<div class="kicker">DEMO · CASO HISTÓRICO ANONIMIZADO</div>',
    '<div class="kicker">DEMO ESTÁTICA SIN SERVIDOR · CASO HISTÓRICO ANONIMIZADO</div>'
    '<p class="note"><a href="prueba.html">Ver el escenario ficticio que rechaza topes desfavorables</a></p>'
)
(DEST/"index.html").write_text(offline,encoding="utf-8")

positive=synthetic_case('comparable')
negative=synthetic_case('no_comparable')
template=r"""<!doctype html><html lang="es-CL"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ALMA Match — verificación y rechazo de planes ficticios</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f5f8f8;color:#17333c;font:16px/1.5 system-ui,Arial}
header{background:#103543;color:white;padding:19px}main{max-width:970px;margin:auto;padding:20px}h1{font-size:clamp(24px,5vw,37px);line-height:1.1}
.card{background:white;border:1px solid #d9e8e5;border-radius:16px;padding:18px;margin:14px 0}
button{background:#008e87;color:white;border:0;border-radius:11px;padding:12px 16px;font-weight:700;margin:4px;cursor:pointer}
button.secondary{background:#e2f1ee;color:#006b67}.flex{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.kpi{padding:13px;border-radius:11px;background:#eaf6f4}.kpi strong{font-size:24px;display:block}
.track{height:11px;border-radius:9px;background:#deebea;overflow:hidden}.fill{height:100%;background:#048d82;border-radius:9px}
.item{border-top:1px solid #e7eeee;padding:12px 0}.warn{background:#fff2db;padding:11px;border-radius:9px;color:#715117}
small{color:#59727b}a{color:#00776e} .good{color:#056c4e;font-weight:700}
@media(max-width:640px){.flex{grid-template-columns:1fr}button{width:100%;margin:4px 0}}
</style></head><body><header><b>ALMA Match</b> · Tu plan. Tu comparación. Tu decisión.</header>
<main><p><a href="index.html">Volver al caso histórico con precios en UF</a></p>
<h1>No basta con tener el mismo porcentaje</h1>
<p>Escenarios <b>100 % inventados</b> para demostrar verificaciones deterministas. No representan isapres ni contratos reales. No hay llamada a Meta en esta página.</p>
<button id="yes">Mostrar alternativa comparable</button><button class="secondary" id="no">Mostrar alternativa rechazada</button>
<div id="result"></div>
<div class="card"><b>Qué hace Meta y qué hace nuestro código</b><p>Muse Spark se probó en una ejecución independiente con un PDF real. Esta demo sintética presenta la verificación de citas/páginas y las reglas de topes y clínicas. Una cita encontrada no certifica una interpretación contractual correcta.</p></div>
</main><script>
const DATA_POS=__POS__;
const DATA_NEG=__NEG__;
const el=document.getElementById('result');
function safe(x){return String(x??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','&':'&amp;'}[c]))}
function render(data){
 const c=data.comparacion,opts=c.alternativas||[];
 const line=(o)=>'<div class="item"><b>'+safe(o.nombre)+'</b> · '+safe(o.isapre)+'<p>'+safe(o.urgencia)+'</p></div>';
 let out='<section class="card"><h2>Plan actual ficticio — Ficticia A</h2><div class="flex"><div class="kpi">Hospitalaria<strong>80 %</strong><small>tope 400 UF al año</small></div><div class="kpi">Urgencia<strong>60 %</strong><small>tope 5 UF por evento</small></div></div>';
 out+='<p class="good">Citas literales comprobadas: '+safe(data.verificacion_documental.citas_comprobadas)+' · esto no valida semántica ni convenios</p></section>';
 out+='<section class="card"><h2>'+safe(c.estado)+'</h2>';
 if(opts.length){
  out+='<h3>'+safe(opts[0].nombre)+'</h3><p>La alternativa conserva la misma clínica ficticia y tiene 85 % de hospitalaria con tope de 450 UF/año; urgencia 65 % con tope de 6 UF por evento.</p>';
  out+='<div class="flex"><div class="kpi">Hospitalaria<strong>80 → 85 %</strong><small>400 → 450 UF/año</small></div><div class="kpi">Urgencia<strong>60 → 65 %</strong><small>5 → 6 UF/evento</small></div></div>';
 } else {
  out+='<div class="warn">No existe un plan equivalente entre estos ejemplos. ALMA no inventa una recomendación.</div>';
 }
 out+='<h3>Opciones descartadas</h3>'+(c.rechazadas||[]).map(r=>'<div class="item"><b>'+safe(r.nombre)+'</b><p>'+safe(r.motivos.join('; '))+'</p></div>').join('');
 out+='<p><small>Precios y ahorro: pendientes. Es un escenario técnico ficticio, no una oferta.</small></p></section>';
 el.innerHTML=out;
}
document.getElementById('yes').onclick=()=>render(DATA_POS);
document.getElementById('no').onclick=()=>render(DATA_NEG);
render(DATA_POS);
</script></body></html>"""
static=template.replace('__POS__',json.dumps(positive,ensure_ascii=False,sort_keys=True)).replace('__NEG__',json.dumps(negative,ensure_ascii=False,sort_keys=True))
(DEST/"prueba.html").write_text(static,encoding="utf-8")
print("Demo estática lista (HTML sin llamadas pagadas):",DEST/"index.html", DEST/"prueba.html")
