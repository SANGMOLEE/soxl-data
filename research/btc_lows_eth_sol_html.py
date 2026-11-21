# -*- coding: utf-8 -*-
"""BTC 사이클 저점 전 1개월 ~ 후 1년: BTC·ETH·SOL 나란히 보기 — 단일 HTML (2026-11-21)
입력: data/crypto/BTCUSD.csv(OHLCV), SOLUSD.csv(OHLCV), ETHUSD_cm.csv(Coin Metrics 종가만, ~2026-05-23; 있으면 ETHUSD.csv OHLCV 우선)
출력: research/charts/btc_lows_eth_sol.html
"""
import os, json, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT = pd.read_csv(f"{ROOT}/data/crypto/BTCUSD.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"])
SL = pd.read_csv(f"{ROOT}/data/crypto/SOLUSD.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"])
if os.path.exists(f"{ROOT}/data/crypto/ETHUSD.csv"):
    ET = pd.read_csv(f"{ROOT}/data/crypto/ETHUSD.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"]); ETH_OHLC = True
else:
    ET = pd.read_csv(f"{ROOT}/data/crypto/ETHUSD_cm.csv", parse_dates=["date"]).set_index("date").dropna(subset=["close"]); ETH_OHLC = False
WINDOWS = [
    ("2015-01-14", "2015-01 저점", "확정 저점 ① — ETH 상장 전(2015-08), SOL 상장 전(2020-04)"),
    ("2018-12-15", "2018-12 저점", "확정 저점 ② — SOL 상장 전"),
    ("2020-03-12", "2020-03 저점", "확정 저점 ③ (코로나) — SOL은 +29일(2020-04-10)부터"),
    ("2022-11-21", "2022-11 저점", "확정 저점 ④ (FTX)"),
    ("2026-06-30", "2026-06-30", "검증 대상(미확정) — ETH 자료 2026-05-23까지"),
    ("2026-11-20", "현재 2026-11", "진행 중 — 11/20 봉 미완성, ETH 자료 없음"),
]
PRE, POST = 30, 365
def seg(df, t, ohlc=True):
    w = df.loc[t - pd.Timedelta(days=PRE): t + pd.Timedelta(days=POST)]
    if ohlc:
        return [[d.strftime("%Y-%m-%d"), round(float(r.open), 4), round(float(r.high), 4), round(float(r.low), 4), round(float(r.close), 4), int(r.volume) if "volume" in r and pd.notna(r.volume) else 0] for d, r in w.iterrows()]
    return [[d.strftime("%Y-%m-%d"), round(float(r.close), 4)] for d, r in w.iterrows()]
def stats(s, t):
    st = {}
    base = s.loc[:t]
    if not len(base) or (t - base.index[-1]).days > 3: return st
    b = float(base.iloc[-1]); st["base"] = round(b, 4)
    after = s.loc[t: t + pd.Timedelta(days=POST)]
    win = s.loc[t - pd.Timedelta(days=PRE): t + pd.Timedelta(days=60)]
    if len(win): st["low"] = win.idxmin().strftime("%Y-%m-%d"); st["lag"] = int((win.idxmin() - t).days)
    for h in (30, 90, 180, 365):
        a = s.loc[:t + pd.Timedelta(days=h)]
        if len(a) and (a.index[-1] - t).days >= h - 3: st[f"r{h}"] = round(float(a.iloc[-1] / b - 1) * 100, 1)
    if len(after) > 1:
        st["maxdd"] = round(float(after.iloc[1:].min() / b - 1) * 100, 1); st["maxup"] = round(float(after.max() / b - 1) * 100, 1); st["maxup_date"] = after.idxmax().strftime("%Y-%m-%d")
    return st
out = []
for d, name, note in WINDOWS:
    t = pd.Timestamp(d)
    out.append(dict(date=d, name=name, note=note,
                    btc=seg(BT, t), eth=seg(ET, t, ETH_OHLC), sol=seg(SL, t), eth_ohlc=ETH_OHLC,
                    stats=dict(btc=stats(BT.close, t), eth=stats(ET.close, t), sol=stats(SL.close, t))))
    print(name, {k: v for k, v in out[-1]["stats"].items()})
tpl = open(f"{ROOT}/research/charts/btc_lows_eth_sol_template.html", encoding="utf-8").read()
open(f"{ROOT}/research/charts/btc_lows_eth_sol.html", "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(out, ensure_ascii=False)))
