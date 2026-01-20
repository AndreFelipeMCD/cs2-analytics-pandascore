import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MEU_TOKEN")
headers = {"accept": "application/json", "authorization": f"Bearer {TOKEN}"}

def analisar_jogadores_partida():
    print("\n" + "="*70)
    print(" 🎯 ELENCO DOS TIMES (CS2) ")
    print("="*70)
    
    match_id = input("Digite o ID do Jogo: ").strip()
    url_match = f"https://api.pandascore.co/matches/{match_id}"
    
    try:
        res = requests.get(url_match, headers=headers)
        if res.status_code != 200:
            print("Jogo não encontrado.")
            return
        jogo = res.json()
        opponents = jogo.get('opponents', [])
        for opp in opponents:
            time_nome = opp['opponent']['name']
            time_id = opp['opponent']['id']
            
            print(f"\n📋 ELENCO: {time_nome.upper()}")
            print("-" * 70)
            
            url_team = f"https://api.pandascore.co/teams/{time_id}"
            res_team = requests.get(url_team, headers=headers)
            
            if res_team.status_code == 200:
                jogadores = res_team.json().get('players', [])
                lista_jogadores = []
                
                for pj in jogadores:
                    lista_jogadores.append({
                        "PLAYER": pj.get('name'),
                        "NOME REAL": f"{pj.get('first_name')} {pj.get('last_name')}",
                        "ID": pj.get('id'),
                        "NAC": pj.get('nationality')
                    })
                
                df = pd.DataFrame(lista_jogadores)
                print(df.to_string(index=False))
            else:
                print(f"Não foi possível carregar os jogadores do time {time_nome}")

        print("\n" + "="*70)
        print("ELENCO DE AMBOS OS TIMES.")
        print("="*70)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    analisar_jogadores_partida()