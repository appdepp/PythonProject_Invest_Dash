import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Для визуализации корреляции

def load_data(tickers, start_date, end_date):
    """Загружает скорректированные цены"""
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close']
    else:
        df = data.to_frame(name=tickers[0])

    return df.dropna(how='all')

def normalize_data(df):
    """Нормализует данные, чтобы все активы начинались с одинаковой цены"""
    return df / df.iloc[0]  # Делим на цену первого дня, чтобы все активы начинались с 1

def plot_price_changes(df):
    """График изменения цены с нормализацией"""
    normalized_df = normalize_data(df)  # Нормализуем данные
    price_changes = normalized_df.diff().dropna()  # Разница между соседними днями
    price_changes.plot(figsize=(14, 6))
    plt.title('Изменение цен активов (нормализовано)')
    plt.xlabel('Дата')
    plt.ylabel('Изменение цены (в относительных единицах)')
    plt.grid(True)
    plt.legend(price_changes.columns)
    plt.tight_layout()
    plt.show()

def plot_returns(df):
    """График доходностей"""
    returns = df.pct_change().dropna()  # Процентное изменение
    returns.plot(figsize=(14, 6))
    plt.title('Доходности активов')
    plt.xlabel('Дата')
    plt.ylabel('Доходность (в долях)')
    plt.grid(True)
    plt.legend(returns.columns)
    plt.tight_layout()
    plt.show()

def plot_correlation(df):
    """Визуализация корреляции между активами"""
    # Рассчитываем корреляцию доходностей
    returns = df.pct_change().dropna()  # Процентное изменение
    correlation_matrix = returns.corr()

    # Визуализируем корреляцию с помощью тепловой карты
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
    plt.title('Корреляция между активами')
    plt.tight_layout()
    plt.show()

def choose_tickers():
    """Выбор тикеров пользователем"""
    available_tickers = [
        'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY', 'BTC-USD', 'ETH-USD', 'FB', 'NVDA', '^GSPC', '^DJI', '^NDX', '^RUT', '^VIX'
    ]
    print("Доступные тикеры:")
    for idx, ticker in enumerate(available_tickers, 1):
        print(f"{idx}. {ticker}")

    selected_tickers = input("Введите номера тикеров через запятую (например: 1,2,5): ")
    selected_indices = [int(i) - 1 for i in selected_tickers.split(',')]

    # Возвращаем выбранные тикеры
    return [available_tickers[i] for i in selected_indices]

def main():
    # 🗓️ Ввод дат
    start_date = input("Введите дату начала (YYYY-MM-DD): ")
    end_date = input("Введите дату конца (YYYY-MM-DD): ")

    # 🏷️ Выбор тикеров
    user_tickers = choose_tickers()

    # Загрузка и построение
    df = load_data(user_tickers, start_date, end_date)

    if df.empty:
        print("❌ Данные не загружены.")
        return

    plot_price_changes(df)  # График изменения цены
    plot_returns(df)        # График доходности
    plot_correlation(df)    # График корреляции

if __name__ == "__main__":
    main()