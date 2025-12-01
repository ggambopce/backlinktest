from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int
    message: str
    result: Optional[Any] = None
