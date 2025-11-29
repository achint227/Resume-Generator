"""
Resume templates module.

This module provides template classes for generating PDF resumes
and a registry for managing available templates.

Usage:
    from src.templates import TemplateRegistry, Template1, Template2
    
    # Get a template class by name
    template_cls = TemplateRegistry.get("resume")
    template = template_cls(resume_id)
    
    # List all available templates
    templates = TemplateRegistry.list_templates()
"""

from typing import Dict, List, Optional, Type

from src.templates.base import Template


class TemplateRegistry:
    """Registry for managing available resume templates.
    
    Provides a centralized way to register, retrieve, and list
    template classes. Templates can be registered using the
    @register decorator.
    
    Example:
        @TemplateRegistry.register("my-template")
        class MyTemplate(Template):
            ...
    """
    
    _templates: Dict[str, Type[Template]] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a template class.
        
        Args:
            name: The unique name identifier for the template.
            
        Returns:
            Decorator function that registers the template class.
            
        Example:
            @TemplateRegistry.register("resume")
            class Template1(Template):
                ...
        """
        def decorator(template_class: Type[Template]) -> Type[Template]:
            cls._templates[name] = template_class
            return template_class
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Type[Template]]:
        """Get a template class by name.
        
        Args:
            name: The name identifier of the template.
            
        Returns:
            The template class if found, None otherwise.
        """
        return cls._templates.get(name)
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """List all registered templates.
        
        Returns:
            List of dictionaries containing template information:
            - name: The template identifier
            - class_name: The template class name
            - description: The template's docstring (first line)
        """
        templates = []
        for name, template_cls in cls._templates.items():
            doc = template_cls.__doc__ or ""
            description = doc.split("\n")[0].strip() if doc else ""
            templates.append({
                "name": name,
                "class_name": template_cls.__name__,
                "description": description,
            })
        return templates
    
    @classmethod
    def get_all(cls) -> Dict[str, Type[Template]]:
        """Get all registered templates.
        
        Returns:
            Dictionary mapping template names to template classes.
        """
        return cls._templates.copy()


# Import and register templates
from src.templates.template1 import Template1
from src.templates.template2 import Template2
from src.templates.template3 import Template3
from src.templates.moderncv import ModernCV

# Register templates with the registry
TemplateRegistry._templates["resume"] = Template1
TemplateRegistry._templates["russel"] = Template2
TemplateRegistry._templates["classic"] = Template3
TemplateRegistry._templates["moderncv"] = ModernCV


__all__ = [
    "Template",
    "TemplateRegistry",
    "Template1",
    "Template2",
    "Template3",
    "ModernCV",
]
