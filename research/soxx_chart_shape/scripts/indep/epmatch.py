from pat2 import *
rng=np.random.default_rng(3)
ep=d.ep.values; dd=d.dd.values
z5a=out['f5']/s; z20a=out['f20']/s; z60a=out['f60']/s
hlN,_,_,_,_=first_hit(M_lo,M_c,KA*s,KB*s,20); _,upN60,_,_,_=first_hit(M_lo,M_c,KA*s,KB*s,60)
def test(label,**kw):
    ev,raw,PL,RH=events(**kw); ev=ev[~np.isnan(M_lo[ev,19])&~np.isnan(z60a[ev])]
    pools=[]
    for i in ev:
        m=(ep==ep[i])&(dd<=-0.25)&(s>=0.67*s[i])&(s<=1.5*s[i])&(np.abs(np.arange(n)-i)>20)&~np.isnan(z60a)
        pools.append(np.where(m)[0])
    ok=np.array([len(p)>=10 for p in pools]); ev=ev[ok]; pools=[p for p,o in zip(pools,ok) if o]
    stats=lambda idx:np.array([np.mean(z5a[idx]<0),np.mean(z20a[idx]<0),np.mean(z60a[idx]<0),np.median(z20a[idx]),np.nanmean(hlN[idx]),np.nanmean(upN60[idx])])
    obs=stats(ev)
    sims=np.array([stats(np.array([rng.choice(p) for p in pools])) for _ in range(5000)])
    names=['P5<0','P20<0','P60<0','medz20','hitL20(cur geom)','up60(cur geom)']
    print(f'== {label}: n={len(ev)} (same-episode, similar-vol matched baseline; 5000 random draws)')
    for k,nm in enumerate(names):
        p_lo=np.mean(sims[:,k]<=obs[k]); p_hi=np.mean(sims[:,k]>=obs[k])
        print(f'   {nm:18s} pattern={obs[k]:+.2f}  matched-baseline mean={sims[:,k].mean():+.2f} [2.5-97.5%: {np.percentile(sims[:,k],2.5):+.2f},{np.percentile(sims[:,k],97.5):+.2f}]  two-sided p={2*min(p_lo,p_hi):.2f}')
base=dict(N=10,ddc=-0.30,clv=0.8,rallyk=2.0,depthmax=1.5,reclaim=True,use_rally=True)
test('CORE',**base)
test('LOOSE2',N=10,ddc=-0.25,clv=0.7,rallyk=1.5,depthmax=2,reclaim=True)
test('LOOSE',N=10,ddc=-0.2,clv=0.6,rallyk=1.0,depthmax=99,reclaim=False)
test('F2 hammer@newlow',**{**base,'use_rally':False,'depthmax':99})
test('F3 rally+undercut any clv',**{**base,'clv':-1,'reclaim':False,'depthmax':99})
