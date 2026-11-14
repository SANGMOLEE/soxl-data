# -*- coding: utf-8 -*-
"""4차: 정량 사다리(X배 익절 → D% 하락·R% 반등 재매수, M% 놓친 상승 복귀, T일 시간 복귀) + 보유분 손절.
손절 종류: fixed(진입가 대비 -S%), btc(BTC 고점 대비 -10%), ma200(SOL 200일선 5일 연속 이탈).
손절 후에도 같은 대기 규칙(손절가 기준 D/R/M/T)으로 재매수."""
import numpy as np, pandas as pd
from solt_exit_search import S2, solt, sol, btc, IS, OOS, fmt
ma200 = sol.rolling(200).mean()
def ladder_stop(etf, a, b, X, D, R, M, T, stop):
    seg = etf[a:b]; idx = seg.index; r = seg.pct_change().fillna(0)
    units, cash, val = 1.0, 0.0, 1.0; eq = []; trades = []; state = "in"; ent_p = sol[idx[0]]; ent_d = idx[0]; ent_val = 1.0
    exit_p = low = t_exit = None; pend = None; bhi = btc[idx[0]]; below = 0
    for i in range(len(idx)):
        d = idx[i]; p = idx[i - 1] if i else None
        if i: val *= (1 + r.iloc[i])
        if pend:
            if pend in ("exit", "stop"): cash += units * val; trades.append((ent_d.date(), d.date(), val / ent_val - 1, pend)); units = 0.0; state = "out"; exit_p = sol[p]; low = sol[p]; t_exit = d
            elif pend == "enter": units = cash / val; cash = 0.0; state = "in"; ent_p = sol[p]; ent_d = d; ent_val = val; bhi = btc[p]; below = 0
            pend = None
        eq.append(cash + units * val)
        if p is None: continue
        if state == "in":
            bhi = max(bhi, btc[p]); below = below + 1 if sol[p] < ma200[p] else 0
            if sol[p] / ent_p >= X: pend = "exit"
            elif stop[0] == "fixed" and sol[p] <= ent_p * (1 - stop[1]): pend = "stop"
            elif stop[0] == "btc" and btc[p] <= bhi * (1 - stop[1]): pend = "stop"
            elif stop[0] == "ma200" and below >= 5: pend = "stop"
        else:
            low = min(low, sol[p]); days = (d - t_exit).days; dipped = low <= exit_p * (1 - D)
            if dipped and sol[p] >= low * (1 + R): pend = "enter"
            elif M is not None and sol[p] >= exit_p * (1 + M): pend = "enter"
            elif T is not None and days >= T and not dipped: pend = "enter"
    if units > 0: trades.append((ent_d.date(), "보유중", val / ent_val - 1, ""))
    return pd.Series(eq, index=idx), trades
SEGS = {"IS 22-11→25-01": (S2, *IS), **OOS}
STOPS = [("none", 0), ("fixed", 0.25), ("fixed", 0.35), ("btc", 0.10), ("btc", 0.15), ("ma200", 5)]
GRID = [(X, D, R, 0.3, 60, s) for X in (1.5, 2, 3) for D in (0.3, 0.4, 0.5) for R in (0.0, 0.2, 0.3) for s in STOPS]
lab = lambda g: f"X{g[0]} D{int(g[1]*100)} R{int(g[2]*100)} M30 T60 + 손절 {g[5][0]}{'' if g[5][0] in ('none','ma200') else int(g[5][1]*100)}"
if __name__ == "__main__":
    rows = []
    for g in GRID:
        res = {}; ok = True
        for k, (etf, a, b) in SEGS.items():
            e, t = ladder_stop(etf, a, b, *g); h = etf[a:b] / etf[a]
            res[k] = (e.iloc[-1] - 1, (e / e.cummax() - 1).min(), len(t))
            if k in ("B 한바퀴 합성", "25-04→26-06 실제") and not (e.iloc[-1] > h.iloc[-1] and res[k][1] > (h / h.cummax() - 1).min()): ok = False
        rows.append((g, ok, np.mean([np.log1p(v[0]) for v in res.values()]), res))
    hdr = "| 규칙 | " + " | ".join(SEGS.keys()) + " | 점수 |"
    print(f"규칙 {len(rows)}, 두 하락 구간 통과 {sum(r[1] for r in rows)}")
    rows_r = sorted([r for r in rows if r[1]], key=lambda r: -r[2])
    print("\n== 강건성 상위 12"); print(hdr); print("|" + "---|" * (len(SEGS) + 2))
    for g, ok, sc, res in rows_r[:12]: print(f"| {lab(g)} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + f" | {sc:.2f} |")
    print("| 그냥 보유 | " + " | ".join(fmt(etf[a:b] / etf[a]) for etf, a, b in SEGS.values()) + " | |")
    print("\n== 전 구간 최대낙폭 -60% 이내 중 강건성 상위 6"); print(hdr); print("|" + "---|" * (len(SEGS) + 2))
    for g, ok, sc, res in [r for r in rows_r if all(v[1] > -0.6 for v in r[3].values())][:6]: print(f"| {lab(g)} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + f" | {sc:.2f} |")
    print("\n== 손절 종류별 최고(강건성)")
    seen = set()
    for g, ok, sc, res in rows_r:
        key = g[5]
        if key in seen: continue
        seen.add(key); print(f"  {lab(g):40s} 점수 {sc:.2f} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%}" for v in res.values()))
    best = rows_r[0][0]; print(f"\n== 1위 {lab(best)} 거래 내역")
    for name in ("IS 22-11→25-01", "B 한바퀴 합성", "25-04→26-06 실제", "26-06→지금 실제"):
        etf, a, b = SEGS[name]; e, t = ladder_stop(etf, a, b, *best); print(f"  [{name}] {fmt(e)}")
        for x in t: print(f"     {x[0]} → {x[1]}: {x[2]:+.0%} {x[3]}  (매수일 SOL ${sol.asof(pd.Timestamp(x[0])):,.1f}, BTC ${btc.asof(pd.Timestamp(x[0])):,.0f})")
