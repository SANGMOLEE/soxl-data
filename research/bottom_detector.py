# -*- coding: utf-8 -*-
"""비트코인 사이클 저점 '실시간 탐지기'. 그날 종가(또는 진행 중 가격)까지의 정보만 쓴다. 사후 확인 신호 없음.
조건 8개(항복 점수 0~8):
  A 일간 RSI(14) ≤ 30            B 주간 RSI(14, 7일 간격 굴림) ≤ 35
  C 200일선 대비 ≤ -20%           D 200주선(1400일) 대비 ≤ +5%
  E 30일 고점 대비 ≤ -25%         F 7일 수익 ≤ -15%
  G 최근 5일 안 투매일(거래량 ≥ 30일 중앙값×2 이고 하루 ≤ -5% 또는 3일 ≤ -10%)
  H 사상 최고가 대비 ≤ -50%
알람 단계: 1단계(주의) 점수 ≥ 3, 2단계(저점 구간) 점수 ≥ 5, 3단계(투매 절정) 점수 ≥ 6 그리고 G 충족.
실행: python research/bottom_detector.py            → 과거 검증 + 현재 상태 출력, research/alarm_state.json 기록
"""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data", "crypto", "BTCUSD.csv")
REALIZED_PRICE = 53000.0   # 실현가격(전체 평균 매입단가) 수동 입력값. 출처: Coin Metrics·CryptoQuant 2026-11 초 52~54k. 온체인 자료가 저장소에 없어 수동 갱신.
BOTTOMS = {"2015-01-14": "2015", "2018-12-15": "2018", "2020-03-12": "2020 코로나", "2022-11-21": "2022", "2026-06-30": "2026 후보"}

def rsi(s, n=14):
    d = s.diff(); u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + u / dn)

def features():
    b = pd.read_csv(D, parse_dates=["date"]).set_index("date").sort_index()
    ix = pd.date_range(b.index[0], b.index[-1]); b = b.reindex(ix).ffill(); c, v = b.close, b.volume
    F = pd.DataFrame(index=ix); F["close"] = c; F["low"] = b.low
    F["rsi_d"] = rsi(c)
    wr = pd.Series(np.nan, index=ix)
    for k in range(7):
        s = c.iloc[k::7]; wr.loc[s.index] = rsi(s)
    F["rsi_w"] = wr
    F["ma200"] = c.rolling(200).mean(); F["ma1400"] = c.rolling(1400).mean()
    F["mayer"] = c / F.ma200 - 1; F["w200"] = c / F.ma1400 - 1
    F["hi30"] = c.rolling(30).max(); F["dd30"] = c / F.hi30 - 1; F["r7"] = c / c.shift(7) - 1
    r1 = c.pct_change(); r3 = c / c.shift(3) - 1; vmed = v.rolling(30).median().shift(1)
    cap = (v >= 2 * vmed) & ((r1 <= -0.05) | (r3 <= -0.10)); F["capday"] = cap; F["G"] = cap.rolling(5).max().fillna(0).astype(bool)
    F["ath"] = c.cummax(); F["ddath"] = c / F.ath - 1
    F["A"] = F.rsi_d <= 30; F["B"] = F.rsi_w <= 35; F["C"] = F.mayer <= -0.20; F["D"] = F.w200 <= 0.05
    F["E"] = F.dd30 <= -0.25; F["F"] = F.r7 <= -0.15; F["H"] = F.ddath <= -0.50
    conds = list("ABCDEFGH"); F["score"] = F[conds].fillna(False).astype(int).sum(axis=1)
    F["level"] = 0; F.loc[F.score >= 3, "level"] = 1; F.loc[F.score >= 5, "level"] = 2; F.loc[(F.score >= 6) & F.G, "level"] = 3
    athd = pd.Series(ix.where(c == F.ath), index=ix).ffill(); F["days_ath"] = (ix - pd.DatetimeIndex(athd)).days
    F.loc[:"2017-01-01", "days_ath"] = (F.loc[:"2017-01-01"].index - pd.Timestamp("2013-12-04")).days   # 2013-12 고점은 자료 밖
    F["gate"] = (F.days_ath >= 240) & (F.ddath <= -0.45)          # 사이클 저점 후보 조건: 고점 후 240일 이상, 고점 대비 -45% 이하
    F["zone"] = F.gate & (F.level >= 2)                           # 저점 구간(1차 매수 신호)
    zone15 = (F.level >= 2).rolling(15).max().fillna(0).astype(bool)
    F["rev_peak"] = (F.score.rolling(10).max() >= 6) & (F.score <= F.score.rolling(10).max() - 2) & (c > c.shift(3))          # 점수 정점 통과
    F["rev_break"] = zone15 & (c > c.shift(1).rolling(5).max()) & (c.shift(1) <= c.shift(2).rolling(5).max())                 # 5일 종가 고점 돌파
    return F

