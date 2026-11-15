# C. "바닥이라고 판단해 미리 매수" 전략 검증: 진짜 바닥 vs 가짜 바닥, 매수시점 오차 ±14일, 손절 유무
from sigs import *
b=btc.dropna()
# 약세장 저점 후보: zigzag 20%, 직전 최고가 대비 -45% 이상
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
bb=b['2013-06':]
ath=bb.cummax()
TRUE=[pd.Timestamp(x) for x in ['2015-01-14','2018-12-15','2020-03-12','2022-11-21']]
cands=[t for t in zz_lows(bb) if bb[t]/ath[t]-1<=-0.45]
def near_true(t): return min(abs((t-T).days) for T in TRUE)
lows=[]
for t in cands:
    if near_true(t)<=10: continue
    typ='현재사이클(미확정)' if t>=pd.Timestamp('2025-10-06') else '가짜'
    lows.append((t,typ))
lows+= [(T,'진짜') for T in TRUE]
lows=sorted(lows)
print("BTC 약세장 저점 후보 (고점대비 -45% 이하, 20% 반등):")
for t,typ in lows: print(f"  {t.date()}  ${bb[t]:,.0f}  고점대비 {bb[t]/ath[t]-1:+.0%}  {typ}")
ALTS=['sol','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx','avax','dot']
def trade(nav, st, H=150, stop=None, trail=None):
    n=nav[st:st+pd.Timedelta(days=H)]
    if len(n)<5: return np.nan
    rel=n/n.iloc[0]
    for i,v in enumerate(rel.values):
        if stop is not None and v<=1-stop: return v*(1-0.004)
        if trail is not None and v<=rel.values[:i+1].max()*(1-trail) and rel.values[:i+1].max()>1.0: return v*(1-0.004)
    return rel.values[-1]*(1-0.004)
VAR={'손절없음·150일보유':dict(),'손절-30%·150일':dict(stop=0.30),'손절-20%·150일':dict(stop=0.20),'손절-30%+고점대비-35%·180일':dict(stop=0.30,trail=0.35,H=180)}
rows=[]
for L,typ in lows:
    for a in ALTS:
        s=raw(a).dropna()
        if s.index[0]>L-pd.Timedelta(days=40) or s.index[-1]<L+pd.Timedelta(days=30): continue
        p=sess(s); nav=lev2(p[L-pd.Timedelta(days=60):],COST)
        for e in [-14,-7,0,7,14]:
            st=nav.index[nav.index.searchsorted(L+pd.Timedelta(days=e))]
            for vn,kw in VAR.items():
                rows.append(dict(L=L.date(),typ=typ,asset=a,e=e,var=vn,m=trade(nav,st,**kw)))
r=pd.DataFrame(rows).dropna(); r.to_csv('output/zone_trades.csv',index=False)
gm=lambda x: np.exp(np.log(x).mean())
per=r.groupby(['typ','L','var','e']).m.median().reset_index()    # 저점별 알트 중앙
pd.set_option('display.width',240)
for vn in VAR:
    print(f"\n== {vn}: 저점별 알트 중앙값 배수 (열=매수시점 오차, 일)")
    print(per[per['var']==vn].pivot_table(index=['typ','L'],columns='e',values='m').round(2).to_string())
summ=per.groupby(['typ','var']).m.agg(중앙='median',기하평균=gm,최악='min',개수='count').round(2)
print("\n== 요약 (저점×오차 전체)"); print(summ.to_string())
# 기본확률: 과거 '-45% 이하 저점' 중 진짜 바닥 비율
nt=sum(1 for _,t in lows if t=='진짜'); nf=sum(1 for _,t in lows if t=='가짜'); p=nt/(nt+nf)
print(f"\n기본확률(진짜/전체) = {nt}/{nt+nf} = {p:.2f}")
for vn in VAR:
    gt=gm(per[(per['var']==vn)&(per.typ=='진짜')].m); gf=gm(per[(per['var']==vn)&(per.typ=='가짜')].m)
    for pp in [p,0.4,0.6]:
        print(f"  {vn:28s} P(진짜)={pp:.2f} → 기하기대배수 {np.exp(pp*np.log(gt)+(1-pp)*np.log(gf)):.2f}  (진짜 {gt:.2f} / 가짜 {gf:.2f})")
# SOL 단독
print("\n== SOL 단독 (매수오차 0일)"); print(r[(r.asset=='sol')&(r.e==0)].pivot_table(index=['typ','L'],columns='var',values='m').round(2).to_string())
