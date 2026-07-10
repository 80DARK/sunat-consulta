from __future__ import annotations

from bs4 import BeautifulSoup

from .models import DniCandidate, Historico


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def parse_hidden_value(soup: BeautifulSoup, name: str) -> str | None:
    element = soup.find("input", {"name": name})

    if element is None:
        return None

    value = element.get("value") or ""
    return value.strip() or None


def is_sunat_error_page(soup: BeautifulSoup) -> bool:
    text = soup.get_text(" ", strip=True).lower()

    messages = (
        "ingrese el código mostrado",
        "código de seguridad",
        "codigo de seguridad",
        "sesión ha expirado",
        "sesion ha expirado",
        "ha ocurrido un error",
        "no se pudo procesar",
    )

    return any(message in text for message in messages)


def parse_dni_candidates(soup: BeautifulSoup) -> list[DniCandidate]:
    candidates: list[DniCandidate] = []

    for item in soup.select("a.aRucs[data-ruc]"):
        ruc = clean_text(item.get("data-ruc"))
        headings = item.select("h4.list-group-item-heading")

        nombre = ""
        if len(headings) >= 2:
            nombre = clean_text(headings[1].get_text(" ", strip=True))

        ubicacion = None
        estado = None

        for paragraph in item.select("p.list-group-item-text"):
            text = clean_text(paragraph.get_text(" ", strip=True))
            normalized = text.lower()

            if normalized.startswith("ubicación:"):
                ubicacion = clean_text(text.split(":", 1)[1])
            elif normalized.startswith("ubicacion:"):
                ubicacion = clean_text(text.split(":", 1)[1])
            elif normalized.startswith("estado:"):
                estado = clean_text(text.split(":", 1)[1])

        if ruc and nombre:
            candidates.append(
                DniCandidate(
                    ruc=ruc,
                    nombre=nombre,
                    ubicacion=ubicacion,
                    estado=estado,
                )
            )

    return candidates


def parse_principal(soup: BeautifulSoup) -> dict[str, str]:
    principal: dict[str, str] = {}

    for row in soup.select("div.row"):
        headings = row.select("h4.list-group-item-heading")

        if not headings:
            continue

        title = clean_text(headings[0].get_text(" ", strip=True)).rstrip(":")
        value_element = row.select_one("p.list-group-item-text")

        if value_element is None and len(headings) > 1:
            value_element = headings[1]

        if not title or value_element is None:
            continue

        value = clean_text(value_element.get_text(" ", strip=True))

        if value:
            principal[title] = value

    return principal


def parse_razon_social(
    soup: BeautifulSoup,
    principal: dict[str, str],
) -> str:
    razon_social = parse_hidden_value(soup, "desRuc")

    if razon_social:
        return razon_social

    ruc_line = principal.get("Número de RUC", "")

    if "-" in ruc_line:
        return clean_text(ruc_line.split("-", 1)[1])

    return ""


def parse_table(soup: BeautifulSoup) -> list[dict[str, str]]:
    table = soup.select_one("table.table")

    if table is None:
        return []

    headers = [
        clean_text(th.get_text(" ", strip=True))
        for th in table.select("thead th")
    ]

    if not headers:
        headers = [
            clean_text(th.get_text(" ", strip=True))
            for th in table.select("tr:first-child th")
        ]

    rows: list[dict[str, str]] = []

    for tr in table.select("tbody tr"):
        columns = [
            clean_text(td.get_text(" ", strip=True))
            for td in tr.select("td")
        ]

        if not columns:
            continue

        first_column = columns[0].lower()

        if "no existen" in first_column or "no hay" in first_column:
            continue

        if headers and len(headers) == len(columns):
            rows.append(dict(zip(headers, columns)))
        else:
            rows.append(
                {
                    f"columna_{index + 1}": value
                    for index, value in enumerate(columns)
                }
            )

    return rows


def parse_historico(soup: BeautifulSoup) -> Historico:
    tables = soup.select("table.table")
    historico = Historico()

    if len(tables) < 3:
        return historico

    for tr in tables[0].select("tbody tr"):
        columns = [
            clean_text(td.get_text(" ", strip=True))
            for td in tr.select("td")
        ]

        if len(columns) == 2 and "no hay" not in columns[0].lower():
            historico.razon_social.append(
                {
                    "nombre": columns[0],
                    "baja": columns[1],
                }
            )

    for tr in tables[1].select("tbody tr"):
        columns = [
            clean_text(td.get_text(" ", strip=True))
            for td in tr.select("td")
        ]

        if len(columns) == 3 and columns[0] != "-":
            historico.condicion.append(
                {
                    "condicion": columns[0],
                    "desde": columns[1],
                    "hasta": columns[2],
                }
            )

    for tr in tables[2].select("tbody tr"):
        columns = [
            clean_text(td.get_text(" ", strip=True))
            for td in tr.select("td")
        ]

        if len(columns) == 2 and columns[0] != "-":
            historico.domicilio.append(
                {
                    "direccion": columns[0],
                    "baja": columns[1],
                }
            )

    return historico