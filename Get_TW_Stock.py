import requests
import json
import os
import re
import yfinance as yf
import pandas as pd
import datetime
from pathlib import Path
from MarketTime import StockMarketTime as smt
import concurrent.futures
from io import StringIO
import logging
import colorlog
import time


global log_show_level
global log_file_path
log_show_level = logging.INFO
log_file_path = "./Stock.log"


class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, log_file=None):
        super().__init__(name, level)
        self.setLevel(level)

        # Define color formatter
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - "
            "%(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'light_white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        )

        # Console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(color_formatter)
        self.addHandler(self.console_handler)

        # File handler
        if log_file:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setFormatter(file_formatter)
            self.addHandler(self.file_handler)
        else:
            self.file_handler = None

    def __set_log_level(self, level):
        self.setLevel(level)
        self.console_handler.setLevel(level)
        if self.file_handler:
            self.file_handler.setLevel(level)

    def log_info(self, message):
        self.info(message)

    def log_error(self, message):
        self.error(message)

    def log_warning(self, message):
        self.warning(message)

    def log_debug(self, message):
        self.debug(message)


TWSE_BASE_URL = "http://www.twse.com.tw/"
TPEX_BASE_URL = "http://www.tpex.org.tw/"


# url = urllib.parse.urljoin(TWSE_BASE_URL, "exchangeReport/STOCK_DAY")
def json_dump(data, file):
    with open(file, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class MutiThread:
    def __init__(self, max_threads=0):
        self.logger = Logger(
            name=__class__.__name__,
            level=log_show_level,
            log_file=log_file_path,
        )
        self.logger.log_debug("Init MutiThread")

        if max_threads == 0:
            self.max_threads = os.cpu_count() - 1
        else:
            self.max_threads = min(max_threads, os.cpu_count())
        self.logger.log_debug(f"Max threads: {self.max_threads}")

    def run_multithreaded(self, work_function, items):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_threads
        ) as executor:
            futures = {
                executor.submit(work_function, item): item for item in items
            }
            results = {}
            failed_items = []

            for future in concurrent.futures.as_completed(futures):
                item = futures[future]
                try:
                    result = future.result()
                    results[item] = result
                    self.logger.log_debug(f"Task for {item} finished")

                except Exception as e:
                    failed_items.append(item)
                    self.logger.log_error(
                        f"Task for {item} failed with exception: {e}"
                    )

            status = not bool(failed_items)
            fail_num = len(failed_items)

            return {
                "status": status,
                "fail_num": fail_num,
                "fail_items": failed_items,
                "result": results,
            }


class httpService:
    def __init__(self):
        self.logger = Logger(
            name=__class__.__name__,
            level=log_show_level,
            log_file=log_file_path,
        )
        self.logger.log_debug("Init httpService")

    def __get(self, url, max_retries=5):
        while max_retries > 0:
            try:
                res = requests.get(url)
                if res.status_code != 200:
                    raise Exception(
                        f"Http request failed with status code "
                        f"{res.status_code}"
                    )
                return res
            except Exception as e:
                self.logger.log_warning(
                    f"Http request failed with exception: {e}"
                )
                max_retries -= 1
        self.logger.log_error(
            f"Http request {url} failed after {max_retries} retries"
        )
        return res

    def get_json(self, url):
        res = self.__get(url)
        if res.status_code != 200:
            self.logger.log_error("Cant get json data")
            return {}
        self.logger.log_debug(f"Get json data from {url}")
        return res.json()

    def get_csv_to_df(self, url):
        res = self.__get(url)
        if res.status_code != 200:
            self.logger.log_error("Cant get csv data")
            return pd.DataFrame()
        self.logger.log_debug(f"Get csv data from {url}")
        return pd.read_csv(StringIO(res.text.replace("=", "")))


