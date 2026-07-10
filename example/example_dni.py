import asyncio
import json

from sunat_consulta import SunatClient
from sunat_consulta.exceptions import SunatError


DNI = "08532482"
TOKEN = "REEMPLAZA_CON_TOKEN_NO_VACIO"


async def main() -> None:
    async with SunatClient() as client:
        try:
            result = await client.consultar_dni(
                dni=DNI,
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
