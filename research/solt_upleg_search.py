# -*- coding: utf-8 -*-
"""저점→고점 구간(상승기)만 보유한다는 전제에서 수익을 최대화하는 규칙 탐색.
엔진: 매일 전일 정보로 목표 비중 w(SOLT, SOL현물, BITU, 현금)를 정하고 당일 종가에 체결. 회전율 1당 0.1% 비용.
상승 구간 4개: U1 2020-05-11→2021-11-06(합성), U2 2022-11-21→2025-01-18(합성, 탐색용), U3 2025-04-08→2025-09-18(실제), U4 2026-06-08→2026-09-25(실제).
강건성 점수 = 4구간 로그수익 평균. 보유(SOLT 100%) 대비 승수도 같이 본다."""
import numpy as np, pandas as pd, itertools
from solt_exit_search import sol, btc, solt, S2
B2 = (1 + np.clip(2 * btc.pct_change().fillna(0), -0.999, None) - 0.0095 / 365).cumprod()
bitu = pd.read_csv(__file__.rsplit("/", 2)[0] + "/data/crypto/BITU.csv", parse_dates=["date"]).sort_values("date").set_index("date")["adj_close"].astype(float)
COST = 0.001
# 특징량 (전일 기준으로 shift 해서 사용)
F = pd.DataFrame({"sol": sol, "btc": btc}).dropna()
r = F.sol.pct_change()
F["ma10"] = F.sol.rolling(10).mean(); F["ma20"] = F.sol.rolling(20).mean(); F["ma50"] = F.sol.rolling(50).mean()
F["z20"] = (F.sol - F.ma20) / F.sol.rolling(20).std()
F["vol20"] = r.rolling(20).std() * np.sqrt(365); F["volpct"] = F.vol20.rolling(250, min_periods=60).rank(pct=True)
F["g7"] = F.sol / F.sol.shift(7) - 1; F["g30"] = F.sol / F.sol.shift(30) - 1
F["ratio"] = F.sol / F.btc; F["rmom20"] = F.ratio / F.ratio.shift(20) - 1
F["dd20"] = F.sol / F.sol.rolling(20).max() - 1   # 20일 고점 대비 낙폭
F["ma20_up"] = F.ma20 > F.ma20.shift(5)
SEGS = {"U1 2020-21 합성": ("syn", "2020-05-11", "2021-11-06"), "U2 2022-25 합성": ("syn", "2022-11-21", "2025-01-18"),
        "U3 2025 실제": ("real", "2025-04-08", "2025-09-18"), "U4 2026 실제": ("real", "2026-06-08", "2026-09-25")}
def assets(kind, a, b):
    s2 = solt if kind == "real" else S2; b2 = bitu if kind == "real" else B2
    A = pd.DataFrame({"SOLT": s2, "SOL": sol, "BITU": b2, "CASH": 1.0}).dropna()[a:b]
    return A / A.iloc[0]
def run(kind, a, b, wfun, state=None):
    """wfun(i, dates, F, prev_w, st) -> dict of weights (sum<=1). i 는 체결일 인덱스, 정보는 dates[i-1] 까지."""
    A = assets(kind, a, b); R = A.pct_change().fillna(0); dates = A.index
    w = {"SOLT": 1.0}; eq = 1.0; eqs = [1.0]; turn = 0.0; st = {} if state is None else dict(state); st["ent"] = {"SOLT": sol[dates[0]]}
    for i in range(1, len(dates)):
        # 하루 수익
        eq *= 1 + sum(w.get(k, 0) * R[k].iloc[i] for k in A.columns)
        # 비중 갱신(전일 정보)
        nw = wfun(i, dates, F, w, st)
        tv = sum(abs(nw.get(k, 0) - w.get(k, 0)) for k in A.columns) / 2
        eq *= (1 - COST * tv * 2); turn += tv; w = nw; eqs.append(eq)
    e = pd.Series(eqs, index=dates); return e, turn
