from curses import meta
from importlib import metadata
from multiprocessing import pool
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import requests
import os
from dotenv import load_dotenv
import uuid

load_dotenv("blockfrost.env")
UPLOAD_FOLDER = "/data/uploads"
ALLOWED_EXTENSIONS = {'json'}
MAX_CONTENT_LENGTH = 500  # 500b

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# API_KEY = os.getenv("BLOCKFROST_API_KEY")
# PROJECT_ID = API_KEY
BASE_URL = "http://172.17.0.1:3000"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/pools")
def get_pools():
    page = request.args.get("page", default=1, type=int)
    count = request.args.get("count", default=100, type=int)
    headers = {"accept": "application/json"}
 
    if count>100:
        return jsonify({
            "error": "Cannot request more than 100 items at one time."
        }), 500
    
    try:
        pool_list_url = f"{BASE_URL}/pools?count={count}&page={page}&order=desc"
        pool_ids_response = requests.get(pool_list_url, headers=headers)
        
    
        if pool_ids_response.status_code != 200:
            print("Failed to fetch pool IDs:", pool_ids_response.text)
            return jsonify({
                "error": "Failed to fetch pool IDs",
                "status_code": pool_ids_response.status_code,
                "message": pool_ids_response.text
            }), 500

        pool_ids = pool_ids_response.json()
        pools_data = []
        
        total_pools = len(pool_ids)
        total_stakes = 0
        total_delegators = 0

        for pid in pool_ids:
            detail_data = get_pool_details(pid)
            history_data = get_pool_history(pid)
            metadata_data = get_pool_metadata(pid)
            
            pool_info = detail_data
            
            if not 'error' in detail_data:
                total_stakes += int(pool_info.get("live_stake", 0) or 0)
                total_delegators += int(pool_info.get("live_delegators", 0) or 0)
                
            
            if isinstance(history_data, list) and len(history_data) > 1:
                latest = history_data[1]
                pool_info["reward_latest"] = {
                    "rewards": latest.get("rewards"),
                    "epoch": latest.get("epoch")
                }
                
            for k, v in metadata_data.items():
                pool_info[f"metadata_{k}"] = v
                
            pools_data.append(pool_info)
        

        return jsonify({
            "page": page,
            "count": count,
            "pools": pools_data,
            "total_pools": total_pools,
            "total_delegators": total_delegators,
            "total_stakes": total_stakes,
            "current_epoch": get_current_epoch_info()
        })
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


def get_pool_details(pool_id):
    headers = {"accept": "application/json"}
    try:
        detail_url = f"{BASE_URL}/pools/{pool_id}"
        response = requests.get(detail_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch pool details", "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}
    

def get_pool_history(pool_id):
    headers = {"accept": "application/json"}
    try:
        history_url = f"{BASE_URL}/pools/{pool_id}/history?count=10&page=1&order=desc"
        response = requests.get(history_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch pool history", "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}
    

def get_pool_metadata(pool_id):
    headers = {"accept": "application/json"}
    try:
        metadata_url = f"{BASE_URL}/pools/{pool_id}/metadata"
        response = requests.get(metadata_url, headers=headers)
        if response.status_code == 200:
            metadata = response.json()
            homepage_url = metadata.get("homepage")
            if homepage_url and homepage_url.startswith("http"):
                try:
                    homepage_response = requests.get(homepage_url)
                    if homepage_response.status_code == 200:
                        homepage_json = homepage_response.json()
                        metadata.update(homepage_json)
                        return metadata
                    else:
                        metadata["homepage_fetch_error"] = f"Failed to fetch homepage JSON: {homepage_response.status_code}"
                        return metadata
                except Exception as e:
                    metadata["homepage_fetch_error"] = str(e)
                    return metadata
            else:
                return metadata
        else:
            return {"error": "Failed to fetch pool metadata", "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}
    
def get_current_epoch_info():
    headers = {"accept": "application/json"}
    try:
        epoch_url = f"{BASE_URL}/epochs/latest"
        response = requests.get(epoch_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch epoch info", "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}
    
    
    
# the following functions are used to handle file uploads
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only .json files allowed"}), 400

    filename = secure_filename(file.filename)
    # Use only 22 hex chars from uuid (32-10=22)
    unique_name = f"{uuid.uuid4().hex[:22]}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    file.save(file_path)

    public_url = f"/files/{unique_name}"
    return jsonify({"url": public_url}), 200

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)