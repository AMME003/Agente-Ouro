import os
import telebot
import requests
import time
import json
from bs4 import BeautifulSoup

# Configuracoes
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

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
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Analise como insider do mercado financeiro (Ouro/DXY):

{dados}

Seja direto, brutal e objetivo. Foque em insights acionaveis para trading."""
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        texto = result['candidates'][0]['content']['parts'][0]['text']
        return texto
        
    except Exception as e:
        return f"Erro na analise IA: {str(e)}"

if __name__ == "__main__":
    try:
        bot.send_message(CHAT_ID, "Agente Ouro 2.0 - Sistema Ativado")
        print("Bot iniciado com sucesso")
    except Exception as e:
        print(f"Erro inicial: {e}")
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Coletando dados...")
            dados = buscar_dados()
            
            print(f"[{time.strftime('%H:%M:%S')}] Analisando com IA...")
            relatorio = analisar_ia(dados)
            
            bot.send_message(CHAT_ID, f"RELATORIO OURO/DXY\n\n{relatorio}")
            
            print(f"[{time.strftime('%H:%M:%S')}] Enviado! Proxima em 1h")
            time.sleep(3600)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(300)
