from curses import meta
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
    count = request.args.get("count", default=20, type=int)
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

        for pid in pool_ids:
            detail_data = get_pool_details(pid)
            history_data = get_pool_history(pid)
            metadata_data = get_pool_metadata(pid)
            
            pool_info = detail_data
            
            if isinstance(history_data, list) and len(history_data) > 0:
                latest = history_data[1]
                pool_info["reward_latest"] = {
                    "rewards": latest.get("rewards"),
                    "epoch": latest.get("epoch")
            }
                
            if metadata_data and "url" in metadata_data:
                pool_info["metadata_url"] = metadata_data["url"]
                # Try to fetch and parse the JSON from the metadata URL
                try:
                    # If the URL is relative (starts with /), prepend server address
                    meta_url = metadata_data["url"]
                    if meta_url.startswith("/"):
                        pool_info["metadata_fetch_error"] = f"The metadata URL is relative, cannot be fetched publicly."
                    meta_response = requests.get(meta_url)
                    if meta_response.status_code == 200:
                        meta_json = meta_response.json()
                        # Add all fields from meta_json into pool_info with 'metadata_' prefix
                        for k, v in meta_json.items():
                            pool_info[f"metadata_{k}"] = v
                    else:
                        pool_info["metadata_fetch_error"] = f"Failed to fetch metadata JSON: {meta_response.status_code}"
                except Exception as e:
                    pool_info["metadata_fetch_error"] = str(e)
                
            pools_data.append(pool_info)

        return jsonify({
            "page": page,
            "count": count,
            "pools": pools_data
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
            return response.json()
        else:
            return {"error": "Failed to fetch pool metadata", "status_code": response.status_code}
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
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    file.save(file_path)

    public_url = f"/files/{unique_name}"
    return jsonify({"url": public_url}), 200

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)