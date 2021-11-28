import pandas as pd
import requests
import time
ALPHAVANTAGE_API_KEY = "V0VBUVL26LN0HCI3"

df = pd.read_csv("digital_currency_list.csv")
codes = df.iloc[:, 0].values[30:]
for code in codes:
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    url_crypto = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={code}&market=INR&apikey={ALPHAVANTAGE_API_KEY}"
    r = requests.get(url_crypto)
    data = r.json()
    try:
        counter = 0
        for days, values in data.get("Time Series (Digital Currency Daily)").items():
            li = [days]
            li.extend([values['1a. open (INR)'], values['2a. high (INR)'], values['3a. low (INR)'],
                       values['4a. close (INR)'], values['5. volume']])
            df.loc[counter] = li
            counter += 1
        print("Hello")
        df.to_csv(r"D:\sem5\FinEazy\manager\crypto_data" + "\\" + code + ".csv", index=False)
        print("Got it",data.get("Time Series (Digital Currency Daily)").items())
    except:
        print(data)
        print(code)
    time.sleep(12)