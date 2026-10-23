# -*- coding: utf-8 -*-
"""
사례 연구 — 'SOX가 60일 고점 대비 TH 이상 급락한 첫날(고점 후 FAST일 이내)'
TH 는 마지막 종가의 60일 고점 대비 낙폭을 1%p 단위로 내림한 값(현재와 같은 깊이),
FAST 는 현재 고점 후 경과일 + 5.  이후 60거래일 동안 얼마나 더 빠졌고, 언제 바닥이었는지.
"""
import pandas as pd, numpy as np, load
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
p = load.panel()
s, y = p["sox"], p["syn3"]
H = 60
TH = np.ceil(p['dd60'].iat[-1]*100)/100   # 예: -18.8% → -18%
FAST = int(p['days_since_hi60'].iat[-1]) + 5
print(f'기준일 {p.index[-1].date()}  TH={TH:.0%}  FAST={FAST}일')

ev, last = [], None
for i, t in enumerate(p.index):
    if i < 250 or i + 1 >= len(p):
        continue
    if p["dd60"].iat[i] <= TH and p["days_since_hi60"].iat[i] <= FAST:
        if last is not None and i - last < H:   # 같은 에피소드
            continue
        last = i
        ev.append(i)

rows = []
for i in ev:
    t = p.index[i]
    fut = s.iloc[i+1:i+1+H]
    n = len(fut)
    mn = fut.min() if n else np.nan
    j = fut.values.argmin() if n else 0
    yf = y.iloc[i+1:i+1+H]
    rows.append(dict(
        date=t.date(), n=n,
        dd60=p["dd60"].iat[i], days=int(p["days_since_hi60"].iat[i]),
        dd_ath=p["dd_ath"].iat[i], ma200=p["ma200"].iat[i],
        spy_dd=p["spy_dd60"].iat[i], vix=p["vix"].iat[i], hy=p["hy"].iat[i], hy20=p["hy_chg20"].iat[i],
        fg=p["fg"].iat[i],
        more_dn=min(mn / s.iat[i] - 1, 0),           # 이후 추가 하락(SOX)
        d2low=(j + 1) if mn < s.iat[i] else 0,       # 바닥까지 거래일
        more_dn3x=min(yf.min() / y.iat[i] - 1, 0),   # 합성 3배 추가 하락
        f10=s.iloc[min(i+10, len(s)-1)] / s.iat[i] - 1,
        f20=s.iloc[min(i+20, len(s)-1)] / s.iat[i] - 1,
        f60=s.iloc[min(i+60, len(s)-1)] / s.iat[i] - 1,
        f60_3x=y.iloc[min(i+60, len(y)-1)] / y.iat[i] - 1,
    ))
E = pd.DataFrame(rows)
E.to_csv("../output/events.csv", index=False)
print(E.round(3).to_string(index=False))

def summ(x, name):
    x = x[x.n >= 40]
    if not len(x):
        return
    print(f"\n[{name}] n={len(x)}")
    print(f"  이 날이 바닥(이후 더 안 빠짐)     : {(x.more_dn >= 0).mean():.0%}")
    print(f"  추가하락 3% 이내                 : {(x.more_dn > -0.03).mean():.0%}")
    print(f"  추가하락 SOX 중앙값/75%/90%       : {x.more_dn.median():.1%} / {x.more_dn.quantile(.25):.1%} / {x.more_dn.quantile(.10):.1%}")
    print(f"  추가하락 합성3배 중앙값/75%/90%   : {x.more_dn3x.median():.1%} / {x.more_dn3x.quantile(.25):.1%} / {x.more_dn3x.quantile(.10):.1%}")
    print(f"  바닥까지 거래일 중앙값            : {x.d2low.median():.0f}  (25~75%: {x.d2low.quantile(.25):.0f}~{x.d2low.quantile(.75):.0f})")
    print(f"  60일 뒤 SOX 수익률 중앙값/플러스확률: {x.f60.median():.1%} / {(x.f60 > 0).mean():.0%}")
    print(f"  60일 뒤 합성3배 중앙값            : {x.f60_3x.median():.1%}")

summ(E, "전체")
summ(E[E.ma200 > 0], "SOX 200일선 위(상승추세 중 급락)")
summ(E[E.spy_dd > -0.05], "SPY 고점 대비 -5% 이내(시장 전체는 멀쩡)")
summ(E[(E.ma200 > 0) & (E.spy_dd > -0.05)], "200일선 위 + SPY 멀쩡")
summ(E[E.vix < 25], "VIX 25 미만")
summ(E[E.vix >= 25], "VIX 25 이상")
