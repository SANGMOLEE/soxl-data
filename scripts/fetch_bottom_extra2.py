# -*- coding: utf-8 -*-
"""저점 탐지 조사 공백 보완용 2차 자료 수집 (GitHub Actions 에서 실행, data/crypto/extra2/ 에 저장).
항목별로 독립. 실패는 _fetch_log.txt 에 남기고 다음 항목으로 넘어간다.
  1) 빗썸·업비트 BTC/KRW 일봉 (김치프리미엄·원화 거래대금 계산용)   → BTC_KRW_BITHUMB_1D.csv, BTC_KRW_UPBIT_1D.csv
  2) CBBI 종합 지수와 구성 지표 이력                                → CBBI.csv
  3) 스테이블코인 총공급 (DefiLlama)                               → STABLECOINS.csv
  4) Binance 선물 미결제약정·롱숏 비율 일별 (2021-12~)              → BINANCE_OI_1D.csv
  5) Bitfinex 마진 롱·숏 잔고                                      → BITFINEX_MARGIN.csv
  6) 예측 시장(폴리마켓·칼시) 비트코인 계약 현재가                    → POLYMARKET_BTC.csv, KALSHI_BTC.csv
  7) BGeometrics 무료 온체인 API (단기·장기 보유자 원가, SOPR, 손익 물량 등) → BG_*.csv
  8) Yahoo: MSTR, 원/달러, 달러지수, 나스닥, 금, ETH                 → Y_*.csv
  9) FRED: 10년물, 기준금리 상단, 달러지수                           → FRED_*.csv
 10) Farside 현물 ETF 일별 순유입                                   → ETF_FLOWS_FARSIDE.csv
"""
import os, io, sys, time, json, zipfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto", "extra2")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept": "application/json,text/html,*/*"}
S = requests.Session(); S.headers.update(UA)
LOG = []
def log(m): print(m, flush=True); LOG.append(m)
def get(url, params=None, tries=3, timeout=60, ok404=False):
    last = None
    for k in range(tries):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 200: return r
            last = f"HTTP {r.status_code}"
            if r.status_code in (400, 401, 403, 404, 451): break
            if r.status_code == 429: time.sleep(20)
        except Exception as e: last = repr(e)
        time.sleep(2 + 3 * k)
    raise RuntimeError(f"{url} -> {last}")
def save(df, name): df.to_csv(os.path.join(OUT, name), index=False)

