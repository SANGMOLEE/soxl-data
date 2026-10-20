"""TIGER 200 IT (139260.KS) 일봉 전체 이력을 내려받아 data/manual/TIGER200IT.csv 로 저장.
GitHub Actions 에서 1회성으로 실행 (연구용). yfinance 우선, 실패 시 네이버 차트 API 폴백."""
import sys, io, json
import pandas as pd

OUT = "data/manual/TIGER200IT.csv"

def via_yfinance():
    import yfinance as yf
    d = yf.Ticker("139260.KS").history(period="max", auto_adjust=False)
    if d is None or d.empty:
        raise ValueError("yfinance 빈 응답")
    d = d.reset_index()
    d.columns = [str(c).lower().replace(" ", "_") for c in d.columns]
    d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")
    out = d[["date", "open", "high", "low", "close", "adj_close", "volume"]].copy()
    out["source"] = "yahoo"
    return out

def via_naver():
    import requests
    url = ("https://api.stock.naver.com/chart/domestic/item/139260/day"
           "?startDateTime=20100101&endDateTime=20991231")
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    rows = r.json()
    d = pd.DataFrame(rows)
    d = d.rename(columns={"localDate": "date", "openPrice": "open", "highPrice": "high",
                          "lowPrice": "low", "closePrice": "close", "accumulatedTradingVolume": "volume"})
    d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")
    d["adj_close"] = d["close"]
    out = d[["date", "open", "high", "low", "close", "adj_close", "volume"]].copy()
    out["source"] = "naver"
    return out

for fn in (via_yfinance, via_naver):
    try:
        out = fn()
        out = out.dropna(subset=["close"]).sort_values("date").drop_duplicates("date")
        out.to_csv(OUT, index=False)
        print(f"{fn.__name__}: {len(out)}행 {out.date.min()}~{out.date.max()} -> {OUT}")
        sys.exit(0)
    except Exception as e:
        print(f"{fn.__name__} 실패: {e!r}")
print("모든 출처 실패"); sys.exit(1)
