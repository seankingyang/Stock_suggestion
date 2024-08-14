import pandas as pd
import numpy as np
import random


def create_signal_fake_data(
    end_date="2022-01-02",
    num_days=50,
    buy_weight=0.35,
    sell_weight=0.35,
    min_position=500,
    max_position=2000,
):
    """
    Generate fake signal data for backtesting.

    Parameters:
    - end_date (str): The start date for the data in 'YYYY-MM-DD' format.
    - num_days (int): The number of days before end_date to generate data for.
    - buy_weight (float): The probability weight for 'buy' signals.
    - sell_weight (float): The probability weight for 'sell' signals.
    - min_position (int): The minimum position size for 'buy' signals.
    - max_position (int): The maximum position size for 'buy' signals.

    Returns:
    - pd.DataFrame: A DataFrame containing the generated signal data.
    """
    start_date = pd.to_datetime(end_date) - pd.Timedelta(days=num_days - 1)
    dates = pd.date_range(
        start=start_date, end=end_date, freq="B"
    )  # 'B' for business days

    hold_weight = 1 - buy_weight - sell_weight
    signals = random.choices(
        ["buy", "sell", "hold"],
        weights=[buy_weight, sell_weight, hold_weight],
        k=len(dates),
    )

    positions = [
        random.randint(min_position, max_position) if s == "buy" else 0
        for s in signals
    ]

    signal_data = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d 00:00:00+08:00"),
            "buy or sell": signals,
            "position": positions,
        }
    )

    # Ensure 'sell' signals always follow 'buy' signals
    for i in range(1, len(signal_data)):
        if (
            signal_data.loc[i, "buy or sell"] == "sell"
            and signal_data.loc[i - 1, "position"] == 0
        ):
            signal_data.loc[i, "buy or sell"] = "hold"
            signal_data.loc[i, "position"] = 0

    return signal_data


def backtest_portfolio(
    signal_df, stock_num, initial_capital=100000, initial_position=0
):
    # Read the stock data
    stock_data = pd.read_csv(f"./DataBase/{stock_num}.csv")
    stock_data["Date"] = pd.to_datetime(stock_data["Date"])
    stock_data.set_index("Date", inplace=True)

    # Convert signal_df date to datetime for proper merging
    signal_df["date"] = pd.to_datetime(signal_df["date"])

    # Merge signal data with stock data
    merged_data = signal_df.merge(
        stock_data, left_on="date", right_index=True, how="inner"
    )

    # Initialize portfolio metrics
    portfolio_value = initial_capital
    position = initial_position
    trades = []

    for _, row in merged_data.iterrows():
        date = row["date"]
        signal = row["buy or sell"]
        price = row["Close"]
        target_position = row["position"]

        if signal == "buy":
            shares_to_buy = target_position - position
            if shares_to_buy > 0:
                cost = shares_to_buy * price
                if cost <= portfolio_value:
                    portfolio_value -= cost
                    position += shares_to_buy
                    trades.append(("buy", date, shares_to_buy, price))
                else:
                    # Not enough capital to buy all shares
                    affordable_shares = portfolio_value // price
                    cost = affordable_shares * price
                    portfolio_value -= cost
                    position += affordable_shares
                    trades.append(("buy", date, affordable_shares, price))
        elif signal == "sell":
            shares_to_sell = position - target_position
            if shares_to_sell > 0:
                revenue = shares_to_sell * price
                portfolio_value += revenue
                position -= shares_to_sell
                trades.append(("sell", date, shares_to_sell, price))

    # Calculate final portfolio value
    if position > 0:
        final_price = merged_data["Close"].iloc[-1]
        portfolio_value += position * final_price

    return portfolio_value, trades, position


# Example usage
signal_data = create_signal_fake_data(
    end_date="2022-05-02", num_days=100,
    min_position=2000000, max_position=2000000
)

# Print the first few rows of the generated data
print(signal_data.head(20))

stock_num = "0050"  # Example stock number
initial_capital = 100000
initial_position = 0

final_value, trade_history, final_position = backtest_portfolio(
    signal_data, stock_num, initial_capital, initial_position
)

print(f"\nInitial capital: ${initial_capital:.2f}")
print(
    f"Final portfolio value: ${final_value:.2f}, "
    f"profit: ${final_value - initial_capital:.2f} "
    f"({(final_value - initial_capital) / initial_capital * 100:.2f}%)"
)
print(f"Final position: {final_position} shares")
print("\nTrade history:")
for trade in trade_history:
    print(
        f"{trade[0].capitalize()} {trade[2]} shares at "
        f"${trade[3]:.2f} on {trade[1]}"
    )
