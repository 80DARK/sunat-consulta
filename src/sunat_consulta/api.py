from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status

from .client import SunatClient
from .exceptions import (
    SunatCaptchaRequired,
    SunatError,
    SunatNotFound,
    SunatResponseChanged,
    SunatUpstreamError,
    SunatValidationError,
)
from .models import (
    ConsultaDniRequest,
    ConsultaResponse,
    ConsultaRucRequest,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.sunat_client = SunatClient()
    yield
    await app.state.sunat_client.close()


app = FastAPI(
    title="SUNAT Consulta API",
    version="0.1.0",
    description="API local para consultas de RUC y DNI.",
    lifespan=lifespan,
)


def get_client(request: Request) -> SunatClient:
    return request.app.state.sunat_client


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/dni", response_model=ConsultaResponse)
async def consultar_dni(
    body: ConsultaDniRequest,
    request: Request,
) -> ConsultaResponse:
    client = get_client(request)

    try:
        return await client.consultar_dni(
            dni=body.dni,
            token=body.token,
            ruc_preferido=body.ruc_preferido,
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


@app.post("/v1/ruc", response_model=ConsultaResponse)
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