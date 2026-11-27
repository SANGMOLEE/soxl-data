"""SOXX 차트 모양 연구 공통 (2026-11-27)
- SOX 지수 일봉(1994~): 고가·저가·종가만 사용 (2005년 이전 시가는 전일 종가 복사 결함)
- SOXX: 2026-11-05 3:1 분할 미조정 → 그 전 가격을 3으로 나눔
- 금리 국면: scripts/reverify_20261124/base.py 의 HIKE/CUTS 그대로"""
import os, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..",".."))
OUT=os.path.join(ROOT,"research","soxx_chart_shape","output")
CH=os.path.join(ROOT,"research","soxx_chart_shape","charts")
def load(n):
    d=pd.read_csv(os.path.join(ROOT,"data","prices",f"{n}.csv"),parse_dates=["date"]).set_index("date").sort_index()
    d=d[~d.index.duplicated()][["open","high","low","close"]].astype(float)
    return d
SOX=load("SOX"); SOXL=load("SOXL")
SOXX=load("SOXX"); SOXX.loc[SOXX.index<"2026-11-05",["open","high","low","close"]]/=3.0
VIX=pd.to_numeric(pd.read_csv(os.path.join(ROOT,"data","macro","VIXCLS.csv"),parse_dates=["date"]).set_index("date")["value"],errors="coerce").dropna()
VIX.loc[pd.Timestamp("2026-11-20")]=35.54; VIX=VIX.sort_index()
HIKE=[("1994-02-04","1995-07-05"),("1999-06-30","2000-12-31"),("2004-06-30","2006-12-31"),("2015-12-16","2019-06-30"),("2022-03-16","2024-01-31"),("2026-09-16","2027-12-31")]
CUTS=[("1995-07-06","1996-06-30"),("1998-09-29","1999-03-31"),("2001-01-03","2003-12-31"),("2007-09-18","2009-06-30"),("2019-07-31","2020-12-31"),("2024-09-18","2026-06-30")]
def regime(t):
    for a,b in HIKE:
        if pd.Timestamp(a)<=t<=pd.Timestamp(b): return "인상기"
    for a,b in CUTS:
        if pd.Timestamp(a)<=t<=pd.Timestamp(b): return "인하기"
    return "그 외"
d=SOX.copy()
d["h252"]=d.high.rolling(252,min_periods=120).max()
d["dd"]=d.low/d.h252-1                       # 장중 저가 기준 52주 고점 대비
d["ddc"]=d.close/d.close.rolling(252,min_periods=120).max()-1
d["pos"]=((d.close-d.low)/(d.high-d.low)).clip(0,1)
d["ma200w"]=d.close.rolling(1000,min_periods=900).mean()   # 200주 ≈ 1000거래일
d["vix"]=VIX.reindex(d.index).ffill()
dl=np.log(d.close).diff()
def rsi(c,n=14):
    x=c.diff(); up=x.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-x.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return 100-100/(1+up/dn)
d["rsi"]=rsi(d.close)
IDX=d.index; N=len(IDX)
H=d.high.values; Lo=d.low.values; C=d.close.values
# 사이클 (2010년 이후는 11/25 재검증 보고서 표, 그 전은 참고)
CYCLES=[("1995-09-?","1996-07-?",False),]
CYC10=[("2011-02-17","2011-10-03"),("2015-06-01","2016-02-11"),("2018-03-12","2018-12-24"),("2020-02-19","2020-03-18"),("2021-12-27","2022-10-14"),("2024-07-10","2025-04-08")]
NOW_PEAK="2026-06-22"
def st(x,nm="",w=30):
    x=np.sort(np.asarray([v for v in x if v==v],dtype=float))
    if len(x)==0: return f"  {nm:{w}s}   0건"
    ex=x[:-3].mean() if len(x)>3 else np.nan
    return f"  {nm:{w}s} {len(x):3d}건 | 플러스 {(x>0).mean()*100:3.0f}% | 중앙 {np.median(x):+6.1f}% | 상위3뺀 {ex:+6.1f}% | 평균 {x.mean():+6.1f}% | 최악 {x.min():+6.1f}%"
