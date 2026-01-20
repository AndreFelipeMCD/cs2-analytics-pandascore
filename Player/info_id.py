import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MEU_TOKEN")
headers = {"accept": "application/json", "authorization": f"Bearer {TOKEN}"}

def buscar_performance_avancada():
    player_id = input("\nDigite o ID do Jogador: ").strip()
    
    res_p = requests.get(f"https://api.pandascore.co/players/{player_id}", headers=headers).json()
    player_name = res_p.get('name', 'Jogador')
    
    url_m = f"https://api.pandascore.co/players/{player_id}/matches"
    params = {"filter[status]": "finished", "sort": "-begin_at", "per_page": 5}
    partidas = requests.get(url_m, headers=headers, params=params).json()

    print(f"\n ANÁLISE DE KILLS: {player_name.upper()}")
    print("-" * 95)
    print(f"{'DATA':<12} | {'TIPO':<5} | {'ADVERSÁRIO':<15} | {'PLACAR'} | {'KILLS':<10} | {'FONTE'}")
    print("-" * 95)

    for m in partidas:
        data = datetime.strptime(m['begin_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
        tipo = f"MD{m['number_of_games']}"
        adv = "Oponente"
        for opp in m.get('opponents', []):
            if opp['opponent'].get('id') != m.get('current_team', {}).get('id'):
                adv = opp['opponent']['name']

        kills_reais = 0
        teve_dado_real = False
        res_d = requests.get(f"https://api.pandascore.co/matches/{m['id']}", headers=headers).json()
        
        rounds_totais = 0
        for game in res_d.get('games', []):
            for p_stat in game.get('player_stats', []):
                if p_stat.get('player_id') == int(player_id):
                    kills_reais += p_stat.get('kills', 0)
                    teve_dado_real = True
            
            if not teve_dado_real:
                rounds_totais += (game.get('status_maps', [{}])[0].get('score', 0) if game.get('status_maps') else 0)
                if rounds_totais == 0: rounds_totais += 22

        if teve_dado_real and kills_reais > 0:
            exibicao_kills = f"{kills_reais}"
            fonte = "REAL (API)"
        else:
            est_tecnica = int(rounds_totais * 0.72)
            exibicao_kills = f"~{est_tecnica}"
            fonte = "EST. TÉCNICA"

        print(f"{data:<12} | {tipo:<5} | {adv[:15]:<15} | {m['results'][0]['score']}-{m['results'][1]['score']:<6} | {exibicao_kills:<10} | {fonte}")

    print("-" * 95)
    print("DICA: Se aparecer 'EST. TÉCNICA', a API não enviou a súmula. Use o valor como base de volume.")

if __name__ == "__main__":
    buscar_performance_avancada()