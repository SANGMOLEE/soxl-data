# Binance 현물 1분봉 일괄 수집 (data.binance.vision 월별/일별 zip + 최근분 REST)
import io, sys, zipfile, time, os, datetime as dt
import requests, pandas as pd, numpy as np
OUT=os.path.join(os.path.dirname(__file__),'..','data'); os.makedirs(OUT,exist_ok=True)
BASE='https://data.binance.vision/data/spot'
COLS=['ot','o','h','l','c','v','ct','qv','n','tbv','tbq','ig']
S=requests.Session()
def get(url,tries=4):
    for k in range(tries):
        try:
            r=S.get(url,timeout=60)
            if r.status_code==404: return None
            r.raise_for_status(); return r.content
        except Exception as e:
            time.sleep(2*(k+1))
    raise RuntimeError(url)
def parse(content):
    z=zipfile.ZipFile(io.BytesIO(content)); f=z.open(z.namelist()[0])
    d=pd.read_csv(f,header=None,names=COLS)
    if not np.issubdtype(d.ot.dtype,np.number): d=d[pd.to_numeric(d.ot,errors='coerce').notna()].astype({'ot':'int64'})
    ot=d.ot.astype('int64'); ot=np.where(ot>1e14, ot//1000, ot)      # 2025년부터 마이크로초
    out=pd.DataFrame({'ts':pd.to_datetime(ot,unit='ms',utc=True)})
    for c in ['o','h','l','c','v','qv','tbv']: out[c]=d[c].astype('float64').values
    out['n']=d.n.astype('int64').values
    return out
def months(start,end):
    y,m=start
    while (y,m)<=end:
        yield y,m; m+=1
        if m==13: y+=1; m=1
def fetch(sym,start):
    parts=[]
    today=dt.date(2026,11,15)
    for y,m in months(start,(2026,10)):
        c=get(f"{BASE}/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip")
        if c is None: print(sym,y,m,'missing'); continue
        parts.append(parse(c))
    d=dt.date(2026,11,1)
    while d<today:
        c=get(f"{BASE}/daily/klines/{sym}/1m/{sym}-1m-{d.isoformat()}.zip")
        if c is not None: parts.append(parse(c))
        d+=dt.timedelta(days=1)
    df=pd.concat(parts).drop_duplicates('ts').sort_values('ts')
    # 최근분: REST
    last=int(df.ts.iloc[-1].timestamp()*1000)+60000; rows=[]
    while True:
        r=S.get('https://data-api.binance.vision/api/v3/klines',params=dict(symbol=sym,interval='1m',startTime=last,limit=1000),timeout=30).json()
        if not r: break
        rows+=r; last=r[-1][0]+60000
        if len(r)<1000: break
    if rows:
        x=pd.DataFrame(rows,columns=COLS); x['ot']=x.ot.astype('int64')
        y_=pd.DataFrame({'ts':pd.to_datetime(x.ot,unit='ms',utc=True)})
        for c in ['o','h','l','c','v','qv','tbv']: y_[c]=x[c].astype('float64').values
        y_['n']=x.n.astype('int64').values; df=pd.concat([df,y_]).drop_duplicates('ts').sort_values('ts')
    df.to_parquet(f"{OUT}/{sym}_1m.parquet",index=False)
    print(sym,len(df),df.ts.iloc[0],df.ts.iloc[-1],flush=True)
if __name__=='__main__':
    for sym,start in [('SOLUSDT',(2020,8)),('BTCUSDT',(2017,8)),('ETHUSDT',(2017,8))]:
        if len(sys.argv)>1 and sym not in sys.argv[1:]: continue
        fetch(sym,start)
