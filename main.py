import os
import telebot
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time

# 1. Configurações de Ambiente (Puxa do Render/Secrets)
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 2. Inicialização das IAs e Bot
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados_mercado():
    """Busca notícias e sentimentos sobre Ouro e Dólar."""
    url = "https://www.investing.com/commodities/gold-news"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Pega as manchetes principais
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias)
    except Exception as e:
        return f"Erro ao buscar notícias: {e}"

def analisar_com_gemini(dados):
    """O 'Cérebro' do robô analisa se há sinais de insiders ou baleias."""
    prompt = (
        f"Você é um especialista em análise de fluxo e geopolítica. Analise estas notícias: {dados}. "
        "Busque especificamente por: 1. Movimentação de baleias (grandes volumes). 2. Manipulação de preço. "
        "3. Correlação inversa com o DXY (Dólar). 4. Compras de Bancos Centrais. "
        "Responda de forma curta e 'brutalmente honesta' para um investidor de elite."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na análise da IA: {e}"

def executar_agente():
    """Loop principal
