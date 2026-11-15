# 트레이딩뷰 차트 데이터 웹소켓에서 봉 수집 (비로그인 공개 데이터)
import json, random, string, re, sys, os, time
import pandas as pd
from websocket import create_connection
OUT=os.path.join(os.path.dirname(__file__),'..','data')
def _rs(n=12): return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
def _msg(f,p): s=json.dumps({"m":f,"p":p},separators=(',',':')); return f"~m~{len(s)}~m~{s}"
def fetch(symbol, interval='60', n_bars=5000, session='extended', timeout=40):
    ws=create_connection("wss://data.tradingview.com/socket.io/websocket",header=["Origin: https://www.tradingview.com"],timeout=timeout)
    cs="cs_"+_rs()
    for f,p in [("set_auth_token",["unauthorized_user_token"]),("chart_create_session",[cs,""]),
                ("resolve_symbol",[cs,"sym1",'='+json.dumps({"symbol":symbol,"adjustment":"splits","session":session})]),
                ("create_series",[cs,"s1","s1","sym1",interval,n_bars])]:
        ws.send(_msg(f,p))
    raw=""; t0=time.time()
    while time.time()-t0<timeout:
        try: r=ws.recv()
        except Exception: break
        if re.match(r"~m~\d+~m~~h~\d+",r): ws.send(r); continue      # heartbeat
        raw+=r
        if 'series_completed' in r or 'symbol_error' in r or 'critical_error' in r: break
    ws.close()
    m=re.search(r'"s":\[(.+?)\}\]',raw)
    if not m:
        err=re.findall(r'(symbol_error|critical_error)[^~]{0,200}',raw); return None, err[:2]
    rows=re.findall(r'"v":\[(.*?)\]',m.group(1))
    data=[list(map(float,x.split(',')))[:6] for x in rows]
    df=pd.DataFrame(data,columns=['t','o','h','l','c','v'][:len(data[0])])
    df['ts']=pd.to_datetime(df.t,unit='s',utc=True); return df.drop(columns='t'), None
if __name__=='__main__':
    jobs=[('BOATS:SOLT','60','regular'),('BOATS:SOLT','5','regular'),('NASDAQ:SOLT','60','extended'),('NASDAQ:SOLT','5','extended'),
          ('BINANCE:SOLUSDT','60','regular'),('BINANCE:BTCUSDT','60','regular'),('COINBASE:SOLUSD','60','regular')]
    for sym,itv,ses in jobs:
        df,err=fetch(sym,itv,5000,ses)
        if df is None: print(sym,itv,ses,'FAIL',err); continue
        fn=f"{OUT}/TV_{sym.replace(':','_')}_{itv}_{ses}.csv"; df.to_csv(fn,index=False)
        print(sym,itv,ses,len(df),df.ts.iloc[0],df.ts.iloc[-1],flush=True)
