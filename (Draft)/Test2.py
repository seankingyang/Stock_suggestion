import talib as ta
import matplotlib.pyplot as plt

plt.style.use('bmh')
import yfinance as yf
import numpy as np
import math
import pandas as pd
from pandas_datareader import data
import csv
from datetime import date, timedelta
from blessings import Terminal
import sys, os
from func_timeout import func_set_timeout


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


@func_set_timeout(10)
def data_download_wrapper(symbol, start, end, interval_t='None'):
    try:
        blockPrint()
        if (interval_t == 'None'):
            price_data = yf.download(symbol, start, end)
        else:
            price_data = yf.download(symbol, start, end, interval=interval_t)
        enablePrint()
        return price_data
    except:
        raise


def request_data(symbol, start, end, interval='None'):
    get_data = False
    price_data = None
    while get_data is False:
        try:
            price_data = data_download_wrapper(symbol, start, end, interval)
            get_data = True
        except:
            print('ERROR: Time out! Retry!')
            get_data = False
        if price_data is None:
            get_data = False
    return price_data


def RegisterAction(direction, symbol, price, amount):
    global available_fund
    global account_dict
    global total_fund
    global num_shares
    if (direction > 0 and price * amount > available_fund):
        print("LOG: Do not have enough fund to do ")
        return
    if (direction > 0):
        available_fund = available_fund - price * amount
        new_price = price
        if (symbol in account_dict.keys()):
            old_price = account_dict[symbol]['price']
            new_price = (price * amount + old_price * num_shares) / (num_shares + amount)
        account_dict[symbol] = {'price': new_price, 'amount': num_shares + amount}
        num_shares = num_shares + amount
        print("LOG: Successfuly buy: " + symbol + " at " + str(price))
        return
    if (direction < 0):
        if (symbol in account_dict.keys() and account_dict[symbol]['amount'] > 0):
            sell_amount = amount
            if (num_shares <= sell_amount):
                sell_amount = num_shares
            get_fund = price * sell_amount
            account_dict[symbol]['amount'] = num_shares - sell_amount
            num_shares = num_shares - sell_amount
            available_fund = available_fund + get_fund
            print("LOG: Successfuly sell: " + symbol + " at " + str(price))
        else:
            print("LOG: Do not have " + symbol + " in stock. Cannot sell.")


def GetCurrentAccountInfo(time):
    global available_fund
    global account_dict
    global total_fund
    global highest_profit
    global lowest_profit
    f = open("account_info_jiucai.txt", "w")
    f.write(str(account_dict))
    f.close()

    cur_fund = 0
    cur_asset_stock = 0
    real_check_time = time + timedelta(days=1)
    before_time = time - timedelta(days=1)
    for key in account_dict:
        # keys are symbols
        # Check the current price, compute the profit/loss
        in_stock_amount = account_dict[key]['amount']
        if (in_stock_amount == 0):
            continue
        buy_price = account_dict[key]['price']
        price_data = request_data(key, str(before_time), str(real_check_time))
        cur_fund = cur_fund + in_stock_amount * (price_data['Close'].values[-1] - buy_price)
        cur_asset_stock = cur_asset_stock + in_stock_amount * (price_data['Close'].values[-1])
    t = Terminal()
    print(t.red("LOG: Current available fund is: " + str(available_fund)))
    print(t.red("LOG: Current gain/loss is: " + str(cur_fund)))
    print(t.red("LOG: Total asset is: " + str(available_fund + cur_asset_stock)))
    if available_fund + cur_asset_stock > highest_profit:
        highest_profit = available_fund + cur_asset_stock
    if available_fund + cur_asset_stock < lowest_profit:
        lowest_profit = available_fund + cur_asset_stock


# Account Settings
available_fund = 100000
total_fund = 100000
num_shares = 0
account_dict = {}

# Testing Range
test_start_time = date(2019, 2, 1)
test_end_time = date(2020, 12, 25)

