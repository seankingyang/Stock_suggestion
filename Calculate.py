# import math
import statistics
from Utility import numerify
import talib
import numpy as np


# Percentage
# unit %
def Cal_percentage(previous, new):
    previous = numerify(previous, "Float")
    new = numerify(new, "Float")

    # Create numpy arrays with at least two values
    values = np.array([previous, new])

    # Calculate percentage change using talib
    per = talib.ROC(values, timeperiod=1)[-1]

    # Format the result to two decimal places
    return per


# Moving Average (MA)
# unit $

# def Cal_MA_mean(import_list):
#     import_list = numerify(import_list, "Float")
#     return statistics.mean(import_list)


def Cal_MA(Total_import_list, samples=5):
    # Convert the input list to a numpy array of floats
    Total_import_list = np.array(Total_import_list, dtype=float)

    # Calculate the simple moving average (SMA) using talib
    MA = talib.SMA(Total_import_list, timeperiod=samples)

    # Convert the result to a list and return
    return MA.tolist()


def Cal_MA_with_desirelist(Total_import_list, desire_ma_list):
    MA_list = []
    for samples in desire_ma_list:
        tmp_list = Cal_MA(Total_import_list, numerify(samples, "Int"))
        MA_list.append(tmp_list)
    return MA_list


# Bias Rate (BIAS, BR)
# unit %
def Cal_BR(Total_import_list, samples=10):
    Total_import_list = numerify(Total_import_list, "Float")
    length = len(Total_import_list)
    BR = []

    for i in range(length):
        if i + 1 < samples:
            br = None
        else:
            sub_list = Total_import_list[i - samples + 1 : i + 1]
            last_close_price = sub_list[-1]

            # Calculate the simple moving average (SMA) using talib
            MA = talib.SMA(np.array(sub_list), timeperiod=samples)[-1]

            br = (last_close_price - MA) / MA * 100

        BR.append(br)

    return BR


# Stochastic Oscillator (KD)
# unit %


# TODO: check the calculation
def Cal_KDJ(stock_high, stock_low, stock_close, samples=10):
    stock_high = np.array(numerify(stock_high, "Float"))
    stock_low = np.array(numerify(stock_low, "Float"))
    stock_close = np.array(numerify(stock_close, "Float"))
    # Calculate the Stochastic Oscillator using talib
    K, D = talib.STOCH(
        stock_high,
        stock_low,
        stock_close,
        fastk_period=samples,
        slowk_period=3,
        slowd_period=3,
        slowk_matype=0,
        slowd_matype=0,
    )

    # Calculate J values
    J_shift = 50
    J = K - D + J_shift

    return K.tolist(), D.tolist(), J.tolist()


# Bolllinger Bands (BBands)
# unit $
def Cal_STD(import_list):
    return statistics.stdev(import_list)


def Cal_BBands(Total_import_list, numofSTD=2.1, samples=20):
    Total_import_list = numerify(Total_import_list, "Float")
    length = len(Total_import_list)

    Center = Cal_MA(Total_import_list, samples)

    STD = []
    for i in range(length):
        if i + 1 < samples:
            std = None
        else:
            std = Cal_STD(Total_import_list[i - samples + 1 : i + 1])
        STD.append(std)

    UL, LL, UL_s, LL_s = [], [], [], []
    for i in range(length):
        if i + 1 < samples:
            ul, ll, ul_s, ll_s = None, None, None, None
        else:
            ul = Center[i] + numofSTD * STD[i]
            ll = Center[i] - numofSTD * STD[i]
            ul_s = Center[i] + 0.1 * STD[i]
            ll_s = Center[i] - 0.1 * STD[i]
        UL.append(ul)
        LL.append(ll)
        UL_s.append(ul_s)
        LL_s.append(ll_s)
    return Center, UL, LL, UL_s, LL_s


# Low Pass Filter (LPF)
# unit $
# notice: according to the sample rate is 1 (everday get the data once)
def Cal_lowpassfilter(Total_import_list, sample_rate=1, Cutoff_freq=0.5):
    RC = 1 / (Cutoff_freq * 2 * 3.1415)
    dt = 1 / sample_rate
    alpha = dt / (RC + dt)
    output = []
    output = output + [Total_import_list[0]]

    for i in range(1, len(Total_import_list)):
        output = output + [
            output[i - 1] + (alpha * (Total_import_list[i] - output[i - 1]))
        ]

    return output