def score(e): return e.iloc[-1] - 1, (e / e.cummax() - 1).min()
# ── 전략 계열 ──
def hold(i, d, F, w, st): return {"SOLT": 1.0}
def mk_constmix(target, band):
    """변동성 수확: SOLT 비중을 target 으로 유지, 밴드 벗어나면 리밸런싱."""
    def f(i, d, F, w, st):
        cur = w.get("SOLT", 0); cash = w.get("CASH", 0)
        # 가치 변동 후 실제 비중은 엔진이 추적하지 않으므로 전일 수익로 근사
        rs = F.sol.pct_change().get(d[i - 1], 0) * 2
        v_s = cur * (1 + rs); v_c = cash; tot = v_s + v_c if v_s + v_c > 0 else 1
        ws = v_s / tot
        if abs(ws - target) > band: return {"SOLT": target, "CASH": 1 - target}
        return {"SOLT": ws, "CASH": 1 - ws}
    return f
def mk_volswitch(pct_hi, pct_lo):
    """변동성 조절: 변동성 백분위가 높으면 현물, 낮으면 SOLT."""
    def f(i, d, F, w, st):
        p = F.volpct.get(d[i - 1], np.nan)
        if p >= pct_hi: return {"SOL": 1.0}
        if p <= pct_lo: return {"SOLT": 1.0}
        return w
    return f
def mk_zband(z_hi, z_lo, park):
    """밴드 스윙: z20 > z_hi 면 익절(park=현물 또는 현금), z20 < z_lo 면 SOLT 복귀."""
    def f(i, d, F, w, st):
        z = F.z20.get(d[i - 1], np.nan)
        if z > z_hi: return {park: 1.0}
        if z < z_lo: return {"SOLT": 1.0}
        return w
    return f
def mk_parabolic(g, days, park):
    """포물선 매도: 7일 상승 g 이상이면 익절, days 일 뒤 복귀(그 전에 20일 고점 대비 -15% 면 즉시 복귀)."""
    def f(i, d, F, w, st):
        if w.get("SOLT", 0) == 1.0:
            if F.g7.get(d[i - 1], 0) > g: st["t"] = i; return {park: 1.0}
            return w
        if i - st.get("t", i) >= days or F.dd20.get(d[i - 1], 0) < -0.15: return {"SOLT": 1.0}
        return w
    return f
def mk_ladder(X, D, R, M, T, park):
    """정량 사다리(4차와 동일 논리)."""
    def f(i, d, F, w, st):
        p = d[i - 1]; px = F.sol[p]
        if w.get("SOLT", 0) == 1.0:
            if px / st["ent"]["SOLT"] >= X: st["xp"] = px; st["lo"] = px; st["t"] = i; return {park: 1.0}
            return w
        st["lo"] = min(st.get("lo", px), px); dipped = st["lo"] <= st["xp"] * (1 - D)
        if (dipped and px >= st["lo"] * (1 + R)) or px >= st["xp"] * (1 + M) or (i - st["t"] >= T and not dipped):
            st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
        return w
    return f
def mk_trendre(X, D, park):
    """X배 익절 후, D% 하락 뒤 10일선 위로 복귀하는 날 재매수(추세 재개 확인)."""
    def f(i, d, F, w, st):
        p = d[i - 1]; px = F.sol[p]
        if w.get("SOLT", 0) == 1.0:
            if px / st["ent"]["SOLT"] >= X: st["xp"] = px; st["lo"] = px; st["below"] = False; return {park: 1.0}
            return w
        st["lo"] = min(st.get("lo", px), px)
        if px < F.ma10[p]: st["below"] = True
        if st["lo"] <= st["xp"] * (1 - D) and st.get("below") and px > F.ma10[p]: st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
        if px >= st["xp"] * 1.3: st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
        return w
    return f
def mk_rotate(k):
    """상대강도 로테이션: SOL/BTC 20일 모멘텀 > k 면 SOLT, 아니면 BITU."""
    def f(i, d, F, w, st):
        m = F.rmom20.get(d[i - 1], 0); return {"SOLT": 1.0} if m > k else {"BITU": 1.0}
    return f
def mk_diplev(D, X):
    """눌림목 증폭: 평소 현물, 20일 고점 대비 -D 이하로 눌리면 SOLT, 진입가 대비 X배면 현물로 복귀."""
    def f(i, d, F, w, st):
        p = d[i - 1]; px = F.sol[p]
        if w.get("SOLT", 0) == 1.0:
            if px / st["ent"]["SOLT"] >= X: return {"SOL": 1.0}
            return w
        if F.dd20[p] <= -D: st["ent"]["SOLT"] = px; return {"SOLT": 1.0}
        return w
    return f
