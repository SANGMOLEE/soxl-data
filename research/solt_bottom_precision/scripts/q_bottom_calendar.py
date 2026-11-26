# Q. 역대 사이클 바닥: 요일·시각·SOLT 거래가능 여부 + 공통점 (BTC 비트스탬프 시간봉 2011~, 바이낸스 1분봉 2017~)
import sys; sys.path.insert(0,'scripts')
from common import *
from scipy.stats import binomtest
pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
E='data/ext/'
bh=pd.read_csv(E+'BTC_BITSTAMP_1H.csv.gz',parse_dates=['date']).set_index('date').sort_index(); bh.index=bh.index.tz_localize('UTC')
bh=bh[(bh.low>0)&(bh.high>=bh.low)]
oc=pd.read_csv(E+'BTC_ONCHAIN.csv',parse_dates=['date']).set_index('date')
fng=pd.read_csv(E+'FNG.csv',parse_dates=['date']).set_index('date').value
fund=pd.read_csv(E+'FUNDING_BINANCE.csv',parse_dates=['date']).set_index('date').rate
b1=m1('BTC')
bd=bh.close.resample('D').last(); bdh=bh.high.resample('D').max(); bdl=bh.low.resample('D').min(); bdv=bh.volume.resample('D').sum()
for _s in (bd,bdh,bdl,bdv): _s.index=_s.index.tz_localize(None)
_bn=b1.resample('D').agg({'h':'max','l':'min','c':'last','v':'sum'}); _bn.index=_bn.index.tz_localize(None)
CUT=pd.Timestamp('2017-09-01')
bd=pd.concat([bd[bd.index<CUT],_bn.c[_bn.index>=CUT]]); bdh=pd.concat([bdh[bdh.index<CUT],_bn.h[_bn.index>=CUT]])
bdl=pd.concat([bdl[bdl.index<CUT],_bn.l[_bn.index>=CUT]]); bdv=pd.concat([bdv[bdv.index<CUT],_bn.v[_bn.index>=CUT]])
_hvb=b1.v.resample('1h').sum(); HV=pd.concat([bh.volume[bh.index<pd.Timestamp('2017-09-01',tz='UTC')],_hvb[_hvb.index>=pd.Timestamp('2017-09-01',tz='UTC')]])
CL=pd.concat([bh.close[bh.index<pd.Timestamp('2017-09-01',tz='UTC')],b1.c.resample('1h').last()[lambda s: s.index>=pd.Timestamp('2017-09-01',tz='UTC')]])
wma200=bd.resample('W').last().rolling(200,min_periods=150).mean().reindex(bd.index,method='ffill')
HALV=[pd.Timestamp(x) for x in ['2012-11-28','2016-07-09','2020-05-11','2024-04-19','2028-04-15']]
CYC=[('2011 사이클','2011-06-08','2012-03-01',None),('2015 사이클','2013-12-04','2015-06-01','2015-01-04 Bitstamp 해킹'),
     ('2018 사이클','2017-12-17','2019-03-01','2018-11-15 BCH 하드포크 분쟁'),('2020 급락','2019-06-26','2020-05-01','2020-03-12 코로나 폭락'),
     ('2022 사이클','2021-11-10','2023-03-01','2022-11-08 FTX 붕괴'),('2026 (진행 중)','2025-10-06','2026-11-26',None)]
def exact_low(a,b):
    """비트스탬프 시간봉 최저 → 2017-08 이후면 바이낸스 1분봉으로 분 단위 보정"""
    if a>=pd.Timestamp('2017-09-01',tz='UTC'):
        m=b1.l[a:b]; return m.idxmin(),m.min(),'Binance 1m'
    w=bh.low[a:b]; t=w.idxmin(); p=w.min(); src='Bitstamp 1h'
    if t>pd.Timestamp('2017-09-01',tz='UTC'):
        m=b1.l[t-pd.Timedelta(hours=3):t+pd.Timedelta(hours=3)]; t,p,src=m.idxmin(),m.min(),'Binance 1m'
    return t,p,src
