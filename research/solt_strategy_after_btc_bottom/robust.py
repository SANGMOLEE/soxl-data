# 견고성: MA(n)·완충폭(b)·확인일(c) 격자 × 체결지연 1~3일 평균, 4개 사이클 + SOL 전구간 + 실제 SOLT
from sigs import *
if __name__=='__main__':
    GRID=[(n,b,c) for n in [15,20,25,30,40] for b in [0.0,0.02,0.04] for c in [1,2]]
    LAGS=[1,2,3]
    rows=[]
    for D,assets in BOTTOMS.items():
        st=pd.Timestamp(D)-pd.Timedelta(days=90); en=pd.Timestamp(D)+pd.Timedelta(days=540)
        for a in assets:
            p=P(a)
            if p.index[0]>st-pd.Timedelta(days=150): continue
            for (n,b,c) in GRID:
                sig=band_sig(p,n,b,c); lm=[]; ex=[]; tr=[]
                for lag in LAGS:
                    eq,e,t,_=run(p,sig,cost=COST,lag=lag,start=st,end=en); lm.append(np.log(eq.iloc[-1])); ex.append(e); tr.append(t)
                rows.append(dict(D=D,asset=a,n=n,b=b,c=c,logm=np.mean(lm),spread=np.ptp(lm),exp=np.mean(ex),trades=np.mean(tr)))
            eq,_,_,_=run(p,pd.Series(1,p.index),cost=COST,lag=0,start=st,end=en)
            rows.append(dict(D=D,asset=a,n=0,b=0,c=0,logm=np.log(eq.iloc[-1]),spread=0,exp=1,trades=1))
    r=pd.DataFrame(rows); r.to_csv('output/robust_grid.csv',index=False)
    cyc=r.groupby(['n','b','c','D']).logm.median().reset_index()
    s=cyc.groupby(['n','b','c']).logm.agg(사이클중앙='median',최악='min',평균='mean')
    s=np.exp(s)
    s=s.join(np.exp(cyc.pivot_table(index=['n','b','c'],columns='D',values='logm')))
    s=s.join(r.groupby(['n','b','c']).agg(지연민감도=('spread','median'),노출=('exp','median'),거래=('trades','median')))
    # SOL 전구간 (2020-11 ~ 2026-11) 합성 SOLT, 그리고 실제 SOLT 기간
    p=P('sol'); add=[]
    for (n,b,c) in GRID+[(0,0,0)]:
        sig=band_sig(p,n,b,c) if n else pd.Series(1,p.index); lm=[]; lm2=[]
        for lag in LAGS:
            eq,_,_,_=run(p,sig,cost=COST,lag=lag if n else 0,start='2020-11-01',end='2026-11-13'); lm.append(np.log(eq.iloc[-1]))
            # 실제 SOLT 가격으로 체결 (2025-03-21 ~ 2026-11-13): 신호는 SOL, 수익은 실제 SOLT
            a=solt.reindex(p.index).dropna(); pos=sig.shift(lag if n else 0).reindex(a.index).fillna(0); held=pos.shift(1).fillna(0); held.iloc[0]=0 if n else 1
            g=1+held*a.pct_change().fillna(0); g=g*(1-0.002*held.diff().abs().fillna(0)); lm2.append(np.log(g.prod()))
        add.append(dict(n=n,b=b,c=c,SOL_2020_26=np.exp(np.mean(lm)),실제SOLT_2025_26=np.exp(np.mean(lm2))))
    s=s.join(pd.DataFrame(add).set_index(['n','b','c']))
    pd.set_option('display.width',260)
    print("[비용 20%, 지연 1~3일 로그평균] 4개 사이클 D-90~D+540 알트 2배 합성. n=0은 구간 시작부터 보유")
    print(s.sort_values('최악',ascending=False).round(2).to_string())
    s.round(3).to_csv('output/robust_summary.csv')
