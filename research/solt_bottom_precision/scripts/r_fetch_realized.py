# R. 실현가격 자료 수집: CoinMetrics(BTC·ETH MVRV→실현가격), BGeometrics(BTC 장기·단기 보유자 실현가격)
import requests, pandas as pd, time, os
OUT='data/ext/'
U="https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
def cm(asset):
    rows=[]; url=U; params=dict(assets=asset,metrics='CapMVRVCur,PriceUSD',frequency='1d',page_size=10000,start_time='2013-01-01',paging_from='start')
    for _ in range(20):
        j=requests.get(url,params=params,timeout=60).json(); rows+=j.get('data',[]); url=j.get('next_page_url'); params=None
        if not url: break
    d=pd.DataFrame(rows); d['date']=pd.to_datetime(d.time).dt.tz_localize(None).dt.normalize()
    d['mvrv']=pd.to_numeric(d.CapMVRVCur,errors='coerce'); d['price']=pd.to_numeric(d.PriceUSD,errors='coerce')
    d=d.dropna(subset=['mvrv','price']); d['realized_price']=d.price/d.mvrv
    return d[['date','price','mvrv','realized_price']]
for a in ['btc','eth']:
    d=cm(a); d.to_csv(OUT+f'CM_{a.upper()}_REALIZED.csv',index=False); print(a,len(d),d.date.min().date(),d.date.max().date(),d.tail(1).round(3).to_dict('records'))
for nm in ['realized-price','sth-realized-price','lth-realized-price']:
    try:
        r=requests.get('https://bitcoin-data.com/v1/'+nm,timeout=60); j=r.json()
        d=pd.DataFrame(j); print(nm,r.status_code,d.shape,list(d.columns)[:4],d.tail(1).to_dict('records'))
        d.to_csv(OUT+f'BG_{nm}.csv',index=False)
    except Exception as e: print(nm,'ERR',e)
    time.sleep(1)
