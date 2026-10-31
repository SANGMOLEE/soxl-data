# -*- coding: utf-8 -*-
"""SOLT형 2x: 중간 폭락 전 익절·되돌림 재매수 규칙 탐색.
탐색(in-sample): 사이클 B 2022-11-21 → 2025-01-18 (합성 2x)
검증(out-of-sample): 사이클 A 2020-05-11 → 2021-11-06 (합성), 실제 SOLT 2025-04-08 → 2025-09-18, 2026-06-08 → 2026-10-30,
                  그리고 한 바퀴 2022-11-21 → 2026-06-06 (고점을 모른다고 가정).
체결: 신호는 당일 종가로 확정, 다음날 종가 체결(선행편향 제거). 재진입도 같은 방식.
"""
import os, itertools, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(__file__), "..", "data", "crypto")
ld = lambda n, c="close": pd.read_csv(os.path.join(D, n + ".csv"), parse_dates=["date"]).sort_values("date").set_index("date")[c].astype(float)
btc, sol, solt = ld("BTCUSD"), ld("SOLUSD"), ld("SOLT", "adj_close")
S2 = (1 + np.clip(2 * sol.pct_change().fillna(0), -0.999, None) - 0.0195 / 365).cumprod()

def rsi(s, n=14):
    d = s.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)
F = pd.DataFrame({"sol": sol, "btc": btc}).dropna()
F["ma20"] = F.sol.rolling(20).mean(); F["ma50"] = F.sol.rolling(50).mean(); F["ma100"] = F.sol.rolling(100).mean()
F["dev50"] = F.sol / F.ma50 - 1; F["dev20"] = F.sol / F.ma20 - 1
F["rsi14"] = rsi(F.sol, 14); F["rsiw"] = rsi(F.sol.resample("W").last(), 14).reindex(F.index, method="ffill")
F["ratio"] = F.sol / F.btc; F["ratio_dev50"] = F.ratio / F.ratio.rolling(50).mean() - 1
F["mayer"] = F.btc / F.btc.rolling(200).mean()
F["gain30"] = F.sol / F.sol.shift(30) - 1; F["gain14"] = F.sol / F.sol.shift(14) - 1

def backtest(etf, a, b, exit_fn, reentry_fn, log=False):
    seg = etf[a:b]; idx = seg.index; r = seg.pct_change().fillna(0)
    pos = 1; eq = [1.0]; trades = []; ent = (idx[0], 1.0); run_hi = sol[idx[0]]; run_lo = None; pend = None
    for i in range(1, len(idx)):
        d = idx[i]; p = idx[i - 1]
        eq.append(eq[-1] * (1 + r.iloc[i]) if pos else eq[-1])
        # 전일 종가 기준 신호 → 오늘 종가 체결
        if pend == "exit": pos = 0; trades.append((ent[0].date(), d.date(), eq[-1] / ent[1] - 1)); run_lo = sol[p]; pend = None
        elif pend == "enter": pos = 1; ent = (d, eq[-1]); run_hi = sol[p]; pend = None
        if pos:
            run_hi = max(run_hi, sol[p])
            if exit_fn(p, run_hi, ent): pend = "exit"
        else:
            run_lo = min(run_lo, sol[p]) if run_lo is not None else sol[p]
            if reentry_fn(p, run_lo): pend = "enter"
    if pos: trades.append((ent[0].date(), "보유중", eq[-1] / ent[1] - 1))
    e = pd.Series(eq, index=idx); return e, trades

def make(family, prm):
    f = F
    if family == "trail":        # 고점 대비 -x% 이탈 시 익절, 저점 대비 +y% 반등 시 재매수
        x, y = prm; return (lambda p, hi, ent: sol[p] < hi * (1 - x)), (lambda p, lo: sol[p] > lo * (1 + y))
    if family == "dev50":        # 50일선 이격 +x 이상이면 익절, 이격 y 이하로 식으면 재매수
        x, y = prm; return (lambda p, hi, ent: f.dev50[p] > x), (lambda p, lo: f.dev50[p] < y)
    if family == "dev20":
        x, y = prm; return (lambda p, hi, ent: f.dev20[p] > x), (lambda p, lo: f.dev20[p] < y)
    if family == "rsi":          # 일간 RSI x 이상 익절, y 이하 재매수
        x, y = prm; return (lambda p, hi, ent: f.rsi14[p] > x), (lambda p, lo: f.rsi14[p] < y)
    if family == "rsiw":         # 주간 RSI
        x, y = prm; return (lambda p, hi, ent: f.rsiw[p] > x), (lambda p, lo: f.rsiw[p] < y)
    if family == "gain30":       # 30일 상승폭 +x 이상 익절, 저점 대비 +y 반등 재매수
        x, y = prm; return (lambda p, hi, ent: f.gain30[p] > x), (lambda p, lo: sol[p] > lo * (1 + y))
    if family == "ratio":        # SOL/BTC 비율 50일 이격 +x 익절, y 이하 재매수
        x, y = prm; return (lambda p, hi, ent: f.ratio_dev50[p] > x), (lambda p, lo: f.ratio_dev50[p] < y)
    if family == "mayer":        # BTC 메이어배수 x 이상 익절, y 이하 재매수
        x, y = prm; return (lambda p, hi, ent: f.mayer[p] > x), (lambda p, lo: f.mayer[p] < y)
    if family == "dev50_trail":  # 이격 과열 또는 추적손절 중 먼저 오는 것, 재매수는 반등 y
        x, t, y = prm; return (lambda p, hi, ent: f.dev50[p] > x or sol[p] < hi * (1 - t)), (lambda p, lo: sol[p] > lo * (1 + y) and f.dev50[p] < x)
    raise ValueError

