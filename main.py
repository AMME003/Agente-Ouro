import os
import telebot
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time

# Configurações de Ambiente
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Inicialização
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados_mercado():
    url = "https://www.investing.com/commodities/gold-news"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias)
    except Exception as e:
        return f"Erro ao buscar notícias: {e}"

def analisar_com_gemini(dados):
    prompt = (
        f"Analise estas notícias de Ouro/DXY: {dados}. "
        "Busque sinais de baleias, manipulação ou compras de Bancos Centrais. "
        "Responda de forma curta e bruta para um investidor."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

def executar_agente():
    print("🚀 Agente iniciado...")
    bot.send_message(CHAT_ID, "🛡️ **Radar de Ouro Ativado.** Monitorando fluxo de baleias e DXY 24h.")
    
    while True:
        try:
            dados = buscar_dados_mercado()
            relatorio = analisar_com_gemini(dados)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO INSIDER** ⚠️\n\n{relatorio}", parse_mode='Markdown')
            time.sleep(3600) 
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    executar_agente()
