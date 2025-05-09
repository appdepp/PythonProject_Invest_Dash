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

# Инициализация session_state для тикеров
if "tickers_list" not in st.session_state:
    st.session_state.tickers_list = [
        'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY',
        'BTC-USD', 'ETH-USD', 'META', 'NVDA', '^GSPC', '^DJI', '^NDX', '^RUT', '^VIX',
        'BA', 'DIS', 'NVDA', 'GS', 'INTC', 'IBM', 'SNAP', 'TWTR', 'SPY', 'IWM', 'SPX',
        'XOM', 'TSM', 'PYPL', 'NFLX', 'UBER', 'SQ', 'BABA', 'TWLO', 'MS', 'GS', 'BIDU'
    ]

with st.sidebar:
    st.header("Параметры")
    start_date = st.date_input("Дата начала", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("Дата конца", pd.to_datetime("2023-12-31"))

    if start_date >= end_date:
        st.error("❗ Дата начала должна быть раньше даты конца.")
        st.stop()

    selected_tickers = st.multiselect(
        "Выберите активы", st.session_state.tickers_list, default=["AAPL", "MSFT"]
    )

    new_ticker = st.text_input("Добавьте свой тикер", "")

    if st.button("Добавить тикер"):
        new_ticker = new_ticker.strip().upper()
        if new_ticker and new_ticker not in st.session_state.tickers_list:
            st.session_state.tickers_list.append(new_ticker)
            st.success(f"✅ Тикер {new_ticker} добавлен в список.")
        elif new_ticker in st.session_state.tickers_list:
            st.warning(f"⚠️ Тикер {new_ticker} уже есть в списке.")
        else:
            st.warning("Введите тикер перед добавлением.")

    if len(selected_tickers) == 1:
        selected_tickers = selected_tickers[0]

    if st.button("🔄 Обновить данные"):
        st.session_state["run_analysis"] = True

# 🧮 Основная логика
if "run_analysis" in st.session_state and st.session_state["run_analysis"]:
    df = load_data(selected_tickers, start_date, end_date)

    if isinstance(df, pd.Series):
        df = df.to_frame()

    st.write("📦 Загруженные данные:", df.head())

    if df.empty or df.dropna().empty:
        st.warning("Нет данных для отображения. Проверьте выбранные активы или даты.")
    else:
        st.plotly_chart(plot_price_changes(df), use_container_width=True)
        st.plotly_chart(plot_returns(df), use_container_width=True)
        st.plotly_chart(plot_cumulative_returns(df), use_container_width=True)
        st.plotly_chart(plot_correlation(df), use_container_width=True)

        st.subheader("📌 Сводная статистика (describe)")
        describe_df = df.describe().round(2)
        st.dataframe(describe_df)

        csv = df.to_csv(index=True).encode("utf-8")
        st.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name="asset_data.csv",
            mime="text/csv"
        )