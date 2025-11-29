# Custom exceptions for the Resume Generator application
"""
This module provides domain-specific exceptions for error handling.

Exception Hierarchy:
    ResumeGeneratorError (base)
    ├── ResumeNotFoundError
    ├── DatabaseError
    ├── TemplateError
    │   └── LaTeXCompilationError
    ├── ValidationError
    └── ConfigurationError
"""

from typing import Optional


class ResumeGeneratorError(Exception):
    """Base exception for Resume Generator.
    
    All domain-specific exceptions inherit from this class to allow
    catching all application errors with a single except clause.
    """
    pass


class ResumeNotFoundError(ResumeGeneratorError):
    """Raised when a resume is not found.
    
    Attributes:
        identifier: The ID or name used to look up the resume.
    """
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Resume not found: {identifier}")


class DatabaseError(ResumeGeneratorError):
    """Raised when a database operation fails.
    
    Attributes:
        operation: The database operation that failed (e.g., 'insert', 'update', 'query').
        details: Additional context about the failure.
    """
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[str] = None):
        self.operation = operation
        self.details = details
        full_message = message
        if operation:
            full_message = f"Database {operation} failed: {message}"
        if details:
            full_message = f"{full_message} - {details}"
        super().__init__(full_message)


class TemplateError(ResumeGeneratorError):
    """Raised when template rendering fails.
    
    Attributes:
        template_name: The name of the template that failed.
        section: The section being rendered when the error occurred.
    """
    def __init__(self, message: str, template_name: Optional[str] = None, section: Optional[str] = None):
        self.template_name = template_name
        self.section = section
        full_message = message
        if template_name:
            full_message = f"Template '{template_name}' error: {message}"
        if section:
            full_message = f"{full_message} (section: {section})"
        super().__init__(full_message)


class LaTeXCompilationError(TemplateError):
    """Raised when LaTeX compilation fails.
    
    Attributes:
        stderr: The stderr output from the LaTeX compiler.
        exit_code: The exit code from the LaTeX process.
    """
    def __init__(self, message: str, stderr: str = "", exit_code: Optional[int] = None):
        self.stderr = stderr
        self.exit_code = exit_code
        full_message = f"LaTeX compilation failed: {message}"
        if exit_code is not None:
            full_message = f"{full_message} (exit code: {exit_code})"
        # Call TemplateError.__init__ but skip the template_name/section formatting
        ResumeGeneratorError.__init__(self, full_message)


class ValidationError(ResumeGeneratorError):
    """Raised when input validation fails.
    
    Attributes:
        field: The field that failed validation.
        value: The invalid value (optional, may be omitted for security).
    """
    def __init__(self, field: str, message: str, value: Optional[str] = None):
        self.field = field
        self.value = value
        full_message = f"Validation error for '{field}': {message}"
        super().__init__(full_message)


class ConfigurationError(ResumeGeneratorError):
    """Raised when configuration is invalid or missing.
    
    Attributes:
        config_key: The configuration key that is invalid or missing.
    """
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.config_key = config_key
        full_message = message
        if config_key:
            full_message = f"Configuration error for '{config_key}': {message}"
        super().__init__(full_message)


# Export all exceptions
__all__ = [
    "ResumeGeneratorError",
    "ResumeNotFoundError", 
    "DatabaseError",
    "TemplateError",
    "LaTeXCompilationError",
    "ValidationError",
    "ConfigurationError",
]
