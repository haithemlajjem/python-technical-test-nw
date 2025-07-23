from fastapi import HTTPException


class BusinessLogicException(HTTPException):
    """
    Base class for business rule violations.
    """

    def __init__(self, status_code: int = 400, detail: str = "Business logic error"):
        super().__init__(status_code=status_code, detail=detail)
