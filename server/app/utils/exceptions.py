"""Domain exceptions mapped to HTTP status codes by the API layer."""
from __future__ import annotations


class PipelineError(Exception):
    """Base class for all recoverable pipeline errors."""

    status_code: int = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EmptyDataError(PipelineError):
    """Raised when an uploaded file has no parseable data."""

    status_code = 400


class FileTooLargeError(PipelineError):
    """Raised when an upload exceeds the configured size limit."""

    status_code = 413


class UnsupportedFileTypeError(PipelineError):
    """Raised when a file extension/content type is not allowed."""

    status_code = 415


class MalformedDataError(PipelineError):
    """Raised when the CSV body cannot be parsed at all."""

    status_code = 422


class InvalidConfigError(PipelineError):
    """Raised when a requested strategy/method is unknown."""

    status_code = 422
