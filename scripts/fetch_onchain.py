# -*- coding: utf-8 -*-
"""비트코인 온체인 일별 자료 수집 (Coin Metrics 커뮤니티 API, 키 불필요).
MVRV(시가총액÷실현시가총액), 시가총액, 가격 → data/crypto/BTC_ONCHAIN.csv
실현가격 = 가격 ÷ MVRV. 실패해도 기존 파일은 건드리지 않는다."""
import os, sys, requests, pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto", "BTC_ONCHAIN.csv")
URL = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
def fetch(metrics):
    rows = []; params = dict(assets="btc", metrics=metrics, frequency="1d", page_size=10000, start_time="2011-01-01", paging_from="start"); url = URL
    for _ in range(20):
        r = requests.get(url, params=params, timeout=60); r.raise_for_status(); j = r.json(); rows += j.get("data", [])
        url = j.get("next_page_url"); params = None
        if not url: break
    return rows
rows = None; err = []
for metrics in ("CapMVRVCur,CapMrktCurUSD,PriceUSD", "CapMVRVCur,PriceUSD"):
    try:
        rows = fetch(metrics)
        if rows: break
    except Exception as e: err.append(f"{metrics}: {e}")
if not rows: print("[FAIL] onchain:", err); sys.exit(1)
df = pd.DataFrame(rows); df["date"] = pd.to_datetime(df["time"]).dt.tz_localize(None).dt.normalize()
out = pd.DataFrame({"date": df["date"], "mvrv": pd.to_numeric(df["CapMVRVCur"], errors="coerce"), "price": pd.to_numeric(df["PriceUSD"], errors="coerce")})
out["mcap"] = pd.to_numeric(df["CapMrktCurUSD"], errors="coerce") if "CapMrktCurUSD" in df else float("nan")
out = out.dropna(subset=["mvrv", "price"]).sort_values("date").drop_duplicates("date"); out["realized_price"] = out["price"] / out["mvrv"]; out["source"] = "coinmetrics"
if len(out) < 3000: print("[FAIL] 행 수 부족", len(out)); sys.exit(1)
out.to_csv(OUT, index=False); print("[OK] onchain", len(out), out["date"].min().date(), out["date"].max().date(), out.tail(1).to_dict("records"))
