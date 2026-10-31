# -*- coding: utf-8 -*-
"""가상 SOLT(2022-10 상장 가정) · 비트코인 · 사이클 점수 3단 차트 HTML 생성.
- 달력: 미국 거래일(SPY.csv). 주말 변동은 다음 거래일 봉에 반영.
- 가상 SOLT: 상장 전(~2025-03-20) 거래일 간 솔라나 수익×2 − 연 20% 일할. OHLC 는 그날 솔라나 OHLC 의 전일 대비 변동을 2배로 환산.
  상장 후: 실제 SOLT OHLC (조정종가 기준 총수익으로 연결). 전체를 오늘 실제 가격($46.70)에 맞춰 스케일.
- 사이클 점수: 직전 확정 저점=1, 고점=100 로그 눈금. 2022-11-21 전은 A(2020-03-12 저점, 2021-11-08 고점), 이후 B(2022-11-21, 2025-10-06).
  새 눈금 C(2026-06-30 저점, 가정 고점 $210k)는 2026-06-30 이후 점선.
출력: research/charts/solt_btc_cycle_chart.html
"""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); D = os.path.join(ROOT, "data", "crypto")
ld = lambda n: pd.read_csv(os.path.join(D, n + ".csv"), parse_dates=["date"]).set_index("date").sort_index()
btc, sol, solt = ld("BTCUSD"), ld("SOLUSD"), ld("SOLT")
cal7 = pd.date_range("2022-09-01", btc.index[-1])
btc7 = btc.reindex(cal7).ffill(); sol7 = sol.reindex(cal7).ffill()
us = pd.DatetimeIndex(pd.read_csv(os.path.join(ROOT, "data", "prices", "SPY.csv"), parse_dates=["date"])["date"])
us = us[(us >= "2022-10-03") & (us <= cal7[-1])]
# SPY 달력이 최신 거래일보다 뒤처지면 평일로 이어 붙인다(미국 휴일은 무시)
if us[-1] < cal7[-1]:
    us = us.append(pd.bdate_range(us[-1] + pd.Timedelta(days=1), cal7[-1]))
LIST = pd.Timestamp("2025-03-20"); DRAG = 0.20
# ── 가상 SOLT ──
rows = []; prev_close_sol = sol7["close"].asof(us[0] - pd.Timedelta(days=1)); v = 100.0; prev_t = us[0] - pd.Timedelta(days=1)
for t in us:
    if t < LIST or t == LIST:
        o, h, l, c = sol7.loc[t, ["open", "high", "low", "close"]]
        days = (t - prev_t).days
        f = lambda x: v * (1 + 2 * (x / prev_close_sol - 1))
        oc, hc, lc = f(o), f(h), f(l); cc = v * (1 + 2 * (c / prev_close_sol - 1) - DRAG * days / 365)
        rows.append((t, oc, max(hc, oc, cc), min(lc, oc, cc), cc)); v = cc; prev_close_sol = c; prev_t = t
    else:
        if t not in solt.index: continue
        r = solt.loc[t]; rp = solt.loc[:t].iloc[-2] if len(solt.loc[:t]) > 1 else r
        ret = r["adj_close"] / rp["adj_close"] - 1; cc = v * (1 + ret); k = cc / r["close"]
        rows.append((t, r["open"] * k, r["high"] * k, r["low"] * k, cc)); v = cc; prev_t = t
S = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).set_index("t")
S = S * (solt["close"].iloc[-1] / S["c"].iloc[-1])   # 오늘 실제 가격 기준으로 스케일
# ── BTC OHLC (미국 거래일, 주말 포함 범위) ──
B = []
for i, t in enumerate(S.index):
    a = (S.index[i - 1] + pd.Timedelta(days=1)) if i else t
    seg = btc7.loc[a:t]; B.append((t, seg["open"].iloc[0], seg["high"].max(), seg["low"].min(), seg["close"].iloc[-1]))
B = pd.DataFrame(B, columns=["t", "o", "h", "l", "c"]).set_index("t")
ma100 = btc7["close"].rolling(100).mean().reindex(B.index); ma200 = btc7["close"].rolling(200).mean().reindex(B.index)
# ── 사이클 점수 ──
A_lo, A_hi = btc.loc["2020-03-12", "close"], btc.loc["2021-11-08", "close"]
B_lo, B_hi = btc.loc["2022-11-21", "close"], btc.loc["2025-10-06", "close"]
C_lo, C_hi = btc.loc["2026-06-30", "close"], 210000.0
def pos(p, lo, hi): return 1 + 99 * np.log(p / lo) / np.log(hi / lo)
score, scoreC = [], []
for t, c in B["c"].items():
    lo, hi = (A_lo, A_hi) if t < pd.Timestamp("2022-11-21") else (B_lo, B_hi)
    score.append((t, float(pos(c, lo, hi))))
    if t >= pd.Timestamp("2026-06-30"): scoreC.append((t, float(pos(c, C_lo, C_hi))))
ts = lambda t: t.strftime("%Y-%m-%d")
data = {
    "solt": [dict(time=ts(t), open=round(r.o, 2), high=round(r.h, 2), low=round(r.l, 2), close=round(r.c, 2)) for t, r in S.iterrows()],
    "btc": [dict(time=ts(t), open=round(r.o), high=round(r.h), low=round(r.l), close=round(r.c)) for t, r in B.iterrows()],
    "ma100": [dict(time=ts(t), value=round(v)) for t, v in ma100.dropna().items()],
    "ma200": [dict(time=ts(t), value=round(v)) for t, v in ma200.dropna().items()],
    "score": [dict(time=ts(t), value=round(v, 1)) for t, v in score],
    "scoreC": [dict(time=ts(t), value=round(v, 1)) for t, v in scoreC],
    "listing": ts(LIST),
    "events": [dict(time="2022-11-21", text="사이클 저점 $15,787", pos="belowBar"), dict(time="2025-10-06", text="사이클 고점 $124,753", pos="aboveBar"),
               dict(time="2026-06-30", text="2026 저점 $58,559", pos="belowBar"), dict(time="2024-04-19", text="반감기", pos="belowBar")],
    "meta": dict(built=ts(cal7[-1]), solt_start=round(S["c"].iloc[0], 2), solt_last=round(S["c"].iloc[-1], 2), solt_max=round(S["c"].max(), 2), solt_max_t=ts(S["c"].idxmax()),
                 btc_last=round(B["c"].iloc[-1]), score_last=round(score[-1][1], 1), scoreC_last=round(scoreC[-1][1], 1) if scoreC else None),
}
tpl = open(os.path.join(HERE, "solt_chart_template.html"), encoding="utf-8").read()
html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
out = os.path.join(HERE, "charts", "solt_btc_cycle_chart.html"); open(out, "w", encoding="utf-8").write(html)
print("written", out, len(html) // 1024, "KB"); print(data["meta"])
