# ALMA Match — Comparador verificable de contratos de isapre

**Meta Global AI Developer Hackathon 2026 · Build for Your World**  
**Nuevo desarrollo del 26 de octubre al 4 de noviembre de 2026 · Prototipo independiente de WordPress y de ALMA comercial.**

ALMA Match busca que una persona comprenda las coberturas, topes, condiciones y precios de su plan de salud sin depender de un intermediario. Las alternativas no se consideran equivalentes por presentar porcentajes similares.

## Qué contiene realmente esta entrega

**1. Uso significativo de IA de Meta.** En `backend/meta_client.py` se integra Meta Model API (`muse-spark-1.3`) para leer PDF, identificar isapre, código, coberturas hospitalarias, ambulatorias, urgencias, redes y topes, y devolver información estructurada con página y cita. Una ejecución real en GitHub Actions analizó un contrato público de Esencial `CS50400826`: [ver ejecución](https://github.com/naranguizv-blip/ALMA-Match-Hackathon-2026/actions/runs/41368596616). **Ese ensayo de API es independiente de las demostraciones gratuitas**; no afirmar que Muse analizó en vivo los casos precargados.

**2. Verificador documental externo.** `backend/verification.py` contrasta los textos atribuidos con la página del PDF, exige información hospitalaria, ambulatoria, de urgencia, red y topes, y bloquea citas inexistentes o incompletas. Encontrar una cita literal **no certifica la interpretación semántica**; la interfaz conserva esta advertencia. Los escaneos sin texto extraíble requieren revisión humana.

**3. Motor de comparación.** `backend/comparison.py` aplica reglas de red, topes y exclusión de la isapre actual y no calcula ahorro sin precios documentados. El catálogo real del negocio no está copiado aquí: seis extractos de Banmédica permanecen bloqueados mientras no se certifiquen todos sus topes/condiciones.

**4. Demo funcional segura con PDF ficticio.** `/presentacion` permite descargar y volver a subir un PDF generado por nosotros. `POST /api/demo-archivo` realmente lee el archivo, comprueba sus citas y muestra un escenario ficticio comparable y uno rechazado por topes o clínicas. Esta ruta **no llama a Meta** ni gasta créditos.

**5. Caso histórico REAL anonimizado con precios en UF.** `/caso-historico` presenta un pago de Nueva Masvida informado por un cliente y cuatro precios ofertados por Consalud en una propuesta histórica. El backend reproduce el ahorro potencial **determinísticamente**, muestra fuentes y diferencia coberturas en Clínica Dávila. El PDF original privado y los datos de identificación del cliente **no** forman parte del repositorio. **La transcripción se hizo manualmente, no mediante Muse Spark en vivo.** La propuesta no acredita que el cliente contratara, ahorrara efectivamente o mantenga esas tarifas. El pago original en UF es **estimado**, no pactado exacto.

## Ejecutar y probar

Python 3.11+:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Visitar:

- `http://127.0.0.1:8000/presentacion` — demo completa sin llamadas pagadas.
- `http://127.0.0.1:8000/caso-historico` — ejercicio histórico en UF.
- `http://127.0.0.1:8000/` — interfaz conversacional, carga de PDF y conexión a Muse Spark.
- `http://127.0.0.1:8000/health` — salud del servidor.
- `GET /api/caso-historico` — datos calculados anonimizados.

El botón de análisis con IA requiere `MODEL_API_KEY` **únicamente como variable de entorno del servidor**, además de autorización y presupuesto de API. El repositorio nunca contiene secretos.

## Pruebas, evidencia y límites

- Tests sin gasto Meta: `tests/` (verificar estado exacto en GitHub Actions).
- Fuente del caso histórico, página 1: pago aproximado de $433.000, pero sumandos $377.000 + $56.300 = $433.300; diferencia no ocultada.
- Propuestas históricas (páginas 2–5): 6,790 / 7,798 / 8,374 / 9,202 UF.
- Típico sesgo evitado: porcentaje alto con tope bajo; se distingue `UF/evento` de `UF/año` y red/sede.
- No presentar porcentajes en Clínica Dávila como garantía actual de convenio; pueden existir condiciones de médicos staff, red y prestaciones.
- La verificación por coincidencia textual no garantiza exactitud de la interpretación, equivalencia integral ni precios vigentes.
- Los datos de catálogo comercial de WordPress no están incluidos; **no** se expone código privado de ALMA ni PDF de terceros.
- No desplegar la ruta de análisis público con Meta sin autenticación, cuotas y revisión de protección de datos.

## Material complementario

- [Evidencias y límites del caso](docs/evidencias-y-limites.md)
- [Guion de video y checklist de entrega](docs/entrega-urgente-hackathon.md)
- [Arquitectura adaptada del taller de Meta](docs/arquitectura-verificacion-meta.md)

## Propiedad y colaboradores

El proyecto del concurso es independiente de los sistemas comerciales existentes. El material del Legal Agent Workshop se utilizó como referencia conceptual y no se copió al repositorio. No se atribuye a ningún colaborador no confirmado. La licencia de reutilización pública del código está pendiente de decisión de la titular; la publicación del repositorio no concede por sí sola derechos de reutilización.
