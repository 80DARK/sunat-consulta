# Contribuir

1. Crea un entorno virtual.
2. Instala el proyecto con dependencias de desarrollo:

```bash
pip install -e ".[api,dev]"
```

3. Ejecuta las pruebas antes de enviar cambios:

```bash
pytest
```

Mantén separadas estas dos capas:

- `sunat_consulta`: cliente, modelos, validadores y parsers.
- `sunat_consulta_api`: FastAPI y entrada HTTP.
