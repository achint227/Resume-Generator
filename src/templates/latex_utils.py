"""
LaTeX utility functions for resume template generation.

This module provides shared utility functions for LaTeX processing,
including character escaping, text formatting, and content hashing.
"""

import hashlib
import json
import re
from typing import Any, Dict, List, Optional


def compute_content_hash(data: Dict[str, Any], template: str, order: str) -> str:
    """Compute a hash digest of resume data, template, and order.
    
    Creates a deterministic hash from the resume content, template name,
    and section order to enable caching of generated PDFs.
    
    Args:
        data: Resume data dictionary.
        template: Template name string.
        order: Section order string (e.g., 'pwe').
        
    Returns:
        First 8 characters of SHA256 hex digest.
    """
    content = json.dumps(data, sort_keys=True) + template + order
    return hashlib.sha256(content.encode()).hexdigest()[:8]


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in a string.
    
    Prefixes LaTeX special characters (&, %, $, #, _, {, }) with
    a backslash to prevent LaTeX compilation errors.
    
    Args:
        text: Input string that may contain special characters.
        
    Returns:
        String with special characters escaped for LaTeX.
    """
    return re.sub(r"([&%$#_{}])", r"\\\1", text)


def escape_latex_recursive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively apply LaTeX escaping to dictionary values.
    
    Traverses a dictionary structure and escapes all string values
    for safe use in LaTeX documents.
    
    Args:
        data: Dictionary potentially containing nested dicts, lists, and strings.
        
    Returns:
        Dictionary with all string values escaped for LaTeX.
    """
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = escape_latex(value)
        elif isinstance(value, dict):
            escape_latex_recursive(value)
        elif isinstance(value, list):
            data[key] = [
                escape_latex_recursive(i)
                if isinstance(i, dict)
                else [escape_latex_recursive(x) if isinstance(x, dict) else escape_latex(x) if isinstance(x, str) else x for x in i]
                if isinstance(i, list)
                else escape_latex(i)
                if isinstance(i, str)
                else i
                for i in value
            ]
    return data


def make_bold(text: str, keywords: Optional[List[str]] = None) -> str:
    """Make specified words bold in LaTeX format.
    
    Wraps occurrences of keywords in the text with LaTeX \\textbf{} command.
    Matching is case-insensitive but preserves original case in output.
    
    Args:
        text: Input string to process.
        keywords: List of words to make bold. If None or empty, returns text unchanged.
        
    Returns:
        String with keywords wrapped in \\textbf{} commands.
    """
    if not keywords:
        return text
    for word in keywords:
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", flags=re.IGNORECASE)
        for match in pattern.finditer(text):
            start, end = match.span()
            word_case = text[start:end]
            text = text[:start] + "\\textbf{" + word_case + "}" + text[end:]
    return text


def split_string(s: str, sep: str = " ") -> str:
    """Split string and wrap each part in braces for LaTeX.
    
    Useful for LaTeX commands that expect multiple arguments in braces,
    such as \\name{First}{Last}.
    
    Args:
        s: Input string to split.
        sep: Separator character(s) to split on. Defaults to space.
        
    Returns:
        String with each part wrapped in braces, e.g., "{First}{Last}".
    """
    return "{" + "}{".join([part.strip() for part in s.split(sep)]) + "}"


def format_bullet_list(
    items: List[str], 
    keywords: Optional[List[str]] = None,
    item_command: str = "\\item"
) -> str:
    """Format a list of items as LaTeX bullet points.
    
    Creates a LaTeX itemize environment with each item as a bullet point.
    Optionally applies keyword bolding to item text.
    
    Args:
        items: List of strings to format as bullet points.
        keywords: Optional list of words to make bold in items.
        item_command: LaTeX command for items. Defaults to "\\item".
        
    Returns:
        LaTeX itemize environment string, or empty string if items is empty.
    """
    if not items:
        return ""
    formatted_items = []
    for item in items:
        formatted_text = make_bold(item, keywords)
        formatted_items.append(f"{item_command}{{{formatted_text}}}\n")
    return f"""\\begin{{itemize}}
{''.join(formatted_items)}\\end{{itemize}}"""


__all__ = [
    "compute_content_hash",
    "escape_latex",
    "escape_latex_recursive",
    "make_bold",
    "split_string",
    "format_bullet_list",
]
