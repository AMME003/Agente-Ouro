import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Pega as chaves que já estão no seu Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Configuração que realmente funciona
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar():
    try:
        header = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=header, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except: return "Erro busca"

def analisar(dados):
    try:
        prompt = f"Analise como insider (Ouro/DXY): {dados}. Seja curto e bruto."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Sistema Estabilizado.** Monitorando...")
    while True:
        try:
            relatorio = analisar(buscar())
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) 
        except: time.sleep(60)
