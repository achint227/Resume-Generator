# Property-based tests for exception hierarchy
"""
**Feature: codebase-refactor, Property 5: Domain-Specific Exceptions for Database Errors**

Tests that all domain-specific exceptions are proper subclasses of ResumeGeneratorError
and contain appropriate context information.
"""

from hypothesis import given, strategies as st, settings

from src.exceptions import (
    ResumeGeneratorError,
    ResumeNotFoundError,
    DatabaseError,
    TemplateError,
    LaTeXCompilationError,
    ValidationError,
    ConfigurationError,
)


# Strategies for generating test data
identifier_strategy = st.text(min_size=1, max_size=100)
message_strategy = st.text(min_size=1, max_size=500)
operation_strategy = st.sampled_from(["insert", "update", "delete", "query", "connect"])
field_strategy = st.text(alphabet=st.characters(whitelist_categories=("L", "N")), min_size=1, max_size=50)
config_key_strategy = st.text(alphabet=st.characters(whitelist_categories=("L", "N", "P")), min_size=1, max_size=50)


class TestDomainSpecificExceptions:
    """
    **Feature: codebase-refactor, Property 5: Domain-Specific Exceptions for Database Errors**
    **Validates: Requirements 3.1**
    
    Property: For any database operation that fails, the system SHALL raise a subclass 
    of ResumeGeneratorError containing context information about the failure.
    """

    @given(identifier=identifier_strategy)
    @settings(max_examples=100)
    def test_resume_not_found_is_subclass_with_context(self, identifier: str):
        """ResumeNotFoundError is a ResumeGeneratorError subclass with identifier context."""
        exc = ResumeNotFoundError(identifier)
        
        # Must be a subclass of ResumeGeneratorError
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.identifier == identifier
        assert identifier in str(exc)

    @given(message=message_strategy, operation=st.one_of(st.none(), operation_strategy))
    @settings(max_examples=100)
    def test_database_error_is_subclass_with_context(self, message: str, operation):
        """DatabaseError is a ResumeGeneratorError subclass with operation context."""
        exc = DatabaseError(message, operation=operation)
        
        # Must be a subclass of ResumeGeneratorError
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.operation == operation
        if operation:
            assert operation in str(exc)

    @given(
        message=message_strategy,
        template_name=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        section=st.one_of(st.none(), st.sampled_from(["header", "education", "experience", "projects"]))
    )
    @settings(max_examples=100)
    def test_template_error_is_subclass_with_context(self, message: str, template_name, section):
        """TemplateError is a ResumeGeneratorError subclass with template context."""
        exc = TemplateError(message, template_name=template_name, section=section)
        
        # Must be a subclass of ResumeGeneratorError
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.template_name == template_name
        assert exc.section == section
        if template_name:
            assert template_name in str(exc)

    @given(
        message=message_strategy,
        stderr=st.text(max_size=200),
        exit_code=st.one_of(st.none(), st.integers(min_value=1, max_value=255))
    )
    @settings(max_examples=100)
    def test_latex_compilation_error_is_subclass_with_context(self, message: str, stderr: str, exit_code):
        """LaTeXCompilationError is a TemplateError subclass with compilation context."""
        exc = LaTeXCompilationError(message, stderr=stderr, exit_code=exit_code)
        
        # Must be a subclass of both TemplateError and ResumeGeneratorError
        assert isinstance(exc, TemplateError)
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.stderr == stderr
        assert exc.exit_code == exit_code
        assert "LaTeX compilation failed" in str(exc)

    @given(field=field_strategy, message=message_strategy)
    @settings(max_examples=100)
    def test_validation_error_is_subclass_with_context(self, field: str, message: str):
        """ValidationError is a ResumeGeneratorError subclass with field context."""
        exc = ValidationError(field, message)
        
        # Must be a subclass of ResumeGeneratorError
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.field == field
        assert field in str(exc)

    @given(message=message_strategy, config_key=st.one_of(st.none(), config_key_strategy))
    @settings(max_examples=100)
    def test_configuration_error_is_subclass_with_context(self, message: str, config_key):
        """ConfigurationError is a ResumeGeneratorError subclass with config key context."""
        exc = ConfigurationError(message, config_key=config_key)
        
        # Must be a subclass of ResumeGeneratorError
        assert isinstance(exc, ResumeGeneratorError)
        
        # Must contain context information
        assert exc.config_key == config_key
        if config_key:
            assert config_key in str(exc)

    @given(identifier=identifier_strategy)
    @settings(max_examples=100)
    def test_all_exceptions_can_be_caught_by_base_class(self, identifier: str):
        """All domain exceptions can be caught with a single ResumeGeneratorError handler."""
        exceptions = [
            ResumeNotFoundError(identifier),
            DatabaseError("test error"),
            TemplateError("test error"),
            LaTeXCompilationError("test error"),
            ValidationError("field", "test error"),
            ConfigurationError("test error"),
        ]
        
        for exc in exceptions:
            try:
                raise exc
            except ResumeGeneratorError as caught:
                # All should be catchable by base class
                assert caught is exc
            except Exception:
                # Should never reach here
                assert False, f"Exception {type(exc).__name__} not caught by ResumeGeneratorError"
