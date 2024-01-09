from flask import Flask
from api import api_bp


app = Flask(__name__)
app.register_blueprint(api_bp)

@app.route("/")
async def home():
    return "Hello world"


if __name__ == "__main__":
    app.run(debug=True, port=8000)