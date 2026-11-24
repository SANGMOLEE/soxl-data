# K. "BTC 저점 = SOLT 저점?" 분해: (1) SOL 타이밍 (2) 2배 감가 (3) 거래시간(주말)
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',260); pd.set_option('display.max_columns',30)
cl=pd.read_parquet('data/synth_solt_daily.parquet'); s1=m1('SOL'); b1=m1('BTC')
sh=bars('SOL','1h')
# 시간봉 단위 가상 SOLT 저가/종가
i=cl.index.searchsorted(sh.index,side='right')-1; ok=i>=0
H=sh[ok].copy(); ii=i[ok]
H['nav_l']=cl.nav.values[ii]*(1+2*(H.l.values/cl.S.values[ii]-1)); H['nav_c']=cl.nav.values[ii]*(1+2*(H.c.values/cl.S.values[ii]-1))
H['nav_l']=H.nav_l.clip(lower=1e-12); H['open']=[session_of(t)!='weekend_closed' for t in H.index]
def nav_at(t,S):
    j=cl.index.searchsorted(t,side='right')-1; return cl.nav.iloc[j]*(1+2*(S/cl.S.iloc[j]-1))
def open_time(t):
    if session_of(t)!='weekend_closed': return t
    et=t.tz_convert('America/New_York'); o=(et+pd.Timedelta(days=(6-et.weekday())%7)).normalize()+pd.Timedelta(hours=20)
    if o<et: o+=pd.Timedelta(days=7)
    return o.tz_convert('UTC')
A=pd.read_csv('output/a_sync_th15.csv',parse_dates=['btc_low_utc'])
ev=list(zip(A.btc_low_utc,A['type']))
ev+= [(pd.Timestamp(x,tz='UTC'),'조용한형') for x in ['2022-11-21 21:52','2022-12-30 14:49']]
ev+= [(pd.Timestamp(x,tz='UTC'),'투매형') for x in ['2026-11-15 01:45','2026-11-21 06:17']]
ev=sorted(set(ev))
BEAR=[('2021-11-10','2023-01-31'),('2025-10-06','2026-12-31')]
def phase(t): return '약세장' if any(pd.Timestamp(a,tz='UTC')<=t<=pd.Timestamp(b,tz='UTC') for a,b in BEAR) else '강세장/조정'
rows=[]
for tb,typ in ev:
    if tb<pd.Timestamp('2020-09-15',tz='UTC'): continue
    Sb=s1.l[tb]; Vb=nav_at(tb,Sb)
    if Vb<=0: continue
    tx=open_time(tb); Sx=Sb if tx==tb else s1.c.asof(tx); Vx=nav_at(tx,Sx)
    end=min(tb+pd.Timedelta(days=90),H.index[-1]); horizon=(end-tb).days
    W=H[tb-pd.Timedelta(days=30):end]; Wa=H[tb:end]; Wo=Wa[Wa.open]
    tmin=W.nav_l.idxmin(); vmin=W.nav_l.min()
    tmin_a=Wo.nav_l.idxmin(); vmin_a=Wo.nav_l.min()                          # 매수 뒤 거래가능 시간의 SOLT 최저
    s_min90=s1.l[tb:end].min()
    sol_at_tmin_a=Wo.l[tmin_a]
    later_lower=vmin_a<Vx*0.98
    cause='-' if not later_lower else ('SOL 신저가' if sol_at_tmin_a<Sb*0.995 else '감가(SOL은 더 높음)')
    rows.append(dict(btc_low=tb,type=typ,phase=phase(tb),sess=session_of(tb),horizon=horizon,
        exec_cost=Vx/Vb-1, solt_min_when=('같은날' if abs((tmin-tb).total_seconds())<=86400 else ('이전' if tmin<tb else '이후')),
        solt_min_days=(tmin-tb).total_seconds()/86400, buy_vs_later_min=Vx/vmin_a-1, later_lower=later_lower, cause=cause,
        sol_later_dd=s_min90/Sb-1, solt_later_dd=vmin_a/Vx-1, sol_at_soltmin_vs_Sb=sol_at_tmin_a/Sb-1,
        mae10=(vmin_a/Vx-1)<=-0.10, mae20=(vmin_a/Vx-1)<=-0.20))
K=pd.DataFrame(rows); K.to_csv('output/k_btc_vs_solt.csv',index=False)
show=K.copy(); show['btc_low']=show.btc_low.dt.strftime('%Y-%m-%d %H:%M')
print("== BTC 저점별: SOLT를 BTC 저점(체결가능 시점)에 샀을 때, 이후 90일 SOLT 최저와의 관계 (가상 SOLT, 시간봉)")
print(show[['btc_low','type','phase','sess','exec_cost','solt_min_when','solt_min_days','solt_later_dd','sol_later_dd','sol_at_soltmin_vs_Sb','cause']].round(3).to_string(index=False))
def summ(x,lab):
    n=len(x); ll=x.later_lower
    print(f"\n[{lab}] n={n}")
    print(f"  SOLT의 (전30~후90일) 최저가 BTC 저점 당일: {(x.solt_min_when=='같은날').mean():.0%}, 이전: {(x.solt_min_when=='이전').mean():.0%}, 이후: {(x.solt_min_when=='이후').mean():.0%}")
    print(f"  매수 뒤 90일 안에 SOLT가 매수가보다 2% 이상 더 낮게 거래: {ll.mean():.0%}  → 원인: SOL 신저가 {(x.cause=='SOL 신저가').mean():.0%}, 감가만으로(SOL은 더 높음) {(x.cause=='감가(SOL은 더 높음)').mean():.0%}")
    print(f"  -10% 이상 더 빠짐 {x.mae10.mean():.0%}, -20% 이상 {x.mae20.mean():.0%};  추가하락 중앙 SOLT {x.solt_later_dd.median():+.1%} vs SOL {x.sol_later_dd.median():+.1%}")
    print(f"  주말 저점 비용(체결가능 시점 SOLT / 저점 순간 이론가): 중앙 {x[x.sess=='weekend_closed'].exec_cost.median():+.1%} (주말 {int((x.sess=='weekend_closed').sum())}건)")
summ(K,'전체'); summ(K[K.phase=='약세장'],'약세장'); summ(K[K.type=='투매형'],'투매형'); summ(K[K.type=='조용한형'],'조용한형')
