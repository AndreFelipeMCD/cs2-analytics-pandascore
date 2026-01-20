import requests
import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MEU_TOKEN")
arquivo = "proximas_partidas_cs2.csv"

if not token:
    raise Exception("Token não encontrado")

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {token}"
}

agora = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

url = "https://api.pandascore.co/csgo/matches"
params = {
    "range[begin_at]": f"{agora},2100-01-01T00:00:00Z",
    "sort": "begin_at",
    "per_page": 50
}

def buscar_proximas():
    print("Buscando próximas partidas...")

    response = requests.get(url, headers=headers, params=params)

    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    dados = response.json()

    with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
        campos = [
            "ID Jogo", "Data", "Hora",
            "Liga", "Time A", "Time B",
            "Tipo Série"
        ]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        total = 0

        for m in dados:
            try:
                if not m.get("begin_at"):
                    continue

                if not m.get("opponents") or len(m["opponents"]) < 2:
                    continue

                data_hora = datetime.strptime(
                    m["begin_at"], "%Y-%m-%dT%H:%M:%SZ"
                )

                writer.writerow({
                    "ID Jogo": m.get("id"),
                    "Data": data_hora.strftime("%d/%m/%Y"),
                    "Hora": data_hora.strftime("%H:%M"),
                    "Liga": m["league"]["name"] if m.get("league") else "N/A",
                    "Time A": m["opponents"][0]["opponent"]["name"],
                    "Time B": m["opponents"][1]["opponent"]["name"],
                    "Tipo Série": f"MD{m['number_of_games']}" if m.get("number_of_games") else "N/A"
                })

                total += 1

            except:
                continue

    print("Finalizado")
    print("Arquivo:", os.path.abspath(arquivo))
    print("Partidas encontradas:", total)

if __name__ == "__main__":
    buscar_proximas()
