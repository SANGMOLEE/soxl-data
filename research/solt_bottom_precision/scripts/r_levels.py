# R3. BTC·ETH·SOL 실현가격과 역대 바닥 MVRV → 목표 가격대
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250)
E='data/ext/'
def daily(sym):
    d=m1(sym).resample('D').agg({'c':'last','v':'sum','qv':'sum','l':'min'}); d.index=d.index.tz_localize(None); return d.dropna()
def ew(d,hl): a=1-0.5**(1/hl); return d.qv.ewm(alpha=a,adjust=False).mean()/d.v.ewm(alpha=a,adjust=False).mean()
real={a:pd.read_csv(E+f'CM_{a}_REALIZED.csv',parse_dates=['date']).set_index('date').realized_price for a in ['BTC','ETH']}
now={a:m1(a).c.iloc[-1] for a in ['BTC','ETH','SOL']}; print("현재가:",{k:round(v,2) for k,v in now.items()},m1('SOL').index[-1])
# 1) 역대 바닥 MVRV (장중 저점 / 그날 실현가격)
print("\n== 역대 사이클 바닥의 MVRV (장중 저점 ÷ 실현가격)")
for a,days in [('BTC',['2015-01-14','2018-12-15','2020-03-13','2022-11-21']),('ETH',['2018-12-15','2020-03-13','2022-06-18'])]:
    for d in days:
        d=pd.Timestamp(d)
        lo=(m1(a).l[d.tz_localize('UTC'):d.tz_localize('UTC')+pd.Timedelta(days=1)].min() if d>=pd.Timestamp('2017-09-01') else 152.4)
        print(f"  {a} {d.date()}: 저점 ${lo:,.2f}, 실현가격 ${real[a].asof(d):,.2f}, MVRV {lo/real[a].asof(d):.2f}")
# 2) SOL 대리 실현가격: 지수가중 VWAP, 글래스노드 2025-03-11 $134로 보정
sd=daily('SOL'); anchor=pd.Timestamp('2025-03-11')
print("\n== SOL 대리 실현가격")
for hl in [180,365,540]:
    p=ew(sd,hl); f=p[anchor]/134.0
    est=p.iloc[-1]/f
    # BTC·ETH 현재 대리/실제 비율로도 보정 (참고)
    rb=ew(daily('BTC'),hl).iloc[-1]/real['BTC'].iloc[-1]; re_=ew(daily('ETH'),hl).iloc[-1]/real['ETH'].iloc[-1]
    print(f"  EW-VWAP 반감기 {hl}일: 현재 ${p.iloc[-1]:.1f} | 2025-03-11 값 ${p[anchor]:.1f} → 보정계수 {f:.2f} → SOL 실현가격 추정 ${est:.1f} | (BTC식 보정 ${p.iloc[-1]/rb:.1f}, ETH식 보정 ${p.iloc[-1]/re_:.1f})")
    if hl==365:
        sol_real=est; sol_hist=(p/f)
# SOL 2022 바닥의 MVRV(대리)
for d in ['2022-06-18','2022-11-21','2022-12-29','2026-06-06','2026-11-21']:
    d=pd.Timestamp(d); lo=m1('SOL').l[d.tz_localize('UTC'):d.tz_localize('UTC')+pd.Timedelta(days=1)].min(); print(f"  SOL {d.date()} 저점 ${lo:.2f} → 대리 MVRV {lo/sol_hist.asof(d):.2f} (대리 실현가격 ${sol_hist.asof(d):.1f})")
pd.Series({'BTC':real['BTC'].iloc[-1],'ETH':real['ETH'].iloc[-1],'SOL':sol_real}).to_csv('output/r_realized_now.csv')
