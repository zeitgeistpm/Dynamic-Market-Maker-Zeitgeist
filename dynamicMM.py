'''
How does this work:
1- Define 2 assets to analize
2- Get the correlation of those tokens for a period of time (let's say 100 days)
3- Take the average volume from that period. This is the long window (A_t)
4- Take the average volume from a shorter period (let's say 15 days). This is the short window (A_s)
5- Define the parameters for the z(r) function:
    . With 3 and 4 we can define r
    . n
    . p
6- According to the correlation returned in 1, define the Base Fee (fee) with the values shown in the paper.
    Also define price ranges.

'''
import math
from getAssetData import getVolumeData
import pandas as pd
from datetime import datetime, date, timedelta
from scipy.stats import pearsonr
import json
import numpy as np
import random
from tqdm import tqdm

today = date.today().strftime('%Y-%m-%d')
with open('apikey.json') as json_file:
    key = json.load(json_file)

apiKey = list(key.values())[0]

symbol1= 'BUSDUSDT'
symbol2= 'BNBUSDT'

def getDateAndCorrelation(exchange, symbol1, symbol2, resolution, initialDate, endDate, apiKey):
    initDate = datetime.strptime(initialDate, "%Y-%m-%d")
    finishDate = datetime.strptime(endDate, "%Y-%m-%d")

    datePeriod= pd.date_range(initDate,finishDate, freq='D')
    volumeTicket1 = getVolumeData(exchange, symbol1, resolution, initialDate, endDate, apiKey)
    volumeTicket2 = getVolumeData(exchange, symbol2, resolution, initialDate, endDate, apiKey)
    
    suffix1 = f'_{symbol1}'
    suffix2 = f'_{symbol2}'
    dataFrameTickets = volumeTicket1.merge(volumeTicket2, how='inner', 
                                        left_index=True, right_index=True, 
                                        suffixes=[suffix1, suffix2])

    correlation = pearsonr(dataFrameTickets[f'close_price{suffix1}'], dataFrameTickets[f'close_price{suffix2}'])
    lastVolSym1 = volumeTicket1['volume'][-1]
    lastVolSym2 = volumeTicket2['volume'][-1]
    return dataFrameTickets, correlation[0], lastVolSym1, lastVolSym2

initialDate = '2020-01-01'

df, correlation, lastVolBUSD, lastVolBNB = getDateAndCorrelation(exchange= 'BINANCE', symbol1= symbol1, symbol2= symbol2, resolution= 'D', initialDate = initialDate, endDate = today, apiKey = apiKey)



#calculate the correlation between both of them and define a base fee
tokenCorrelation = correlation
if tokenCorrelation>=0.95:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with similar assets')
    riskLevel = 0
    fee = 0.003
    minFee = 0.002
    maxFee = 0.006
elif tokenCorrelation >=0.85:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with highly correlated assets')
    riskLevel = 1
    fee = 0.01
    minFee = 0.0067
    maxFee = 0.02
elif tokenCorrelation > 0.7:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with correlated assets')
    riskLevel = 2
    fee = 0.02
    minFee = 0.0137
    maxFee = 0.04
else:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with weakly correlated assets')
    riskLevel = 3
    fee = 0.03
    minFee = 0.02
    maxFee = 0.06

print(f'Fee: {fee} \n Minimum Fee: {minFee} \n Maximum Fee: {maxFee}')

##################### parameter determination #####################
if riskLevel == 0:
    m = 0.009
    p = 8
    n = 1 
elif riskLevel == 1:
    m = 0.009
    p = 7.5
    n = 1 
elif riskLevel == 2:
    m = 0.007
    p = 7.5
    n = 1 
elif riskLevel == 3:
    m = 0.005
    p = 6
    n = 0.9

k= 1

#Ratio volume calculation:
def getVolumeRatio(symbol, df):
    colname = f'volume_{symbol}'
    periodLengthLong = df.shape[0]
    #calculate EMA for the average volume
    longWindow = df[colname].ewm(span=periodLengthLong).mean()[-1]
    periodLengthShort = round(periodLengthLong*0.1, 0)
    shortWindow = df[colname].ewm(span=periodLengthShort).mean()[-1]
    r = shortWindow/longWindow
    return r

def z_r(r):
    z = (m*(r-n))/math.sqrt(p + (r-n)**2)
    return z

def bondingFunction(x):
    y= k*x
    return y

def dynamicVariation(x):
    var = x + deltaX*(1-fee-z)
    return var

####################################################LOOPING SIMULATION #####################################################
print('--------------------------------------LOOP PRINTS--------------------------------------')
pool1 = 1000000 
pool2 = 1000000
endDate = datetime(2020,4,1)
simulationRecord = pd.DataFrame([])
indexer = 0
data = {'date': [], 'accountX': [], 'accountY': [], 'totalFee': [], 'whoBuy': [], 'ratioVolume': [], 'z': [], 'buy': [], 'sell': []}

for i in tqdm(range(100)):
    symbols = [symbol1, symbol2]
    poolInventory= [pool1, pool2]
    buyAsset = random.choice(symbols)
    indexNum = symbols.index(buyAsset)
    if indexNum == 0:
        yElement = buyAsset[1]
    else:
        yElement = buyAsset[0]
    # print(f'We are going to buy {buyAsset} and we will give away {yElement}')

    stopTime = endDate.strftime('%Y-%m-%d')
    # endsAt = df[df['date'] == stopTime].index[0]
    # endsAt +=1
    # temp = df[:endsAt]
    temp = df.loc[:stopTime, :]

    r = getVolumeRatio(buyAsset, temp)

    # print(r)

    # print(f'z value: {z_r(r)}')
    z = z_r(r)



    #how much you want to buy
    deltaX = random.uniform(0, 5000)

    dy = bondingFunction(poolInventory[indexNum]) - bondingFunction(dynamicVariation(poolInventory[indexNum]))

    # print (f'if you want to acquire {deltaX} of {buyAsset}, you will have to give up to {dy*(-1)} of {yElement}')
    # print(dy)

    ########################## ESTABLISHING BOUNDS FOR THE POOL ###################################
    totalFee = fee + z
    # print(f'final fee: {totalFee}')

    if (totalFee> minFee) & (totalFee<maxFee):
        # print("The total fee is in range, you don't have liquidity problems")
        pass
    else:
        print("The total fee is OUT OF RANGE, you have liquidity problems, so we will turn down your pool")
        break
    
    if indexNum == 0:
        pool1 += deltaX
        pool2 += dy
    else:
        pool1 += dy
        pool2 += deltaX

    data['date'].append(stopTime)
    data['accountX'].append(pool1)
    data['accountY'].append(pool2)
    data['totalFee'].append(totalFee)
    data['whoBuy'].append(buyAsset)
    data['ratioVolume'].append(r)
    data['z'].append(z)
    data['buy'].append(deltaX)
    data['sell'].append(dy)

    endDate += timedelta(1)
    ###############################################################################################


pd.DataFrame.from_dict(data).to_csv('simulationRecord.csv')

