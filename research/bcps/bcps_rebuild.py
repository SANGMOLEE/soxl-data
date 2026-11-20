# -*- coding: utf-8 -*-
"""BCPS v1.1(PC 프로젝트, 트레이딩뷰 내장 자료 2016-05-15~2026-08-05)을 저장소 자료로 다시 계산해 오늘까지 잇는다.
BCPS = mean(V, P, M, H)
  V 가치평가     median(MVRV, 200주 Mayer, 730일 편차)의 백분위
  P 가격위치     mean(365일 수익률, ATH 낙폭)의 백분위
  M 실현가 모멘텀 실현가격 30일/365일 비율의 백분위
  H 채굴경제     해시프라이스(추세제거)의 백분위 — 자료(hashprice) 없으면 빼고 3요소 평균
  각 원지표는 4년(1460일)·5년(1825일) 창 백분위의 평균.
출력: research/bcps/bcps_series.csv (date, bcps_emb 내장값, bcps_rb 재계산, bcps 합본=내장 우선·이후 재계산, band)
실행: python research/bcps/bcps_rebuild.py"""
import os, sys, numpy as np, pandas as pd
R = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(R, "..", "..", "data", "crypto")
b = pd.read_csv(os.path.join(D, "BTCUSD.csv"), parse_dates=["date"]).set_index("date").sort_index()
o = pd.read_csv(os.path.join(D, "BTC_ONCHAIN.csv"), parse_dates=["date"]).set_index("date").sort_index()
emb = pd.read_csv(os.path.join(R, "bcps_v11_embedded.csv"), parse_dates=["date"]).set_index("date")
full = pd.date_range(o.index[0], max(b.index[-1], o.index[-1]))
P = o.price.reindex(full).ffill(); yb = b.close.reindex(full); P[yb.notna()] = yb[yb.notna()]      # 2014-09 이후는 Yahoo 종가(탐지기와 같은 자료)
MV = o.mvrv.reindex(full).ffill(); RP = o.realized_price.reindex(full).ffill()
HP = o["hashprice"].reindex(full).ffill() if "hashprice" in o else pd.Series(np.nan, index=full)
if HP.notna().sum() < 2000 and "hashrate" in o:      # 채굴 수익 자료가 없으면 근사: 블록보상(BTC)×144블록×가격 ÷ 해시레이트 (수수료 제외)
    HR = o["hashrate"].reindex(full).ffill(); sub = pd.Series(50.0, index=full)
    for d, r in [("2012-11-28", 25), ("2016-07-09", 12.5), ("2020-05-11", 6.25), ("2024-04-20", 3.125)]: sub[pd.Timestamp(d):] = r
    HP = (sub * 144 * P / HR).where(HR > 0); HP_NOTE = "근사(발행량×가격÷해시레이트, 수수료 제외)"
else: HP_NOTE = "실측(채굴수익÷해시레이트)"

def pct(s, w): return s.rolling(w, min_periods=int(w * 0.6)).apply(lambda a: (a[:-1] < a[-1]).mean() * 100, raw=True)
def std(s): return (pct(s, 1460) + pct(s, 1825)) / 2
V = pd.concat([std(MV), std(P / P.rolling(1400).mean() - 1), std(P / P.rolling(730).mean() - 1)], axis=1).median(axis=1)
Pp = (std(P / P.shift(365) - 1) + std(P / P.cummax() - 1)) / 2
M = std(RP.rolling(30).mean() / RP.rolling(365).mean())
parts = {"V": V, "P": Pp, "M": M}
if HP.notna().sum() > 2000:
    lh = np.log(HP); H = std(lh - lh.rolling(365, min_periods=200).mean()); parts["H"] = H     # 추세제거: 1년 이동평균 대비
