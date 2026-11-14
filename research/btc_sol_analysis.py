# -*- coding: utf-8 -*-
"""BTC/SOL/BITU/SOLT 실측 분석 (data/crypto/*.csv, Yahoo via GitHub Actions crypto-once.yml).
- 전환점 대조, 교차상관, 사이클 베타
- 레버리지 ETF 실측 감쇠, 200일선 레짐 필터 vs 보유
- 주의: 신호는 종가 확정 후 다음 날부터 반영(선행편향 제거). 첫 버전은 진입/청산일 수익을 당일 반영한
  선행편향 버그로 +242% 가 나왔으나 수정 후 -88% (2025-03~2026-10, SOLT 60/10/20 규칙). 기록으로 남김.
"""
import os, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(__file__), "..", "data", "crypto")
ld = lambda n, c="close": pd.read_csv(os.path.join(D, n + ".csv"), parse_dates=["date"]).sort_values("date").set_index("date")[c].astype(float)
btc, sol = ld("BTCUSD"), ld("SOLUSD"); bitu, solt = ld("BITU", "adj_close"), ld("SOLT", "adj_close")

def st(eq): ret = eq.iloc[-1] / eq.iloc[0] - 1; dd = (eq / eq.cummax() - 1).min(); return f"{ret:+8.1%} / 낙폭 {dd:6.1%}"
def synth2x(px, fee=0.0195):
    r = px.pct_change().fillna(0); return (1 + np.clip(2 * r, -0.999, None) - fee / 365).cumprod()
def regime(px, n=200):
    ma = px.rolling(n).mean(); sig = (px > ma).astype(int).shift(1).fillna(0)
    return (1 + px.pct_change().fillna(0) * sig).cumprod(), int((sig.diff().abs() > 0).sum() // 2)
def dipbuy(px, lookback=60, conf=0.10, stop=20):
    pos = 0; eq = [1.0]; lo = px.rolling(lookback).min(); los = px.rolling(stop).min().shift(1)
    for i in range(1, len(px)):
        eq.append(eq[-1] * (px.iloc[i] / px.iloc[i - 1] if pos else 1))
        if pos == 0 and px.iloc[i] >= lo.iloc[i] * (1 + conf) and px.iloc[i - 1] < lo.iloc[i - 1] * (1 + conf): pos = 1
        elif pos == 1 and px.iloc[i] < los.iloc[i]: pos = 0
    return pd.Series(eq, index=px.index)

if __name__ == "__main__":
    j = pd.concat([btc, sol], axis=1, keys=["btc", "sol"]).dropna(); r = np.log(j).diff().dropna()
    print("일간 상관 전체/최근1년:", round(r.corr().iloc[0, 1], 3), round(r[-365:].corr().iloc[0, 1], 3))
    w = np.log(j.resample("W").last()).diff().dropna()
    print("주간 교차상관 k(SOL 후행 주):", {k: round(w["btc"].corr(w["sol"].shift(-k)), 3) for k in (0, 1, 2, 4, 8)})
    print("SOL 일간 베타 전체/최근1년:", round(np.polyfit(r["btc"], r["sol"], 1)[0], 2), round(np.polyfit(r["btc"][-365:], r["sol"][-365:], 1)[0], 2))
    for name, etf, und in (("BITU", bitu, btc), ("SOLT", solt, sol)):
        jj = pd.concat([etf, und], axis=1, keys=["e", "u"]).dropna(); jj = jj / jj.iloc[0]
        print(f"{name} 실측: ETF {st(jj['e'])} | 기초 {st(jj['u'])}")
    S2 = synth2x(sol["2020-06-01":]); B2 = synth2x(btc["2019-01-01":])
    for n in (100, 150, 200):
        es, ts = regime(S2, n); eb, tb = regime(B2, n); es, eb = es["2021":], eb["2021":]
        print(f"합성2x 2021~ {n}일선 필터: SOLT형 {st(es)} | BITU형 {st(eb)} | 50:50 {st((es/es.iloc[0]+eb/eb.iloc[0])/2)}")
    P = pd.concat([bitu, solt], axis=1, keys=["bitu", "solt"]).dropna()
    print("실제 ETF 구간 규칙(60/10/20, 선행편향 제거): SOLT", st(dipbuy(P["solt"])), "| BITU", st(dipbuy(P["bitu"])))
