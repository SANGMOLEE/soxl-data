# -*- coding: utf-8 -*-
"""3차 탐색: 정량 사다리 규칙.
  진입(사이클 저점) → SOL 현물이 진입가 대비 X배 되면 SOLT 익절(분할 가능)
  → 익절가 대비 D% 하락을 기다림 → 하락 저점에서 R% 반등 확인 시 재매수(R=0 이면 D% 하락 즉시 매수)
  → 재매수가 대비 다시 X배 목표. 익절 후 하락 없이 익절가 대비 +M% 를 넘으면 '놓친 상승' 복귀 매수(M=None 이면 복귀 없음).
  → 익절 후 T일 안에 D% 하락이 없으면 시간 복귀(T=None 이면 없음).
체결: 전일 종가 신호 → 당일 종가 체결. 평가는 SOLT(2x) 경로, 신호는 SOL 현물 배수.
"""
import numpy as np, pandas as pd, itertools
from solt_exit_search import S2, solt, sol, btc, IS, OOS, fmt

def ladder(etf, a, b, X, D, R, M=None, T=None, tranches=1, X2=None):
    """tranches=2 이면 X 에 절반, X2 에 나머지 익절."""
    seg = etf[a:b]; idx = seg.index; r = seg.pct_change().fillna(0)
    units = 1.0; cash = 0.0; eq = []; trades = []
    ent_p = sol[idx[0]]; ent_d = idx[0]; state = "in"; exit_p = None; low = None; t_exit = None; pend = None; sold_half = False
    val = 1.0  # 보유분 가치(단위당)
    for i in range(len(idx)):
        d = idx[i]; p = idx[i - 1] if i else None
        if i: val *= (1 + r.iloc[i])
        # 전일 신호 체결
        if pend:
            if pend == "exit_all": cash += units * val; trades.append((ent_d.date(), d.date(), val / ent_val - 1)); units = 0.0; state = "out"; exit_p = sol[p]; low = sol[p]; t_exit = d; sold_half = False
            elif pend == "exit_half": cash += 0.5 * units * val; units *= 0.5; sold_half = True
            elif pend == "enter": units = cash / val if val > 0 else 0; cash = 0.0; state = "in"; ent_p = sol[p]; ent_d = d; ent_val = val; sold_half = False
            pend = None
        if i == 0: ent_val = val
        eq.append(cash + units * val)
        if p is None: continue
        mult = sol[p] / ent_p
        if state == "in":
            if tranches == 2 and not sold_half and mult >= X: pend = "exit_half"
            elif tranches == 2 and sold_half and mult >= X2: pend = "exit_all"
            elif tranches == 1 and mult >= X: pend = "exit_all"
        else:
            low = min(low, sol[p]); days = (d - t_exit).days
            dipped = low <= exit_p * (1 - D)
            if dipped and sol[p] >= low * (1 + R): pend = "enter"
            elif M is not None and sol[p] >= exit_p * (1 + M): pend = "enter"
            elif T is not None and days >= T and not dipped: pend = "enter"
    if units > 0: trades.append((ent_d.date(), "보유중", val / ent_val - 1))
    return pd.Series(eq, index=idx), trades

GRID = [(X, D, R, M, T, tr, X2) for X in (1.5, 2, 2.5, 3, 4, 5, 7) for D in (0.2, 0.3, 0.4, 0.5) for R in (0.0, 0.1, 0.2, 0.3)
        for M in (None, 0.3) for T in (None, 60) for tr, X2 in ((1, None), (2, None))]
GRID = [g if g[5] == 1 else (g[0], g[1], g[2], g[3], g[4], 2, g[0] * 2) for g in GRID]
SEGS = {"IS 22-11→25-01": (S2, *IS), **OOS}
label = lambda g: f"X{g[0]} D{int(g[1]*100)} R{int(g[2]*100)}" + (f" M{int(g[3]*100)}" if g[3] else "") + (f" T{g[4]}" if g[4] else "") + (f" 분할(X2={g[6]})" if g[5] == 2 else "")
if __name__ == "__main__":
    rows = []
    for g in GRID:
        res = {}; ok = True
        for k, (etf, a, b) in SEGS.items():
            e, t = ladder(etf, a, b, g[0], g[1], g[2], g[3], g[4], g[5], g[6]); h = etf[a:b] / etf[a]
            res[k] = (e.iloc[-1] - 1, (e / e.cummax() - 1).min(), len(t))
            if k in ("B 한바퀴 합성", "25-04→26-06 실제") and not (e.iloc[-1] > h.iloc[-1] and res[k][1] > (h / h.cummax() - 1).min()): ok = False
        score = np.mean([np.log1p(v[0]) for v in res.values()]); rows.append((g, ok, score, res))
    print(f"규칙 수 {len(rows)}, 두 하락 구간 통과 {sum(r[1] for r in rows)}")
    rows_is = sorted(rows, key=lambda r: -r[3]["IS 22-11→25-01"][0])
    print("\n== IS(22-11→25-01 상승기) 수익 상위 6 — 그리고 그 규칙의 검증 성적")
    hdr = "| 규칙 | " + " | ".join(SEGS.keys()) + " |"; print(hdr); print("|" + "---|" * (len(SEGS) + 1))
    for g, ok, score, res in rows_is[:6]: print(f"| {label(g)} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + " |")
    print("\n== 강건성(6구간 로그수익 평균) 상위 12, 두 하락 구간 통과 조건")
    rows_r = sorted([r for r in rows if r[1]], key=lambda r: -r[2]); print(hdr); print("|" + "---|" * (len(SEGS) + 1))
    for g, ok, score, res in rows_r[:12]: print(f"| {label(g)} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + f" | {score:.2f}")
    print("| 그냥 보유 | " + " | ".join(fmt(etf[a:b] / etf[a]) for etf, a, b in SEGS.values()) + " |")
    print("\n== 최대낙폭 -50% 이내(전 구간)로 제한했을 때 강건성 상위 5")
    rows_dd = [r for r in rows_r if all(v[1] > -0.5 for v in r[3].values())]
    for g, ok, score, res in rows_dd[:5]: print(f"| {label(g)} | " + " | ".join(f"{v[0]:+,.0%}/{v[1]:.0%} ({v[2]})" for v in res.values()) + f" | {score:.2f}")
    best = rows_r[0][0]
    print(f"\n== 강건성 1위 {label(best)} 거래 내역")
    for name in ("IS 22-11→25-01", "B 한바퀴 합성", "25-04→26-06 실제", "26-06→지금 실제"):
        etf, a, b = SEGS[name]; e, t = ladder(etf, a, b, best[0], best[1], best[2], best[3], best[4], best[5], best[6])
        print(f"  [{name}] {fmt(e)}")
        for x in t: print(f"     {x[0]} → {x[1]}: {x[2]:+.0%}  (매수일 SOL ${sol.asof(pd.Timestamp(x[0])):,.1f})")
