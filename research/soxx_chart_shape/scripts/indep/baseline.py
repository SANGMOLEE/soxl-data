from feat import *
from math import erf
class norm:
    @staticmethod
    def cdf(x): return 0.5*(1+erf(x/np.sqrt(2)))
d=add_fc(load()); n=len(d)
C0=d.close.iloc[-1]; L=8129.234375; U=9728.1201171875
aL=np.log(L/C0); bU=np.log(U/C0); s_now=d.sfc.iloc[-1]
print(f'aL={aL:.4f} bU={bU:.4f} sfc={s_now:.4f} aL/s={aL/s_now:.3f} bU/s={bU/s_now:.3f}')
# ---- B1 analytic Gaussian BM continuous lows
for s in (0.040,0.0453,0.050,0.055,0.062):
    p1=2*norm.cdf(aL/(s*np.sqrt(20)))
    print(f'B1 s={s:.4f} P(min<L,20d cont)={p1:.3f}  P(up first, cont both, no time limit)={-aL/(bU-aL):.3f}')
# ---- B2 iid bootstrap of normalized bars
sp=d.sfc.shift(1); Cp=d.close.shift(1)
z=pd.DataFrame({'zr':d.r/sp,'zl':np.log(d.low/Cp)/sp,'zh':np.log(d.high/Cp)/sp,'dd':d.dd.shift(1),'date':d.date}).dropna()
rng=np.random.default_rng(7)
def sim(pool,s,T=60,N=200000,demean=True,blocks=None):
    P=pool[['zr','zl','zh']].values.copy()
    mu=P[:,0].mean()
    if demean: P=P-mu
    idx=rng.integers(0,len(P),(N,T))
    zr=P[idx,0]*s; zl=P[idx,1]*s; zh=P[idx,2]*s
    cum=np.cumsum(zr,1); prev=np.c_[np.zeros(N),cum[:,:-1]]
    lo=prev+zl; c=cum
    return lo,c,mu
for name,pool in [('all',z),('bear dd<=-20%',z[z.dd<=-0.2]),('pre2005 bear',z[(z.dd<=-0.2)&(z.date<'2005')])]:
  for s in (0.040,0.0453,0.055,0.062):
    lo,c,mu=sim(pool,s)
    hl,up,nei,il,iu=first_hit(lo,c,aL,bU,20)
    _,up60,nei60,_,_=first_hit(lo,c,aL,bU,60)
    f5=c[:,4];f20=c[:,19];f60=c[:,59]
    q=lambda f:(np.mean(f<0),np.median(f),np.percentile(f,10),np.percentile(f,5))
    print(f'B2[{name} n={len(pool)} mu_z={mu:.3f}] s={s:.4f} P(hitL20)={hl.mean():.3f} P(upFirst within20)={up.mean():.3f} (neither {nei.mean():.3f}) within60={up60.mean():.3f} (neither {nei60.mean():.3f})')
    if s==0.0453:
        for h,f in ((5,f5),(20,f20),(60,f60)):
            p,m,p10,p5=q(f); print(f'    h={h}: P(<0)={p:.3f} median={np.expm1(m):+.3%} p10={np.expm1(p10):+.2%} p5={np.expm1(p5):+.2%} ')
# non-demeaned (bear drift) variant
pool=z[z.dd<=-0.2]
lo,c,mu=sim(pool,0.0453,demean=False)
hl,up,nei,il,iu=first_hit(lo,c,aL,bU,20); _,up60,nei60,_,_=first_hit(lo,c,aL,bU,60)
print('B2 bear WITH bear-regime drift: hitL20',hl.mean().round(3),'up20',up.mean().round(3),'up60',up60.mean().round(3),'P(f20<0)',(c[:,19]<0).mean().round(3),'P(f60<0)',(c[:,59]<0).mean().round(3))
