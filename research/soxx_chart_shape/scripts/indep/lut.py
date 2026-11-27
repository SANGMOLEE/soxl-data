# Vol-only model lookup table (B2: iid bootstrap of ex-ante-vol-normalized daily bars from bear days, zero drift)
from feat import *
d=pd.read_pickle('d.pkl')
sp=d.sfc.shift(1); Cp=d.close.shift(1)
z=pd.DataFrame({'zr':d.r/sp,'zl':np.log(d.low/Cp)/sp,'zh':np.log(d.high/Cp)/sp,'dd':d.dd.shift(1)}).dropna()
P=z[z.dd<=-0.2][['zr','zl','zh']].values; P=P-P[:,0].mean()
print('pool std zr',P[:,0].std(), 'mean zl',P[:,1].mean())
rng=np.random.default_rng(11); N=200000; T=60
idx=rng.integers(0,len(P),(N,T))
zr=P[idx,0]; zl=P[idx,1]
cum=np.cumsum(zr,1); prev=np.c_[np.zeros(N),cum[:,:-1]]; lo=prev+zl
np.save('sim_lo.npy',lo.astype(np.float32)); np.save('sim_c.npy',cum.astype(np.float32))
