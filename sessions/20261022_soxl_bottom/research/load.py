# -*- coding: utf-8 -*-
"""공통 로더 — 저장소 data/ 를 읽어 하나의 일간 패널로 만든다."""
import os
import pandas as pd, numpy as np
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data") + os.sep

def px(t, col="close"):
    d = pd.read_csv(D + f"prices/{t}.csv", parse_dates=["date"]).set_index("date")
    return d[col].astype(float)

def macro(s):
    d = pd.read_csv(D + f"macro/{s}.csv", parse_dates=["date"]).set_index("date")
    return pd.to_numeric(d["value"], errors="coerce")

def rsi(s, n=14):
    d = s.diff()
    u = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    v = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + u/v)

def panel():
    sox = px("SOX"); cal = px("SPY").index.union(sox.index)
    p = pd.DataFrame(index=sox.index)
    p["sox"] = sox
    p["spy"] = px("SPY").reindex(p.index)
    p["nvda"] = px("NVDA").reindex(p.index)
    p["soxl"] = px("SOXL").reindex(p.index)
    p["soxl_low"] = px("SOXL", "low").reindex(p.index)
    p["soxl_vol"] = px("SOXL", "volume").reindex(p.index)
    p["vix"] = macro("VIXCLS").reindex(p.index).ffill(limit=3)
    p["hy"] = macro("BAMLH0A0HYM2").reindex(p.index).ffill(limit=3)
    p["nfci"] = macro("NFCI").reindex(p.index, method="ffill")
    p["t10y2y"] = macro("T10Y2Y").reindex(p.index).ffill(limit=3)
    fg = pd.read_csv(D + "sentiment/fear_greed.csv", parse_dates=["date"]).set_index("date")["value"]
    p["fg"] = fg.reindex(p.index).ffill(limit=3)
    # 합성 3배: SOX 일간수익률 x3 - 연 0.9% 보수
    r = p["sox"].pct_change().fillna(0)
    p["syn3"] = (1 + 3*r - 0.009/252).cumprod()
    s = p["sox"]
    p["dd60"] = s / s.rolling(60, min_periods=20).max() - 1
    p["days_since_hi60"] = s.rolling(60, min_periods=20).apply(lambda a: len(a)-1-np.argmax(a), raw=True)
    p["dd_ath"] = s / s.cummax() - 1
    p["ma200"] = s / s.rolling(200).mean() - 1
    p["ma50"] = s / s.rolling(50).mean() - 1
    p["rsi"] = rsi(s)
    p["spy_dd60"] = p["spy"] / p["spy"].rolling(60, min_periods=20).max() - 1
    p["vix60max"] = p["vix"].rolling(60, min_periods=20).max()
    p["hy_chg20"] = p["hy"] - p["hy"].shift(20)
    # NVDA 필터: NVDA 낙폭 / SOX 낙폭 (504거래일 창)
    nd = p["nvda"] / p["nvda"].rolling(504, min_periods=100).max() - 1
    sd = s / s.rolling(504, min_periods=100).max() - 1
    p["nvda_ratio"] = nd / sd
    return p
