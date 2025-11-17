from flask import Flask, jsonify
from flask_cors import CORS
from flask import send_from_directory
from pathlib import Path
import json

app = Flask(__name__)
CORS(app)

LOAD_DIR = Path("etl/load")

@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")


@app.route("/api/data", methods=["GET"])
def get_json_data():
    data_list = []
    for json_file in LOAD_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data_list.append({
                    "filename": json_file.name,
                    "records": data
                })
        except Exception as e:
            print(f"Erro ao ler {json_file}: {e}")

    return jsonify(data_list)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
