import pandas_datareader as web
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from Utility import *
from Calculate import *
import os, time


def SetEnd_Start_DATE(end_str="", start_str=""):
    flag_start = True
    flag_end = True
    end_date = None
    start_date = None

    if start_str == "":
        start_str = end_str
    if end_str == "":
        end_date = datetime.date.today()
        flag_end = False
    if start_str == "":
        start_date = end_date
        flag_start = False
    pattern_list = [".", "-", "_"]
    for pattern in pattern_list:
        print(pattern)
        if flag_end & isWithStr(end_str, pattern):
            end_tuple = numerify(List_2_Tuple(Split_str(end_str, pattern)))
            end_date = datetime.date(*end_tuple)
        if flag_start & isWithStr(start_str, pattern):
            start_tuple = numerify(List_2_Tuple(Split_str(start_str, pattern)))
            print("HI", start_tuple)
            start_date = datetime.date(*start_tuple)

    return end_date, start_date


def Get_Stock_info(stock_id, start_datetime, end_datetime):
    return yf.download(stock_id, start=start_datetime, end=end_datetime)
    #return web.get_data_yahoo(stock_id, start_datetime, end_datetime)
    #return web.DataReader(stock_id, 'yahoo', start_datetime, end_datetime)


def Check_date_isUpdate(today_date, check_date_plist):
    Update_flag = False
    if not os.path.isfile(check_date_plist):
        Update_flag = True
    else:
        Check_date_data = Load_Plist(check_date_plist)
        if "Check_date" in list(Check_date_data.keys()):
            Check_date = Check_date_data["Check_date"]
            if Check_date != str(today_date):
                Update_flag = True
    return Update_flag


def Check_stock_database_date_Update(stock_code, stock_type, today_date):
    stock_csv_path, stock_totalcode = Get_Stocktotalcode_stockcsvpath(
        stock_code, stock_type
    )

    stock_content = pd.read_csv(stock_csv_path)
    Last_Data = stock_content.iloc[-1]
    Last_Data_date = Last_Data["Date"]
    Last_Data_close = Last_Data["Close"]

    if Last_Data_date != str(today_date):
        day = 1
    else:
        day = 0
    if int(datetime.datetime.now().strftime("%H")) < 9:
        end = today_date - datetime.timedelta(days=1)
        day = -1
    else:
        end = today_date

    start = datetime.datetime.strptime(
        Last_Data_date, '%Y-%m-%d'
    ).date() + datetime.timedelta(days=day)
    print("\t\t", start, "-", end)
    try:
        stock = Get_Stock_info(stock_totalcode, start, end)
        stock.to_csv("./TEMP/tmp.csv")
        tmp_content = pd.read_csv("./TEMP/tmp.csv")
        tmp_last_data_date = tmp_content.iloc[-1]["Date"]
        tmp_last_data_close = tmp_content.iloc[-1]["Close"]
        if tmp_last_data_date != Last_Data_date:
            stock_content = pd.concat(
                [stock_content, tmp_content], ignore_index=True
            )
            stock_content.to_csv(stock_csv_path, index=False)

        else:
            if float(tmp_last_data_close) != float(Last_Data_close):
                indexNames = stock_content[
                    (stock_content['Date'] == str(end))
                ].index
                stock_content.drop(indexNames, inplace=True)
                stock_content = pd.concat(
                    [stock_content, tmp_content], ignore_index=True
                )
                stock_content.to_csv(stock_csv_path, index=False)
    except:
        print("\t\t", "Can't not update.... Last date:", Last_Data_date)


def Get_stock_totalcode(stockcode, stocktype):
    if (
        stocktype.upper() == "TW"
        or stocktype.upper() == "TWO"
        or stocktype.upper() == "SZ"
    ):
        stock_totalcode = stockcode + "." + stocktype.upper()
    else:
        stock_totalcode = stockcode
    return stock_totalcode


def Get_Stocktotalcode_stockcsvpath(stock_code, stock_type):
    csv_path = "./DataBase/" + stock_code + ".csv"
    totalcode = Get_stock_totalcode(stock_code, stock_type)
    return csv_path, totalcode


