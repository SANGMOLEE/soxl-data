# B. 실시간 규칙 백테스트 엔진 (신호: 기초자산 1배 가격·BTC, 체결: 다음 거래일 이후, 2배 일일재조정 합성)
from lib import *
BOTTOMS={'2015-01-14':['ltc','xrp','dash','xmr','doge'],
         '2018-12-15':['eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx'],
         '2020-03-12':['eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx'],
         '2022-11-21':['sol','eth','ada','avax','dot','link','bnb','doge','xrp','ltc','xlm']}
def raw(a): return sol if a=='sol' else (btc if a=='btc' else cm[a])
B_S=sess(btc)
def signals(p, b, name):
    """p, b: 거래일 표본 (신호 계산용, 같은 인덱스). 1=보유, 0=현금"""
    k,*par=name.split('_')
    if k=='MA':   n=int(par[0]); return (p>p.rolling(n).mean()).astype(int)
    if k=='XMA':  f,s=map(int,par); return (p.rolling(f).mean()>p.rolling(s).mean()).astype(int)
    if k=='BMA':  n=int(par[0]); return (b>b.rolling(n).mean()).astype(int)
    if k=='MAB':  n,m=map(int,par); return ((p>p.rolling(n).mean())&(b>b.rolling(m).mean())).astype(int)
    if k=='DON':  N,M=map(int,par)
    if k=='DON':
        hi=p.rolling(N).max().shift(1); lo=p.rolling(M).min().shift(1); s=pd.Series(np.nan,p.index)
        s[p>hi]=1; s[p<lo]=0; return s.ffill().fillna(0).astype(int)
    if k=='MAT':  # MA 진입 + (MA 이탈 또는 2배NAV 고점대비 -X% 손절) 청산, 재진입은 MA 재돌파 시
        n,x=int(par[0]),float(par[1])/100; up=(p>p.rolling(n).mean()).values; r=p.pct_change().fillna(0).values
        pos=np.zeros(len(p),int); inpos=False; peak=1; nav=1; armed=True
        for i in range(len(p)):
            if inpos:
                nav*=1+2*r[i]; peak=max(peak,nav)
                if (not up[i]) or nav<peak*(1-x): inpos=False; armed=not up[i]
            else:
                if not up[i]: armed=True
                if up[i] and armed: inpos=True; nav=1; peak=1
            pos[i]=int(inpos)
        return pd.Series(pos,p.index)
    if k=='HOLD': return pd.Series(1,p.index)
    raise ValueError(name)
def run(p, sig, cost=0.20, lag=1, tc=0.002, start=None, end=None):
    """sig[t]는 t일 종가에 확정 → pos[t+lag]부터 보유. 반환: 자산곡선(시작 1), 노출률, 거래수"""
    pos=sig.shift(lag).fillna(0)
    sl=slice(start,end); p=p[sl]; pos=pos[sl].copy(); pos.iloc[0]=pos.iloc[0]  # 구간 첫날 이전 포지션은 무시
    r=p.pct_change().fillna(0); dt=p.index.to_series().diff().dt.days.fillna(0)
    held=pos.shift(1).fillna(0)        # t일 수익은 t-1일 종가 보유분이 받음
    held.iloc[0]=0
    g=1+held*((1+2*r).clip(lower=0)*np.exp(-cost*dt/365)-1)
    trades=held.diff().abs().fillna(held.iloc[0]); g=g*(1-tc*trades)
    eq=g.cumprod(); mdd=(eq/eq.cummax()-1).min()
    return eq, held.mean(), int(trades.sum()), mdd
def episode(a, D, name, pre=90, post=540, **kw):
    s=raw(a).dropna(); p=sess(s); b=B_S.reindex(p.index).ffill()
    st=pd.Timestamp(D)-pd.Timedelta(days=pre); en=pd.Timestamp(D)+pd.Timedelta(days=post)
    if p.index[0]>st-pd.Timedelta(days=150): return None   # 이동평균 예열 부족
    sig=signals(p,b,name)
    eq,ex,tr,mdd=run(p,sig,start=st,end=en,**kw)
    return dict(asset=a,D=D,rule=name,mult=eq.iloc[-1],exposure=ex,trades=tr,mdd=mdd)
