from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup

from .exceptions import (
    SunatCaptchaRequired,
    SunatError,
    SunatNotFound,
    SunatResponseChanged,
    SunatUpstreamError,
    SunatValidationError,
)
from .models import ConsultaResponse, SunatData
from .parsers import (
    is_sunat_error_page,
    parse_dni_candidates,
    parse_hidden_value,
    parse_historico,
    parse_principal,
    parse_razon_social,
    parse_table,
)
from .validators import validate_dni, validate_ruc


class SunatClient:
    URL = (
        "https://e-consultaruc.sunat.gob.pe/"
        "cl-ti-itmrconsruc/jcrS00Alias"
    )

    def __init__(self, timeout: float = 25.0) -> None:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers={
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "es-PE,es;q=0.9",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://e-consultaruc.sunat.gob.pe",
                "Referer": self.URL,
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
                ),
            },
        )

    async def __aenter__(self) -> "SunatClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def consultar_dni(
        self,
        dni: str,
        token: str,
        ruc_preferido: str | None = None,
    ) -> ConsultaResponse:
        dni = validate_dni(dni)
        token = token.strip()

        if not token:
            raise SunatValidationError("El token no puede estar vacío.")

        payload = {
            "accion": "consPorTipdoc",
            "razSoc": "",
            "nroRuc": "",
            "nrodoc": dni,
            "token": token,
            "contexto": "ti-it",
            "modo": "1",
            "search1": "",
            "rbtnTipo": "2",
            "tipdoc": "1",
            "search2": dni,
            "search3": "",
            "codigo": "",
        }

        response = await self._post(payload)
        soup = BeautifulSoup(response.text, "html.parser")

        self._raise_if_rejected(soup)

        candidates = parse_dni_candidates(soup)

        if not candidates:
            raise SunatNotFound(
                f"No se encontró un contribuyente asociado al DNI {dni}."
            )

        num_rnd = parse_hidden_value(soup, "numRnd")

        if not num_rnd:
            raise SunatResponseChanged(
                "SUNAT no devolvió numRnd para continuar con el detalle del RUC."
            )

        if ruc_preferido:
            ruc_preferido = validate_ruc(ruc_preferido)
            candidates = [
                item for item in candidates
                if item.ruc == ruc_preferido
            ]

            if not candidates:
                raise SunatNotFound(
                    "El RUC indicado no pertenece a los resultados del DNI."
                )

        data_items: list[SunatData] = []

        for candidate in candidates:
            try:
                detail = await self._consultar_detalle_ruc(
                    ruc=candidate.ruc,
                    num_rnd=num_rnd,
                )
                data_items.append(detail)
            except SunatError:
                continue

        if not data_items:
            raise SunatUpstreamError(
                "SUNAT devolvió RUC asociados al DNI, pero no fue posible obtener sus detalles."
            )

        return ConsultaResponse(
            ok=True,
            queried_at=datetime.now(timezone.utc),
            data=data_items[0] if len(data_items) == 1 else None,
            data_items=data_items,
            candidates=candidates,
        )

    async def consultar_ruc(
        self,
        ruc: str,
        token: str,
    ) -> ConsultaResponse:
        ruc = validate_ruc(ruc)
        token = token.strip()

        if not token:
            raise SunatValidationError("El token no puede estar vacío.")

        payload = {
            "accion": "consPorRuc",
            "razSoc": "",
            "nroRuc": ruc,
            "nrodoc": "",
            "token": token,
            "contexto": "ti-it",
            "modo": "1",
            "rbtnTipo": "1",
            "search1": ruc,
            "tipdoc": "1",
            "search2": "",
            "search3": "",
            "codigo": "",
        }

        response = await self._post(payload)
        soup = BeautifulSoup(response.text, "html.parser")

        self._raise_if_rejected(soup)

        principal = parse_principal(soup)

        if not principal:
            raise SunatNotFound(
                f"No se encontró información para el RUC {ruc}."
            )

        data = await self._build_extended_data(
            ruc=ruc,
            principal=principal,
            soup=soup,
        )

        return ConsultaResponse(
            ok=True,
            queried_at=datetime.now(timezone.utc),
            data=data,
        )

    async def _consultar_detalle_ruc(
        self,
        ruc: str,
        num_rnd: str,
    ) -> SunatData:
        payload = {
            "accion": "consPorRuc",
            "actReturn": "1",
            "nroRuc": ruc,
            "numRnd": num_rnd,
            "modo": "1",
        }

        response = await self._post(payload)
        soup = BeautifulSoup(response.text, "html.parser")

        self._raise_if_rejected(soup)

        principal = parse_principal(soup)

        if not principal:
            raise SunatResponseChanged(
                "SUNAT no devolvió el detalle esperado del RUC."
            )

        return await self._build_extended_data(
            ruc=ruc,
            principal=principal,
            soup=soup,
        )

    async def _build_extended_data(
        self,
        ruc: str,
        principal: dict[str, str],
        soup: BeautifulSoup,
    ) -> SunatData:
        data = SunatData(
            ruc=ruc,
            principal=principal,
        )

        razon_social = parse_razon_social(soup, principal)

        if not razon_social:
            return data

        data.historico = await self._consultar_historico(
            ruc=ruc,
            razon_social=razon_social,
        )

        data.trabajadores = await self._consultar_tabla(
            action="getCantTrab",
            ruc=ruc,
            razon_social=razon_social,
        )
        data.anexos = await self._consultar_tabla(
            action="getLocAnex",
            ruc=ruc,
            razon_social=razon_social,
        )
        data.representantes = await self._consultar_tabla(
            action="getRepLeg",
            ruc=ruc,
            razon_social=razon_social,
        )

        return data

    async def _consultar_historico(
        self,
        ruc: str,
        razon_social: str,
    ):
        response = await self._post(
            {
                "accion": "getinfHis",
                "contexto": "ti-it",
                "modo": "1",
                "nroRuc": ruc,
                "desRuc": razon_social,
            }
        )

        soup = BeautifulSoup(response.text, "html.parser")
        return parse_historico(soup)

    async def _consultar_tabla(
        self,
        action: str,
        ruc: str,
        razon_social: str,
    ) -> list[dict[str, str]]:
        response = await self._post(
            {
                "accion": action,
                "contexto": "ti-it",
                "modo": "1",
                "nroRuc": ruc,
                "desRuc": razon_social,
            }
        )

        soup = BeautifulSoup(response.text, "html.parser")
        return parse_table(soup)

    async def _post(self, data: dict[str, Any]) -> httpx.Response:
        try:
            response = await self._client.post(self.URL, data=data)
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as exc:
            raise SunatUpstreamError(
                f"SUNAT respondió HTTP {exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise SunatUpstreamError(
                "No fue posible comunicarse con SUNAT."
            ) from exc

    @staticmethod
    def _raise_if_rejected(soup: BeautifulSoup) -> None:
        if not is_sunat_error_page(soup):
            return

        text = soup.get_text(" ", strip=True).lower()

        if (
            "código de seguridad" in text
            or "codigo de seguridad" in text
            or "ingrese el código mostrado" in text
        ):
            raise SunatCaptchaRequired(
                "SUNAT rechazó el código de seguridad o requiere uno válido."
            )

        raise SunatResponseChanged(
            "SUNAT devolvió una página no compatible con el parser."
        )