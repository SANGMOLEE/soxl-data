# 사이클 바닥 주변 구간만 알트 1분봉 수집 (2018-12, 2020-03, 2022 바닥)
import sys; sys.path.insert(0,'scripts')
from fetch_binance_1m import get, parse, BASE
import pandas as pd, os
OUT=os.path.join(os.path.dirname(__file__),'..','data')
WIN=[(y,m) for y in [2018] for m in [10,11,12]]+[(2019,m) for m in range(1,13)]+[(2020,m) for m in range(2,13)]+[(2021,m) for m in range(1,4)]+[(2022,m) for m in range(5,13)]+[(2023,m) for m in range(1,13)]
SYMS=['BNBUSDT','LTCUSDT','ADAUSDT','XRPUSDT','TRXUSDT','XLMUSDT','ETCUSDT','LINKUSDT','DOGEUSDT','AVAXUSDT','DOTUSDT','MATICUSDT']
for sym in SYMS:
    parts=[]
    for y,m in WIN:
        c=get(f"{BASE}/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip")
        if c is not None: parts.append(parse(c))
    if parts:
        d=pd.concat(parts).drop_duplicates('ts').sort_values('ts'); d.to_parquet(f"{OUT}/{sym}_1m_win2.parquet",index=False)
        print(sym,len(d),d.ts.iloc[0],d.ts.iloc[-1],flush=True)
