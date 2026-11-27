from feat import *
d=pd.read_pickle('d.pkl'); s_now=d.sfc.iloc[-1]
d['frv20']=np.sqrt((d.r**2)[::-1].rolling(20).mean()[::-1].shift(-1))
m=(d.dd<=-0.3)&d.sfc.between(0.03,0.07)
print('calib realized fwd20 RMS / sfc on B3 days: median',(d.frv20/d.sfc)[m].median().round(3),'mean',(d.frv20/d.sfc)[m].mean().round(3))
mm=m&d.hl20.notna()
x=d[mm]
pre=(x.date>='2000-01-01')&(x.date<'2004-01-01')
for lab,xx in (('B3 all',x),('B3 excl 2000-03',x[~pre]),('B3 only 2000-03',x[pre])):
    g=xx.groupby('ep').agg(hl=('hl20','mean'),up=('up60','mean'),n=('hl20','size'))
    print(f'{lab}: days={len(xx)} eps={len(g)} hitL20={xx.hl20.mean():.3f} up60={xx.up60.mean():.3f} | episode-equal-weight hitL20={g.hl.mean():.3f} up60={g.up.mean():.3f}')
    for h in (5,20,60):
        z=xx[f'z{h}'].dropna()*s_now
        print(f'     h={h}: P(<0)={(z<0).mean():.3f} median={np.expm1(z.median()):+.1%} p10={np.expm1(z.quantile(.1)):+.1%} p5={np.expm1(z.quantile(.05)):+.1%}')
# Gaussian w/ HAR horizon vols, zero drift (log), close-to-close
for h,sig in ((5,0.048),(20,0.046),(60,0.0435)):
    S=sig*np.sqrt(h)
    print(f'Gauss h={h} sig={sig}: median 0%, p10={np.expm1(-1.2816*S):+.1%} p5={np.expm1(-1.645*S):+.1%}')
