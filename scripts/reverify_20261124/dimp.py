from exits import *
r=rL.values*100; P=pos.values; V=vx.values; Bm=bear.values; R=real.values
COST=0.2
isD=np.array([i>=2 and r[i]<=-8 and P[i]<0.2 and r[i-1]<0 for i in range(N)])
D=[i for i in range(2,N-11) if isD[i]]
def d2(i): return (c[i+1]/c[i]-1)*100
def pb(i): x,_=limit(i,0.15,10); y,_=limit(i,0.25,10); return (x+y)/2
def pol(i):
    a=d2(i); b=pb(i)
    return {"D2 다음 날 종가 (현행)":a-COST,"(b) +15%절반·+25%나머지·10일":b-COST,"절반 D2 + 절반 (b)":(a+b)/2-COST,
            "VIX≥30이면 (b), 아니면 D2":(b if V[i]>=30 else a)-COST,"당일 -12%↓면 (b), 아니면 D2":(b if r[i]<=-12 else a)-COST,
            "첫날 종가 +10%↑면 정리, 아니면 (b)":(a if a>=10 else b)-COST}
for nm,sel in (("2010~ 실제",lambda i:R[i]),("~2009 합성",lambda i:not R[i]),("2019~",lambda i:cal[i].year>=2019),("하락장&VIX≥30",lambda i:R[i] and Bm[i] and V[i]>=30)):
    idx=[i for i in D if sel(i)]; res={}
    for i in idx:
        for k,v in pol(i).items(): res.setdefault(k,[]).append(v)
    print(f"\n[{nm}] {len(idx)}건")
    for k,v in res.items(): print(st(v,k,40))
