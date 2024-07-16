def br_analysis(BR):
    result = "Neutral"
    if BR[-1] < -10:
        result = "Extremely Low - Strong Buy"
    elif BR[-1] < -7:
        result = "Very Low - Buy"
    elif BR[-1] < -5:
        result = "Low - Consider Buying"
    elif BR[-1] > 10:
        result = "Extremely High - Strong Sell"
    elif BR[-1] > 7:
        result = "Very High - Sell"
    elif BR[-1] > 5:
        result = "High - Consider Selling"
    return result


def kd_analysis(K, D):
    result = "Neutral"
    if K[-1] > 80 and D[-1] > 80:
        if K[-1] < K[-2] and K[-1] < D[-1]:
            result = "Overbought - Consider Selling"
        else:
            result = "Overbought - Caution"
    elif K[-1] < 20 and D[-1] < 20:
        if K[-1] > K[-2] and K[-1] > D[-1]:
            result = "Oversold - Consider Buying"
        else:
            result = "Oversold - Caution"
    return result


def macd_analysis(DIF_MACD):
    result = "Neutral"
    if (DIF_MACD[-1] > 0 and DIF_MACD[-3] > 0 and DIF_MACD[-2] > 0) or (
        DIF_MACD[-1] < 0 and DIF_MACD[-3] < 0 and DIF_MACD[-2] < 0
    ):
        trend = "High" if DIF_MACD[-1] > 0 else "Low"
        if DIF_MACD[-3] > DIF_MACD[-2] and DIF_MACD[-2] > DIF_MACD[-1]:
            result = f"{trend} - SELL Signal"
        elif DIF_MACD[-3] < DIF_MACD[-2] and DIF_MACD[-2] < DIF_MACD[-1]:
            result = f"{trend} - BUY Signal"
        else:
            result = f"{trend} - Stability, observe further"
    elif DIF_MACD[-1] > 0 and DIF_MACD[-2] < 0:
        result = "Bullish Crossover - BUY Signal"
    elif DIF_MACD[-1] < 0 and DIF_MACD[-2] > 0:
        result = "Bearish Crossover - SELL Signal"
    elif DIF_MACD[-1] == 0:
        if DIF_MACD[-2] > 0:
            result = "Neutral - Leaning to SELL"
        elif DIF_MACD[-2] < 0:
            result = "Neutral - Leaning to BUY"

    return result


def ema_analysis(EMA12, EMA26, stock_close):
    result = "Neutral"
    # Bullish crossover
    if EMA12[-2] < EMA26[-2] and EMA12[-1] >= EMA26[-1]:
        result = "Bullish Crossover - BUY Signal"
    # Bearish crossover
    elif EMA12[-2] > EMA26[-2] and EMA12[-1] <= EMA26[-1]:
        result = "Bearish Crossover - SELL Signal"
    # Price moves above EMA12
    elif stock_close[-1] > EMA12[-1] and stock_close[-2] <= EMA12[-2]:
        result = "Price above EMA12 - Consider BUY"
    # Price moves below EMA12
    elif stock_close[-1] < EMA12[-1] and stock_close[-2] >= EMA12[-2]:
        result = "Price below EMA12 - Consider SELL"
    return result


def lowpassfilter_analysis(
    Stock_now, stock_close_lft, stock_close_lft_UL, stock_close_lft_LL
):
    result = "Neutral"
    if (
        Stock_now > stock_close_lft_UL[-1]
        and stock_close_lft[-1] < stock_close_lft[-2]
    ):
        result = "Overbought - SELL Signal"
    elif (
        Stock_now < stock_close_lft_LL[-1]
        and stock_close_lft[-1] > stock_close_lft[-2]
    ):
        result = "Oversold - BUY Signal!"
    return result


def bbands_analysis(Stock_now, LL, UL, Center):
    result = "Neutral"
    # If the current stock price is above the Upper Limit and the Center line is trending downwards
    if Stock_now > UL[-1] and Center[-1] < Center[-2]:
        result = "Overbought - Consider SELLING"
    # If the current stock price is below the Lower Limit and the Center line is trending upwards
    elif Stock_now < LL[-1] and Center[-1] > Center[-2]:
        result = "Oversold - Consider BUYING"
    return result
