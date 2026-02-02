import os
import telebot
import requests
import time
from bs4 import BeautifulSoup

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
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
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': GEMINI_KEY
        }
        
        payload = {
            "contents": [{"parts": [{"text": f"Analise mercado Ouro/DXY: {dados}"}]}]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return f"Erro API: {response.status_code} - {response.text[:200]}"
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "Sistema Ativado")
    
    while True:
        try:
            dados = buscar_dados()
            relatorio = analisar_ia(dados)
            bot.send_message(CHAT_ID, f"RELATORIO:\n\n{relatorio}")
            time.sleep(3600)
        except:
            time.sleep(300)
