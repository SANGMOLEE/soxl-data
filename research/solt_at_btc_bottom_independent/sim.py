# SOLT 가격 @ BTC 저점 — 몬테카를로 (독립 추정)
import numpy as np, pandas as pd
rng=np.random.default_rng(20261115)
B0=65383.9; SOL0=72.35            # 2026-11-15 (일) Yahoo
SOLT_F=32.98; SOL_F=78.10         # 2026-11-13 (금) SOLT 종가 / 같은 날 SOL
day0=pd.Timestamp('2026-11-15')
hol={pd.Timestamp(x) for x in ['2026-11-26','2026-12-25','2027-01-01','2027-01-18','2027-02-15']}
cal=pd.date_range(day0,periods=120)
is_sess=np.array([(d.weekday()<5) and (d not in hol) for d in cal])

def simulate(n, Bsamp, Tsamp, k_mu=1.45, k_sd=0.45, fixed=None):
    out=[]; need=n
    while need>0:
        m=need*6
        B=Bsamp(m); T=Tsamp(m).astype(int)
        k=np.clip(rng.normal(k_mu,k_sd,m),0.3,2.8) if fixed is None else np.full(m,fixed)
        sb=rng.uniform(0.40,0.60,m)/np.sqrt(365)       # BTC 일변동성
        se=rng.uniform(0.22,0.35,m)/np.sqrt(365)       # SOL 고유 변동성
        al=rng.normal(-0.15,0.15,m)/365                # SOL/BTC 추세 (연)
        c=rng.uniform(0.05,0.12,m)/365                 # SOLT 보수+금리+베이시스 (연)
        Tm=T.max()
        z=rng.standard_normal((m,Tm))*sb[:,None]
        t=np.arange(1,Tm+1)[None,:]
        mask=t<=T[:,None]
        W=np.cumsum(np.where(mask,z,0),axis=1)
        WT=W[np.arange(m),T-1][:,None]
        drift=np.log(B/B0)[:,None]
        lb=W - (t/T[:,None])*WT + (t/T[:,None])*drift      # 브라운 다리: 0 -> ln(B/B0)
        lb=np.where(mask,lb,np.nan)
        ok=np.nanmin(np.where(t<T[:,None],lb,np.inf),axis=1)>drift[:,0]   # 저점은 T일에만
        ok&=(T>=1)
        idx=np.where(ok)[0][:need]
        for i in idx:
            Ti=T[i]; path=lb[i,:Ti]
            db=np.diff(np.r_[0,path])
            ls=np.log(SOL0)+np.cumsum(k[i]*db+al[i]+rng.standard_normal(Ti)*se[i])
            sol_path=np.exp(ls)
            # SOLT: 미국 거래일 종가에만 2배 재조정
            v=SOLT_F; ref=SOL_F; last_d=-2; solt_min=np.inf
            for j in range(Ti):
                d=j+1
                if is_sess[d]:
                    v=v*(1+2*(sol_path[j]/ref-1))*np.exp(-c[i]*(d-last_d)); ref=sol_path[j]; last_d=d
                    solt_min=min(solt_min,v)
            ind=v*(1+2*(sol_path[-1]/ref-1))*np.exp(-c[i]*(Ti-last_d))   # 저점 시각의 환산가
            solt_min=min(solt_min,ind)
            out.append((B[i],Ti,k[i],sol_path[-1],ind,solt_min,sol_path.min()))
        need=n-len(out)
    return pd.DataFrame(out,columns=['B','T','k','SOL','SOLT','SOLT_min_before','SOL_min_before'])

tri=lambda a,mo,b: (lambda m: rng.triangular(a,mo,b,m))
uni=lambda a,b: (lambda m: rng.uniform(a,b,m))
SC=[('H 7월저점 유지(눌림 저점)',0.40,tri(58800,62500,65000),uni(1,21)),
    ('M 이탈·실현가격 부근',      0.33,tri(50000,53700,55500),uni(10,50)),
    ('D 깊은 이탈 44~50k',        0.24,tri(44000,48700,50000),uni(20,60)),
    ('X 꼬리 30~39k',             0.03,uni(30000,39000),uni(30,75))]
N=6000
res={}
for name,p,bs,ts in SC:
    r=simulate(N,bs,ts); r['sc']=name; r['p']=p; res[name]=r
allr=pd.concat(res.values())
q=lambda x: pd.Series({'P10':x.quantile(.1),'P25':x.quantile(.25),'중앙':x.median(),'P75':x.quantile(.75),'P90':x.quantile(.9)})
rows=[]
for name,p,_,_ in SC:
    r=res[name]
    rows.append(dict(시나리오=name,확률=p,BTC중앙=r.B.median(),SOL중앙=r.SOL.median(),
        **{('SOLT '+k_):v for k_,v in q(r.SOLT).items()}, SOLT저점전최저_중앙=r.SOLT_min_before.median()))
tab=pd.DataFrame(rows); pd.set_option('display.width',250)
print(tab.round(2).to_string(index=False))
# 확률 가중 혼합 (다음 BTC 저점 기준)
w=np.concatenate([np.full(len(res[n]),p/len(res[n])) for n,p,_,_ in SC])
v=allr.SOLT.values; o=np.argsort(v); cw=np.cumsum(w[o])
wq=lambda qq: v[o][np.searchsorted(cw,qq)]
print("\n혼합 분포 SOLT: P10 %.2f  P25 %.2f  중앙 %.2f  P75 %.2f  P90 %.2f"%tuple(wq(x) for x in [.1,.25,.5,.75,.9]))
br=allr[allr.sc!=SC[0][0]]; wb=np.concatenate([np.full(len(res[n]),p/len(res[n])) for n,p,_,_ in SC[1:]]); wb/=wb.sum()
v2=br.SOLT.values; o2=np.argsort(v2); c2=np.cumsum(wb[o2])
print("이탈 시나리오만(M+D+X): P10 %.2f  P25 %.2f  중앙 %.2f  P75 %.2f  P90 %.2f"%tuple(v2[o2][np.searchsorted(c2,x)] for x in [.1,.25,.5,.75,.9]))
for thr in [30,25,20,15,12,10]:
    print(f"P(SOLT@BTC저점 < {thr}) = {w[v<thr].sum():.0%}")
tab.round(2).to_csv('output/scenarios.csv',index=False)
