from Utility import (
    numerify,
    p_log,
    Load_Plist,
    BColors,
    series2list,
)
from Calculate import (
    Cal_percentage,
    Cal_MA,
    Cal_MA_with_desirelist,
    Cal_BR,
    Cal_KDJ,
    Cal_Vol_Price,
    Cal_MACD,
    Cal_EMA,
    Cal_lowpassfilter,
    Cal_BBands,
    Cal_ATR,
)
from Stock_analyze import (
    br_analysis,
    kd_analysis,
    macd_analysis,
    ema_analysis,
    lowpassfilter_analysis,
    bbands_analysis,
)

# import prettytable as pt
import os
import time
import matplotlib.pyplot as plt
import datetime
import pandas as pd

# import copy


def fill_up(input_value, desired_len, prefix="", suffix=""):
    """
    Ensures that the input_value, when combined with optional prefix and suffix,
    reaches a desired length by recursively adding the prefix and suffix until the length is met or exceeded.

    Parameters:
    - input_value: The initial value to be modified.
    - desired_len: The desired length of the final string.
    - prefix: A string to be added to the beginning of input_value if needed.
    - suffix: A string to be added to the end of input_value if needed.

    Returns:
    - A string of at least desired_len length, modified by adding prefix and suffix as needed.
    """
    input_value = str(input_value)  # Ensure the input is treated as a string
    # If both prefix and suffix are empty, return the input_value as is
    if prefix == "" and suffix == "":
        return input_value
    # If the current length meets or exceeds the desired length, return the current value
    if len(input_value) >= desired_len:
        return input_value
    # Recursively call fill_up with the modified value until the desired length is reached
    return fill_up(prefix + input_value + suffix, desired_len, prefix, suffix)


def plot_something(
    stock_code,
    title,
    X_value,
    Y_value_list,
    Y_value_lable_list,
    Xlabel,
    Ylabel,
    save_png_path="",
    plotrange=-150,
):
    print("\t\t\tPlotting Close & " + fill_up(title, 12, "", "."), end=" ")
    if len(Y_value_list) == len(Y_value_lable_list):
        # plt.figure(figsize=(25, 15), dpi=50, linewidth=1)
        # plt.title(stock_code+"  Close & "+title, fontsize=15, x=0.5, y=1.03)
        fig, ax1 = plt.subplots(figsize=(30, 15), dpi=50, linewidth=1)
        ax1.title.set_text(stock_code + "  Close & " + title)
        ax1.set_xlabel(Xlabel, fontsize=15)

        temp = ["MA", "LFT", "BBand", "EMA", "Vegas"]
        isTwin = True
        for te in temp:
            if title == te:
                isTwin = False
                break

        if isTwin:
            isAdd = False
            for idx in range(len(Y_value_list)):
                if idx == 0:
                    ax1.set_ylabel("Stock price ($)", fontsize=15)
                    ax1.plot(
                        X_value[plotrange:],
                        Y_value_list[idx][plotrange:],
                        label=Y_value_lable_list[idx],
                        color="Red",
                    )

                else:
                    if isAdd:
                        ax2.plot(
                            X_value[plotrange:],
                            Y_value_list[idx][plotrange:],
                            label=Y_value_lable_list[idx],
                        )
                    else:
                        ax2 = ax1.twinx()
                        ax2.set_ylabel(Ylabel, fontsize=15)
                        ax2.plot(
                            X_value[plotrange:],
                            Y_value_list[idx][plotrange:],
                            label=Y_value_lable_list[idx],
                        )
                        isAdd = True
            ax1.legend(loc="upper left", fontsize=15)
            ax2.legend(loc="upper right", fontsize=15)

        else:
            ax1.set_ylabel(Ylabel, fontsize=15)
            for idx in range(len(Y_value_list)):
                ax1.plot(
                    X_value[plotrange:],
                    Y_value_list[idx][plotrange:],
                    label=Y_value_lable_list[idx],
                )
            ax1.legend(loc="upper left", fontsize=15)
        plt.xlim(0, abs(plotrange) - 1)
        plt.yticks(fontsize=15)
        # plt.grid(b=True, which='major', color='#666666',
        # linestyle='--', axis="x")
        ax1.xaxis.grid(color="#666666", linestyle="--")
        ax1.yaxis.grid(color="#666666", linestyle="--")
        print("Saving PNG...", end=" ")
        if not save_png_path == "":
            plt.savefig(save_png_path, dpi=300)
        plt.close()
        print("DONE")
    else:
        print("Can't not plot")


