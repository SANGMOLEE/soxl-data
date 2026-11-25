import sys, os; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd
exec(open('scripts/o_after_bottom.py',encoding='utf-8').read().split("rows=[]")[0])
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'NanumGothic.ttf' in f: fm.fontManager.addfont(f)
plt.rcParams['font.family']='NanumGothic'; plt.rcParams['axes.unicode_minus']=False; plt.rcParams['text.parse_math']=False
cases=[('btc','2015-01-14','BTC 2015 바닥'),('eth','2018-12-15','ETH 2018 바닥'),('eth','2020-03-12','ETH 2020 바닥'),
       ('btc','2022-11-21','BTC 2022 바닥 (조용한 바닥)'),('sol','2022-11-21','SOL: BTC 바닥일(2022-11-21)에 샀다면'),('sol','2022-12-29','SOL: 자기 바닥(2022-12-29)에 샀다면')]
fig,axes=plt.subplots(3,2,figsize=(13,11)); axes=axes.ravel()
for ax,(a,d,lab) in zip(axes,cases):
    t0=pd.Timestamp(d); q=px(a)[t0:t0+pd.Timedelta(days=365)]; n=nav2(q); x=(q.index-t0).days
    ax.plot(x,q/q.iloc[0],color='#555555',lw=1.3,label='1배 (현물)'); ax.plot(x,n,color='#d62728',lw=1.3,label='2배 일일재조정 (SOLT형)')
    for k in [1.5,2,3]: ax.axhline(k,color='#1f77b4',lw=0.6,ls=':')
    pk=n[:t0+pd.Timedelta(days=120)].idxmax(); ax.scatter([(pk-t0).days],[n[pk]],color='#d62728',s=20,zorder=5)
    ax.set_yscale('log'); ax.set_title(lab,fontsize=10); ax.grid(alpha=0.3); ax.set_xlabel('바닥 후 일수')
    from matplotlib.ticker import NullFormatter, FixedLocator
    tk=[0.3,0.5,1,1.5,2,3,5,8,15,30]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.set_yticklabels([str(v) for v in tk]); ax.yaxis.set_minor_formatter(NullFormatter())
axes[0].legend(fontsize=8,loc='upper left')
fig.suptitle('사이클 바닥 후 1년: 급반등 → 횡보·조정 → 본상승. 빨간 점 = 2배 상품의 120일 안 고점 (점선 = 1.5·2·3배)',fontsize=11)
plt.tight_layout(); plt.savefig('charts/o_after_bottom_paths.png',dpi=110); print('saved')
