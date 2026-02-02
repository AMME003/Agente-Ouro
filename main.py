import os
import telebot
import requests
import time
from bs4 import BeautifulSoup

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')  # Adicione no Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem noticias"
    except:
        return "Erro ao buscar"

def analisar_ia(dados):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_KEY}'
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Analise como insider (Ouro/DXY): {dados}. Seja brutal e direto."}],
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "Sistema Ativado - ChatGPT")
    
    while True:
        try:
            dados = buscar_dados()
            relatorio = analisar_ia(dados)
            bot.send_message(CHAT_ID, f"RELATORIO:\n\n{relatorio}")
            time.sleep(3600)
        except:
            time.sleep(300)
