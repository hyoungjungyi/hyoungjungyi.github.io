import random
import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from matplotlib.dates import DateFormatter, date2num, num2date
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "deep_chronos_google_api.json")
print("current directory", os.getcwd())

# Streamlit Page Configuration
st.set_page_config(page_title="Portfolio Allocation Over Time", layout="wide")

# 🔹 Google Sheets API 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1bRkd6crVHwwZes4bGBT1CzxOVGBo9C38g9aOwiZM5mE/edit#gid=0"
spreadsheet = client.open_by_url(SPREADSHEET_URL)

def load_google_sheet(sheet_name):
    """ 구글 시트에서 데이터를 가져오는 함수 """
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load {sheet_name} from Google Sheets: {e}")
        return pd.DataFrame()

marketdata = load_google_sheet("market")
marketdata["date"] = pd.to_datetime(marketdata["date"])
data = load_google_sheet("result")
data["date"] = pd.to_datetime(data["date"])
future_prices = load_google_sheet("market_past")
future_prices["date"] = pd.to_datetime(future_prices["date"])
current_date = datetime.today().date()

# Title
st.title("Portfolio Allocation Over Time (Stacked Bar Chart)")

col1, col2 = st.columns(2)
with col1:
    selected_models = st.multiselect("Select Model", data["model"].unique(), default=[data["model"].unique()[0]])
    selected_market = st.selectbox("Select Market", data["market"].unique(), index=0)
with col2:
    start_date = st.date_input("Test Data: Start Date", value=pd.Timestamp("2024-01-26"))
    end_date = st.date_input("Test Data: End Date", value=pd.Timestamp.today())

# 모델별 데이터 저장
model_data_dict = {}
for model in selected_models:
    model_selected_data = data[
        (data["market"] == selected_market) &
        (data["model"] == model) &
        (data["date"] >= pd.to_datetime(start_date))
    ].copy()
    
    if model_selected_data.empty:
        continue
    
    max_end_date = model_selected_data[model_selected_data['date'] > pd.to_datetime(start_date + timedelta(days=60))]['date'].min()
    if pd.isna(max_end_date):
        max_end_date = data["date"].max()
    model_filtered_data = model_selected_data[
        (model_selected_data["date"] <= pd.to_datetime(max_end_date))
    ].copy()
    
    model_data_dict[model] = {
        "selected_data": model_selected_data,
        "filtered_data": model_filtered_data,
        "max_end_date": max_end_date
    }

# Tabs
tab1, tab2, tab3 = st.tabs(["Stacked Bar Chart", "Ranked View", "Market Preview"])

