import os, telebot, requests, time
from google import genai
from bs4 import BeautifulSoup

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

# Inicializa o Cliente Moderno (SDK 2.0 - 2026)
client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias agora."
    except Exception as e:
        return f"Erro busca: {str(e)}"

def analisar_mercado(dados):
    try:
        # Sintaxe oficial: client.models.generate_content
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Analise como trader de elite focado em XAUUSD e DXY: {dados}. Seja curto, direto e brutalmente honesto."
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⏳ Limite de quota atingido. Aguardando liberação do Google..."
        return f"Erro técnico na IA: {str(e)}"

if __name__ == "__main__":
    print("🚀 Agente Ouro 2.0 Online...")
    # Mensagem de confirmação para o seu ID pessoal
    bot.send_message(CHAT_ID, "🛡️ **Agente Ouro 2.0 Ativado.** Monitoramento iniciado via SDK 2026.")
    
    while True:
        try:
            texto = buscar_noticias()
            relatorio = analisar_mercado(texto)
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO INSIDER:**\n\n{relatorio}")
            time.sleep(3600) # 1 hora de intervalo para respeitar a quota gratuita
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)
