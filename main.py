import os
import telebot
import requests
import time
from bs4 import BeautifulSoup
import traceback

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "735855732"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def buscar_precos():
    try:
        # API gratuita de forex/commodities
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Calcular preco aproximado do ouro (inverso)
        # XAU = onca troy de ouro em USD
        # Usando proxy: buscar de outra API
        
        # Alternativa: API metals
        metals_url = "https://api.metals.live/v1/spot"
        metals_res = requests.get(metals_url, timeout=10)
        metals_data = metals_res.json()
        
        ouro = None
        for metal in metals_data:
            if metal.get('metal') == 'gold':
                ouro = metal.get('price')
                break
        
        # DXY via outra fonte
        dxy_url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey=demo"
        
        if ouro:
            ouro_str = f"{ouro:.2f}"
        else:
            ouro_str = "N/A"
        
        # Buscar DXY de forma alternativa (via correlacao EUR/USD inversa)
        try:
            eurusd_url = "https://api.fxratesapi.com/latest?base=USD&symbols=EUR"
            eur_res = requests.get(eurusd_url, timeout=10)
            eur_data = eur_res.json()
            eur_rate = eur_data.get('rates', {}).get('EUR', 0)
            
            # DXY aproximado (correlacao inversa com EUR/USD)
            if eur_rate > 0:
                dxy_aprox = 100 / eur_rate * 0.57  # Fator de ajuste
                dxy_str = f"{dxy_aprox:.2f}"
            else:
                dxy_str = "N/A"
        except:
            dxy_str = "N/A"
        
        return f"XAUUSD: {ouro_str} | DXY: {dxy_str}"
        
    except Exception as e:
        print(f"ERRO buscar_precos: {e}")
        traceback.print_exc()
        
        # FALLBACK: Usar precos hardcoded recentes se APIs falharem
        return "XAUUSD: 2719.50 (estimado) | DXY: 108.20 (estimado)"

def buscar_noticias():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Tentar diferentes fontes
        urls = [
            "https://www.investing.com/commodities/gold-news",
            "https://www.marketwatch.com/investing/future/gc00",
            "https://www.kitco.com/news/"
        ]
        
        for url in urls:
            try:
                res = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Investing.com
                if 'investing.com' in url:
                    noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:8]]
                # MarketWatch
                elif 'marketwatch.com' in url:
                    noticias = [h.text.strip() for h in soup.find_all('h3', class_='article__headline')[:8]]
                # Kitco
                elif 'kitco.com' in url:
                    noticias = [a.text.strip() for a in soup.find_all('a', class_='news-analysis__title')[:8]]
                
                if noticias and len(noticias) > 0:
                    return " | ".join(noticias)
            except:
                continue
        
        return "Noticias nao disponiveis no momento"
        
    except Exception as e:
        print(f"ERRO buscar_noticias: {e}")
        return "Noticias nao disponiveis"

def analisar_insider(precos, noticias):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_KEY}'
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": """Voce e um TRADER INSIDER profissional. 

IMPORTANTE: Se os precos estiverem como "estimado" ou "N/A", SEMPRE mencione que sao estimativas e que o trader deve CONFIRMAR OS PRECOS REAIS antes de entrar.

Seu objetivo:

1. IDENTIFICAR BRECHAS nas noticias:
   - Declaracoes de Fed/BCE/BoJ
   - Dados economicos surpresa
   - Mudancas em politicas monetarias
   - Sentimento de risco (risk-on/risk-off)

2. ANTECIPAR BIG PLAYERS:
   - Fluxo institucional
   - Safe-haven flows
   - Correlacoes ouro/dolar/bonds
   - Posicionamento de bancos centrais

3. GERAR CALL DIRETO com precos REAIS ou ESTIMADOS:

FORMATO OBRIGATORIO:
🎯 CALL: [COMPRA/VENDA]
📊 Entrada: [preco] (CONFIRMAR PRECO REAL)
🛡️ Stop Loss: [preco]
💰 Take Profit: [preco]
⚡ Justificativa: [2-3 linhas]
🔍 Sinais Ocultos: [big players]

Se precos estiverem "N/A", use logica baseada em noticias e tendencias."""
                },
                {
                    "role": "user",
                    "content": f"""DADOS:
{precos}

NOTICIAS:
{noticias}

Gere um CALL AGORA."""
                }
            ],
            "max_tokens": 800,
            "temperature": 0.6
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if 'error' in result:
            return f"ERRO: {result['error'].get('message', 'Erro')}"
        
        if 'choices' not in result:
            return f"Resposta invalida"
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"ERRO analisar_insider: {e}")
        traceback.print_exc()
        return f"Erro na analise: {str(e)}"

if __name__ == "__main__":
    print("=" * 50)
    print("INICIANDO AGENTE INSIDER")
    print("=" * 50)
    
    try:
        bot.send_message(CHAT_ID, "🔥 AGENTE INSIDER ATIVADO 🔥\n\nMonitorando mercado 24/7...")
        print("✓ Mensagem inicial enviada")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    contador = 0
    
    while True:
        try:
            contador += 1
            print("\n" + "=" * 50)
            print(f"CICLO #{contador} - {time.strftime('%H:%M:%S')}")
            print("=" * 50)
            
            print("→ Buscando precos...")
            precos = buscar_precos()
            print(f"  {precos}")
            
            print("→ Buscando noticias...")
            noticias = buscar_noticias()
            print(f"  {len(noticias)} caracteres")
            
            print("→ Processando IA...")
            call = analisar_insider(precos, noticias)
            
            print("→ Enviando...")
            mensagem = f"⚡ INSIDER #{contador} ⚡\n\n{precos}\n\n{call}"
            bot.send_message(CHAT_ID, mensagem)
            print("✓ ENVIADO!")
            
            print(f"\n⏰ Proximo: {time.strftime('%H:%M', time.localtime(time.time() + 3600))}")
            time.sleep(3600)
            
        except Exception as e:
            print(f"✗ ERRO: {e}")
            traceback.print_exc()
            time.sleep(300)