rb4 = pd.concat(parts.values(), axis=1).mean(axis=1)
rb3 = pd.concat([V, Pp, M], axis=1).mean(axis=1)
# 합본에는 3요소(V·P·M)를 쓴다. 근사 해시프라이스를 넣은 4요소는 전체 상관은 비슷하지만 저점권(<28) 오차가 더 크다(2.8 → 4.7).
# 채굴 수익 실측(RevUSD)이 들어오면 다시 비교한다. 4요소 값은 bcps_rb4 열로 같이 저장한다.
rb = rb3
def band(x): return -1 if np.isnan(x) else 0 if x < 5 else 1 if x < 15 else 2 if x < 28 else 3 if x < 42 else 4 if x < 60 else 5 if x < 74 else 6 if x < 86 else 7
NAMES = ["최극단 저점", "극저점권", "저점권", "저평가", "중립", "과열", "고점권", "극고점권"]
out = pd.DataFrame({"bcps_emb": emb.bcps.reindex(full), "bcps_rb": rb, "bcps_rb4": rb4}); out["bcps"] = out.bcps_emb.combine_first(out.bcps_rb)
for k, v in parts.items(): out[k] = v
out["band"] = out.bcps.apply(band); out = out.dropna(subset=["bcps"]); out.index.name = "date"; out.round(2).to_csv(os.path.join(R, "bcps_series.csv"))
cmp = out.dropna(subset=["bcps_emb", "bcps_rb"])
print(f"해시프라이스: {HP_NOTE if 'H' in parts else '없음'}")
cmp4 = out.dropna(subset=["bcps_emb", "bcps_rb4"]); print(f"4요소(근사 H) 참고: 상관 {cmp4.bcps_emb.corr(cmp4.bcps_rb4):.3f}, 저점권 오차 {(cmp4[cmp4.bcps_emb < 28].bcps_emb - cmp4[cmp4.bcps_emb < 28].bcps_rb4).abs().mean():.2f}")
print(f"합본 요소 V·P·M | 재계산 vs 내장: 상관 {cmp.bcps_emb.corr(cmp.bcps_rb):.3f}, 평균오차 {(cmp.bcps_emb - cmp.bcps_rb).abs().mean():.2f}, 저점권(<28) 구간 평균오차 {(cmp[cmp.bcps_emb < 28].bcps_emb - cmp[cmp.bcps_emb < 28].bcps_rb).abs().mean():.2f}")
for d in ["2018-12-14", "2020-03-12", "2022-11-21", "2025-10-06", "2026-06-30", "2026-08-05"]:
    r = out.loc[d]; print(f"  {d} 내장 {r.bcps_emb:5.1f} 재계산 {r.bcps_rb:5.1f} | " + " ".join(f"{k} {r[k]:4.1f}" for k in parts))
last = out.iloc[-1]; print(f"오늘 {out.index[-1].date()}: BCPS {last.bcps:.1f} ({NAMES[int(last.band)]}) | " + " ".join(f"{k} {last[k]:.1f}" for k in parts) + f" | MVRV {MV.iloc[-1]:.3f}")
print("8/5 이후 최저:", out.loc["2026-08-06":].bcps.min().round(1), out.loc["2026-08-06":].bcps.idxmin().date())

def what_if(px):
    """오늘 종가가 px 라면 V·P·M 백분위가 얼마인지(마지막 점만 다시 계산). M은 실현가격 기반이라 그대로 둔다."""
    def last_pct(hist, val):
        return np.mean([(hist.iloc[-w:].dropna() < val).mean() * 100 for w in (1460, 1825)])
    P2 = P.copy(); P2.iloc[-1] = px
    v = np.median([last_pct(MV, px / RP.iloc[-1]), last_pct(P / P.rolling(1400).mean() - 1, px / P2.rolling(1400).mean().iloc[-1] - 1), last_pct(P / P.rolling(730).mean() - 1, px / P2.rolling(730).mean().iloc[-1] - 1)])
    pp = (last_pct(P / P.shift(365) - 1, px / P.iloc[-366] - 1) + last_pct(P / P.cummax() - 1, px / P.cummax().iloc[-1] - 1)) / 2
    return (v + pp + M.iloc[-1]) / 3
print("오늘 종가가 이 가격이면 BCPS(3요소):", " | ".join(f"{px:,} → {what_if(px):.1f}" for px in [62000, 60500, 58500, 56000, 53500, 50000, 48000, 45000]))
