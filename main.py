import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Configuração via Environment Variables
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicializa o Gemini com a versão mais recente e estável
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Nenhuma notícia encontrada."
    except Exception as e:
        return f"Erro na busca: {str(e)}"

def analisar(dados):
    try:
        prompt = f"Analise como um trader insider focado em baleias e DXY: {dados}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Isso vai enviar o erro real (ex: API_KEY_INVALID ou MODEL_NOT_FOUND)
        return f"Erro Técnico na IA: {str(e)}"

if __name__ == "__main__":
    print("🚀 Iniciando Agente...")
    try:
        bot.send_message(CHAT_ID, "🛡️ **Sistema Reiniciado.** Verificando chaves...")
        while True:
            texto_noticias = buscar()
            relatorio = analisar(texto_noticias)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}", parse_mode='Markdown')
            time.sleep(3600)
    except Exception as e:
        print(f"Erro fatal: {e}")
