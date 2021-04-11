# Dynamic-Market-Maker
In this repository I simulate the work of the recently proposed Dynamic Market Maker, which proposes dynamic variations in the determination of rates, to incentivize or discourage trade, as appropriate.

More info: https://files.kyber.network/DMM-Feb21.pdf


## How to use this:
The first thing that you'll need to do is creating an account on finnhub (https://finnhub.io/) to get access to an API KEY. After that, what you need to do is to create a JSON file called "apikey.json" with the following structure:

{"apikey": *your API key*}

(Or, you just can replace the content of the apiKey object with your key).
After that, you'll have to decide from which exchange you'll get the info. For that purpose, you may want to run symbols.py, which will return you a CSV file with all the assets available from that particular exchange. Next, you need to define the assets to be used. Reminder: if you want to simulate the behavior of a pool composed of, let's say, ETH and BTC, you'll need to have the same comparison token for both of them, meaning that you'll need to pick for example ETH/USDT and BTC/USDT (disclaimer: with this, it's pretended to simulate kind of a pool between the market movements of these two).

## How does this work?
1- Establishing the pair of assets and an initial date. This will get into a function (getDateAndCorrelation) which will return:
  - a DataFrame with information from these 2 pairs like for each date:
    - Close Price
    - High Price 
    - Low Price
    - Open Price
    - Volume
  - the correlation coefficient between the close price of these 2 assets
  - the last volume registered for both of the assets.
This equation is made for an initial test on daily data. If you want to have a different time measure, you'll need to change the *resolution* parameter of the getDateAndCorrelation() function.

2- With the correlation value of the prices, will be defined the initial fee, the min and max fee (if your fee is out of this segment, you are dealing with liquidity problems), and the parameters of the variant factor z (m, n, p). For this last function also will be defined a volume ratio that'll regulate the dynamic fee. This is initially calculated with the ratio between the Exponential Moving Average of the last 10% of the observations and the total amount of observations.
The parameters and functions used here are derivated by the paper, and I make some variations to adjust the variant factor when we are dealing with less correlated pairs. Is also important to clarify that the method used for this case pretends to adjust dynamically the fee by the volume of each pool. This has the advantage of using just on-chain information.

3- Inside the loop, the first thing that will be determined is which buy will be simulated (to see which asset increases and which decreases).
 
4- The next step is to define 3 things to simulate the behavior : 
  - An initial amount of X asset
  - An initial amount of Y asset
  - A date to start simulating

After this, a loop will pick the data frame returned in getDateAndCorrelation() picking the information between the initial date and the date picked recently. With this, it will calculate the volume ratio to adjust the fee. 
When this is calculated, there will be generated a random volume of the asset that will be traded, and with this and the dynamic fee, the amount of the asset that you'll give away will be returned.

5- Finally, it will be checked if the total fee is in range (between the min and max fee previously determined on step 2). If it is, the transfer and new values will be registered and the loop will pass to the next iteration (day in this case). If it isn't, it means that you are running out of liquidity and your liquidity pool will be disabled. 
