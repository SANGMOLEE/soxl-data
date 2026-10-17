# -*- coding: utf-8 -*-
"""10/19(월) 종가 시나리오: 미국 10/16(금) 종가 반영한 S2·G 블록 + 가격별 P 블록 → 표시점수.
레버리지(243880) 가격은 하루 등락 2배 근사: lev = lev_close × (1 + 2r)."""
import os, sys, json
import numpy as np, pandas as pd
S = sys.argv[1]; sys.path.insert(0, os.path.join(S, "engine"))
from tiger_it_short_bottom import *
P = os.path.join(S, "data", "prices"); repo = os.path.dirname(os.path.dirname(S))
d = pd.read_csv(os.path.join(S, "output", "daily.csv"), index_col=0, parse_dates=True); c = d["close"]
sox = read_price(os.path.join(P, "SOX.csv"))["close"]; vix = read_price(os.path.join(P, "VIX.csv"))["close"]
lev = read_price(os.path.join(P, "TIGER200IT_LEV.csv"))["close"] if os.path.exists(os.path.join(P, "TIGER200IT_LEV.csv")) else None
nq = read_price(os.path.join(P, "NASDAQ.csv"))["close"] if os.path.exists(os.path.join(P, "NASDAQ.csv")) else None
us = "2026-10-16"
g1 = (sox / sox.rolling(20).max() - 1).loc[us]; g2 = wilder_rsi(sox).loc[us]; v20 = vix.rolling(20).max().loc[us]
G = bands_le([g1], G1_CUTS, G1_PTS)[0] + bands_le([g2], G2_CUTS, G2_PTS)[0]; S2 = bands_ge([v20], S2_CUTS, S2_PTS)[0]
fgp = os.path.join(repo, "data", "sentiment", "fear_greed.csv"); fg = pd.read_csv(fgp, parse_dates=["date"]).set_index("date")["value"]
fg_last = fg.iloc[-1]; S3 = bands_le([fg_last], S3_CUTS, S3_PTS)[0]
S1 = d["S1"].iloc[-1]; S4 = d["S4"].iloc[-1]   # 코스피 실현변동성·원달러는 10/16 값 유지
Sblk = S1 + S2 + S3 + S4
print(json.dumps({"us_date": us, "SOX": round(float(sox.loc[us]), 2), "SOX_dd20": round(float(g1), 4), "SOX_rsi": round(float(g2), 1), "VIX": float(vix.loc[us]), "VIX_20max": round(float(v20), 2),
                  "NASDAQ": None if nq is None else round(float(nq.loc[us]), 2), "NASDAQ_chg": None if nq is None else round(float(nq.loc[us] / nq.shift(1).loc[us] - 1), 4),
                  "fear_greed": {"date": str(fg.index[-1].date()), "value": float(fg_last)}, "G": G, "S2": S2, "S3": S3, "S1": S1, "S4": S4, "S": Sblk,
                  "lev_close_1016": None if lev is None else float(lev.iloc[-1]), "lev_last_date": None if lev is None else str(lev.index[-1].date()),
                  "etf_close_1016": float(c.iloc[-1])}, ensure_ascii=False))
base = c.iloc[-1]; levc = None if lev is None else lev.iloc[-1]
rows = []
for V, label in [(2, "V2"), (10, "V10")]:
    for chg in [0.06, 0.04, 0.02, 0.0, -0.02, -0.04, -0.05, -0.07, -0.10, -0.12]:
        px = base * (1 + chg); c2 = pd.concat([c, pd.Series([px], index=[pd.Timestamp("2026-10-19")])])
        p1 = px / c2.rolling(20).max().iloc[-1] - 1; p2 = wilder_rsi(c2).iloc[-1]; p3 = px / c2.rolling(20).mean().iloc[-1] - 1; p4 = px / c2.iloc[-6] - 1
        Pblk = bands_le([p1], P1_CUTS, P1_PTS)[0] + bands_le([p2], P2_CUTS, P2_PTS)[0] + bands_le([p3], P3_CUTS, P3_PTS)[0] + bands_le([p4], P4_CUTS, P4_PTS)[0]
        rows.append({"V": label, "chg": chg, "etf": round(px), "lev": None if levc is None else round(levc * (1 + 2 * chg)), "P": Pblk, "display": 100 - Pblk - V - Sblk - G, "rsi": round(p2, 1), "dd20": round(p1, 3)})
T = pd.DataFrame(rows); print(T.to_string(index=False))
# 기준선 경계 가격 (0.1% 간격 탐색)
for V in (2, 10):
    bounds = {}
    for thr in (50, 45, 40, 35):
        found = None
        for chg in np.arange(0.08, -0.20, -0.001):
            px = base * (1 + chg); c2 = pd.concat([c, pd.Series([px], index=[pd.Timestamp("2026-10-19")])])
            p1 = px / c2.rolling(20).max().iloc[-1] - 1; p2 = wilder_rsi(c2).iloc[-1]; p3 = px / c2.rolling(20).mean().iloc[-1] - 1; p4 = px / c2.iloc[-6] - 1
            Pblk = bands_le([p1], P1_CUTS, P1_PTS)[0] + bands_le([p2], P2_CUTS, P2_PTS)[0] + bands_le([p3], P3_CUTS, P3_PTS)[0] + bands_le([p4], P4_CUTS, P4_PTS)[0]
            if 100 - Pblk - V - Sblk - G <= thr: found = (round(chg, 3), round(px), None if levc is None else round(levc * (1 + 2 * chg))); break
        bounds[thr] = found
    print("V", V, "경계(처음 ≤thr 되는 등락·ETF·레버리지):", bounds)
