# -*- coding: utf-8 -*-
"""비트코인 사이클 저점 직후 '반등 신호' 연구 (2014-09 ~ 최근, Yahoo 일봉 종가).
1) 확정 저점별 반등 첫날·첫 주 크기와 직전 상태, 이후 구조 회복 일수
2) 후보 신호 7종을 전 기간에 돌려, 약세장 중간 반등(가짜)과 진짜 저점 뒤 신호를 구분
   성공 = 신호일 이후 1년 동안 '신호 직전 60일 최저 종가'를 다시 깨지 않음
3) 결합 신호(순서형) 검증
실행: python research/bottom_signal_study.py
"""
import os, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "crypto", "BTCUSD.csv")
b = pd.read_csv(D, parse_dates=["date"]).set_index("date").sort_index()
ix = pd.date_range(b.index[0], b.index[-1]); b = b.reindex(ix).ffill(); c = b.close; r = c.pct_change()
ma = lambda n: c.rolling(n).mean(); ath = c.cummax(); dd = c / ath - 1
def rsi(s, n=14):
    d = s.diff(); u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + u / dn)
drsi = rsi(c); wr = rsi(c.resample("W-SUN").last())
m20, m50, m200 = ma(20), ma(50), ma(200)
low30 = c.rolling(30).min()
below200 = (c < m200).astype(int); run200 = below200.groupby((below200 == 0).cumsum()).cumsum()
bear = (dd <= -0.40)
BOTTOMS = {"2015-01-14": "2015 사이클", "2018-12-15": "2018 사이클", "2020-03-12": "2020 코로나", "2022-11-21": "2022 사이클", "2026-06-30": "2026 후보"}

def build_signals():
    S = {}
    S["S1 약세장 30일 저점에서 7일 +20%"] = (c / c.shift(7) - 1 >= 0.20) & (c.shift(7) <= low30.shift(7) * 1.05) & bear.shift(7, fill_value=False)
    S["S2 약세장 하루 +10%"] = (r >= 0.10) & bear.shift(1, fill_value=False)
    S["S3 RSI≤30 후 20일선 회복"] = (drsi.rolling(15).min() <= 30) & (c > m20) & (c.shift(1) <= m20.shift(1)) & bear
    S["S4 50일선 위 + 50일선 상승전환(장기 약세 후)"] = (c > m50) & (m50.diff(5) > 0) & (m50.diff(5).shift(1) <= 0) & bear & (below200.rolling(180).sum() >= 120)
    s5 = pd.Series(False, index=ix)
    for i in range(150, len(ix)):
        d = ix[i]
        if dd[d] > -0.25: continue
        w = c[ix[i - 120]:d]; Ld = w.idxmin(); Lv = w.min(); after = c[Ld:d].iloc[:-1]   # 오늘 제외
        if len(after) < 10: continue
        Hd = after.idxmax(); Hv = after.max()
        if Hv < Lv * 1.20 or Hd == d: continue
        pb = c[Hd:d].iloc[:-1]
        if len(pb) < 3: continue
        if pb.min() >= Lv * 1.03 and pb.min() <= Hv * 0.92 and c[d] > Hv and c[ix[i - 1]] <= Hv: s5[d] = True
    S["S5 저점 상승 후 반등고점 종가 돌파"] = s5
    S["S6 200일선 회복(120일+ 하회 후)"] = (c > m200) & (run200.shift(1) >= 120)
    w7 = (wr > 50) & (wr.shift(1) <= 50) & (wr.rolling(26).min() <= 35); s7 = pd.Series(False, index=ix); s7[w7[w7].index] = True
    S["S7 주간 RSI 50 회복(26주 내 35 이하 후)"] = s7
    return {k: v.fillna(False).astype(bool) for k, v in S.items()}

def evaluate(s, gap=45):
    out = []; last = None
    for d in s[s].index:
        if last is not None and (d - last).days < gap: continue
        last = d; ref = c[d - pd.Timedelta(days=60):d].min(); fut = c[d + pd.Timedelta(days=1):d + pd.Timedelta(days=365)]
        if len(fut) and fut.min() <= ref: st = "실패"
        elif len(fut) < 365: st = "진행중"
        else: st = "성공"
        f = lambda n: c[d + pd.Timedelta(days=n)] / c[d] - 1 if d + pd.Timedelta(days=n) <= ix[-1] else np.nan
        bot = max([pd.Timestamp(x) for x in BOTTOMS if pd.Timestamp(x) <= d], default=None)
        lag = f"저점+{(d - bot).days}일, 저점대비 {c[d] / c[bot] - 1:+.0%}" if bot is not None and (d - bot).days <= 400 else ""
        out.append(dict(date=d, status=st, px=c[d], f90=f(90), f180=f(180), worst=(fut.min() / c[d] - 1) if len(fut) else np.nan, lag=lag))
    return out

if __name__ == "__main__":
    print("== 1. 저점별 반등 첫날·첫 주")
    for d, k in BOTTOMS.items():
        d = pd.Timestamp(d); p = c[d]; f = lambda n: c[d + pd.Timedelta(days=n)] / p - 1
        print(f"  {k} {d.date()} ${p:,.0f} 고점대비 {p / ath[d] - 1:+.0%} | 첫날 {f(1):+.1%} | 첫주 최대일간 {r[d + pd.Timedelta(days=1):d + pd.Timedelta(days=7)].max():+.1%} | 7일 {f(7):+.0%} | 30일 {f(30):+.0%} | 90일 {f(90):+.0%} | 일간RSI {drsi[d]:.0f} 주간RSI {wr.reindex(ix, method='ffill')[d]:.0f}")
    S = build_signals(); summary = []
    for k, s in S.items():
        ev = evaluate(s); judged = [e for e in ev if e["status"] != "진행중"]; ok = [e for e in judged if e["status"] == "성공"]
        summary.append((k, len(ev), len(judged), len(ok)))
        print(f"\n### {k}: 사건 {len(ev)} / 판정 {len(judged)} / 성공 {len(ok)} ({len(ok) / len(judged):.0%})" if judged else f"\n### {k}: 사건 {len(ev)}")
        for e in ev: print(f"   {e['date'].date()} {e['status']:3s} ${e['px']:>8,.0f} | 90일 {e['f90']:+5.0%} | 180일 {e['f180']:+5.0%} | 1년 최악 {e['worst']:+5.0%} | {e['lag']}")
    print("\n== 요약"); [print(f"  {k}: 사건 {n}, 성공률 {ok}/{j}") for k, n, j, ok in summary]
