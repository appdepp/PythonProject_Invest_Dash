import yfinance as yf
import pandas as pd


def load_price_data(tickers, start="2022-01-01", end="2024-12-31"):
    if isinstance(tickers, str):
        tickers = [tickers]

    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=False)

        # Проверим, есть ли нужная колонка
        if "Adj Close" not in data.columns.levels[0] and len(tickers) > 1:
            raise ValueError("Нет колонки 'Adj Close'. Возможно, auto_adjust=True.")

        # Получаем скорректированные цены
        if len(tickers) == 1:
            df = data["Adj Close"].to_frame(name=tickers[0])
        else:
            df = data["Adj Close"]

        df.dropna(how="all")
        return df

    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()



def calculate_returns(df_prices):
    returns = df_prices.pct_change().dropna()
    return returns



if __name__ == "__main__":
    df = load_price_data(["AAPL", "MSFT", "TSLA"])
    print(df.head())

    from charts import plot_prices, plot_returns
    plot_prices(df)

    returns = calculate_returns(df)
    print(returns.head())
    plot_returns(returns)

