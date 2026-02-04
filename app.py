import os
import json
import time
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.api
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Permitir CORS para o domínio do GitHub Pages e local
CORS(app)

# Database Connection String (Neon)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    """Inicializa a tabela site_content se não existir"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Criar tabela
        cur.execute('''
            CREATE TABLE IF NOT EXISTS site_content (
                id SERIAL PRIMARY KEY,
                content JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Inserir conteúdo inicial se a tabela estiver vazia
        cur.execute("SELECT COUNT(*) FROM site_content WHERE id = 1")
        if cur.fetchone()[0] == 0:
            # Tentar carregar conteúdo inicial do arquivo local
            try:
                with open('content-data.json', 'r', encoding='utf-8') as f:
                    initial_content = json.load(f)
                cur.execute("INSERT INTO site_content (id, content) VALUES (1, %s)", (json.dumps(initial_content),))
            except:
                # Fallback se o arquivo não existir
                cur.execute("INSERT INTO site_content (id, content) VALUES (1, '{}')")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Cloudinary Setup
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "drwaal5yo"),
    api_key = os.environ.get("CLOUDINARY_API_KEY", "319315945712879"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "rgwuTZMMDTczf5saKGmrVARCb7I")
)

@app.route('/')
def home():
    return jsonify({"status": "Enju Tours API is running on Neon Postgres", "version": "1.1.0"}), 200

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
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT content FROM site_content WHERE id = 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify(row['content'])
        return jsonify({"error": "Content not found"}), 404
    except Exception as e:
        print(f"Error fetching content: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/content', methods=['POST'])
def save_content():
    new_content = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Usar ON CONFLICT para atualizar se já existir o ID 1
        cur.execute("""
            INSERT INTO site_content (id, content) 
            VALUES (1, %s) 
            ON CONFLICT (id) 
            DO UPDATE SET content = EXCLUDED.content, created_at = CURRENT_TIMESTAMP
        """, (json.dumps(new_content),))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Content saved successfully to Neon"})
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
    init_db()
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
