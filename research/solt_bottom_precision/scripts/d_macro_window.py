# D. 거시 타이밍이 맞았다고 가정(바닥 ±창): 실행 규칙별 2배 상품 결과. 진짜 바닥 vs 가짜 바닥.
import sys; sys.path.insert(0,'scripts')
from d_engine import *
pd.set_option('display.width',260)
B=load('BTC')
WINDOWS=[('2018-12-15','진짜','2018 사이클 바닥'),('2020-03-13','진짜','2020 코로나 바닥'),('2022-11-21','진짜','2022 사이클 바닥'),
         ('2018-02-06','가짜','2018-02 투매'),('2018-06-29','가짜','2018-06 저점'),('2019-12-18','가짜','2019-12 저점'),
         ('2022-06-18','가짜','2022-06 투매'),('2022-11-09','가짜','2022-11 FTX')]
ASSETS=sys.argv[1].split(',') if len(sys.argv)>1 else ['BTC','ETH','SOL']
K=[1.5,2.0,3.0]
rows=[]
for d,typ,lab in WINDOWS:
    d=pd.Timestamp(d,tz='UTC'); w=B.l[d-pd.Timedelta(days=2):d+pd.Timedelta(days=2)]; D_=w.idxmin()
    ws,we=D_-pd.Timedelta(days=30),D_+pd.Timedelta(days=60)
    for a in ASSETS:
        m=load(a)
        if m is None or m.index[0]>ws-pd.Timedelta(days=5) or m.index[-1]<D_+pd.Timedelta(days=60): continue
        cl=nav_build(m,(ws-pd.Timedelta(days=5)).strftime('%Y-%m-%d'),(D_+pd.Timedelta(days=430)).strftime('%Y-%m-%d'))
        h1=h1_of(m[ws-pd.Timedelta(days=1):D_+pd.Timedelta(days=430)])
        horizon=min(365,(m.index[-1]-D_).days-1)
        own=m.l[ws:we]; t_own=own.idxmin()
        for k in K:
            base=dict(window=lab,typ=typ,asset=a,k=k,horizon=horizon)
            def add(name,res,entry_vs_own=np.nan):
                if res: rows.append(dict(**base,strategy=name,m=res['m'],how=res['how'],days=res['days'],mae=res['mae'],entry_vs_own_low=entry_vs_own))
            # 오라클: BTC 바닥 그 분 (주말이면 다음 개장)
            t0=D_
            while not is_open(t0): t0+=pd.Timedelta(hours=1)
            S0=m.l[D_] if t0==D_ else m.c.asof(t0)
            add('① BTC바닥 그 분(사후)',manage(h1,cl,t0,S0,k=k,T_days=horizon),S0/own.min()-1)
            t1=t_own
            while not is_open(t1): t1+=pd.Timedelta(hours=1)
            S1=m.l[t_own] if t1==t_own else m.c.asof(t1)
            add('② 자기 바닥 그 분(사후)',manage(h1,cl,t1,S1,k=k,T_days=horizon),S1/own.min()-1)
            # 실행 규칙 (창 시작부터, 사후정보 없음)
            tr=confirm_rule(h1,cl,ws,we,k=k,T_days=horizon)
            if tr:
                mm=np.prod([z['m'] for z in tr]); rows.append(dict(**base,strategy='③ 반등확인+손절(재시도4)',m=mm,how=tr[-1]['how'],days=tr[-1]['days'],mae=min(z['mae'] for z in tr),
                                                                  entry_vs_own_low=tr[-1]['S_in']/own.min()-1,tries=len(tr)))
            tr2=confirm_rule(h1,cl,ws,we,k=k,use_stop=False,tries=1,T_days=horizon)
            if tr2: add('④ 반등확인, 손절없이 목표까지',tr2[0],tr2[0]['S_in']/own.min()-1)
            # 시간분산 4회: D-30, D-10, D+10, D+30 (각 1/4)
            parts=[]
            for off in [-30,-10,10,30]:
                tt=D_+pd.Timedelta(days=off)
                while not is_open(tt): tt+=pd.Timedelta(hours=1)
                r_=manage(h1,cl,tt,m.c.asof(tt),k=k,T_days=horizon-off if off>0 else horizon)
                if r_: parts.append(r_['m'])
            if parts: rows.append(dict(**base,strategy='⑤ 시간분산 4회(D-30,-10,+10,+30)',m=np.mean(parts),how='',days=np.nan,mae=np.nan,entry_vs_own_low=np.nan))
R=pd.DataFrame(rows); R.to_csv(f"output/d_macro_window_{'_'.join(ASSETS)}.csv",index=False)
gm=lambda v: float(np.exp(np.log(np.clip(v,1e-6,None)).mean()))
for typ in ['진짜','가짜']:
    x=R[R.typ==typ]
    t=x.groupby(['strategy','k']).apply(lambda g: pd.Series({'n':len(g),'목표달성':(g.how=='목표').mean() if (g.how!='').any() else np.nan,'기하평균':gm(g.m),'중앙':g.m.median(),'최악':g.m.min(),
        '진입_자기바닥대비':g.entry_vs_own_low.median(),'중앙일수':g.days.median(),'최대낙폭중앙':g.mae.median()}))
    print(f"\n== {typ} 바닥 창 (자산: {','.join(ASSETS)})"); print(t.round(2).to_string())
print("\n== 개별 (k=2)")
print(R[R.k==2].pivot_table(index=['typ','window','asset'],columns='strategy',values='m').round(2).to_string())
