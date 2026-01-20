import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MEU_TOKEN")
URL_BASE = "https://api.pandascore.co/csgo/matches"
headers = {"accept": "application/json", "authorization": f"Bearer {TOKEN}"}

def analisar_confronto_completo():
    match_id = input("\nDigite o ID do Jogo (Match ID): ").strip()
    
    url_match = f"https://api.pandascore.co/matches/{match_id}"
    res_m = requests.get(url_match, headers=headers).json()

    if 'opponents' not in res_m or len(res_m['opponents']) < 2:
        print(" Não foi possível encontrar os times para este ID.")
        return

    times = [
        {"id": res_m['opponents'][0]['opponent']['id'], "name": res_m['opponents'][0]['opponent']['name']},
        {"id": res_m['opponents'][1]['opponent']['id'], "name": res_m['opponents'][1]['opponent']['name']}
    ]

    print(f"\n ANÁLISE COMPLETA: {times[0]['name']} VS {times[1]['name']}")
    
    stats_confronto = []

    for t in times:
        print("\n" + "="*70)
        print(f" TIME: {t['name'].upper()}")
        print("-" * 70)
        
        url_t = f"https://api.pandascore.co/teams/{t['id']}/matches"
        params = {"filter[status]": "finished", "per_page": 5} 
        partidas = requests.get(url_t, headers=headers, params=params).json()

        vitorias = 0
        ov25_count = 0
        
        print(f"{'DATA':<12} | {'ADVERSÁRIO':<20} | {'PLACAR':<8} | {'STATUS'}")
        
        for m in partidas:
            data = datetime.strptime(m['begin_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
            
            adv = "Desconhecido"
            for opp in m['opponents']:
                if opp['opponent']['id'] != t['id']:
                    adv = opp['opponent']['name']
            
            res = m.get('results', [])
            s1 = res[0]['score'] if len(res) > 0 else 0
            s2 = res[1]['score'] if len(res) > 1 else 0
            placar_formatado = f"{s1}-{s2}"
            
            venceu = m.get('winner_id') == t['id']
            status = "VITÓRIA " if venceu else "DERROTA "
            if venceu: vitorias += 1
            
            if (s1 + s2) >= 3:
                ov25_count += 1
                placar_formatado += " (3 maps)"

            print(f"{data:<12} | {adv[:20]:<20} | {placar_formatado:<8} | {status}")

        wr = (vitorias / len(partidas) * 100) if partidas else 0
        ov_rate = (ov25_count / len(partidas) * 100) if partidas else 0
        stats_confronto.append({"wr": wr, "ov25": ov_rate})
        
        print("-" * 70)
        print(f" Resumo: Win Rate {wr:.0f}% | Tendência 3 Mapas: {ov_rate:.0f}%")

    print("\n" + " VEREDITO PARA APOSTA " + "="*47)
    diff = abs(stats_confronto[0]['wr'] - stats_confronto[1]['wr'])
    
    if diff > 40:
        print("Vitória seca do favorito ou Under 2.5 (Um time está muito melhor).")
    elif stats_confronto[0]['ov25'] >= 60 and stats_confronto[1]['ov25'] >= 60:
        print("Over 2.5 Mapas (Ambos os times costumam jogar 3 mapas).")
    else:
        print("Analise os placares acima. Se ambos vêm de vitórias, jogo tende a ser difícil.")
    print("="*70)

if __name__ == "__main__":
    analisar_confronto_completo()