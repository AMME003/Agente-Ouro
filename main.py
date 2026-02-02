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
        # API 1: Metals-API (gratuita, dados reais de commodities)
        metals_url = "https://api.metals.live/v1/spot/gold"
        try:
            metals_res = requests.get(metals_url, timeout=10)
            metals_data = metals_res.json()
            
            # metals.live retorna array de dados
            if isinstance(metals_data, list) and len(metals_data) > 0:
                ouro_price = metals_data[0].get('price')
                if ouro_price:
                    ouro = f"{ouro_price:.2f}"
                    print(f"  [metals.live] Ouro: {ouro}")
            else:
                ouro = None
        except Exception as e:
            print(f"  [metals.live] Falhou: {e}")
            ouro = None
        
        # API 2: Goldapi.io (gratuita, 100 requests/mes)
        if not ouro:
            try:
                goldapi_url = "https://www.goldapi.io/api/XAU/USD"
                goldapi_headers = {"x-access-token": "goldapi-demo"}  # Use API key real se tiver
                gold_res = requests.get(goldapi_url, headers=goldapi_headers, timeout=10)
                gold_data = gold_res.json()
                
                if 'price' in gold_data:
                    ouro = f"{gold_data['price']:.2f}"
                    print(f"  [goldapi.io] Ouro: {ouro}")
            except Exception as e:
                print(f"  [goldapi.io] Falhou: {e}")
        
        # API 3: Twelve Data (gratuita, 800 calls/dia) - MELHOR OPCAO
        if not ouro:
            try:
                twelve_url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={os.environ.get('TWELVE_API_KEY')}"
                twelve_res = requests.get(twelve_url, timeout=10)
                twelve_data = twelve_res.json()
                
                if 'price' in twelve_data:
                    ouro = f"{float(twelve_data['price']):.2f}"
                    print(f"  [twelvedata] Ouro: {ouro}")
            except Exception as e:
                print(f"  [twelvedata] Falhou: {e}")
        
        # Buscar DXY
        dxy = None
        
        # API: Twelve Data para DXY
        try:
            dxy_url = "https://api.twelvedata.com/price?symbol=DXY&apikey=demo"
            dxy_res = requests.get(dxy_url, timeout=10)
            dxy_data = dxy_res.json()
            
            if 'price' in dxy_data:
                dxy = f"{float(dxy_data['price']):.2f}"
                print(f"  [twelvedata] DXY: {dxy}")
        except Exception as e:
            print(f"  DXY falhou: {e}")
        
        # Resultado final
        ouro_final = ouro if ouro else "ERRO"
        dxy_final = dxy if dxy else "ERRO"
        
        if ouro_final == "ERRO" or dxy_final == "ERRO":
            return f"XAUUSD: {ouro_final} | DXY: {dxy_final} (APIs indisponiveis - aguarde proximo ciclo)"
        
        return f"XAUUSD: {ouro_final} | DXY: {dxy_final}"
        
    except Exception as e:
        print(f"ERRO GERAL buscar_precos: {e}")
        traceback.print_exc()
        return "XAUUSD: ERRO | DXY: ERRO (Falha nas APIs)"

def buscar_noticias():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tentar diferentes seletores
        noticias = []
        
        # Seletor 1
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:8]]
        
        # Seletor 2 (se falhar)
        if not noticias:
            noticias = [a.text.strip() for a in soup.find_all('a', attrs={'data-test': 'article-title-link'})[:8]]
        
        # Seletor 3
        if not noticias:
            noticias = [h2.text.strip() for h2 in soup.find_all('h2')[:8]]
        
        if noticias and len(noticias) > 2:
            return " | ".join(noticias)
        
        return "Noticias nao disponiveis no momento"
        
    except Exception as e:
        print(f"ERRO buscar_noticias: {e}")
        return "Sem noticias"

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
                    "content": """Voce e um TRADER INSIDER profissional especializado em XAUUSD e DXY.

REGRAS CRITICAS:
- Se precos mostrarem "ERRO", SEMPRE mencione que dados estao indisponiveis e aguarde proximo ciclo
- Use APENAS precos numericos reais fornecidos
- NUNCA invente precos

SEU OBJETIVO:

1. IDENTIFICAR BRECHAS:
   - Decisoes de Fed/BCE/BoJ
   - Dados economicos (NFP, CPI, PMI)
   - Tensoes geopoliticas
   - Sentiment shifts

2. ANTECIPAR BIG PLAYERS:
   - Fluxo institucional para safe-haven
   - Central banks buying gold
   - Hedge funds positioning
   - Correlation breaks

3. GERAR CALL DIRETO:

FORMATO:
🎯 CALL: [COMPRA/VENDA]
📊 Entrada: [preco exato fornecido]
🛡️ Stop Loss: [preco]
💰 Take Profit: [preco]
⚡ Justificativa: [2-3 linhas brutais]
🔍 Sinais Ocultos: [smart money flows]

SEJA DIRETO E AGRESSIVO."""
                },
                {
                    "role": "user",
                    "content": f"""DADOS REAIS ATUAIS:
{precos}

NOTICIAS RECENTES:
{noticias}

Gere CALL com base nos dados REAIS fornecidos."""
                }
            ],
            "max_tokens": 800,
            "temperature": 0.6
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if 'error' in result:
            return f"ERRO OPENAI: {result['error'].get('message')}"
        
        if 'choices' not in result:
            return "Resposta invalida da API"
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"ERRO analisar_insider: {e}")
        traceback.print_exc()
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    print("=" * 50)
    print("AGENTE INSIDER - DADOS REAIS")
    print("=" * 50)
    
    try:
        bot.send_message(CHAT_ID, "🔥 AGENTE INSIDER ATIVADO 🔥\n\nDados em tempo real ativados...")
        print("✓ Bot iniciado")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    contador = 0
    
    while True:
        try:
            contador += 1
            print("\n" + "=" * 50)
            print(f"CICLO #{contador} - {time.strftime('%d/%m %H:%M:%S')}")
            print("=" * 50)
            
            print("→ Buscando precos REAIS (testando 3 APIs)...")
            precos = buscar_precos()
            print(f"  RESULTADO: {precos}")
            
            # Se precos falharam, aguardar e tentar novamente
            if "ERRO" in precos:
                print("⚠️ APIs indisponiveis, aguardando 2 minutos...")
                time.sleep(120)
                continue
            
            print("→ Buscando noticias...")
            noticias = buscar_noticias()
            print(f"  {len(noticias)} caracteres")
            
            print("→ Processando IA INSIDER...")
            call = analisar_insider(precos, noticias)
            
            print("→ Enviando CALL...")
            mensagem = f"⚡ INSIDER #{contador} ⚡\n{time.strftime('%d/%m %H:%M')}\n\n{precos}\n\n{call}"
            bot.send_message(CHAT_ID, mensagem)
            print("✓ CALL ENVIADO!")
            
            print(f"\n⏰ Proximo call: {time.strftime('%H:%M', time.localtime(time.time() + 3600))}")
            time.sleep(3600)
            
        except Exception as e:
            print(f"✗ ERRO: {e}")
            traceback.print_exc()
            time.sleep(300)
