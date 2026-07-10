"""Compatibilidad con la ruta antigua de la API.

La aplicación FastAPI vive en :mod:`sunat_consulta_api.app`. Este módulo se
mantiene para que `uvicorn sunat_consulta.api:app` siga funcionando.
"""

from sunat_consulta_api.app import app, create_app

__all__ = ["app", "create_app"]
