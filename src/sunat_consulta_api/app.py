from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status

from sunat_consulta import SunatClient
from sunat_consulta.exceptions import (
    SunatCaptchaRequired,
    SunatError,
    SunatNotFound,
    SunatResponseChanged,
    SunatUpstreamError,
    SunatValidationError,
)
from sunat_consulta.models import (
    ConsultaDniRequest,
    ConsultaResponse,
    ConsultaRucRequest,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.sunat_client = SunatClient()
    yield
    await app.state.sunat_client.close()


def create_app() -> FastAPI:
    api = FastAPI(
        title="SUNAT Consulta API",
        version="0.1.0",
        description="API local para consultas de RUC y DNI.",
        lifespan=lifespan,
    )

    api.add_api_route("/health", health, methods=["GET"])
    api.add_api_route(
        "/v1/dni",
        consultar_dni,
        methods=["POST"],
        response_model=ConsultaResponse,
    )
    api.add_api_route(
        "/v1/ruc",
        consultar_ruc,
        methods=["POST"],
        response_model=ConsultaResponse,
    )

    return api


def get_client(request: Request) -> SunatClient:
    return request.app.state.sunat_client


async def health() -> dict[str, str]:
    return {"status": "ok"}


async def consultar_dni(
    body: ConsultaDniRequest,
    request: Request,
) -> ConsultaResponse:
    client = get_client(request)

    try:
        return await client.consultar_dni(
            dni=body.dni,
            token=body.token,
        )

    except SunatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except SunatCaptchaRequired as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except SunatNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except SunatResponseChanged as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except SunatUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except SunatError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


async def consultar_ruc(
    body: ConsultaRucRequest,
    request: Request,
) -> ConsultaResponse:
    client = get_client(request)

    try:
        return await client.consultar_ruc(
            ruc=body.ruc,
            token=body.token,
        )

    except SunatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except SunatCaptchaRequired as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except SunatNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except SunatResponseChanged as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except SunatUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except SunatError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


app = create_app()
