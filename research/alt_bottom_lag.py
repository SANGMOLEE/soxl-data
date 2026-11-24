# -*- coding: utf-8 -*-
"""BTC 저점 = 알트(SOL) 저점인가? 실측 검증 (Yahoo 일봉 종가).
1) BTC 주요 저점마다 알트별 최종 저점 시차·추가 하락·BTC 대비 비율 흐름
2) SOL/BTC 비율의 저점 시차와 BTC 저점 뒤 SOL 상대 성적
3) 합성 SOLT(일일 2배, 연 20% 비용)를 BTC 저점에 사면 vs SOL 저점에 사면 vs BITU로 사서 로테이션
실행: python research/alt_bottom_lag.py"""
import os, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto")
def load(n):
    s = pd.read_csv(os.path.join(D, f"{n}.csv"), parse_dates=["date"]).set_index("date").close.sort_index()
    return s.reindex(pd.date_range(s.index[0], s.index[-1])).ffill()
BTC = load("BTCUSD"); ALTS = {n: load(n) for n in ["ETHUSD", "LTCUSD", "XRPUSD", "BNBUSD", "ADAUSD", "DOGEUSD", "LINKUSD", "SOLUSD", "AVAXUSD", "DOTUSD"]}
BOTTOMS = ["2018-12-15", "2020-03-12", "2022-11-21", "2026-06-30", "2026-11-20"]
PRE, POST = 60, 150

print("== 1. BTC 저점(종가) 기준 ±창(-60~+150일) 안 알트 최종 저점")
print("   시차 = 알트 저점일 - BTC 저점일(일). 추가하락 = BTC 저점일 알트가격 → 알트 저점 가격. 비율저점 = 알트/BTC 비율의 최저일 시차")
summary = []
for b in BOTTOMS:
    b = pd.Timestamp(b); print(f"\n  BTC 저점 {b.date()} ${BTC[b]:,.0f}")
    for n, s in ALTS.items():
        if b - pd.Timedelta(days=PRE) < s.index[0] or b not in s.index: continue
        w = s[b - pd.Timedelta(days=PRE): min(b + pd.Timedelta(days=POST), s.index[-1])]; lo = w.idxmin(); lag = (lo - b).days
        r = (s / BTC).dropna(); rw = r[b - pd.Timedelta(days=PRE): min(b + pd.Timedelta(days=POST), r.index[-1])]; rlag = (rw.idxmin() - b).days
        extra = s[lo] / s[b] - 1; rel = {k: (s[min(b + pd.Timedelta(days=k), s.index[-1])] / s[b]) / (BTC[min(b + pd.Timedelta(days=k), BTC.index[-1])] / BTC[b]) - 1 for k in (30, 60, 90)}
        pend = " (진행 중)" if (s.index[-1] - b).days < POST else ""
        print(f"    {n:8s} 저점 {lo.date()} 시차 {lag:+4d}일 추가하락 {extra:+6.1%} | 비율저점 시차 {rlag:+4d}일 | BTC 대비 +30/60/90일 {rel[30]:+.0%}/{rel[60]:+.0%}/{rel[90]:+.0%}{pend}")
        if not pend: summary.append(dict(bottom=b.date(), alt=n, lag=lag, extra=extra, rlag=rlag, rel30=rel[30], rel90=rel[90]))
S = pd.DataFrame(summary)
print("\n  요약(확정 사례만): 사례", len(S), "| 시차 중앙값", int(S.lag.median()), "일, 시차 ≤7일(동시) 비율", f"{(S.lag.abs() <= 7).mean():.0%}", "| 추가하락 중앙값", f"{S.extra.median():+.1%}", "최악", f"{S.extra.min():+.1%}")
print("  알트가 BTC 저점 뒤에 더 낮은 저점을 만든 비율(시차>7일·추가하락<-5%):", f"{((S.lag > 7) & (S.extra < -0.05)).mean():.0%}", "| 비율저점 시차 중앙값", int(S.rlag.median()), "일 | BTC 대비 +30일 중앙값", f"{S.rel30.median():+.0%}", "+90일", f"{S.rel90.median():+.0%}")

print("\n== 2. SOL 상세 (BTC 저점 → SOL 저점 → SOL/BTC 비율 저점)")
SOL = ALTS["SOLUSD"]; R = (SOL / BTC).dropna()
for b in BOTTOMS[2:]:
    b = pd.Timestamp(b); w = SOL[b - pd.Timedelta(days=PRE): b + pd.Timedelta(days=POST)]; lo = w.idxmin(); rw = R[b - pd.Timedelta(days=PRE): b + pd.Timedelta(days=POST)]
    print(f"  BTC {b.date()}: SOL 당일 ${SOL[b]:.1f} → SOL 저점 {lo.date()} ${w.min():.1f} ({w.min()/SOL[b]-1:+.0%}, {(lo-b).days:+d}일) | 비율 저점 {rw.idxmin().date()} ({(rw.idxmin()-b).days:+d}일), 비율 당일→저점 {rw.min()/R[b]-1:+.0%}")
