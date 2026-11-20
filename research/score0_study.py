# -*- coding: utf-8 -*-
"""bv1 — 저점 거리 점수: 확정된 네 사이클 저점에서 0이 되도록 앵커를 고정한 모형 (2026-11-20, 재작성)
각 지표 x(낮을수록 저점형으로 정렬): 앵커 a = 확정 저점 넷(2015-01·2018-12·2020-03·2022-11) 당일 값 중 가장 덜 극단적인 값.
2026-06-30은 확정 저점이 아니므로 앵커에 넣지 않고 검증 대상으로만 본다. (첫 판은 2026-06-30을 넷에 넣는 오류가 있었고 폐기함.)
  거리_i = clip((x − a) / (중립_i − a), 0, 1) × 100,  중립_i = 2015~2026 전 기간 중앙값.
  점수 = 구간(5지표 평균) 50% + 타이밍(6지표 평균) 50%.  네 저점에서는 정의상 모든 지표가 앵커 이하 → 0.
평가: 가짜 저점 점수, 0 또는 ≤5가 찍힌 날(저점 ±7일 밖), 저점 하나 뺀 교차 검증, 현재값과 '0이 되는 가격'.
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score100_features import load, ORIENT, local_lows
F = load(); c = F.close
LOWS4 = [pd.Timestamp(x) for x in ("2015-01-14", "2018-12-15", "2020-03-12", "2022-11-21")]  # 확정 저점만
TEST = pd.Timestamp("2026-06-30")  # 미확정 — 검증 대상
ZC = ["mayer", "w200", "ddath", "mvrv", "rsi_w"]; TC = ["rsi14", "dd30", "dd90", "bbz", "ma50d", "r7"]
COLS = ZC + TC
LABEL = dict(mayer="200일선 이격", w200="200주선 이격", ddath="ATH 낙폭", mvrv="MVRV", rsi_w="주간 RSI", rsi14="일간 RSI14", dd30="30일 낙폭", dd90="90일 낙폭", bbz="볼린저 z", ma50d="50일선 이격", r7="7일 수익")

def fit(lows):
    X = F[COLS]
    anchor = {k: min(X.at[t, k] * ORIENT[k] for t in lows if pd.notna(X.at[t, k])) for k in COLS}   # 정렬값(클수록 저점형)의 최소 = 가장 덜 극단
    neutral = {k: (X[k] * ORIENT[k]).loc["2015":].median() for k in COLS}
    return anchor, neutral

def score(anchor, neutral):
    D = pd.DataFrame(index=F.index)
    for k in COLS:
        x = F[k] * ORIENT[k]; D[k] = ((anchor[k] - x) / (anchor[k] - neutral[k])).clip(0, 1) * 100
    Z = D[ZC].mean(axis=1); T = D[TC].mean(axis=1); S = 0.5 * Z + 0.5 * T
    return S, Z, T, D

anchor, neutral = fit(LOWS4); S, Z, T, D = score(anchor, neutral)
print("== 1. 앵커(네 저점 중 가장 덜 극단적인 값)와 중립값 (원단위) ==")
for k in COLS:
    a = anchor[k] * ORIENT[k]; n = neutral[k] * ORIENT[k]
    vals = {t.strftime('%y-%m'): F.at[t, k] for t in LOWS4}
    f = (lambda v: f"{v:+.0%}") if k in ("mayer", "w200", "ddath", "dd30", "dd90", "ma50d", "r7") else (lambda v: f"{v:.2f}") if k in ("mvrv", "bbz") else (lambda v: f"{v:.0f}")
    print(f"  {LABEL[k]:9s} 앵커 {f(a):>7s} | 중립 {f(n):>7s} | 저점값 " + ", ".join(f"{d} {f(v)}" for d, v in vals.items()))

print("\n== 2. 확정 저점 넷(정의상 0), 2026-06-30(검증 대상), 가짜 저점의 점수 ==")
for x in ("2015-01-14", "2018-12-15", "2020-03-12", "2022-11-21", "2026-06-30", "2015-08-24", "2018-02-05", "2018-06-28", "2019-12-17", "2022-06-18", "2026-02-05"):
    t = pd.Timestamp(x); over = [LABEL[k] + f" {D.at[t,k]:.0f}" for k in COLS if D.at[t, k] > 0]
    print(f"  {x}: 점수 {S[t]:5.1f} (Z {Z[t]:4.1f} T {T[t]:4.1f}) | 0이 아닌 지표: {', '.join(over) if over else '없음'}")

print("\n== 3. 저점 ±7일 밖에서 점수가 낮게 찍힌 날 (2015~2026) ==")
near = pd.Series(False, index=F.index)
for t in local_lows(F): near.loc[t - pd.Timedelta(days=7): t + pd.Timedelta(days=7)] = True
for th in (0, 3, 5, 10):
    m = (S <= th) & ~near & S.notna(); days = F.index[m]
    eps = []; last = None
    for d in days:
        if last is None or (d - last).days > 10: eps.append(d)
        last = d
    print(f"  점수 ≤{th:2d}: {int(m.sum()):4d}일, 사건 {len(eps)}건 {[e.strftime('%y-%m-%d') for e in eps][:12]}")

print("\n== 4. 교차 검증: 저점 하나를 빼고 셋으로 앵커를 잡은 뒤 뺀 저점의 점수 ==")
for t in LOWS4:
    a2, n2 = fit([u for u in LOWS4 if u != t]); S2, Z2, T2, D2 = score(a2, n2)
    over = [LABEL[k] + f" {D2.at[t,k]:.0f}" for k in COLS if D2.at[t, k] > 0]
    print(f"  제외 {t.date()}: 그 저점 점수 {S2[t]:.1f} (Z {Z2[t]:.1f} T {T2[t]:.1f}) | 0이 아닌 지표: {', '.join(over) if over else '없음'} | 그 저점 ±30일 최저 점수일 {S2.loc[t-pd.Timedelta(days=30):t+pd.Timedelta(days=30)].idxmin().date()}")

print("\n== 5. 사이클 저점 전후 경로 (−10 … 저점 … +10) — 2026-06-30 포함 ==")
for t in LOWS4 + [TEST]:
    seg = S.loc[t - pd.Timedelta(days=10): t + pd.Timedelta(days=10)]
    print(" ", t.date(), " ".join(f"{int(round(v)):3d}" for v in seg.values))

print("\n== 5-1. 2026-06-30 검증: 2026-05-15~08-15 구간 최저 점수일 ==")
w = S.loc["2026-05-15":"2026-08-15"]; print(f"  최저 {w.min():.1f} ({w.idxmin().date()}), 6/30 당일 {S[TEST]:.1f}, 6/30 뒤 10일 최저 {S.loc[TEST:TEST+pd.Timedelta(days=10)].min():.1f}")
print("  6/30 당일 0이 아닌 지표:", {LABEL[k]: round(D.at[TEST, k]) for k in COLS if D.at[TEST, k] > 0})

print("\n== 6. 현재 ==")
x = F.index[-1]; print(f"  {x.date()} BTC {c[x]:,.0f} | 점수 {S[x]:.1f} = 구간 {Z[x]:.1f} · 타이밍 {T[x]:.1f}")
print("  지표별 거리(0=앵커 도달):", {LABEL[k]: round(D.at[x, k]) for k in COLS})
# 각 지표가 오늘 앵커에 닿는 가격(가격 파생 지표만, 다른 조건 고정)
ma200 = F.close.rolling(200).mean()[x]; ma1400 = F.close.rolling(1400).mean()[x]; ma50 = F.close.rolling(50).mean()[x]
hi30 = F.close.rolling(30).max()[x]; hi90 = F.close.rolling(90).max()[x]; ath = F.ath[x]; rp = c[x] / (F.mvrv[x])  # 실현가격
prices = {"200일선 이격": ma200 * (1 + anchor["mayer"] * ORIENT["mayer"]), "200주선 이격": ma1400 * (1 + anchor["w200"] * ORIENT["w200"]), "ATH 낙폭": ath * (1 + anchor["ddath"] * ORIENT["ddath"]),
          "MVRV": rp * anchor["mvrv"] * ORIENT["mvrv"], "30일 낙폭": hi30 * (1 + anchor["dd30"] * ORIENT["dd30"]), "90일 낙폭": hi90 * (1 + anchor["dd90"] * ORIENT["dd90"]), "50일선 이격": ma50 * (1 + anchor["ma50d"] * ORIENT["ma50d"]), "7일 수익": c[x - pd.Timedelta(days=7)] * (1 + anchor["r7"] * ORIENT["r7"])}
print("  오늘 기준, 지표가 앵커(0)에 닿는 가격:", {k: f"{v:,.0f}" for k, v in prices.items()})
print("  → 모든 가격 지표가 0이 되려면(가장 낮은 값):", f"{min(prices.values()):,.0f}", "| 구간 지표만:", f"{min(prices[k] for k in ('200일선 이격','200주선 이격','ATH 낙폭','MVRV')):,.0f}")
print("  최근 30일:", " ".join(f"{int(round(v))}" for v in S.iloc[-30:]))
S.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score0_series.csv"), header=["score0"])
