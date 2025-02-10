# DeepOverseer Demo

## Prerequisite
```bash
pip install streamlit yfinance matplotlib plotly

```

## run
```bash
streamlit run app.py  --server.port 8501 --server.address 0.0.0.0
```

* db fetch
```bash
(base) [ec2-user@ip-172-31-23-97 stock_demo]$ python fetch_stock_data.py 
{'idprice': 1, 'date': datetime.date(2023, 12, 1), 'ticker': 'YAHOO', 'start_price': 10.0, 'end_price': 20.0}
{'idprice': 2, 'date': datetime.date(2024, 1, 23), 'ticker': 'MS', 'start_price': 40.0, 'end_price': 50.0}
```

