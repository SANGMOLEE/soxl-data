# -*- coding: utf-8 -*-
"""TIGER 200 IT 단기저점 연구 - 한국 시장 데이터 수집 (GitHub Actions 러너에서 실행)

출력: sessions/20261016_tiger200it_bottom/data/
  prices/{이름}.csv          date,open,high,low,close,adj_close,volume,source
  krx/etf_139260.csv         NAV,시가,고가,저가,종가,거래량,거래대금,기초지수
  krx/flow_{이름}.csv        투자자별 순매수 거래대금 (기관합계,기타법인,개인,외국인합계,전체)
  krx/index_{이름}.csv       KRX 지수 OHLCV
  krx/short_139260.csv       공매도 거래량
  collect_log.json           성공/실패 기록
"""
import os, sys, json, datetime, traceback
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "data")
os.makedirs(os.path.join(OUT, "prices"), exist_ok=True)
os.makedirs(os.path.join(OUT, "krx"), exist_ok=True)

LOG = {"ok": [], "failed": [], "notes": [], "run_at_utc": datetime.datetime.utcnow().isoformat()}

def ok(msg):   LOG["ok"].append(msg);     print("[OK]  ", msg)
def fail(msg): LOG["failed"].append(msg); print("[FAIL]", msg)
def note(msg): LOG["notes"].append(msg);  print("[NOTE]", msg)

# ─────────────────────────────── 1. Yahoo (yfinance)
YF = {
    "TIGER200IT": "139260.KS",   # 매매 대상
    "KOSPI":      "^KS11",
    "KOSPI200":   "^KS200",
    "KOSDAQ":     "^KQ11",
    "SAMSUNG":    "005930.KS",
    "HYNIX":      "000660.KS",
    "KODEX_SEMI": "091160.KS",
    "USDKRW":     "KRW=X",
    "SOX":        "^SOX",
    "VIX":        "^VIX",
    "SOXX":       "SOXX",
    "EWY":        "EWY",         # 미국상장 한국 ETF (야간 선행지표)
}
try:
    import yfinance as yf
    for name, sym in YF.items():
        try:
            df = yf.Ticker(sym).history(period="max", auto_adjust=False)
            if df is None or len(df) == 0:
                fail(f"yahoo {name} ({sym}): 빈 응답"); continue
            df = df.reset_index()
            df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
            keep = ["date", "open", "high", "low", "close", "adj_close", "volume"]
            for k in keep:
                if k not in df.columns: df[k] = None
            df = df[keep].copy()
            df["source"] = "yahoo"
            df = df[df["close"].notna()]
            df.to_csv(os.path.join(OUT, "prices", f"{name}.csv"), index=False)
            ok(f"yahoo {name} ({sym}): {len(df)}행 {df['date'].iloc[0]}~{df['date'].iloc[-1]}")
        except Exception as e:
            fail(f"yahoo {name} ({sym}): {e!r}")
except Exception as e:
    fail(f"yfinance import: {e!r}")