def what_if(price):
    """오늘 종가가 price 라면 점수·단계가 얼마인지(조건이 켜지는 가격 탐색용)."""
    b = pd.read_csv(D, parse_dates=["date"]).set_index("date").sort_index(); b.iloc[-1, b.columns.get_loc("close")] = price
    b.iloc[-1, b.columns.get_loc("low")] = min(b["low"].iloc[-1], price)
    tmp = D + ".whatif.csv"; b.reset_index().to_csv(tmp, index=False)
    global D_; old = globals()["D"]; globals()["D"] = tmp
    try: x = features().iloc[-1]
    finally: globals()["D"] = old; os.remove(tmp)
    return int(x.score), int(x.level), bool(x.zone)

def episodes(F, level, gap=45):
    """알람 단계가 level 이상으로 '처음' 올라간 날(직전 gap 일 동안 그 단계가 없었던 날)."""
    on = F.level >= level; out = []; last = None
    for d in on[on].index:
        if last is None or (d - last).days > gap: out.append(d)
        last = d
    return out

def evaluate(F, level):
    c = F.close; rows = []
    for d in episodes(F, level):
        fut = c[d:d + pd.Timedelta(days=365)]; lo = fut.min(); lod = fut.idxmin()
        f = lambda n: (c[d + pd.Timedelta(days=n)] / c[d] - 1) if d + pd.Timedelta(days=n) <= c.index[-1] else np.nan
        rows.append(dict(date=d, px=c[d], score=int(F.score[d]), more=lo / c[d] - 1, days_to_low=(lod - d).days, f90=f(90), f180=f(180), f365=f(365), ddath=F.ddath[d]))
    return pd.DataFrame(rows)

def trigger_levels(F):
    """현재 기준으로 각 조건이 켜지는 가격(근사). 이동평균·고점은 오늘 값 고정."""
    x = F.iloc[-1]
    return {"C 200일선 -20%": x.ma200 * 0.80, "D 200주선 +5%": x.ma1400 * 1.05, "E 30일 고점 -25%": x.hi30 * 0.75,
            "F 7일 -15%": F.close.iloc[-8] * 0.85, "H 사상최고가 -50%": x.ath * 0.50, "6월 저점(종가)": 58558.86, "실현가격(수동)": REALIZED_PRICE}

