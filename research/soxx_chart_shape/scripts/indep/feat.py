import pandas as pd, numpy as np
def load():
    d=pd.read_csv('/home/user/soxl-data/data/prices/SOX.csv',parse_dates=['date'])
    d=d[['date','high','low','close']].reset_index(drop=True)
    d['r']=np.log(d.close).diff()
    for w in (5,10,20,60,120):
        d[f's{w}']=d.r.rolling(w).std()
    # EWMA vol (lambda .94 ~ RiskMetrics) and .97
    d['ew94']=np.sqrt((d.r**2).ewm(alpha=0.06,adjust=False).mean())
    d['ew97']=np.sqrt((d.r**2).ewm(alpha=0.03,adjust=False).mean())
    d['max252']=d.close.rolling(252,min_periods=60).max()
    d['dd']=d.close/d.max252-1
    d['clv']=(d.close-d.low)/(d.high-d.low)
    d['rng']=np.log(d.high/d.low)
    v=pd.read_csv('/home/user/soxl-data/data/macro/VIXCLS.csv',parse_dates=['date'])
    v['value']=pd.to_numeric(v['value'],errors='coerce')
    d=d.merge(v[['date','value']].rename(columns={'value':'vix'}),on='date',how='left')
    d['vix']=d.vix.ffill()
    return d

def add_fc(d):
    r2=d.r**2
    for w in (5,20,60):
        d[f'rv{w}']=np.sqrt(r2.rolling(w).mean())
    # HAR 20d coefficients (full-sample fit, used only as a vol normalizer; checked vs pre-2016 fit)
    b=np.array([-0.652,0.11,0.344,0.381])
    d['sfc']=np.exp(b[0]+b[1]*np.log(d.rv5)+b[2]*np.log(d.rv20)+b[3]*np.log(d.rv60))
    return d

def fwd(d,H=60):
    n=len(d); C=d.close.values; Lo=d.low.values; Hi=d.high.values
    out={}
    for h in (5,20,60):
        f=np.full(n,np.nan); f[:n-h]=np.log(C[h:]/C[:n-h]); out[f'f{h}']=f
    # forward matrices of log low/high/close rel to C_t, days 1..H
    M_lo=np.full((n,H),np.nan); M_hi=np.full((n,H),np.nan); M_c=np.full((n,H),np.nan)
    for k in range(1,H+1):
        M_lo[:n-k,k-1]=np.log(Lo[k:]/C[:n-k]); M_hi[:n-k,k-1]=np.log(Hi[k:]/C[:n-k]); M_c[:n-k,k-1]=np.log(C[k:]/C[:n-k])
    return out,M_lo,M_hi,M_c

def first_hit(M_lo,M_c,a,b,T):
    """a<0 lower log barrier on lows (strict <), b>0 upper on closes (strict >). returns (hitLowWithinT, upFirst) arrays; nan if incomplete.
    upFirst: close>b occurs on day before first low<a day (same day: count as low first, conservative)."""
    a=np.broadcast_to(np.asarray(a,float),(M_lo.shape[0],)); b=np.broadcast_to(np.asarray(b,float),(M_lo.shape[0],))
    lo=M_lo[:,:T]; c=M_c[:,:T]
    complete=~np.isnan(lo[:,-1])
    hl=(lo<a[:,None]); hu=(c>b[:,None])
    big=10**6
    il=np.where(hl.any(1),hl.argmax(1),big); iu=np.where(hu.any(1),hu.argmax(1),big)
    hitL=hl.any(1).astype(float); hitL[~complete]=np.nan
    up=(iu<il).astype(float)
    # unresolved within T (neither) -> nan in race? keep separate
    neither=(il==big)&(iu==big)
    up_res=up.copy(); up_res[~complete]=np.nan
    return hitL, up_res, neither, il, iu

def wilson(k,n,z=1.96):
    if n==0: return (np.nan,np.nan,np.nan)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return p,c-h,c+h
