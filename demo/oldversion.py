import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the data
file_path = "fakeresult.csv"
data = pd.read_csv(file_path)

# Convert date column to datetime format
data['date'] = pd.to_datetime(data['date'])

# Streamlit app
st.title("Final Portfolio Value Over Time")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Final Portfolio Value", "Recommendation", "Market Preview"])

with tab1:
    # Select ticker(s)
    tickers = data['ticker'].unique()
    selected_tickers = st.multiselect("Select Tickers:", tickers, default=tickers)

    # Filter data based on selected tickers
    filtered_data = data[data['ticker'].isin(selected_tickers)]

    # Plotting the graph using Plotly
    fig = go.Figure()

    for ticker in selected_tickers:
        ticker_data = filtered_data[filtered_data['ticker'] == ticker]
        color = f"rgba({hash(ticker) % 255}, {(hash(ticker) // 255) % 255}, {(hash(ticker) // (255*255)) % 255}, 1)"
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=ticker_data['Final Portfolio Value'],
            mode='lines',
            name=ticker,
            line=dict(width=2, color=color)
        ))

        # Highlight points where pred_len changes with hoverable bar chart
        pred_len_changes = ticker_data[ticker_data['pred_len'].diff() != 0]
        for _, row in pred_len_changes.iterrows():
            portfolio_ratios = row['portfolio_ratio']
            if isinstance(portfolio_ratios, str):
                try:
                    portfolio_ratios = eval(portfolio_ratios)
                except:
                    portfolio_ratios = []
            top_5_stocks = row['top_5_portfolio'].split(', ') if isinstance(row['top_5_portfolio'], str) else []
            if isinstance(portfolio_ratios, list) and len(portfolio_ratios) == len(top_5_stocks):
                bar_chart = go.Figure()
                bar_chart.add_trace(go.Bar(
                    x=top_5_stocks,
                    y=portfolio_ratios,
                    marker_color=['red', 'blue', 'green', 'orange', 'purple']
                ))
                bar_chart.update_layout(
                    title="Portfolio Ratios",
                    xaxis_title="Stock",
                    yaxis_title="Ratio",
                    template="plotly_white"
                )

                fig.add_trace(go.Scatter(
                    x=[row['date']],
                    y=[row['Final Portfolio Value']],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    hoverinfo='text',
                    hovertext=f"<b>{ticker}</b><br>Date: {row['date'].strftime('%Y-%m-%d')}<br>Portfolio Ratios:<br>" + "<br>".join([f"{stock}: {ratio}" for stock, ratio in zip(top_5_stocks, portfolio_ratios)])
                ))

    fig.update_layout(
        title="Final Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Final Portfolio Value",
        legend_title="Tickers",
        template="plotly_white"
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)

with tab2:
    st.header("Recommendation of Portfolio Contributions by End Date")

    # Summarize total contributions by stock
    portfolio_allocation_summary = []

    # Extract the top 5 portfolio ratios per row and aggregate contributions
    for _, row in data.iterrows():
        top_5_ratios = row["portfolio_ratio"]
        if isinstance(top_5_ratios, str):
            try:
                top_5_ratios = eval(top_5_ratios)
            except:
                continue
        top_5_stocks = row["top_5_portfolio"].split(", ") if isinstance(row["top_5_portfolio"], str) else []
        if len(top_5_ratios) == len(top_5_stocks):
            for stock, contribution in zip(top_5_stocks, top_5_ratios):
                portfolio_allocation_summary.append({"Stock": stock, "Contribution": contribution})

    # Convert to DataFrame
    allocation_summary_df = pd.DataFrame(portfolio_allocation_summary)

    # Aggregate total contributions per stock
    total_contributions = allocation_summary_df.groupby("Stock")["Contribution"].sum().sort_values(ascending=False)

    # Create a recommendation DataFrame
    rec_df = pd.DataFrame({
        "Stock": total_contributions.index,
        "Total Contribution": total_contributions.values
    })

    # Display Recommendation table
    st.write("Portfolio Contributions Recommendation by Total Value:")
    st.table(rec_df)

    # Bar chart for Recommendation contributions
    st.bar_chart(total_contributions)

with tab3:
    st.header("Market Dashboard")

    # Ensure the required columns exist
    if 'volume' in data.columns and 'close' in data.columns:
        marketdata = data[['ticker', 'volume', 'close']]
        marketdata = marketdata.groupby('ticker').agg({'volume': 'sum', 'close': 'mean'}).reset_index()

        # Format volume and price
        marketdata['volume'] = marketdata['volume'].apply(lambda x: f"{x / 1_000_000:.2f}M")
        marketdata['close'] = marketdata['close'].apply(lambda x: f"${x:.2f}")

        st.write("Market Summary")
        st.table(marketdata)
    else:
        st.write("The required columns for market data visualization are missing.")
