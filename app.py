import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from routes import routes


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise ValueError("❌ SECRET_KEY not set in .env")

app.register_blueprint(routes)


if __name__ == "__main__":
    DEBUG = os.getenv("DEBUG_MODE", "false").lower() == "true"
    app.run(debug=DEBUG)