rows=[]
for name,ath,end,shock in CYC:
    ath=pd.Timestamp(ath,tz='UTC'); end=pd.Timestamp(end,tz='UTC')
    _w=bh.high[ath-pd.Timedelta(days=10):ath+pd.Timedelta(days=10)]
    if len(_w): hi_t=_w.idxmax(); hi=bh.high[hi_t]
    else: hi_t=ath; hi=31.91                       # 2011-06-08 마운트곡스 고점 (비트스탬프 자료 이전)
    t,p,src=exact_low(hi_t,end)
    d=t.normalize().tz_localize(None); et=t.tz_convert('America/New_York'); kst=t.tz_convert('Asia/Seoul')
    dclose_low=bd[max(hi_t.tz_localize(None).normalize(),bd.index[0]):end.tz_localize(None)].idxmin()
    pre24=CL.asof(t-pd.Timedelta(hours=24)); pre7=CL.asof(t-pd.Timedelta(days=7)); pre30=CL.asof(t-pd.Timedelta(days=30))
    _med=HV[t-pd.Timedelta(days=30):t-pd.Timedelta(hours=1)].median(); vx=HV[t.floor('h')]/_med if _med>0 else np.nan
    # 저점 일봉 모양
    rng=bdh[d]-bdl[d]; wick=(bd[d]-bdl[d])/rng if rng>0 else np.nan
    # 저점 전 30일 안의 최대 하루 하락(투매일)
    r=bd.pct_change(); pre=r[d-pd.Timedelta(days=30):d]; cap_d=pre.idxmin(); cap_r=pre.min()
    nxt=(bdh[d:d+pd.Timedelta(days=7)].max()/p-1)
    rp=oc.realized_price.asof(d); mv=p/rp
    mvmin_t=oc.mvrv[d-pd.Timedelta(days=60):d+pd.Timedelta(days=60)].idxmin()
    f_at=fng.asof(d) if d>=fng.index[0] else np.nan
    f_min_t=fng[d-pd.Timedelta(days=30):d+pd.Timedelta(days=30)].idxmin() if d>=fng.index[0] else None
    fu=fund[d-pd.Timedelta(days=7):d].mean()*3*365 if d>=fund.index[0] else np.nan
    nh=[h for h in HALV if h>d][0]; ph=[h for h in HALV if h<=d]
    rows.append(dict(사이클=name,저점_UTC=t.strftime('%Y-%m-%d %H:%M'),요일_UTC=t.strftime('%a'),미동부=et.strftime('%a %H:%M'),한국=kst.strftime('%a %H:%M'),
        SOLT시간대=session_of(t),원천=src,저점가=round(p,2),종가최저일=dclose_low.strftime('%Y-%m-%d %a'),
        고점후_일=(t-hi_t).days,고점대비=p/hi-1,직전24h=p/pre24-1,직전7일=p/pre7-1,직전30일=p/pre30-1,저점시간_거래량배수=vx,
        일봉아래꼬리비율=wick,MVRV_자료일=oc.index[oc.index<=d][-1].strftime('%m-%d'),공포탐욕_자료일=(fng.index[fng.index<=d][-1].strftime('%m-%d') if d>=fng.index[0] else None),최대투매일=f"{cap_d.strftime('%m-%d')} ({cap_r:+.0%})",투매일에서저점까지_일=(d-cap_d).days,
        이후7일반등=nxt,MVRV=mv,실현가격대비=p/rp-1,MVRV최저일=mvmin_t.strftime('%Y-%m-%d'),공포탐욕=f_at,공포최저일=(f_min_t.strftime('%Y-%m-%d') if f_min_t is not None else None),
        펀딩7일연율=fu,주200선대비=bd[d]/wma200[d]-1,다음반감기까지_일=(nh-d).days,직전반감기후_일=((d-ph[-1]).days if ph else np.nan),충격사건=shock or '-',
        충격에서저점까지_일=((d-pd.Timestamp(shock[:10])).days if shock else np.nan)))
