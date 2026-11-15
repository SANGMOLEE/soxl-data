# 공통 로더
import os, numpy as np, pandas as pd
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'); D=os.path.join(ROOT,'data')
_cache={}
def m1(sym):
    if sym not in _cache:
        d=pd.read_parquet(f"{D}/{sym}USDT_1m.parquet"); d=d.set_index('ts').sort_index(); _cache[sym]=d
    return _cache[sym]
def bars(sym, rule):
    k=(sym,rule)
    if k not in _cache:
        d=m1(sym); _cache[k]=d.resample(rule,label='left',closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum','qv':'sum','n':'sum'}).dropna(subset=['c'])
    return _cache[k]
def solt24():
    """SOLT 시간봉 24시간(평일): 야후 프리/정규/애프터 + 트레이딩뷰 BOATS 야간"""
    y=pd.read_csv(f"{D}/YF_SOLT_60m.csv",parse_dates=['ts']); y['src']='yahoo'
    b=pd.read_csv(f"{D}/TV_BOATS_SOLT_60_regular.csv",parse_dates=['ts']); b['src']='boats'
    s=pd.concat([y,b]).sort_values('ts').drop_duplicates('ts').set_index('ts')
    s['et']=s.index.tz_convert('America/New_York'); return s
def session_of(ts_utc):
    """SOLT 거래 가능 구간 분류 (미국 동부시간 기준). 공휴일은 무시(근사)"""
    et=ts_utc.tz_convert('America/New_York'); wd=et.weekday(); h=et.hour+et.minute/60
    if wd==5 or (wd==4 and h>=20) or (wd==6 and h<20): return 'weekend_closed'
    if 9.5<=h<16: return 'regular'
    if 4<=h<9.5: return 'pre'
    if 16<=h<20: return 'post'
    return 'overnight_boats'
