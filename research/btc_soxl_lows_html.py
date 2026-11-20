# -*- coding: utf-8 -*-
"""BTC 사이클 저점 전후 구간을 SOXL과 나란히 보는 단일 HTML 생성 (2026-11-21)
입력: data/crypto/BTCUSD.csv, data/prices/SOXL.csv  → 출력: research/charts/btc_soxl_lows.html
창: 확정 저점 4곳 + 검증 대상 2026-06-30 + 현재(2026-11-20). 각 창에 ±200일 종가를 내장.
"""
import os, json, pandas as pd, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VX = pd.read_csv(f"{ROOT}/data/macro/VIXCLS.csv", parse_dates=["date"]).set_index("date").iloc[:, 0].dropna()
BT = pd.read_csv(f"{ROOT}/data/crypto/BTCUSD.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"])
SX = pd.read_csv(f"{ROOT}/data/prices/SOXL.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"])
btc = BT["close"]; sox = SX["adj_close"]
WINDOWS = [
    ("2015-01-14", "2015-01 저점", "확정 저점 ①"),
    ("2018-12-15", "2018-12 저점", "확정 저점 ②"),
    ("2020-03-12", "2020-03 저점", "확정 저점 ③ (코로나)"),
    ("2022-11-21", "2022-11 저점", "확정 저점 ④ (FTX)"),
    ("2026-06-30", "2026-06-30", "검증 대상 (미확정)"),
    ("2026-11-20", "현재 2026-11", "진행 중 — SOXL 자료는 2026-10-26까지"),
]
PAD = 200
def seg(df, t):
    w = df.loc[t - pd.Timedelta(days=PAD): t + pd.Timedelta(days=PAD)]
    return [[d.strftime("%Y-%m-%d"), round(float(r.open), 4), round(float(r.high), 4), round(float(r.low), 4), round(float(r.close), 4), int(r.volume) if pd.notna(r.volume) else 0] for d, r in w.iterrows()]
out = []
for d, name, note in WINDOWS:
    t = pd.Timestamp(d)
    b = btc.loc[t - pd.Timedelta(days=60): t + pd.Timedelta(days=60)]
    s = sox.loc[t - pd.Timedelta(days=60): t + pd.Timedelta(days=60)]
    stats = {}
    if len(s):
        sl = s.idxmin(); stats["soxl_low"] = sl.strftime("%Y-%m-%d"); stats["lag"] = int((sl - t).days)
        pre = sox.loc[t - pd.Timedelta(days=120): t]
        stats["soxl_dd_pre"] = round(float(s.min() / pre.max() - 1) * 100, 1) if len(pre) else None
    for h in (30, 90):
        for nm, ser in (("btc", btc), ("soxl", sox)):
            a = ser.loc[:t]; b2 = ser.loc[:t + pd.Timedelta(days=h)]
            if len(a) and len(b2) and b2.index[-1] > t: stats[f"{nm}_{h}"] = round(float(b2.iloc[-1] / a.iloc[-1] - 1) * 100, 1)
    vv = VX.loc[:t]; stats["vix"] = round(float(vv.iloc[-1]), 2) if len(vv) else None; stats["vix_date"] = vv.index[-1].strftime("%Y-%m-%d") if len(vv) else None
    vw = VX.loc[t - pd.Timedelta(days=PAD): t + pd.Timedelta(days=PAD)]; vmx = vw.loc[t - pd.Timedelta(days=60): t + pd.Timedelta(days=60)]
    stats["vix_max"] = round(float(vmx.max()), 2) if len(vmx) else None; stats["vix_max_date"] = vmx.idxmax().strftime("%Y-%m-%d") if len(vmx) else None
    out.append(dict(date=d, name=name, note=note, btc=seg(BT, t), soxl=seg(SX, t), vix=[[x.strftime("%Y-%m-%d"), round(float(y), 2)] for x, y in vw.items()], stats=stats))
json.dump(out, open("/tmp/btc_soxl_windows.json", "w"), ensure_ascii=False)
for w in out: print(w["name"], w["stats"], len(w["btc"]), len(w["soxl"]))
t = open(f"{ROOT}/research/charts/btc_soxl_lows_template.html", encoding="utf-8").read()
open(f"{ROOT}/research/charts/btc_soxl_lows.html", "w", encoding="utf-8").write(t.replace("__DATA__", json.dumps(out, ensure_ascii=False)))
