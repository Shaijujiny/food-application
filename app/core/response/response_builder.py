from fastapi.responses import JSONResponse
from app.core.response.base_schema import CustomResponse
from app.core.response.status_mapper import get_http_status
from app.core.i18n.message_resolver import MessageResolver


class ResponseBuilder:

    @staticmethod
    def build(
        error_type,
        message_code,
        lang="en",
        data=None
    ):

        status_code = get_http_status(error_type)

        response = CustomResponse(
            status=1 if status_code < 400 else -1,
            error_type=error_type,
            message=MessageResolver.resolve(message_code, lang),
            status_code=status_code,
            data=data
        )

        return JSONResponse(
            status_code=status_code,  # 👈 THIS FIXES YOUR ISSUE
            content=response.model_dump(by_alias=True)
        )