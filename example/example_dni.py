import argparse
import asyncio
import json
import os
import sys

from sunat_consulta import SunatClient
from sunat_consulta.exceptions import SunatError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consulta SUNAT por DNI usando el paquete importable.",
    )
    parser.add_argument(
        "dni",
        nargs="?",
        default=os.getenv("SUNAT_DNI"),
        help="DNI a consultar. Tambien puedes usar SUNAT_DNI.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("SUNAT_TOKEN"),
        help="Token vigente de SUNAT. Tambien puedes usar SUNAT_TOKEN.",
    )

    args = parser.parse_args()

    if not args.dni:
        parser.error("indica un DNI o define SUNAT_DNI")

    if not args.token:
        parser.error("indica --token o define SUNAT_TOKEN")

    return args


async def main() -> None:
    args = parse_args()

    async with SunatClient() as client:
        try:
            result = await client.consultar_dni(
                dni=args.dni,
                token=args.token,
            )

            print(json.dumps(
                result.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            ))

        except SunatError as exc:
            print(json.dumps(
                {
                    "ok": False,
                    "error": {
                        "type": exc.__class__.__name__,
                        "message": str(exc),
                    },
                },
                indent=2,
                ensure_ascii=False,
            ))


if __name__ == "__main__":
    asyncio.run(main())
