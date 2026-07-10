from datetime import datetime

from pydantic import BaseModel, Field


class SunatErrorDetail(BaseModel):
    code: str
    message: str


class DniCandidate(BaseModel):
    ruc: str
    nombre: str
    ubicacion: str | None = None
    estado: str | None = None


class Historico(BaseModel):
    razon_social: list[dict[str, str]] = Field(default_factory=list)
    condicion: list[dict[str, str]] = Field(default_factory=list)
    domicilio: list[dict[str, str]] = Field(default_factory=list)


class SunatData(BaseModel):
    ruc: str
    principal: dict[str, str] = Field(default_factory=dict)
    historico: Historico = Field(default_factory=Historico)
    trabajadores: list[dict[str, str]] = Field(default_factory=list)
    anexos: list[dict[str, str]] = Field(default_factory=list)
    representantes: list[dict[str, str]] = Field(default_factory=list)


class ConsultaResponse(BaseModel):
    ok: bool
    source: str = "sunat_web"
    queried_at: datetime
    data: SunatData | None = None
    data_items: list[SunatData] = Field(default_factory=list)
    candidates: list[DniCandidate] = Field(default_factory=list)
    error: SunatErrorDetail | None = None


class ConsultaDniRequest(BaseModel):
    dni: str
    token: str = Field(min_length=1)


class ConsultaRucRequest(BaseModel):
    ruc: str
    token: str = Field(min_length=1)
