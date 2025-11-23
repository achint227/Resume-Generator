from flask import jsonify, request, send_file

from src.database.operations import (add_resume, all_resumes, find_by_name,
                                      find_by_resume_name, update_resume)
from src.templates.moderncv import ModernCV
from src.templates.template1 import Template1
from src.templates.template2 import Template2
from src.templates.template3 import Template3


def register_routes(app):
    @app.route("/", methods=["GET"])
    def hello_word():
        return jsonify({"message": "Hello from Resume-Generator"})

    @app.route("/templates", methods=["GET"])
    def get_templates():
        templates = [
            {"id": "classic", "name": "Classic", "description": "Classic ATS-friendly resume template"},
            {"id": "moderncv", "name": "Modern CV", "description": "Modern CV template with clean design"},
            {"id": "resume", "name": "Resume", "description": "Professional resume template"},
            {"id": "russel", "name": "Russell", "description": "Russell style resume template"}
        ]
        return jsonify({"templates": templates})

    @app.route("/resume", methods=["GET"], endpoint="f1")
    def get_all():
        try:
            return jsonify(all_resumes())
        except Exception as e:
            print(e)
            return jsonify({"message": "Error"}), 500

    @app.route("/download/<id>/<template>/<order>", methods=["GET"])
    def send_resume_with_template(id, template, order):
        if len(order) != 3 or any(x not in order for x in "pwe"):
            return jsonify({"message": "invalid format for order"}), 422
        if template == "moderncv":
            resume = ModernCV(id)
        elif template == "resume":
            resume = Template1(id)
        elif template == "russel":
            resume = Template2(id)
        elif template == "classic":
            resume = Template3(id)
        else:
            return jsonify({"message": "Service unavailable"}), 503
        filename = resume.create_file(order)
        return send_file(filename, as_attachment=True)

    @app.route("/copy/<id>/<template>/<order>", methods=["GET"])
    def resume_text(id, template, order):
        if len(order) != 3 or any(x not in order for x in "pwe"):
            return jsonify({"message": "invalid format for order"}), 422
        if template == "moderncv":
            resume = ModernCV(id)
        elif template == "resume":
            resume = Template1(id)
        elif template == "russel":
            resume = Template2(id)
        elif template == "classic":
            resume = Template3(id)
        else:
            return jsonify({"message": "Service unavailable"}), 503

        return jsonify({"resume": resume.build_resume(order)})

    @app.route("/resume/<name>", methods=["GET"], endpoint="f2")
    def get_resume(name):
        user = find_by_resume_name(name)
        user["_id"] = str(user["_id"])
        if user:
            return jsonify(user)
        return jsonify({"message": "Not found"}), 404

    @app.route("/resume/user/<name>", methods=["GET"])
    def get_resume_by_user(name):
        user = find_by_name(name)
        user["_id"] = str(user["_id"])
        if user:
            return jsonify(user)
        return jsonify({"message": "Not found"}), 404

    @app.route("/resume", methods=["POST"])
    def add_document():
        resume = request.json
        try:
            resume_id = add_resume(resume)
            return jsonify({"message": "added", "id": str(resume_id)}), 201
        except Exception as e:
            print(f"Error adding resume: {e}")
            return jsonify({"message": "couldn't insert"}), 422

    @app.route("/resume/<id>", methods=["PUT"])
    def update_document(id):
        resume = request.json
        try:
            updated = update_resume(id, resume)
            if updated:
                return jsonify({"message": "updated", "id": id}), 200
            else:
                return jsonify({"message": "resume not found"}), 404
        except Exception as e:
            print(f"Error updating resume: {e}")
            return jsonify({"message": "couldn't update"}), 422
