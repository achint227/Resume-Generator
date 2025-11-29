"""
API response models for consistent response formatting.

This module provides standardized response structures for all API endpoints,
ensuring consistent response formats across the application.

Requirements: 4.2, 4.3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ErrorDetail:
    """Detailed error information for API error responses.
    
    Attributes:
        code: A machine-readable error code (e.g., 'VALIDATION_ERROR').
        message: A human-readable error message.
        field: The field that caused the error (for validation errors).
        details: Additional context about the error.
    """
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.field is not None:
            result["field"] = self.field
        if self.details is not None:
            result["details"] = self.details
        return result


@dataclass
class APIResponse:
    """Standard API response structure.
    
    All API responses follow this consistent format with a success indicator
    and either data (for successful responses) or error information.
    
    Attributes:
        success: Whether the request was successful.
        data: The response data (for successful responses).
        error: Error information (for failed responses).
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error.to_dict()
        return result


@dataclass
class ErrorResponse:
    """Convenience class for creating error responses.
    
    Attributes:
        message: The error message.
        code: The error code.
        field: The field that caused the error (optional).
        details: Additional error details (optional).
    """
    message: str
    code: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_api_response(self) -> APIResponse:
        """Convert to an APIResponse object."""
        return APIResponse(
            success=False,
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                field=self.field,
                details=self.details,
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.to_api_response().to_dict()


# Error codes
class ErrorCodes:
    """Standard error codes for API responses."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    TEMPLATE_ERROR = "TEMPLATE_ERROR"
    LATEX_ERROR = "LATEX_COMPILATION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Response factory functions
def success_response(data: Any = None) -> APIResponse:
    """Create a successful API response.
    
    Args:
        data: The response data.
        
    Returns:
        APIResponse with success=True and the provided data.
    """
    return APIResponse(success=True, data=data)


def error_response(
    message: str,
    code: str = ErrorCodes.INTERNAL_ERROR,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> APIResponse:
    """Create an error API response.
    
    Args:
        message: The error message.
        code: The error code.
        field: The field that caused the error (optional).
        details: Additional error details (optional).
        
    Returns:
        APIResponse with success=False and error information.
    """
    return APIResponse(
        success=False,
        error=ErrorDetail(
            code=code,
            message=message,
            field=field,
            details=details,
        )
    )


def validation_error_response(
    field: str,
    message: str,
    value: Optional[Any] = None,
) -> APIResponse:
    """Create a validation error response.
    
    Args:
        field: The field that failed validation.
        message: Description of the validation failure.
        value: The invalid value (optional).
        
    Returns:
        APIResponse with validation error information.
    """
    details = None
    if value is not None:
        details = {"value": value}
    
    return error_response(
        message=message,
        code=ErrorCodes.VALIDATION_ERROR,
        field=field,
        details=details,
    )


def not_found_response(resource: str, identifier: str) -> APIResponse:
    """Create a not found error response.
    
    Args:
        resource: The type of resource that was not found.
        identifier: The identifier used to look up the resource.
        
    Returns:
        APIResponse with not found error information.
    """
    return error_response(
        message=f"{resource} not found: {identifier}",
        code=ErrorCodes.NOT_FOUND,
        details={"resource": resource, "identifier": identifier},
    )


__all__ = [
    "APIResponse",
    "ErrorResponse",
    "ErrorDetail",
    "ErrorCodes",
    "success_response",
    "error_response",
    "validation_error_response",
    "not_found_response",
]
