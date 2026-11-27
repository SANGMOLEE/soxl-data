from pat2 import *
import io,contextlib
# matched baseline: bear days dd<=-25% with sfc within x0.75..1.33 of event's
bear=(d.dd.values<=-0.25)
hlN,upN20,_,_,_=first_hit(M_lo,M_c,KA*s,KB*s,20); _,upN60,_,_,_=first_hit(M_lo,M_c,KA*s,KB*s,60)
z20a=out['f20']/s; z60a=out['f60']/s; z5a=out['f5']/s
def matched(ev):
    E={'neg5':[],'neg20':[],'neg60':[],'hlN':[],'upN':[],'mz20':[]}
    for i in ev:
        m=bear&(s>=0.75*s[i])&(s<=1.33*s[i])&(np.abs(np.arange(n)-i)>20)
        E['neg5'].append(np.nanmean(np.where(np.isnan(z5a[m]),np.nan,z5a[m]<0)))
        E['neg20'].append(np.nanmean(np.where(np.isnan(z20a[m]),np.nan,z20a[m]<0)))
        E['neg60'].append(np.nanmean(np.where(np.isnan(z60a[m]),np.nan,z60a[m]<0)))
        E['hlN'].append(np.nanmean(hlN[m])); E['upN'].append(np.nanmean(upN60[m])); E['mz20'].append(np.nanmedian(z20a[m]))
    return {k:np.array(v) for k,v in E.items()}
rows=[]
def run(label,**kw):
    ev,raw,PL,RH=events(**kw)
    ev=ev[~np.isnan(M_lo[ev,19])]
    if len(ev)==0: return
    with contextlib.redirect_stdout(io.StringIO()):
        r=evaluate(ev,PL,RH,label)
    E=matched(ev)
    hl=r['hlo']; up=r['upo60']; n20=(r['z20']<0).astype(float); n20[np.isnan(r['z20'])]=np.nan
    n60=(r['z60']<0).astype(float); n60[np.isnan(r['z60'])]=np.nan
    n5=(r['z5']<0).astype(float)
    rows.append(dict(label=label,n=len(ev),raw=len(raw),eps=len(set(d.ep.values[ev])),
        pre03=np.mean(d.date.values[ev]<np.datetime64('2004-01-01')),
        hl20=np.nanmean(hl),hl20_mod=r['ph'].mean(),up60=np.nanmean(up),up60_mod=r['pu60'].mean(),
        neg5=np.mean(n5),neg5_b=np.nanmean(E['neg5']),
        neg20=np.nanmean(n20),neg20_b=np.nanmean(E['neg20']),mz20=np.nanmedian(r['z20']),
        neg60=np.nanmean(n60),neg60_b=np.nanmean(E['neg60']),mz60=np.nanmedian(r['z60']),
        hlN=np.nanmean(r['hln']),hlN_b=np.nanmean(E['hlN']),upN=np.nanmean(r['upn60']),upN_b=np.nanmean(E['upN'])))
base=dict(N=10,ddc=-0.30,clv=0.8,rallyk=2.0,depthmax=1.5,reclaim=True,use_rally=True)
run('CORE',**base)
for N in (5,20): run(f'N={N}',**{**base,'N':N})
for c in (0.6,0.7,0.9): run(f'clv>={c}',**{**base,'clv':c})
for dd_ in (-0.2,-0.25,-0.35,-0.4): run(f'dd<={dd_}',**{**base,'ddc':dd_})
for rk in (1.0,1.5,2.5,3.0): run(f'rally>={rk}σ',**{**base,'rallyk':rk})
run('depth any',**{**base,'depthmax':99}); run('depth<=1σ',**{**base,'depthmax':1.0})
run('no reclaim',**{**base,'reclaim':False})
run('LOOSE: N10 dd<=-20 clv>=.6 rally>=1σ anydepth noreclaim',N=10,ddc=-0.2,clv=0.6,rallyk=1.0,depthmax=99,reclaim=False)
run('LOOSE2: N10 dd<=-25 clv>=.7 rally>=1.5σ depth<=2',N=10,ddc=-0.25,clv=0.7,rallyk=1.5,depthmax=2,reclaim=True)
# component families (no rally)
run('F1 hammer@newlow (dd<=-30,clv>=.8,no rally)',**{**base,'use_rally':False,'reclaim':False,'depthmax':99})
run('F2 hammer@newlow+reclaim',**{**base,'use_rally':False,'depthmax':99})
run('F3 rally+undercut, any clv',**{**base,'clv':-1,'reclaim':False,'depthmax':99})
run('F3b rally+undercut, clv<0.5',**{**base,'clv':-1,'reclaim':False,'depthmax':99,'extra':d.clv.values<0.5})
pd.set_option('display.width',250)
T=pd.DataFrame(rows).set_index('label')
print(T.round(2).to_string())
T.to_csv('grid.csv')