if __name__ == "__main__":
    F = features(); c = F.close
    print("== 1. 과거 저점 당일의 탐지기 상태")
    for d, k in BOTTOMS.items():
        d = pd.Timestamp(d); x = F.loc[d]; w = F.loc[d - pd.Timedelta(days=10):d + pd.Timedelta(days=3)]
        on = "".join(k2 for k2 in "ABCDEFGH" if bool(x[k2]))
        first2 = F.loc[d - pd.Timedelta(days=120):d]; f2 = first2[first2.level >= 2]; f3 = first2[first2.level >= 3]
        print(f"  {k} {d.date()} ${x.close:,.0f}: 점수 {int(x.score)} [{on}] 단계 {int(x.level)} | 저점±10일 최고 점수 {int(w.score.max())}, 최고 단계 {int(w.level.max())}"
              + (f" | 2단계 첫 발생 {f2.index[0].date()} ${f2.close.iloc[0]:,.0f} (저점까지 {x.close / f2.close.iloc[0] - 1:+.0%}, {(d - f2.index[0]).days}일 전)" if len(f2) else " | 2단계 미발생")
              + (f" | 3단계 첫 발생 {f3.index[0].date()} ${f3.close.iloc[0]:,.0f} ({x.close / f3.close.iloc[0] - 1:+.0%})" if len(f3) else " | 3단계 미발생"))
    for lv in (1, 2, 3):
        E = evaluate(F, lv); print(f"\n== 2. {lv}단계 알람 첫 발생 {len(E)}건 (이후 1년 추가 하락 / 수익)")
        for _, r in E.iterrows():
            print(f"  {r.date.date()} ${r.px:>8,.0f} 점수 {r.score} 고점대비 {r.ddath:+.0%} | 이후 최저까지 {r.more:+5.0%} ({int(r.days_to_low)}일) | 90일 {r.f90:+5.0%} 180일 {r.f180:+5.0%} 1년 {r.f365:+5.0%}")
        if len(E): print(f"  → 추가 하락 중앙값 {E.more.median():+.0%}, 최악 {E.more.min():+.0%} | 1년 수익 중앙값 {E.f365.median():+.0%}, 플러스 비율 {(E.f365.dropna() > 0).mean():.0%} (n={E.f365.notna().sum()})")
    x = F.iloc[-1]; on = "".join(k for k in "ABCDEFGH" if bool(x[k]))
    print(f"\n== 3. 현재 {F.index[-1].date()} ${x.close:,.0f}: 점수 {int(x.score)} [{on}] 단계 {int(x.level)} | 일간RSI {x.rsi_d:.0f} 주간RSI {x.rsi_w:.0f} 200일선 {x.mayer:+.1%} 200주선 {x.w200:+.1%} 30일고점 {x.dd30:+.1%} 7일 {x.r7:+.1%} 고점대비 {x.ddath:+.1%}")
    T = trigger_levels(F); print("   조건이 켜지는 가격:", {k: round(v) for k, v in sorted(T.items(), key=lambda kv: -kv[1])})
    scan = {}
    for p in range(int(x.close // 500 * 500), 44500, -500):
        sc, lv, zn = what_if(float(p))
        if "level1" not in scan and lv >= 1: scan["level1"] = p
        if "level2" not in scan and lv >= 2: scan["level2"] = p
        if "zone" not in scan and zn: scan["zone"] = p; break
    print("   오늘 종가가 이 가격이면: 1단계", scan.get("level1"), "| 2단계", scan.get("level2"), "| 저점 구간(1차 매수 신호)", scan.get("zone"))
    print(f"   고점 후 {int(x.days_ath)}일, 시간·낙폭 조건 {bool(x.gate)} | 반전 신호: 점수정점 {bool(x.rev_peak)}, 5일고점돌파 {bool(x.rev_break)}")
    state = dict(date=str(F.index[-1].date()), price=round(float(x.close)), score=int(x.score), level=int(x.level), conditions_on=on,
                 gate=bool(x.gate), zone=bool(x.zone), rev_peak=bool(x.rev_peak), rev_break=bool(x.rev_break), days_since_ath=int(x.days_ath),
                 zone_7d=bool(F.zone.iloc[-7:].any()), oversold=bool(x.rsi_d <= 30),
                 alarm=bool(x.zone or x.level >= 2 or ((x.rev_peak or x.rev_break) and F.zone.iloc[-30:].any())),
                 notice=bool(x.level >= 1 or x.rsi_d <= 30 or x.close <= 58558.86 * 1.05), next_prices=scan,
                 rsi_d=round(float(x.rsi_d), 1), rsi_w=round(float(x.rsi_w), 1), vs_ma200=round(float(x.mayer), 4), vs_ma200w=round(float(x.w200), 4),
                 dd30=round(float(x.dd30), 4), r7=round(float(x.r7), 4), dd_ath=round(float(x.ddath), 4), ma200=round(float(x.ma200)), ma200w=round(float(x.ma1400)),
                 trigger_prices={k: round(float(v)) for k, v in T.items()}, max_level_7d=int(F.level.iloc[-7:].max()), max_score_7d=int(F.score.iloc[-7:].max()),
                 near_realized=bool(x.close <= REALIZED_PRICE * 1.05), near_june_low=bool(x.close <= 58558.86 * 1.05))
    json.dump(state, open(os.path.join(HERE, "alarm_state.json"), "w"), ensure_ascii=False, indent=1)
    print("   alarm_state.json 기록:", state["level"], state["score"], state["conditions_on"])
