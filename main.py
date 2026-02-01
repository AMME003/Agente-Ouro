import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Configuração via Environment Variables do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicialização estável
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except Exception as e:
        return f"Erro busca: {str(e)}"

def analisar(dados):
    try:
        # Prompt focado na sua missão de Ouro e DXY
        prompt = f"Analise estas notícias como insider de mercado focado em baleias, Ouro e DXY: {dados}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro técnico na IA: {str(e)}"

if __name__ == "__main__":
    print("🚀 Agente Online...")
    # Confirmação para o seu ID pessoal
    bot.send_message(CHAT_ID, "🛡️ **Sistema Estabilizado.** Monitorando XAUUSD e DXY...")
    while True:
        try:
            texto_noticias = buscar()
            relatorio = analisar(texto_noticias)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) # Relatórios de hora em hora
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)
