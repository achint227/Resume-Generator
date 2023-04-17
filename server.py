from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from waitress import serve

from build_resume import build_resume
from load_user import add_resume, all_resumes, find_by_name, find_by_resume_name
from moderncv import ModernCV

app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": "*",
                       "methods": ["GET", "POST", "PUT", "DELETE"]}},
)


@app.route("/resume", methods=["GET"], endpoint="f1")
def get_all():
    try:
        return jsonify(all_resumes())
    except Exception as e:
        print(e)
        return jsonify({"message": "Error"}), 500


@app.route("/download/<id>/<template>", methods=["GET"])
def send_resume_with_template(id, template):
    if template == 'moderncv':
        resume = ModernCV(id)
    else:
        return jsonify({"message": "Service unavailable"}), 503
    filename = resume.create_file()
    return send_file(filename, as_attachment=True)


@app.route("/download/<id>", methods=["GET"])
def send_resume(id):
    filename = build_resume(id)
    return send_file(filename, as_attachment=True)


@app.route("/resume/<name>", methods=["GET"], endpoint="f2")
def get_resume(name):
    user = find_by_resume_name(name)
    user["_id"] = str(user["_id"])
    if user:
        return jsonify(user)
    return jsonify({"message": "Not found"}), 404


@app.route("/resume/user/<name>", methods=["GET"])
def get_resume(name):
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
    except:
        return jsonify({"message": "couldn't insert"}), 422
    finally:
        return jsonify({"message": "added", "id": str(resume_id)})


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
