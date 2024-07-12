# For Stock analyze

1.Moving average (5 days,15 days,20 days,30 days,60 days, 90 days)
    def Cal_MA(input,samples=5):
        pd.rolling(samples).mean (maybe like this)

1. Bias Rate (乖離率)
    def Cal_BR(input,samples=10):
        (Closeprice-MA(samples))/MA(samples) * 100 (%)

   NOTE: 1. 1 < Bias Rate < 7 => 市場過熱 賣壓會重 股價跌
         1. -7 < Bias Rate < -1 => 市場過冷 買壓會重 股價漲

1.stochastic  oscillator(KD)
    def Cal_KD(input):
        RSV= (Closeprice - Min(i-8,i)) / (Max(i-8,i) - Min(i-8,i)) *100 (%)
        k(i) = 2/3*k(i-1)+ 1/3*RSV
        D(i) = 2/3*D(i-1)+ 1/3*k(i)

    NOTE:1.KD >80 時，為高檔超買訊號，市場過熱，股價要開始 "跌"了。
            高檔鈍化: KD的 K值在80以上 連續3天
                     表示非常的強勢，通常會再漲的機會 就會變得非常高。
         1.KD <20 時，為低檔超賣訊號，市場過冷，股價要開始 "漲"了。
            低檔鈍化: KD的 K值在20以下 連續3天
                     表示非常的弱勢，通常會再跌的機會 就會變得非常高。

1.Bollinger Bands (BBands)
    def Cal_BBands(input,numofSD=2):
        center = Cal_MA(input,20)
        SD = []
        for i in range(len(input)):
            SD(i) = Cal_SD(input[0:i+1])
        UL = center + numofSD \* SD
        LL = center - numofSD \* SD

        UL_small = center + 0.1 \* SD
        LL_small = center - 0.1 \* SD



    NOTE: 1. 價格由下向上，穿越下軌線時是買進訊號。
             價格由下向上，穿越中間線時股價可能加速向上，是加碼買進訊號。
             價格在中間線與上軌線之間，波動為多頭市場，可做多。
          2. 價格在中間線與上軌線間，由上往下跌破中間線，為賣出訊號。
             價格在中間線與下軌線之間，向下波動時為空頭市場，可做空。
          => Summary:
          1. if price(i) < LL(i) && price(i-1) < LL(i-1) && price(i) > price(i-1) = buy (the better is for 2-3 day with this signal then take action)
             if LL_small(i) < price(i) < UL_small(i) && price(i) > price(i-1) = buy (this stock may rise very fast)
             if LL(i) < price(i) <  UL(i) = buy (for long turn)
          2. if UL_small(i-1) < price(i-1)< UL(i-1) && price(i) < UL_small(i) = sell
             if price(i) > UL(i) && price(i-1) > UL(i-1) && price(i) < price(i-1) = sell

1. Low pass filter( want to avoid the phase difference between the result with the raw data, MA will have the phase difference)
    a. manually method.

OTHER FUNCTION

1.Standard Deviation(SD)
    import statistics
    def Cal_SD(input_list):
        SD = statistics.stdev(input_list)

MODIFY
1.Use the yfinance to get the history info to save to the database (now is pandas_datareader) ==> maybe it is not necessary.
1.Use the mySQL to store the database (now is separated and stored in local only)
