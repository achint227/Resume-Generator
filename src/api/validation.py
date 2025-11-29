"""
Input validation module for API requests.

This module provides validation functions for API input parameters,
raising ValidationError for invalid inputs.

Requirements: 4.1
"""

from typing import Any, Dict, List, Optional

from src.exceptions import ValidationError


def validate_order(order: str) -> bool:
    """Validate the section order parameter.
    
    The order parameter must be a 3-character string containing
    exactly the characters 'p', 'w', and 'e' (in any order).
    
    Args:
        order: The order string to validate.
        
    Returns:
        True if the order is valid.
        
    Raises:
        ValidationError: If the order is invalid.
    """
    if not isinstance(order, str):
        raise ValidationError(
            field="order",
            message="Order must be a string",
            value=str(type(order).__name__),
        )
    
    if len(order) != 3:
        raise ValidationError(
            field="order",
            message="Order must be exactly 3 characters",
            value=order,
        )
    
    if set(order) != {"p", "w", "e"}:
        raise ValidationError(
            field="order",
            message="Order must contain exactly 'p', 'w', and 'e'",
            value=order,
        )
    
    return True


def validate_resume_data(data: Optional[Dict[str, Any]]) -> List[str]:
    """Validate resume data and return list of errors.
    
    Validates that the resume data contains all required fields
    with appropriate types.
    
    Args:
        data: The resume data dictionary to validate.
        
    Returns:
        List of validation error messages (empty if valid).
        
    Raises:
        ValidationError: If data is None or not a dictionary.
    """
    if data is None:
        raise ValidationError(
            field="body",
            message="Request body is required",
        )
    
    if not isinstance(data, dict):
        raise ValidationError(
            field="body",
            message="Request body must be a JSON object",
            value=str(type(data).__name__),
        )
    
    errors: List[str] = []
    
    # Validate basic_info
    basic_info = data.get("basic_info")
    if not basic_info:
        errors.append("basic_info is required")
    elif not isinstance(basic_info, dict):
        errors.append("basic_info must be an object")
    else:
        # Validate required fields in basic_info
        if not basic_info.get("name"):
            errors.append("basic_info.name is required")
        if not basic_info.get("email"):
            errors.append("basic_info.email is required")
    
    # Validate education (optional but must be list if present)
    education = data.get("education")
    if education is not None and not isinstance(education, list):
        errors.append("education must be an array")
    
    # Validate experiences (optional but must be list if present)
    experiences = data.get("experiences")
    if experiences is not None and not isinstance(experiences, list):
        errors.append("experiences must be an array")
    
    # Validate projects (optional but must be list if present)
    projects = data.get("projects")
    if projects is not None and not isinstance(projects, list):
        errors.append("projects must be an array")
    
    # Validate keywords (optional but must be list if present)
    keywords = data.get("keywords")
    if keywords is not None and not isinstance(keywords, list):
        errors.append("keywords must be an array")
    
    return errors


def validate_resume_data_strict(data: Optional[Dict[str, Any]]) -> None:
    """Validate resume data and raise ValidationError if invalid.
    
    This is a stricter version that raises an exception instead of
    returning a list of errors.
    
    Args:
        data: The resume data dictionary to validate.
        
    Raises:
        ValidationError: If any validation errors are found.
    """
    errors = validate_resume_data(data)
    if errors:
        raise ValidationError(
            field="body",
            message="; ".join(errors),
        )


def validate_template_name(template: str, valid_templates: List[str]) -> bool:
    """Validate that a template name is valid.
    
    Args:
        template: The template name to validate.
        valid_templates: List of valid template names.
        
    Returns:
        True if the template is valid.
        
    Raises:
        ValidationError: If the template is invalid.
    """
    if not isinstance(template, str):
        raise ValidationError(
            field="template",
            message="Template must be a string",
            value=str(type(template).__name__),
        )
    
    if template not in valid_templates:
        raise ValidationError(
            field="template",
            message=f"Invalid template. Valid options: {', '.join(valid_templates)}",
            value=template,
        )
    
    return True


def validate_resume_id(resume_id: str) -> bool:
    """Validate that a resume ID is valid.
    
    Args:
        resume_id: The resume ID to validate.
        
    Returns:
        True if the ID is valid.
        
    Raises:
        ValidationError: If the ID is invalid.
    """
    if not isinstance(resume_id, str):
        raise ValidationError(
            field="id",
            message="Resume ID must be a string",
            value=str(type(resume_id).__name__),
        )
    
    if not resume_id or not resume_id.strip():
        raise ValidationError(
            field="id",
            message="Resume ID cannot be empty",
        )
    
    return True


__all__ = [
    "validate_order",
    "validate_resume_data",
    "validate_resume_data_strict",
    "validate_template_name",
    "validate_resume_id",
]
