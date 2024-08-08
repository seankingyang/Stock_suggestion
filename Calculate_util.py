import numpy as np
import pandas as pd
from talib import abstract
import json


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


def cal_SMA(dataframe, sample_period_list=[10]):
    df = modify_dataframe_header(dataframe)
    output_df = pd.DataFrame()
    for sample_period in sample_period_list:
        output_df[f"SMA_{sample_period}"] = abstract.SMA(
            df, timeperiod=sample_period
        )
    return output_df


def cal_ADX(dataframe, sample_period=14):
    df = modify_dataframe_header(dataframe)

    output_df = pd.DataFrame()
    output_df[f"ADX_{sample_period}"] = abstract.ADX(
        df,
        timeperiod=sample_period
    )
    return output_df


def cal_ADXR(dataframe, sample_period=14):
    df = modify_dataframe_header(dataframe)

    output_df = pd.DataFrame()
    output_df[f"ADXR_{sample_period}"] = abstract.ADXR(
        df,
        timeperiod=sample_period
    )
    return output_df

def cal_CDLDARKCLOUDCOVER(dataframe, penetration=0.5):
    df = modify_dataframe_header(dataframe)

    output_df = pd.DataFrame()
    output_df[f"CDLDARKCLOUDCOVER_{penetration}"] = abstract.CDLDARKCLOUDCOVER(
        df, penetration=penetration
    )
    return output_df


file_path = "/home/isaacyang/Stock_suggestion/DataBase/0050.csv"
df = pd.read_csv(file_path)
print(df)


