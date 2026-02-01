import os, telebot, requests, time
from google import genai
from bs4 import BeautifulSoup

# Configurações obtidas do Environment Variables do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732" # Seu ID confirmado

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias no momento."
    except Exception as e:
        return f"Erro na busca: {str(e)}"

def analisar_mercado(dados):
    try:
        # Usando o modelo estável 1.5-flash
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Analise como insider de mercado (XAUUSD e DXY): {dados}"
        )
        return response.text
    except Exception as e:
        return f"Erro técnico na IA: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Agente Ouro Online e Atualizado.**")
    while True:
        try:
            dados = buscar_noticias()
            relatorio = analisar_mercado(dados)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO INSIDER:**\n\n{relatorio}")
            time.sleep(3600) # Monitora de hora em hora
        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(60)
