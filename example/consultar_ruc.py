import asyncio
import json

from src.sunat_consulta import SunatClient
from src.sunat_consulta.exceptions import SunatError


RUC = "20100070970"
TOKEN = "REEMPLAZA_CON_TOKEN_NO_VACIO"


async def main() -> None:
    async with SunatClient() as client:
        try:
            result = await client.consultar_ruc(
                ruc=RUC,
                token=TOKEN,
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