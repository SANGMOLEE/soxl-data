# 범용 엔진: 임의 자산 1분봉 → 가상 2배(미국 16:00 ET 재조정) / 진입·손절·목표 시뮬레이션
import sys; sys.path.insert(0,'scripts')
from common import *
from pandas.tseries.holiday import USFederalHolidayCalendar
HOL=USFederalHolidayCalendar().holidays('2015-01-01','2028-01-01')
def load(sym):
    p=f"{D}/{sym}USDT_1m.parquet"
    if os.path.exists(p): return m1(sym)
    for suf in ['_1m_win2','_1m_win']:
        p=f"{D}/{sym}USDT{suf}.parquet"
        if os.path.exists(p): return pd.read_parquet(p).set_index('ts').sort_index()
    return None
def nav_build(m, start, end, cost=0.20, L=2.0):
    days=[d for d in pd.bdate_range(start,end) if d not in HOL]
    ts=[pd.Timestamp(d.strftime('%Y-%m-%d')+' 16:00',tz='America/New_York').tz_convert('UTC') for d in days]
    c=m.c; S=[c.asof(t-pd.Timedelta(minutes=1)) for t in ts]
    cl=pd.DataFrame({'S':S},index=pd.DatetimeIndex(ts,name='t')).dropna()
    cl=cl[cl.index<=m.index[-1]]
    nav=[1.0]
    for i in range(1,len(cl)):
        dtd=(cl.index[i]-cl.index[i-1]).days
        nav.append(max(nav[-1]*(1+L*(cl.S.iloc[i]/cl.S.iloc[i-1]-1))*np.exp(-cost*dtd/365),1e-12))
    cl['nav']=nav; return cl
def nav_at(cl,t,S,L=2.0):
    i=cl.index.searchsorted(t,side='right')-1
    if i<0: return np.nan
    return cl.nav.iloc[i]*(1+L*(S/cl.S.iloc[i]-1))
def s_for_nav(cl,t,target_nav,L=2.0):
    i=cl.index.searchsorted(t,side='right')-1; return cl.S.iloc[i]*(1+(target_nav/cl.nav.iloc[i]-1)/L)
def h1_of(m): return m.resample('1h').agg({'o':'first','h':'max','l':'min','c':'last'}).dropna()
def is_open(t): return session_of(t)!='weekend_closed'
def manage(h1, cl, t_in, S_in, k=2.0, stop=None, T_days=365, tc=0.002):
    """보유 관리: 시간봉 단위. 반환 dict(m, how, days, mae)"""
    n0=nav_at(cl,t_in,S_in)
    if not np.isfinite(n0) or n0<=0: return None
    seg=h1[t_in+pd.Timedelta(hours=1):t_in+pd.Timedelta(days=T_days)]
    mae=0.0
    for t,r in seg.iterrows():
        lo_nav=nav_at(cl,t,r.l)/n0-1; mae=min(mae,lo_nav)
        if not is_open(t): continue
        if stop is not None and r.l<=stop:
            Sx=min(stop,r.o); return dict(m=nav_at(cl,t,Sx)/n0*(1-tc)**2,how='손절',days=(t-t_in).total_seconds()/86400,mae=mae)
        S_t=s_for_nav(cl,t,k*n0)
        if r.h>=S_t:
            Sx=max(S_t,r.o); return dict(m=nav_at(cl,t,Sx)/n0*(1-tc)**2,how='목표',days=(t-t_in).total_seconds()/86400,mae=mae)
    if len(seg)==0: return None
    t=seg.index[-1]; return dict(m=nav_at(cl,t,seg.c.iloc[-1])/n0*(1-tc)**2,how='기한',days=(t-t_in).total_seconds()/86400,mae=mae)
def confirm_rule(h1, cl, w_start, w_end, x=0.05, hold_h=1, s=0.02, k=2.0, tries=4, use_stop=True, T_days=365):
    """창 안에서: 누적 최저 L 추적 → L×(1+x) 역지정가 매수 → (손절 L×(1-s)) → 목표 k. 손절 시 재무장."""
    L=np.inf; Lt=None; out=[]; t=w_start
    seg=h1[w_start:w_end]
    i=0; idx=seg.index
    while i<len(idx) and len(out)<tries:
        t=idx[i]; r=seg.iloc[i]
        if r.l<L: L=r.l; Lt=t; i+=1; continue
        trig=L*(1+x)
        if is_open(t) and (t-Lt)>=pd.Timedelta(hours=hold_h) and r.h>=trig:
            S_in=max(trig,r.o); res=manage(h1,cl,t,S_in,k=k,stop=(L*(1-s) if use_stop else None),T_days=T_days)
            if res is None: break
            res.update(entry_t=t,S_in=S_in,L=L); out.append(res)
            if res['how']!='손절': break
            # 손절 후: 그 시점 이후부터 다시 저점 추적
            t_exit=t+pd.Timedelta(days=res['days']); j=idx.searchsorted(t_exit)
            if j>=len(idx): break
            i=j; L=seg.l.iloc[i]; Lt=idx[i]; continue
        i+=1
    return out
