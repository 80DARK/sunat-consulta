# sunat-consulta

Cliente Python y API FastAPI para consultar datos publicos de SUNAT por RUC o
DNI usando el flujo web de SUNAT.

> Proyecto no oficial. SUNAT puede cambiar su HTML o requerir codigo de
> seguridad; este paquete no evita captchas ni se salta restricciones.

## Instalacion

Para usarlo como modulo:

```bash
pip install -e .
```

Para usarlo tambien como API:

```bash
pip install -e ".[api]"
```

Para desarrollo y tests:

```bash
pip install -e ".[api,dev]"
```

## Uso como modulo

```python
import asyncio

from sunat_consulta import SunatClient


async def main() -> None:
    async with SunatClient() as client:
        result = await client.consultar_ruc(
            ruc="20100070970",
            token="TOKEN_MANUAL",
        )
        print(result.model_dump(mode="json"))


asyncio.run(main())
```

Tambien puedes consultar por DNI:

```python
result = await client.consultar_dni(
    dni="08532482",
    token="TOKEN_MANUAL",
)
```

Si SUNAT devuelve varios RUC para el mismo DNI, el cliente consulta todos y los
retorna en `data_items`.

## Uso como API

Levanta el servidor:

```bash
uvicorn sunat_consulta_api.app:app --reload
```

O usa el comando instalado:

```bash
sunat-consulta-api
```

Endpoints:

- `GET /health`
- `POST /v1/ruc`
- `POST /v1/dni`

Ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/v1/ruc \
  -H "Content-Type: application/json" \
  -d "{\"ruc\":\"20100070970\",\"token\":\"TOKEN_MANUAL\"}"
```

Para consultar por DNI mediante la API:

```bash
curl -X POST http://127.0.0.1:8000/v1/dni \
  -H "Content-Type: application/json" \
  -d "{\"dni\":\"08532482\",\"token\":\"TOKEN_MANUAL\"}"
```

## Estructura

```text
src/
  sunat_consulta/      # libreria importable
  sunat_consulta_api/  # wrapper FastAPI
example/              # ejemplos de uso
test/                 # pruebas unitarias
```

## Tests

```bash
pytest
```

## Nota

El parametro `token` debe venir del flujo manual que SUNAT espera. Este
proyecto solo organiza la consulta y el parseo de respuestas publicas.
