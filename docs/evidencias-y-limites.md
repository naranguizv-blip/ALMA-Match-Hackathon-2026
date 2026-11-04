# Evidencias del prototipo y alcance de las afirmaciones

## A. Contrato auténtico leído por Meta Model API

- Modelo: `muse-spark-1.3`; integración en `backend/meta_client.py`.
- Evidencia reproducible: [GitHub Actions — contrato Esencial CS50400826](https://github.com/naranguizv-blip/ALMA-Match-Hackathon-2026/actions/runs/41368596616).
- La ejecución independiente confirmó recepción, extracción de datos y reconocimiento del código del PDF público.
- No se probó una ejecución completa desde navegador con Muse Spark y una comparación comercial final aprobada. No afirmar lo contrario.
- Verificación de citas por página = correspondencia textual frente al texto PDF extraído; **no** prueba de equivalencia de pólizas ni certeza semántica absoluta.

## B. Caso histórico real anonimizado

**Fuente:** propuesta comercial de nueve páginas aportada por la fundadora para este ensayo; el documento completo contiene identificadores personales, por lo que NO se incorpora a GitHub ni se envía a terceros.

| Dato derivado del original | Valor | Página | Naturaleza |
|---|---:|---|---|
| Isapre original | Nueva Masvida | 1 | Fuente |
| Total de pago mensual declarado | $433.000 | 1 | Aproximado por el cliente |
| Desglose informativo | $377.000 + $56.300 = **$433.300** | 1 | Discrepancia de $300 |
| Tope día cama | 7,4 UF | 1 | Cláusula de prestación |
| Tope medicamentos hospitalarios | **15 UF** | 1 | Por evento en esta fuente; no confundir con otro contrato |
| Tope materiales/insumos | 18 UF | 1 | Según tabla del documento |
| Easy Focus 2 26 | **6,790 UF**, $277.372 | 2 | Precio de propuesta |
| Easy Focus 8 26 | **7,798 UF**, $318.549 | 3 | Precio de propuesta |
| Life Focus 6 26 | **8,374 UF**, $342.078 | 4 | Precio de propuesta |
| Life Focus 215 7 26 | **9,202 UF**, $375.902 | 5 | Precio de propuesta |
| Desglose de hospitalaria/ambulatoria/urgencia por clínica | Variable | 3–6 | Anexos/condiciones sujetos a revisión |

### Cómo se calculan las UF del plan original

El PDF no declara el precio pactado original en UF. Para **visualización aproximada** inferimos un valor CLP/UF de $40.850 a partir de los precios CLP y UF publicados en la misma propuesta (p. ej., $277.372 ÷ 6,790 UF ≈ $40.850). No es una UF oficial fechada.

- Pago total informado aproximado: $433.000 / $40.850 ≈ **10,600 UF**.
- Ahorro mensual aproximado vs. Easy Focus 2: (433.000 / 40.850) − 6,790 ≈ **3,810 UF**.
- Otras alternativas: **2,802**, **2,226** y **1,398 UF** de ahorro mensual aproximado.
- Los cálculos se ejecutan con `decimal.Decimal` y redondeo explícito en `backend/historical_case.py` — no por instrucciones generativas ni por precios inventados.
- El ahorro en CLP es diferencia de valores anotados en la propuesta, **no** ahorro efectivamente contratado.
- Si se utilizara $433.300 en lugar de $433.000, cambiarían las diferencias. El documento no resuelve cuál total representa el pago efectivo: se conserva el informado.

### Cobertura de Clínica Dávila

Las tablas de condiciones en páginas 3 a 6 mencionan porcentajes y modalidades para Dávila/Dávila Vespucio con distinciones por hospitalaria, ambulatoria, urgencia y condiciones de prestadores. El motor no presupone que el porcentaje nominal sea idéntico al contrato original, ni que Dávila integre las mismas redes o beneficios en cada propuesta.

## C. Demostración sin datos privados

Los endpoints `/api/demo-archivo` y `/api/demo-caso/{scenario}` trabajan exclusivamente con contratos **sintéticos inventados** y sin llamada a Meta. Un plan B mejora topes en la misma clínica ficticia; otros se rechazan por tope menor, sede diferente o isapre original. El PDF de demostración no debe confundirse con un contrato de cliente.

## D. Criterios de auditoría del jurado

| Afirmación | Qué la demuestra | Qué no demuestra |
|---|---|---|
| Se usó Meta Muse Spark significativamente | Cliente API en código + ejecución real con PDF | Análisis automático de TODOS los contratos de la demo |
| La extracción tiene control independiente | `verification.py` + casos de prueba sobre citas/páginas | Interpretación médica o contractual correcta garantizada |
| Se comparan topes y clínicas | Motor determinista, pruebas de rechazo | Equivalencia total o convenios vigentes |
| Se puede mostrar un ahorro real potencial | Precio histórico en UF + diferencia reproducible | Cambio contratado, ahorro efectivo o tarifa vigente |
| No se publica información privada | Solo datos anonimizados + escenario ficticio | Que se autorice automáticamente su uso comercial futuro |

**Estado comercial:** prueba técnica para concurso; no cotización vigente, recomendación contractual aprobada ni producto desplegable al público.
