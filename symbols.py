import requests
import json
import pandas as pd

with open('apikey.json') as json_file:
    key = json.load(json_file)

apiKey = list(key.values())[0]

r = requests.get(f'https://finnhub.io/api/v1/crypto/exchange?token={apiKey}')
query= json.loads(r.content)
df = pd.DataFrame.from_dict(query)
for i, col in enumerate(df[0]):
    print(f'{i+1}- {col}')

value = int(input('Pick the number of the exchange that you want to get info about the symbols: '))

index = value-1
exchange = df[0][index].lower()

r = requests.get(f'https://finnhub.io/api/v1/crypto/symbol?exchange={exchange}&token={apiKey}')
query= json.loads(r.content)
df = pd.DataFrame.from_dict(query)
df.to_csv(f'symbols-of-{exchange}.csv')