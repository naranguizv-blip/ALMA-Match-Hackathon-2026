# ALMA Match — Meta Global AI Developer Hackathon 2026

Proyecto independiente de Mejora Isapre. **No incluye código de ALMA comercial ni datos privados de la Biblioteca de WordPress.**

## Estado de la versión 0.5
- Interfaz local para subir un PDF de prueba.
- Servidor FastAPI que envía el archivo a Meta Model API para extracción estructurada.
- Resultado en JSON, con fuente y estado **extraído por IA, pendiente de revisión**.
- Cinco pruebas locales de validación realizadas con éxito antes de subir el código.
- **No hay llamada real a Meta verificada desde esta versión**, ni cálculo de precios, ni motor comparador, ni despliegue público.

## Prueba local (Python 3.11+)
```sh
python -m venv .venv
# Activar .venv según tu sistema
pip install -r requirements.txt
# Configurar MODEL_API_KEY solo como variable de entorno del servidor local
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Abre http://127.0.0.1:8000 . Pruebas: `python -m pytest -q`.

## Seguridad
No publicar claves Meta, documentación privada, contratos de pacientes ni datos de clientes. Este servidor aún no tiene autenticación ni límites de uso y **no debe exponerse a Internet**. Solo usar documentos de prueba sin datos personales.

## Próximos pasos
1. Probar una llamada real a Meta con una clave almacenada de forma privada.
2. Integrar extracción con la interfaz conversacional v0.4.
3. Agregar un comparador determinista de cobertura con un catálogo de muestra autorizado, excluyendo la isapre actual.
4. No confundir topes por evento y por año; no inventar tarifas ni ahorros.
5. Seleccionar licencia, probar y preparar presentación del Hackathon.

**Repositorio privado. Licencia de código abierto pendiente de elección consciente.**
