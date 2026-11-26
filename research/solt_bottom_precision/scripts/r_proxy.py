# R2. SOL 대리 실현가격: 장기 VWAP이 BTC·ETH 온체인 실현가격을 얼마나 잘 따라가나 → SOL에 적용
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250)
E='data/ext/'
def daily(sym):
    d=m1(sym).resample('D').agg({'c':'last','v':'sum','qv':'sum','l':'min'}); d.index=d.index.tz_localize(None); return d.dropna()
real={a:pd.read_csv(E+f'CM_{a}_REALIZED.csv',parse_dates=['date']).set_index('date').realized_price for a in ['BTC','ETH']}
def vwap_roll(d,n): return d.qv.rolling(n,min_periods=int(n*0.8)).sum()/d.v.rolling(n,min_periods=int(n*0.8)).sum()
def vwap_ew(d,hl):
    a=1-0.5**(1/hl); return d.qv.ewm(alpha=a,adjust=False).mean()/d.v.ewm(alpha=a,adjust=False).mean()
res=[]
for a in ['BTC','ETH']:
    d=daily(a)
    for kind,par in [('roll',365),('roll',540),('roll',730),('roll',1095),('roll',1460),('ew',180),('ew',365),('ew',540),('ew',730)]:
        p=vwap_roll(d,par) if kind=='roll' else vwap_ew(d,par)
        j=pd.concat([p,real[a]],axis=1,keys=['proxy','real']).dropna()['2020-08':]
        e=np.log(j.proxy/j.real); res.append(dict(asset=a,proxy=f'{kind}{par}',bias=e.mean(),mae=e.abs().mean(),last_ratio=j.proxy.iloc[-1]/j.real.iloc[-1]))
R=pd.DataFrame(res); print("== 대리지표(VWAP) vs 온체인 실현가격, 2020-08~ (로그 오차)")
print(R.pivot(index='proxy',columns='asset',values=['bias','mae','last_ratio']).round(3).to_string())
R.to_csv('output/r_proxy_fit.csv',index=False)
