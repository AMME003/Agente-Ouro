import os, telebot, requests, time
from google import genai
from bs4 import BeautifulSoup

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicializa as ferramentas modernas
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
        # Usa o modelo Gemini 2.0 Flash (o mais moderno e rápido)
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"Analise como insider de mercado focado em XAUUSD e DXY: {dados}. Seja brutalmente honesto."
        )
        return response.text
    except Exception as e:
        return f"Erro técnico na IA: {str(e)}"

if __name__ == "__main__":
    print("🚀 Agente Ouro Online...")
    bot.send_message(CHAT_ID, "🛡️ **Sistema Atualizado.** Iniciando monitoramento real...")
    while True:
        try:
            dados = buscar_noticias()
            relatorio = analisar_mercado(dados)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO INSIDER:**\n\n{relatorio}")
            time.sleep(3600) # Monitoramento de hora em hora
        except Exception as e:
            time.sleep(60)