# ###################### This is the main #######################
today_date = datetime.date.today()
log_path = "./Handle_output/stock_suggestion_" + str(today_date) + ".txt"
if os.path.isfile(log_path):
    os.remove(log_path)

p_log(["=============================================="], log_path)
p_log(["=============== Plot Database ================"], log_path)
tStart = time.time()
Stock_own_path = "./Handle_input/STOCK_own.plist"
# Stock_own_path = "./Handle_input/STOCK_track.plist"

Stock_own_content = Load_Plist(Stock_own_path)
Stock_keys = list(Stock_own_content.keys())
n = 1
Total_money = 1000000
invest_total = 0

suggestion_buy = []
suggestion_sell = []
# ############## only for debug ##############
# Stock_keys = [Stock_keys[0]]
# print(Stock_keys)
# ############################################

now_time = int(datetime.datetime.now().strftime("%H"))
global G_plot
G_plot = True
for stock in Stock_keys:
    p_log(
        [
            "\t-> "
            + str(n)
            + ". "
            + stock
            + "\t "
            + Stock_own_content[stock]["Codename"]
        ],
        log_path,
    )
    n += 1
    isplot = False
    stock_name = Stock_own_content[stock]["Name"]
    stock_code = Stock_own_content[stock]["Codename"]
    folder_name = "./Handle_output/" + stock_name

    stock = pd.read_csv("./DataBase/" + stock_code + ".csv")
    stock_close = numerify(series2list(stock["Close"]), "Float")
    stock_volume = numerify(series2list(stock["Volume"]), "Float")
    stock_date = series2list(stock["Date"])
    stock_H = numerify(series2list(stock["High"]), "Float")
    stock_L = numerify(series2list(stock["Low"]), "Float")

    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    tmp_file = ".tmp" + stock_date[-1]
    tmp_file_path = folder_name + "/" + tmp_file

    if not os.path.isfile(tmp_file_path):
        if now_time == 13:
            now_min = int(datetime.datetime.now().strftime("%M"))
            if now_min >= 30 and G_plot:
                if not os.path.isfile(tmp_file_path):
                    isplot = True
                    file_list = os.listdir(folder_name)
                    for file in file_list:
                        os.remove(folder_name + "/" + file)
                    tmp = open(tmp_file_path, "w")
                    tmp.close()
            else:
                isplot = False
        elif now_time > 8 and now_time < 14 and G_plot:
            isplot = False
        else:
            if G_plot:
                if not os.path.isfile(tmp_file_path):
                    file_list = os.listdir(folder_name)
                    for file in file_list:
                        os.remove(folder_name + "/" + file)
                    tmp = open(tmp_file_path, "w")
                    tmp.close()
                isplot = True

    p_log(["\t\t\tCalculating..."], log_path)
    #   This should be controlled by input or something input data
    desire_MA = [5, 10, 15, 20, 30, 60, 90]
    stock_MA_list = Cal_MA_with_desirelist(stock_close, desire_MA)

    Center, UL, LL, UL_s, LL_s = Cal_BBands(stock_close, 2, 20)

    stock_close_lft = Cal_lowpassfilter(stock_close, 1, 0.01)
    stock_close_lft_UL = [1.05 * i for i in stock_close_lft]
    stock_close_lft_LL = [0.95 * i for i in stock_close_lft]

    K, D, J = Cal_KDJ(stock_close, 20)

    BR = Cal_BR(stock_close, 20)

    Vol_pri = Cal_Vol_Price(stock_volume, stock_close)

    DIF, MACD, DIF_MACD = Cal_MACD(stock_close, stock_H, stock_L, 12, 26, 9)

    EMA12 = Cal_EMA(stock_close, stock_H, stock_L, 12)
    EMA26 = Cal_EMA(stock_close, stock_H, stock_L, 26)
    EMA_20MA = Cal_MA(stock_close, 20)

    EMA30 = Cal_EMA(stock_close, stock_H, stock_L, 30)
    EMA60 = Cal_EMA(stock_close, stock_H, stock_L, 60)
    EMA120 = Cal_EMA(stock_close, stock_H, stock_L, 120)
    EMA240 = Cal_EMA(stock_close, stock_H, stock_L, 240)

    plot_range_num = -100
    Stock_now = stock_close[-1]
    Stock_yesd = stock_close[-2]
    stock_per = round(Cal_percentage(Stock_yesd, Stock_now), 2)
    if stock_per > 0:
        stock_per = (
            f"{BColors.RED}" + str(stock_per) + "% \u2191" + f"{BColors.ENDC}"
        )
    elif stock_per < 0:
        stock_per = (
            f"{BColors.GREEN}"
            + str(stock_per)
            + "% \u2193"
            + f"{BColors.ENDC}"
        )
    else:
        stock_per = str(stock_per) + "%"
    p_log(
        ["\t\t\t\tStock_now:", str(round(Stock_now, 2)) + " \t" + stock_per],
        log_path,
    )

    ATR = Cal_ATR(stock_close, stock_H, stock_L, 21)
    U = Total_money * 0.01 / ATR[-1]
    Four_U = round(U * 4, 2)
    sugg_pos = round(U * 4 / round(Stock_now, 2), 0)
    ATR_per = round(Cal_percentage(ATR[-2], ATR[-1]), 2)
    if ATR_per > 0:
        ATR_per = (
            f"{BColors.RED}" + str(ATR_per) + "% \u2191" + f"{BColors.ENDC}"
        )
    elif ATR_per < 0:
        ATR_per = (
            f"{BColors.GREEN}" + str(ATR_per) + "% \u2193" + f"{BColors.ENDC}"
        )
    else:
        ATR_per = str(ATR_per) + "%"
    p_log(
        ["\t\t\t\tATR:", "{:.2f}".format(ATR[-1]) + " \t" + ATR_per, "\n"],
        log_path,
    )
    p_log(["\t\t\t\t4U($):", "{:.2f}".format(Four_U)], log_path)
    p_log(
        ["\t\t\t\tSuggest position(units):", "{:.2f}".format(sugg_pos), "\n"],
        log_path,
    )

    p_log(["\t\t\t\tBR:", "{:.2f}".format(BR[-1]) + "%"], log_path, " ")
    BR_result = br_analysis(BR)
    p_log(["\n\t\t\t\t\tAction:", BR_result, "\n"], log_path)

    p_log(
        [
            "\t\t\t\tKDJ:",
            "{:.2f}".format(K[-1]) + "%",
            "{:.2f}".format(D[-1]) + "%",
            "{:.2f}".format(J[-1] - 50) + "%",
        ],
        log_path,
        " ",
    )
    KD_result = kd_analysis(K, D)
    p_log(["\n\t\t\t\t\tAction:", KD_result, "\n"], log_path)

    p_log(
        [
            "\t\t\t\tMACD [DIF, MACD, DIF_MACD]:",
            "{:.2f}".format(DIF[-1]),
            "{:.2f}".format(MACD[-1]),
            "{:.2f}".format(DIF_MACD[-1]),
        ],
        log_path,
        " ",
    )
    MACD_result = macd_analysis(DIF_MACD)
    p_log(["\n\t\t\t\t\tAction:", MACD_result, "\n"], log_path)

    p_log(
        [
            "\t\t\t\tEMA  [EMA12, EMA26]:",
            "{:.2f}".format(EMA12[-1]),
            "{:.2f}".format(EMA26[-1]),
        ],
        log_path,
        " ",
    )
    EMA_result = ema_analysis(EMA12, EMA26, stock_close)
    p_log(["\n\t\t\t\t\tAction:", EMA_result, "\n"], log_path)

    p_log(
        [
            "\t\t\t\tLFT   [LL, UL]:",
            "[" + "{:.2f}".format(stock_close_lft_LL[-1]) + ",",
            "{:.2f}".format(stock_close_lft_UL[-1]) + "]",
        ],
        log_path,
        " ",
    )
    LFT_result = lowpassfilter_analysis(
        Stock_now, stock_close_lft, stock_close_lft_UL, stock_close_lft_LL
    )
    p_log(["\n\t\t\t\t\tAction:", LFT_result, "\n"], log_path)

    p_log(
        [
            "\t\t\t\tBBand [LL, UL]:",
            "[" + "{:.2f}".format(LL[-1]) + ",",
            "{:.2f}".format(UL[-1]) + "]",
        ],
        log_path,
        " ",
    )
    BB_result = bbands_analysis(Stock_now, LL, UL, Center)
    p_log(["\n\t\t\t\t\tAction:", BB_result, "\n"], log_path)

    result_list = [
        BR_result,
        KD_result,
        LFT_result,
        BB_result,
        MACD_result,
        EMA_result,
    ]

    result_buy_num = 0
    result_sell_num = 0
    total_result = "Nothing"
    for result in result_list:
        if "Sell" in result or "SELL" in result:
            result_sell_num += 1
        elif "Buy" in result or "BUY" in result:
            result_buy_num += 1

    if result_sell_num >= 2 and result_buy_num < 2:
        total_result = "SELL!"
        suggestion_sell.append(stock_name)
    elif result_buy_num >= 2 and result_sell_num < 2:
        total_result = "BUY!"
        suggestion_buy.append(stock_name)
        invest_total += sugg_pos * round(Stock_now, 2)
    p_log(["\t--\tSUGGESTION:", total_result, "--"], log_path)
    p_log(["\n\n"], log_path)

    if isplot and G_plot:
        print("\n")
        ma_name_list = []
        for m in range(len(desire_MA)):
            ma_name_list.append("MA_" + str(desire_MA[m]))
        ###########################
        plot_dict = {
            # "Vol-price": {
            #     "value_list": [Vol_pri],
            #     "value_name": ["Vol-price"],
            #     "Ylabel": "Total price ($)",
            # },
            # "BR": {
            #     "value_list": [BR],
            #     "value_name": ["BR"],
            #     "Ylabel": "Ratio (%)",
            # },
            # "KD": {
            #     "value_list": [K, D, J],
            #     "value_name": ["K", "D", "J"],
            #     "Ylabel": "Ratio (%)",
            # },
            # "LFT": {
            #     "value_list": [
            #         stock_close_lft,
            #         stock_close_lft_UL,
            #         stock_close_lft_LL,
            #     ],
            #     "value_name": ["LFT", "LFT_UL", "LFT_LL"],
            #     "Ylabel": "Price ($)",
            # },
            # "MA": {
            #     "value_list": stock_MA_list,
            #     "value_name": ma_name_list,
            #     "Ylabel": "Price ($)",
            # },
            # "BBand": {
            #     "value_list": [Center, UL, LL, UL_s, LL_s],
            #     "value_name": ["MA_20", "UL", "LL", "UL_s", "LL_s"],
            #     "Ylabel": "Price ($)",
            # },
            "MACD": {
                "value_list": [DIF, MACD, DIF_MACD],
                "value_name": ["DIF", "MACD", "DIF_MACD"],
                "Ylabel": "Ratio",
            },
            "EMA": {
                "value_list": [EMA12, EMA26, EMA_20MA],
                "value_name": ["EMA12", "EMA26", "MA20"],
                "Ylabel": "Price ($)",
            },
            "Vegas": {
                "value_list": [EMA12, EMA30, EMA60, EMA120, EMA240],
                "value_name": ["EMA12", "EMA30", "EMA60", "EMA120", "EMA240"],
                "Ylabel": "Price ($)",
            },
            # "ATR": {
            #       "value_list": [ATR],
            #       "value_name": ["ATR"],
            # "Ylabel": ""
            # },
        }

        for plot_key in plot_dict:
            title = plot_key
            temp_date = []
            for d in stock_date:
                temp_date.append(d.split("-", 1)[1].replace("-", "/"))
            X_value = temp_date
            Y_value_list = [stock_close] + plot_dict[plot_key]["value_list"]
            Y_value_lable_list = ["Close"] + plot_dict[plot_key]["value_name"]
            Xlabel = "Date"
            Ylabel = plot_dict[plot_key]["Ylabel"]
            save_png_path = (
                folder_name
                + "/"
                + stock_code
                + "_"
                + plot_key
                + "_"
                + stock_date[-1]
                + ".png"
            )
            plot_something(
                stock_code,
                title,
                X_value,
                Y_value_list,
                Y_value_lable_list,
                Xlabel,
                Ylabel,
                save_png_path,
                plot_range_num,
            )


tEnd = time.time()

p_log(["It cost ", (tEnd - tStart), "sec"], log_path)
p_log(["============ Plot Database Finish ============"], log_path)
p_log(["==============================================\n\n"], log_path)


p_log(["=============================================="], log_path)
p_log(["========== Summary of Stock Action ==========="], log_path)
p_log(["Suggest to Buy:"], log_path, " ")
for i in suggestion_buy:
    p_log([i], log_path, " ")

p_log(["\n"], log_path)
p_log(["Suggest to Sell:"], log_path, " ")
for i in suggestion_sell:
    p_log([i], log_path, " ")

p_log(["\n"], log_path)
p_log(["=============== Summary Finish ==============="], log_path)
p_log(["==============================================\n\n"], log_path)


p_log(
    ["If suggest all sotcks, total invest money:", str(invest_total)], log_path
)

# plt.grid( b=True, which='major', color='#666666', linestyle='--' )
