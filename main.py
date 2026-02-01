import os, telebot, requests, time
from google import genai
from bs4 import BeautifulSoup

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Nova forma de inicializar (SDK 2.0)
client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        res = requests.get("https://www.investing.com/commodities/gold-news", 
                           headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except: return "Erro na busca"

def analisar_ia(dados):
    try:
        # Chamada oficial para o modelo 1.5-flash no novo SDK
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Analise como insider (Ouro/DXY): {dados}. Seja bruto."
        )
        return response.text
    except Exception as e:
        return f"Erro técnico: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Agente Ouro 2.0 Ativado.**")
    while True:
        try:
            relatorio = analisar_ia(buscar_dados())
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) 
        except: time.sleep(60)
