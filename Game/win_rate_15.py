import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MEU_TOKEN")
headers = {"accept": "application/json", "authorization": f"Bearer {TOKEN}"}

def consultar_winrate(team_id):
    url = f"https://api.pandascore.co/teams/{team_id}/matches"
    params = {"filter[status]": "finished", "per_page": 15}
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            partidas = r.json()
            if not partidas or not isinstance(partidas, list): return 0
            vits = sum(1 for p in partidas if p.get('winner_id') == team_id)
            return (vits / len(partidas)) * 100
    except: return 0
    return 0

def consultar_h2h(id_a, id_b):
    url = "https://api.pandascore.co/matches/past"
    params = {"filter[opponent_id]": f"{id_a},{id_b}", "per_page": 50}
    v_a, v_b, total = 0, 0, 0
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            partidas = r.json()
            for m in partidas:
                winner = m.get('winner_id')
                if winner == id_a: v_a += 1
                elif winner == id_b: v_b += 1
                total += 1
            return {"total": total, "v_a": v_a, "v_b": v_b}
    except: return None

def consultar_map_pool(team_id):
    """Busca mapas abrindo as partidas do Win Rate com filtro de título"""
    url = f"https://api.pandascore.co/teams/{team_id}/matches"
    
    params = {
        "filter[status]": "finished",
        "videogame_title": "cs-2", 
        "per_page": 50 
    }
    
    map_stats = {}
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            partidas = r.json()
            for p in partidas:
                games = p.get('games', [])
                for g in games:
                    map_obj = g.get('map')
                    if map_obj and map_obj.get('name'):
                        m_name = map_obj['name'].replace('de_', '').capitalize()
                        if m_name in ["Default", "Unknown", "Tbd"]: continue
                        winner = g.get('winner')
                        vitoria = 1 if winner and winner.get('id') == team_id else 0
                        if m_name not in map_stats:
                            map_stats[m_name] = {"v": 0, "t": 0}
                        map_stats[m_name]["t"] += 1
                        map_stats[m_name]["v"] += vitoria
            
            resultado = {m: {"wr": (d["v"]/d["t"])*100, "j": d["t"]} for m, d in map_stats.items()}
            return resultado
    except Exception as e:
        print(f"Erro ao processar mapas: {e}")
    return {}
def analisar_pelo_match_id():
    print("\n" + "="*65)
    print(" ANALISADOR PRO CS2 - DADOS TOTAIS E MAP POOL ")
    print("="*65)
    
    match_id = input("Digite o ID do Jogo: ").strip()
    url_match = f"https://api.pandascore.co/matches/{match_id}"
    
    try:
        res = requests.get(url_match, headers=headers)
        if res.status_code != 200:
            print(f"Erro ao acessar API: {res.status_code}")
            return
            
        jogo = res.json()
        
        opponents = jogo.get('opponents')
        if not opponents or len(opponents) < 2:
            print("Aviso: Times ainda não definidos para este ID.")
            return

        time_a = opponents[0].get('opponent')
        time_b = opponents[1].get('opponent')
        
        if not time_a or not time_b:
            print("Erro: Dados dos times estão incompletos na API.")
            return

        print(f"\nCONFRONTO: {time_a['name']} vs {time_b['name']}")
        print(f"LIGA: {jogo.get('league', {}).get('name', 'N/A')}")

        wr_a = consultar_winrate(time_a['id'])
        wr_b = consultar_winrate(time_b['id'])
        h2h = consultar_h2h(time_a['id'], time_b['id'])
        pool_a = consultar_map_pool(time_a['id'])
        pool_b = consultar_map_pool(time_b['id'])

        print("-" * 65)
        print(f"{'TIME':<25} | {'WIN RATE GERAL':<20}")
        print(f"{time_a['name']:<25} | {wr_a:>18.1f}%")
        print(f"{time_b['name']:<25} | {wr_b:>18.1f}%")
        print("-" * 65)

        if h2h and h2h['total'] > 0:
            print(f"H2H DIRETO: {h2h['total']} jogos | {time_a['name']}: {h2h['v_a']} | {time_b['name']}: {h2h['v_b']}")
        else:
            print("Sem histórico de confrontos diretos.")
        print("-" * 65)

        print(f"{'MAPA':<15} | {time_a['name'][:15]:<18} | {time_b['name'][:15]:<18}")
        print("-" * 65)

        mapas_ativos = ['Mirage', 'Inferno', 'Nuke', 'Ancient', 'Anubis', 'Vertigo', 'Dust2']
        tem_dados = False
        for m in mapas_ativos:
            s_a = pool_a.get(m, {"wr": 0, "j": 0})
            s_b = pool_b.get(m, {"wr": 0, "j": 0})
            
            if s_a['j'] > 0 or s_b['j'] > 0:
                tem_dados = True
                txt_a = f"{s_a['wr']:.0f}% ({s_a['j']}j)"
                txt_b = f"{s_b['wr']:.0f}% ({s_b['j']}j)"
                print(f"{m:<15} | {txt_a:<18} | {txt_b:<18}")
        
        if not tem_dados:
            print("Dados de mapas não encontrados para este confronto.")
        print("-" * 65)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    analisar_pelo_match_id()
    