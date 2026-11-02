# ALMA Match: estado y entrega Hackathon 2026

## Trabajo nuevo desarrollado en el Hackathon (desde el 26 de octubre)

- Backend FastAPI + Muse Spark: lectura de PDF auténtico comprobada con GitHub Actions, independiente de WordPress.
- Frontend conversacional v0.6; comparaciones ilustrativas separadas de decisiones verificadas.
- **Nuevo verificador v0.7:** cotejo determinista de fragmentos citados contra el texto extraído por página del mismo PDF; aborta comparación si faltan hospitalaria, ambulatoria, urgencia, clínicas o topes.
- **Bloqueo comercial v0.7:** solo admitir planes individuales con comercialización registrada y **coberturas + topes + revisión para comparación aprobadas**.
- Fórmulas del 7 % en condiciones de simulación, sin emitir cotización ni ahorro contractual.
- El JSON del modelo **no** se considera verificado automáticamente.
- El validador literal no verifica por sí solo la interpretación semántica: solo afirma que la cadena citada existe en esa página.
- Para PDF escaneado sin capa de texto legible, el flujo se detiene y ofrece revisión; fotografías/OCR no disponibles en v0.7.
- Sin secretos ni PDFs protegidos de terceros en el repositorio. El material del Legal Agent Workshop se usó solo como inspiración metodológica.

## Fuentes y validación

El catálogo reducido conserva seis códigos Banmédica cuyo corte 202608 consta como **individual y "Si Comer."** en el archivo de la Superintendencia aportado \`Planes_de_Salud_202608.txt\`. Esto **no acredita su vigencia en noviembre ni valida automáticamente los topes**. Las seis coberturas siguen pendientes de contrastarse contra PDF y, hasta entonces, el comparador no las recomendará.

El contrato real Esencial \`CS50400826\` fue leído por Muse Spark 1.3 en una ejecución independiente. La extracción JSON precargada de v0.6 contiene resúmenes, no citas literales verificadas: con el nuevo validador queda bloqueada por falta de correspondencia. Es un resultado correcto, no una avería.

## Probar sin gasto de Meta

\`\`\`bash
pip install -r requirements.txt
python -m pytest -q
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
\`\`\`

Las pruebas usan PDF ficticio elaborado para test y llamadas Muse simuladas. Para analizar un PDF real desde la aplicación se requiere \`MODEL_API_KEY\` configurada **solo en el servidor** y una ejecución autorizada con créditos disponibles.

## Pendientes críticos para entregar

1. Validar un conjunto reducido de documentos/coberturas por clínica, prestación, periodicidad y tope, preferiblemente mediante casos ficticios comprobables y fuentes permitidas; marcar explícitamente lo real versus simulado.
2. Probar flujo completo de subida → Muse → verificador → comparación/denegación. **No está demostrado de extremo a extremo con Meta desde navegador**.
3. Confirmar información de comercialización del periodo relevante; no usar agosto 2026 como demostración automática de vigencia en noviembre.
4. Elegir caso que permita una alternativa explicable y un caso fallido por tope/red diferente; si faltan datos de precios, ocultar ahorro.
5. Auditar el código a publicar (sin WordPress privado, ni llaves ni PDFs de terceros), licencia propia y requisitos oficiales.
6. Video funcional de 3 minutos; repositorio público; realizar entrega oficial antes del 4/11 21:00 ET (23:00 Chile).

## Fuera de alcance hasta después del concurso

No integrar WhatsApp, CRM, cotizador WordPress, miles de planes, fotografía/OCR, precios finales y derivación operativa de clientes. Solo se permite consentimiento explícito al ofrecer contacto; la demo no envía información de clientes.
