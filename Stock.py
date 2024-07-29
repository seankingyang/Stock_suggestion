# import pandas_datareader as web
# import numpy as np
import yfinance as yf
import pandas as pd
import datetime
from Utility import (
    Plist_operator,
    Load_Plist,
    Write_Plist,
    isWithStr,
    Split_str,
    List_2_Tuple,
    numerify,
)
import os
import time


class StockData:
    def __init__(self):
        pass

    def get_stock_info(self, stock_id, start_datetime, end_datetime):
        if start_datetime is None and end_datetime is None:
            start_datetime = datetime.datetime(
                1900, 1, 1
            )  # Default start date
            end_datetime = datetime.datetime.today()  # Default end date
        elif start_datetime is None:
            start_datetime = datetime.datetime(
                1900, 1, 1
            )  # Default start date
        elif end_datetime is None:
            end_datetime = datetime.datetime.today()  # Default end date

        return yf.download(
            stock_id,
            start=start_datetime,
            end=end_datetime + datetime.timedelta(days=1),
        )


class DateChecker:
    def __init__(self, check_date_plist):
        self.check_date_plist = check_date_plist

    def check_date_is_update(self, today_date):
        if not os.path.isfile(self.check_date_plist):
            return True
        else:
            check_date_data = Load_Plist(self.check_date_plist)
            if "Check_date" in check_date_data:
                check_date = check_date_data["Check_date"]
                return check_date != str(today_date)
        return False


class StockDatabase:
    def __init__(self, stock_code, stock_type):
        self.stock_code = stock_code
        self.stock_type = stock_type
        self.stock_csv_path, self.stock_totalcode = (
            self.get_stocktotalcode_stockcsvpath()
        )

    def get_stock_totalcode(self):
        if self.stock_type.upper() in ["TW", "TWO", "SZ"]:
            return f"{self.stock_code}.{self.stock_type.upper()}"
        return self.stock_code

    def get_stocktotalcode_stockcsvpath(self):
        csv_path = f"./DataBase/{self.stock_code}.csv"
        totalcode = self.get_stock_totalcode()
        return csv_path, totalcode

    def check_stock_database_date_update(self, today_date):
        stock_content = pd.read_csv(self.stock_csv_path)
        last_data = stock_content.iloc[-1]
        last_data_date = last_data["Date"]
        last_data_close = last_data["Close"]

        if last_data_date != str(today_date):
            day = 1
        else:
            day = 0
        if int(datetime.datetime.now().strftime("%H")) < 9:
            end = today_date - datetime.timedelta(days=1)
            day = -1
        else:
            end = today_date

        start = datetime.datetime.strptime(
            last_data_date, "%Y-%m-%d"
        ).date() + datetime.timedelta(days=day)
        print("\t\t", start, "-", end)
        try:
            stock_data = StockData()
            stock = stock_data.get_stock_info(self.stock_totalcode, start, end)
            stock.to_csv("./TEMP/tmp.csv")
            tmp_content = pd.read_csv("./TEMP/tmp.csv")
            tmp_last_data_date = tmp_content.iloc[-1]["Date"]
            tmp_last_data_close = tmp_content.iloc[-1]["Close"]
            if tmp_last_data_date != last_data_date:
                stock_content = pd.concat(
                    [stock_content, tmp_content], ignore_index=True
                )
                stock_content.to_csv(self.stock_csv_path, index=False)
            else:
                if float(tmp_last_data_close) != float(last_data_close):
                    index_names = stock_content[
                        (stock_content["Date"] == str(end))
                    ].index
                    stock_content.drop(index_names, inplace=True)
                    stock_content = pd.concat(
                        [stock_content, tmp_content], ignore_index=True
                    )
                    stock_content.to_csv(self.stock_csv_path, index=False)
        except Exception as e:
            print("\t\t", "Can't not update.... Last date:", last_data_date)
            print("\t\t", "Error:", str(e))

    def load_check_stock_file_exist_date(self, check_date_plist):
        today_date = datetime.date.today()
        date_checker = DateChecker(check_date_plist)
        update_flag = date_checker.check_date_is_update(today_date)

        if not os.path.isfile(self.stock_csv_path):
            print("\t\t\tUpdating...")
            stock_data = StockData()
            stock = stock_data.get_stock_info(self.stock_totalcode, None, None)
            stock.to_csv(self.stock_csv_path)
        else:
            if update_flag:
                print("\t\t\tUpdating...")
                self.check_stock_database_date_update(today_date)

        return pd.read_csv(self.stock_csv_path)

    def get_last_two_stock_content(self):
        today_date = datetime.date.today()
        self.check_stock_database_date_update(today_date)
        stock_content = pd.read_csv(self.stock_csv_path)
        previous = stock_content.iloc[-2]
        new = stock_content.iloc[-1]
        return previous, new


# ###################### This is the main #######################


def load_check_stock_file_exist_date(stock_code, stock_type, check_date_plist):
    stock_db = StockDatabase(stock_code, stock_type)
    return stock_db.load_check_stock_file_exist_date(check_date_plist)


def main():
    stock_own_path = "./Handle_input/STOCK_own.plist"
    check_date_plist = "./DataBase/Check_date.plist"

    stock_own_content = Load_Plist(stock_own_path)
    stock_keys = list(stock_own_content.keys())

    print("==============================================")
    print("================= STOCK LIST =================")
    print(str(stock_keys))
    print("==============================================\n\n")

    print("==============================================")
    print("============== Update Database ===============")
    t_start = time.time()
    n = 1
    for key in stock_keys:
        print(
            "\t-> "
            + str(n)
            + ". "
            + key
            + "\t "
            + stock_own_content[key]["Codename"]
        )
        n += 1
        stock_type = stock_own_content[key]["Stock_type"]
        stock_name = stock_own_content[key]["Name"]
        stock_code = stock_own_content[key]["Codename"]
        stock_position = stock_own_content[key]["Position"]
        stock_unit = stock_own_content[key]["Unit"]
        stock_cost = stock_own_content[key]["TotalCost"]

        stock_content = load_check_stock_file_exist_date(
            stock_code, stock_type, check_date_plist
        )

    # ##Post process###
    t_end = time.time()
    print("It cost %f sec" % (t_end - t_start))
    print("=========== Update Database Finish ===========")
    print("==============================================\n\n")

    now_time = int(datetime.datetime.now().strftime("%H"))
    if now_time == 13:
        now_min = int(datetime.datetime.now().strftime("%M"))
        if now_min >= 30:
            check_date = str(datetime.date.today())
        else:
            check_date = str(
                datetime.date.today() - datetime.timedelta(days=1)
            )
    elif now_time < 14:
        check_date = str(datetime.date.today() - datetime.timedelta(days=1))
    else:
        check_date = str(datetime.date.today())

    check_date_dict = {"Check_date": check_date}
    Write_Plist(check_date_plist, check_date_dict)


if __name__ == "__main__":
    main()