class StockCodeMapping:
    def __init__(self, file_path="./Handle_Stock/Stock_Code_Mapping.json"):
        self.logger = Logger(
            name=__class__.__name__,
            level=log_show_level,
            log_file=log_file_path,
        )
        self.logger.log_debug("Init StockCodeMapping")

        self.file_path = file_path
        self.fetch_urls = {
            "TWSE": (
                "https://openapi.twse.com.tw/v1"
                "/exchangeReport/STOCK_DAY_ALL"
            ),
            "TPEX": (
                "https://www.tpex.org.tw/openapi/v1/"
                "tpex_mainboard_daily_close_quotes"
            ),
        }
        self.httpService = httpService()
        self.stock_code_mapping = self.get_stock_code_mapping(True)

    def get_stock_code_mapping(self, is_update=False):
        stock_code_mapping = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                stock_code_mapping = json.load(f)
            if not is_update:
                return stock_code_mapping
        stock_code_mapping = self.update_stock_code_mapping(stock_code_mapping)
        return stock_code_mapping

    def update_stock_code_mapping(self, stock_code_mapping):
        # Fetch TWSE and TPEX stock data
        stock_data_sources = {
            "TWSE": ("Code", "Name", "TW", "TW"),
            "TPEX": ("SecuritiesCompanyCode", "CompanyName", "TWO", "OTC"),
        }

        def update_mapping(
            stock_data, code_key, name_key, yfinance_suffix, stock_type
        ):
            for stock_dict in stock_data:
                stock_code = stock_dict[code_key]
                stock_name = stock_dict[name_key]
                if (
                    not re.findall(r'(購|售|熊|年|元展)\d+', stock_name)
                    and not re.findall(r'[A-Z]', stock_code)
                    and not re.findall(r'0200\d{2}', stock_code)
                ):
                    stock_code_mapping[stock_code] = {
                        'Code': stock_code,
                        'yfinance_code': f"{stock_code}.{yfinance_suffix}",
                        'Name': stock_name,
                        'Type': stock_type,
                    }

        for market, (
            code_key,
            name_key,
            yfinance_suffix,
            stock_type,
        ) in stock_data_sources.items():
            stock_data = self.fetch_stock_data(market)
            update_mapping(
                stock_data, code_key, name_key, yfinance_suffix, stock_type
            )

        json_dump(stock_code_mapping, self.file_path)
        return stock_code_mapping

    def fetch_stock_data(self, market):
        if market not in self.fetch_urls:
            raise ValueError(f"Invalid market: {market}")
        stock_info_json = self.httpService.get_json(self.fetch_urls[market])
        return stock_info_json


class StockHistory:

    def __init__(self, output_folder="./Stock_DB"):
        self.logger = Logger(
            name=__class__.__name__,
            level=log_show_level,
            log_file=log_file_path,
        )
        self.logger.log_debug("Init StockHistory")
        self.output_folder = output_folder
        self.output_folder_path = Path(output_folder)
        self.output_folder_path.mkdir(parents=True, exist_ok=True)

    def get_stock_history(self, yf_stock_number, start=""):
        ticker = yf.Ticker(yf_stock_number)
        if start:
            df = ticker.history(start=start, period="max")
        else:
            df = ticker.history(period="max")
        df = df.round(2)
        return df

    def save_stock_history(self, stock_number):
        if ".TWO" in stock_number:
            file_name = stock_number.replace(".TWO", "") + ".csv"
        elif ".TW" in stock_number:
            file_name = stock_number.replace(".TW", "") + ".csv"
        file_full_path = self.output_folder_path / file_name

        if file_full_path.is_file():
            df_exist = pd.read_csv(file_full_path, index_col='Date')
            last_date_in_csv = df_exist.index[-1].split(' ')[0]
            last_open_time = smt.last_open_time(
                datetime.datetime.today()
            ).strftime('%Y-%m-%d')
            if last_date_in_csv == last_open_time:
                return

            df_new = self.get_stock_history(
                stock_number, start=last_date_in_csv
            )
            df_new = df_new.iloc[1:]
            df = pd.concat([df_exist, df_new]).drop_duplicates()

        else:
            df = self.get_stock_history(stock_number)
        if len(df.index) == 0:
            self.logger.log_warning(f"{stock_number} has no data")
            return
        df.to_csv(file_full_path)


def main():
    file = "./Handle_Stock/Stock_Code_Mapping.json"
    stock_code_mapping = StockCodeMapping()
    stock_history = StockHistory("./DataBase")
    stock_code_mapping = json.load(open(file, "r"))
    stock_numbers = [
        stock['yfinance_code'] for stock in stock_code_mapping.values()
    ]
    m_thread = MutiThread(max_threads=0)
    result = m_thread.run_multithreaded(
        stock_history.save_stock_history, stock_numbers
    )
    if result['status']:
        log.log_info("All stock history data saved successfully")
    else:
        log.log_error(
            f"Failed to save {result['fail_num']} stock history data"
        )
        log.log_error(f"Failed items: {result['fail_items']}")


if __name__ == "__main__":
    tStart = time.time()
    log_show_level = logging.DEBUG
    log_file_path = "./123.log"

    log = Logger(name=__name__, level=log_show_level, log_file=log_file_path)

    main()

    tEnd = time.time()
    log.log_info(f"Time taken: {tEnd - tStart} seconds")