# ─────────────────────────────── 2. KRX (pykrx)
TODAY = datetime.date.today().strftime("%Y%m%d")
try:
    from pykrx import stock

    def save(df, path, label):
        if df is None or len(df) == 0:
            fail(f"{label}: 빈 응답"); return
        df = df.copy()
        df.index.name = "date"
        df.to_csv(path, encoding="utf-8-sig")
        ok(f"{label}: {len(df)}행 {df.index[0]}~{df.index[-1]}")

    # 2-1. ETF OHLCV + NAV
    try:
        df = stock.get_etf_ohlcv_by_date("20110101", TODAY, "139260")
        save(df, os.path.join(OUT, "krx", "etf_139260.csv"), "krx etf_139260")
    except Exception as e:
        fail(f"krx etf_139260: {e!r}")

    # 2-2. 투자자별 순매수 (거래대금) — ETF, 코스피 전체, 삼성전자, 하이닉스
    for label, tk in {"139260": "139260", "KOSPI": "KOSPI", "005930": "005930", "000660": "000660"}.items():
        try:
            df = stock.get_market_trading_value_by_date("20150101", TODAY, tk)
            save(df, os.path.join(OUT, "krx", f"flow_{label}.csv"), f"krx flow_{label}")
        except Exception as e:
            fail(f"krx flow_{label}: {e!r}")
        try:
            df = stock.get_market_trading_volume_by_date("20150101", TODAY, tk)
            save(df, os.path.join(OUT, "krx", f"flowvol_{label}.csv"), f"krx flowvol_{label}")
        except Exception as e:
            fail(f"krx flowvol_{label}: {e!r}")

    # 2-3. 지수 — 이름에 '정보기술' / '변동성' / '코스피 200' 포함되는 것 전부
    found = {}
    for mkt in ["KOSPI", "KOSDAQ", "KRX", "테마"]:
        try:
            for t in stock.get_index_ticker_list(market=mkt):
                try:
                    nm = stock.get_index_ticker_name(t)
                except Exception:
                    nm = "?"
                found[t] = f"{mkt}:{nm}"
        except Exception as e:
            fail(f"krx index list {mkt}: {e!r}")
    json.dump(found, open(os.path.join(OUT, "krx", "index_tickers.json"), "w"), ensure_ascii=False, indent=1)
    note(f"krx 지수 목록 {len(found)}개 저장")
    want = [t for t, nm in found.items()
            if any(k in nm for k in ["정보기술", "변동성", "VKOSPI", "V-KOSPI"]) or nm.endswith(":코스피 200") or nm.endswith(":코스피")]
    for t in want:
        try:
            df = stock.get_index_ohlcv("20100101", TODAY, t)
            safe = found[t].split(":", 1)[1].replace(" ", "_").replace("/", "_")
            save(df, os.path.join(OUT, "krx", f"index_{t}_{safe}.csv"), f"krx index {found[t]}")
        except Exception as e:
            fail(f"krx index {found[t]}: {e!r}")

    # 2-4. 공매도
    try:
        df = stock.get_shorting_volume_by_date("20180101", TODAY, "139260")
        save(df, os.path.join(OUT, "krx", "short_139260.csv"), "krx short_139260")
    except Exception as e:
        fail(f"krx short_139260: {e!r}")
    try:
        df = stock.get_shorting_volume_by_date("20180101", TODAY, "005930")
        save(df, os.path.join(OUT, "krx", "short_005930.csv"), "krx short_005930")
    except Exception as e:
        fail(f"krx short_005930: {e!r}")

    # 2-5. ETF 구성종목 (현재)
    try:
        df = stock.get_etf_portfolio_deposit_file("139260")
        save(df, os.path.join(OUT, "krx", "pdf_139260.csv"), "krx pdf_139260")
    except Exception as e:
        fail(f"krx pdf_139260: {e!r}")

except Exception as e:
    fail(f"pykrx import: {e!r}")
    traceback.print_exc()

