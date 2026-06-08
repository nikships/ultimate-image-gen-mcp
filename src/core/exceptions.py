"""
Custom exceptions for the Ultimate Gemini MCP server.
"""


class UltimateGeminiError(Exception):
    """Base exception for all Ultimate Gemini MCP errors."""


class ConfigurationError(UltimateGeminiError):
    """Raised when there's a configuration error."""


class ValidationError(UltimateGeminiError):
    """Raised when input validation fails."""


class APIError(UltimateGeminiError):
    """Raised when an API request fails."""

    def __init__(
        self, message: str, status_code: int | None = None, response_data: dict | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(APIError):
    """Raised when API authentication fails."""


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""


class ContentPolicyError(APIError):
    """Raised when content violates safety policies."""


class ImageProcessingError(UltimateGeminiError):
    """Raised when image processing fails."""


class FileOperationError(UltimateGeminiError):
    """Raised when file operations fail."""
