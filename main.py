import os
import telebot
import requests
import time
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# Configurações
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicializar cliente (nova forma oficial)
client = genai.Client(api_key=GEMINI_KEY)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = requests.get(
            "https://www.investing.com/commodities/gold-news",
            headers=headers,
            timeout=15
        )
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias disponíveis."
    except Exception as e:
        return f"Erro ao buscar: {str(e)}"

def analisar_ia(dados):
    try:
        prompt = f"""Analise como insider (Ouro/DXY):

{dados}

Seja direto e brutal. Insights para trading agora."""
        
        # Sintaxe correta da nova SDK
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        return response.text
        
    except Exception as e:
        return f"❌ Erro IA: {str(e)}"

def servidor_web():
    """Servidor HTTP para o Render"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Bot Online')
        def log_message(self, format, *args):
            pass
    
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == "__main__":
    # Servidor em thread separada
    import threading
    threading.Thread(target=servidor_web, daemon=True).start()
    
    # Inicialização
    try:
        bot.send_message(CHAT_ID, "🛡️ **Agente Ouro 2.0 - Sistema Ativado**")
    except Exception as e:
        print(f"Erro ao enviar mensagem inicial: {e}")
    
    # Loop principal
    while True:
        try:
            dados = buscar_dados()
            relatorio = analisar_ia(dados)
            
            bot.send_message(
                CHAT_ID,
                f"⚠️ **RELATÓRIO OURO/DXY**\n\n{relatorio}",
                parse_mode='Markdown'
            )
            
            print(f"✅ Relatório enviado: {time.strftime('%H:%M:%S')}")
            time.sleep(3600)  # 1 hora
            
        except Exception as e:
            print(f"❌ Erro no loop: {e}")
            time.sleep(300)  # 5 min se der erro
```

### 3. **Configuração no Render**

**Start Command:**
```
python main.py
```

**Environment Variables:**
- `GEMINI_API_KEY` = sua chave do Gemini
- `TELEGRAM_TOKEN` = token do bot
- `PORT` = 10000

### 4. **Deploy no Render**

1. ✅ Faça commit dos arquivos no GitHub
2. ✅ No Render: **Manual Deploy** 
3. ✅ Marque **"Clear build cache & deploy"**
4. ✅ Aguarde 3-5 minutos

## 🔑 Mudanças Críticas (2025 → 2026):

| ❌ Biblioteca Antiga (morreu 30/11/2025) | ✅ Nova SDK Oficial |
|------------------------------------------|---------------------|
| `google-generativeai` | `google-genai` |
| `import google.generativeai as genai` | `from google import genai` |
| `genai.configure(api_key=...)` | `client = genai.Client(api_key=...)` |
| `model.generate_content()` | `client.models.generate_content()` |
| `gemini-1.5-flash` | `gemini-2.0-flash-exp` |

## 📊 O que esperar nos logs:

✅ **Sucesso:**
```
Successfully installed google-genai
🛡️ Agente Ouro 2.0 - Sistema Ativado
✅ Relatório enviado: 16:39:46
