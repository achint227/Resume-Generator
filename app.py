from flask import Flask
from flask_cors import CORS
from waitress import serve

from src.api.routes import register_routes

app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}},
)

register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
