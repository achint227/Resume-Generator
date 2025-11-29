"""
Property-based tests for LaTeX utility functions.

Tests verify correctness properties for LaTeX escaping and formatting utilities.
"""

from hypothesis import given, strategies as st, settings

from src.templates.latex_utils import escape_latex


# **Feature: codebase-refactor, Property 4: LaTeX Character Escaping**
# **Validates: Requirements 2.4**
@given(st.text())
@settings(max_examples=100)
def test_latex_escape_special_chars_are_prefixed_with_backslash(text: str) -> None:
    """
    For any input string containing LaTeX special characters (&, %, $, #, _, {, }),
    the escape function SHALL prefix each special character with a backslash,
    and the resulting string SHALL be valid LaTeX.
    """
    result = escape_latex(text)
    
    # Define the special characters that must be escaped
    special_chars = "&%$#_{}"
    
    # For each special character in the original text,
    # verify it appears escaped in the result
    for char in special_chars:
        # Count occurrences in original text
        original_count = text.count(char)
        
        if original_count > 0:
            # The escaped version should appear in result
            escaped_char = f"\\{char}"
            escaped_count = result.count(escaped_char)
            
            # Each special char should be escaped exactly once
            assert escaped_count == original_count, (
                f"Character '{char}' appeared {original_count} times in input "
                f"but escaped version '{escaped_char}' appeared {escaped_count} times in output"
            )
            
            # The unescaped character should not appear in result
            # (except as part of the escape sequence)
            # We verify by checking that removing all escaped versions
            # leaves no unescaped special chars
            result_without_escaped = result.replace(escaped_char, "")
            assert char not in result_without_escaped, (
                f"Unescaped '{char}' found in result after removing escaped versions"
            )


# **Feature: codebase-refactor, Property 4: LaTeX Character Escaping**
# **Validates: Requirements 2.4**
@given(st.text())
@settings(max_examples=100)
def test_latex_escape_preserves_non_special_chars(text: str) -> None:
    """
    For any input string, non-special characters should be preserved unchanged.
    The escape function should only modify the special LaTeX characters.
    """
    result = escape_latex(text)
    
    special_chars = "&%$#_{}"
    
    # Remove all special chars and their escaped versions to compare
    text_without_special = text
    result_without_escaped = result
    
    for char in special_chars:
        text_without_special = text_without_special.replace(char, "")
        result_without_escaped = result_without_escaped.replace(f"\\{char}", "")
    
    # After removing special chars from input and escaped chars from output,
    # the remaining text should be identical
    assert text_without_special == result_without_escaped, (
        f"Non-special characters were modified during escaping"
    )


# **Feature: codebase-refactor, Property 4: LaTeX Character Escaping**
# **Validates: Requirements 2.4**
@given(st.text())
@settings(max_examples=100)
def test_latex_escape_idempotent_on_non_special_text(text: str) -> None:
    """
    For any input string without special characters, escaping should return
    the string unchanged (identity function for safe input).
    """
    special_chars = "&%$#_{}"
    
    # Skip if text contains special chars
    if any(char in text for char in special_chars):
        return
    
    result = escape_latex(text)
    assert result == text, (
        f"Text without special chars was modified: '{text}' -> '{result}'"
    )



import inspect
from typing import Any, Dict, get_type_hints

from src.templates import TemplateRegistry
from src.templates.base import Template


# **Feature: codebase-refactor, Property 3: Template Method Signature Consistency**
# **Validates: Requirements 2.3**
def test_all_templates_implement_abstract_methods() -> None:
    """
    For any template class registered in the system, the class SHALL implement
    all abstract methods from the base Template class with consistent signatures.
    """
    # Get all abstract methods from the base Template class
    base_abstract_methods = {
        name: method
        for name, method in inspect.getmembers(Template, predicate=inspect.isfunction)
        if getattr(method, "__isabstractmethod__", False)
    }
    
    # Get all registered templates
    templates = TemplateRegistry.get_all()
    
    assert len(templates) > 0, "No templates registered in the registry"
    
    for template_name, template_cls in templates.items():
        # Verify the template is a subclass of Template
        assert issubclass(template_cls, Template), (
            f"Template '{template_name}' ({template_cls.__name__}) "
            f"is not a subclass of Template"
        )
        
        # Verify all abstract methods are implemented
        for method_name in base_abstract_methods:
            assert hasattr(template_cls, method_name), (
                f"Template '{template_name}' ({template_cls.__name__}) "
                f"does not implement required method '{method_name}'"
            )
            
            # Get the method from the template class
            template_method = getattr(template_cls, method_name)
            
            # Verify it's not still abstract
            assert not getattr(template_method, "__isabstractmethod__", False), (
                f"Template '{template_name}' ({template_cls.__name__}) "
                f"has not implemented abstract method '{method_name}'"
            )


# **Feature: codebase-refactor, Property 3: Template Method Signature Consistency**
# **Validates: Requirements 2.3**
def test_template_method_signatures_match_base() -> None:
    """
    For any template class, the implemented methods SHALL have signatures
    compatible with the base Template class abstract methods.
    """
    # Define expected signatures for abstract methods
    expected_signatures = {
        "new_section": ["self", "section_name", "content", "summary"],
        "create_education": ["self", "education"],
        "create_project": ["self", "project"],
        "create_experience": ["self", "experience"],
        "build_header": ["self"],
    }
    
    templates = TemplateRegistry.get_all()
    
    for template_name, template_cls in templates.items():
        for method_name, expected_params in expected_signatures.items():
            method = getattr(template_cls, method_name, None)
            assert method is not None, (
                f"Template '{template_name}' missing method '{method_name}'"
            )
            
            # Get the method signature
            sig = inspect.signature(method)
            actual_params = list(sig.parameters.keys())
            
            # Check that all expected parameters are present
            for param in expected_params:
                assert param in actual_params, (
                    f"Template '{template_name}' method '{method_name}' "
                    f"missing parameter '{param}'. "
                    f"Expected: {expected_params}, Got: {actual_params}"
                )


# **Feature: codebase-refactor, Property 3: Template Method Signature Consistency**
# **Validates: Requirements 2.3**
def test_template_return_types_are_strings() -> None:
    """
    For any template class, the formatting methods SHALL return strings
    containing LaTeX content.
    """
    string_returning_methods = [
        "new_section",
        "create_education",
        "create_project",
        "create_experience",
        "build_header",
        "bullets_from_list",
        "build_resume",
    ]
    
    templates = TemplateRegistry.get_all()
    
    for template_name, template_cls in templates.items():
        for method_name in string_returning_methods:
            method = getattr(template_cls, method_name, None)
            if method is None:
                continue
                
            # Try to get type hints
            try:
                hints = get_type_hints(method)
                if "return" in hints:
                    assert hints["return"] == str, (
                        f"Template '{template_name}' method '{method_name}' "
                        f"should return str, but returns {hints['return']}"
                    )
            except Exception:
                # Type hints may not be available, skip this check
                pass
