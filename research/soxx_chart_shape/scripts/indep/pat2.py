from feat import *
import sys
d=pd.read_pickle('d2.pkl'); n=len(d)
SLO=np.load('sim_lo.npy'); SC=np.load('sim_c.npy')
out,M_lo,M_hi,M_c=fwd(d,H=250)
low=d.low.values; high=d.high.values; close=d.close.values; s=d.sfc.values
KA=np.log(8129.234375/close[-1])/s[-1]; KB=np.log(9728.1201171875/close[-1])/s[-1]
def prior_low_info(N):
    PL=np.full(n,np.nan); RH=np.full(n,np.nan); PLi=np.full(n,-1)
    for t in range(N,n):
        w=low[t-N:t]; j=int(np.argmin(w)); PL[t]=w[j]; PLi[t]=t-N+j
        RH[t]=high[PLi[t]+1:t].max() if PLi[t]+1<t else np.nan
    return PL,RH,PLi
cache={N:prior_low_info(N) for N in (5,10,20)}
def model_p(ka,kb,T):
    # vol-only probabilities from simulated normalized paths, for arrays ka<0 (lows), kb>0 (closes)
    res_hl=[];res_up=[]
    lo=SLO[:,:T]; c=SC[:,:T]
    for a,b in zip(ka,kb):
        hl,up,_,_,_=first_hit(lo,c,a,b,T)
        res_hl.append(hl.mean()); res_up.append(up.mean())
    return np.array(res_hl),np.array(res_up)
def events(N=10,ddc=-0.30,clv=0.8,rallyk=2.0,depthmax=1.5,reclaim=True,use_rally=True,declust=10,extra=None):
    PL,RH,PLi=cache[N]
    uc=low<PL; depth=np.log(PL/low)/s; rz=np.log(RH/PL)/s
    m=(d.dd.values<=ddc)&uc&(depth<=depthmax)&(d.clv.values>=clv)
    if reclaim: m&=close>PL
    if use_rally: m&=np.nan_to_num(rz,nan=-9)>=rallyk
    if extra is not None: m&=extra
    m[-1]=False  # exclude current day
    idx=np.where(m)[0]
    keep=[];last=-999
    for i in idx:
        if i-last>declust: keep.append(i); last=i   # last = last kept event
    return np.array(keep,int),np.array(idx,int),PL,RH
def evaluate(ev,PL,RH,label,show=False):
    ev=ev[~np.isnan(M_lo[ev,19])]  # need complete 20d window
    k=len(ev)
    if k==0: print(label,'no events'); return None
    # own barriers
    a=np.log(low[ev]/close[ev]); b=np.log(RH[ev]/close[ev])
    hlo,upo,neio,_,_=first_hit(M_lo[ev],M_c[ev],a,b,20)
    _,upo60,nei60,_,_=first_hit(M_lo[ev],M_c[ev],a,b,60)
    _,upo250,_,_,_=first_hit(M_lo[ev],M_c[ev],a,b,250)
    ph,pu=model_p(a/s[ev],np.maximum(b,1e-6)/s[ev],20)
    ph60,pu60=model_p(a/s[ev],np.maximum(b,1e-6)/s[ev],60)
    # normalized (current-geometry) barriers
    hln,upn,_,_,_=first_hit(M_lo[ev],M_c[ev],KA*s[ev],KB*s[ev],20)
    _,upn60,_,_,_=first_hit(M_lo[ev],M_c[ev],KA*s[ev],KB*s[ev],60)
    z5=out['f5'][ev]/s[ev]; z20=out['f20'][ev]/s[ev]; z60=out['f60'][ev]/s[ev]
    R={}
    def pr(name,y,p=None):
        yy=y[~np.isnan(y)]; kk=int(yy.sum()); nn=len(yy); P,lo,hi=wilson(kk,nn)
        txt=f'{name}: {kk}/{nn}={P:.2f} [{lo:.2f},{hi:.2f}]'
        if p is not None:
            pp=p[~np.isnan(y)]; txt+=f' model={pp.mean():.2f} (O-E={kk-pp.sum():+.1f}, z={(kk-pp.sum())/np.sqrt((pp*(1-pp)).sum()):+.2f})'
        R[name]=(kk,nn,P,lo,hi)
        return txt
    print(f'== {label}: n={k} (episodes {len(set(d.ep.values[ev]))})')
    print('   OWN barriers (lower=event low, upper=rally high, close):',pr('hitL20',hlo,ph),'|',pr('up20',upo,pu),'|',pr('up60',upo60,pu60),f'| up250 {np.nanmean(upo250):.2f}')
    print('   CURRENT-geometry barriers (-%.2fσ low / +%.2fσ close):'%(-KA,KB),pr('hlN20',hln),'|',pr('upN60',upn60))
    for h,zz in ((5,z5),(20,z20),(60,z60)):
        zz2=zz[~np.isnan(zz)]
        if len(zz2)==0: continue
        sc=zz2*s[-1]
        print(f'   h={h}: n={len(zz2)} P(<0)={np.mean(zz2<0):.2f} {wilson((zz2<0).sum(),len(zz2))[1]:.2f}-{wilson((zz2<0).sum(),len(zz2))[2]:.2f}  median z={np.median(zz2):+.2f} (scaled {np.expm1(np.median(sc)):+.1%}) p10 {np.expm1(np.percentile(sc,10)):+.1%} worst {np.expm1(sc.min()):+.1%} | raw median {np.expm1(np.median(out[f"f{h}"][ev][~np.isnan(zz)])):+.1%} raw worst {np.expm1(np.nanmin(out[f"f{h}"][ev])):+.1%}')
    if show:
        tab=pd.DataFrame({'date':d.date.values[ev].astype('datetime64[D]'),'close':close[ev].round(1),'dd':(d.dd.values[ev]*100).round(0),'sfc%':(s[ev]*100).round(1),
            'clv':d.clv.values[ev].round(2),'low%':(a*100).round(1),'rallyH%':(b*100).round(1),'hitL20':hlo,'pModel':ph.round(2),'up20':upo,'up60':upo60,'pUp60':pu60.round(2),
            'f5%':(np.expm1(out['f5'][ev])*100).round(1),'f20%':(np.expm1(out['f20'][ev])*100).round(1),'f60%':(np.expm1(out['f60'][ev])*100).round(1)})
        print(tab.to_string(index=False))
    return dict(ev=ev,R=R,z5=z5,z20=z20,z60=z60,hlo=hlo,ph=ph,upo60=upo60,pu60=pu60,hln=hln,upn60=upn60)
if __name__=='__main__':
    ev,raw,PL,RH=events()
    print('raw events',len(raw),'declustered',len(ev))
    evaluate(ev,PL,RH,'CORE N10 dd<=-30 clv>=.8 rally>=2σ depth<=1.5σ reclaim',show=True)
