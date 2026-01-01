"""
Custom exception classes.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{id}' not found"
        )


class BadRequestException(HTTPException):
    """Raised when request is invalid."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class ConflictException(HTTPException):
    """Raised when there's a conflict (e.g., duplicate resource)."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class InvalidSwaggerSpecException(HTTPException):
    """Raised when Swagger spec is invalid."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid Swagger specification: {message}"
        )


class GenerationFailedException(HTTPException):
    """Raised when MCP generation fails."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCP generation failed: {message}"
        )
