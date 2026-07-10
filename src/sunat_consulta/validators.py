import re
from .exceptions import SunatValidationError


def validate_dni(dni: str) -> str:
    dni = dni.strip()

    if not re.fullmatch(r"\d{8}", dni):
        raise SunatValidationError(
            "El DNI debe contener exactamente 8 dígitos."
        )

    return dni


def validate_ruc(ruc: str) -> str:
    ruc = ruc.strip()

    if not re.fullmatch(r"\d{11}", ruc):
        raise SunatValidationError(
            "El RUC debe contener exactamente 11 dígitos."
        )

    factors = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(
        int(digit) * factor
        for digit, factor in zip(ruc[:10], factors)
    )

    verifier = 11 - (total % 11)
    verifier = 0 if verifier == 10 else 1 if verifier == 11 else verifier

    if int(ruc[-1]) != verifier:
        raise SunatValidationError(
            "El dígito verificador del RUC no es válido."
        )

    return ruc