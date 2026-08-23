"""Custom exceptions with structured error responses."""
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception with error code."""
    def __init__(self, status_code: int, detail: str, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundException(APIException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} '{identifier}' not found",
            code="NOT_FOUND"
        )


class ValidationException(APIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code="VALIDATION_ERROR"
        )


class UnauthorizedException(APIException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED"
        )