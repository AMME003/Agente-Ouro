import os
from google import genai

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_KEY)

print("=== MODELOS DISPONIVEIS ===")
try:
    models = client.models.list()
    for model in models:
        print(f"Nome: {model.name}")
        print(f"Suporta generateContent: {hasattr(model, 'supported_generation_methods')}")
        print("---")
except Exception as e:
    print(f"Erro ao listar: {e}")
