# B. SOL 저점 순간 SOLT를 실제로 얼마에 살 수 있었나 (24시간 SOLT 시간봉 = 야후 프리/정규/애프터 + BOATS 야간)
import sys; sys.path.insert(0,'scripts')
from common import *
from a_bottom_sync_lib import zigzag
pd.set_option('display.width',250)
s1=m1('SOL'); sh=bars('SOL','1h')
S=solt24()
# 1) 정규장 종가(16:00 ET) 시점 SOLT 종가와 SOL 가격 → 이론값 기준점
reg=S[(S.src=='yahoo')&(S.et.dt.strftime('%H:%M')=='15:30')].copy()     # 15:30~16:00 정규 마지막 봉
reg['close_utc']=reg.index+pd.Timedelta(minutes=30)
reg['sol_at_close']=[s1.c.asof(t-pd.Timedelta(minutes=1)) for t in reg.close_utc]
ref=reg.set_index('close_utc')[['c','sol_at_close']].rename(columns={'c':'P0','sol_at_close':'S0'})
def fair_at(t, sol_price):
    r=ref[ref.index<=t]
    if r.empty: return np.nan
    P0,S0=r.iloc[-1]; return P0*(1+2*(sol_price/S0-1))
# 2) 시간대별 실제 SOLT 가격 vs 이론값 괴리
hm=S.et.dt.strftime('%H:%M')
S['bar_end']=S.index+pd.to_timedelta(np.where((S.src=='yahoo')&hm.isin(['09:00','15:30']),30,60),unit='m')
S['sess']=[session_of(t) for t in S.index]
dev=[]
for t,row in S.iloc[::3].iterrows():           # 표본 1/3
    te=row.bar_end-pd.Timedelta(minutes=1); sp=s1.c.asof(te); f=fair_at(te,sp)
    if np.isfinite(f): dev.append(dict(sess=row.sess,dev=row.c/f-1))
dev=pd.DataFrame(dev)
print("== SOLT 실제 종가 / 이론값 - 1 (시간대별)")
print(dev.groupby('sess').dev.describe(percentiles=[.1,.5,.9]).round(4).to_string())
# 3) SOL 스윙 저점별 매수 가능 가격
out=[]
for th in [0.10,0.15]:
    piv=zigzag(sh['2025-03-21':],th)
    for k,t,p in piv:
        if k!='L': continue
        w=s1.l[t:t+pd.Timedelta(minutes=59)]; ts=w.idxmin(); ls=w.min()
        ses=session_of(ts); f=fair_at(ts,ls)
        # 같은 시간(또는 다음 개장) SOLT 봉
        after=S[S.bar_end>ts]
        first=after.iloc[0]; same_hour=(first.name<=ts)
        win24=S[(S.bar_end>ts)&(S.index<=ts+pd.Timedelta(hours=24))]
        win72=S[(S.index>=ts-pd.Timedelta(days=3))&(S.index<=ts+pd.Timedelta(days=3))]
        out.append(dict(th=th,sol_low_utc=ts,sol_low=ls,et=ts.tz_convert('America/New_York').strftime('%a %m-%d %H:%M'),sess=ses,fair=f,
            solt_first_open_bar=first.name.tz_convert('America/New_York').strftime('%a %H:%M'),same_hour=same_hour,
            first_bar_low_vs_fair=first.l/f-1, first_bar_open_vs_fair=first.o/f-1,
            best24h_vs_fair=win24.l.min()/f-1, solt_low72=win72.l.min(), solt_low72_at=win72.l.idxmin().tz_convert('America/New_York').strftime('%m-%d %H:%M'),
            solt_low72_vs_fair=win72.l.min()/f-1))
O=pd.DataFrame(out); O.to_csv('output/b_solt_exec.csv',index=False)
for th in [0.10,0.15]:
    x=O[O.th==th]; print(f"\n== SOL 스윙저점 (zigzag {th:.0%}) n={len(x)} — 이론 SOLT(그 순간 SOL 저점 기준) 대비 실제 매수가")
    print(x[['et','sess','sol_low','fair','solt_first_open_bar','same_hour','first_bar_low_vs_fair','first_bar_open_vs_fair','best24h_vs_fair','solt_low72','solt_low72_at','solt_low72_vs_fair']].round(3).to_string(index=False))
    print("  시간대 분포:",x.sess.value_counts().to_dict())
    for lab,g in [('개장 중 저점',x[x.sess!='weekend_closed']),('주말 저점',x[x.sess=='weekend_closed'])]:
        if len(g): print(f"  {lab} n={len(g)}: 첫 거래가능 봉 저가 중앙 {g.first_bar_low_vs_fair.median():+.1%}, 시가 {g.first_bar_open_vs_fair.median():+.1%}, 24시간 내 최저 {g.best24h_vs_fair.median():+.1%}")
# 4) 2020-08 이후 전체 SOL 스윙저점의 시간대 분포 (SOLT가 있었다면)
allp=[]
for th in [0.10,0.15,0.20]:
    for k,t,p in zigzag(sh,th):
        if k=='L':
            w=s1.l[t:t+pd.Timedelta(minutes=59)]; allp.append(dict(th=th,ts=w.idxmin(),sess=session_of(w.idxmin())))
P=pd.DataFrame(allp)
print("\n== 2020-08 이후 SOL 스윙저점의 시간대 분포 (SOLT 24시간 체계 가정)")
print(P.groupby('th').sess.value_counts(normalize=True).unstack().round(2).to_string())
print(P.groupby('th').size().to_string())
