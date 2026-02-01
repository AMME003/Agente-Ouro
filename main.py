import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Config
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar():
    try:
        res = requests.get("https://www.investing.com/commodities/gold-news", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return " | ".join([a.text.strip() for a in soup.find_all('a', class_='title')[:5]])
    except: return "Erro na busca"

def analisar(dados):
    try:
        return model.generate_content(f"Analise como insider: {dados}. Foco em baleias e DXY.").text
    except: return "Erro na IA"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ Agente Ativado.")
    while True:
        try:
            relatorio = analisar(buscar())
            bot.send_message(CHAT_ID, f"⚠️ RELATÓRIO: {relatorio}")
            time.sleep(3600)
        except: time.sleep(60)
