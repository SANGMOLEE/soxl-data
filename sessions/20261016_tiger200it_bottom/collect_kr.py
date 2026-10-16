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
