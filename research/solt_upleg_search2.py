# -*- coding: utf-8 -*-
"""상승기 탐색 2차: 자산가치 추적 엔진(리밸런싱 정확), 로테이션 세분화, 로테이션+추세필터·+사다리 결합."""
import numpy as np, pandas as pd
from solt_upleg_search import F, SEGS, assets, COST, score, hold, mk_ladder, mk_parabolic
for n in (10, 20, 30, 40): F[f"rmom{n}"] = F.ratio / F.ratio.shift(n) - 1
for n in (10, 30): F[f"ma{n}"] = F.sol.rolling(n).mean()
F["bma20"] = F.btc.rolling(20).mean()
def run(kind, a, b, wfun):
    A = assets(kind, a, b); R = A.pct_change().fillna(0); dates = A.index
    v = {k: 0.0 for k in A.columns}; v["SOLT"] = 1.0; eqs = [1.0]; turn = 0.0; st = {"ent": {"SOLT": F.sol[dates[0]]}}
    for i in range(1, len(dates)):
        for k in v: v[k] *= 1 + R[k].iloc[i]
        tot = sum(v.values()); w = {k: v[k] / tot for k in v}
        nw = wfun(i, dates, F, w, st)
        if nw is not None:
            tv = sum(abs(nw.get(k, 0) - w[k]) for k in v) / 2; tot *= 1 - COST * tv * 2; turn += tv
            v = {k: tot * nw.get(k, 0) for k in v}
        eqs.append(sum(v.values()))
    return pd.Series(eqs, index=dates), turn
def mk_constmix(t, band):
    def f(i, d, F, w, st): return {"SOLT": t, "CASH": 1 - t} if abs(w["SOLT"] - t) > band else None
    return f
def mk_rot(n, k, park="BITU"):
    def f(i, d, F, w, st): return {"SOLT": 1.0} if F[f"rmom{n}"].get(d[i - 1], 0) > k else {park: 1.0}
    return f
def mk_rot_trend(n, k, ma, park_weak="BITU", park_down="SOL"):
    """SOL/BTC 모멘텀으로 SOLT/BITU 택하되, 택한 자산의 기초가 ma일선 아래면 park_down(현물)."""
    def f(i, d, F, w, st):
        p = d[i - 1]
        if F[f"rmom{n}"][p] > k: return {"SOLT": 1.0} if F.sol[p] > F[f"ma{ma}"][p] else {park_down: 1.0}
        return {park_weak: 1.0} if F.btc[p] > F.bma20[p] else {park_down: 1.0}
    return f
def mk_rot_ladder(n, k, X, D):
    """로테이션 + SOLT 보유 중 X배 익절(→BITU), 익절가 대비 D% 하락 뒤 복귀 또는 +30% 돌파 복귀 또는 60일 시간 복귀."""
    def f(i, d, F, w, st):
        p = d[i - 1]; px = F.sol[p]
        if F[f"rmom{n}"][p] <= k: st.pop("xp", None); st["ent"]["SOLT"] = px; return {"BITU": 1.0}
        if "xp" in st:
            st["lo"] = min(st["lo"], px); dipped = st["lo"] <= st["xp"] * (1 - D)
            if dipped or px >= st["xp"] * 1.3 or i - st["t"] >= 60: st.pop("xp"); st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
            return {"BITU": 1.0}
        if w.get("SOLT", 0) < 0.99: st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
        if px / st["ent"]["SOLT"] >= X: st["xp"] = px; st["lo"] = px; st["t"] = i; return {"BITU": 1.0}
        return None
    return f
FAM = {"보유": [("SOLT 100%", hold)]}
FAM["변동성수확(정확)"] = [(f"목표{int(t*100)}% 밴드{int(b*100)}", mk_constmix(t, b)) for t in (0.5, 0.7, 0.8, 0.9) for b in (0.05, 0.1, 0.2)]
FAM["로테이션"] = [(f"{n}일 비율모멘텀>{k}→{pk}", mk_rot(n, k, pk)) for n in (10, 20, 30, 40) for k in (-0.1, -0.05, 0.0, 0.05) for pk in ("BITU", "SOL")]
FAM["로테이션+추세"] = [(f"{n}일>{k}, {ma}일선 이탈 시 현물", mk_rot_trend(n, k, ma)) for n in (20, 30) for k in (-0.1, -0.05, 0.0) for ma in (10, 20, 30)]
FAM["로테이션+사다리"] = [(f"{n}일>{k}, X{X} D{int(D*100)}", mk_rot_ladder(n, k, X, D)) for n in (20, 30) for k in (-0.1, -0.05) for X in (1.5, 2.0) for D in (0.2, 0.3)]
if __name__ == "__main__":
    hold_res = {k: score(run(*v, hold)[0]) for k, v in SEGS.items()}
    rows = []
    for fam, lst in FAM.items():
        for name, fn in lst:
            res = {}
            for k, v in SEGS.items(): e, turn = run(*v, fn); res[k] = score(e) + (turn,)
            sc = np.mean([np.log1p(res[k][0]) for k in SEGS]); mult = np.exp(np.mean([np.log1p(res[k][0]) - np.log1p(hold_res[k][0]) for k in SEGS]))
            wins = sum(res[k][0] > hold_res[k][0] for k in SEGS); rows.append((fam, name, sc, mult, wins, res))
    rows.sort(key=lambda x: -x[3])
    hdr = "| 계열 | 규칙 | " + " | ".join(SEGS) + " | 보유대비 | 승 | 회전 |"; sep = "|" + "---|" * (len(SEGS) + 5)
    def line(x): fam, name, sc, mult, wins, res = x; return f"| {fam} | {name} | " + " | ".join(f"{res[k][0]:+,.0%}/{res[k][1]:.0%}" for k in SEGS) + f" | x{mult:.2f} | {wins}/4 | {res['U2 2022-25 합성'][2]:.0f} |"
    print("== 보유 대비 기하평균 상위 15"); print(hdr); print(sep)
    for x in rows[:15]: print(line(x))
    print("\n== 계열별 최고"); print(hdr); print(sep); seen = set()
    for x in rows:
        if x[0] in seen: continue
        seen.add(x[0]); print(line(x))
    print("\n== 4구간 모두 보유 이김"); print(hdr); print(sep)
    for x in [x for x in rows if x[4] == 4][:8]: print(line(x))
    print("\n== 실제 구간(U3·U4) 둘 다 이기고 U2 도 이긴 규칙"); print(hdr); print(sep)
    for x in [x for x in rows if all(x[5][k][0] > hold_res[k][0] for k in ("U2 2022-25 합성", "U3 2025 실제", "U4 2026 실제"))][:8]: print(line(x))