# ─────────────────────────────── 2b. 네이버 금융 (KRX가 해외 IP를 막을 때의 대안)
import time, io, re
try:
    import requests
    NH = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
          "Referer": "https://finance.naver.com/"}
    os.makedirs(os.path.join(OUT, "naver"), exist_ok=True)
    SESSION = requests.Session(); SESSION.headers.update(NH)

    def get(url, **kw):
        r = SESSION.get(url, timeout=30, **kw); r.raise_for_status(); return r

    def read_tables(html, **kw):
        try:
            return pd.read_html(io.StringIO(html), flavor="lxml", **kw)
        except Exception:
            return pd.read_html(io.StringIO(html), flavor="bs4", **kw)

    # 2b-1. 코스피 투자자별 일별 매매동향 (억원) — 개인/외국인/기관계 ...
    START = pd.Timestamp("2015-01-01")
    def naver_investor_trend(sosok, label):
        rows = []
        bizdate = datetime.date.today().strftime("%Y%m%d")
        for page in range(1, 400):
            url = f"https://finance.naver.com/sise/investorDealTrendDay.naver?bizdate={bizdate}&sosok={sosok}&page={page}"
            r = get(url); r.encoding = "euc-kr"
            tabs = read_tables(r.text, match="날짜")
            if not tabs: break
            t = tabs[0]
            if isinstance(t.columns, pd.MultiIndex):
                t.columns = ["_".join([str(c) for c in col if not str(c).startswith("Unnamed")]).strip("_") for col in t.columns]
            t = t.dropna(how="all")
            t = t[t.iloc[:, 0].astype(str).str.match(r"\d{2}\.\d{2}\.\d{2}")]
            if len(t) == 0: break
            rows.append(t)
            last = pd.to_datetime(t.iloc[-1, 0], format="%y.%m.%d")
            if last < START: break
            time.sleep(0.15)
        if not rows: fail(f"naver investor {label}: 빈 응답"); return
        df = pd.concat(rows, ignore_index=True)
        df = df.rename(columns={df.columns[0]: "date"})
        df["date"] = pd.to_datetime(df["date"], format="%y.%m.%d").dt.strftime("%Y-%m-%d")
        df = df.drop_duplicates("date").sort_values("date")
        df = df[pd.to_datetime(df["date"]) >= START]
        df.to_csv(os.path.join(OUT, "naver", f"investor_{label}.csv"), index=False, encoding="utf-8-sig")
        ok(f"naver investor {label}: {len(df)}행 {df['date'].iloc[0]}~{df['date'].iloc[-1]} cols={list(df.columns)}")

    for sosok, label in []:
        try: naver_investor_trend(sosok, label)
        except Exception as e: fail(f"naver investor {label}: {e!r}")

    # 2b-2. 종목별 외국인·기관 순매매 (주수) — 139260, 005930, 000660
    def naver_frgn(code):
        rows = []
        for page in range(1, 300):
            r = get(f"https://finance.naver.com/item/frgn.naver?code={code}&page={page}"); r.encoding = "euc-kr"
            tabs = read_tables(r.text, match="기관")
            cand = [t for t in tabs if t.shape[1] >= 8]
            if not cand: break
            t = cand[-1]
            if isinstance(t.columns, pd.MultiIndex):
                t.columns = ["_".join([str(c) for c in col if not str(c).startswith("Unnamed")]).strip("_") for col in t.columns]
            t = t.dropna(how="all")
            t = t[t.iloc[:, 0].astype(str).str.match(r"\d{4}\.\d{2}\.\d{2}")]
            if len(t) == 0: break
            rows.append(t)
            last = pd.to_datetime(t.iloc[-1, 0], format="%Y.%m.%d")
            if last < START: break
            time.sleep(0.15)
        if not rows: fail(f"naver frgn {code}: 빈 응답"); return
        df = pd.concat(rows, ignore_index=True)
        df = df.rename(columns={df.columns[0]: "date"})
        df["date"] = pd.to_datetime(df["date"], format="%Y.%m.%d").dt.strftime("%Y-%m-%d")
        df = df.drop_duplicates("date").sort_values("date")
        df = df[pd.to_datetime(df["date"]) >= START]
        df.to_csv(os.path.join(OUT, "naver", f"frgn_{code}.csv"), index=False, encoding="utf-8-sig")
        ok(f"naver frgn {code}: {len(df)}행 {df['date'].iloc[0]}~{df['date'].iloc[-1]} cols={list(df.columns)}")

    for code in []:
        try: naver_frgn(code)
        except Exception as e: fail(f"naver frgn {code}: {e!r}")

    # 2b-3. VKOSPI / 코스피200 / 업종지수 — 여러 경로 시도, 되는 것만 저장
    tries = {
        "fchart_VKOSPI": "https://fchart.stock.naver.com/sise.nhn?symbol=VKOSPI&timeframe=day&count=4000&requestType=0",
        "fchart_KPI200": "https://fchart.stock.naver.com/sise.nhn?symbol=KPI200&timeframe=day&count=4000&requestType=0",
        "fchart_KOSPI":  "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=4000&requestType=0",
        "fchart_139260": "https://fchart.stock.naver.com/sise.nhn?symbol=139260&timeframe=day&count=4000&requestType=0",
        "mapi_VKOSPI":   "https://m.stock.naver.com/api/index/VKOSPI/price?pageSize=100&page=1",
        "mapi_KPI200":   "https://m.stock.naver.com/api/index/KPI200/price?pageSize=100&page=1",
        "sise_VKOSPI":   "https://finance.naver.com/sise/sise_index_day.naver?code=VKOSPI&page=1",
        "sise_KPI200":   "https://finance.naver.com/sise/sise_index_day.naver?code=KPI200&page=1",
        "nhn_investor":  "https://finance.naver.com/sise/investorDealTrendDay.nhn?bizdate=20261016&sosok=01&page=1",
        "nhn_index_day": "https://finance.naver.com/sise/sise_index_day.nhn?code=KPI200&page=1",
        "mapi_stock_trend": "https://m.stock.naver.com/api/stock/005930/trend?pageSize=20&page=1",
        "mapi_etf_trend":   "https://m.stock.naver.com/api/stock/139260/trend?pageSize=20&page=1",
        "mapi_index_trend": "https://m.stock.naver.com/api/index/KOSPI/trend?pageSize=20&page=1",
        "mapi_index_price": "https://m.stock.naver.com/api/index/KOSPI/price?pageSize=20&page=1",
        "mapi_vkospi_basic": "https://m.stock.naver.com/api/index/VKOSPI/basic",
        "api_index_chart":  "https://api.stock.naver.com/chart/domestic/index/KOSPI/day?startDateTime=20261001&endDateTime=20261016",
        "api_vkospi_chart": "https://api.stock.naver.com/chart/domestic/index/VKOSPI/day?startDateTime=20261001&endDateTime=20261016",
        "fchart_VKOSPI2":   "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI200VOL&timeframe=day&count=100&requestType=0",
        "investor_total":   "https://finance.naver.com/sise/sise_trans_style.naver",
        "sise_investor_by_date": "https://finance.naver.com/sise/sise_index.naver?code=KOSPI",
        "mapi_vkospi_price20": "https://m.stock.naver.com/api/index/VKOSPI/price?pageSize=20&page=1",
        "mapi_kpi200_price20": "https://m.stock.naver.com/api/index/KPI200/price?pageSize=20&page=1",
        "mapi_idx_trend_list": "https://m.stock.naver.com/api/index/KOSPI/trend/list?pageSize=20&page=1",
        "mapi_idx_investor": "https://m.stock.naver.com/api/index/KOSPI/investor?pageSize=20&page=1",
        "mapi_idx_investorTrend": "https://m.stock.naver.com/api/index/KOSPI/investorTrend?pageSize=20&page=1",
        "mapi_idx_trendDaily": "https://m.stock.naver.com/api/index/KOSPI/trendDaily?pageSize=20&page=1",
        "mapi_idx_dealTrend": "https://m.stock.naver.com/api/index/KOSPI/investorDealTrend?pageSize=20&page=1",
        "api_idx_investor": "https://api.stock.naver.com/index/KOSPI/investor?pageSize=20&page=1",
        "mapi_idx_total": "https://m.stock.naver.com/api/index/KOSPI/total",
        "sise_deal_rank": "https://finance.naver.com/sise/investorDealTrendDay.naver?bizdate=20261016&sosok=01",
    }
    for k, url in tries.items():
        try:
            r = get(url)
            txt = r.text
            note(f"naver try {k}: HTTP {r.status_code}, {len(txt)} bytes, head={txt[:120]!r}")
            if r.ok and len(txt) > 200:
                open(os.path.join(OUT, "naver", f"try_{k}.txt"), "w", encoding="utf-8").write(txt[:400000])
        except Exception as e:
            fail(f"naver try {k}: {e!r}")

    # 2b-3b. 모바일 API 투자자 동향 전체 수집 — page 파라미터가 무시되므로(4차 실행에서 확인) 페이지 방식 탐색
    def _first_date(js):
        if isinstance(js, dict): js = js.get("trendList") or js.get("list") or js.get("data") or []
        return (str(js[0].get("bizdate", ""))[:8], js) if js else ("", [])
    def mapi_trend(kind, code, label, start="20150101"):
        base = f"https://m.stock.naver.com/api/{kind}/{code}/trend"
        d1, js1 = _first_date(get(f"{base}?pageSize=20&page=1").json())
        if not js1: fail(f"naver mapi trend {label}: 빈 응답"); return
        last1 = str(js1[-1].get("bizdate", ""))[:8]
        scheme = None
        for q in [f"{base}?pageSize=20&page=2", f"{base}?pageSize=20&pageNo=2", f"{base}?pageSize=20&offset=20",
                  f"{base}?pageSize=20&bizdate={last1}", f"{base}?bizdate={last1}&pageSize=20", f"{base}?pageSize=20&endDate={last1}",
                  f"{base}?pageSize=20&page=1&bizdate={last1}", f"{base}?pageSize=20&startDate=20250101&endDate={last1}"]:
            try:
                d2, js2 = _first_date(get(q).json())
                note(f"naver trend scheme {label} {q.split('?')[1]} -> first={d2} n={len(js2)}")
                if js2 and d2 and d2 != d1 and d2 <= last1: scheme = q; break
            except Exception as e:
                note(f"naver trend scheme {label} {q.split('?')[1]} -> {e!r}")
        rows = list(js1)
        if scheme is None:
            fail(f"naver mapi trend {label}: 페이지 넘김 방법 못 찾음 — 최근 20일만 저장")
        else:
            cur = last1; seen = {str(r.get("bizdate"))[:8] for r in rows}
            for _ in range(1, 600):
                if "page=2" in scheme: q = scheme.replace("page=2", f"page={_+1}")
                elif "pageNo=2" in scheme: q = scheme.replace("pageNo=2", f"pageNo={_+1}")
                elif "offset=20" in scheme: q = scheme.replace("offset=20", f"offset={20*_}")
                else: q = scheme.replace(last1, cur)
                d2, js2 = _first_date(get(q).json())
                new = [r for r in js2 if str(r.get("bizdate"))[:8] not in seen]
                if not new: break
                rows.extend(new); seen.update(str(r.get("bizdate"))[:8] for r in new)
                cur = min(str(r.get("bizdate"))[:8] for r in new)
                # 날짜 앵커 방식이면 그 날짜 '이전'으로 가야 하므로 하루 빼서 다시 요청
                if "page" not in scheme and "offset" not in scheme:
                    cur = (pd.Timestamp(cur) - pd.Timedelta(days=1)).strftime("%Y%m%d")
                if cur < start: break
                time.sleep(0.05)
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(OUT, "naver", f"mapi_trend_{label}.csv"), index=False, encoding="utf-8-sig")
        ok(f"naver mapi trend {label}: {len(df)}행 {df['bizdate'].min()}~{df['bizdate'].max()} (고유 {df['bizdate'].nunique()})")
    for kind, code, label in [("stock", "005930", "005930"), ("stock", "000660", "000660"), ("stock", "139260", "139260")]:
        try: mapi_trend(kind, code, label)
        except Exception as e: fail(f"naver mapi trend {label}: {e!r}")

    # 2b-3b'. 코스피 투자자별(개인/외국인/기관) — index trend는 하루치 dict만 주므로 bizdate로 하루씩 (2016-01-01~)
    try:
        r = get("https://m.stock.naver.com/api/index/KOSPI/trend?bizdate=20261015"); js = r.json()
        note(f"naver index trend bizdate test -> {str(js)[:150]}")
        if isinstance(js, dict) and str(js.get("bizdate", "")).startswith("20261015"):
            etfp = os.path.join(OUT, "prices", "TIGER200IT.csv")
            days = pd.read_csv(etfp)["date"].astype(str).str.replace("-", "")
            days = [d for d in days if d >= "20160101"]
            rows = []
            for d in days:
                try:
                    js = get(f"https://m.stock.naver.com/api/index/KOSPI/trend?bizdate={d}").json()
                    if isinstance(js, dict) and js.get("bizdate"): rows.append(js)
                except Exception: pass
                time.sleep(0.03)
            df = pd.DataFrame(rows).drop_duplicates("bizdate")
            df.to_csv(os.path.join(OUT, "naver", "mapi_trend_KOSPI.csv"), index=False, encoding="utf-8-sig")
            ok(f"naver index trend KOSPI: {len(df)}행 {df['bizdate'].min()}~{df['bizdate'].max()} cols={list(df.columns)}")
        else:
            fail("naver index trend KOSPI: bizdate 방식 불가")
    except Exception as e:
        fail(f"naver index trend KOSPI: {e!r}")

    # 2b-3c. 모바일 API 지수 일별 시세 전체 (VKOSPI, KPI200)
    def mapi_index_price(code, label, start="2010-01-01"):
        rows = []
        for page in range(1, 500):
            r = get(f"https://m.stock.naver.com/api/index/{code}/price?pageSize=20&page={page}")
            js = r.json()
            if not isinstance(js, list) or not js: break
            rows.extend(js)
            d = str(js[-1].get("localTradedAt", ""))[:10]
            if d and d < start: break
            time.sleep(0.08)
        if not rows: fail(f"naver mapi price {label}: 빈 응답"); return
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["localTradedAt"].astype(str).str[:10])
        for ccol in ["closePrice", "openPrice", "highPrice", "lowPrice"]:
            if ccol in df.columns: df[ccol] = pd.to_numeric(df[ccol].astype(str).str.replace(",", ""), errors="coerce")
        df = df.drop_duplicates("date").sort_values("date")
        df[["date", "openPrice", "highPrice", "lowPrice", "closePrice"]].rename(columns={"openPrice": "open", "highPrice": "high", "lowPrice": "low", "closePrice": "close"}).to_csv(
            os.path.join(OUT, "naver", f"index_{label}.csv"), index=False, encoding="utf-8-sig")
        ok(f"naver mapi price {label}: {len(df)}행 {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")
    for code, label in [("VKOSPI", "VKOSPI"), ("KPI200", "KOSPI200")]:
        try: mapi_index_price(code, label)
        except Exception as e: fail(f"naver mapi price {label}: {e!r}")

    # 2b-4. VKOSPI 일별 페이지 전체 (sise_index_day) — 위 시도가 성공하면 전 기간 수집
    def naver_index_day(code, label, maxpage=700):
        rows = []
        for page in range(1, maxpage):
            r = get(f"https://finance.naver.com/sise/sise_index_day.naver?code={code}&page={page}"); r.encoding = "euc-kr"
            tabs = read_tables(r.text, match="날짜")
            if not tabs: break
            t = tabs[0].dropna(how="all")
            t = t[t.iloc[:, 0].astype(str).str.match(r"\d{4}\.\d{2}\.\d{2}")]
            if len(t) == 0: break
            rows.append(t)
            last = pd.to_datetime(t.iloc[-1, 0], format="%Y.%m.%d")
            if last < pd.Timestamp("2010-01-01"): break
            time.sleep(0.12)
        if not rows: fail(f"naver index_day {label}: 빈 응답"); return
        df = pd.concat(rows, ignore_index=True)
        df = df.rename(columns={df.columns[0]: "date"})
        df["date"] = pd.to_datetime(df["date"], format="%Y.%m.%d").dt.strftime("%Y-%m-%d")
        df = df.drop_duplicates("date").sort_values("date")
        df.to_csv(os.path.join(OUT, "naver", f"index_{label}.csv"), index=False, encoding="utf-8-sig")
        ok(f"naver index_day {label}: {len(df)}행 {df['date'].iloc[0]}~{df['date'].iloc[-1]} cols={list(df.columns)}")

    for code, label in []:
        try: naver_index_day(code, label)
        except Exception as e: fail(f"naver index_day {label}: {e!r}")

