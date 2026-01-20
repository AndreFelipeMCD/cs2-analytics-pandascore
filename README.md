# CS2 Analytics – PandaScore API

Projeto em Python para coletar, organizar e analisar dados de partidas e jogadores de Counter-Strike 2, utilizando a API da PandaScore.

A ideia do projeto é transformar dados brutos da API em informações úteis para análise de desempenho de times, histórico de partidas e estatísticas de jogadores.

## O que esse projeto faz

- Salva as proximas partidas em arquivos CSV
- Calcula win rate dos últimos 5 e 15 jogos
- Analisa confrontos diretos (H2H)
- Lista o elenco completo dos times
- Exibe informações detalhadas dos jogadores
- Usa variáveis de ambiente para proteger o token da API

## Tecnologias usadas

- Python
- Requests
- Pandas
- APIs REST
- python-dotenv

## Estrutura do projeto

Os scripts estão organizados por tipo de análise (partidas, times e jogadores), junto com arquivos de configuração e dependências do projeto.

## Como usar

1. Clone o repositório
2. Crie um arquivo `.env` com seu token da PandaScore
3. Instale as dependências:
   pip install -r requirements.txt
4. Execute os scripts conforme a análise desejada