def mk_trendfilter(park):
    """추세 필터: 20일선 위·20일선 상승이면 SOLT, 아니면 park."""
    def f(i, d, F, w, st):
        p = d[i - 1]; return {"SOLT": 1.0} if (F.sol[p] > F.ma20[p] and F.ma20_up[p]) else {park: 1.0}
    return f
FAM = {}
FAM["보유"] = [("SOLT 100%", hold)]
FAM["변동성수확(리밸런싱)"] = [(f"목표{int(t*100)}% 밴드{int(b*100)}", mk_constmix(t, b)) for t in (0.6, 0.7, 0.8, 0.9) for b in (0.05, 0.1, 0.15)]
FAM["변동성조절(SOLT↔현물)"] = [(f"고{int(h*100)}/저{int(l*100)}", mk_volswitch(h, l)) for h in (0.7, 0.8, 0.9) for l in (0.3, 0.5, 0.6)]
FAM["밴드스윙(z20)"] = [(f"z>{zh} 익절→{pk}, z<{zl} 복귀", mk_zband(zh, zl, pk)) for zh in (1.5, 2.0, 2.5) for zl in (-0.5, 0.0, 0.5) for pk in ("CASH", "SOL")]
FAM["포물선매도"] = [(f"7일+{int(g*100)}% 매도→{pk}, {dy}일 복귀", mk_parabolic(g, dy, pk)) for g in (0.3, 0.5, 0.8) for dy in (5, 10, 20) for pk in ("CASH", "SOL")]
FAM["정량사다리"] = [(f"X{X} D{int(D*100)} R{int(R*100)} M30 T{T}→{pk}", mk_ladder(X, D, R, 0.3, T, pk)) for X in (1.3, 1.5, 2.0) for D in (0.15, 0.2, 0.3) for R in (0.0, 0.1) for T in (30, 60) for pk in ("CASH", "SOL")]
FAM["추세재개재매수"] = [(f"X{X} D{int(D*100)} 10일선복귀→{pk}", mk_trendre(X, D, pk)) for X in (1.3, 1.5, 2.0) for D in (0.15, 0.2, 0.3) for pk in ("CASH", "SOL")]
FAM["BITU↔SOLT 로테이션"] = [(f"비율모멘텀>{k}", mk_rotate(k)) for k in (-0.1, -0.05, 0.0, 0.05)]
FAM["눌림목증폭(현물↔SOLT)"] = [(f"-{int(D*100)}% 눌림 SOLT, X{X} 현물", mk_diplev(D, X)) for D in (0.15, 0.2, 0.3) for X in (1.3, 1.5, 2.0)]
FAM["추세필터(20일선)"] = [(f"이탈 시 {pk}", mk_trendfilter(pk)) for pk in ("CASH", "SOL")]
if __name__ == "__main__":
    hold_res = {k: score(run(*v, hold)[0]) for k, v in SEGS.items()}
    rows = []
    for fam, lst in FAM.items():
        for name, fn in lst:
            res = {};
            for k, v in SEGS.items(): e, turn = run(*v, fn); res[k] = score(e) + (turn,)
            sc = np.mean([np.log1p(res[k][0]) for k in SEGS]); mult = np.exp(np.mean([np.log1p(res[k][0]) - np.log1p(hold_res[k][0]) for k in SEGS]))
            wins = sum(res[k][0] > hold_res[k][0] for k in SEGS); rows.append((fam, name, sc, mult, wins, res))
    rows.sort(key=lambda x: -x[2])
    hdr = "| 계열 | 규칙 | " + " | ".join(SEGS) + " | 보유대비 기하평균 | 승 |"; sep = "|" + "---|" * (len(SEGS) + 4)
    def line(x): fam, name, sc, mult, wins, res = x; return f"| {fam} | {name} | " + " | ".join(f"{res[k][0]:+,.0%}/{res[k][1]:.0%}" for k in SEGS) + f" | x{mult:.2f} | {wins}/4 |"
    print("== 상승 구간 4개 강건성 상위 15"); print(hdr); print(sep)
    for x in rows[:15]: print(line(x))
    print("\n== 계열별 최고"); print(hdr); print(sep)
    seen = set()
    for x in rows:
        if x[0] in seen: continue
        seen.add(x[0]); print(line(x))
    print("\n== 4구간 모두 보유를 이긴 규칙 중 상위"); print(hdr); print(sep)
    for x in [x for x in rows if x[4] == 4][:10]: print(line(x))
