import os, requests

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"

try:
    response = requests.get(url)
    models = response.json()
    if "models" in models:
        print("=== MODELOS QUE SUA CHAVE PODE USAR ===")
        for m in models["models"]:
            print(f"ID: {m['name']} | Métodos: {m['supportedGenerationMethods']}")
    else:
        print(f"ERRO DE CONFIGURAÇÃO: {models}")
except Exception as e:
    print(f"ERRO DE CONEXÃO: {e}")
