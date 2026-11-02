# ALMA Match — Hackathon Meta 2026 (versión 0.6)

Prototipo independiente de Mejora Isapre / ALMA comercial. **Repositorio de desarrollo: privado.** Enfocado en demostrar lectura de contratos con IA y comparación de coberturas basada en documentos, sin duplicar ni exponer la Biblioteca de WordPress.

## Qué está implementado

- Interfaz visual conservando la línea gráfica v0.4, sin barra lateral de pasos.
- Captura de edad, cargas, **isapre actual**, pactado en **UF**, pago actual y solo **renta imponible** para estimar el 7 %.
- Lectura de PDF nuevo con **Muse Spark** vía servidor FastAPI, sin clave API en el navegador.
- Comparador determinista con catálogo reducido de **seis** extractos Banmédica (datos recopilados previamente por la usuaria), que no se presentan como verificados para contratación.
- Excluye planes de la isapre actual y bloquea comparación si el PDF corresponde a otra isapre distinta de la que indicó el cliente.
- Resultado con plan actual, hasta tres alternativas documentales, clínica por clínica, hospitalaria, ambulatoria y urgencias, más desplegables.
- No ofrece ahorro ni cotización si faltan precio base, factores, GES y la UF aplicable.
- La demostración precargada permite ver el recorrido sin hacer otra llamada a Meta.
- **11 pruebas automatizadas locales aprobadas** (sin consumir créditos de Meta).

## Qué está realmente comprobado

Una ejecución independiente de GitHub Actions confirmó que **Muse Spark 1.3 leyó el PDF público CS50400826** y extrajo datos estructurados. Esta nueva aplicación v0.6 combina el mismo tipo de llamada con un comparador de muestra. **Todavía no se ha ensayado en un navegador la experiencia completa con una nueva lectura de Meta**: el test del endpoint emplea una respuesta simulada para no gastar créditos.

La extracción de ejemplo es un resumen de una lectura previa del contrato. La IA no verifica por sí sola sus resultados. Los seis extractos Banmédica tampoco equivalen a cotizaciones ni a una revisión contractual final. No se publican PDF de terceros.

## Ejecutar en un equipo de desarrollo

Python 3.11+:

```sh
python -m venv .venv
# activar entorno y luego:
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000` y pulsar **Ver demo ya analizada** para comprobar la comparación sin créditos.

Para procesar un PDF nuevo, configura `MODEL_API_KEY` exclusivamente como variable local del servidor. No agregues claves a GitHub ni al JavaScript. Solo utilizar documentos públicos y sin datos personales.

Pruebas sin coste de API:

```sh
python -m pytest -q
```

## Límites y próximos pasos

- Pendientes precios y factores vigentes, GES, verificación exhaustiva por prestación y cálculo financiero real.
- Contrastar contra los PDF originales las condiciones resumidas de Banmédica.
- La extracción dinámica de nuevos documentos requiere una llamada real a Meta (consume créditos). El flujo de demostración precargada no.
- Este prototipo no envía formularios de contacto ni modifica WordPress.
- **No desplegar públicamente** el servidor antes de agregar autenticación, cuotas, protección frente a abuso y evaluación de privacidad.
- Revisar licencia de código abierto y derechos de publicación antes de cambiar el repositorio a público.