# 2018 Q4(실패 저점)·2023-10(진짜 바닥)·지금(10/14 저점) 같은 잣대 비교 (2026-10-23, 주인님 질문 "두 사례 중 어디에 가까운가")
import pandas as pd, numpy as np, runpy
G = runpy.run_path('nail/research/bottom_study.py', run_name='lib')
NAIL, ITB, SPY, M, APARTS, hy_pct = G['NAIL'], G['ITB'], G['SPY'], G['M'], G['APARTS'], G['hy_pct']
P = lambda t: pd.read_csv(f'nail/data/prices/{t}.csv', parse_dates=['date']).set_index('date').close
TNX, VIX = P('TNX'), P('VIX')
import os
Q = pd.read_csv('nail/data/prices/QQQ.csv' if os.path.exists('nail/data/prices/QQQ.csv') else 'data/prices/QQQ.csv', parse_dates=['date']).set_index('date').close
oil = M['DCOILWTICO']; cpi = M['CPIAUCSL']; ff = M['DFF']; mtg = M['MORTGAGE30US']; hy = M['BAMLH0A0HYM2']; hs = M['MSACSR']
c = NAIL.close
def row(low, lab):
    t = pd.Timestamp(low); i = c.index.get_loc(t); t6 = c.index[min(i+6, len(c)-1)]
    def asof(s, d): s = s[s.index <= d]; return s.iloc[-1]
    def dd(s, d, n=252): s = s[s.index <= d]; return s.iloc[-1] / s.iloc[-n:].max() - 1
    tn = TNX[TNX.index <= t6]; pk = tn.iloc[-252:].idxmax()
    w = TNX[(TNX.index >= t - pd.Timedelta(days=200)) & (TNX.index <= t + pd.Timedelta(days=60))]; pk2 = w.idxmax()
    m = (t - pd.DateOffset(days=45)).to_period('M').to_timestamp()
    yoy = cpi.loc[m] / cpi.loc[m - pd.DateOffset(years=1)] - 1; yoy3 = cpi.loc[m - pd.DateOffset(months=3)] / cpi.loc[m - pd.DateOffset(months=15)] - 1
    a = APARTS.loc[t]
    hi_ath = c[c.index <= t].idxmax()
    return {'사례': lab, '저점일': t.date(), '+6일': t6.date(),
        'NAIL 1년 낙폭(저점)': f'{dd(c,t):+.0%}', 'NAIL 사상최고 대비': f'{c.loc[t]/c[c.index<=t].max()-1:+.0%}',
        '사상최고 후 경과(개월)': round((t - hi_ath).days/30.4),
        '6일 반등': f'{c.loc[t6]/c.loc[t]-1:+.1%}',
        'ITB 756일 낙폭': f'{a.A1_dd756:+.0%}', 'ITB 주봉 RSI': round(a.A3_rsiW,1), 'ITB/SPY 위치': round(a.A2_rs504,1),
        'SPY 1년 낙폭(저점)': f'{dd(SPY.close,t):+.1%}', 'QQQ 1년 낙폭(+6일)': f'{dd(Q,t6):+.1%}', 'SPY 1년 낙폭(+6일)': f'{dd(SPY.close,t6):+.1%}',
        'VIX(저점)': round(asof(VIX,t),1), 'VIX 63일 최고(+6일)': round(VIX[VIX.index<=t6].iloc[-63:].max(),1),
        'HY(저점)': asof(hy,t), 'HY 백분위': round(hy_pct(t)), 'HY 63일 변화bp': round((asof(hy,t)-hy[hy.index<=t].iloc[-64])*100),
        '10년물 정점일(±창)': pk2.date(), '정점→저점 거래일': len(TNX.loc[pk2:t])-1 if pk2 <= t else -(len(TNX.loc[t:pk2])-1),
        '10년물 정점 대비(+6일)bp': round((TNX.loc[t6]-tn.iloc[-252:].max())*100),
        '기준금리 6개월 변화': round(asof(ff,t)-ff[ff.index<=t].iloc[-127],2),
        'CPI 전년비': f'{yoy:.1%}', 'CPI 3개월 방향': '상승' if yoy > yoy3 else '하락',
        'WTI 63일 변화': f'{asof(oil,t)/oil[oil.index<=t].iloc[-64]-1:+.0%}', 'WTI': round(asof(oil,t)),
        '모기지': asof(mtg,t), '신규주택 재고개월': asof(hs, m)}
T = pd.DataFrame([row('2018-10-24','2018 Q4 (실패 저점)'), row('2023-10-25','2023-10 (진짜 바닥)'), row('2026-10-14','지금')]).set_index('사례').T
pd.set_option('display.width', 200); print(T.to_string())
