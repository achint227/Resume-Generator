"""
API routes for the Resume Generator application.

This module defines all REST API endpoints following RESTful conventions
with proper input validation and consistent response formats.

Requirements: 3.3, 4.1, 4.2, 4.3, 4.4
"""

import logging
from typing import Optional

from flask import Flask, jsonify, request, send_file

from src.api.responses import (
    APIResponse,
    ErrorCodes,
    error_response,
    not_found_response,
    success_response,
    validation_error_response,
)
from src.api.swagger import init_swagger
from src.api.validation import (
    validate_order,
    validate_resume_data,
    validate_resume_id,
    validate_template_name,
)
from src.exceptions import (
    ConfigurationError,
    DatabaseError,
    LaTeXCompilationError,
    ResumeGeneratorError,
    ResumeNotFoundError,
    TemplateError,
    ValidationError,
)
from src.repositories import get_resume_repository
from src.templates.moderncv import ModernCV
from src.templates.template1 import Template1
from src.templates.template2 import Template2
from src.templates.template3 import Template3

logger = logging.getLogger(__name__)

TEMPLATES = {
    "moderncv": ModernCV,
    "resume": Template1,
    "russel": Template2,
    "classic": Template3,
}

TEMPLATE_INFO = [
    {"id": "classic", "name": "Classic", "description": "Classic ATS-friendly resume template"},
    {"id": "moderncv", "name": "Modern CV", "description": "Modern CV template with clean design"},
    {"id": "resume", "name": "Resume", "description": "Professional resume template"},
    {"id": "russel", "name": "Russell", "description": "Russell style resume template"},
]


def get_template(template_name: str, resume_id: str) -> Optional[object]:
    """Get template instance by name.
    
    Args:
        template_name: The name of the template.
        resume_id: The ID of the resume to use with the template.
        
    Returns:
        Template instance or None if template not found.
    """
    template_class = TEMPLATES.get(template_name)
    if template_class:
        return template_class(resume_id)
    return None


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for custom exceptions.
    
    Args:
        app: The Flask application instance.
    """
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle validation errors with 422 status."""
        response = validation_error_response(
            field=error.field,
            message=str(error),
            value=error.value,
        )
        return jsonify(response.to_dict()), 422
    
    @app.errorhandler(ResumeNotFoundError)
    def handle_not_found_error(error: ResumeNotFoundError):
        """Handle not found errors with 404 status."""
        response = not_found_response("Resume", error.identifier)
        return jsonify(response.to_dict()), 404
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        """Handle database errors with 500 status."""
        logger.error(f"Database error: {error}")
        response = error_response(
            message="A database error occurred",
            code=ErrorCodes.DATABASE_ERROR,
            details={"operation": error.operation} if error.operation else None,
        )
        return jsonify(response.to_dict()), 500
    
    @app.errorhandler(LaTeXCompilationError)
    def handle_latex_error(error: LaTeXCompilationError):
        """Handle LaTeX compilation errors with 500 status."""
        logger.error(f"LaTeX compilation error: {error}")
        response = error_response(
            message="Failed to compile resume PDF",
            code=ErrorCodes.LATEX_ERROR,
        )
        return jsonify(response.to_dict()), 500
    
    @app.errorhandler(TemplateError)
    def handle_template_error(error: TemplateError):
        """Handle template errors with 500 status."""
        logger.error(f"Template error: {error}")
        response = error_response(
            message="Failed to render template",
            code=ErrorCodes.TEMPLATE_ERROR,
            details={
                "template": error.template_name,
                "section": error.section,
            } if error.template_name else None,
        )
        return jsonify(response.to_dict()), 500
    
    @app.errorhandler(ConfigurationError)
    def handle_config_error(error: ConfigurationError):
        """Handle configuration errors with 500 status."""
        logger.error(f"Configuration error: {error}")
        response = error_response(
            message="Server configuration error",
            code=ErrorCodes.CONFIGURATION_ERROR,
        )
        return jsonify(response.to_dict()), 500
    
    @app.errorhandler(ResumeGeneratorError)
    def handle_app_error(error: ResumeGeneratorError):
        """Handle generic application errors with 500 status."""
        logger.error(f"Application error: {error}")
        response = error_response(
            message="An application error occurred",
            code=ErrorCodes.INTERNAL_ERROR,
        )
        return jsonify(response.to_dict()), 500


