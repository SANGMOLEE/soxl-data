# 공용: 완충폭·확인일 MA 신호, 자산 캐시
from engine import *
import itertools
def band_sig(p,n,b,c):
    ma=p.rolling(n).mean().values; v=p.values; s=np.zeros(len(v),int); st=False; cnt=0
    for i in range(len(v)):
        if np.isnan(ma[i]): continue
        if not st:
            cnt=cnt+1 if v[i]>ma[i]*(1+b) else 0
            if cnt>=c: st=True; cnt=0
        else:
            if v[i]<ma[i]*(1-b): st=False
        s[i]=int(st)
    return pd.Series(s,p.index)
COST=0.20
cache={}
def P(a):
    if a not in cache: cache[a]=sess(raw(a).dropna())
    return cache[a]
