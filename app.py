import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 🧠 Cache the data loading
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
        title='Normalized Price Changes',
        xaxis_title='Date',
        yaxis_title='Price Change',
        template='plotly_dark'
    )
    return fig

def plot_returns(df):
    returns = df.pct_change().dropna()
    fig = go.Figure()
    for column in returns.columns:
        fig.add_trace(go.Scatter(x=returns.index, y=returns[column], mode='lines', name=column))
    fig.update_layout(
        title='Asset Returns',
        xaxis_title='Date',
        yaxis_title='Return',
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
        title='Cumulative Returns',
        xaxis_title='Date',
        yaxis_title='Cumulative Return',
        template='plotly_dark'
    )
    return fig

def plot_correlation(df):
    returns = df.pct_change().dropna()
    correlation_matrix = returns.corr()
    fig = px.imshow(
        correlation_matrix,
        labels=dict(x="Assets", y="Assets", color="Correlation"),
        color_continuous_scale='RdBu_r',
        title="Asset Correlation Matrix"
    )
    fig.update_layout(template='plotly_dark')
    return fig

def plot_moving_average(df, ma_type='SMA', window=10):
    fig = go.Figure()
    for column in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))
        if ma_type == 'SMA':
            ma = df[column].rolling(window=window).mean()
        else:
            ma = df[column].ewm(span=window, adjust=False).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma, mode='lines', name=f"{column} {ma_type} {window}"))
    fig.update_layout(
        title=f"{ma_type} - Moving Average",
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'
    )
    return fig

def plot_volatility(df, window=10):
    volatility = df.pct_change().rolling(window).std()
    fig = go.Figure()
    for column in volatility.columns:
        fig.add_trace(go.Scatter(x=volatility.index, y=volatility[column], mode='lines', name=f"{column} Volatility"))
    fig.update_layout(
        title=f"{window}-Day Rolling Volatility",
        xaxis_title='Date',
        yaxis_title='Volatility',
        template='plotly_dark'
    )
    return fig

# 👉 Streamlit UI
st.title("📊 Asset Analysis Dashboard")

# Initialize tickers list in session_state
if "tickers_list" not in st.session_state:
    st.session_state.tickers_list = [
        'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NFLX', 'QQQ', 'SPY',
        'BTC-USD', 'ETH-USD', 'META', 'NVDA', '^GSPC', '^DJI', '^NDX', '^RUT', '^VIX',
        'BA', 'DIS', 'NVDA', 'GS', 'INTC', 'IBM', 'SNAP', 'TWTR', 'SPY', 'IWM', 'SPX',
        'XOM', 'TSM', 'PYPL', 'NFLX', 'UBER', 'SQ', 'BABA', 'TWLO', 'MS', 'GS', 'BIDU'
    ]

with st.sidebar:
    st.header("Settings")
    start_date = st.date_input("Start Date", pd.to_datetime("2024-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime("2025-01-01"))

    if start_date >= end_date:
        st.error("❗ Start date must be before end date.")
        st.stop()

    selected_tickers = st.multiselect("Select Assets", st.session_state.tickers_list, default=["AAPL", "MSFT"])
    new_ticker = st.text_input("Add a Custom Ticker", "")

    if st.button("Add Ticker"):
        new_ticker = new_ticker.strip().upper()
        if new_ticker and new_ticker not in st.session_state.tickers_list:
            st.session_state.tickers_list.append(new_ticker)
            st.success(f"✅ Ticker {new_ticker} added.")
        elif new_ticker in st.session_state.tickers_list:
            st.warning(f"⚠️ Ticker {new_ticker} already exists.")
        else:
            st.warning("Please enter a ticker before adding.")

    if len(selected_tickers) == 1:
        selected_tickers = selected_tickers[0]

    if st.button("🔄 Run Analysis"):
        st.session_state["run_analysis"] = True

# 🧮 Main Logic
if "run_analysis" in st.session_state and st.session_state["run_analysis"]:
    df = load_data(selected_tickers, start_date, end_date)

    if isinstance(df, pd.Series):
        df = df.to_frame()

    st.write("📦 Loaded Data:", df.head())

    if df.empty or df.dropna().empty:
        st.warning("No data to display. Check selected assets or dates.")
    else:
        st.plotly_chart(plot_price_changes(df), use_container_width=True)
        st.plotly_chart(plot_returns(df), use_container_width=True)
        st.plotly_chart(plot_cumulative_returns(df), use_container_width=True)
        st.plotly_chart(plot_correlation(df), use_container_width=True)

        # ✅ NEW: Moving Average
        st.subheader("📈 Moving Average")
        ma_type = st.selectbox("Type", ["SMA", "EMA"])
        ma_window = st.slider("Window", min_value=5, max_value=60, value=20)
        st.plotly_chart(plot_moving_average(df, ma_type, ma_window), use_container_width=True)

        # ✅ NEW: Volatility Plot
        st.subheader("🔢 Volatility (Standard Deviation)")
        vol_window = st.slider("Volatility Window", 5, 60, 14)
        st.plotly_chart(plot_volatility(df, vol_window), use_container_width=True)

        # ✅ NEW: Daily Returns Table
        st.subheader("📋 Daily Returns")
        daily_returns = df.pct_change().dropna().round(4)
        st.dataframe(daily_returns)

        # # ✅ NEW: Bar Chart of Last Day Returns
        # st.subheader("📊 Last Day Returns")
        # if not daily_returns.empty and len(daily_returns) > 0:
        #     last_day = daily_returns.iloc[-1]
        #     last_day_df = pd.DataFrame(last_day).T
        #     last_day_df.index = [last_day_df.index[0].strftime('%Y-%m-%d')]
        #     st.bar_chart(last_day)
        #     st.write("Last day returns:", last_day_df)
        # else:
        #     st.warning("Not enough data to display last day returns.")

        # Summary Statistics
        st.subheader("📌 Summary Statistics")
        describe_df = df.describe().round(2)
        st.dataframe(describe_df)

        # ✅ NEW: Download Summary CSV
        st.subheader("📥 Export Data")
        csv = df.to_csv(index=True).encode("utf-8")
        st.download_button("📥 Download Raw Prices CSV", data=csv, file_name="asset_data.csv", mime="text/csv")

        stats_csv = describe_df.to_csv(index=True).encode("utf-8")
        st.download_button("📊 Download Summary Stats CSV", data=stats_csv, file_name="summary_statistics.csv", mime="text/csv")