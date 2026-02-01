import os, telebot, requests, time
import google.generativeai as genai
from bs4 import BeautifulSoup

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Forçamos a configuração da versão estável
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except:
        return "Erro na busca"

def analisar_mercado(dados):
    try:
        # Gerando conteúdo de forma simples e direta
        response = model.generate_content(f"Analise como trader (Ouro/DXY): {dados}")
        return response.text
    except Exception as e:
        return f"Erro na IA: {str(e)}"

if __name__ == "__main__":
    # Mensagem de boot para você saber que ele ligou
    bot.send_message(CHAT_ID, "🛡️ Agente Ouro ligado. Aguardando processamento...")
    while True:
        try:
            texto = buscar_noticias()
            relatorio = analisar_mercado(texto)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) # 1 hora de espera
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)
