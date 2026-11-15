# E. 유튜브 '매매법아카이브' 바닥 포착형 매매법 5종을 SOL→가상 SOLT로 검증
import sys; sys.path.insert(0,'scripts')
from d_engine import *
pd.set_option('display.width',260)
ASSET=sys.argv[1] if len(sys.argv)>1 else 'SOL'
m=load(ASSET); m=m['2020-08-12':'2026-11-13']
cl=nav_build(m,'2020-08-12','2026-11-13'); h1=h1_of(m)
def ohlc(rule): return m.resample(rule,label='left',closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum','tbv':'sum'}).dropna()
def rsi(c,n=14):
    d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean(); return 100-100/(1+up/dn)
def bull_engulf(b): return (b.c>b.o)&(b.c.shift(1)<b.o.shift(1))&(b.o<=b.c.shift(1))&(b.c>=b.o.shift(1))
def bear_engulf(b): return (b.c<b.o)&(b.c.shift(1)>b.o.shift(1))&(b.o>=b.c.shift(1))&(b.c<=b.o.shift(1))
def pivots(b,n):
    """확정 시점(i+n 봉 종가)에만 알 수 있는 스윙 고/저"""
    hi=b.h.rolling(2*n+1,center=True).max(); lo=b.l.rolling(2*n+1,center=True).min()
    ph=b.h[(b.h==hi)]; pl=b.l[(b.l==lo)]
    step=b.index[1]-b.index[0]
    return [(t+(n+1)*step,t,v) for t,v in ph.items()], [(t+(n+1)*step,t,v) for t,v in pl.items()]
SIG={}
# 1) RSI 쌍바닥 (1h)
b=ohlc('1h'); r=rsi(b.c); mid=b.c.rolling(20).mean(); sd=b.c.rolling(20).std(); lbb=mid-2*sd
be=bull_engulf(b); se=bear_engulf(b); red3=(b.c<b.o)&(b.c.shift(1)<b.o.shift(1))&(b.c.shift(2)<b.o.shift(2))
setup=(r<30)&(b.c<lbb)&(se|red3)
out=[]; i=0; idx=b.index; n=len(b); arr_be=be.values; arr_setup=setup.values
while i<n:
    if not arr_setup[i]: i+=1; continue
    s=i; j=s+1
    while j<n and j<s+48 and not arr_be[j]: j+=1
    if j>=n or j>=s+48: i=s+1; continue
    e1=j; k=e1+2; L2=np.inf; L2i=None; done=False
    while k<n and k<e1+72:
        if b.l.iloc[k-1]<L2: L2=b.l.iloc[k-1]; L2i=k-1
        if arr_be[k] and L2i is not None and b.l.iloc[L2i]>=lbb.iloc[L2i]:
            out.append((idx[k]+pd.Timedelta(hours=1),b.c.iloc[k],L2)); done=True; break
        k+=1
    i=k+1 if done else s+1
SIG['① RSI 쌍바닥(1h)']=out
# 2) CHoCH + 매물대 되돌림 (4h)
b=ohlc('4h'); PH,PL=pivots(b,3); vs=b.v.rolling(20).mean().shift(1); out=[]
ph_conf=sorted(PH); pl_conf=sorted(PL); used=set()
step=pd.Timedelta(hours=4)
for i in range(30,len(b)):
    t=b.index[i]; tc=t+step
    phs=[x for x in ph_conf if x[0]<=t]; pls=[x for x in pl_conf if x[0]<=t]
    if len(phs)<1 or len(pls)<2: continue
    last_ph=phs[-1]
    if last_ph[1] in used: continue
    down=pls[-1][2]<pls[-2][2]
    if down and b.c.iloc[i]>last_ph[2] and b.v.iloc[i]>1.5*vs.iloc[i]:
        used.add(last_ph[1])
        seg=b[last_ph[1]:t]; tl=seg.l.idxmin(); pre=b[:tl]; pre=pre[pre.c<pre.o]
        if pre.empty: continue
        ob=pre.iloc[-1]; box_lo,box_hi=ob.l,ob.h
        for j in range(i+1,min(i+31,len(b))):
            bj=b.iloc[j]
            if bj.l<=box_hi and bj.c>bj.o and bj.c>=box_lo:
                out.append((b.index[j]+step,bj.c,min(box_lo,bj.l))); break
            if bj.c<box_lo: break
SIG['② CHoCH+매물대 되돌림(4h)']=out
# 3) 피보나치 황금구간 (1h)
b=ohlc('1h'); PH,PL=pivots(b,3); out=[]; ph_conf=sorted(PH); pl_conf=sorted(PL)
k_ph=0; last_used=None
for ct,pt,B in ph_conf:
    # 이 고점 B 이전의 스윙 저점 A, 그리고 그 전 스윙 고점이 B보다 낮지 않으면(하락 후 구조 전환) 성립
    prev_ph=[x for x in ph_conf if x[1]<pt]; lows=[x for x in pl_conf if x[1]<pt and x[0]<=ct]
    if not prev_ph or not lows: continue
    A_t,A=lows[-1][1],lows[-1][2]
    if not (prev_ph[-1][1]<A_t and B>prev_ph[-1][2]): continue      # A 이후 직전 고점 돌파 = 구조 전환
    if last_used==A_t: continue
    zt=B-0.5*(B-A); zb=B-0.618*(B-A)
    seg=b[ct:ct+pd.Timedelta(hours=72)]
    for t,row in seg.iterrows():
        if row.c<A: break
        if row.l<=zt and row.c>=zb and row.c>row.o and min(row.o,row.c)>row.l:
            out.append((t+pd.Timedelta(hours=2),b.o.asof(t+pd.Timedelta(hours=1)),A*0.998)); last_used=A_t; break
SIG['③ 피보나치 황금구간(1h)']=out
# 4) 하락추세선 돌파 (4h)
b=ohlc('4h'); PH,_=pivots(b,3); out=[]; ph_conf=sorted(PH); used=set()
for i in range(30,len(b)):
    t=b.index[i]; phs=[x for x in ph_conf if x[0]<=t]
    if len(phs)<2: continue
    (c1,t1,v1),(c2,t2,v2)=phs[-2],phs[-1]
    if not v2<v1 or (t1,t2) in used: continue
    slope=(v2-v1)/((t2-t1)/step); line=v2+slope*((t-t2)/step)
    if b.c.iloc[i]>line and b.c.iloc[i-1]<=v2+slope*((b.index[i-1]-t2)/step):
        used.add((t1,t2)); out.append((t+step,b.c.iloc[i],b.l.iloc[max(0,i-5):i+1].min()))
SIG['④ 하락추세선 돌파(4h)']=out
# 5) HMA(100) 기울기 전환 (일봉)
b=ohlc('1D')
def wma(x,n): w=np.arange(1,n+1); return x.rolling(n).apply(lambda a: np.dot(a,w)/w.sum(),raw=True)
hma=wma(2*wma(b.c,50)-wma(b.c,100),10); out=[]; gray=False
for i in range(110,len(b)):
    falling=hma.iloc[i-1]<=hma.iloc[i-2]
    if falling and b.c.iloc[i-1]>hma.iloc[i-1]: gray=True
    if gray and hma.iloc[i]>hma.iloc[i-1] and hma.iloc[i-1]<=hma.iloc[i-2]:
        out.append((b.index[i]+pd.Timedelta(days=1),b.c.iloc[i],b.l.iloc[i-10:i+1].min())); gray=False
SIG['⑤ HMA100 기울기 전환(1D)']=out
# ===== 순차 매매 시뮬레이션 =====
BEAR=[('2021-11-10','2023-01-31'),('2025-10-06','2026-11-15')]
def phase(t): return '약세장' if any(pd.Timestamp(a,tz='UTC')<=t<=pd.Timestamp(b_,tz='UTC') for a,b_ in BEAR) else '강세장/조정'
def own_target(name,S,stop):
    R=S-stop
    return {'①':S+3*R,'②':S+2*R,'③':None,'④':S+(S-stop),'⑤':None}[name[0]]
rows=[]; prox=[]
for name,sigs in SIG.items():
    for t,S,stop in sigs:
        lo=m.l[t-pd.Timedelta(days=30):t+pd.Timedelta(days=30)].min(); prox.append(dict(method=name,t=t,entry_vs_low60=S/lo-1,phase=phase(t)))
    for mode in ['영상 원래 청산','영상 손절+SOLT 1.5배','영상 손절+SOLT 2배']:
        free=pd.Timestamp('2000-01-01',tz='UTC')
        for t,S,stop in sigs:
            if t<free or stop>=S or t>pd.Timestamp('2026-10-01',tz='UTC'): continue
            while not is_open(t): t+=pd.Timedelta(hours=1)
            S_in=m.c.asof(t)
            if S_in<=stop: continue
            if mode=='영상 원래 청산':
                tgt=own_target(name,S_in,stop)
                if tgt is None:
                    if name.startswith('③'):   # 피보: 목표는 스윙고점 B ≈ 진입가 + (진입-A)/0.44 근사
                        tgt=S_in+(S_in-stop)*1.0
                    else:                      # HMA: 기울기 하락전환 청산 → 근사로 2R
                        tgt=S_in+2*(S_in-stop)
                k_nav=nav_at(cl,t,tgt)/nav_at(cl,t,S_in)
                res=manage(h1,cl,t,S_in,k=k_nav,stop=stop,T_days=90)
            else:
                k=1.5 if '1.5배' in mode else 2.0
                res=manage(h1,cl,t,S_in,k=k,stop=stop,T_days=180)
            if res is None: continue
            rows.append(dict(method=name,mode=mode,t=t,phase=phase(t),m=res['m'],how=res['how'],days=res['days']))
            free=t+pd.Timedelta(days=res['days'])
R=pd.DataFrame(rows); P=pd.DataFrame(prox); R.to_csv(f'output/e_youtube_{ASSET}.csv',index=False)
gm=lambda v: float(np.exp(np.log(np.clip(v,1e-6,None)).mean()))
def summ(g):
    return pd.Series({'거래':len(g),'승률(목표)':(g.how=='목표').mean(),'거래당 기하':gm(g.m),'거래당 평균':g.m.mean(),'누적배수':float(np.prod(g.m)),'최악':g.m.min(),'평균보유일':g.days.mean()})
print(f"== {ASSET}: 유튜브 바닥포착형 매매법 → 가상 SOLT(2배), 2020-09~2026-10, 순차매매(포지션 1개), 매매비용 편도 0.2%")
print(R.groupby(['method','mode']).apply(summ).round(2).to_string())
print("\n== 약세장 구간만")
print(R[R.phase=='약세장'].groupby(['method','mode']).apply(summ).round(2).to_string())
print("\n== 신호의 바닥 근접도: 진입가 / (앞뒤 30일 최저) - 1")
print(P.groupby('method').entry_vs_low60.describe(percentiles=[.25,.5,.75]).round(3).to_string())
print("신호 수:",{k:len(v) for k,v in SIG.items()})
