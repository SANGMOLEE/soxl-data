# 기존 1분봉 parquet 뒤에 REST로 최신분 이어 붙이기
import sys, requests, pandas as pd, os
D=os.path.join(os.path.dirname(__file__),'..','data')
COLS=['ot','o','h','l','c','v','ct','qv','n','tbv','tbq','ig']
for sym in sys.argv[1:]:
    p=f"{D}/{sym}_1m.parquet"; df=pd.read_parquet(p)
    last=int(df.ts.iloc[-1].timestamp()*1000)+60000; rows=[]
    while True:
        r=requests.get('https://data-api.binance.vision/api/v3/klines',params=dict(symbol=sym,interval='1m',startTime=last,limit=1000),timeout=30).json()
        if not r: break
        rows+=r; last=r[-1][0]+60000
        if len(r)<1000: break
    if rows:
        x=pd.DataFrame(rows,columns=COLS)
        y=pd.DataFrame({'ts':pd.to_datetime(x.ot.astype('int64'),unit='ms',utc=True)})
        for c in ['o','h','l','c','v','qv','tbv']: y[c]=x[c].astype('float64').values
        y['n']=x.n.astype('int64').values
        df=pd.concat([df,y]).drop_duplicates('ts').sort_values('ts'); df.to_parquet(p,index=False)
    print(sym,len(df),df.ts.iloc[-1],flush=True)
