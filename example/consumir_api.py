import argparse
import asyncio
import json
import os
import sys

import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume la API local de SUNAT Consulta.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("SUNAT_API_URL", "http://127.0.0.1:8000"),
        help="URL base de la API. Ejemplo: http://127.0.0.1:8922",
    )
    parser.add_argument(
        "--dni",
        default=os.getenv("SUNAT_DNI"),
        help="DNI a consultar. Tambien puedes usar SUNAT_DNI.",
    )
    parser.add_argument(
        "--ruc",
        default=os.getenv("SUNAT_RUC"),
        help="RUC a consultar. Tambien puedes usar SUNAT_RUC.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("SUNAT_TOKEN"),
        help="Token vigente de SUNAT. Tambien puedes usar SUNAT_TOKEN.",
    )

    args = parser.parse_args()

    if bool(args.dni) == bool(args.ruc):
        parser.error("indica exactamente uno: --dni o --ruc")

    if not args.token:
        parser.error("indica --token o define SUNAT_TOKEN")

    return args


async def health_check(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    response.raise_for_status()

    print("Health:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def consultar_ruc(
    client: httpx.AsyncClient,
    ruc: str,
    token: str,
) -> None:
    response = await client.post(
        "/v1/ruc",
        json={
            "ruc": ruc,
            "token": token,
        },
    )

    print(f"Consulta RUC | HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def consultar_dni(
    client: httpx.AsyncClient,
    dni: str,
    token: str,
) -> None:
    response = await client.post(
        "/v1/dni",
        json={
            "dni": dni,
            "token": token,
        },
    )

    print(f"Consulta DNI | HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()


async def main() -> None:
    args = parse_args()
    timeout = httpx.Timeout(60.0)

    async with httpx.AsyncClient(
        base_url=args.base_url,
        timeout=timeout,
    ) as client:
        try:
            await health_check(client)

            if args.dni:
                await consultar_dni(client, args.dni, args.token)
            else:
                await consultar_ruc(client, args.ruc, args.token)

        except httpx.ConnectError:
            print(
                "No se pudo conectar a FastAPI. "
                "Levanta primero el servidor con uvicorn."
            )

        except httpx.HTTPError as exc:
            print(f"Error HTTP al consumir la API: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
