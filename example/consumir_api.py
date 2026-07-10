import asyncio
import json

import httpx


BASE_URL = "http://127.0.0.1:8000"
CAPTCHA_CODE = "REEMPLAZA_CON_CODIGO_MANUAL"
TOKEN = ""


async def health_check(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    response.raise_for_status()

    print("Health:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def consultar_ruc(
    client: httpx.AsyncClient,
    ruc: str,
) -> None:
    response = await client.post(
        "/v1/ruc",
        json={
            "ruc": ruc,
            "captcha_code": CAPTCHA_CODE,
            "token": TOKEN,
        },
    )

    print(f"Consulta RUC | HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def consultar_dni(
    client: httpx.AsyncClient,
    dni: str,
    ruc_preferido: str | None = None,
) -> None:
    payload = {
        "dni": dni,
        "captcha_code": CAPTCHA_CODE,
        "token": TOKEN,
    }

    if ruc_preferido:
        payload["ruc_preferido"] = ruc_preferido

    response = await client.post("/v1/dni", json=payload)

    print(f"Consulta DNI | HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def main() -> None:
    timeout = httpx.Timeout(60.0)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=timeout,
    ) as client:
        try:
            await health_check(client)

            # Descomenta solo la consulta que quieras probar.
            await consultar_ruc(client, "20100070970")

            # await consultar_dni(
            #     client,
            #     dni="08532482",
            # )

            # Ejemplo si el DNI tiene varios RUC:
            # await consultar_dni(
            #     client,
            #     dni="08532482",
            #     ruc_preferido="10085324824",
            # )

        except httpx.ConnectError:
            print(
                "No se pudo conectar a FastAPI. "
                "Levanta primero el servidor con uvicorn."
            )

        except httpx.HTTPError as exc:
            print(f"Error HTTP al consumir la API: {exc}")


if __name__ == "__main__":
    asyncio.run(main())