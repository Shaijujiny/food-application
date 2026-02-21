from app.core.error.error_types import ErrorType


def get_http_status(error_type: ErrorType) -> int:
    return int(error_type.name.split("_")[1])