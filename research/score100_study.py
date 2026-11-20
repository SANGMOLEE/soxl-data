# -*- coding: utf-8 -*-
"""100점 저점 점수 — 설계·백테스트 (2026-11-20)
구간 점수(느린 층 백분위 평균) × 타이밍 점수(빠른 층 백분위 평균) → 0~100.
평가: 과거 저점 당일 점수, ±30일 안 최고점이 저점 당일인가, 임계 첫 돌파의 선행/지연, 오경보, 확인 신호 지연.
실행: python research/score100_study.py
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score100_features import *

F = load(); P = pct_rank(F, FAST + SLOW)
lows = local_lows(F); cyc = [pd.Timestamp(x) for x in CYCLE_LOWS]
c = F.close

def composite(zone_cols, time_cols, wz=0.5, mode="mean"):
    Z = P[zone_cols].mean(axis=1); T = P[time_cols].mean(axis=1)
    S = wz * Z + (1 - wz) * T if mode == "mean" else np.sqrt(Z.clip(0) * T.clip(0))
    return S, Z, T

def evaluate(S, name, thr=None, verbose=True):
    """저점 당일 점수 / ±30일 창 안 최고점 날짜와 저점의 차이 / 임계 첫 돌파의 지연 / 오경보."""
    rows = []
    for t in lows:
        if pd.isna(S.get(t)): continue
        w = S.loc[t - pd.Timedelta(days=30): t + pd.Timedelta(days=30)]
        peakday = (w.idxmax() - t).days
        pre = S.loc[t - pd.Timedelta(days=60): t]
        rows.append(dict(low=t, cyc=t in cyc, s=S[t], peak=w.max(), lag=peakday, rank=(w > S[t]).sum() + 1, premax=pre.max()))
    R = pd.DataFrame(rows).set_index("low")
    Rc = R[R.cyc]
    out = dict(name=name, cyc_s=Rc.s.round(0).tolist(), cyc_lag=Rc.lag.tolist(), cyc_rank=Rc["rank"].tolist(),
               all_hit0=f"{(R.lag == 0).mean():.0%}", all_pm2=f"{(R.lag.abs() <= 2).mean():.0%}", all_pm7=f"{(R.lag.abs() <= 7).mean():.0%}", all_s_med=round(R.s.median()))
    if thr is not None:
        near = pd.Series(False, index=S.index)
        for t in lows: near.loc[t - pd.Timedelta(days=7): t + pd.Timedelta(days=7)] = True
        fp = ((S >= thr) & ~near).loc["2015":"2025"]
        eps = 0; last = None
        for d in fp.index[fp]:
            if last is None or (d - last).days > 10: eps += 1
            last = d
        out["fp_days/yr"] = round(fp.sum() / 11, 1); out["fp_episodes"] = eps
        # 사이클 저점에서 임계 첫 돌파일(저점 -60일 이후)과 저점의 차이, 그때 가격의 저점 대비 거리
        first = []
        for t in cyc:
            seg = S.loc[t - pd.Timedelta(days=60): t + pd.Timedelta(days=30)]
            hit = seg[seg >= thr]
            first.append((int((hit.index[0] - t).days), f"{c[hit.index[0]] / c[t] - 1:+.0%}") if len(hit) else (None, None))
        out["cyc_first_cross(lag,price)"] = first
    if verbose: print(out)
    return R, out

print("== 자료:", F.index[0].date(), "~", F.index[-1].date(), "| 국소 저점", len(lows), "| 사이클 저점", len(cyc))
print("\n== 1. 개별 층")
Zcols = ["mayer", "w200", "ddath", "mvrv", "rp", "rsi_w"]
Tcols = ["rsi14", "dd30", "dd90", "bbz", "ma50d", "r7"]
Zs = P[Zcols].mean(axis=1); Ts = P[Tcols].mean(axis=1)
evaluate(Zs, "구간(Z) 6지표 평균", thr=85)
evaluate(Ts, "타이밍(T) 6지표 평균", thr=85)
print("\n== 2. 결합 방식 비교 (임계 80)")
cands = {}
for wz in (0.3, 0.5, 0.7):
    S, Z, T = composite(Zcols, Tcols, wz); cands[f"mean wz={wz}"] = S; evaluate(S, f"산술평균 wz={wz}", thr=80)
S, Z, T = composite(Zcols, Tcols, mode="geo"); cands["geo"] = S; evaluate(S, "기하평균(구간×타이밍)", thr=80)
print("\n== 3. 피처 추가/제거 민감도 (산술 0.5, 임계 80)")
for add in (["volr"], ["rsi7"], ["r3"], ["bcps"], ["days_ath"]):
    zc = Zcols + [a for a in add if a in SLOW]; tc = Tcols + [a for a in add if a in FAST]
    S, _, _ = composite(zc, tc, 0.5); evaluate(S, f"+{add}", thr=80)
for drop in ("rsi_w", "w200", "r7", "dd90"):
    zc = [x for x in Zcols if x != drop]; tc = [x for x in Tcols if x != drop]
    S, _, _ = composite(zc, tc, 0.5); evaluate(S, f"-{drop}", thr=80)

print("\n== 4. 기준 모형(산술 0.5)의 사이클 저점 전후 점수 경로 (저점 -10 ~ +10일)")
S, Z, T = composite(Zcols, Tcols, 0.5)
for t in cyc:
    seg = S.loc[t - pd.Timedelta(days=10): t + pd.Timedelta(days=10)]
    print(t.date(), " ".join(("  ." if pd.isna(x) else f"{int(round(x)):3d}") for x in seg.values), "| 저점일 점수", S[t], "Z", Z[t], "T", T[t])

print("\n== 5. 확인 신호 지연 (저점 뒤 며칠째에 '저점 지났다'를 알 수 있나) — 사이클 저점")
def confirm_lag(t, rule):
    seg = F.loc[t: t + pd.Timedelta(days=30)]
    for i in range(1, len(seg)):
        d = seg.index[i]
        if rule == "close>2일고점" and seg.close.iloc[i] > seg.high.iloc[i - 2: i].max(): return i, f"{seg.close.iloc[i] / c[t] - 1:+.1%}"
        if rule == "2일연속상승" and i >= 2 and seg.close.iloc[i] > seg.close.iloc[i - 1] > seg.close.iloc[i - 2]: return i, f"{seg.close.iloc[i] / c[t] - 1:+.1%}"
        if rule == "점수-15&3일상승" and S[d] <= S.loc[t: d].max() - 15 and seg.close.iloc[i] > seg.close.iloc[max(0, i - 3)]: return i, f"{seg.close.iloc[i] / c[t] - 1:+.1%}"
        if rule == "저점+5%" and seg.close.iloc[i] >= c[t] * 1.05: return i, f"{seg.close.iloc[i] / c[t] - 1:+.1%}"
    return None, None
for rule in ("close>2일고점", "2일연속상승", "점수-15&3일상승", "저점+5%"):
    print(f"  {rule:14s}", [confirm_lag(t, rule) for t in cyc])
print("  같은 규칙이 '가짜 저점'(2018-02-05, 2018-06-28, 2022-06-18, 2026-02-05)에서도 켜지나:")
for rule in ("close>2일고점", "2일연속상승"):
    print(f"  {rule:14s}", [confirm_lag(pd.Timestamp(x), rule) for x in ("2018-02-05", "2018-06-28", "2022-06-18", "2026-02-05")])

print("\n== 6. 교차 검증: 사이클 저점 하나를 빼고 임계를 고른 뒤(나머지 저점의 최소 저점일 점수-5) 뺀 저점에 적용")
for t in [u for u in cyc if pd.notna(S.get(u))]:
    others = [u for u in cyc if u != t and pd.notna(S.get(u))]
    thr = min(S[u] for u in others if pd.notna(S[u])) - 5
    seg = S.loc[t - pd.Timedelta(days=60): t + pd.Timedelta(days=30)]; hit = seg[seg >= thr]
    print(f"  제외 {t.date()}: 임계 {thr:.0f} → 첫 돌파 {(hit.index[0]-t).days if len(hit) else None}일, 저점일 점수 {S[t]:.0f}, 저점일이 ±30일 최고점? {S.loc[t-pd.Timedelta(days=30):t+pd.Timedelta(days=30)].idxmax().date()==t.date()}")

print("\n== 6-2. 가짜·중간 저점에서의 점수 (같은 모형) — 구간 점수가 가르는가")
for x in ("2018-02-05","2018-06-28","2019-12-17","2021-07-20","2022-01-22","2022-06-18","2025-04-08","2026-02-05"):
    t=pd.Timestamp(x); print(f"  {x}: 점수 {S[t]:.0f} Z {Z[t]:.0f} T {T[t]:.0f} | 고점후 {int(F.at[t,'days_ath'])}일, ATH대비 {F.at[t,'ddath']:+.0%}, MVRV {F.at[t,'mvrv']:.2f}")
print("\n== 7. 현재")
x = F.index[-1]; print(x.date(), "점수", round(S[x]), "구간Z", round(Z[x]), "타이밍T", round(T[x]), "| 최근 30일 최고", round(S.iloc[-30:].max()), S.iloc[-30:].idxmax().date())
print("   Z 구성:", {k: round(P.at[x, k]) for k in Zcols}, "\n   T 구성:", {k: round(P.at[x, k]) for k in Tcols})
S.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score100_series.csv"), header=["score100"])
