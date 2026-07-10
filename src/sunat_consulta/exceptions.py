class SunatError(Exception):
    """Error base del cliente SUNAT."""


class SunatValidationError(SunatError):
    """DNI, RUC o parámetros de entrada inválidos."""


class SunatCaptchaRequired(SunatError):
    """SUNAT requiere un código de seguridad válido."""


class SunatNotFound(SunatError):
    """No se encontraron resultados."""


class SunatResponseChanged(SunatError):
    """SUNAT devolvió una página con estructura no compatible."""


class SunatUpstreamError(SunatError):
    """Error de red o error HTTP del servicio SUNAT."""