def bithumb():
    j = get("https://api.bithumb.com/public/candlestick/BTC_KRW/24h").json()["data"]
    d = pd.DataFrame(j, columns=["t", "open", "close", "high", "low", "volume"]); d["date"] = pd.to_datetime(d.t.astype("int64"), unit="ms").dt.normalize()
    d = d[["date", "open", "high", "low", "close", "volume"]].drop_duplicates("date").sort_values("date"); save(d, "BTC_KRW_BITHUMB_1D.csv")
    log(f"[OK] bithumb: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

def upbit():
    rows = []; to = None
    for _ in range(40):
        p = dict(market="KRW-BTC", count=200)
        if to: p["to"] = to
        j = get("https://api.upbit.com/v1/candles/days", p).json()
        if not j: break
        rows += j; to = j[-1]["candle_date_time_utc"].replace("T", " "); time.sleep(0.25)
        if len(j) < 200: break
    d = pd.DataFrame(rows); d["date"] = pd.to_datetime(d["candle_date_time_utc"]).dt.normalize()
    d = d.rename(columns={"opening_price": "open", "high_price": "high", "low_price": "low", "trade_price": "close", "candle_acc_trade_volume": "volume", "candle_acc_trade_price": "krw_volume"})
    d = d[["date", "open", "high", "low", "close", "volume", "krw_volume"]].drop_duplicates("date").sort_values("date"); save(d, "BTC_KRW_UPBIT_1D.csv")
    log(f"[OK] upbit: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

def cbbi():
    j = get("https://colintalkscrypto.com/cbbi/data/latest.json").json()
    d = pd.DataFrame({k: pd.Series(v) for k, v in j.items()}); d.index = pd.to_datetime(d.index.astype("int64"), unit="s"); d.index.name = "date"
    d = d.sort_index().reset_index(); save(d, "CBBI.csv"); log(f"[OK] cbbi: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()} cols={list(d.columns)[1:]}")

def stables():
    j = get("https://stablecoins.llama.fi/stablecoincharts/all").json()
    d = pd.DataFrame([{"date": pd.to_datetime(int(x["date"]), unit="s"), "usd": x.get("totalCirculatingUSD", {}).get("peggedUSD")} for x in j]).dropna()
    save(d, "STABLECOINS.csv"); log(f"[OK] stablecoins: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

def binance_oi():
    days = pd.date_range("2021-12-01", pd.Timestamp.utcnow().tz_localize(None).normalize())
    def one(day):
        u = f"https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-{day:%Y-%m-%d}.zip"
        try:
            r = S.get(u, timeout=40)
            if r.status_code != 200: return None
            z = zipfile.ZipFile(io.BytesIO(r.content)); x = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
            last = x.iloc[-1]
            return dict(date=day, oi_btc=last.get("sum_open_interest"), oi_usd=last.get("sum_open_interest_value"), oi_btc_max=x["sum_open_interest"].max(), oi_btc_min=x["sum_open_interest"].min(),
                        ls_ratio=last.get("count_long_short_ratio"), top_ls_ratio=last.get("sum_toptrader_long_short_ratio"), taker_ls=last.get("sum_taker_long_short_vol_ratio"))
        except Exception: return None
    with ThreadPoolExecutor(8) as ex: res = [r for r in ex.map(one, days) if r]
    d = pd.DataFrame(res).sort_values("date"); save(d, "BINANCE_OI_1D.csv"); log(f"[OK] binance_oi: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()} (requested {len(days)})")

def bitfinex():
    out = None
    for side in ("long", "short"):
        j = get(f"https://api-pub.bitfinex.com/v2/stats1/pos.size:1D:tBTCUSD:{side}/hist", dict(limit=10000)).json()
        s = pd.DataFrame(j, columns=["t", side]); s["date"] = pd.to_datetime(s.t, unit="ms").dt.normalize(); s = s[["date", side]].drop_duplicates("date")
        out = s if out is None else out.merge(s, on="date", how="outer"); time.sleep(1)
    out = out.sort_values("date"); save(out, "BITFINEX_MARGIN.csv"); log(f"[OK] bitfinex margin: {len(out)} rows {out.date.min().date()} ~ {out.date.max().date()}")

def polymarket():
    rows = []
    for off in range(0, 6000, 500):
        try: j = get("https://gamma-api.polymarket.com/markets", dict(closed="false", limit=500, offset=off), tries=2).json()
        except Exception as e: log(f"[..] polymarket page {off}: {e}"); break
        if not j: break
        for m in j:
            q = (m.get("question") or "")
            if any(k in q.lower() for k in ("bitcoin", "btc")):
                rows.append(dict(question=q, outcomes=m.get("outcomes"), prices=m.get("outcomePrices"), end=m.get("endDate"), volume=m.get("volume"), liquidity=m.get("liquidity"), slug=m.get("slug")))
        if len(j) < 500: break
        time.sleep(0.3)
    d = pd.DataFrame(rows); d["fetched_utc"] = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"); save(d, "POLYMARKET_BTC.csv"); log(f"[OK] polymarket: {len(d)} bitcoin markets")

def kalshi():
    rows = []; cur = None
    for _ in range(30):
        p = dict(limit=200, status="open", with_nested_markets="true")
        if cur: p["cursor"] = cur
        j = get("https://api.elections.kalshi.com/trade-api/v2/events", p, tries=2).json()
        for e in j.get("events", []):
            t = (e.get("title") or "") + " " + (e.get("series_ticker") or "")
            if any(k in t.lower() for k in ("bitcoin", "btc")):
                for m in e.get("markets", []) or []:
                    rows.append(dict(event=e.get("title"), market=m.get("title"), subtitle=m.get("subtitle") or m.get("yes_sub_title"), yes_bid=m.get("yes_bid"), yes_ask=m.get("yes_ask"), last=m.get("last_price"), close=m.get("close_time"), volume=m.get("volume"), ticker=m.get("ticker")))
        cur = j.get("cursor")
        if not cur: break
        time.sleep(0.3)
    d = pd.DataFrame(rows); d["fetched_utc"] = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"); save(d, "KALSHI_BTC.csv"); log(f"[OK] kalshi: {len(d)} bitcoin markets")

def bgeometrics():
    base = "https://bitcoin-data.com/v1/"
    names = ["sth-realized-price", "lth-realized-price", "realized-price", "mvrv-zscore", "sth-mvrv", "lth-mvrv", "nupl", "sopr", "sth-sopr", "lth-sopr", "supply-profit", "supply-loss",
             "puell-multiple", "reserve-risk", "true-market-mean", "active-investor-price", "cvdd", "balanced-price", "terminal-price", "delta-cap", "nrpl-usd", "realized-loss", "rhodl-ratio",
             "hashribbons", "etf-flow-btc", "etf-btc-total", "open-interest-futures", "funding-rate", "asopr", "vdd-multiple", "exchange-reserve-btc", "thermo-cap", "investor-cap", "nvts", "mvrv"]
    ok, bad = [], []
    for n in names:
        try:
            r = S.get(base + n, timeout=60)
            if r.status_code == 429:
                bad.append(n + ":429"); time.sleep(30); continue
            if r.status_code != 200: bad.append(f"{n}:{r.status_code}"); time.sleep(2); continue
            j = r.json(); d = pd.DataFrame(j if isinstance(j, list) else j.get("data", j))
            if len(d) < 50: bad.append(n + ":short"); continue
            save(d, "BG_" + n.replace("-", "_") + ".csv"); ok.append(f"{n}({len(d)})")
        except Exception as e: bad.append(f"{n}:{type(e).__name__}")
        time.sleep(4)
    log(f"[OK] bgeometrics ok={ok}"); log(f"[..] bgeometrics unavailable={bad}")

def yahoo():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from collect import fetch_yahoo
    for name, sym, start in (("MSTR", "MSTR", "2020-01-01"), ("USDKRW", "KRW=X", "2010-01-01"), ("DXY", "DX-Y.NYB", "2010-01-01"), ("NASDAQ", "^IXIC", "2010-01-01"), ("GOLD", "GC=F", "2010-01-01"), ("ETHUSD", "ETH-USD", "2017-01-01")):
        try:
            d = fetch_yahoo(sym, start); save(d, f"Y_{name}.csv"); log(f"[OK] yahoo {name}: {len(d)} rows ~ {d['date'].max().date()}")
        except Exception as e: log(f"[FAIL] yahoo {name}: {e!r}")
        time.sleep(1)

def fred():
    for sid in ("DGS10", "DFEDTARU", "DTWEXBGS"):
        try:
            r = get("https://fred.stlouisfed.org/graph/fredgraph.csv", dict(id=sid, cosd="2010-01-01")); d = pd.read_csv(io.StringIO(r.text)); d.columns = ["date", "value"]
            save(d, f"FRED_{sid}.csv"); log(f"[OK] fred {sid}: {len(d)} rows ~ {d.date.iloc[-1]}")
        except Exception as e: log(f"[FAIL] fred {sid}: {e!r}")

def farside():
    r = get("https://farside.co.uk/bitcoin-etf-flow-all-data/", tries=2); t = pd.read_html(io.StringIO(r.text))
    d = max(t, key=len); save(d, "ETF_FLOWS_FARSIDE.csv"); log(f"[OK] farside: {d.shape}")

JOBS = [("bithumb", bithumb), ("upbit", upbit), ("cbbi", cbbi), ("stables", stables), ("bitfinex", bitfinex), ("polymarket", polymarket), ("kalshi", kalshi),
        ("yahoo", yahoo), ("fred", fred), ("farside", farside), ("binance_oi", binance_oi), ("bgeometrics", bgeometrics)]
only = set(sys.argv[1:])
for name, fn in JOBS:
    if only and name not in only: continue
    try: fn()
    except Exception as e: log(f"[FAIL] {name}: {e!r}")
open(os.path.join(OUT, "_fetch_log.txt"), "w").write(f"run {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC\n" + "\n".join(LOG) + "\n")
