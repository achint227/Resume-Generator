from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from waitress import serve

from load_user import (add_resume, all_resumes, find_by_name,
                       find_by_resume_name)
from moderncv import ModernCV
from template1 import Template1
from template2 import Template2

app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": "*",
                       "methods": ["GET", "POST", "PUT", "DELETE"]}},
)


@app.route("/",methods=["GET"])
def hello_word():
  return jsonify({"message":"Hello from Resume-Generator"})


@app.route("/resume", methods=["GET"], endpoint="f1")
def get_all():
    try:
        return jsonify(all_resumes())
    except Exception as e:
        print(e)
        return jsonify({"message": "Error"}), 500


@app.route("/download/<id>/<template>/<order>", methods=["GET"])
def send_resume_with_template(id, template, order):
    if len(order)!=3 or any(x not in order for x in 'pwe'):
        return jsonify({"message": "invalid format for order"}), 422
    if template == 'moderncv':
        resume = ModernCV(id)
    elif template == 'resume':
        resume = Template1(id)
    elif template == 'russel':
        resume = Template2(id)
    else:
        return jsonify({"message": "Service unavailable"}), 503
    filename = resume.create_file(order)
    return send_file(filename, as_attachment=True)


@app.route("/copy/<id>/<template>/<order>", methods=["GET"])
def resume_text(id, template, order):
    if len(order)!=3 or any(x not in order for x in 'pwe'):
        return jsonify({"message": "invalid format for order"}), 422
    if template == 'moderncv':
        resume = ModernCV(id)
    elif template == 'resume':
        resume = Template1(id)
    elif template == 'russel':
        resume = Template2(id)
    else:
        return jsonify({"message": "Service unavailable"}), 503
            
    return jsonify({"resume":resume.build_resume(order)})


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
    app.run(host="0.0.0.0", port=8000)
