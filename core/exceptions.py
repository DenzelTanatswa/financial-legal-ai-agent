"""
Domain-specific exceptions for the Financial & Legal AI Agent Platform.

Hierarchy:
    AppError (base)
    ├── DocumentError
    │   ├── UnsupportedFileTypeError
    │   ├── FileTooLargeError
    │   ├── PathTraversalError
    │   └── TextExtractionError
    ├── ClassificationError
    ├── AnalysisError
    │   ├── AgentError
    │   └── ValidationError
    └── ConfigurationError
"""
from __future__ import annotations


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


# ── Document errors ──────────────────────────────────────────────────────────

class DocumentError(AppError):
    """Raised for any document-level failure."""

    def __init__(self, message: str, code: str = "DOCUMENT_ERROR") -> None:
        super().__init__(message, code)


class UnsupportedFileTypeError(DocumentError):
    """Raised when an uploaded file extension is not supported."""

    def __init__(self, extension: str) -> None:
        super().__init__(
            f"File type '{extension}' is not supported. "
            "Accepted formats: PDF, DOCX, TXT, CSV, XLSX.",
            code="UNSUPPORTED_FILE_TYPE",
        )
        self.extension = extension


class FileTooLargeError(DocumentError):
    """Raised when an uploaded file exceeds the configured size limit."""

    def __init__(self, size_mb: float, limit_mb: float) -> None:
        super().__init__(
            f"File size {size_mb:.1f} MB exceeds the maximum allowed size of {limit_mb:.1f} MB.",
            code="FILE_TOO_LARGE",
        )
        self.size_mb = size_mb
        self.limit_mb = limit_mb


class PathTraversalError(DocumentError):
    """Raised when a file path attempts to escape the upload directory."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Access denied: path '{path}' is outside the permitted upload directory.",
            code="PATH_TRAVERSAL",
        )
        self.path = path


class TextExtractionError(DocumentError):
    """Raised when text cannot be extracted from a document."""

    def __init__(self, filename: str, reason: str = "") -> None:
        detail = f" Reason: {reason}" if reason else ""
        super().__init__(
            f"Could not extract text from '{filename}'.{detail}",
            code="TEXT_EXTRACTION_FAILED",
        )
        self.filename = filename


# ── Classification errors ────────────────────────────────────────────────────

class ClassificationError(AppError):
    """Raised when document classification fails."""

    def __init__(self, message: str = "Document classification failed.") -> None:
        super().__init__(message, code="CLASSIFICATION_ERROR")


# ── Analysis errors ──────────────────────────────────────────────────────────

class AnalysisError(AppError):
    """Raised when the analysis pipeline fails."""

    def __init__(self, message: str, code: str = "ANALYSIS_ERROR") -> None:
        super().__init__(message, code)


class AgentError(AnalysisError):
    """Raised when a specialist agent fails to produce a valid response."""

    def __init__(self, agent_name: str, reason: str = "") -> None:
        detail = f" Reason: {reason}" if reason else ""
        super().__init__(
            f"Agent '{agent_name}' failed to complete analysis.{detail}",
            code="AGENT_ERROR",
        )
        self.agent_name = agent_name


class ValidationError(AnalysisError):
    """Raised when the validation layer rejects an agent response."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            f"Response validation failed.{' ' + reason if reason else ''}",
            code="VALIDATION_ERROR",
        )


# ── Configuration errors ─────────────────────────────────────────────────────

class ConfigurationError(AppError):
    """Raised when required configuration or environment variables are missing."""

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Missing required configuration: '{key}'. "
            "Check your .env file.",
            code="CONFIGURATION_ERROR",
        )
        self.key = key
