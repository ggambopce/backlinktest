from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette import status

from app.schemas.common import ApiResponse


class BusinessException(Exception):
    def __init__(self, code: int, message: str, http_status: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.http_status = http_status


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.http_status,
            content=ApiResponse(
                code=exc.code,
                message=exc.message,
                result=None,
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # FastAPI 기본 HTTPException도 ApiResponse로 감싸기
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                code=exc.status_code,
                message=exc.detail,
                result=None,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # 예상 못한 500 에러도 통일된 포맷으로
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(
                code=500,
                message="서버 오류입니다.",
                result=None,
            ).model_dump(),
        )
