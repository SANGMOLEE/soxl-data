# -*- coding: utf-8 -*-
"""비트코인 저점 이후 상승 시작 시점, 비트코인·솔라나(알트) 저점 간격 연구용 자료 수집 (GitHub Actions 실행, data/crypto/sol_study/).
  1) Coin Metrics 커뮤니티 일별 종가: 주요 알트 (긴 이력)                 → CM_PRICES.csv
  2) Binance 현물 일봉: BTC·ETH·SOL·주요 알트 USDT 쌍, SOLBTC·ETHBTC      → BINANCE_1D.csv.gz
  3) Binance 현물 30분봉: BTCUSDT (2017-08~), SOLUSDT (2020-08~), ETHUSDT → BINANCE_30M_{SYM}.csv.gz
  4) Bitstamp 30분봉: 2015-01, 2015-08 저점 전후                          → BITSTAMP_30M_2015.csv
  5) Binance 무기한 선물 펀딩비: SOLUSDT, ETHUSDT                          → FUNDING_{SYM}.csv
"""
import os, io, sys, time, zipfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto", "sol_study"); os.makedirs(OUT, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (research data fetch)"
LOG = []
def log(m): print(m, flush=True); LOG.append(m)
NOWM = pd.Timestamp.utcnow().tz_localize(None)
COLS = ["t", "open", "high", "low", "close", "volume", "ct", "quote_vol", "trades", "taker_buy_base", "taker_buy_quote", "ig"]

def zip_csv(url):
    try:
        r = S.get(url, timeout=60)
        if r.status_code != 200: return None
        z = zipfile.ZipFile(io.BytesIO(r.content)); raw = z.read(z.namelist()[0]).decode()
        d = pd.read_csv(io.StringIO(raw), header=None if raw[:1].isdigit() else 0); d = d.iloc[:, :12]; d.columns = COLS[:len(d.columns)]
        t = d["t"].astype("int64"); t = t.where(t < 10**14, t // 1000); d["date"] = pd.to_datetime(t, unit="ms")
        return d[["date", "open", "high", "low", "close", "volume", "quote_vol", "trades", "taker_buy_base"]]
    except Exception: return None

def klines(sym, itv, start):
    months = pd.date_range(start, NOWM, freq="MS"); urls = [f"https://data.binance.vision/data/spot/monthly/klines/{sym}/{itv}/{sym}-{itv}-{m:%Y-%m}.zip" for m in months]
    cur = pd.date_range(NOWM.replace(day=1).normalize(), NOWM.normalize(), freq="D")      # 이번 달은 월 파일이 없어 일 파일로 받는다
    urls += [f"https://data.binance.vision/data/spot/daily/klines/{sym}/{itv}/{sym}-{itv}-{d:%Y-%m-%d}.zip" for d in cur]
    with ThreadPoolExecutor(8) as ex: parts = [p for p in ex.map(zip_csv, urls) if p is not None]
    if not parts: return None
    return pd.concat(parts).drop_duplicates("date").sort_values("date")

def cm_prices():
    assets = "btc,eth,ltc,xrp,doge,ada,bnb,sol,link,avax,dot,trx,xlm,bch,etc,xmr,dash"
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"; params = dict(assets=assets, metrics="PriceUSD", frequency="1d", page_size=10000, start_time="2013-01-01", paging_from="start"); rows = []
    for _ in range(40):
        r = S.get(url, params=params, timeout=90); r.raise_for_status(); j = r.json(); rows += j.get("data", []); url = j.get("next_page_url"); params = None
        if not url: break
    d = pd.DataFrame(rows); d["date"] = pd.to_datetime(d["time"]).dt.tz_localize(None).dt.normalize(); d["PriceUSD"] = pd.to_numeric(d["PriceUSD"], errors="coerce")
    w = d.pivot_table(index="date", columns="asset", values="PriceUSD").sort_index(); w.to_csv(os.path.join(OUT, "CM_PRICES.csv"))
    log(f"[OK] cm_prices: {w.shape} {w.index[0].date()} ~ {w.index[-1].date()} first valid: " + ", ".join(f"{c}:{w[c].first_valid_index().date()}" for c in w.columns))

def binance_1d():
    syms = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "AVAXUSDT", "DOTUSDT", "TRXUSDT", "BCHUSDT", "SOLBTC", "ETHBTC"]; out = []
    for s in syms:
        d = klines(s, "1d", "2017-08-01")
        if d is None: log(f"[..] binance_1d {s}: none"); continue
        d.insert(0, "symbol", s); out.append(d); log(f"[OK] binance_1d {s}: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")
    pd.concat(out).to_csv(os.path.join(OUT, "BINANCE_1D.csv.gz"), index=False)

