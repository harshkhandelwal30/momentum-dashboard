import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

lookback_periods = {
    '1M': 30,
    '3M': 90,
    '6M': 180
}


# data = pd.read_csv("nifty50.csv")
# data = pd.read_csv("nifty200.csv")
data = pd.read_csv("nifty500.csv")
nifty_50_tickers = data.iloc[:, 0].tolist()


end_date = datetime.today()
start_date = end_date - timedelta(days=max(lookback_periods.values()))

print(f"Fetching data from {start_date.date()} to {end_date.date()}...")
price_data = yf.download(
    tickers=" ".join(nifty_50_tickers),
    start=start_date,
    end=end_date,
    group_by='ticker',
    auto_adjust=True
)

adj_close_data = pd.DataFrame()
for ticker in nifty_50_tickers:
    try:
        adj_close_data[ticker] = price_data[ticker]["Close"]
    except Exception as e:
        print(f"Could not fetch data for {ticker}: {e}")

valid_stocks = adj_close_data.dropna(axis=1)

#calculating scores and returns
all_scores = pd.DataFrame(index=valid_stocks.columns)

for label, days in lookback_periods.items():
    subset = valid_stocks[-days:]
    returns = (subset.iloc[-1] - subset.iloc[0]) / subset.iloc[0] * 100
    percentile_scores = np.ceil(returns.rank(pct=True) * 100).astype(int)
    all_scores[f"{label} Return (%)"] = returns
    all_scores[f"{label} Score"] = percentile_scores

# stocks with scores > 90 in all periods
high_momentum = all_scores[
    (all_scores['1M Score'] > 90) & 
    (all_scores['3M Score'] > 90) & 
    (all_scores['6M Score'] > 90)
]

#final tables
print("\nAll Momentum Scores (1M, 3M, 6M):")
print(all_scores)

print("\nHigh Momentum Stocks (Score > 90 in all periods):")
print(high_momentum)
