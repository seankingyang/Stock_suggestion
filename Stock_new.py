import yfinance as yf
import pandas as pd
import requests
import os
from io import StringIO
import datetime
import json
import re
import concurrent.futures

from pathlib import Path

from MarketTime import FutureMarketTime as fmt, StockMarketTime as smt



def json_dump(data, file):
    with open(file, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_stock_history(stock_number, start=""):
    # Check if file exists
    ticker = yf.Ticker(stock_number)
    if start:
        df = ticker.history(start=start, period="max")
    else:
        df = ticker.history(period="max")
    df = df.round(2)
    return df


def get_stock_history_and_save(stock_number, output_folder="./Stock_DB"):
    output_folder_path = Path(output_folder)
    output_folder_path.mkdir(parents=True, exist_ok=True)
    if ".TWO" in stock_number:
        file_name = stock_number.replace(".TWO", "") + ".csv"
    elif ".TW" in stock_number:
        file_name = stock_number.replace(".TW", "") + ".csv"
    file_full_path = output_folder_path / file_name

    if file_full_path.is_file():
        df_exist = pd.read_csv(file_full_path, index_col='Date')
        last_date_in_csv = df_exist.index[-1].split(' ')[0]
        last_open_time = smt.last_open_time(
            datetime.datetime.today()
        ).strftime('%Y-%m-%d')
        if last_date_in_csv == last_open_time:
            return

        df_new = get_stock_history(stock_number, start=last_date_in_csv)
        df_new = df_new.iloc[1:]
        df = pd.concat([df_exist, df_new]).drop_duplicates()

    else:
        df = get_stock_history(stock_number)
    if len(df.index) == 0:
        print(f"{stock_number} has no data")
        return
    df.to_csv(file_full_path)

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
                           



class Stock_info:
    def __init__(self, tracking_stocks_file):
        if tracking_stocks_file:
            if not os.path.exists(tracking_stocks_file):
                raise FileNotFoundError(
                    f"File {tracking_stocks_file} not found"
                )
            self.tracking_stocks_maping = json.load(open(tracking_stocks_file))
            self.__get_sotock_full_code()
        else:
            self.tracking_stocks_maping = (
                self.__get_all_tw_stock_number_and_name()
            )
            self.__get_sotock_full_code()
            json_dump(
                self.tracking_stocks_maping, "./Handle_input/tw_stock.json"
            )
        # Get the all TW stock number
    
    def __get_sotock_full_code(self):
        for stock in self.tracking_stocks_maping:
            if "Stock_full_code" not in self.tracking_stocks_maping[stock]:
                if self.tracking_stocks_maping[stock]["Stock_type"] == "TWO":
                    self.tracking_stocks_maping[stock][
                        "Stock_full_code"
                    ] = f"{stock}.TWO"
                elif self.tracking_stocks_maping[stock]["Stock_type"] == "TW":
                    self.tracking_stocks_maping[stock][
                        "Stock_full_code"
                    ] = f"{stock}.TW"        
    def __get_all_tw_stock_number_and_name(self):
        max_time = 15
        i = 0
        date = datetime.datetime.today()
        stock_number_name_mapping = {}

        while stock_number_name_mapping == {} and i < max_time:
            try:
                all_tw_info = self.__grab_all_tw_stock_info(date)
                if all_tw_info is not None and (
                    '證券名稱' in all_tw_info.columns
                ):
                    stock_number_name_mapping = {}
                    for idx, row in all_tw_info.iterrows():
                        if (
                            not re.findall(
                                r'[購|售|熊|年|元展]\d+', row['證券名稱']
                            )
                            and not re.findall(
                                r'[A-Z]', idx.replace('.TW', '')
                            )
                            and not re.findall(
                                r'0200\d{2}', idx.replace('.TW', '')
                            )
                        ):
                            if ".TWO" in idx:
                                stock_type = "TWO"
                                code = idx.replace(".TWO", "")
                            elif ".TW" in idx:
                                stock_type = "TW"
                                code = idx.replace(".TW", "")
                            stock_number_name_mapping[row['證券名稱']] = {
                                "Name:": row['證券名稱'],
                                "Codename": code,
                                "Stock_full_code": idx,
                                "Stock_type": stock_type,
                            }
                    break
                else:
                    stock_number_name_mapping = {}
            except Exception as e:
                print(e)
            i += 1
            date -= datetime.timedelta(days=1)
        return stock_number_name_mapping

    def get_all_tw_stock_info(self, date=datetime.datetime.today()):
        return self.__grab_all_tw_stock_info(date)




    def __grab_all_tw_stock_info(self, date=datetime.datetime.today()):
        if not isinstance(date, str):
            date = date.strftime('%Y%m%d')
        url = (
            f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv"
            f"&type=ALL&date={date}"
        )
        res = requests.get(url)
        res.encoding = 'big5'
        if res.text == '':
            return pd.DataFrame()
        df = pd.read_csv(
            StringIO(res.text.replace("=", "")),
            header=["證券代號" in line for line in res.text.split("\n")].index(
                True
            )
            - 1,
        )
        df['證券代號'] = df['證券代號'] 
        df = df.set_index('證券代號')
        df[['成交金額', '成交股數']] = df[['成交金額', '成交股數']].apply(
            lambda x: x.str.replace(',', '')
        )
        return df

    def update_stock_info(self):
        # 獲取 CPU 執行緒數並計算最大執行緒數
        max_threads = os.cpu_count() - 1

        # 使用 ThreadPoolExecutor 來管理多執行緒
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_threads
        ) as executor:
            # 提交所有任務並保留未來的順序
            futures = {
                executor.submit(
                    get_stock_history_and_save, stock_number
                ): stock_number
                for stock_number in self.tracking_stocks_maping
            }

            # 確保輸出順序與 tracking_stocks_mapping 一致
            for future in concurrent.futures.as_completed(futures):
                stock_number = futures[future]
                try:
                    future.result()
                    print(f"Stock {stock_number} updated successfully.")
                except Exception as e:
                    print(f"Stock {stock_number} update failed with: {e}")


s = Stock_info("./Handle_input/tw_stock.json")
# s.update_stock_info()
get_stock_history_and_save("8069.TWO")
