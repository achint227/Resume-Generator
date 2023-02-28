from flask import Flask, jsonify, request
from load_user import find_by_name, add_resume, all_resumes

app = Flask(__name__)


@app.route("/resume", methods=["GET"], endpoint="f1")
def get_all():
    try:
        return jsonify(all_resumes())
    except Exception as e:
        print(e)
        return jsonify({"message": "Error"}), 500


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
    resume = request.json["resume"]
    try:
        resume_id = add_resume(resume)
    except:
        return jsonify({"message": "couldn't insert"}), 422
    finally:
        return jsonify({"message": "added"})


if __name__ == "__main__":
    app.run(port=8000)