GRID = {
    "trail": [(x, y) for x in (0.15, 0.2, 0.25, 0.3, 0.35) for y in (0.1, 0.15, 0.2, 0.3)],
    "dev50": [(x, y) for x in (0.3, 0.4, 0.5, 0.6, 0.8) for y in (-0.1, 0.0, 0.1, 0.2)],
    "dev20": [(x, y) for x in (0.2, 0.3, 0.4, 0.5) for y in (-0.1, 0.0, 0.05)],
    "rsi": [(x, y) for x in (75, 80, 85, 90) for y in (35, 45, 55)],
    "rsiw": [(x, y) for x in (75, 80, 85, 90) for y in (45, 55, 65)],
    "gain30": [(x, y) for x in (0.5, 0.8, 1.0, 1.5) for y in (0.1, 0.2, 0.3)],
    "ratio": [(x, y) for x in (0.2, 0.3, 0.4, 0.6) for y in (-0.1, 0.0, 0.1)],
    "mayer": [(x, y) for x in (1.5, 1.8, 2.0, 2.4) for y in (1.0, 1.2, 1.4)],
    "dev50_trail": [(x, t, y) for x in (0.5, 0.6, 0.8) for t in (0.2, 0.25, 0.3) for y in (0.15, 0.2, 0.3)],
}
IS = ("2022-11-21", "2025-01-18")
OOS = {"A 2020-21 합성": (S2, "2020-05-11", "2021-11-06"), "B 한바퀴 합성": (S2, "2022-11-21", "2026-06-06"),
       "25-04→25-09 실제": (solt, "2025-04-08", "2025-09-18"), "25-04→26-06 실제": (solt, "2025-04-08", "2026-06-08"), "26-06→지금 실제": (solt, "2026-06-08", "2026-10-30")}
st = lambda e: (e.iloc[-1] - 1, (e / e.cummax() - 1).min())
fmt = lambda e: f"{e.iloc[-1]-1:+,.0%}/{(e/e.cummax()-1).min():.0%}"

if __name__ == "__main__":
    hold = S2[IS[0]:IS[1]]; print("기준(그냥 보유, IS):", fmt(hold / hold.iloc[0]))
    results = []
    for fam, grid in GRID.items():
        for prm in grid:
            ex, re = make(fam, prm); e, t = backtest(S2, *IS, ex, re)
            ret, dd = st(e); results.append((fam, prm, ret, dd, len(t)))
    R = pd.DataFrame(results, columns=["family", "prm", "ret", "dd", "n"])
    print("\n== 계열별 최고 (IS 사이클 B 상승기, 수익 기준)")
    best = R.sort_values("ret", ascending=False).groupby("family").head(1).sort_values("ret", ascending=False)
    for _, row in best.iterrows(): print(f"  {row.family:12s} {str(row.prm):22s} 수익 {row.ret:+,.0%}  낙폭 {row.dd:.0%}  거래 {row.n}")
    print("\n== 상위 8개 규칙의 검증(OOS) 성적")
    top = R.sort_values("ret", ascending=False).head(8)
    print("| 규칙 | IS 22-11→25-01 | " + " | ".join(OOS.keys()) + " |"); print("|" + "---|" * (len(OOS) + 2))
    for _, row in top.iterrows():
        ex, re = make(row.family, row.prm); cells = []
        for k, (etf, a, b) in OOS.items(): e, t = backtest(etf, a, b, ex, re); cells.append(f"{fmt(e)} ({len(t)})")
        print(f"| {row.family} {row.prm} | {row.ret:+,.0%}/{row.dd:.0%} ({row.n}) | " + " | ".join(cells) + " |")
    print("| 그냥 보유 | " + fmt(hold / hold.iloc[0]) + " | " + " | ".join(fmt(etf[a:b] / etf[a]) for etf, a, b in OOS.values()) + " |")
    # 강건성: 계열별로 IS·OOS 모두 보유를 이기는 규칙 수
    print("\n== 강건성: '한바퀴 합성'과 '25-04→26-06 실제' 둘 다 그냥 보유보다 수익·낙폭 모두 나은 규칙 (계열별 개수/전체)")
    for fam, grid in GRID.items():
        ok = 0
        for prm in grid:
            ex, re = make(fam, prm); good = True
            for k in ("B 한바퀴 합성", "25-04→26-06 실제"):
                etf, a, b = OOS[k]; e, _ = backtest(etf, a, b, ex, re); h = etf[a:b] / etf[a]
                if not (e.iloc[-1] > h.iloc[-1] and (e / e.cummax() - 1).min() > (h / h.cummax() - 1).min()): good = False
            ok += good
        print(f"  {fam:12s} {ok}/{len(grid)}")
    # 최고 규칙 거래 내역
    fam, prm = top.iloc[0].family, top.iloc[0].prm; ex, re = make(fam, prm)
    print(f"\n== 최고 규칙 {fam} {prm} 거래 내역 (IS)")
    for x in backtest(S2, *IS, ex, re)[1]: print(f"   {x[0]} → {x[1]}: {x[2]:+.0%}")
    print(f"== 같은 규칙, 실제 SOLT 2025-04-08 → 2026-10-30")
    for x in backtest(solt, "2025-04-08", "2026-10-30", ex, re)[1]: print(f"   {x[0]} → {x[1]}: {x[2]:+.0%}")