C=pd.DataFrame(rows); C.to_csv('output/q_cycle_bottoms.csv',index=False)
print("== 역대 BTC 사이클 바닥 (장중 최저)")
print(C.T.to_string())
# ---- 비교군: 약세장 주요 저점 (고점 대비 -45% 이하 + 20% 반등) 2013~ ----
def zz_lows(x,th=0.20):
    lows=[]; mode='up'; hi=x.iloc[0]; lo=x.iloc[0]; lo_i=x.index[0]
    for t,v in x.items():
        if mode=='up':
            if v>hi: hi=v
            if v<=hi*(1-th): mode='down'; lo=v; lo_i=t
        else:
            if v<lo: lo=v; lo_i=t
            if v>=lo*(1+th): lows.append(lo_i); mode='up'; hi=v
    return lows
c=bd['2013-06':].dropna(); ath_=c.cummax(); L=[t for t in zz_lows(c) if c[t]/ath_[t]-1<=-0.45]
cyc_days={pd.Timestamp(x[:10]) for x in C.저점_UTC}
rows=[]
for d in L:
    w=bh.low[pd.Timestamp(d,tz='UTC')-pd.Timedelta(days=1):pd.Timestamp(d,tz='UTC')+pd.Timedelta(days=2)]; t=w.idxmin()
    if t>pd.Timestamp('2017-09-01',tz='UTC'):
        m=b1.l[t-pd.Timedelta(hours=3):t+pd.Timedelta(hours=3)]; t=m.idxmin()
    rows.append(dict(t=t,dow=t.strftime('%a'),sess=session_of(t),cycle_bottom=any(abs((t.normalize().tz_localize(None)-x).days)<=1 for x in cyc_days),
                     dd=c[d]/ath_[d]-1))
Z=pd.DataFrame(rows); Z.to_csv('output/q_bear_lows.csv',index=False)
print(f"\n== 비교군: 약세장 주요 저점 {len(Z)}건 (고점 대비 -45% 이하, 이후 20% 반등; 2013~2026)")
print(Z.assign(t=Z.t.dt.strftime('%Y-%m-%d %H:%M')).to_string(index=False))
wk=Z.dow.isin(['Sat','Sun']).sum(); n=len(Z)
print(f"\n달력 주말(UTC 토·일) 저점 {wk}/{n} = {wk/n:.0%} (무작위 기대 28.6%, 이항검정 p={binomtest(wk,n,2/7).pvalue:.2f})")
cl=(Z.sess=='weekend_closed').sum(); print(f"SOLT 거래 불가 시간(금 20:00~일 20:00 ET) 저점 {cl}/{n} = {cl/n:.0%} (무작위 기대 28.6%, p={binomtest(cl,n,2/7).pvalue:.2f})")
print("요일 분포(UTC):",Z.dow.value_counts().reindex(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']).fillna(0).astype(int).to_dict())
print("SOLT 시간대 분포:",Z.sess.value_counts().to_dict())
# ---- 형태별(투매형/조용한형) 주말 비율: 2020~2026 BTC 스윙저점 48건 ----
A=pd.read_csv('output/a_sync_th15.csv',parse_dates=['btc_low_utc'])
A['wk']=[session_of(x)=='weekend_closed' for x in A.btc_low_utc]; A['dow']=A.btc_low_utc.dt.strftime('%a')
print("\n== 2020~2026 BTC 스윙저점 (15% 기준) 형태별 SOLT 거래불가(주말) 비율")
for ty,g in A.groupby('type'): print(f"  {ty}: {int(g.wk.sum())}/{len(g)} = {g.wk.mean():.0%} (p={binomtest(int(g.wk.sum()),len(g),2/7).pvalue:.2f}); 요일 {g.dow.value_counts().to_dict()}")
# ---- ETH·SOL 사이클 바닥 ----
print("\n== ETH·SOL 사이클 바닥 (바이낸스 1분봉)")
for sym,a_,b_ in [('ETH','2018-11-01','2019-02-01'),('ETH','2020-03-01','2020-04-01'),('ETH','2022-05-01','2022-12-31'),('SOL','2022-11-01','2023-01-31')]:
    m=m1(sym).l[a_:b_]; t=m.idxmin()
    print(f"  {sym} {t.strftime('%Y-%m-%d %H:%M')} UTC {t.strftime('%a')} | 미동부 {t.tz_convert('America/New_York').strftime('%a %H:%M')} | 한국 {t.tz_convert('Asia/Seoul').strftime('%a %H:%M')} | SOLT시간대 {session_of(t)} | ${m.min():,.2f}")
