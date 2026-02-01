import os, telebot, requests, time

# Configurações do Render
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_noticias():
    try:
        res = requests.get("https://www.investing.com/commodities/gold-news", 
                           headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:5]]
        return " | ".join(noticias) if noticias else "Sem notícias."
    except: return "Erro na busca"

def analisar_ia(dados):
    # Chamada direta via API REST (Sem depender de biblioteca do Google)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Analise como insider (Ouro/DXY): {dados}. Seja curto e bruto."}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        res_json = response.json()
        # Se a chave estiver ruim, o erro aparecerá aqui detalhado
        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na Chave ou API: {res_json.get('error', {}).get('message', 'Erro desconhecido')}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🛡️ **Agente Ouro Modo Direto Ativado.**")
    while True:
        try:
            relatorio = analisar_ia(buscar_noticias())
            bot.send_message(CHAT_ID, f"⚠️ **RELATÓRIO:**\n\n{relatorio}")
            time.sleep(3600) 
        except: time.sleep(60)
