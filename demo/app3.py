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
print("current directory",os.getcwd())


# Streamlit Page Configuration
st.set_page_config(page_title="Portfolio Allocation Over Time", layout="wide")

# 🔹 Google Sheets API 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/hyeongjeongyi/demo/stock_demo/credentials/deep_chronos_google_api.json", scope)
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
        return pd.DataFrame()  # 빈 데이터프레임 반환
        

marketdata = load_google_sheet("market")
marketdata["date"] = pd.to_datetime(marketdata["date"])
data=load_google_sheet("result")
data["date"] = pd.to_datetime(data["date"])
future_prices=load_google_sheet("market_past")
future_prices["date"] = pd.to_datetime(future_prices["date"])
current_date = datetime.today().date()

# Title
st.title("Portfolio Allocation Over Time (Stacked Bar Chart)")



col1, col2 = st.columns(2)
with col1:
    selected_models = st.selectbox("Select Model", data["model"].unique(), index=0)
    selected_market = st.selectbox("Select Market",data["market"].unique(), index=0)
with col2:
    start_date = st.date_input("Test Data: Start Date", value=pd.Timestamp("2024-01-26"))
    end_date = st.date_input("Test Data: End Date", value=pd.Timestamp.today())
    
selected_models=default=[data["model"].unique()[0:2]]
    

selected_data = data[
    (data["market"] == selected_market) & 
    (data["model"].isin(selected_models)) &  
    (data["date"] >= pd.to_datetime(start_date)) 
].copy()
max_end_date = selected_data[selected_data['date'] > pd.to_datetime(start_date + timedelta(days=60))]['date'].min()
filtered_data = data[
    (data["market"] == selected_market) & 
    (data["model"].isin(selected_models)) &  
    (data["date"] >= pd.to_datetime(start_date)) &
    (data["date"]<=pd.to_datetime(max_end_date))
].copy()

