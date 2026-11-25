# O2. 바닥에서 2배 상품: 1.5배·2배 도달 시점과 그 전 최대 하락, 계속 보유 시 녹는 정도 + 2026 실제 SOLT
import sys, os; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd
exec(open('scripts/o_after_bottom.py',encoding='utf-8').read().split("rows=[]")[0])
rows=[]
for cy,(D,assets) in CYC.items():
    D=pd.Timestamp(D)
    for a in assets:
        p=px(a)
        if p.index[0]>D-pd.Timedelta(days=60) or p.index[-1]<D+pd.Timedelta(days=200): continue
        for anchor in ['BTC 바닥일','자기 바닥']:
            t0=D if anchor=='BTC 바닥일' else p[D-pd.Timedelta(days=60):D+pd.Timedelta(days=60)].idxmin()
            n=nav2(p[t0:t0+pd.Timedelta(days=400)])
            r=dict(cycle=cy,asset=a,anchor=anchor)
            for k in [1.5,2.0,3.0]:
                w=n[n>=k]; r[f'd{k}']=(w.index[0]-t0).days if len(w) else np.nan
                r[f'mae{k}']=(n[:w.index[0]].min()-1) if len(w) else n.min()-1
            pk=n[:t0+pd.Timedelta(days=120)].idxmax(); r['peak120']=n[pk]; r['peak_day']=(pk-t0).days
            r['after_peak_min']=n[pk:t0+pd.Timedelta(days=365)].min()/n[pk]-1          # 고점 뒤 계속 보유 시 최대 녹음
            r['d365_vs_peak']=n[:t0+pd.Timedelta(days=365)].iloc[-1]/n[pk]-1
            rows.append(r)
R=pd.DataFrame(rows); R.to_csv('output/o2_targets.csv',index=False)
for anc in ['BTC 바닥일','자기 바닥']:
    x=R[R.anchor==anc]
    print(f"\n==== 기준: {anc} (BTC·ETH·SOL·알트, 2배 일일재조정, 비용 연20%) n={len(x)}")
    for k in [1.5,2.0,3.0]:
        d=x[f'd{k}']; print(f"  {k}배: 1년 안 도달 {d.notna().mean():.0%}, 30일 안 {(d<=30).mean():.0%}, 60일 안 {(d<=60).mean():.0%}, 90일 안 {(d<=90).mean():.0%}; 도달일 중앙 {d.median():.0f}일; 도달 전 최대 하락 중앙 {x[f'mae{k}'].median():+.0%} (하위25% {x[f'mae{k}'].quantile(.25):+.0%})")
    print(f"  120일 안 최고점: 중앙 {x.peak120.median():.2f}배 (중앙 {x.peak_day.median():.0f}일째). 그 뒤 1년까지 계속 보유하면 고점 대비 최대 {x.after_peak_min.median():+.0%} (하위25% {x.after_peak_min.quantile(.25):+.0%}), 1년 시점 {x.d365_vs_peak.median():+.0%}")
    print(x[x.asset.isin(['btc','eth','sol'])][['cycle','asset','d1.5','mae1.5','d2.0','mae2.0','d3.0','peak120','peak_day','after_peak_min','d365_vs_peak']].round(2).to_string(index=False))
