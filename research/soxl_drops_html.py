# -*- coding: utf-8 -*-
"""SOXL 역대 하루 낙폭(종가 대비 종가) 상위 10일과 각 전후 30일 차트 — 단일 HTML 생성 (2026-11-21)
입력: data/prices/SOXL.csv(조정 종가), data/crypto/BTCUSD.csv(같은 날 BTC 참고) → research/charts/soxl_top_drops.html
"""
import os, json, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = pd.read_csv(f"{ROOT}/data/prices/SOXL.csv", parse_dates=["date"]).set_index("date")["adj_close"].dropna()
btc = pd.read_csv(f"{ROOT}/data/crypto/BTCUSD.csv", parse_dates=["date"]).set_index("date")["close"].dropna()
r = s.pct_change() * 100
top = r.nsmallest(10)
PAD = 30
out = []
for rank, (d, v) in enumerate(top.items(), 1):
    w = s.loc[d - pd.Timedelta(days=PAD): d + pd.Timedelta(days=PAD)]
    prev = s.loc[:d].iloc[-2]; c0 = s[d]
    after = s.loc[d + pd.Timedelta(days=1): d + pd.Timedelta(days=PAD)]
    pre = s.loc[d - pd.Timedelta(days=PAD): d - pd.Timedelta(days=1)]
    def ret(n):
        a = s.loc[d:].iloc[:n + 1]
        return round(float(a.iloc[-1] / c0 - 1) * 100, 1) if len(a) == n + 1 else None
    b_same = None
    if d in btc.index:
        bp = btc.loc[:d]
        if len(bp) >= 2: b_same = round(float(bp.iloc[-1] / bp.iloc[-2] - 1) * 100, 1)
    st = dict(rank=rank, date=d.strftime("%Y-%m-%d"), drop=round(float(v), 2), prev=round(float(prev), 2), close=round(float(c0), 2),
              next1=ret(1), next5=ret(5), next20=ret(20),
              low_after=(after.idxmin().strftime("%Y-%m-%d") if len(after) else None),
              low_after_pct=(round(float(after.min() / c0 - 1) * 100, 1) if len(after) else None),
              pre_high_pct=(round(float(c0 / pre.max() - 1) * 100, 1) if len(pre) else None),
              btc_same=b_same)
    out.append(dict(**st, series=[[x.strftime("%Y-%m-%d"), round(float(y), 4)] for x, y in w.items()]))
    print(rank, st)
t = open(f"{ROOT}/research/charts/soxl_top_drops_template.html", encoding="utf-8").read()
open(f"{ROOT}/research/charts/soxl_top_drops.html", "w", encoding="utf-8").write(t.replace("__DATA__", json.dumps(out, ensure_ascii=False)))