def register_routes(app: Flask) -> None:
    """Register all API routes with the Flask application.
    
    Args:
        app: The Flask application instance.
    """
    # Register error handlers first
    register_error_handlers(app)
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring.
        ---
        tags:
          - Health
        summary: Health check
        description: Returns the health status of the API for load balancers and monitoring tools.
        responses:
          200:
            description: API is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return jsonify({"status": "healthy"}), 200

    @app.route("/", methods=["GET"])
    def hello_world():
        """Root endpoint.
        ---
        tags:
          - Health
        summary: Root endpoint
        description: Returns a simple message to verify the API is running.
        responses:
          200:
            description: API is running
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Hello from Resume-Generator
        """
        response = success_response({"message": "Hello from Resume-Generator"})
        return jsonify(response.to_dict())

    @app.route("/templates", methods=["GET"])
    def get_templates():
        """Get list of available templates.
        ---
        tags:
          - Templates
        summary: List available templates
        description: Returns a list of all available resume templates with their IDs and descriptions.
        responses:
          200:
            description: List of templates
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    templates:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: string
                            example: classic
                          name:
                            type: string
                            example: Classic
                          description:
                            type: string
                            example: Classic ATS-friendly resume template
        """
        response = success_response({"templates": TEMPLATE_INFO})
        return jsonify(response.to_dict())

    @app.route("/resume", methods=["GET"], endpoint="get_all_resumes")
    def get_all():
        """Get all resumes.
        ---
        tags:
          - Resumes
        summary: List all resumes
        description: Returns a list of all stored resumes.
        responses:
          200:
            description: List of resumes
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: array
                  items:
                    $ref: '#/definitions/Resume'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        try:
            repo = get_resume_repository()
            resumes = repo.get_all()
            # Convert Resume objects to dicts
            resume_list = [r.to_dict() for r in resumes]
            response = success_response(resume_list)
            return jsonify(response.to_dict())
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error fetching resumes: {e}")
            raise DatabaseError(str(e), operation="query")

    @app.route("/download/<id>/<template>/<order>", methods=["GET"])
    def send_resume_with_template(id, template, order):
        """Download resume as PDF with specified template and section order.
        ---
        tags:
          - PDF Generation
        summary: Download resume as PDF
        description: |
          Generates and downloads a PDF resume using the specified template and section order.
          The order parameter controls the arrangement of sections:
          - 'p' = Projects
          - 'w' = Work Experience
          - 'e' = Education
        parameters:
          - name: id
            in: path
            type: string
            required: true
            description: Resume ID
            example: "12345"
          - name: template
            in: path
            type: string
            required: true
            description: Template name
            enum: [classic, moderncv, resume, russel]
            example: classic
          - name: order
            in: path
            type: string
            required: true
            description: Section order (3 chars containing 'p', 'w', 'e')
            example: wpe
          - name: force
            in: query
            type: boolean
            required: false
            description: Force regeneration, bypassing cache
            default: false
        produces:
          - application/pdf
        responses:
          200:
            description: PDF file download
            schema:
              type: file
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          422:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: PDF generation error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        # Validate inputs
        validate_resume_id(id)
        validate_template_name(template, list(TEMPLATES.keys()))
        validate_order(order)
        
        resume = get_template(template, id)
        if not resume:
            raise ValidationError(
                field="template",
                message=f"Template '{template}' not found",
                value=template,
            )
        
        # ?force=true to bypass cache
        force = request.args.get("force", "false").lower() == "true"
        
        try:
            filename = resume.create_file(order, force=force)
            return send_file(filename, as_attachment=True)
        except LaTeXCompilationError:
            raise
        except TemplateError:
            raise
        except Exception as e:
            logger.error(f"Error generating resume PDF: {e}")
            raise TemplateError(str(e), template_name=template)

    @app.route("/copy/<id>/<template>/<order>", methods=["GET"])
    def resume_text(id, template, order):
        """Get resume LaTeX source with specified template and section order.
        ---
        tags:
          - PDF Generation
        summary: Get LaTeX source
        description: |
          Returns the LaTeX source code for a resume using the specified template and section order.
          Useful for manual editing or debugging.
        parameters:
          - name: id
            in: path
            type: string
            required: true
            description: Resume ID
            example: "12345"
          - name: template
            in: path
            type: string
            required: true
            description: Template name
            enum: [classic, moderncv, resume, russel]
            example: classic
          - name: order
            in: path
            type: string
            required: true
            description: Section order (3 chars containing 'p', 'w', 'e')
            example: wpe
        responses:
          200:
            description: LaTeX source code
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    resume:
                      type: string
                      description: LaTeX source code
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          422:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Template error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        # Validate inputs
        validate_resume_id(id)
        validate_template_name(template, list(TEMPLATES.keys()))
        validate_order(order)
        
        resume = get_template(template, id)
        if not resume:
            raise ValidationError(
                field="template",
                message=f"Template '{template}' not found",
                value=template,
            )

        try:
            latex_content = resume.build_resume(order)
            response = success_response({"resume": latex_content})
            return jsonify(response.to_dict())
        except Exception as e:
            logger.error(f"Error building resume: {e}")
            raise TemplateError(str(e), template_name=template)

    @app.route("/resume/<name>", methods=["GET"], endpoint="get_resume_by_resume_name")
    def get_resume(name):
        """Get resume by resume name.
        ---
        tags:
          - Resumes
        summary: Get resume by name
        description: Retrieves a resume by its name field.
        parameters:
          - name: name
            in: path
            type: string
            required: true
            description: Resume name
            example: "software-engineer-resume"
        responses:
          200:
            description: Resume found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  $ref: '#/definitions/Resume'
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        try:
            repo = get_resume_repository()
            resume = repo.get_by_resume_name(name)
            if resume:
                response = success_response(resume.to_dict())
                return jsonify(response.to_dict())
            raise ResumeNotFoundError(name)
        except ResumeNotFoundError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error fetching resume: {e}")
            raise DatabaseError(str(e), operation="query")

    @app.route("/resume/user/<name>", methods=["GET"])
    def get_resume_by_user(name):
        """Get resume by user name.
        ---
        tags:
          - Resumes
        summary: Get resume by user name
        description: Retrieves a resume by the user's name (basic_info.name field).
        parameters:
          - name: name
            in: path
            type: string
            required: true
            description: User name
            example: "John Doe"
        responses:
          200:
            description: Resume found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  $ref: '#/definitions/Resume'
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        try:
            repo = get_resume_repository()
            resume = repo.get_by_name(name)
            if resume:
                response = success_response(resume.to_dict())
                return jsonify(response.to_dict())
            raise ResumeNotFoundError(name)
        except ResumeNotFoundError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error fetching resume: {e}")
            raise DatabaseError(str(e), operation="query")

    @app.route("/resume", methods=["POST"], endpoint="create_resume")
    def add_document():
        """Create a new resume.
        ---
        tags:
          - Resumes
        summary: Create a new resume
        description: Creates a new resume with the provided data.
        consumes:
          - application/json
        parameters:
          - name: body
            in: body
            required: true
            description: Resume data
            schema:
              $ref: '#/definitions/ResumeInput'
        responses:
          201:
            description: Resume created successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    message:
                      type: string
                      example: added
                    id:
                      type: string
                      example: "12345"
          422:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        resume_data = request.json
        
        # Validate input
        errors = validate_resume_data(resume_data)
        if errors:
            raise ValidationError(
                field="body",
                message="; ".join(errors),
            )
        
        try:
            repo = get_resume_repository()
            from src.models.resume import Resume
            resume = Resume.from_dict(resume_data)
            resume_id = repo.create(resume)
            response = success_response({"message": "added", "id": str(resume_id)})
            return jsonify(response.to_dict()), 201
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error adding resume: {e}")
            raise DatabaseError(str(e), operation="insert")

    @app.route("/resume/<id>", methods=["PUT"])
    def update_document(id):
        """Update an existing resume.
        ---
        tags:
          - Resumes
        summary: Update a resume
        description: Updates an existing resume with the provided data.
        consumes:
          - application/json
        parameters:
          - name: id
            in: path
            type: string
            required: true
            description: Resume ID
            example: "12345"
          - name: body
            in: body
            required: true
            description: Updated resume data
            schema:
              $ref: '#/definitions/ResumeInput'
        responses:
          200:
            description: Resume updated successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    message:
                      type: string
                      example: updated
                    id:
                      type: string
                      example: "12345"
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          422:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        validate_resume_id(id)
        resume_data = request.json
        
        # Validate input
        errors = validate_resume_data(resume_data)
        if errors:
            raise ValidationError(
                field="body",
                message="; ".join(errors),
            )
        
        try:
            repo = get_resume_repository()
            from src.models.resume import Resume
            resume = Resume.from_dict(resume_data)
            updated = repo.update(id, resume)
            if updated:
                response = success_response({"message": "updated", "id": id})
                return jsonify(response.to_dict()), 200
            raise ResumeNotFoundError(id)
        except ResumeNotFoundError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error updating resume: {e}")
            raise DatabaseError(str(e), operation="update")

    @app.route("/resume/<id>", methods=["DELETE"])
    def delete_document(id):
        """Delete a resume by ID.
        ---
        tags:
          - Resumes
        summary: Delete a resume
        description: Deletes a resume by its ID.
        parameters:
          - name: id
            in: path
            type: string
            required: true
            description: Resume ID
            example: "12345"
        responses:
          200:
            description: Resume deleted successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    message:
                      type: string
                      example: deleted
                    id:
                      type: string
                      example: "12345"
          404:
            description: Resume not found
            schema:
              $ref: '#/definitions/ErrorResponse'
          500:
            description: Database error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        validate_resume_id(id)
        
        try:
            repo = get_resume_repository()
            deleted = repo.delete(id)
            if deleted:
                response = success_response({"message": "deleted", "id": id})
                return jsonify(response.to_dict()), 200
            raise ResumeNotFoundError(id)
        except ResumeNotFoundError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error deleting resume: {e}")
            raise DatabaseError(str(e), operation="delete")
