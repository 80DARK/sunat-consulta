#Si te preguntas por el parametro TOKEN, este en realidad no es valido por
#el backend de SUNAT, pero es necesario para poder usar el paquete importable.
#ya que el backend de SUNAT espera en el payload ese parametro, y si no lo envias,
#el backend de SUNAT devuelve un error 400.


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
        description="Consulta SUNAT por RUC usando el paquete importable.",
    )
    parser.add_argument(
        "ruc",
        nargs="?",
        default=os.getenv("SUNAT_RUC"),
        help="RUC a consultar. Tambien puedes usar SUNAT_RUC.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("SUNAT_TOKEN"),
        help="Token vigente de SUNAT. Tambien puedes usar SUNAT_TOKEN.",
    )

    args = parser.parse_args()

    if not args.ruc:
        parser.error("indica un RUC o define SUNAT_RUC")

    if not args.token:
        parser.error("indica --token o define SUNAT_TOKEN")

    return args


async def main() -> None:
    args = parse_args()

    async with SunatClient() as client:
        try:
            result = await client.consultar_ruc(
                ruc=args.ruc,
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