# Volume and Price
def Cal_Vol_Price(Total_import_list_volume, Total_import_list_price):
    output = []
    volume_len = len(Total_import_list_volume)
    price_len = len(Total_import_list_price)
    if volume_len == price_len:
        isSameLen = True
    else:
        isSameLen = False

    if isSameLen:
        for i in range(volume_len):
            volume_price = (
                Total_import_list_volume[i] * Total_import_list_price[i]
            )
            output.append(volume_price)

    return output


# Moving Average Convergence Divergence (MACD)
def Cal_EMA(
    Total_import_list, Total_import_list_High, Total_import_list_Low, samples
):
    length = len(Total_import_list)
    EMA = []
    DI = 0
    for i in range(length):
        if i + 1 < samples:
            ema = None
            DI = (
                DI
                + (
                    Total_import_list_High[i]
                    + Total_import_list_Low[i]
                    + Total_import_list[i] * 2
                )
                / 4
            )
        elif i + 1 == samples:
            ema = DI / samples
        else:
            ema = (EMA[-1] * (samples - 1) + Total_import_list[i] * 2) / (
                samples + 1
            )

        EMA.append(ema)
    return EMA


def Cal_MACD(
    Total_import_list,
    Total_import_list_High,
    Total_import_list_Low,
    Sample_1=12,
    Sample_2=26,
    Sample_Dif=9,
):
    MACD, DIF, DIF_MACD = [], [], []
    if Sample_1 > Sample_2:
        temp = Sample_2
        Sample_2 = Sample_1
        Sample_1 = temp

    if Sample_1 != Sample_2:
        EMA_1 = Cal_EMA(
            Total_import_list,
            Total_import_list_High,
            Total_import_list_Low,
            Sample_1,
        )
        EMA_2 = Cal_EMA(
            Total_import_list,
            Total_import_list_High,
            Total_import_list_Low,
            Sample_2,
        )
        for i in range(len(EMA_1)):
            if EMA_1[i] and EMA_2[i]:
                DIF.append(EMA_1[i] - EMA_2[i])
            else:
                DIF.append(None)

        length = len(DIF)
        for j in range(length):
            if j + 1 < Sample_2 + Sample_Dif:
                macd = None
            elif j + 1 == Sample_2 + Sample_Dif:
                macd = (
                    sum(DIF[Sample_2 : (Sample_2 + Sample_Dif)]) / Sample_Dif
                )
            else:
                macd = (MACD[-1] * (Sample_Dif - 1) + DIF[j] * 2) / (
                    Sample_Dif + 1
                )
            MACD.append(macd)

        for k in range(length):
            if DIF[k] is None or MACD[k] is None:
                dif_macd = None
            else:
                dif_macd = DIF[k] - MACD[k]
            DIF_MACD.append(dif_macd)

    return DIF, MACD, DIF_MACD


# Exponential Moving Average (EMA)
# EMA_now = EMA_prev + alpa * (Rawdata_now - EMA_prev)
# alpa = 2/(N+1)
def Cal_Tr(
    Total_import_list, Total_import_list_High, Total_import_list_Low
):  # True range
    length = len(Total_import_list)
    Tr = []
    for i in range(length):
        if i == 0:
            tr = 0.0
        else:
            tr = max(
                (Total_import_list_High[i] - Total_import_list_Low[i]),
                abs(Total_import_list_High[i] - Total_import_list[i - 1]),
                abs(Total_import_list_Low[i] - Total_import_list[i - 1]),
            )
        Tr.append(tr)
    return Tr


def Cal_EMA_pos(
    Total_import_list, Total_import_list_High, Total_import_list_Low, samples
):
    length = len(Total_import_list)
    EMA_pos = []
    Tr = Cal_Tr(
        Total_import_list, Total_import_list_High, Total_import_list_Low
    )
    for i in range(length):
        if i + 1 < samples:
            ema_pos = None
        elif i + 1 == samples:
            ema_pos = sum(Tr[0:samples]) / samples
        else:
            ema_pos = (EMA_pos[-1] * (samples - 1) + Tr[i] * 2) / (samples + 1)

        EMA_pos.append(ema_pos)
    return EMA_pos


# Average True Range (ATR)
def Cal_ATR(
    Total_import_list,
    Total_import_list_High,
    Total_import_list_Low,
    samples=21,
):
    ATR = Cal_EMA_pos(
        Total_import_list,
        Total_import_list_High,
        Total_import_list_Low,
        samples,
    )
    return ATR
