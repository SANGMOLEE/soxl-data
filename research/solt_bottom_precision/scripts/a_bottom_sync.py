# A. BTC 스윙 저점(1분 정밀) ↔ SOL 저점: 시차·낙폭배율·반등·이후 신저가 여부
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
TH=float(sys.argv[1]) if len(sys.argv)>1 else 0.15
bh=bars('BTC','1h'); sh=bars('SOL','1h'); b1=m1('BTC'); s1=m1('SOL')
bh=bh['2020-08-11':]; 
def zigzag(h, th):
    """시간봉 고가/저가 기반 zigzag. 반환 [(kind, ts, price)]"""
    piv=[]; mode=None; hi=h.h.iloc[0]; hi_t=h.index[0]; lo=h.l.iloc[0]; lo_t=h.index[0]
    for t,(hh,ll) in zip(h.index, h[['h','l']].values):
        if hh>hi: hi,hi_t=hh,t
        if ll<lo: lo,lo_t=ll,t
        if mode!='down' and ll<=hi*(1-th):
            piv.append(('H',hi_t,hi)); mode='down'; lo,lo_t=ll,t
        elif mode!='up' and hh>=lo*(1+th):
            if mode is not None: piv.append(('L',lo_t,lo))
            mode='up'; hi,hi_t=hh,t
    return piv
def exact_low(m, t_hour, span_h=1):
    w=m.l[t_hour:t_hour+pd.Timedelta(hours=span_h)-pd.Timedelta(minutes=1)]; return w.idxmin(), w.min()
piv=zigzag(bh,TH)
rows=[]
for i,(k,t,p) in enumerate(piv):
    if k!='L': continue
    th_=[x for x in piv[:i] if x[0]=='H']
    if not th_: continue
    _,t_hi,p_hi=th_[-1]
    tb,lb=exact_low(b1,t)                      # BTC 저점 분 단위
    def smin(a,b_): w=s1.l[tb+pd.Timedelta(minutes=a):tb+pd.Timedelta(minutes=b_)]; return w.idxmin(), w.min()
    ts72,ls72=smin(-72*60,72*60); ts24,ls24=smin(-24*60,24*60); ts2,ls2=smin(-120,120)
    s_at=s1.l[tb]                               # 같은 분 SOL 저가
    s_hi=s1.h[t_hi-pd.Timedelta(hours=24):tb].max()
    # 이후 90일 SOL 최저 (3일 뒤부터)
    fut=s1.l[tb+pd.Timedelta(days=3):tb+pd.Timedelta(days=90)]
    tf,lf=(fut.idxmin(),fut.min()) if len(fut) else (pd.NaT,np.nan)
    b_at_tf=b1.c.asof(tf) if pd.notna(tf) else np.nan
    bfut=b1.l[tb+pd.Timedelta(days=3):tb+pd.Timedelta(days=90)]
    # 투매형 판정: 저점 전 24시간 BTC 하락률, 저점 시간 거래량 / 이전 7일 시간 중앙값
    pre24=b1.c.asof(tb-pd.Timedelta(hours=24)); vol_ratio=bh.v[t]/bh.v[t-pd.Timedelta(days=7):t-pd.Timedelta(hours=1)].median()
    r1h=bh.c[t]/bh.c.asof(t-pd.Timedelta(hours=1))-1
    rows.append(dict(btc_low_utc=tb, btc_low=lb, btc_leg=lb/p_hi-1, leg_days=(tb-t_hi).days,
        btc_24h=lb/pre24-1, vol_x=vol_ratio,
        sol_low72_utc=ts72, lag72_min=(ts72-tb).total_seconds()/60, sol_low72=ls72, sol_at_btc_low_vs_low72=s_at/ls72-1,
        lag24_min=(ts24-tb).total_seconds()/60, lag2h_min=(ts2-tb).total_seconds()/60, sol_at_vs_low2h=s_at/ls2-1,
        sol_leg=ls72/s_hi-1, beta=np.log(ls72/s_hi)/np.log(lb/p_hi),
        sol_reb_24h=s1.h[ts72:ts72+pd.Timedelta(hours=24)].max()/ls72-1, btc_reb_24h=b1.h[tb:tb+pd.Timedelta(hours=24)].max()/lb-1,
        sol_lower_low_90d=lf/ls72-1 if pd.notna(lf) else np.nan, sol_ll_date=tf, sol_ll_days=(tf-tb).days if pd.notna(tf) else np.nan,
        btc_at_sol_ll_vs_btclow=b_at_tf/lb-1 if pd.notna(b_at_tf) else np.nan, btc_lower_low_90d=bfut.min()/lb-1 if len(bfut) else np.nan))
A=pd.DataFrame(rows)
A['type']=np.where((A.btc_24h<=-0.08)|(A.vol_x>=4),'투매형','조용한형')
A.to_csv(f'output/a_sync_th{int(TH*100)}.csv',index=False)
show=A[['btc_low_utc','btc_low','btc_leg','btc_24h','vol_x','type','lag72_min','lag2h_min','sol_at_btc_low_vs_low72','beta','sol_reb_24h','sol_lower_low_90d','sol_ll_days','btc_at_sol_ll_vs_btclow','btc_lower_low_90d']].copy()
show['btc_low_utc']=show.btc_low_utc.dt.strftime('%Y-%m-%d %H:%M')
print(f"== BTC 스윙 저점 (시간봉 zigzag {TH:.0%}), n={len(A)}")
print(show.round(3).to_string(index=False))
def summ(x,lab):
    print(f"\n[{lab}] n={len(x)}")
    print(f"  SOL ±72h 최저가 BTC 저점과 같은 시각(±30분): {(x.lag72_min.abs()<=30).mean():.0%},  ±2시간: {(x.lag72_min.abs()<=120).mean():.0%},  ±24시간: {(x.lag72_min.abs()<=1440).mean():.0%}")
    print(f"  SOL이 먼저(-) / 나중(+) 시차 중앙 {x.lag72_min.median():.0f}분,  BTC 저점 순간 SOL은 ±72h 최저보다 중앙 {x.sol_at_btc_low_vs_low72.median():+.1%} 위 (75% 분위 {x.sol_at_btc_low_vs_low72.quantile(.75):+.1%})")
    print(f"  낙폭 배율(로그) 중앙 {x.beta.median():.2f}, 24시간 반등 SOL {x.sol_reb_24h.median():+.1%} vs BTC {x.btc_reb_24h.median():+.1%}")
    ll=x.sol_lower_low_90d<0
    print(f"  이후 90일 내 SOL 신저가: {ll.mean():.0%}  (그중 BTC도 신저가였던 비율 {(x[ll].btc_at_sol_ll_vs_btclow<0).mean() if ll.any() else np.nan:.0%}), SOL 추가하락 중앙 {x[ll].sol_lower_low_90d.median() if ll.any() else np.nan:+.1%}")
summ(A,'전체'); summ(A[A.type=='투매형'],'투매형'); summ(A[A.type=='조용한형'],'조용한형')