def Load_Check_Stock_file_exist_date(stock_code, stock_type, check_date_plist):
    stock_csv_path, stock_totalcode = Get_Stocktotalcode_stockcsvpath(
        stock_code, stock_type
    )
    Today_Date = datetime.date.today()
    Update_flag = Check_date_isUpdate(Today_Date, check_date_plist)

    if not os.path.isfile(stock_csv_path):
        print("\t\t\tUpdating...")
        stock = Get_Stock_info(stock_totalcode, None, None)
        stock.to_csv(stock_csv_path)

    else:
        if Update_flag:
            print("\t\t\tUpdating...")
            Check_stock_database_date_Update(
                stock_code, stock_type, Today_Date
            )

    return pd.read_csv(stock_csv_path)


def Get_last_two_stock_content(stock_code, stock_type):
    Today_Date = datetime.date.today()
    stock_csv_path, stock_totalcode = Get_Stocktotalcode_stockcsvpath(
        stock_code, stock_type
    )
    Check_stock_database_date_Update(stock_code, stock_type, Today_Date)
    stock_content = pd.read_csv(stock_csv_path)
    previous = stock_content.iloc[-2]
    new = stock_content.iloc[-1]
    return previous, new


####################### This is the main #######################

Stock_own_path = "./Handle_input/STOCK_own.plist"
#Stock_own_path = "./Handle_input/STOCK_track.plist"


Check_date_plist = "./DataBase/Check_date.plist"


Stock_own_content = Load_Plist(Stock_own_path)
Stock_keys = list(Stock_own_content.keys())
############### only for debug ##############
# Stock_keys = [Stock_keys[0]]
#############################################
print("==============================================")
print("================= STOCK LIST =================")
print(str(Stock_keys))
print("==============================================\n\n")


print("==============================================")
print("============== Update Database ===============")
tStart = time.time()
n = 1
for key in Stock_keys:
    print(
        "\t-> "
        + str(n)
        + ". "
        + key
        + "\t "
        + Stock_own_content[key]["Codename"]
    )
    n += 1
    stock_type = Stock_own_content[key]["Stock_type"]
    stock_name = Stock_own_content[key]["Name"]
    stock_code = Stock_own_content[key]["Codename"]
    stock_position = Stock_own_content[key]["Position"]
    stock_unit = Stock_own_content[key]["Unit"]
    stock_cost = Stock_own_content[key]["TotalCost"]

    Stock_content = Load_Check_Stock_file_exist_date(
        stock_code, stock_type, Check_date_plist
    )

###Post process###
tEnd = time.time()
print("It cost %f sec" % (tEnd - tStart))
print("=========== Update Database Finish ===========")
print("==============================================\n\n")
now_time = int(datetime.datetime.now().strftime("%H"))
if now_time == 13:
    now_min = int(datetime.datetime.now().strftime("%M"))
    if now_min >= 30:
        Check_date = str(datetime.date.today())
    else:
        Check_date = str(datetime.date.today() - datetime.timedelta(days=1))

elif now_time < 14:
    Check_date = str(datetime.date.today() - datetime.timedelta(days=1))
else:
    Check_date = str(datetime.date.today())
Check_date_dict = {"Check_date": Check_date}
Write_Plist(Check_date_plist, Check_date_dict)

########DEBUG#####
# end, start = SetEnd_Start_DATE()
# print("Start:", start, "End:", end)
# start = datetime.date(2020, 9, 24)
# end = datetime.date(2020, 9, 24)
# print("Start:", start, "End:", end)
# # end = datetime.date.today()
#
#
# stock2 = web.DataReader("2338.TW", 'yahoo', None, None)
# # stock2.to_csv('./DataBase/00850.csv')
# TB2 = MakeTable(stock2.head(), "Date")
# print(TB2)

# datetime.datetime.strptime(str,'%Y-%m-%d')
# datetime.timedelta(days=1)

# pd.concat

# header = []
# header = Stock_content.columns.tolist()