print("  최근 10일 SOL / SOL÷BTC(×1000):", " ".join(f"{d.strftime('%m/%d')} {SOL[d]:.0f}/{R[d]*1000:.2f}" for d in SOL.index[-10:]))

print("\n== 3. 합성 SOLT(일 2배, 연 -20%)·BITU(일 2배, 연 -16%)를 언제 사느냐")
def lev(s, k=2.0, drag=0.20):
    r = s.pct_change().fillna(0) * k - drag / 365; return (1 + r).cumprod()
def path(s, start, k, drag):
    seg = s[start:]; return lev(seg, k, drag)
for b in ["2022-11-21", "2026-06-30"]:
    b = pd.Timestamp(b); w = SOL[b - pd.Timedelta(days=PRE): b + pd.Timedelta(days=POST)]; sl = w.idxmin()
    solt_b = path(SOL, b, 2, 0.20); solt_s = path(SOL, sl, 2, 0.20); bitu_b = path(BTC, b, 2, 0.16)
    lo_d = solt_b.idxmin(); print(f"\n  BTC 저점 {b.date()} 매수 SOLT: 최저 {solt_b.min():.2f}배 ({lo_d.date()}, +{(lo_d-b).days}일) | SOL 저점 {sl.date()} (+{(sl-b).days}일)")
    for k in (90, 180, 365):
        e = b + pd.Timedelta(days=k)
        if e > SOL.index[-1]: print(f"    +{k}일: 자료 끝"); continue
        print(f"    +{k}일: SOLT@BTC저점 {solt_b[e]:.2f}배 | SOLT@SOL저점 {solt_s[e] if e >= sl else float('nan'):.2f}배 | BITU@BTC저점 {bitu_b[e]:.2f}배 | SOL 현물@BTC저점 {SOL[e]/SOL[b]:.2f}배")
    # 로테이션: BTC 저점에 BITU, SOL/BTC 20일 모멘텀 > 0 되는 첫날 SOLT로 교체
    mom = R / R.shift(20) - 1; sw = mom[b:].index[mom[b:] > 0][0]
    comb = pd.concat([bitu_b[:sw], bitu_b[sw] * path(SOL, sw, 2, 0.20)[1:]]); 
    def at(ser, d): return ser[d] if d in ser.index else float("nan")
    print(f"    로테이션(BITU→SOLT 교체일 {sw.date()}, +{(sw-b).days}일): " + ", ".join(f"+{k}일 {at(comb, b+pd.Timedelta(days=k)):.2f}배" for k in (90, 180, 365)))

print("\n== 4. SOL 자체 저점 확인 규칙 비교 (BTC 저점 알람 뒤 SOLT 진입 시점을 정하는 규칙)")
print("   각 규칙의 첫 발동일(BTC 저점 이후), SOL 저점 대비 진입가, 진입 뒤 SOLT 최저, +365일 또는 자료 끝 SOLT 배수")
R20 = R.rolling(20).mean(); S20 = SOL.rolling(20).mean(); S50 = SOL.rolling(50).mean(); H10 = SOL.rolling(10).max().shift(1)
RULES = {
  "A 즉시(BTC 저점 다음날)": lambda d: True,
  "B SOL/BTC 20일 모멘텀 > 0": lambda d: mom[d] > 0,
  "C SOL/BTC 비율 20일선 위": lambda d: R[d] > R20[d],
  "D SOL 20일선 위": lambda d: SOL[d] > S20[d],
  "E SOL 10일 고점 돌파": lambda d: SOL[d] > H10[d],
  "F SOL 20일선 위 & 비율 20일선 위": lambda d: SOL[d] > S20[d] and R[d] > R20[d],
  "G SOL 50일선 위": lambda d: SOL[d] > S50[d],
  "H 비율 20일 모멘텀 > +10%": lambda d: mom[d] > 0.10,
}
for b in ["2022-11-21", "2026-06-30", "2026-11-20"]:
    b = pd.Timestamp(b); w = SOL[b - pd.Timedelta(days=PRE): b + pd.Timedelta(days=POST)]; sl = w.idxmin(); print(f"\n  BTC 저점 {b.date()} (SOL 저점 {sl.date()} ${w.min():.1f})")
    for name, f in RULES.items():
        days = [d for d in SOL[b + pd.Timedelta(days=1):].index if f(d)]
        if not days: print(f"    {name:28s} 미발동"); continue
        e = days[0]; pth = path(SOL, e, 2, 0.20); end = min(e + pd.Timedelta(days=365), SOL.index[-1])
        print(f"    {name:28s} 진입 {e.date()} (+{(e-b).days:3d}일) SOL ${SOL[e]:.1f} 저점 대비 {SOL[e]/w.min()-1:+5.0%} | 진입 뒤 SOLT 최저 {pth[:end].min():.2f}배 | {'+365일' if end < SOL.index[-1] else '현재'} {pth[end]:.2f}배")
