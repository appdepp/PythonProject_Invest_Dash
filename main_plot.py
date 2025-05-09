import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # Для визуализации корреляции


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

    # Создание интерактивного графика с plotly
    fig = go.Figure()

    for column in price_changes.columns:
        fig.add_trace(go.Scatter(
            x=price_changes.index,
            y=price_changes[column],
            mode='lines',
            name=column
        ))

    fig.update_layout(
        title='Изменение цен активов (нормализовано)',
        xaxis_title='Дата',
        yaxis_title='Изменение цены (в относительных единицах)',
        template='plotly_dark',
        autosize=True,
    )

    fig.show()


def plot_returns(df):
    """График доходностей"""
    returns = df.pct_change().dropna()  # Процентное изменение

    # Создание интерактивного графика с plotly
    fig = go.Figure()

    for column in returns.columns:
        fig.add_trace(go.Scatter(
            x=returns.index,
            y=returns[column],
            mode='lines',
            name=column
        ))

    fig.update_layout(
        title='Доходности активов',
        xaxis_title='Дата',
        yaxis_title='Доходность (в долях)',
        template='plotly_dark',
        autosize=True,
    )

    fig.show()


def plot_correlation(df):
    """Визуализация корреляции между активами"""
    # Рассчитываем корреляцию доходностей
    returns = df.pct_change().dropna()  # Процентное изменение
    correlation_matrix = returns.corr()

    # Визуализируем корреляцию с помощью plotly express (тепловая карта)
    fig = px.imshow(correlation_matrix,
                    labels=dict(x="Активы", y="Активы", color="Корреляция"),
                    color_continuous_scale='RdBu_r',
                    title="Корреляция между активами")

    fig.update_layout(
        template='plotly_dark',
        autosize=True,
    )

    fig.show()


def choose_tickers():
    """Выбор тикеров пользователем"""
    available_tickers = [
        'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY', 'BTC-USD', 'ETH-USD', 'FB', 'NVDA', '^GSPC',
        '^DJI', '^NDX', '^RUT', '^VIX'
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
    plot_returns(df)  # График доходности2024-12-31
    plot_correlation(df)  # График корреляции


if __name__ == "__main__":
    main()