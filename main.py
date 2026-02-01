import os, telebot, requests, time
from google import genai
from bs4 import BeautifulSoup

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias no momento."
    except Exception:
        return "Erro na busca"

def analisar_mercado(dados):
    try:
        # Mudamos para o 1.5-flash que tem limites mais generosos no plano grátis
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Analise como insider de mercado (Ouro e DXY): {dados}. Seja brutalmente honesto."
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⏳ Limite de requisições atingido. Aguardando o Google liberar..."
        return f"Erro técnico na IA: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Sistema Online.** Monitorando Ouro e Dólar...")
    while True:
        try:
            dados = buscar_noticias()
            relatorio = analisar_mercado(dados)
            
            # Só envia se não for mensagem de erro de limite
            if "Limite de requisições" not in relatorio:
                bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO INSIDER:**\n\n{relatorio}")
            
            # Intervalo de 1 hora para não estourar a quota gratuita novamente
            time.sleep(3600) 
        except Exception:
            time.sleep(60)