def binance_30m():
    for s, st in (("BTCUSDT", "2017-08-01"), ("SOLUSDT", "2020-08-01"), ("ETHUSDT", "2017-08-01")):
        d = klines(s, "30m", st)
        if d is None: log(f"[FAIL] binance_30m {s}"); continue
        d[["date", "open", "high", "low", "close", "volume", "taker_buy_base"]].to_csv(os.path.join(OUT, f"BINANCE_30M_{s}.csv.gz"), index=False); log(f"[OK] binance_30m {s}: {len(d)} rows {d.date.min()} ~ {d.date.max()}")

def bitstamp_30m():
    rows = []
    for a, b in (("2014-12-20", "2015-02-10"), ("2015-08-05", "2015-09-10")):
        ts = int(pd.Timestamp(a).timestamp()); end = int(pd.Timestamp(b).timestamp())
        while ts < end:
            j = S.get("https://www.bitstamp.net/api/v2/ohlc/btcusd/", params=dict(step=1800, limit=1000, start=ts), timeout=60).json()["data"]["ohlc"]
            if not j: break
            rows += j; ts = int(j[-1]["timestamp"]) + 1800; time.sleep(0.3)
    d = pd.DataFrame(rows).drop_duplicates("timestamp"); d["date"] = pd.to_datetime(d["timestamp"].astype(int), unit="s")
    d[["date", "open", "high", "low", "close", "volume"]].sort_values("date").to_csv(os.path.join(OUT, "BITSTAMP_30M_2015.csv"), index=False); log(f"[OK] bitstamp_30m: {len(d)} rows")

def funding():
    for s in ("SOLUSDT", "ETHUSDT"):
        parts = []
        for m in pd.date_range("2020-01-01", NOWM, freq="MS"):
            try:
                r = S.get(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m:%Y-%m}.zip", timeout=40)
                if r.status_code != 200: continue
                z = zipfile.ZipFile(io.BytesIO(r.content)); raw = z.read(z.namelist()[0]).decode(); x = pd.read_csv(io.StringIO(raw), header=None if raw[:1].isdigit() else 0); x = x.iloc[:, :3]; x.columns = ["t", "h", "rate"]; parts.append(x)
            except Exception: pass
        if not parts: log(f"[FAIL] funding {s}"); continue
        d = pd.concat(parts); d["date"] = pd.to_datetime(d["t"].astype("int64"), unit="ms").dt.floor("h"); d = d[["date", "rate"]].drop_duplicates("date").sort_values("date")
        d.to_csv(os.path.join(OUT, f"FUNDING_{s}.csv"), index=False); log(f"[OK] funding {s}: {len(d)} rows {d.date.min()} ~ {d.date.max()}")

for name, fn in (("cm_prices", cm_prices), ("binance_1d", binance_1d), ("bitstamp_30m", bitstamp_30m), ("funding", funding), ("binance_30m", binance_30m)):
    try: fn()
    except Exception as e: log(f"[FAIL] {name}: {e!r}")
open(os.path.join(OUT, "_fetch_log.txt"), "w").write(f"run {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC\n" + "\n".join(LOG) + "\n")
