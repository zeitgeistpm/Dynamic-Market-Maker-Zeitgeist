import requests
import dateutil.parser as dp
import json
import pandas as pd
from datetime import datetime
import numpy as np

with open('apikey.json') as json_file:
    key = json.load(json_file)

apiKey = list(key.values())[0]

def getVolumeData(exchange, symbol, resolution, initialDate, endDate, apiKey):
    initialDate = str(initialDate)
    endDate = str(endDate)
    initialDate = initialDate.replace('/', '-')
    endDate = endDate.replace('/', '-')
    
    if (int(initialDate.split('-')[1]) > 12) | (int(endDate.split('-')[1]) > 12):
        print('initialDate and endDate MUST be in ISO format (yyyy-mm-dd)')
        return -1

    def timeConverter(datetime):
        '''
        datetime: ISO format
        '''
        t= str(datetime)
        parsed_t = dp.parse(t)
        t_in_seconds = parsed_t.timestamp()
        return int(t_in_seconds)

    fromTime= timeConverter(initialDate)
    toTime= timeConverter(endDate)

    r = requests.get(f'https://finnhub.io/api/v1/crypto/candle?symbol={exchange}:{symbol}&resolution={resolution}&from={fromTime}&to={toTime}&token={apiKey}')
    query= json.loads(r.content)
    if query['s'] == 'no_data':
        print(f'There is no data for {symbol}')
        return -1

    indexes= len(query['t'])
    ind = np.arange(indexes)

    df = pd.DataFrame.from_dict(query)
    # df = pd.DataFrame(query, index=query[t])
    del df['s']
    df['t'] = df.index
    df = df.rename(columns = {'c': 'close_price', 
                            'h': 'high_price', 
                            'l': 'low_price', 
                            'o': 'open_price',
                            't': 'date',
                            'v': 'volume'})
    
    df['date'] = df['date'].apply(lambda x: str(datetime.utcfromtimestamp(x)))
    df = df.set_index('date')

    return df
    # return query
