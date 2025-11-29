"""
Swagger/OpenAPI configuration for the Resume Generator API.

This module configures Flasgger to provide interactive API documentation
at the /docs endpoint.

Requirements: 7.1
"""

from typing import Any, Dict

from flasgger import Swagger
from flask import Flask


# OpenAPI specification template
SWAGGER_TEMPLATE: Dict[str, Any] = {
    "swagger": "2.0",
    "info": {
        "title": "Resume Generator API",
        "description": "API for generating PDF resumes from structured data using LaTeX templates",
        "version": "1.0.0",
        "contact": {
            "name": "Resume Generator",
        },
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json", "application/pdf"],
    "definitions": {
        "BasicInfo": {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string", "example": "John Doe"},
                "email": {"type": "string", "example": "john.doe@example.com"},
                "phone": {"type": "string", "example": "+1-555-123-4567"},
                "address": {"type": "string", "example": "San Francisco, CA"},
                "summary": {"type": "string", "example": "Experienced software engineer..."},
                "github": {"type": "string", "example": "https://github.com/johndoe"},
                "linkedin": {"type": "string", "example": "https://linkedin.com/in/johndoe"},
                "homepage": {"type": "string", "example": "https://johndoe.dev"},
            },
        },
        "Education": {
            "type": "object",
            "required": ["university", "degree", "location", "duration"],
            "properties": {
                "university": {"type": "string", "example": "Stanford University"},
                "degree": {"type": "string", "example": "B.S. Computer Science"},
                "location": {"type": "string", "example": "Stanford, CA"},
                "duration": {"type": "string", "example": "2018 - 2022"},
                "info": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["GPA: 3.9", "Dean's List"],
                },
            },
        },
        "ProjectDetail": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string", "example": "API Redesign"},
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Python", "Flask"],
                },
                "details": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Improved API response time by 40%"],
                },
            },
        },
        "Experience": {
            "type": "object",
            "required": ["company", "title", "location", "duration"],
            "properties": {
                "company": {"type": "string", "example": "Tech Corp"},
                "title": {"type": "string", "example": "Senior Software Engineer"},
                "location": {"type": "string", "example": "San Francisco, CA"},
                "duration": {"type": "string", "example": "2022 - Present"},
                "projects": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/ProjectDetail"},
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Python", "AWS"],
                },
                "description": {"type": "string", "example": "Led backend development..."},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["backend", "leadership"],
                },
            },
        },
        "Project": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string", "example": "Open Source CLI Tool"},
                "description": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Built a CLI tool for automating deployments"],
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Go", "Docker"],
                },
                "repo": {"type": "string", "example": "https://github.com/johndoe/cli-tool"},
            },
        },
        "Resume": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "example": "12345"},
                "name": {"type": "string", "example": "software-engineer-resume"},
                "basic_info": {"$ref": "#/definitions/BasicInfo"},
                "education": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Education"},
                },
                "experiences": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Experience"},
                },
                "projects": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Project"},
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Python", "AWS", "Docker"],
                },
            },
        },
        "ResumeInput": {
            "type": "object",
            "required": ["basic_info"],
            "properties": {
                "name": {"type": "string", "example": "software-engineer-resume"},
                "basic_info": {"$ref": "#/definitions/BasicInfo"},
                "education": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Education"},
                },
                "experiences": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Experience"},
                },
                "projects": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Project"},
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Python", "AWS", "Docker"],
                },
            },
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "VALIDATION_ERROR"},
                        "message": {"type": "string", "example": "Invalid input"},
                        "field": {"type": "string", "example": "order"},
                        "details": {"type": "object"},
                    },
                },
            },
        },
    },
}

# Swagger configuration
SWAGGER_CONFIG: Dict[str, Any] = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}


def init_swagger(app: Flask) -> Swagger:
    """Initialize Swagger/OpenAPI documentation for the Flask app.
    
    Args:
        app: The Flask application instance.
        
    Returns:
        The configured Swagger instance.
    """
    swagger = Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    return swagger


__all__ = ["init_swagger", "SWAGGER_TEMPLATE", "SWAGGER_CONFIG"]
