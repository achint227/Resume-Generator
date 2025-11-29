"""
Property-based tests for API layer.

This module contains property-based tests for API input validation
and response format consistency.

Uses Hypothesis for property-based testing with minimum 100 iterations.
"""

import json
from typing import Any, Dict

import pytest
from flask import Flask
from hypothesis import given, settings, strategies as st

from src.api.responses import (
    APIResponse,
    ErrorCodes,
    ErrorDetail,
    error_response,
    not_found_response,
    success_response,
    validation_error_response,
)
from src.api.validation import (
    validate_order,
    validate_resume_data,
    validate_template_name,
)
from src.exceptions import ValidationError


# Strategies for generating test data
valid_order_strategy = st.permutations(["p", "w", "e"]).map(lambda x: "".join(x))

invalid_order_length_strategy = st.text(
    alphabet="pwexyz123", min_size=0, max_size=10
).filter(lambda x: len(x) != 3)

invalid_order_chars_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=3, max_size=3
).filter(lambda x: set(x) != {"p", "w", "e"})


# **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
# **Validates: Requirements 3.3, 4.1**
class TestInvalidAPIInputHandling:
    """Property tests for invalid API input handling.
    
    For any API request with invalid input parameters, the system SHALL
    return an HTTP 4xx status code with a response body containing an
    error message describing the validation failure.
    """

    @settings(max_examples=100)
    @given(invalid_order_length_strategy)
    def test_invalid_order_length_raises_validation_error(self, order: str):
        """Invalid order length should raise ValidationError.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_order(order)
        
        assert exc_info.value.field == "order"
        assert "3 characters" in str(exc_info.value) or "string" in str(exc_info.value)

    @settings(max_examples=100)
    @given(invalid_order_chars_strategy)
    def test_invalid_order_chars_raises_validation_error(self, order: str):
        """Invalid order characters should raise ValidationError.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_order(order)
        
        assert exc_info.value.field == "order"

    @settings(max_examples=100)
    @given(valid_order_strategy)
    def test_valid_order_does_not_raise(self, order: str):
        """Valid order should not raise ValidationError.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        # Should not raise
        result = validate_order(order)
        assert result is True

    @settings(max_examples=100)
    @given(st.none() | st.integers() | st.lists(st.integers()))
    def test_non_dict_resume_data_raises_validation_error(self, data: Any):
        """Non-dict resume data should raise ValidationError.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_resume_data(data)
        
        assert exc_info.value.field == "body"

    @settings(max_examples=100)
    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20).filter(lambda x: x != "basic_info"),
        values=st.text(),
        min_size=0,
        max_size=5,
    ))
    def test_missing_basic_info_returns_error(self, data: Dict[str, Any]):
        """Missing basic_info should return validation errors.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        # Ensure basic_info is not present
        data.pop("basic_info", None)
        
        errors = validate_resume_data(data)
        assert len(errors) > 0
        assert any("basic_info" in error for error in errors)

    @settings(max_examples=100)
    @given(st.text(min_size=1, max_size=20).filter(lambda x: x not in ["classic", "moderncv", "resume", "russel"]))
    def test_invalid_template_raises_validation_error(self, template: str):
        """Invalid template name should raise ValidationError.
        
        **Feature: codebase-refactor, Property 6: Invalid API Input Handling**
        **Validates: Requirements 3.3, 4.1**
        """
        valid_templates = ["classic", "moderncv", "resume", "russel"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_template_name(template, valid_templates)
        
        assert exc_info.value.field == "template"
        assert template == exc_info.value.value


# **Feature: codebase-refactor, Property 7: API Response Format Consistency**
# **Validates: Requirements 4.2, 4.3**
class TestAPIResponseFormatConsistency:
    """Property tests for API response format consistency.
    
    For any API endpoint response (success or error), the response body
    SHALL contain a consistent structure with at minimum a success indicator
    and either data or error information.
    """

    @settings(max_examples=100)
    @given(st.one_of(
        st.none(),
        st.text(),
        st.integers(),
        st.lists(st.text()),
        st.dictionaries(keys=st.text(min_size=1), values=st.text(), max_size=5),
    ))
    def test_success_response_has_consistent_format(self, data: Any):
        """Success responses should have consistent format.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        response = success_response(data)
        response_dict = response.to_dict()
        
        # Must have success indicator
        assert "success" in response_dict
        assert response_dict["success"] is True
        
        # Must have data if provided
        if data is not None:
            assert "data" in response_dict
            assert response_dict["data"] == data
        
        # Should not have error
        assert "error" not in response_dict or response_dict.get("error") is None

    @settings(max_examples=100)
    @given(
        st.text(min_size=1, max_size=100),
        st.sampled_from([
            ErrorCodes.VALIDATION_ERROR,
            ErrorCodes.NOT_FOUND,
            ErrorCodes.DATABASE_ERROR,
            ErrorCodes.TEMPLATE_ERROR,
            ErrorCodes.INTERNAL_ERROR,
        ]),
    )
    def test_error_response_has_consistent_format(self, message: str, code: str):
        """Error responses should have consistent format.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        response = error_response(message=message, code=code)
        response_dict = response.to_dict()
        
        # Must have success indicator
        assert "success" in response_dict
        assert response_dict["success"] is False
        
        # Must have error information
        assert "error" in response_dict
        error = response_dict["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == code
        assert error["message"] == message

    @settings(max_examples=100)
    @given(
        st.text(min_size=1, max_size=50),
        st.text(min_size=1, max_size=100),
    )
    def test_validation_error_response_has_field_info(self, field: str, message: str):
        """Validation error responses should include field information.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        response = validation_error_response(field=field, message=message)
        response_dict = response.to_dict()
        
        # Must have success indicator
        assert "success" in response_dict
        assert response_dict["success"] is False
        
        # Must have error with field info
        assert "error" in response_dict
        error = response_dict["error"]
        assert error["code"] == ErrorCodes.VALIDATION_ERROR
        assert error["field"] == field

    @settings(max_examples=100)
    @given(
        st.text(min_size=1, max_size=30),
        st.text(min_size=1, max_size=50),
    )
    def test_not_found_response_has_resource_info(self, resource: str, identifier: str):
        """Not found responses should include resource information.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        response = not_found_response(resource=resource, identifier=identifier)
        response_dict = response.to_dict()
        
        # Must have success indicator
        assert "success" in response_dict
        assert response_dict["success"] is False
        
        # Must have error with not found code
        assert "error" in response_dict
        error = response_dict["error"]
        assert error["code"] == ErrorCodes.NOT_FOUND
        
        # Should have details with resource info
        assert "details" in error
        assert error["details"]["resource"] == resource
        assert error["details"]["identifier"] == identifier

    @settings(max_examples=100)
    @given(st.one_of(
        st.none(),
        st.text(),
        st.integers(),
        st.lists(st.text()),
        st.dictionaries(keys=st.text(min_size=1), values=st.text(), max_size=5),
    ))
    def test_api_response_is_json_serializable(self, data: Any):
        """All API responses should be JSON serializable.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        # Test success response
        success = success_response(data)
        success_json = json.dumps(success.to_dict())
        assert success_json is not None
        
        # Test error response
        error = error_response(message="test error", code=ErrorCodes.INTERNAL_ERROR)
        error_json = json.dumps(error.to_dict())
        assert error_json is not None

    @settings(max_examples=100)
    @given(
        st.booleans(),
        st.one_of(st.none(), st.text(), st.integers()),
    )
    def test_api_response_dataclass_consistency(self, success: bool, data: Any):
        """APIResponse dataclass should maintain consistency.
        
        **Feature: codebase-refactor, Property 7: API Response Format Consistency**
        **Validates: Requirements 4.2, 4.3**
        """
        if success:
            response = APIResponse(success=True, data=data)
        else:
            response = APIResponse(
                success=False,
                error=ErrorDetail(code="TEST", message="test")
            )
        
        response_dict = response.to_dict()
        
        # Success indicator must always be present
        assert "success" in response_dict
        assert response_dict["success"] == success