strong_change = 0.02
percent_buy = 0.4  # of total fund

highest_profit = 0
lowest_profit = available_fund

symbol = 'GOOGL'

read_last_time = False
if read_last_time:
    read_dict = np.load('account_record_jiucai.npy', allow_pickle='TRUE').item()
    test_start_time = read_dict['start_time'] + timedelta(days=7)
    account_dict = read_dict['account']
    available_fund = read_dict['fund']
    highest_profit = read_dict['high']
    lowest_profit = read_dict['low']


def is_morning_bearish(today_bar, percentage):
    print("Morning variation is: " + str(
        (today_bar['Open'].values[1] - today_bar['Open'].values[0]) / today_bar['Open'].values[0]))
    return today_bar['Open'].values[1] < today_bar['Open'].values[0] * (1 - percentage)


def is_morning_bullish(today_bar, percentage):
    return today_bar['Open'].values[1] > today_bar['Open'].values[0] * (1 + percentage)


def is_afternoon_bullish(today_bar, percentage):
    print("Afternoon variation is: " + str(
        (today_bar['Close'].values[-1] - today_bar['Open'].values[-3]) / today_bar['Open'].values[-3]))
    return today_bar['Close'].values[-1] > today_bar['Open'].values[-3] * (1 + percentage)


def is_yesterday_afternoon_bearish(yesterday_bar, percentage):
    return yesterday_bar['Close'].values[-1] < yesterday_bar['Open'].values[-3] * (1 - percentage)


while test_start_time < test_end_time:
    today = test_start_time
    today_data = request_data(symbol, str(today), str(today + timedelta(days=1)), interval='1h')
    while (today_data.shape[0] == 0):
        today = today + timedelta(days=1)
        today_data = request_data(symbol, str(today), str(today + timedelta(days=1)), interval='1h')

    yesterday = today - timedelta(days=1)
    yesterday_data = request_data(symbol, str(yesterday), str(today), interval='1h')
    while (yesterday_data.shape[0] == 0):
        yesterday = yesterday - timedelta(days=1)
        yesterday_data = request_data(symbol, str(yesterday), str(today), interval='1h')
    print("LOG_time: Testing: " + str(today) + " and " + str(yesterday))

    if (is_yesterday_afternoon_bearish(yesterday_data, strong_change)):
        # Buy signal
        buy_price = today_data['Open'].values[0]
        buy_amount = (available_fund + buy_price * num_shares) * percent_buy / buy_price
        RegisterAction(1, symbol, buy_price, buy_amount)

    if (is_morning_bearish(today_data, strong_change)):
        # Buy signal
        buy_price = today_data['Open'].values[1]
        buy_amount = (available_fund + buy_price * num_shares) * percent_buy / buy_price
        RegisterAction(1, symbol, buy_price, buy_amount)

    if (is_morning_bullish(today_data, strong_change)):
        # Sell signal
        sell_price = today_data['Open'].values[1]
        sell_amount = (available_fund + sell_price * num_shares) * percent_buy / sell_price
        RegisterAction(-1, symbol, sell_price, sell_amount)

    if (is_afternoon_bullish(today_data, strong_change)):
        # Sell signal
        sell_price = today_data['Open'].values[-2]
        sell_amount = (available_fund + sell_price * num_shares) * percent_buy / sell_price
        RegisterAction(-1, symbol, sell_price, sell_amount)

    # Check assets every week
    GetCurrentAccountInfo(today)
    account_record = {'start_time': today, 'account': account_dict, 'fund': available_fund,
                      'high': highest_profit, 'low': lowest_profit}
    np.save('account_record_jiucai.npy', account_record)
    test_start_time = today + timedelta(days=1)
print('Profit rate: ' + str((highest_profit - total_fund) / total_fund * 100))
print('Loss rate: ' + str((total_fund - lowest_profit) / total_fund * 100))












