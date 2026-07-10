import pytest

from sunat_consulta.exceptions import SunatValidationError
from sunat_consulta.validators import validate_dni, validate_ruc


def test_validate_dni_accepts_valid_dni():
    assert validate_dni("08532482") == "08532482"


def test_validate_dni_strips_spaces():
    assert validate_dni(" 08532482 ") == "08532482"


def test_validate_dni_rejects_non_numeric():
    with pytest.raises(SunatValidationError, match="8 dígitos"):
        validate_dni("0853A482")


def test_validate_dni_rejects_invalid_length():
    with pytest.raises(SunatValidationError, match="8 dígitos"):
        validate_dni("1234567")


def test_validate_ruc_accepts_valid_ruc():
    assert validate_ruc("20131312955") == "20131312955"


def test_validate_ruc_strips_spaces():
    assert validate_ruc(" 20131312955 ") == "20131312955"


def test_validate_ruc_rejects_non_numeric():
    with pytest.raises(SunatValidationError, match="11 dígitos"):
        validate_ruc("2013131295A")


def test_validate_ruc_rejects_invalid_length():
    with pytest.raises(SunatValidationError, match="11 dígitos"):
        validate_ruc("2013131295")


def test_validate_ruc_rejects_invalid_verifier():
    with pytest.raises(
        SunatValidationError,
        match="dígito verificador del RUC",
    ):
        validate_ruc("20131312954")