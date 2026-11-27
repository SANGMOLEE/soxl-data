from feat import *
d=add_fc(load()); n=len(d)
C0=d.close.iloc[-1]; L=8129.234375; U=9728.1201171875
aL=np.log(L/C0); bU=np.log(U/C0); s_now=d.sfc.iloc[-1]
ka=aL/s_now; kb=bU/s_now
out,M_lo,M_hi,M_c=fwd(d,H=250)
s=d.sfc.values
hl20,up20,_,_,_=first_hit(M_lo,M_c,ka*s,kb*s,20)
_,up60,nei60,_,_=first_hit(M_lo,M_c,ka*s,kb*s,60)
_,up250,nei250,_,_=first_hit(M_lo,M_c,ka*s,kb*s,250)
d['hl20']=hl20; d['up20']=up20; d['up60']=up60; d['up250']=up250; d['nei60']=nei60
for h in (5,20,60): d[f'f{h}']=out[f'f{h}']; d[f'z{h}']=out[f'f{h}']/s
# episodes: bear runs dd<=-20%, merge gaps<60d
b=(d.dd<=-0.20).values; ep=np.full(n,-1); e=-1; last=-999
for i in range(n):
    if b[i]:
        if i-last>60: e+=1
        ep[i]=e; last=i
d['ep']=ep
eps=d[d.ep>=0].groupby('ep').date.agg(['min','max','size']); print(eps.to_string())
d.to_pickle('d.pkl')
def summ(m,label):
    x=d[m & d.hl20.notna()]
    k=x.hl20.sum(); nn=len(x); p,lo,hi=wilson(k,nn)
    xs=x[x.up60.notna()]
    p2,l2,h2=wilson(xs.up60.sum(),len(xs))
    print(f'{label}: days={nn} episodes={x.ep.nunique()} hitL20={p:.3f} [{lo:.3f},{hi:.3f}] up20={x.up20.mean():.3f} up60={p2:.3f} [{l2:.3f},{h2:.3f}] up250={x.up250.mean():.3f}')
    for h in (5,20,60):
        xx=d[m & d[f'z{h}'].notna()]
        zz=xx[f'z{h}']*s_now
        print(f'     h={h} n={len(xx)} P(<0)={(zz<0).mean():.3f} median={np.expm1(zz.median()):+.2%} p10={np.expm1(zz.quantile(.1)):+.1%} p5={np.expm1(zz.quantile(.05)):+.1%} worst={np.expm1(zz.min()):+.1%}')
    # by-episode shares
    g=x.groupby('ep').agg(n=('hl20','size'),hl=('hl20','mean'),up60=('up60','mean'),start=('date','min'))
    print('     by episode:', '; '.join(f"{r.start.year}:{r.n}d hl{r.hl:.2f} up{r.up60:.2f}" for _,r in g.iterrows()))
for ddc in (-0.25,-0.30,-0.35):
    for lo_,hi_ in ((0.03,0.07),(0.035,0.06)):
        m=(d.dd<=ddc)&(d.sfc.between(lo_,hi_))
        summ(m,f'B3 dd<={ddc} sfc in[{lo_},{hi_}]')
summ((d.dd<=-0.30),'B3 dd<=-30% any vol')
summ(d.sfc>0,'ALL days any vol')
