import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 🧠 Кеширование загрузки данных
@st.cache_data
def load_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close']
    else:
        # Если один тикер — делаем to_frame
        df = data.to_frame(name=tickers if isinstance(tickers, str) else tickers[0])

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

def plot_cumulative_returns(df):
    returns = df.pct_change().dropna()
    cumulative_returns = (1 + returns).cumprod()
    fig = go.Figure()
    for column in cumulative_returns.columns:
        fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[column], mode='lines', name=column))
    fig.update_layout(
        title='Накопленная доходность активов',
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

# 👉 Интерфейс Streamlit
st.title("📊 Анализ активов")

with st.sidebar:
    st.header("Параметры")
    start_date = st.date_input("Дата начала", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("Дата конца", pd.to_datetime("2023-12-31"))

    if start_date >= end_date:
        st.error("❗ Дата начала должна быть раньше даты конца.")
        st.stop()

    tickers_list = [
        'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY',
        'BTC-USD', 'ETH-USD', 'META', 'NVDA', '^GSPC', '^DJI', '^NDX', '^RUT', '^VIX',
        'BA', 'DIS', 'NVDA', 'GS', 'INTC', 'IBM', 'SNAP', 'TWTR', 'SPY', 'IWM', 'SPX',
        'XOM', 'TSM', 'PYPL', 'NFLX', 'UBER', 'SQ', 'BABA', 'TWLO', 'MS', 'GS', 'BIDU'
    ]
    selected_tickers = st.multiselect("Выберите активы", tickers_list, default=["AAPL", "MSFT"])

    # Обработка одного выбранного тикера
    if len(selected_tickers) == 1:
        selected_tickers = selected_tickers[0]

    if st.button("🔄 Обновить данные"):
        st.session_state["run_analysis"] = True

# 🧮 Основная логика
if "run_analysis" in st.session_state and st.session_state["run_analysis"]:
    df = load_data(selected_tickers, start_date, end_date)

    if isinstance(df, pd.Series):
        df = df.to_frame()

    # 👇 Отладка — показать первые строки (можно убрать потом)
    st.write("📦 Загруженные данные:", df.head())

    if df.empty or df.dropna().empty:
        st.warning("Нет данных для отображения. Проверьте выбранные активы или даты.")
    else:
        # Графики
        st.plotly_chart(plot_price_changes(df), use_container_width=True)
        st.plotly_chart(plot_returns(df), use_container_width=True)
        st.plotly_chart(plot_cumulative_returns(df), use_container_width=True)
        st.plotly_chart(plot_correlation(df), use_container_width=True)

        # Таблица describe
        st.subheader("📌 Сводная статистика (describe)")
        describe_df = df.describe().round(2)
        st.dataframe(describe_df)

        # Кнопка скачать
        csv = df.to_csv(index=True).encode("utf-8")
        st.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name="asset_data.csv",
            mime="text/csv"
        )