# SOLT 등 야후 장중봉 (정규장+프리/애프터) 수집
import requests, pandas as pd, os, sys, time
OUT=os.path.join(os.path.dirname(__file__),'..','data'); os.makedirs(OUT,exist_ok=True)
H={'User-Agent':'Mozilla/5.0'}
def chart(sym, rng, itv, prepost=True, p1=None, p2=None):
    params=dict(interval=itv, includePrePost=str(prepost).lower(), events='div,splits')
    if p1: params.update(period1=int(p1), period2=int(p2))
    else: params['range']=rng
    r=requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}',params=params,headers=H,timeout=30).json()
    res=r['chart']['result'][0]; q=res['indicators']['quote'][0]
    df=pd.DataFrame({'ts':pd.to_datetime(res['timestamp'],unit='s',utc=True),'o':q['open'],'h':q['high'],'l':q['low'],'c':q['close'],'v':q['volume']}).dropna(subset=['c'])
    meta=res['meta']; return df, meta
if __name__=='__main__':
    for sym in ['SOLT','BITU','SOL-USD','BTC-USD']:
        for rng,itv in [('730d','60m'),('60d','5m'),('60d','15m'),('7d','1m')]:
            try:
                df,meta=chart(sym,rng,itv, prepost=not sym.endswith('-USD'))
                df.to_csv(f"{OUT}/YF_{sym}_{itv}.csv",index=False)
                print(sym,itv,len(df),df.ts.iloc[0],df.ts.iloc[-1],meta.get('exchangeTimezoneName'),meta.get('currentTradingPeriod',{}).get('pre',{}))
            except Exception as e: print(sym,itv,'ERR',e)
            time.sleep(1)
