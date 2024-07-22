import requests
import re
import pandas as pd
import prettytable as pt
import warnings

# from tabulate import tabulate

warnings.filterwarnings("ignore")


def Print_list(input_list, prefix="", postfix=""):
    type_list = type(input_list)
    if not (type_list == list):
        print("The input is not list!! It is:", type_list)
    else:
        temp_str = ""
        for item in input_list:
            if temp_str == "":
                temp_str = str(item)
            else:
                temp_str = temp_str + ", " + str(item)
        print(prefix + temp_str + postfix)


def normalize_stockname(input_txt):
    if not isinstance(input_txt, str):
        return False, None
    else:
        stock_id_input_arr = re.findall("([\\d\\w\\.]+)", input_txt)
        stock_id_arr = []
        for check_stock in stock_id_input_arr:
            temp = check_stock.split("_")[0].upper()
            if temp == "TSE":
                stock_type = "tse"
                stock_id = check_stock.split("_")[1]
            elif temp == "OTC":
                stock_type = "otc"
                stock_id = check_stock.split("_")[1]
            else:
                stock_type = "tse"
                stock_id = check_stock.split("_")[-1]
            stock_id_arr.append(stock_type + "_" + stock_id + ".tw")

        Print_list(stock_id_arr, "Stock ID:")
        return True, stock_id_arr


def generate_full_url(stock_id_arr):
    if not isinstance(stock_id_arr, list):
        return False, None
    else:
        base_url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="
        end_url = "&json=1&delay=0"
        stock_url = ""
        for stock in stock_id_arr:
            if stock_url == "":
                stock_url = stock
            else:
                stock_url = stock_url + "|" + stock
        complete_url = base_url + stock_url + end_url
        # print("complete_url:", complete_url)
        return True, complete_url


def stock_process(stock_json):
    msg_arr = stock_json["msgArray"]
    if msg_arr == []:
        print(
            "The stock CAN'T be idientified,\n"
            "Please check if stock id are correct"
        )
    else:
        stock_dictarr = {}
        header = [
            "Name",
            "ID",
            "Price_now",
            "Percent",
            "Price_open",
            "Price_yest",
            "Volumn",
        ]
        mark = ["n", "c", "z", "Per", "o", "y", "v"]
        for i in range(len(header)):
            temp_arr = []
            for msg in msg_arr:
                if mark[i] == "Per":
                    p_n = (
                        (float(msg["z"]) - float(msg["y"]))
                        / float(msg["y"])
                        * 100
                    )
                    value = str(round(p_n, 3)) + " %"
                else:
                    value = msg[mark[i]]
                temp_arr.append(value)
            stock_dictarr[header[i]] = temp_arr

        stock_arrdict = []
        for msg in msg_arr:
            temp = {}
            temp["Name"] = msg["n"]
            temp["ID"] = msg["c"]
            temp["Price_now"] = msg["z"]
            temp["Price_open"] = msg["o"]
            temp["Volumn"] = msg["v"]
            temp["Price_yest"] = msg["y"]
            p_n = (
                (float(temp["Price_now"]) - float(temp["Price_yest"]))
                / float(temp["Price_yest"])
                * 100
            )
            p = str(round(p_n, 3)) + " %"
            temp["Percent"] = p
            stock_arrdict.append(temp)

        # print("stock_dictarr:\n",stock_dictarr)
        # print("stock_arrdict:\n",stock_arrdict)

        return stock_dictarr, stock_arrdict


def convertTODataform(stock_dictarr):
    if isinstance(stock_dictarr, dict):
        stock_df = pd.DataFrame.from_dict(stock_dictarr)
        stock_df.set_index("Name", inplace=True)
        stock_df.style.map(show, subset=pd.IndexSlice["Percent"])
        # print("stock_df:\n", stock_df)
    return stock_df


def show(input_txt):
    val = float(input_txt.split(" ")[0])
    color = "red" if val < 0 else "green"
    return "color:%s" % color


# stock_id_input = "2330 OTC_6488"

print("===============================")
print("============ START ============")
print("===============================")
looping = True
while looping:
    input_txt = input("Enter stock id or Exit: ")
    if (
        "EXIT" in input_txt.upper()
        or "Q" in input_txt.upper()
        or "E" in input_txt.upper()
    ):
        looping = False
        break
    else:
        status_1, stock_id_arr = normalize_stockname(input_txt)
        status_2, complete_url = generate_full_url(stock_id_arr)

    if status_1 and status_2:
        response = requests.get(complete_url)
        stock_json = response.json()
        # print(stock_id_arr)
        # print(stock_json)
        stock_dictarr, stock_arrdict = stock_process(stock_json)
        stock_df = convertTODataform(stock_dictarr)
        tb1 = pt.PrettyTable()
        tb1.add_column("Name", stock_df.index)
        for (
            col
        ) in stock_df.columns.values:  # df.columns.values的意思是获取列的名称
            tb1.add_column(col, stock_df[col])

        print("TB1:\n")
        print(tb1)

    else:
        if not status_1:
            print("Something error in 1")
        if not status_2:
            print("Something error in 2")

    # Real 00878 00692 2330
    # response = requests.get(complete_url)
    # stock_json = response.json()
    # print(stock_json)
    # Real


print("===============================")
print("============= END =============")
print(" Thanks for useing this script")
print("===============================")
