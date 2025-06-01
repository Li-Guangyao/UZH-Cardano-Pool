from flask import Flask, render_template, jsonify, request
import requests
import os
from dotenv import load_dotenv

load_dotenv("blockfrost.env")

app = Flask(__name__)
# API_KEY = os.getenv("BLOCKFROST_API_KEY")
# PROJECT_ID = API_KEY
BASE_URL = "localhost"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/pools")
def get_pools():
    page = request.args.get("page", default=1, type=int)
    count = request.args.get("count", default=10, type=int)
    pool_list_url = f"{BASE_URL}/pools?count={count}&page={page}&order=asc"
    headers = {"project_id": ""}

    pool_ids_response = requests.get(pool_list_url, headers=headers)
    if pool_ids_response.status_code != 200:
        return jsonify({"error": "Failed to fetch pool IDs"}), 500

    pool_ids = pool_ids_response.json()
    pools_data = []

    for pid in pool_ids:
        detail_url = f"{BASE_URL}/pools/{pid}"
        detail_response = requests.get(detail_url, headers=headers)
        if detail_response.status_code == 200:
            pool_info = detail_response.json()
            pool_info["pool_id"] = pid
            pools_data.append(pool_info)

    return jsonify({
        "page": page,
        "count": count,
        "pools": pools_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)