# Tabs for different views
tab1, tab2, tab3= st.tabs(["Stacked Bar Chart", "Ranked View","Market Preview"])
with tab1:

    # 원형 그래프 
    """
    TAB 1 원형그래프 -----------------
    """
    st.subheader(f"Recommended Portfolio Allocation on {selected_data.iloc[-1]["date"]}, model {selected_data.iloc[-1]["model"]}")
    # 첫 번째 행 데이터 가져오기
    last_row = selected_data.iloc[-1]
    top_5_portfolio = last_row["top_5_portfolio"].split(", ")  # 종목 이름
    portfolio_ratio = eval(last_row["portfolio_ratio"])       # 비율
    pie_fig = go.Figure(data=[go.Pie(
        labels=top_5_portfolio,
        values=portfolio_ratio,
        hoverinfo='label+percent',
        textinfo='label+value',
        marker=dict(
            line=dict(color='black', width=1)  # 테두리 추가
        )
    )])
    # Layout 설정
    pie_fig.update_layout(
        title=f"Hold this ratio for ( {last_row["pred_len"]} ) days",
        template="plotly_white",
        height=400
    )
    # Streamlit에 원형 그래프 표시
    st.plotly_chart(pie_fig, use_container_width=True)




    
    """
    TAB 1 선 그래프 -----------------
    """
    # 날짜 선택 UI 추가
    st.subheader("Highlight Specific Date")
    all_dates = sorted(selected_data['date'].dt.date.unique())  # 전체 데이터에서 유효한 날짜 리스트
    selected_date = st.selectbox("Select a date to highlight:", options=all_dates)
    # highlight_date를 선택된 날짜 또는 이전의 가장 가까운 날짜로 설정
    available_dates = filtered_data['date'].dt.date.unique()
    if selected_date in available_dates:
        highlight_date = selected_date
    else:
        highlight_date = max([d for d in available_dates if d <= selected_date], default=min(available_dates))
    # Plotting the graph using Plotly
    fig = go.Figure()
    for model in selected_models:
        model_data = filtered_data[filtered_data['model'] == model]
        # max_end_date까지 데이터 확장

        color = f"rgba({hash(model) % 255}, {(hash(model) // 255) % 255}, {(hash(model) // (255*255)) % 255}, 1)"

            # Add the line trace (this will be included in the legend)
        fig.add_trace(go.Scatter(
            x=model_data['date'],
            y=model_data['Final Portfolio Value'],
            mode='lines',
            name=model,
            line=dict(width=3, color=color),
            marker=dict(size=8, color=color),
            showlegend=True
        ))
        max_value = model_data['Final Portfolio Value'].max()
        min_value = model_data['Final Portfolio Value'].min()
        # Highlight selected or nearest previous date on the line graph
        if highlight_date in model_data['date'].dt.date.values:
            highlighted_value = model_data[model_data['date'].dt.date == highlight_date]['Final Portfolio Value'].values[0]
            # 빨간색 세로선 추가
            fig.add_shape(
                type="line",
                x0=highlight_date,  # 세로선의 시작 x축 값
                x1=highlight_date,  # 세로선의 끝 x축 값
                y0=min_value * 0.95,  # y축의 시작 값 (그래프의 최하단 값으로 설정)
                y1=max_value,
                line=dict(
                    color="red",
                    width=5,
                    dash='dashdot'
                ),
            )
    fig.update_layout(
        title="Predicted Final Portfolio Value by Model",
        xaxis_title="Date",
        yaxis_title="Final Portfolio Value",
        legend_title="Models",
        template="plotly_white",
    )
    st.plotly_chart(fig)

    


    """
    TAB 1 막대그래프 -----------------
    """
    all_dates = sorted(filtered_data["date"].unique())  
     # Add stacked bar charts below the main graph
    st.subheader("Test date results by model")
    for model in selected_models:
        model_data = filtered_data[filtered_data['model'] == model]
    
        stacked_bar_data = []
        for _, row in model_data.iterrows():
            if row['market'] not in selected_market:
                continue

            portfolio_ratios = eval(row['portfolio_ratio']) if isinstance(row['portfolio_ratio'], str) else []
            top_5_stocks = row['top_5_portfolio'].split(', ') if isinstance(row['top_5_portfolio'], str) else []
            if len(portfolio_ratios) == len(top_5_stocks):
                stacked_bar_data.append({
                    'date': row['date'],
                    'stocks': top_5_stocks,
                    'ratios': portfolio_ratios
                })

        if stacked_bar_data:
            fig = go.Figure()

            stacked_bar_df = pd.DataFrame(stacked_bar_data)
            # ✅ 모든 날짜를 포함하는 데이터프레임 생성
            full_dates_df = pd.DataFrame({"date": all_dates})
            stacked_bar_df = full_dates_df.merge(stacked_bar_df, on="date", how="left").fillna(0)  # 없는 값은 0으로 채움\


            # highlight_date를 선택된 날짜 또는 이전의 가장 가까운 날짜로 설정
            available_dates = [bar['date'].date() for bar in stacked_bar_data]
            if selected_date in available_dates:
                highlight_date = selected_date
            else:
                highlight_date = max([d for d in available_dates if d <= selected_date], default=min(available_dates))

            for bar_data in stacked_bar_data:
                # 각 stock의 색상 설정
                stock_colors = px.colors.qualitative.Plotly[:len(bar_data['stocks'])]
                for i, stock in enumerate(bar_data['stocks']):
                    # highlight_date와 일치하는 날짜는 원래 색상, 나머지는 투명하게 처리
                    if bar_data['date'].date() == highlight_date:
                        opacity = 1.0  # 강조된 날짜는 불투명
                    else:
                        opacity = 0.2  # 나머지 날짜는 흐리게

                    fig.add_trace(go.Bar(
                        x=[bar_data['date']],
                        y=[bar_data['ratios'][i]],
                        name=stock,
                        marker=dict(color=stock_colors[i], opacity=opacity),
                        hoverinfo='text',
                        text=stock
                    ))

            fig.update_layout(
                barmode='stack',
                title=f"Stacked Portfolio Ratios for {model}",
                xaxis_title="Date",
                yaxis_title="Portfolio Ratio",
                template="plotly_white",
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )

            st.subheader(f"{model}")
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    # ✅ 최신 날짜 데이터만 사용하도록 수정
    last_row = selected_data.iloc[-1]
    st.header(f"Detailed Recommendation of Portfolio Investment at {last_row["date"]}, model {last_row["model"]}")

    # ✅ 최신 날짜의 상위 5개 포트폴리오 데이터 가져오기
    top_5_portfolio = last_row["top_5_portfolio"].split(", ")  # 종목 이름
    portfolio_ratio = eval(last_row["portfolio_ratio"])  # 비율

    # ✅ portfolio_ratio와 top_5_portfolio로 새로운 리스트 생성
    portfolio_allocation_summary = [
        {"Stock": stock, "Contribution": ratio} for stock, ratio in zip(top_5_portfolio, portfolio_ratio)
    ]

    # ✅ DataFrame 생성 (최신 날짜 데이터 기반)
    allocation_summary_df = pd.DataFrame(portfolio_allocation_summary)

    # ✅ 기여도 계산 (최신 날짜 데이터 기반)
    total_contributions = allocation_summary_df.groupby("Stock")["Contribution"].sum().sort_values(ascending=False)

    # ✅ 최종 추천 테이블 생성
    rec_df = pd.DataFrame({
        "Stock": total_contributions.index,
        "Total Contribution": total_contributions.values
    })

    # ✅ 테이블 및 막대 그래프 출력
    st.write("Portfolio Contributions Recommendation by Total Value:")
    st.table(rec_df)

    st.bar_chart(total_contributions)



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
