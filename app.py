import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase Setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("WARNING: Supabase credentials not found in .env file.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

# Cloudinary Setup
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "drwaal5yo"),
    api_key = os.environ.get("CLOUDINARY_API_KEY", "319315945712879"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "rgwuTZMMDTczf5saKGmrVARCb7I")
)

@app.route('/')
def home():
    return jsonify({"status": "Enju Tours API is running", "version": "1.0.0"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username == 'admin' and password == 'admin123':
        return jsonify({"token": "enju-tours-token-123"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/content', methods=['GET'])
def get_content():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        # Check if we verify content from a 'site_content' table
        # Assuming a simple key-value store or a single row for the whole site JSON
        response = supabase.table('site_content').select("*").eq('id', 1).execute()
        
        if response.data:
            return jsonify(response.data[0]['content'])
        else:
            # Fallback if DB is empty, try to load local json to bootstrap
            try:
                with open('content-data.json', 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                return jsonify(local_data)
            except Exception as e:
                return jsonify({"error": "Content not found"}), 404

    except Exception as e:
        print(f"Error fetching content: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/content', methods=['POST'])
def save_content():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    new_content = request.json
    
    try:
        # Upsert content (assuming ID 1 is the main site content)
        data = {
            "id": 1,
            "content": new_content
        }
        response = supabase.table('site_content').upsert(data).execute()
        return jsonify({"message": "Content saved successfully", "data": response.data})
    except Exception as e:
        print(f"Error saving content: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Upload to Cloudinary - SEM DEPENDÊNCIA DE SUPABASE STORAGE
        upload_result = cloudinary.uploader.upload(
            file,
            folder="enju_tours/images",
            resource_type="image"
        )
        return jsonify({"url": upload_result['secure_url']})
    except Exception as e:
        print(f"Cloudinary error: {e}")
        return jsonify({"error": f"Erro no Cloudinary: {str(e)}"}), 500

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video part"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Upload to Cloudinary (video)
        upload_result = cloudinary.uploader.upload(
            file,
            folder="enju_tours/videos",
            resource_type="video"
        )
        return jsonify({"url": upload_result['secure_url']})
    except Exception as e:
        print(f"Cloudinary video error: {e}")
        return jsonify({"error": f"Erro no Cloudinary (Video): {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
