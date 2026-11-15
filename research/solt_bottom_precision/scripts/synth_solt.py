# 가상 SOLT: SOL 1분봉 → 미국 거래일 16:00 ET 종가 기준 2배 일일재조정 (주말·공휴일은 다음 거래일에 합산)
import sys; sys.path.insert(0,'scripts')
from common import *
from pandas.tseries.holiday import USFederalHolidayCalendar
COST=0.20
def build(cost=COST):
    s1=m1('SOL'); c=s1.c
    days=pd.bdate_range('2020-08-12','2026-11-13'); hol=USFederalHolidayCalendar().holidays('2020-01-01','2027-01-01')
    days=[d for d in days if d not in hol]
    closes=[]
    for d in days:
        t=pd.Timestamp(d.strftime('%Y-%m-%d')+' 16:00',tz='America/New_York').tz_convert('UTC')
        closes.append((t,c.asof(t-pd.Timedelta(minutes=1))))
    cl=pd.DataFrame(closes,columns=['t','S']).dropna().set_index('t')
    # 각 재조정 구간 (이전 종가, 이번 종가]의 SOL 고가/저가
    hi=s1.h.groupby(pd.cut(s1.index,bins=[cl.index[0]-pd.Timedelta(days=4)]+list(cl.index),right=True)).max().values
    lo=s1.l.groupby(pd.cut(s1.index,bins=[cl.index[0]-pd.Timedelta(days=4)]+list(cl.index),right=True)).min().values
    cl['Shi']=hi[:len(cl)]; cl['Slo']=lo[:len(cl)]
    nav=[1.0]; nh=[np.nan]; nl=[np.nan]
    for i in range(1,len(cl)):
        S0=cl.S.iloc[i-1]; dtd=(cl.index[i]-cl.index[i-1]).days; n0=nav[-1]; f=np.exp(-cost*dtd/365)
        nav.append(max(n0*(1+2*(cl.S.iloc[i]/S0-1))*f,1e-9)); nh.append(n0*(1+2*(cl.Shi.iloc[i]/S0-1))); nl.append(max(n0*(1+2*(cl.Slo.iloc[i]/S0-1)),1e-9))
    cl['nav']=nav; cl['nav_hi']=nh; cl['nav_lo']=nl
    return cl
if __name__=='__main__':
    cl=build(); cl.to_parquet('data/synth_solt_daily.parquet')
    # 실제 SOLT와 비교 (2025-03-21 ~)
    import pandas as pd
    a=pd.read_csv('/home/user/soxl-data/research/solt_strategy_after_btc_bottom/data/SOLT.csv',parse_dates=['date']).set_index('date').adj_close
    x=cl.copy(); x.index=x.index.tz_convert('America/New_York').normalize().tz_localize(None)
    j=pd.concat([x.nav,a],axis=1,keys=['syn','act']).dropna()
    j=j/j.iloc[0]; print("가상 vs 실제 SOLT (2025-03-20~):", j.iloc[-1].round(3).to_dict(), " 로그 RMSE", round(float(np.sqrt((np.log(j.syn/j.act)**2).mean())),3))
    for a_,b_ in [('2025-04-08','2025-09-18'),('2025-10-06','2026-02-05'),('2026-06-05','2026-10-08')]:
        print(a_,b_,"실제 %.2f  가상 %.2f"%(j.act[b_]/j.act[a_], j.syn[b_]/j.syn[a_]))
