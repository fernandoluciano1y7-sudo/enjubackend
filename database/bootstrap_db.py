import json
import urllib.request

# Point to our local Flask server which handles the Supabase upsert
API_URL = "http://localhost:5000/api/content"

def bootstrap():
    print("Iniciando migração de content-data.json para Supabase...")
    
    try:
        # Tenta abrir na raiz do projeto (onde está o arquivo agora)
        try:
            with open('content-data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
             with open('./content-data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
        req = urllib.request.Request(
            API_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✓ Sucesso! Conteúdo migrado para o Supabase.")
            else:
                print(f"✗ Erro ao migrar: {response.status}")
            
    except FileNotFoundError:
        print("✗ Erro: Arquivo content-data.json não encontrado.")
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")

if __name__ == "__main__":
    bootstrap()
