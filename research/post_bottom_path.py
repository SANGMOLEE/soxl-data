# -*- coding: utf-8 -*-
"""사이클 바닥 뒤 BTC는 바로 크게 반등했나, 횡보했나? 그때 2배 상품(합성)은? (Yahoo 일봉 종가)
실행: python research/post_bottom_path.py"""
import os, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto")
def load(n):
    s = pd.read_csv(os.path.join(D, f"{n}.csv"), parse_dates=["date"]).set_index("date").close.sort_index(); return s.reindex(pd.date_range(s.index[0], s.index[-1])).ffill()
BTC, ETH, SOL = load("BTCUSD"), load("ETHUSD"), load("SOLUSD")
def lev(s, k=2.0, drag=0.16):
    r = s.pct_change().fillna(0) * k - drag / 365; return (1 + r).cumprod()
BOTTOMS = {"2015-01-14": "2015", "2018-12-15": "2018", "2020-03-12": "2020 코로나", "2022-11-21": "2022", "2026-06-30": "2026-06(첫 저점)"}
def first_hit(s, b, mult):
    hit = s[b:][s[b:] >= s[b] * mult]; return (hit.index[0] - b).days if len(hit) else None
print("== 1. BTC 바닥 뒤 경로 (종가, 바닥=1.00)")
print(f"{'바닥':16s} {'+30일':>6s} {'+60일':>6s} {'+90일':>6s} {'+180일':>7s} {'+365일':>7s} | {'+50%까지':>8s} {'+100%까지':>9s} | {'180일 내 최대 되돌림':>18s} | 바닥 뒤 90~270일 구간 범위(최저~최고)")
for b, name in BOTTOMS.items():
    b = pd.Timestamp(b); p = BTC[b]; row = []
    for k in (30, 60, 90, 180, 365):
        e = b + pd.Timedelta(days=k); row.append(f"{BTC[e]/p:6.2f}" if e <= BTC.index[-1] else "   —  ")
    h50, h100 = first_hit(BTC, b, 1.5), first_hit(BTC, b, 2.0)
    seg = BTC[b: b + pd.Timedelta(days=180)]; dd = (seg / seg.cummax() - 1).min()
    mid = BTC[b + pd.Timedelta(days=90): b + pd.Timedelta(days=270)]
    rng = f"{mid.min()/p:.2f}~{mid.max()/p:.2f}" if len(mid) > 30 else "—"
    print(f"{name:16s} {' '.join(row)} | {str(h50)+'일' if h50 else '미도달':>8s} {str(h100)+'일' if h100 else '미도달':>9s} | {dd:+18.0%} | {rng}")

print("\n== 2. 바닥 다음날 2배 상품을 사서 그냥 들고 있으면 (합성: BTC 2배 연 -16%, ETH·SOL 2배 연 -20%)")
print("   '깎임' = 2배 상품 배수 ÷ (현물 배수 2배 - 1) 로 본 변동성·비용 손실. 1.0이면 손실 없음")
for b, name in BOTTOMS.items():
    b = pd.Timestamp(b); out = [f"{name:16s}"]
    for lab, s, drag in (("BTC2x", BTC, 0.16), ("ETH2x", ETH, 0.20), ("SOL2x", SOL, 0.20)):
        if b < s.index[0] + pd.Timedelta(days=5): out.append(f"{lab}: 자료없음"); continue
        L = lev(s[b:], 2, drag); part = []
        for k in (90, 180, 365):
            e = b + pd.Timedelta(days=k)
            if e > s.index[-1]: part.append(f"+{k}일 —"); continue
            spot = s[e] / s[b]; ideal = 2 * spot - 1; part.append(f"+{k}일 {L[e]:.2f}배(현물 {spot:.2f}, 깎임 {L[e]/ideal if ideal > 0 else float('nan'):.2f})")
        part.append(f"최저 {L[:b+pd.Timedelta(days=365)].min():.2f}배")
        out.append(f"{lab}: " + " | ".join(part))
    print("  " + "\n     ".join(out))

print("\n== 3. 바닥 뒤 구간별 성격 (30일 실현변동성, 연율 / 구간 수익)")
for b, name in BOTTOMS.items():
    b = pd.Timestamp(b); segs = []
    for a, z in ((0, 60), (60, 180), (180, 365)):
        s0, s1 = b + pd.Timedelta(days=a), b + pd.Timedelta(days=z)
        if s1 > BTC.index[-1]: segs.append(f"{a}~{z}일: —"); continue
        seg = BTC[s0:s1]; vol = seg.pct_change().std() * np.sqrt(365); segs.append(f"{a}~{z}일: {seg.iloc[-1]/seg.iloc[0]-1:+.0%} (변동성 {vol:.0%}, 범위 {seg.min()/seg.iloc[0]-1:+.0%}~{seg.max()/seg.iloc[0]-1:+.0%})")
    print(f"  {name:16s} " + " | ".join(segs))
