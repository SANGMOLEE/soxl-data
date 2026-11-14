# -*- coding: utf-8 -*-
"""비트코인 저점 해부 연구용 추가 자료 일회성 수집 (GitHub Actions 에서 실행, data/crypto/extra/ 에 저장).
각 항목은 서로 독립이며 하나가 실패해도 나머지는 저장한다. 결과 요약은 _fetch_log.txt.
  1) Bitstamp 일봉·시간봉 (2011-08~)          → BTC_BITSTAMP_1D.csv, BTC_BITSTAMP_1H.csv.gz
  2) 공포탐욕지수 (alternative.me, 2018-02~)   → FNG.csv
  3) 무기한 선물 펀딩비 (Binance 공개 파일, BitMEX) → FUNDING_BINANCE.csv, FUNDING_BITMEX.csv
  4) Coin Metrics 커뮤니티 온체인 추가 지표     → BTC_ONCHAIN_EXTRA.csv
  5) Binance 현물 시간봉 (매수·매도 체결량 포함) → BTC_BINANCE_1H.csv.gz
  6) Deribit 내재변동성 지수 DVOL              → DVOL.csv
  7) Coinbase 일봉 (코인베이스 프리미엄 계산용)  → BTC_COINBASE_1D.csv
"""
import os, io, sys, time, zipfile, datetime as dt
import requests, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto", "extra")
os.makedirs(OUT, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (research data fetch)"
LOG = []
def log(msg): print(msg, flush=True); LOG.append(msg)
def get(url, params=None, tries=4, timeout=60):
    last = None
    for k in range(tries):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 200: return r
            last = f"HTTP {r.status_code}"
            if r.status_code in (400, 403, 404, 451): break
        except Exception as e: last = repr(e)
        time.sleep(2 + 3 * k)
    raise RuntimeError(f"{url} -> {last}")
NOW = int(time.time())

def bitstamp(step, name, start="2011-08-01", gz=False):
    ts = int(pd.Timestamp(start).timestamp()); rows = []
    while ts < NOW:
        j = get("https://www.bitstamp.net/api/v2/ohlc/btcusd/", dict(step=step, limit=1000, start=ts)).json()["data"]["ohlc"]
        if not j: ts += step * 1000; continue
        rows += j; last = int(j[-1]["timestamp"])
        ts = last + step if last >= ts else ts + step * 1000
        time.sleep(0.25)
    d = pd.DataFrame(rows).drop_duplicates("timestamp"); d["date"] = pd.to_datetime(d["timestamp"].astype(int), unit="s")
    d = d[["date", "open", "high", "low", "close", "volume"]].sort_values("date")
    d = d[pd.to_numeric(d["volume"]) > 0]
    p = os.path.join(OUT, name + (".csv.gz" if gz else ".csv")); d.to_csv(p, index=False)
    log(f"[OK] {name}: {len(d)} rows {d.date.min()} ~ {d.date.max()}")

def fng():
    j = get("https://api.alternative.me/fng/", dict(limit=0, format="json")).json()["data"]
    d = pd.DataFrame(j); d["date"] = pd.to_datetime(d["timestamp"].astype(int), unit="s")
    d = d[["date", "value", "value_classification"]].sort_values("date"); d.to_csv(os.path.join(OUT, "FNG.csv"), index=False)
    log(f"[OK] FNG: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

def months(start):
    m = pd.Timestamp(start); end = pd.Timestamp.utcnow().tz_localize(None)
    while m <= end: yield m.strftime("%Y-%m"); m += pd.offsets.MonthBegin(1)

def binance_zip(url):
    r = S.get(url, timeout=60)
    if r.status_code != 200: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); raw = z.read(z.namelist()[0]).decode()
    head = None if raw[:1].isdigit() else 0
    return pd.read_csv(io.StringIO(raw), header=head)

def funding_binance():
    parts = []; miss = 0
    for m in months("2019-09-01"):
        d = binance_zip(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{m}.zip")
        if d is None: miss += 1; continue
        d.columns = ["calc_time", "interval_h", "rate"][:len(d.columns)]; parts.append(d)
    try:  # 이번 달(월 파일 없음)과 초기 구간은 API 로 보충. 미국 IP 차단이면 건너뜀.
        st = 1567296000000; api = []
        for _ in range(40):
            j = get("https://fapi.binance.com/fapi/v1/fundingRate", dict(symbol="BTCUSDT", startTime=st, limit=1000), tries=2).json()
            if not j: break
            api += j; st = j[-1]["fundingTime"] + 1
            if len(j) < 1000: break
        if api:
            a = pd.DataFrame(api); parts.append(pd.DataFrame({"calc_time": a.fundingTime, "interval_h": 8, "rate": a.fundingRate.astype(float)}))
    except Exception as e: log(f"[..] binance funding API skipped: {e}")
    d = pd.concat(parts); d["date"] = pd.to_datetime(d["calc_time"].astype("int64"), unit="ms").dt.floor("h")
    d = d[["date", "rate"]].drop_duplicates("date").sort_values("date"); d.to_csv(os.path.join(OUT, "FUNDING_BINANCE.csv"), index=False)
    log(f"[OK] FUNDING_BINANCE: {len(d)} rows {d.date.min()} ~ {d.date.max()} (missing months {miss})")

def funding_bitmex():
    rows = []; start = 0
    for _ in range(60):
        j = get("https://www.bitmex.com/api/v1/funding", dict(symbol="XBTUSD", count=500, start=start, reverse="false")).json()
        if not j: break
        rows += j; start += len(j); time.sleep(1.2)
        if len(j) < 500: break
    d = pd.DataFrame(rows); d["date"] = pd.to_datetime(d["timestamp"]).dt.tz_localize(None)
    d = d[["date", "fundingRate"]].rename(columns={"fundingRate": "rate"}).sort_values("date"); d.to_csv(os.path.join(OUT, "FUNDING_BITMEX.csv"), index=False)
    log(f"[OK] FUNDING_BITMEX: {len(d)} rows {d.date.min()} ~ {d.date.max()}")

def coinmetrics():
    url0 = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    want = ["HashRate", "IssTotUSD", "RevUSD", "FeeTotUSD", "AdrActCnt", "TxCnt", "CapRealUSD", "CapMrktCurUSD", "SplyCur", "NVTAdj", "NVTAdj90",
            "VtyDayRet30d", "FlowInExUSD", "FlowOutExUSD", "FlowInExNtv", "FlowOutExNtv", "SplyExNtv", "TxTfrValAdjUSD", "SplyAct1yr", "CapMVRVFF",
            "SOPR", "SplyActPct1yr", "RevHashRateUSD", "DiffMean", "ROI30d", "ROI1yr"]
    out = None; ok = []; bad = []
    for m in want:
        try:
            rows = []; url = url0; params = dict(assets="btc", metrics=m, frequency="1d", page_size=10000, start_time="2010-07-01", paging_from="start")
            for _ in range(10):
                j = get(url, params, tries=2).json(); rows += j.get("data", []); url = j.get("next_page_url"); params = None
                if not url: break
            if not rows: raise RuntimeError("empty")
            d = pd.DataFrame(rows); d["date"] = pd.to_datetime(d["time"]).dt.tz_localize(None).dt.normalize()
            s = pd.to_numeric(d[m], errors="coerce"); s.index = d["date"]; s = s[~s.index.duplicated()]
            out = s.to_frame(m) if out is None else out.join(s.to_frame(m), how="outer"); ok.append(m)
        except Exception as e: bad.append(m)
        time.sleep(0.7)
    out.sort_index().to_csv(os.path.join(OUT, "BTC_ONCHAIN_EXTRA.csv"))
    log(f"[OK] BTC_ONCHAIN_EXTRA: {len(out)} rows, metrics ok={ok} unavailable={bad}")

def binance_1h():
    parts = []; miss = []
    for m in months("2017-08-01"):
        d = binance_zip(f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-{m}.zip")
        if d is None: miss.append(m); continue
        d = d.iloc[:, :11]; d.columns = ["t", "open", "high", "low", "close", "volume", "ct", "quote_vol", "trades", "taker_buy_base", "taker_buy_quote"]
        t = d["t"].astype("int64"); t = t.where(t < 10**14, t // 1000)   # 2025년부터 마이크로초
        d["date"] = pd.to_datetime(t, unit="ms"); parts.append(d[["date", "open", "high", "low", "close", "volume", "quote_vol", "trades", "taker_buy_base"]])
    d = pd.concat(parts).drop_duplicates("date").sort_values("date"); d.to_csv(os.path.join(OUT, "BTC_BINANCE_1H.csv.gz"), index=False)
    log(f"[OK] BTC_BINANCE_1H: {len(d)} rows {d.date.min()} ~ {d.date.max()} (missing {miss})")

def dvol():
    rows = []; end = NOW * 1000; start = int(pd.Timestamp("2021-03-01").timestamp() * 1000)
    for _ in range(30):
        j = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", dict(currency="BTC", start_timestamp=start, end_timestamp=end, resolution="1D")).json()["result"]
        rows += j["data"]
        if not j.get("continuation") or not j["data"]: break
        end = j["continuation"]
    d = pd.DataFrame(rows, columns=["t", "open", "high", "low", "close"]); d["date"] = pd.to_datetime(d.t, unit="ms")
    d = d[["date", "open", "high", "low", "close"]].drop_duplicates("date").sort_values("date"); d.to_csv(os.path.join(OUT, "DVOL.csv"), index=False)
    log(f"[OK] DVOL: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

def coinbase_1d():
    rows = []; s = pd.Timestamp("2015-01-01"); endall = pd.Timestamp.utcnow().tz_localize(None)
    while s < endall:
        e = s + pd.Timedelta(days=299)
        j = get("https://api.exchange.coinbase.com/products/BTC-USD/candles", dict(granularity=86400, start=s.isoformat(), end=e.isoformat())).json()
        rows += j; s = e + pd.Timedelta(days=1); time.sleep(0.4)
    d = pd.DataFrame(rows, columns=["t", "low", "high", "open", "close", "volume"]); d["date"] = pd.to_datetime(d.t, unit="s")
    d = d[["date", "open", "high", "low", "close", "volume"]].drop_duplicates("date").sort_values("date"); d.to_csv(os.path.join(OUT, "BTC_COINBASE_1D.csv"), index=False)
    log(f"[OK] BTC_COINBASE_1D: {len(d)} rows {d.date.min().date()} ~ {d.date.max().date()}")

JOBS = [("bitstamp_1d", lambda: bitstamp(86400, "BTC_BITSTAMP_1D")), ("fng", fng), ("coinmetrics", coinmetrics), ("funding_binance", funding_binance),
        ("funding_bitmex", funding_bitmex), ("dvol", dvol), ("coinbase_1d", coinbase_1d), ("binance_1h", binance_1h),
        ("bitstamp_1h", lambda: bitstamp(3600, "BTC_BITSTAMP_1H", gz=True))]
only = set(sys.argv[1:])
for name, fn in JOBS:
    if only and name not in only: continue
    try: fn()
    except Exception as e: log(f"[FAIL] {name}: {e!r}")
open(os.path.join(OUT, "_fetch_log.txt"), "w").write(f"run {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC\n" + "\n".join(LOG) + "\n")
