# -*- coding: utf-8 -*-
"""100점 저점 점수 연구 — 공통 피처 (2026-11-20). 모든 값은 그날 종가까지의 정보만 사용(사후 없음)."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data", "crypto", "BTCUSD.csv")
ONCHAIN = os.path.join(HERE, "..", "data", "crypto", "BTC_ONCHAIN.csv")
BCPS = os.path.join(HERE, "bcps", "bcps_series.csv")
VIX = os.path.join(HERE, "..", "data", "macro", "VIXCLS.csv")

CYCLE_LOWS = ["2015-01-14", "2018-12-15", "2020-03-12", "2022-11-21", "2026-06-30"]

def rsi(s, n=14):
    d = s.diff(); u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + u / dn)

def load():
    b = pd.read_csv(D, parse_dates=["date"]).set_index("date").sort_index()
    ix = pd.date_range(b.index[0], b.index[-1]); b = b.reindex(ix).ffill()
    c, h, l, v = b.close, b.high, b.low, b.volume
    F = pd.DataFrame(index=ix); F["close"] = c; F["high"] = h; F["low"] = l; F["vol"] = v
    # ── 빠른(타이밍) 피처: 낮을수록/높을수록 저점형 방향은 ORIENT 에 기록
    F["rsi14"] = rsi(c, 14); F["rsi7"] = rsi(c, 7); F["rsi3"] = rsi(c, 3)
    F["dd30"] = c / c.rolling(30).max() - 1; F["dd90"] = c / c.rolling(90).max() - 1
    F["r1"] = c.pct_change(); F["r3"] = c / c.shift(3) - 1; F["r7"] = c / c.shift(7) - 1; F["r14"] = c / c.shift(14) - 1
    F["volr"] = v / v.rolling(30).median().shift(1)
    F["bbz"] = (c - c.rolling(20).mean()) / c.rolling(20).std()
    dn = (c.diff() < 0).astype(int); F["downrun"] = dn.groupby((dn == 0).cumsum()).cumsum()
    F["rv20"] = np.log(c).diff().rolling(20).std() * np.sqrt(365)
    F["lowtail"] = (c - l) / (h - l).replace(0, np.nan)           # 당일 종가가 저가에서 얼마나 회복했나(1=고가 마감)
    F["ma50d"] = c / c.rolling(50).mean() - 1
    F["lo14"] = c / c.rolling(14).min() - 1                        # 0이면 14일 신저가
    # ── 느린(구간) 피처
    F["mayer"] = c / c.rolling(200).mean() - 1; F["w200"] = c / c.rolling(1400).mean() - 1
    F["ath"] = c.cummax(); F["ddath"] = c / F.ath - 1
    athd = pd.Series(ix.where(c == F.ath), index=ix).ffill(); F["days_ath"] = (ix - pd.DatetimeIndex(athd)).days
    F.loc[:"2017-01-01", "days_ath"] = (F.loc[:"2017-01-01"].index - pd.Timestamp("2013-12-04")).days
    wr = pd.Series(np.nan, index=ix)
    for k in range(7):
        s = c.iloc[k::7]; wr.loc[s.index] = rsi(s)
    F["rsi_w"] = wr
    o = pd.read_csv(ONCHAIN, parse_dates=["date"]).set_index("date").sort_index()
    F["mvrv"] = o.mvrv.reindex(ix).ffill(); F["rp"] = c / o.realized_price.reindex(ix).ffill() - 1
    bc = pd.read_csv(BCPS, parse_dates=["date"]).set_index("date").sort_index()
    F["bcps"] = bc.bcps.reindex(ix).ffill()
    vx = pd.read_csv(VIX, parse_dates=["date"]).set_index("date")["value"]; F["vix"] = vx.reindex(ix).ffill()
    return F

# 방향: -1 = 낮을수록 저점형, +1 = 높을수록 저점형
ORIENT = dict(rsi14=-1, rsi7=-1, rsi3=-1, dd30=-1, dd90=-1, r1=-1, r3=-1, r7=-1, r14=-1, volr=+1, bbz=-1, downrun=+1, rv20=+1,
              lowtail=+1, ma50d=-1, lo14=-1, mayer=-1, w200=-1, ddath=-1, days_ath=+1, rsi_w=-1, mvrv=-1, rp=-1, bcps=-1, vix=+1)
FAST = ["rsi14", "rsi7", "rsi3", "dd30", "dd90", "r1", "r3", "r7", "r14", "volr", "bbz", "downrun", "rv20", "lowtail", "ma50d", "lo14"]
SLOW = ["mayer", "w200", "ddath", "days_ath", "rsi_w", "mvrv", "rp", "bcps"]

def pct_rank(F, cols, win=1460, minp=180):
    """4년 창 백분위(0~100, 높을수록 저점형). 그날까지의 정보만."""
    P = pd.DataFrame(index=F.index)
    for k in cols:
        s = F[k] * ORIENT[k]
        P[k] = s.rolling(win, min_periods=minp).rank(pct=True) * 100
    return P

def local_lows(F, win=91, dd=-0.20):
    c = F.close
    m = (c == c.rolling(win, center=True).min()) & (c / c.rolling(90).max() - 1 <= dd)
    return list(F.index[m])
