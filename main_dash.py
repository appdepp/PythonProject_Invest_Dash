import dash
from dash import dcc, html
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Инициализация Dash-приложения
app = dash.Dash(__name__)


# Функции для получения данных и построения графиков (оставляем те же, что у вас)
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

    return fig


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

    return fig


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

    return fig


# Веб-страница Dash
app.layout = html.Div([
    html.H1("Анализ активов"),

    # Поля для выбора дат
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date='2020-01-01',
        end_date='2023-12-31',
        display_format='YYYY-MM-DD',
        style={'padding': '10px'}
    ),

    # Мультивыбор тикеров
    dcc.Checklist(
        id='tickers-checklist',
        options=[
            {'label': 'AAPL', 'value': 'AAPL'},
            {'label': 'MSFT', 'value': 'MSFT'},
            {'label': 'TSLA', 'value': 'TSLA'},
            {'label': 'GOOGL', 'value': 'GOOGL'},
            {'label': 'AMZN', 'value': 'AMZN'},
            {'label': 'NFLX', 'value': 'NFLX'},
            {'label': 'QQQ', 'value': 'QQQ'},
            {'label': 'SPY', 'value': 'SPY'},
            {'label': 'BTC-USD', 'value': 'BTC-USD'},
            {'label': 'ETH-USD', 'value': 'ETH-USD'},
            {'label': 'FB', 'value': 'FB'},
            {'label': 'NVDA', 'value': 'NVDA'},
            {'label': '^GSPC', 'value': '^GSPC'},
            {'label': '^DJI', 'value': '^DJI'},
            {'label': '^NDX', 'value': '^NDX'},
            {'label': '^RUT', 'value': '^RUT'},
            {'label': '^VIX', 'value': '^VIX'}
        ],
        value=['AAPL', 'MSFT'],  # по умолчанию
        style={'padding': '10px'}
    ),

    # Графики
    dcc.Graph(id='price-changes-graph'),
    dcc.Graph(id='returns-graph'),
    dcc.Graph(id='correlation-graph')
])


# Обновление графиков на основе введенных данных
@app.callback(
    [dash.dependencies.Output('price-changes-graph', 'figure'),
     dash.dependencies.Output('returns-graph', 'figure'),
     dash.dependencies.Output('correlation-graph', 'figure')],
    [dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('tickers-checklist', 'value')]
)
def update_graphs(start_date, end_date, selected_tickers):
    if not selected_tickers:
        selected_tickers = ['AAPL']  # По умолчанию, если ничего не выбрано

    # Загрузка данных
    df = load_data(selected_tickers, start_date, end_date)

    if df.empty:
        return go.Figure(), go.Figure(), go.Figure()  # Если данных нет, вернем пустые графики

    # Построение графиков
    price_changes_fig = plot_price_changes(df)
    returns_fig = plot_returns(df)
    correlation_fig = plot_correlation(df)

    return price_changes_fig, returns_fig, correlation_fig


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)