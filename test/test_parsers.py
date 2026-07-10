from bs4 import BeautifulSoup

from sunat_consulta.parsers import (
    is_sunat_error_page,
    parse_dni_candidates,
    parse_hidden_value,
    parse_historico,
    parse_principal,
    parse_razon_social,
    parse_table,
)


def test_parse_hidden_value_returns_value():
    soup = BeautifulSoup(
        '<input name="numRnd" value="ABC123">',
        "html.parser",
    )

    assert parse_hidden_value(soup, "numRnd") == "ABC123"


def test_parse_hidden_value_returns_none_when_missing():
    soup = BeautifulSoup("<html></html>", "html.parser")

    assert parse_hidden_value(soup, "numRnd") is None


def test_is_sunat_error_page_detects_security_message():
    soup = BeautifulSoup(
        "<html><body>Ingrese el código mostrado</body></html>",
        "html.parser",
    )

    assert is_sunat_error_page(soup) is True


def test_is_sunat_error_page_returns_false_for_normal_html():
    soup = BeautifulSoup(
        "<html><body>Consulta correcta</body></html>",
        "html.parser",
    )

    assert is_sunat_error_page(soup) is False


def test_parse_dni_candidates_extracts_candidates():
    html = """
    <a class="aRucs" data-ruc="10085324824">
        <h4 class="list-group-item-heading">RUC</h4>
        <h4 class="list-group-item-heading">JUAN PEREZ QUISPE</h4>
        <p class="list-group-item-text">Ubicación: LIMA</p>
        <p class="list-group-item-text">Estado: ACTIVO</p>
    </a>
    <a class="aRucs" data-ruc="10444555666">
        <h4 class="list-group-item-heading">RUC</h4>
        <h4 class="list-group-item-heading">JUAN PEREZ Q.</h4>
        <p class="list-group-item-text">Ubicacion: CALLAO</p>
        <p class="list-group-item-text">Estado: BAJA</p>
    </a>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = parse_dni_candidates(soup)

    assert len(result) == 2
    assert result[0].ruc == "10085324824"
    assert result[0].nombre == "JUAN PEREZ QUISPE"
    assert result[0].ubicacion == "LIMA"
    assert result[0].estado == "ACTIVO"
    assert result[1].ubicacion == "CALLAO"


def test_parse_principal_extracts_key_values():
    html = """
    <div class="row">
        <h4 class="list-group-item-heading">Número de RUC:</h4>
        <p class="list-group-item-text">20131312955 - EMPRESA SAC</p>
    </div>
    <div class="row">
        <h4 class="list-group-item-heading">Estado del Contribuyente:</h4>
        <p class="list-group-item-text">ACTIVO</p>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = parse_principal(soup)

    assert result["Número de RUC"] == "20131312955 - EMPRESA SAC"
    assert result["Estado del Contribuyente"] == "ACTIVO"


def test_parse_razon_social_prefers_hidden_value():
    html = """
    <input name="desRuc" value="EMPRESA OCULTA SAC">
    <div class="row">
        <h4 class="list-group-item-heading">Número de RUC:</h4>
        <p class="list-group-item-text">20131312955 - EMPRESA VISIBLE SAC</p>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    principal = parse_principal(soup)

    assert parse_razon_social(soup, principal) == "EMPRESA OCULTA SAC"


def test_parse_razon_social_falls_back_to_principal():
    html = """
    <div class="row">
        <h4 class="list-group-item-heading">Número de RUC:</h4>
        <p class="list-group-item-text">20131312955 - EMPRESA VISIBLE SAC</p>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    principal = parse_principal(soup)

    assert parse_razon_social(soup, principal) == "EMPRESA VISIBLE SAC"


def test_parse_table_extracts_rows():
    html = """
    <table class="table">
        <thead>
            <tr>
                <th>Periodo</th>
                <th>Trabajadores</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>2024-01</td>
                <td>15</td>
            </tr>
            <tr>
                <td>2024-02</td>
                <td>18</td>
            </tr>
        </tbody>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = parse_table(soup)

    assert result == [
        {"Periodo": "2024-01", "Trabajadores": "15"},
        {"Periodo": "2024-02", "Trabajadores": "18"},
    ]


def test_parse_table_skips_empty_notice_rows():
    html = """
    <table class="table">
        <thead>
            <tr>
                <th>Dato</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>No existen registros</td>
            </tr>
        </tbody>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")

    assert parse_table(soup) == []


def test_parse_historico_extracts_three_sections():
    html = """
    <table class="table">
        <tbody>
            <tr><td>RAZON 1</td><td>---</td></tr>
        </tbody>
    </table>
    <table class="table">
        <tbody>
            <tr><td>HABIDO</td><td>01/01/2020</td><td>--</td></tr>
        </tbody>
    </table>
    <table class="table">
        <tbody>
            <tr><td>AV SIEMPRE VIVA 123</td><td>--</td></tr>
        </tbody>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = parse_historico(soup)

    assert result.razon_social == [{"nombre": "RAZON 1", "baja": "---"}]
    assert result.condicion == [
        {"condicion": "HABIDO", "desde": "01/01/2020", "hasta": "--"}
    ]
    assert result.domicilio == [
        {"direccion": "AV SIEMPRE VIVA 123", "baja": "--"}
    ]