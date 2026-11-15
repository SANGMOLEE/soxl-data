# A. 사후(오라클) 사건연구: BTC 바닥일 D 기준, D+a 매수 → D+b 매도 의 2배 합성 수익
from lib import *
import sys
COST=float(sys.argv[1]) if len(sys.argv)>1 else 0.20
BOTTOMS={'2015-01-14':['btc','ltc','xrp','dash','xmr','doge'],
         '2018-12-15':['btc','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx'],
         '2020-03-12':['btc','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx'],
         '2022-11-21':['btc','sol','eth','ada','avax','dot','link','bnb','doge','xrp','ltc','xlm']}
def series(a):
    s=sol if a=='sol' else (btc if a=='btc' else cm[a])
    return sess(s)
def nav_at(nav, d0, off):
    t=pd.Timestamp(d0)+pd.Timedelta(days=off); i=nav.index.searchsorted(t); 
    return nav.iloc[min(i,len(nav)-1)] if i<len(nav) else np.nan
A=[0,7,14,30,60,90,120]; Bv=[30,60,90,120,180,270,365,540]
rows=[]
for D,assets in BOTTOMS.items():
    for a in assets:
        p=series(a); p=p[pd.Timestamp(D)-pd.Timedelta(days=200):pd.Timestamp(D)+pd.Timedelta(days=760)]
        nav=lev2(p,COST); one=p/p.iloc[0]
        for x in A:
            for y in Bv:
                if y<=x: continue
                n0,n1=nav_at(nav,D,x),nav_at(nav,D,y); o0,o1=nav_at(one,D,x),nav_at(one,D,y)
                rows.append(dict(D=D,asset=a,a=x,b=y,r2=n1/n0,r1=o1/o0))
ev=pd.DataFrame(rows)
ev.to_csv(f'output/events_cost{int(COST*100)}.csv',index=False)
alts=ev[ev.asset!='btc']
# 사이클별 알트 중앙값 → 사이클 간 중앙값/최소 (사이클 1표)
per=alts.groupby(['D','a','b']).r2.median().reset_index()
piv_med=per.groupby(['a','b']).r2.median().unstack('b')
piv_min=per.groupby(['a','b']).r2.min().unstack('b')
pd.set_option('display.width',220)
print(f"[비용 연 {COST:.0%}] 알트 2배 합성: 매수 D+a(행) → 매도 D+b(열) 배수, 4개 사이클 '사이클별 알트 중앙값'의 중앙값")
print(piv_med.round(2).to_string())
print("\n같은 표, 4개 사이클 중 최저 사이클")
print(piv_min.round(2).to_string())
print("\n사이클별 (매수 D+0) 알트 2배 중앙값:")
print(per[per.a==0].pivot(index='D',columns='b',values='r2').round(2).to_string())
print("\n사이클별 (매수 D+0) 알트 1배 중앙값:")
print(alts[alts.a==0].groupby(['D','b']).r1.median().unstack('b').round(2).to_string())
print("\nBTC 2배 (매수 D+0):"); print(ev[(ev.asset=='btc')&(ev.a==0)].pivot(index='D',columns='b',values='r2').round(2).to_string())
print("\nSOL 2배 2022 (행 a):"); print(ev[ev.asset=='sol'].pivot(index='a',columns='b',values='r2').round(2).to_string())