with tab1:
    for model in selected_models:
        selected_data = model_data_dict[model]["selected_data"]
        if selected_data.empty:
            continue
        
        last_row = selected_data.iloc[-1]
        st.subheader(f"Recommended Portfolio Allocation on {last_row['date']}, Model: {model}")
        
        
        top_5_portfolio = last_row["top_5_portfolio"].split(", ")
        portfolio_ratio = eval(last_row["portfolio_ratio"])
        pie_fig = go.Figure(data=[go.Pie(labels=top_5_portfolio, values=portfolio_ratio)])
        pie_fig.update_layout(
            title=f"Hold this ratio for ( {last_row["pred_len"]} ) days",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(pie_fig, use_container_width=True)
    
    fig = go.Figure()
    for model in selected_models:
        model_filtered_data = model_data_dict[model]["filtered_data"]
        if model_filtered_data.empty:
            continue
        
        fig.add_trace(go.Scatter(
            x=model_filtered_data['date'],
            y=model_filtered_data['Final Portfolio Value'],
            mode='lines',
            name=model
        ))
    st.plotly_chart(fig)

    # Stacked Bar Chart 추가
    st.subheader("Test date results by model")
    for model in selected_models:
        model_filtered_data = model_data_dict[model]["filtered_data"]
        if model_filtered_data.empty:
            continue
        
        stacked_bar_data = []
        for _, row in model_filtered_data.iterrows():
            portfolio_ratios = eval(row["portfolio_ratio"])
            top_5_stocks = row["top_5_portfolio"].split(", ")
            if len(portfolio_ratios) == len(top_5_stocks):
                stacked_bar_data.append({
                    "date": row["date"],
                    "stocks": top_5_stocks,
                    "ratios": portfolio_ratios
                })
        
        fig = go.Figure()
        for bar_data in stacked_bar_data:
            for i, stock in enumerate(bar_data["stocks"]):
                fig.add_trace(go.Bar(
                    x=[bar_data["date"]],
                    y=[bar_data["ratios"][i]],
                    name=stock
                ))
        
        fig.update_layout(
            barmode="stack",
            title=f"Stacked Portfolio Ratios for {model}",
            xaxis_title="Date",
            yaxis_title="Portfolio Ratio"
        )
        
        st.plotly_chart(fig, use_container_width=True)


with tab2:
    for model in selected_models:
        selected_data = model_data_dict[model]["selected_data"]
        if selected_data.empty:
            continue
        
        last_row = selected_data.iloc[-1]
        st.header(f"Detailed Recommendation of Portfolio Investment at {last_row['date']}, Model: {model}")
        
        top_5_portfolio = last_row["top_5_portfolio"].split(", ")
        portfolio_ratio = eval(last_row["portfolio_ratio"])
        allocation_summary_df = pd.DataFrame({"Stock": top_5_portfolio, "Contribution": portfolio_ratio})
        
        st.write("Portfolio Contributions Recommendation by Total Value:")
        st.table(allocation_summary_df)
        st.bar_chart(allocation_summary_df.set_index("Stock"))



with tab3:
    st.header("Market Dashboard")

    # ✅ 선택된 시장 데이터 필터링
    selected_future_data = future_prices[future_prices["market"] == selected_market].copy()

    # ✅ date 컬럼을 datetime 타입으로 변환 (날짜 비교 문제 방지)
    selected_future_data["date"] = pd.to_datetime(selected_future_data["date"])

    # ✅ 사용자가 분석할 티커 선택 (기본값: "GS"가 존재하는 경우만)
    available_tickers = selected_future_data["ticker"].unique()
    default_ticker = "GS" if "GS" in available_tickers else available_tickers[0]

    selected_tickers = st.multiselect(
        "Select Tickers for Future Price Analysis:", 
        available_tickers, 
        default=default_ticker
    )

    # ✅ 선택된 티커들만 개별적으로 플롯
    cols = st.columns(2)
    for i, ticker in enumerate(selected_tickers):
        ticker_prices = selected_future_data[selected_future_data["ticker"] == ticker].copy()

        # ✅ 중복 제거 및 정렬
        ticker_prices = ticker_prices.drop_duplicates().sort_values(by="date")

        # ✅ 과거 데이터만 선택
        past_prices = ticker_prices.copy()  # 미래 데이터 없이 전체 사용

        # ✅ 그래프 생성
        fig = go.Figure()

        # ✅ 과거 가격 데이터 (녹색 선)
        if not past_prices.empty:
            fig.add_trace(go.Scatter(
                x=past_prices["date"],
                y=past_prices["close"],
                mode='lines',
                name=f"Past Prices ({ticker})",
                line=dict(color='green')
            ))

        # ✅ 레이아웃 설정 (X축 시간 데이터 올바르게 표시)
        fig.update_layout(
            title=f"Price Analysis for {ticker}",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis=dict(type="date"),
            template="plotly_white",
            height=400
        )

        # ✅ Streamlit에 그래프 표시
        cols[i % 2].plotly_chart(fig, use_container_width=True)



    # Convert 'volume' to a readable format (e.g., millions or billions)
    def format_volume(volume):
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.2f}M"
        return f"{volume:,}"

    selected_market = st.selectbox("Select Market for ticker prices:", marketdata["market"].unique(), index=0)
    
    # marketdata의 시장명을 대문자로 변환 후 필터링
    marketdata["market"] = marketdata["market"].str.upper().str.strip()
    selected_market = selected_market.upper().strip()

    # 시장 필터링 적용
    filtered_marketdata = marketdata[marketdata["market"] == selected_market]

    # 데이터가 비었는지 확인
    if filtered_marketdata.empty:
        st.warning("No data available for the selected market.")
    else:
        # 테이블에 표시할 데이터 선택
        display_data = filtered_marketdata[["ticker", "open", "close", "high", "low", "adjclose", "volume", "zadjcp"]]
        display_data = display_data.rename(columns={
            "ticker": "Ticker",
            "open": "Open",
            "close": "Close",
            "high": "High",
            "low": "Low",
            "adjclose": "Adj Close",
            "volume": "Volume",
            "zadjcp": "Zadjcp"
        })
        # 인덱스를 1부터 시작하도록 설정
        display_data.index = range(1, len(display_data) + 1)
        
        # 테이블 출력
        st.table(display_data)
