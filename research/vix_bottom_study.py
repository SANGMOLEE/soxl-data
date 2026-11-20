# -*- coding: utf-8 -*-
"""VIX가 비트코인 사이클 저점 탐지에 보탬이 되는가 — 실측 (2026-11-20)
질문 1. 과거 BTC 저점 당일·전후의 VIX 수준과 10년 백분위는?
질문 2. 탐지기 점수(bottom_detector)가 켜진 날을 VIX로 가르면 이후 수익·추가 낙폭이 달라지는가?
질문 3. VIX 급등(≥30) 자체가 BTC 매수 신호인가?
질문 4. BTC 자체 변동성(30일 실현변동성 백분위)이 VIX보다 나은가?
실행: python research/vix_bottom_study.py
"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bottom_detector import features, BOTTOMS
VIXF = os.path.join(HERE, "..", "data", "macro", "VIXCLS.csv")

F = features()
vix = pd.read_csv(VIXF, parse_dates=["date"]).set_index("date")["value"].astype(float).sort_index()
vix_pct10 = vix.rolling(2520, min_periods=1500).rank(pct=True)          # 10년 백분위(거래일 기준)
vix_max30 = vix.rolling(21).max()
F["vix"] = vix.reindex(F.index).ffill(); F["vix_pct"] = vix_pct10.reindex(F.index).ffill(); F["vix_max30"] = vix_max30.reindex(F.index).ffill()
F["rv30"] = np.log(F.close).diff().rolling(30).std() * np.sqrt(365)
F["rv_pct"] = F.rv30.rolling(1460, min_periods=730).rank(pct=True)        # BTC 자체 변동성의 4년 백분위
c = F.close
for n in (90, 180, 365):
    F[f"fwd{n}"] = c.shift(-n) / c - 1
F["mae180"] = c.rolling(180).min().shift(-179) / c - 1                       # 이후 180일 최대 추가 낙폭

print("== 1. 과거 BTC 저점에서의 VIX ==")
rows = []
for d, name in BOTTOMS.items():
    t = pd.Timestamp(d); w = F.loc[t - pd.Timedelta(days=30): t + pd.Timedelta(days=30)]
    rows.append(dict(저점=d, 이름=name, VIX당일=round(F.at[t, "vix"], 1), VIX10년백분위=round(F.at[t, "vix_pct"] * 100), 전후30일최고=round(w.vix.max(), 1),
                     최고일=w.vix.idxmax().date(), BTC실현변동성=round(F.at[t, "rv30"] * 100), RV백분위=(round(F.at[t, "rv_pct"] * 100) if pd.notna(F.at[t, "rv_pct"]) else None), 탐지점수=int(F.at[t, "score"])))
print(pd.DataFrame(rows).to_string(index=False))
print("참고 VIX 전체(1990~) 중앙값 %.1f, 2014~ 중앙값 %.1f, 90백분위 %.1f" % (vix.median(), vix["2014":].median(), vix["2014":].quantile(.9)))

print("\n== 2. 탐지기 신호일을 VIX로 갈랐을 때 (2015~2026, 중복 신호는 30일마다 1건으로 묶음) ==")
def episodes(mask, gap=30):
    idx = F.index[mask.fillna(False)]; out = []; last = None
    for t in idx:
        if last is None or (t - last).days > gap: out.append(t)
        last = t
    return out
def table(mask, label):
    eps = episodes(mask); r = F.loc[eps]
    print(f"\n[{label}] 사건 {len(eps)}건")
    for cut_name, m in (("VIX<20", r.vix < 20), ("VIX 20~30", (r.vix >= 20) & (r.vix < 30)), ("VIX≥30", r.vix >= 30)):
        s = r[m]
        if len(s) == 0: print(f"  {cut_name:9s} n=0"); continue
        print(f"  {cut_name:9s} n={len(s):2d} | 180일 중앙 {s.fwd180.median():+.0%} (25~75% {s.fwd180.quantile(.25):+.0%}~{s.fwd180.quantile(.75):+.0%}) | 365일 중앙 {s.fwd365.median():+.0%} | 180일 추가낙폭 중앙 {s.mae180.median():.0%} 최악 {s.mae180.min():.0%} | 승률(365일>0) {(s.fwd365 > 0).mean():.0%}")
    for name, m in (("VIX10년백분위≥80", r.vix_pct >= .8), ("VIX10년백분위<80", r.vix_pct < .8)):
        s = r[m]
        if len(s): print(f"  {name:14s} n={len(s):2d} | 180일 중앙 {s.fwd180.median():+.0%} | 365일 중앙 {s.fwd365.median():+.0%} | 추가낙폭 중앙 {s.mae180.median():.0%} 최악 {s.mae180.min():.0%}")
    print("  사건별:", "; ".join(f"{t.date()} V{F.at[t,'vix']:.0f} 점수{int(F.at[t,'score'])} 365일{F.at[t,'fwd365']:+.0%} 낙폭{F.at[t,'mae180']:.0%}" for t in eps))
table(F.score >= 4, "점수≥4 (현재 수준)")
table(F.score >= 5, "점수≥5 (2단계)")
table(F.zone, "저점 구간(게이트+2단계)")

print("\n== 3. VIX 급등 자체가 BTC 매수 신호인가 (VIX≥30 첫 돌파일, 2014~) ==")
spk = episodes((F.vix >= 30) & (F.vix.shift(1) < 30), gap=30); r = F.loc[spk]
base = F.loc["2015":"2025"]
print(f"VIX≥30 돌파 {len(spk)}건: 180일 중앙 {r.fwd180.median():+.0%}, 365일 중앙 {r.fwd365.median():+.0%}, 승률(365일) {(r.fwd365>0).mean():.0%}, 180일 추가낙폭 중앙 {r.mae180.median():.0%} 최악 {r.mae180.min():.0%}")
print(f"무조건(모든 날 2015~2025): 180일 중앙 {base.fwd180.median():+.0%}, 365일 중앙 {base.fwd365.median():+.0%}, 승률 {(base.fwd365>0).mean():.0%}, 추가낙폭 중앙 {base.mae180.median():.0%}")
print("사건별:", "; ".join(f"{t.date()} V{F.at[t,'vix']:.0f} 고점대비{F.at[t,'ddath']:+.0%} 점수{int(F.at[t,'score'])} 365일{F.at[t,'fwd365']:+.0%}" for t in spk))
print(f"VIX≥30 돌파일 중 탐지 점수≥4였던 비율: {(r.score>=4).mean():.0%}, 게이트(고점 후 240일·-45%) 안이었던 비율: {r.gate.mean():.0%}")

print("\n== 4. BTC 자체 변동성(RV30 4년 백분위) vs VIX — 점수≥4 사건 ==")
eps = episodes(F.score >= 4); r = F.loc[eps]
for name, m in (("RV백분위≥90", r.rv_pct >= .9), ("RV백분위<90", r.rv_pct < .9)):
    s = r[m]
    if len(s): print(f"  {name:10s} n={len(s):2d} | 180일 중앙 {s.fwd180.median():+.0%} | 365일 중앙 {s.fwd365.median():+.0%} | 추가낙폭 중앙 {s.mae180.median():.0%} 최악 {s.mae180.min():.0%}")
print("  점수≥4 사건에서 VIX와 365일 수익 순위상관 %.2f, RV백분위와 순위상관 %.2f (n=%d)" % (r.vix.rank().corr(r.fwd365.rank()), r.rv_pct.rank().corr(r.fwd365.rank()), len(r)))

print("\n== 5. 동행성: BTC 일간수익 vs VIX 일간변화 (2015~) ==")
j = pd.DataFrame(dict(b=np.log(c).diff(), v=np.log(F.vix).diff())).loc["2015":].dropna(); j = j[j.v != 0]
print(f"전체 상관 {j.b.corr(j.v):+.2f} | VIX +10% 이상 급등일 BTC 중앙 {j[j.v>=.1].b.median():+.1%} (n={int((j.v>=.1).sum())}) | 2020-03 제외 상관 {j.drop(j.loc['2020-02-20':'2020-04-15'].index).b.corr(j.drop(j.loc['2020-02-20':'2020-04-15'].index).v):+.2f}")

print("\n== 6. 현재(최근 자료일) ==")
x = F.iloc[-1]
print(f"{F.index[-1].date()} BTC {x.close:,.0f} 점수 {int(x.score)} | VIX {x.vix:.1f} (10년 백분위 {x.vix_pct*100:.0f}, 21일 최고 {x.vix_max30:.1f}) | BTC 실현변동성 {x.rv30*100:.0f}% (4년 백분위 {x.rv_pct*100:.0f})")