except Exception as e:
    fail(f"naver block: {e!r}")
    traceback.print_exc()

# ─────────────────────────────── 3. VKOSPI 직접 시도 (KRX 통계 API)
try:
    import requests
    url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    hdr = {"User-Agent": "Mozilla/5.0", "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201030108"}
    # 파생상품 지수(VKOSPI) 시세 추이 bld. 실패해도 무방 — 로그만 남김
    for bld, idx in [("dbms/MDC/STAT/standard/MDCSTAT01201", "1"),]:
        payload = {"bld": bld, "locale": "ko_KR", "idxIndMidclssCd": "01", "indIdx": idx, "indIdx2": "001",
                   "strtDd": "20100101", "endDd": TODAY, "share": "1", "money": "1", "csvxls_isNo": "false"}
        r = requests.post(url, data=payload, headers=hdr, timeout=60)
        note(f"krx raw {bld}: HTTP {r.status_code}, {len(r.text)} bytes")
        if r.ok and r.text.strip().startswith("{"):
            json.dump(r.json(), open(os.path.join(OUT, "krx", f"raw_{bld.split('/')[-1]}.json"), "w"), ensure_ascii=False)
except Exception as e:
    fail(f"krx raw VKOSPI: {e!r}")

json.dump(LOG, open(os.path.join(OUT, "collect_log.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({"ok": len(LOG["ok"]), "failed": len(LOG["failed"])}))
