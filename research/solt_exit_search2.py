# -*- coding: utf-8 -*-
"""2차 탐색: 과열 익절 + 추적 손절 결합, BTC 기준 추적, 변동성 비례 추적.
목적함수는 IS 수익이 아니라 6개 구간(IS 1 + OOS 5)의 로그수익 평균(강건성)이며,
'한바퀴 합성'과 '25-04→26-06 실제' 두 하락 포함 구간에서 그냥 보유보다 수익·낙폭 모두 나아야 후보가 된다."""
import numpy as np, pandas as pd
from solt_exit_search import F, S2, solt, sol, btc, backtest, IS, OOS, fmt, st
atr = (sol.pct_change().abs().rolling(20).mean())            # 20일 평균 일간 변동폭
bhi = None
def make2(fam, prm):
    f = F
    if fam == "trail_sol":   x, y = prm; return (lambda p, hi, ent: sol[p] < hi * (1 - x)), (lambda p, lo: sol[p] > lo * (1 + y))
    if fam == "trail_vol":   k, y = prm; return (lambda p, hi, ent: sol[p] < hi * (1 - k * atr[p])), (lambda p, lo: sol[p] > lo * (1 + y))
    if fam == "trail_btc":   # BTC 가 자기 고점 대비 -x 면 SOLT 익절, BTC 가 저점 대비 +y 면 재매수
        x, y = prm
        hiB = {}; loB = {}
        def ex(p, hi, ent):
            hiB["v"] = max(hiB.get("v", btc[p]), btc[p]) if hiB.get("ent") == ent[0] else btc[p]; hiB["ent"] = ent[0]
            return btc[p] < hiB["v"] * (1 - x)
        def re(p, lo):
            loB["v"] = min(loB.get("v", btc[p]), btc[p]);
            ok = btc[p] > loB["v"] * (1 + y)
            if ok: loB.clear()
            return ok
        return ex, re
    if fam == "heat_trail":  # 30일 +x 과열이면 익절, 또는 고점 대비 -t 추적 손절. 재매수: 저점 대비 +y 반등 그리고 30일 상승폭 < x
        x, t, y = prm; return (lambda p, hi, ent: f.gain30[p] > x or sol[p] < hi * (1 - t)), (lambda p, lo: sol[p] > lo * (1 + y) and f.gain30[p] < x)
    if fam == "rsi_trail":   # RSI x 과열 익절 또는 추적 -t. 재매수: RSI < y2 이거나 저점 대비 +y
        x, t, y = prm; return (lambda p, hi, ent: f.rsi14[p] > x or sol[p] < hi * (1 - t)), (lambda p, lo: sol[p] > lo * (1 + y) and f.rsi14[p] < x)
    if fam == "ratio_trail": # SOL/BTC 비율 과열 +x 익절 또는 추적 -t
        x, t, y = prm; return (lambda p, hi, ent: f.ratio_dev50[p] > x or sol[p] < hi * (1 - t)), (lambda p, lo: sol[p] > lo * (1 + y) and f.ratio_dev50[p] < x)
    raise ValueError
GRID2 = {
    "trail_sol": [(x, y) for x in (0.2, 0.25, 0.3, 0.35, 0.4, 0.45) for y in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4)],
    "trail_vol": [(k, y) for k in (3, 4, 5, 6, 8) for y in (0.1, 0.15, 0.2, 0.3)],
    "trail_btc": [(x, y) for x in (0.1, 0.15, 0.2, 0.25, 0.3) for y in (0.1, 0.15, 0.2, 0.3)],
    "heat_trail": [(x, t, y) for x in (0.8, 1.0, 1.5, 9.9) for t in (0.25, 0.3, 0.35, 0.4) for y in (0.15, 0.2, 0.3)],
    "rsi_trail": [(x, t, y) for x in (80, 85, 90) for t in (0.25, 0.3, 0.35, 0.4) for y in (0.15, 0.2, 0.3)],
    "ratio_trail": [(x, t, y) for x in (0.3, 0.4, 0.6) for t in (0.25, 0.3, 0.35, 0.4) for y in (0.15, 0.2, 0.3)],
}
SEGS = {"IS 22-11→25-01": (S2, *IS), **OOS}
if __name__ == "__main__":
    rows = []
    for fam, grid in GRID2.items():
        for prm in grid:
            res = {}; ok = True
            for k, (etf, a, b) in SEGS.items():
                ex, re = make2(fam, prm); e, t = backtest(etf, a, b, ex, re); h = etf[a:b] / etf[a]
                res[k] = (e.iloc[-1] - 1, (e / e.cummax() - 1).min(), len(t))
                if k in ("B 한바퀴 합성", "25-04→26-06 실제") and not (e.iloc[-1] > h.iloc[-1] and res[k][1] > (h / h.cummax() - 1).min()): ok = False
            score = np.mean([np.log1p(v[0]) for v in res.values()])
            rows.append((fam, prm, ok, score, res))
    rows.sort(key=lambda r: (-r[2], -r[3]))
    print("조건 통과(두 하락 구간에서 보유보다 수익·낙폭 모두 우세) 규칙 수:", sum(r[2] for r in rows), "/", len(rows))
    print("\n== 강건성 점수 상위 12 (조건 통과 중)")
    print("| 규칙 | " + " | ".join(SEGS.keys()) + " | 점수 |"); print("|" + "---|" * (len(SEGS) + 2))
    for fam, prm, ok, score, res in rows[:12]:
        print(f"| {fam} {prm} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + f" | {score:.2f} |")
    print("| 그냥 보유 | " + " | ".join(fmt(etf[a:b] / etf[a]) for etf, a, b in SEGS.values()) + " | |")
    print("\n== 계열별 최고(조건 통과 중)")
    seen = set()
    for fam, prm, ok, score, res in rows:
        if not ok or fam in seen: continue
        seen.add(fam); print(f"  {fam:12s} {str(prm):20s} 점수 {score:.2f} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%}" for v in res.values()))
    best = rows[0]; fam, prm = best[0], best[1]
    print(f"\n== 최고 규칙 {fam} {prm} 거래 내역")
    for name, (etf, a, b) in SEGS.items():
        if name in ("IS 22-11→25-01", "25-04→26-06 실제", "26-06→지금 실제"):
            ex, re = make2(fam, prm); e, t = backtest(etf, a, b, ex, re); print(f"  [{name}] " + fmt(e))
            for x in t: print(f"     {x[0]} → {x[1]}: {x[2]:+.0%}")
