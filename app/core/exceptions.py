class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EmailNotFoundException(AppException):
    """Raised when an email cannot be found."""

    def __init__(self, email_id: str):
        super().__init__(
            message=f"Email '{email_id}' was not found.",
            status_code=404,
        )


class AgentRunException(AppException):
    """Raised when the agent workflow fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
        )