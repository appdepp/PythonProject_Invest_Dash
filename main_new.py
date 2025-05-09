import dash
from dash import dcc, html, Input, Output, State
import dash.dash_table
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Инициализация Dash-приложения
app = dash.Dash(__name__)
server = app.server  # для развертывания на платформе

# Функции
def load_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close']
    else:
        df = data.to_frame(name=tickers[0])
    return df.dropna(how='all')

def normalize_data(df):
    df_clean = df.dropna()
    if df_clean.empty:
        return df_clean
    return df_clean / df_clean.iloc[0]

def plot_price_changes(df):
    normalized_df = normalize_data(df)
    price_changes = normalized_df.diff().dropna()
    fig = go.Figure()
    for column in price_changes.columns:
        fig.add_trace(go.Scatter(x=price_changes.index, y=price_changes[column], mode='lines', name=column))
    fig.update_layout(
        title='Изменение цен активов (нормализовано)',
        xaxis_title='Дата',
        yaxis_title='Изменение цены',
        template='plotly_dark'
    )
    return fig

def plot_returns(df):
    returns = df.pct_change().dropna()
    fig = go.Figure()
    for column in returns.columns:
        fig.add_trace(go.Scatter(x=returns.index, y=returns[column], mode='lines', name=column))
    fig.update_layout(
        title='Доходности активов',
        xaxis_title='Дата',
        yaxis_title='Доходность',
        template='plotly_dark'
    )
    return fig

def plot_correlation(df):
    returns = df.pct_change().dropna()
    correlation_matrix = returns.corr()
    fig = px.imshow(
        correlation_matrix,
        labels=dict(x="Активы", y="Активы", color="Корреляция"),
        color_continuous_scale='RdBu_r',
        title="Корреляция между активами"
    )
    fig.update_layout(template='plotly_dark')
    return fig

# Лейаут
app.layout = html.Div([
    html.H1("Анализ активов"),

    dcc.DatePickerRange(
        id='date-picker-range',
        start_date='2020-01-01',
        end_date='2023-12-31',
        display_format='YYYY-MM-DD',
        style={'padding': '10px'}
    ),

    dcc.Checklist(
        id='tickers-checklist',
        options=[
            {'label': i, 'value': i} for i in [
                'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY',
                'BTC-USD', 'ETH-USD', 'FB', 'NVDA', '^GSPC', '^DJI', '^NDX', '^RUT', '^VIX'
            ]
        ],
        value=['AAPL', 'MSFT'],
        style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(5, 1fr)',  # 5 чекбоксов в ряд
            'gap': '10px',  # Расстояние между чекбоксами
            'padding': '10px'
        }
    ),

    html.Button("Обновить", id='update-button', n_clicks=0, style={'margin': '10px'}),
    html.Button("Скачать CSV", id="download-button", n_clicks=0, style={'margin': '10px'}),
    dcc.Download(id="download-data"),

    dcc.Loading(
        children=[
            dcc.Graph(id='price-changes-graph'),
            dcc.Graph(id='returns-graph'),
            dcc.Graph(id='correlation-graph')
        ],
        type='circle',
        color='#0071e3'
    ),

    html.Div([
        html.H3("Сводная статистика (describe)", style={'marginTop': '30px'}),
        dash.dash_table.DataTable(
            id='describe-table',
            columns=[],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'backgroundColor': '#f1f1f1', 'fontWeight': 'bold'}
        )
    ])
])

# ✅ Обновление графиков и таблицы только по кнопке "Обновить"
@app.callback(
    [
        Output('price-changes-graph', 'figure'),
        Output('returns-graph', 'figure'),
        Output('correlation-graph', 'figure'),
        Output('describe-table', 'data'),
        Output('describe-table', 'columns')
    ],
    Input('update-button', 'n_clicks'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('tickers-checklist', 'value')
)
def update_all(n_clicks, start_date, end_date, selected_tickers):
    if not selected_tickers:
        selected_tickers = ['AAPL']
    df = load_data(selected_tickers, start_date, end_date)

    if df.empty or df.dropna().empty:
        return go.Figure(), go.Figure(), go.Figure(), [], []

    price_changes_fig = plot_price_changes(df)
    returns_fig = plot_returns(df)
    correlation_fig = plot_correlation(df)

    describe_df = df.describe().reset_index().round(2)
    columns = [{"name": col, "id": col} for col in describe_df.columns]
    data = describe_df.to_dict('records')

    return price_changes_fig, returns_fig, correlation_fig, data, columns

# ✅ Скачивание CSV
@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date"),
    State("tickers-checklist", "value"),
    prevent_initial_call=True
)
def download_csv(n_clicks, start_date, end_date, selected_tickers):
    if not selected_tickers:
        selected_tickers = ['AAPL']

    df = load_data(selected_tickers, start_date, end_date)
    if df.empty:
        return dash.no_update

    csv_string = df.to_csv(index=True)
    return dict(content=csv_string, filename="asset_data.csv")

# Запуск
if __name__ == '__main__':
    app.run(debug=True)