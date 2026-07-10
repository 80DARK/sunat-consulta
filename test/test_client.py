import asyncio
import inspect
from types import SimpleNamespace

from sunat_consulta.client import SunatClient
from sunat_consulta.models import ConsultaDniRequest, SunatData


def test_consultar_dni_public_api_does_not_require_preferred_ruc():
    parameters = inspect.signature(SunatClient.consultar_dni).parameters

    assert "ruc_preferido" not in parameters
    assert "ruc_preferido" not in ConsultaDniRequest.model_fields


def test_consultar_dni_fetches_all_ruc_candidates(monkeypatch):
    async def run_test():
        client = SunatClient()
        detail_calls: list[tuple[str, str]] = []
        session_calls = 0

        async def fake_post(data):
            assert "ruc_preferido" not in data
            return SimpleNamespace(
                text="""
                <input name="numRnd" value="ABC123">
                <a class="aRucs" data-ruc="10085324824">
                    <h4 class="list-group-item-heading">RUC</h4>
                    <h4 class="list-group-item-heading">JUAN PEREZ QUISPE</h4>
                    <p class="list-group-item-text">Ubicacion: LIMA</p>
                    <p class="list-group-item-text">Estado: ACTIVO</p>
                </a>
                <a class="aRucs" data-ruc="10444555666">
                    <h4 class="list-group-item-heading">RUC</h4>
                    <h4 class="list-group-item-heading">JUAN PEREZ Q.</h4>
                    <p class="list-group-item-text">Ubicacion: CALLAO</p>
                    <p class="list-group-item-text">Estado: ACTIVO</p>
                </a>
                """,
            )

        async def fake_ensure_session():
            nonlocal session_calls
            session_calls += 1

        async def fake_consultar_detalle_ruc(ruc: str, num_rnd: str):
            detail_calls.append((ruc, num_rnd))
            return SunatData(ruc=ruc, principal={"Número de RUC": ruc})

        monkeypatch.setattr(client, "_post", fake_post)
        monkeypatch.setattr(client, "_ensure_session", fake_ensure_session)
        monkeypatch.setattr(
            client,
            "_consultar_detalle_ruc",
            fake_consultar_detalle_ruc,
        )

        try:
            result = await client.consultar_dni(
                dni="08532482",
                token="TOKEN",
            )
        finally:
            await client.close()

        assert detail_calls == [
            ("10085324824", "ABC123"),
            ("10444555666", "ABC123"),
        ]
        assert result.data is None
        assert [item.ruc for item in result.data_items] == [
            "10085324824",
            "10444555666",
        ]
        assert session_calls == 1

    asyncio.run(run_test())
