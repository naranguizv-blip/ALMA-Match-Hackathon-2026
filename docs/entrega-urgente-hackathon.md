# ALMA Match — cierre de entrega, 3–4 de noviembre de 2026

**Fecha límite informada por la participante:** miércoles 4 de noviembre de 2026, 21:00 ET = 23:00 Chile continental.

**Objetivo:** presentar trabajo nuevo hecho durante el concurso, separado del ALMA de WordPress. No rehacer funcionalidades existentes.

## Estado comprobado

- Repositorio `naranguizv-blip/ALMA-Match-Hackathon-2026` sigue **privado**; principal `main` no incluye aún todas las ramas nuevas.
- Desarrollo de muestra: PR #1 (PDF y Meta), PR #2 (comparador v0.6), PR #3 (verificador v0.7), encadenados; siguen **borradores sin fusionar**.
- GitHub Actions de v0.7: **28 pruebas aprobadas** en ejecución del 2 de noviembre (CI sin llamadas de pago).
- Muse Spark 1.3 **sí analizó un PDF auténtico de Esencial** en una acción independiente. **No** hay prueba demostrada de flujo completo desde navegador `/api/analizar` con Meta real.
- `/api/demo-caso/comparable` y `/api/demo-caso/no_comparable`: escenarios ficticios que prueban topes, red y exclusión de isapre, **sin IA ni catálogo comercial**. Mostrar claramente esa distinción.
- Seis planes Banmédica del corte 202608 en el prototipo: comercialización histórica verificada para ese corte, pero coberturas/topes NO certificados y NO elegibles para presentar recomendaciones.
- Verificador de evidencia por página exige cita literal; el mero match textual no garantiza significado correcto.
- No hay precios finales validados ni ahorro CLP/UF comprobado; no mostrar números de ahorro reales.
- No hay alojamiento público confirmado para aplicación ni video publicado.

## Solo tareas imprescindibles para concursar

**P0. Una sola presentación defendible, NO más módulos:**

1. Unir/revisar las ramas #1–#3 y ejecutar CI final. No mezclar código privado de WordPress.
2. Hacer una demostración de *comportamiento real del prototipo*: mostrar interfaz, un caso ficticio comparable y otro rechazado; apoyar la lectura IA con la evidencia de la acción exitosa de Meta (o con una nueva ejecución autorizada por la usuaria). Ser explícitos cuando algo es simulado.
3. Registrar video de **hasta 3 minutos** en MP4; revisar que se vean texto y barras en móvil y computador y que no aparezca ninguna clave/API ni correo personal. Subir a servicio accesible a los jueces y comprobar permisos.
4. Auditar derechos (licencia del código propio, PDFs de terceros solo si derechos lo permiten; NO incluir Legal Agent Workshop, documentos privados ni datos personales), llaves y `.env`; publicar solo repositorio independiente después de aprobación de la titular.
5. Completar formulario `https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit` con repositorio, video, título, descripción, participantes confirmados y temática. Guardar constancia de envío antes del plazo.

**P1 opcional si sobra tiempo:** validar al menos una alternativa real con contrato/condiciones documentados o prueba integrada Muse desde servidor. Sin esto, declarar que la *comparación comercial real es una capacidad posterior*, no un hecho realizado.

**NO hacer antes del envío:** más de 6–20 planes, precios de clientes, fotografía/OCR, CRM, WhatsApp, Biblioteca WordPress, agente legal completo, SAM, voz, integraciones nuevas.

## Guion de demostración honesto, máximo 3:00

- **0:00–0:20:** «En Chile, entender un contrato de isapre y compararlo con otra oferta requiere revisar redes, prestaciones, urgencias y topes. ALMA Match hace entendible ese análisis.»
- **0:20–0:45:** Mostrar la pantalla de ALMA Match y la carga de documento. Señalar la conexión real a Muse Spark, respaldada por ejecución separada ya probada. **No describir una lectura simulada como si fuera llamada Meta en vivo.**
- **0:45–1:20:** Mostrar ejemplo ficticio A→B: cobertura hospitalaria 80 %→85 %, ambulatoria 70 %→75 %, urgencia 60 %→65 %; misma clínica ficticia y topes 400→450 UF/año, 60→70 UF/año, 5→6 UF/evento. Etiqueta «simulación».
- **1:20–2:00:** Mostrar rechazo del plan C: urgencia 60 % en ambos, pero tope 2 UF/evento vs. 5 UF/evento; D usa otra clínica y E es misma isapre.
- **2:00–2:25:** Mostrar verificación de citas contra página y bloqueo si falla; advertir que coincidencia textual no garantiza interpretación semántica.
- **2:25–2:45:** Mostrar resultado sin plan comparable y sin ahorro inventado cuando faltan precios.
- **2:45–3:00:** «Trabajo nuevo del Hackathon: lectura Meta, motor de comparación y capa independiente de verificación. La integración con ALMA comercial será posterior.»

## Texto breve para presentación

**Título:** ALMA Match — comparación verificable de contratos de isapre

**Resumen (prototipo):** ALMA Match aborda un problema cotidiano en Chile: los porcentajes de cobertura por sí solos no permiten comparar planes de salud. Nuestro prototipo combina lectura de PDF con Muse Spark (Meta Model API), extracción estructurada de coberturas hospitalarias, ambulatorias y de urgencia, y un motor independiente que comprueba citas, clínicas, topes y periodos. En vez de inventar recomendaciones, detiene la comparación cuando faltan evidencias. La demostración incluye escenarios contractuales ficticios, uno comparable y otro descartado, para no exponer datos de clientes. Es código nuevo del Hackathon, separado del sistema comercial ALMA.

**Track sugerido:** Build for Your World.

## Controles y límites importantes

- No utilizar pago ni créditos API sin autorización expresa. No ingresar tarjeta.
- No volver público repositorio sin aprobar licencia y auditoría.
- No ofrecer alternativas comerciales ni afirmar ahorro real usando el catálogo no verificado.
- No presentar «test con Mock» como «flujo completo Meta en navegador».
- No mostrar datos de cliente, secretos GitHub/Meta ni repositorios WordPress.
- Solo incorporar colaborador si está aprobado en el concurso; no atribuir participación automáticamente a terceros.
