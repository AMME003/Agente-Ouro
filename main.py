import os
import telebot
import requests
import time
from bs4 import BeautifulSoup

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem noticias disponiveis"
    except Exception as e:
        return f"Erro ao buscar: {str(e)}"

def analisar_ia(dados):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_KEY}'
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Voce e um analista insider do mercado financeiro. Seja direto, brutal e objetivo em suas analises."
                },
                {
                    "role": "user",
                    "content": f"Analise estas noticias sobre Ouro/DXY e de insights acionaveis para trading: {dados}"
                }
            ],
            "max_tokens": 600,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # DEBUG: Mostrar resposta completa
        result = response.json()
        print(f"Resposta API: {result}")
        
        # Verificar se tem erro
        if 'error' in result:
            return f"ERRO OPENAI: {result['error'].get('message', 'Erro desconhecido')}"
        
        # Verificar se tem choices
        if 'choices' not in result:
            return f"Resposta invalida da API: {result}"
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        return f"Erro IA: {str(e)}"

if __name__ == "__main__":
    try:
        bot.send_message(CHAT_ID, "Sistema Ativado - ChatGPT (Debug Mode)")
        print("Bot iniciado")
    except Exception as e:
        print(f"Erro inicial: {e}")
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Coletando dados...")
            dados = buscar_dados()
            
            print(f"[{time.strftime('%H:%M:%S')}] Analisando...")
            relatorio = analisar_ia(dados)
            
            bot.send_message(CHAT_ID, f"RELATORIO:\n\n{relatorio}")
            
            print(f"[{time.strftime('%H:%M:%S')}] Enviado!")
            time.sleep(3600)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(300)
