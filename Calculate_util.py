import numpy as np
import pandas as pd
from talib import abstract
import json
import matplotlib.pyplot as plt


def get_talib_function_help_json_info():
    import talib

    groups_function = talib.get_function_groups()
    help_dict = {}
    for key, value in groups_function.items():
        help_dict[key] = {}
        for func in value:

            info = abstract.Function(func).info
            help_dict[key][func] = {"help_info": info}
    return json.dumps(help_dict, indent=3)


def modify_dataframe_header(dataframe):
    # Convert all column names to lowercase
    dataframe.columns = dataframe.columns.str.lower()
    return dataframe


class Calculate_util:
    def __init__(self, dataframe):
        self.df = modify_dataframe_header(dataframe)

    def cal_SMA(self, sample_period_list=[10]):
        output_df = pd.DataFrame()
        for sample_period in sample_period_list:
            column_name = f"SMA_{sample_period}"
            output_df[column_name] = abstract.SMA(
                self.df, timeperiod=sample_period
            )
        return output_df

    def cal_ICHIMOKUCLOUD(
        self, transfer_period=9, base_period=26, lagging_period=52
    ):  
        #column_name = (f"ICHIMOKUCLOUD_{transfer_period}_"
        #               f"{base_period}_{lagging_period}")
        output_df = pd.DataFrame()
        high_transfer = self.df['high'].rolling(window=transfer_period).max()
        low_transfer = self.df['low'].rolling(window=transfer_period).min()
        output_df[f"transfer_line_{transfer_period}"] = (
            high_transfer + low_transfer
        ) / 2

        high_base = self.df['high'].rolling(window=base_period).max()
        low_base = self.df['low'].rolling(window=base_period).min()
        output_df[f"base_line_{base_period}"] = (high_base + low_base) / 2

        output_df["Leading_line_A"] = (
            (output_df[f"transfer_line_{transfer_period}"] + 
             output_df[f"base_line_{base_period}"]) / 2
        ).shift(base_period)

        high_lagging = self.df['high'].rolling(window=lagging_period).max()
        low_lagging = self.df['low'].rolling(window=lagging_period).min()
        output_df["Leading_line_B"] = (
            (high_lagging + low_lagging) / 2
        ).shift(base_period)

        output_df["Lagging_line"] = self.df['close'].shift(base_period)
        return output_df

    def cal_ADX(self, sample_period=14):

        output_df = pd.DataFrame()
        column_name = f"ADX_{sample_period}"
        output_df[column_name] = abstract.ADX(
            self.df,
            timeperiod=sample_period
        )
        return output_df

    def cal_ADXR(self, sample_period=14):

        output_df = pd.DataFrame()
        column_name = f"ADXR_{sample_period}"
        output_df[column_name] = abstract.ADXR(
            self.df,
            timeperiod=sample_period
        )
        return output_df

    def cal_CDLCOUNTERATTACK(self):
        column_name = "CDLCOUNTERATTACK"
        output_df = pd.DataFrame()
        output_df[column_name] = abstract.CDLCOUNTERATTACK(
            self.df
        )
        return output_df

    def cal_CDLDARKCLOUDCOVER(self, penetration=0.5):
        column_name = f"CDLDARKCLOUDCOVER_{penetration}"
        output_df = pd.DataFrame()
        output_df[column_name] = abstract.CDLDARKCLOUDCOVER(
            self.df,
            penetration=penetration
        )
        return output_df


file_path = "/home/isaacyang/Stock_suggestion/DataBase/0050.csv"
df = pd.read_csv(file_path)
print(df)
cal_util = Calculate_util(df)

output_df = cal_util.cal_ICHIMOKUCLOUD()
print(output_df)


def plot_df_and_output_df(df, output_df, x=200):
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'].tail(x), df['close'].tail(x), label='close')
    for column in output_df.columns:
        plt.plot(df['date'].tail(x), output_df[column].tail(x), label=column)
    plt.legend()
    plt.show()


plot_df_and_output_df(df, output_df)


