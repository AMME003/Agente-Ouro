import os
import telebot
import requests
import time
from bs4 import BeautifulSoup

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_precos():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Buscar preco do ouro
        res_ouro = requests.get("https://www.investing.com/currencies/xau-usd", headers=headers, timeout=15)
        soup_ouro = BeautifulSoup(res_ouro.text, 'html.parser')
        preco_ouro = soup_ouro.find('span', {'data-test': 'instrument-price-last'})
        ouro = preco_ouro.text.strip() if preco_ouro else "N/A"
        
        # Buscar preco do DXY
        res_dxy = requests.get("https://www.investing.com/indices/usdollar", headers=headers, timeout=15)
        soup_dxy = BeautifulSoup(res_dxy.text, 'html.parser')
        preco_dxy = soup_dxy.find('span', {'data-test': 'instrument-price-last'})
        dxy = preco_dxy.text.strip() if preco_dxy else "N/A"
        
        return f"XAUUSD: {ouro} | DXY: {dxy}"
        
    except Exception as e:
        return f"Erro ao buscar precos: {str(e)}"

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem noticias"
    except Exception as e:
        return f"Erro ao buscar noticias: {str(e)}"

def analisar_ia(precos, noticias):
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
                    "content": "Voce e um trader profissional especializado em Ouro (XAUUSD) e DXY. Seja direto, brutal e objetivo. Use SOMENTE os dados fornecidos, nao invente precos."
                },
                {
                    "role": "user",
                    "content": f"""DADOS ATUAIS:
{precos}

NOTICIAS RECENTES:
{noticias}

Analise o cenario atual e de insights acionaveis para trading. Seja direto e agressivo nas recomendacoes."""
                }
            ],
            "max_tokens": 700,
            "temperature": 0.5
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if 'error' in result:
            return f"ERRO OPENAI: {result['error'].get('message', 'Erro desconhecido')}"
        
        if 'choices' not in result:
            return f"Resposta invalida: {result}"
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        return f"Erro IA: {str(e)}"

if __name__ == "__main__":
    try:
        bot.send_message(CHAT_ID, "Agente Ouro 2.0 - Sistema Ativado")
        print("Bot iniciado")
    except Exception as e:
        print(f"Erro inicial: {e}")
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Buscando precos...")
            precos = buscar_precos()
            print(f"Precos: {precos}")
            
            print(f"[{time.strftime('%H:%M:%S')}] Buscando noticias...")
            noticias = buscar_noticias()
            
            print(f"[{time.strftime('%H:%M:%S')}] Analisando com IA...")
            relatorio = analisar_ia(precos, noticias)
            
            mensagem = f"RELATORIO OURO/DXY\n\n{precos}\n\n{relatorio}"
            bot.send_message(CHAT_ID, mensagem)
            
            print(f"[{time.strftime('%H:%M:%S')}] Enviado!")
            time.sleep(3600)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(300)
