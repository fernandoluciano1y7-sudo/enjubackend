import urllib.request
import urllib.parse
import json
import base64
import os

API_URL = "http://localhost:5000/api"

def create_test_image():
    # Create valid minimal PNG content
    # 1x1 Red Pixel
    data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKwMqnAAAAABJRU5ErkJggg==")
    with open("test_pixel.png", "wb") as f:
        f.write(data)
    return "test_pixel.png"

def upload_image(filepath):
    url = f"{API_URL}/upload"
    boundary = '---BOUNDARY'
    
    with open(filepath, 'rb') as f:
        file_content = f.read()
    
    filename = os.path.basename(filepath)
    
    part1 = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\n"
        "Content-Type: image/png\r\n\r\n"
    ).encode('utf-8')
    
    part2 = b"\r\n" + f"--{boundary}--\r\n".encode('utf-8')
    
    body = part1 + file_content + part2
    
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"[SUCCESS] Upload realizado: {result['url']}")
            return result['url']
    except Exception as e:
        print(f"[ERROR] Falha no Upload: {e}")
        try:
           print(e.read().decode())
        except:
           pass
        return None

def update_content(new_image_url):
    # 1. Get current content
    try:
        with urllib.request.urlopen(f"{API_URL}/content") as resp:
            content = json.loads(resp.read().decode('utf-8'))
    except:
        print("[ERROR] Falha ao ler content")
        return

    # 2. Modify Hero Image (Force cache breaking with timestamp logic if needed, but URL changed so it's fine)
    print(f"[INFO] Trocando imagem Hero atual ({content.get('hero', {}).get('mainImage', 'N/A')}) por: {new_image_url}")
    
    if 'hero' not in content: content['hero'] = {}
    content['hero']['mainImage'] = new_image_url
    content['hero']['titleHighlight'] = "TESTE UPLOAD"

    # 3. Save
    req = urllib.request.Request(f"{API_URL}/content", data=json.dumps(content).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("[SUCCESS] Conteúdo atualizado com sucesso!")
    except Exception as e:
        print(f"[ERROR] Falha ao salvar content: {e}")

if __name__ == "__main__":
    print("--- INICIANDO TESTE DE UPLOAD ---")
    img = create_test_image()
    url = upload_image(img)
    if url:
        update_content(url)
        print("--- TESTE CONCLUIDO ---")
        print("Verifique o site. O título 'ANGOLA' deve ter mudado para 'TESTE UPLOAD' e a imagem deve ser um pixel vermelho.")
