# Stock API

Using the python `requests` pkg

```python
import requests

class httpService:
    def __init__(self):
        pass

    def __get(self, url):
        res = requests.get(url)
        res.encoding = 'big5'
        if res.status_code != 200:
            raise Exception(f"Http request failed with status code {res.status_code}")
        return res
    
    def get_json(self, url):
        res = self.__get(url)
        return res.json()
    
    def get_csv(self, url):
        res = self.__get(url)
        return pd.read_csv(StringIO(res.text.replace("=", "")))

```

## [TWSW API](https://openapi.twse.com.tw/) 上市資料

1. 上市個股日本益比、殖利率及股價淨值比（依代碼查詢）
    `https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL`

    ```json
    {
        "Code": "string",
        "Name": "string",
        "PEratio": "string",
        "DividendYield": "string",
        "PBratio": "string"
    }
    ```

1. 上市個股日收盤價及月平均價
   `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL`

    ```json
    {
        "Code": "string",
        "Name": "string",
        "ClosingPrice": "string",
        "MonthlyAveragePrice": "string"
    }
    ```

1. 上市個股日成交資訊
    `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`

    ```json
    {
        "Code": "string",
        "Name": "string",
        "TradeVolume": "string",
        "TradeValue": "string",
        "OpeningPrice": "string",
        "HighestPrice": "string",
        "LowestPrice": "string",
        "ClosingPrice": "string",
        "Change": "string",
        "Transaction": "string"
    }
    ```

## [TPEX API](https://www.tpex.org.tw/openapi/) 上櫃資料
