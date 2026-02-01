import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Puxa as configurações que você já salvou no Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Configuração estável da IA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        header = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=header, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias agora."
    except Exception as e:
        return f"Erro na busca: {str(e)}"

def analisar_ia(dados):
    try:
        # Prompt direto para o seu perfil de investidor
        prompt = f"Analise como insider de mercado (XAUUSD/DXY): {dados}. Seja brutalmente honesto."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {str(e)}"

if __name__ == "__main__":
    print("🚀 Iniciando...")
    bot.send_message(CHAT_ID, "🛡️ **Sistema Online.** Monitorando Ouro e Dólar...")
    while True:
        try:
            dados_mercado = buscar_dados()
            relatorio = analisar_ia(dados_mercado)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) # 1 hora de intervalo
        except Exception as e:
            time.sleep(60)
