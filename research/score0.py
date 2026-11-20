# -*- coding: utf-8 -*-
"""bv1 — 저점 거리 점수 (0 = 확정된 네 사이클 저점) — 운용 코드 (2026-11-20, 재작성)
앵커 = 확정 저점 2015-01-14·2018-12-15·2020-03-12·2022-11-21 당일 값 중 가장 덜 극단적인 값(고정). 중립 = 2015~ 중앙값(고정).
2026-06-30은 확정 저점이 아니므로 앵커에 포함하지 않는다(첫 판의 오류를 바로잡음). 다섯 번째 저점이 확정되면 그때 재고정하고 bv2로 올린다.
거리_i = clip((앵커_i − 값_i)/(앵커_i − 중립_i), 0, 1)×100.  점수 = 0.5×구간(5) + 0.5×타이밍(6).  0 = 네 저점과 같거나 더 극단.
연구: score0_study.py / score0_research_2026-11-20.md.  실행: python research/score0.py → research/score0_state.json
"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score100_features import load, ORIENT
ZC = ["mayer", "w200", "ddath", "mvrv", "rsi_w"]; TC = ["rsi14", "dd30", "dd90", "bbz", "ma50d", "r7"]; COLS = ZC + TC
# 고정 앵커(원단위, 2026-11-20 산출) — 바꾸면 "사후"
ANCHOR = dict(mayer=-0.2932, w200=0.0156, ddath=-0.6106, mvrv=0.8775, rsi_w=33.53, rsi14=31.40, dd30=-0.2582, dd90=-0.2943, bbz=-1.0974, ma50d=-0.1692, r7=-0.0500)
# 엄격 눈금(네 확정 저점 중앙값) — 2·3차 비중 참고용
STRICT = dict(mayer=-0.4252, w200=-0.0981, ddath=-0.7557, mvrv=0.7340, rsi_w=31.30, rsi14=23.39, dd30=-0.4460, dd90=-0.5190, bbz=-2.2011, ma50d=-0.4003, r7=-0.2319)
NEUTRAL = dict(mayer=0.1121, w200=0.6647, ddath=-0.3850, mvrv=1.6376, rsi_w=55.71, rsi14=51.96, dd30=-0.0626, dd90=-0.1297, bbz=0.2221, ma50d=0.0186, r7=0.0062)
LABEL = dict(mayer="200일선", w200="200주선", ddath="ATH낙폭", mvrv="MVRV", rsi_w="주간RSI", rsi14="일간RSI", dd30="30일낙폭", dd90="90일낙폭", bbz="볼린저z", ma50d="50일선", r7="7일수익")

def band(s): return "저점(과거 저점 수준)" if s <= 5 else "저점 근접" if s <= 15 else "저점권" if s <= 35 else "중간" if s <= 65 else "저점 아님"

def dist(F, anc):
    D = pd.DataFrame(index=F.index)
    for k in COLS:
        a, n = anc[k] * ORIENT[k], NEUTRAL[k] * ORIENT[k]; x = F[k] * ORIENT[k]
        D[k] = ((a - x) / (a - n)).clip(0, 1) * 100
    return D

def compute():
    F = load(); D = dist(F, ANCHOR); Ds = dist(F, STRICT)
    F["Z"] = D[ZC].mean(axis=1); F["T"] = D[TC].mean(axis=1); F["score0"] = 0.5 * F.Z + 0.5 * F["T"]
    F["strict"] = 0.5 * Ds[ZC].mean(axis=1) + 0.5 * Ds[TC].mean(axis=1)
    return F, D

if __name__ == "__main__":
    F, D = compute(); x = F.index[-1]; r = F.iloc[-1]; c = F.close
    ma200 = c.rolling(200).mean()[x]; ma1400 = c.rolling(1400).mean()[x]; rp = c[x] / F.mvrv[x]
    pz = {"200일선": ma200 * (1 + ANCHOR["mayer"]), "ATH낙폭": F.ath[x] * (1 + ANCHOR["ddath"]), "MVRV": rp * ANCHOR["mvrv"], "200주선": ma1400 * (1 + ANCHOR["w200"])}
    print(f"{x.date()} BTC {c[x]:,.0f} | bv1 저점거리 점수 {r.score0:.1f} [{band(r.score0)}] = 구간 {r.Z:.1f} · 타이밍 {r['T']:.1f} | 엄격 {r.strict:.1f}")
    print("  지표별 거리:", {LABEL[k]: round(D.at[x, k]) for k in COLS})
    print("  구간 지표가 0에 닿는 가격:", {k: f"{v:,.0f}" for k, v in pz.items()}, "→ 전부 0:", f"{min(pz.values()):,.0f}")
    print("  최근 30일:", " ".join(str(int(round(v))) for v in F.score0.iloc[-30:]))
    st = dict(model="bv1", date=str(x.date()), close=round(float(c[x])), score0=round(float(r.score0), 1), band=band(r.score0), strict=round(float(r.strict), 1), zone=round(float(r.Z), 1), timing=round(float(r["T"]), 1),
              components={LABEL[k]: round(float(D.at[x, k])) for k in COLS}, zero_price={k: round(float(v)) for k, v in pz.items()}, zero_price_all=round(float(min(pz.values()))))
    json.dump(st, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score0_state.json"), "w"), ensure_ascii=False, indent=1)
