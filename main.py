import os, telebot, requests, time

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_dados():
    try:
        res = requests.get("https://www.investing.com/commodities/gold-news", 
                           headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except: return "Erro na busca"

def analisar_ia(dados):
    # Mudança para o modelo 1.0-pro (Máxima compatibilidade)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Analise como insider (Ouro/DXY): {dados}. Seja curto e bruto."}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        res_json = response.json()
        
        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"ERRO FINAL: {res_json.get('error', {}).get('message', 'Acesse o link do passo 2')}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Agente Ouro: Forçando Conexão Estável...**")
    while True:
        try:
            relatorio = analisar_ia(buscar_dados())
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) 
        except: time.sleep(60)
