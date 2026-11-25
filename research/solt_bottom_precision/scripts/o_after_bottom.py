# O. 사이클 바닥 뒤: 바로 반등했나, 횡보했나? 그리고 2배 상품은 얼마나 녹았나 (일봉)
import os, numpy as np, pandas as pd
pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
D2=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','solt_strategy_after_btc_bottom','data')
cm=pd.read_csv(f'{D2}/CM_PRICES.csv',parse_dates=['date']).set_index('date').sort_index()
bst=pd.read_csv(f'{D2}/BTC_BITSTAMP_1D.csv',parse_dates=['date']).set_index('date').close
btc=pd.concat([bst[bst.index<cm.btc.dropna().index[0]],cm.btc.dropna()])
CYC={'2011':('2011-11-18',['btc']),'2015':('2015-01-14',['btc','ltc','xrp','dash','doge','xmr']),
     '2018':('2018-12-15',['btc','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx']),
     '2020':('2020-03-12',['btc','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx']),
     '2022':('2022-11-21',['btc','sol','eth','ada','avax','dot','link','bnb','doge','xrp','ltc','xlm'])}
def px(a): return (btc if a=='btc' else cm[a]).dropna()
def nav2(p,cost=0.20):
    r=p.pct_change().fillna(0); return ((1+2*r).clip(lower=0)*np.exp(-cost/365)).cumprod()
rows=[]
for cy,(D,assets) in CYC.items():
    D=pd.Timestamp(D)
    for a in assets:
        p=px(a)
        if p.index[0]>D-pd.Timedelta(days=60) or p.index[-1]<D+pd.Timedelta(days=200): continue
        for anchor in ['BTC 바닥일','자기 바닥(±60일)']:
            t0=D if anchor=='BTC 바닥일' else p[D-pd.Timedelta(days=60):D+pd.Timedelta(days=60)].idxmin()
            q=p[t0:t0+pd.Timedelta(days=400)]; P0=q.iloc[0]; n=nav2(q)
            g=lambda d: q[:t0+pd.Timedelta(days=d)].max()/P0-1
            def tto(x):
                w=q[q>=P0*(1+x)]; return (w.index[0]-t0).days if len(w) else np.nan
            first90=q[:t0+pd.Timedelta(days=90)]; tr=first90.idxmax(); Pr=first90.max()
            after=q[tr:]; brk=after[after>Pr*1.0001]; tb=brk.index[0] if len(brk) else None
            base=q[tr:tb] if tb is not None else q[tr:]
            base_days=(tb-tr).days if tb is not None else np.nan
            dd_base=base.min()/Pr-1
            lower=q[t0+pd.Timedelta(days=1):].min()/P0-1          # 바닥 이후 더 낮아졌나
            # 2배: 반등 고점, 횡보 끝(돌파일)에서 자기 반등고점 대비
            n_r=n[tr]; n_b=(n[tb] if tb is not None else n.iloc[-1])
            er=lambda s: abs(np.log(s.iloc[-1]/s.iloc[0]))/np.log(s).diff().abs().sum() if len(s)>5 else np.nan
            rows.append(dict(cycle=cy,asset=a,anchor=anchor,t0=t0.date(),
                g7=g(7),g14=g(14),g30=g(30),g60=g(60),g90=g(90),t50=tto(0.5),t100=tto(1.0),
                reflex_day=(tr-t0).days,reflex_gain=Pr/P0-1,base_days=base_days,base_dd=dd_base,lower_after=lower,
                er_0_60=er(q[:t0+pd.Timedelta(days=60)]),er_60_240=er(q[t0+pd.Timedelta(days=60):t0+pd.Timedelta(days=240)]),
                x2_reflex=n_r,x2_at_breakout_vs_reflex=n_b/n_r-1,x1_at_breakout_vs_reflex=(q[tb]/Pr-1) if tb is not None else q.iloc[-1]/Pr-1,
                x2_d90=n[:t0+pd.Timedelta(days=90)].iloc[-1],x2_d180=n[:t0+pd.Timedelta(days=180)].iloc[-1],x2_d365=n[:t0+pd.Timedelta(days=365)].iloc[-1],
                x1_d180=q[:t0+pd.Timedelta(days=180)].iloc[-1]/P0,
                x2_max90=n[:t0+pd.Timedelta(days=90)].max(),hit2x_90=(n[:t0+pd.Timedelta(days=90)]>=2).any(),hit15_90=(n[:t0+pd.Timedelta(days=90)]>=1.5).any()))
R=pd.DataFrame(rows); R.to_csv('output/o_after_bottom.csv',index=False)
cols=['g7','g14','g30','g60','g90','t50','reflex_day','reflex_gain','base_days','base_dd','lower_after','x2_max90','x2_d180','x1_d180','x2_at_breakout_vs_reflex']
for anc in ['BTC 바닥일','자기 바닥(±60일)']:
    x=R[R.anchor==anc]
    print(f"\n==== 기준: {anc}")
    print("[BTC·ETH·SOL 개별]")
    print(x[x.asset.isin(['btc','eth','sol'])][['cycle','asset','t0']+cols].round(2).to_string(index=False))
    print("[사이클별 알트 중앙값 (BTC 제외)]")
    print(x[x.asset!='btc'].groupby('cycle')[cols].median().round(2).to_string())
