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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        res_ouro = requests.get("https://www.investing.com/currencies/xau-usd", headers=headers, timeout=15)
        soup_ouro = BeautifulSoup(res_ouro.text, 'html.parser')
        preco_ouro = soup_ouro.find('span', {'data-test': 'instrument-price-last'})
        ouro = preco_ouro.text.strip() if preco_ouro else "N/A"
        
        res_dxy = requests.get("https://www.investing.com/indices/usdollar", headers=headers, timeout=15)
        soup_dxy = BeautifulSoup(res_dxy.text, 'html.parser')
        preco_dxy = soup_dxy.find('span', {'data-test': 'instrument-price-last'})
        dxy = preco_dxy.text.strip() if preco_dxy else "N/A"
        
        return f"XAUUSD: {ouro} | DXY: {dxy}"
        
    except Exception as e:
        print(f"ERRO buscar_precos: {e}")
        return "XAUUSD: N/A | DXY: N/A"

def buscar_noticias():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get("https://www.investing.com/commodities/gold-news", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [a.text.strip() for a in soup.find_all('a', class_='title')[:8]]
        return " | ".join(noticias) if noticias else "Sem noticias"
    except Exception as e:
        print(f"ERRO buscar_noticias: {e}")
        return "Sem noticias disponiveis"

def buscar_analise_tecnica():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get("https://www.investing.com/currencies/xau-usd-technical", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        resumo = soup.find('div', class_='summary')
        if resumo:
            return resumo.text.strip()[:200]
        return "Analise tecnica nao disponivel"
    except Exception as e:
        print(f"ERRO buscar_analise_tecnica: {e}")
        return "Analise tecnica nao disponivel"

def analisar_insider(precos, noticias, tecnica):
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
                    "content": """Voce e um TRADER INSIDER com acesso a informacoes privilegiadas. Seu objetivo:

1. IDENTIFICAR BRECHAS: Analise noticias procurando por:
   - Declaracoes de bancos centrais (Fed, BCE, BoJ)
   - Mudancas em politicas monetarias
   - Dados economicos fora do esperado
   - Movimentacoes incomuns de volume

2. ANTECIPAR BIG PLAYERS: Detecte sinais de:
   - Bancos acumulando ou vendendo ouro
   - Fundos institucionais reposicionando carteiras
   - Fluxo de capital entre ativos safe-haven
   - Correlacoes anormais ouro/dolar/bonds

3. GERAR CALL DIRETO: 
   - CALL DE COMPRA: Se identificar acumulacao institucional, divergencias altistas, ou catalisadores positivos
   - CALL DE VENDA: Se identificar distribuicao, sinais de topo, ou catalisadores negativos
   - Sempre inclua: Preco de entrada sugerido, Stop Loss, Take Profit, justificativa

4. SEJA BRUTAL E DIRETO: Sem enrolacao. Vai direto ao ponto.

FORMATO OBRIGATORIO:
🎯 CALL: [COMPRA/VENDA]
📊 Entrada: [preco]
🛡️ Stop Loss: [preco]
💰 Take Profit: [preco]
⚡ Justificativa: [analise insider em 2-3 linhas]
🔍 Sinais Ocultos: [o que os big players estao fazendo]"""
                },
                {
                    "role": "user",
                    "content": f"""DADOS ATUAIS:
{precos}

ANALISE TECNICA:
{tecnica}

NOTICIAS (ultimas 8):
{noticias}

ANALISE COMO INSIDER e gere um CALL agora."""
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
            return f"Resposta invalida: {result}"
        
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
        bot.send_message(CHAT_ID, "🔥 AGENTE INSIDER ATIVADO 🔥\n\nMonitorando mercado 24/7 para calls agressivos...")
        print("✓ Mensagem inicial enviada")
    except Exception as e:
        print(f"✗ Erro ao enviar mensagem inicial: {e}")
    
    contador = 0
    
    while True:
        try:
            contador += 1
            print("\n" + "=" * 50)
            print(f"CICLO #{contador} - {time.strftime('%d/%m/%Y %H:%M:%S')}")
            print("=" * 50)
            
            print("→ Buscando precos...")
            precos = buscar_precos()
            print(f"  Precos: {precos}")
            
            print("→ Buscando noticias...")
            noticias = buscar_noticias()
            print(f"  Noticias: {len(noticias)} caracteres")
            
            print("→ Buscando analise tecnica...")
            tecnica = buscar_analise_tecnica()
            print(f"  Tecnica: {tecnica[:50]}...")
            
            print("→ Processando com IA...")
            call = analisar_insider(precos, noticias, tecnica)
            print(f"  Resposta: {len(call)} caracteres")
            
            print("→ Enviando para Telegram...")
            mensagem = f"⚡ RELATORIO INSIDER #{contador} ⚡\n\n{precos}\n\n{call}"
            bot.send_message(CHAT_ID, mensagem)
            print("✓ CALL ENVIADO COM SUCESSO!")
            
            print(f"\n⏰ Proximo call em 1 hora (as {time.strftime('%H:%M', time.localtime(time.time() + 3600))})")
            print("=" * 50)
            
            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("\n\n✗ Bot interrompido pelo usuario")
            break
            
        except Exception as e:
            print(f"\n✗ ERRO NO LOOP PRINCIPAL: {e}")
            traceback.print_exc()
            print("\n⏰ Aguardando 5 minutos antes de tentar novamente...")
            time.sleep(300)

