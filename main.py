import os
import telebot
import requests
import time
from bs4 import BeautifulSoup
from google import genai

# Configuracoes
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicializar cliente
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
        return " | ".join(noticias) if noticias else "Sem noticias disponiveis."
    except Exception as e:
        return f"Erro ao buscar: {str(e)}"

def analisar_ia(dados):
    try:
        prompt = f"""Analise como insider (Ouro/DXY):

{dados}

Seja direto e brutal. Insights para trading agora."""
        
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt
        )
        
        return response.text
        
    except Exception as e:
        return f"Erro IA: {str(e)}"

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
    
    # Inicializacao
    try:
        bot.send_message(CHAT_ID, "Agente Ouro 2.0 - Sistema Ativado")
    except Exception as e:
        print(f"Erro ao enviar mensagem inicial: {e}")
    
    # Loop principal
    while True:
        try:
            dados = buscar_dados()
            relatorio = analisar_ia(dados)
            
            bot.send_message(
                CHAT_ID,
                f"RELATORIO OURO/DXY\n\n{relatorio}"
            )
            
            print(f"Relatorio enviado: {time.strftime('%H:%M:%S')}")
            time.sleep(3600)
            
        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(300)
