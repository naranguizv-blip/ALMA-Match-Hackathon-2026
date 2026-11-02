# ALMA Match — adaptación técnica del Legal Agent Workshop (Meta, noviembre 2026)

**Ámbito:** exclusivamente el prototipo independiente del Hackathon. No modificar WordPress, ALMA comercial ni la Biblioteca central. Este documento describe decisiones de diseño; **no** certifica que las verificaciones ya estén implementadas.

## Estado comprobado al revisar

- Rama de trabajo: `desarrollo/comparador-visual-v0.6`; pull request borrador #2, repositorio privado.
- `backend/meta_client.py` interpreta PDF mediante Meta Muse Spark y produce JSON con página y evidencia, **sin verificar independientemente la fuente**.
- `backend/main.py` admite PDF, NO imagen/fotografía; prueba extremo a extremo con un modelo simulado, no prueba real de navegador.
- `backend/comparison.py` descarta la misma isapre y no calcula ahorros sin precios confirmados; tiene índice ilustrativo de clínicas/porcentajes y 7% estimado con UF de referencia.
- `backend/catalogo_demo.json` contiene seis extractos de Banmédica. Carecen de estados robustos `comercializacion_verificada`/fecha/corte y no pueden presentarse como oferta.
- `backend/extraccion_demo.json`: campos de "evidencia" resumidos y no citas literales verificadas de la página. No atribuirles calidad de prueba documental.
- Tests v0.6: once pasaron en GitHub Actions, **no** validan la exactitud de las coberturas originales.

## Qué se adopta y qué NO se copia

El ZIP consultado incluye `agent/agent_kit/document_text.py`, `agent/verification/`, `agent/ESCALATION_RULES.md`, `ground_truth/`, `solutions/02_session2/`. Tomar solo **principios de diseño** y escribir código propio: el ZIP no incluye un archivo de licencia explícito.

1. **Evidencia página por página:** hash SHA-256 de archivo, código del plan, fuente, página, fragmento textual exacto y tipo de cobertura. Mantener la interpretación separada de la cita literal.
2. **Reglas fuera de la IA:** validar campos/porcentajes/periodicidad/topes, coherencia hospitalaria–ambulatoria–urgencia, coincidencia de plan y proveedor, y periodo de comercialización.
3. **Lista de referencia independiente:** casos ficticios revisados manualmente contra el PDF; no mostrar esa referencia al modelo. Comparar resultados con esta referencia en tests.
4. **Escalación:** si falta documento, evidencia o precio, dejar el análisis incompleto, solicitar solo el dato imprescindible o proponer revisión humana; no rellenar vacíos.
5. **Trazabilidad:** estado de cada afirmación: `extraida` → `cita_corresponde` → `validacion_reglas` → `revisada`. Evitar la etiqueta global 'verificado' por solo pasar una prueba.

**Advertencias del taller:** su `quote_on_page` compara contra una transcripción generada por IA; esto valida coincidencia con esa transcripción, no exactitud absoluta frente a los píxeles originales. `verify_checklist.py` y `verify_claims.py` usan Muse como juez: evaluación por modelo, no prueba determinista. En la solución del taller, la salida ilegible de `verify_claims.py` incluso se acepta como válida; **ALMA Match debe bloquear resultados cuando falle una verificación**. `check_signatures.py` es un placeholder, no implementar. No portar loop legal completo ni consola jurídica.

## Flujo mínimo de demostración aprobado

`PDF actual ficticio o público`
→ `Muse Spark extrae estructura y evidencia`
→ `validar esquema + página/fragmento + reglas clínicas/topes`
→ `resolver únicamente planes DEMO marcados comercializados y revisados`
→ `excluir isapre actual`
→ `comparar por clínica, hospitalaria, ambulatoria, urgencia y topes`
→ `hasta 3 alternativas DOCUMENTALES o mensaje de evidencia insuficiente`
→ `consentimiento explícito SOLO si se ofrece contacto; no integrar WordPress durante el Hackathon`.

Los porcentajes idénticos no implican equivalencia: considerar prestación, prestador/sede, modalidad, tope, periodo y exclusiones. **Precios, ahorros y contratación** solo con valores finales/fechas/UF/GES/factores confirmados; de lo contrario ocultar el ranking de ahorro.

## Entrega imprescindible P0 (antes del 4 de noviembre, 23:00 Chile)

1. Añadir un verificador de evidencia al resultado de `meta_client.py`/backend sin reconstruirlo: exigir cita y página comprobables, y mostrar `pendiente` si no coinciden. Para PDF escaneado, revisión visual o muestra de referencia humana; no prometer comprobación perfecta.
2. Añadir `comercializado_verificado`, `corte`, `fecha_verificacion`, `fuente` en catálogo pequeño; mostrar **solo** planes con estado afirmativo confirmado contra registros originales. Si no hay ninguno, mostrar cero, nunca alternativas inventadas.
3. Reglas de bloqueo: misma isapre, falta de hospitalaria/ambulatoria/urgencia, redes/topes incompletos, porcentajes o unidades inválidos, ausencia de precio verificable cuando la meta sea ahorro. Resultado claro 'no hay alternativa comparable verificada'.
4. Casos de prueba: (i) extracción correcta, (ii) mismo porcentaje pero distinto tope/red, (iii) dato faltante, (iv) isapre actual, (v) plan no comercializado, (vi) documento dudoso. Distinguir tests unitarios de una demostración real.
5. Grabar un único flujo funcional en video de **3 minutos**, mostrando Meta Muse, evidencia, verificador y alternativa/no-alternativa. Usar datos ficticios y/o PDF público permitido. Evitar datos de clientes.
6. Hacer público únicamente el repositorio de trabajo nuevo, limpiar credenciales, PDF de terceros, material del taller y dependencias. Confirmar reglas y crear envío antes del plazo.

## Fuera de alcance del Hackathon

- Integración real con Biblioteca central WordPress y gestión de 1000+ planes.
- WhatsApp 360dialog, CRM ALMA, consentimiento operativo de derivación, pagos/comisiones.
- Loop autónomo 30 turnos, consola del agente, firmas, segmentación SAM 3.1, sistema multiusuario.
- Precios definitivos o afirmaciones de ahorro sin GES, factores y datos comerciales confirmados.
- Publicar backend sin control de abuso, límites de uso, gestión de secretos y privacidad.

## Fuente interna revisada

`legal-agent-workshop-main.zip` obtenido de la Biblioteca de ChatGPT: `README.md`, `HANDBOOK.md`, `agent/VERIFICATION.md`, `agent/ESCALATION_RULES.md`, `agent/agent_kit/document_text.py`, `agent/agent_kit/case_record.py`, `solutions/02_session2/agent/verification/*`. No se copió código del taller a este repositorio.
