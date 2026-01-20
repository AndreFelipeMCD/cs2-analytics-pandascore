import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MEU_TOKEN")
headers = {"accept": "application/json", "authorization": f"Bearer {TOKEN}"}

def analisar_confronto_pelo_jogo():
    match_id = input("\nDigite o ID do Jogo (Match ID): ").strip()
    
    # 1. Busca os detalhes da partida para descobrir quem são os times
    url_match = f"https://api.pandascore.co/matches/{match_id}"
    res_m = requests.get(url_match, headers=headers).json()

    if 'opponents' not in res_m or len(res_m['opponents']) < 2:
        print("❌ Não foi possível encontrar os dois times para este ID de jogo.")
        return

    times = [
        {"id": res_m['opponents'][0]['opponent']['id'], "name": res_m['opponents'][0]['opponent']['name']},
        {"id": res_m['opponents'][1]['opponent']['id'], "name": res_m['opponents'][1]['opponent']['name']}
    ]

    print(f"\n🔥 ANALISANDO CONFRONTO: {times[0]['name']} VS {times[1]['name']}")
    print("=" * 70)

    stats_times = []

    # 2. Loop para analisar cada um dos dois times
    for t in times:
        url_t = f"https://api.pandascore.co/teams/{t['id']}/matches"
        params = {"filter[status]": "finished", "per_page": 10}
        partidas = requests.get(url_t, headers=headers, params=params).json()

        vitorias = 0
        jogos_3_mapas = 0
        total_jogos = len(partidas)

        for m in partidas:
            if m.get('winner_id') == t['id']:
                vitorias += 1
            
            res = m.get('results', [])
            if len(res) >= 2:
                # Soma os placares: se deu 2-1 ou 1-2, a soma é 3 (Over 2.5)
                if (res[0]['score'] + res[1]['score']) >= 3:
                    jogos_3_mapas += 1

        wr = (vitorias / total_jogos * 100) if total_jogos > 0 else 0
        ov25 = (jogos_3_mapas / total_jogos * 100) if total_jogos > 0 else 0
        
        stats_times.append({"wr": wr, "ov25": ov25})
        
        print(f"📋 TIME: {t['name']}")
        print(f"   👉 Win Rate: {wr:.1f}% | Tendência Over 2.5: {ov25:.1f}%")
        print("-" * 70)

    # 3. Lógica de Decisão de Aposta
    wr_diff = abs(stats_times[0]['wr'] - stats_times[1]['wr'])
    media_ov25 = (stats_times[0]['ov25'] + stats_times[1]['ov25']) / 2

    print("💡 CONCLUSÃO PARA APOSTA:")
    if wr_diff < 15 and media_ov25 > 50:
        print("💎 ALTA CHANCE DE OVER 2.5: Times parelhos e com histórico de 3 mapas!")
    elif wr_diff > 40:
        fav = times[0]['name'] if stats_times[0]['wr'] > stats_times[1]['wr'] else times[1]['name']
        print(f"🚜 ALTA CHANCE DE 2-0 (UNDER 2.5): {fav} é muito superior.")
    else:
        print("⚠️ JOGO EQUILIBRADO: Melhor ir no 'Vencedor Partida' em vez de total de mapas.")
    print("=" * 70)

if __name__ == "__main__":
    analisar_confronto_pelo_jogo()