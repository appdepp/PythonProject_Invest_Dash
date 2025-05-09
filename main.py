import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def load_data(tickers, start_date, end_date, use_adjusted=True):
    """
    Загружает данные по тикерам за указанный период.
    :param tickers: список тикеров
    :param start_date: начальная дата
    :param end_date: конечная дата
    :param use_adjusted: использовать скорректированные цены
    :return: DataFrame с ценами
    """
    col = "Adj Close" if not use_adjusted else "Close"
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=use_adjusted)
        if isinstance(data.columns, pd.MultiIndex):
            df = data[col]
        else:
            df = data[[col]].rename(columns={col: tickers[0]})
        return df.dropna(how='all')
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()


def plot_prices(df, title="Цены акций"):
    """ Строит график цен """
    df.plot()
    plt.title(title)
    plt.xlabel('Дата')
    plt.ylabel('Цена (USD)')
    plt.grid(True)
    plt.legend(df.columns)
    plt.tight_layout()
    plt.show()


def plot_returns(df, title="Доходности акций"):
    """ Строит график доходности """
    returns = df.pct_change().dropna()
    returns.plot()
    plt.title(title)
    plt.xlabel('Дата')
    plt.ylabel('Доходность (в долях)')
    plt.grid(True)
    plt.legend(returns.columns)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'TSLA']
    start_date = '2023-01-01'
    end_date = '2024-12-31'

    df_prices = load_data(tickers, start_date, end_date, use_adjusted=True)

    if df_prices.empty:
        print("Данные не загружены.")
        exit()

    plot_prices(df_prices)
    plot_returns(df_prices)