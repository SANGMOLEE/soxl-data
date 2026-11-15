# H. 검증: "BTC 저점 = SOL(SOLT) 저점"인가 — 일봉 종가 기준
from sigs import *
pd.set_option('display.width',220)
b=btc['2020-06':]; s=sol
# BTC 주요 저점: zigzag 20% (2020-06 이후)
def zz_lows(x,th=0.20):
    lows=[]; mode='up'; hi=x.iloc[0]; lo=x.iloc[0]; lo_i=x.index[0]
    for t,v in x.items():
        if mode=='up':
            if v>hi: hi=v
            if v<=hi*(1-th): mode='down'; lo=v; lo_i=t
        else:
            if v<lo: lo=v; lo_i=t
            if v>=lo*(1+th): lows.append(lo_i); mode='up'; hi=v
    return lows
rows=[]
for L in zz_lows(b):
    w=s[L-pd.Timedelta(days=30):L+pd.Timedelta(days=60)]; m=w.idxmin()
    row=dict(BTC저점=L.date(),BTC=round(b[L]),SOL_그날=round(s[L],2),SOL최저일=m.date(),차이일=(m-L).days,SOL최저=round(w.min(),2),그날대비=w.min()/s[L]-1)
    if L>=solt.index[0]:
        sl=solt_raw[L-pd.Timedelta(days=30):L+pd.Timedelta(days=60)]; Ls=solt_raw.index[solt_raw.index.searchsorted(L)]
        row.update(SOLT_그날=round(solt_raw[Ls],2),SOLT최저일=sl.idxmin().date(),SOLT최저=round(sl.min(),2),SOLT그날대비=sl.min()/solt_raw[Ls]-1)
    rows.append(row)
o=pd.DataFrame(rows); print("== BTC 주요 저점(20% 반등) vs 그 전후(-30일~+60일) SOL·SOLT 최저 종가")
print(o.round(3).to_string(index=False))
same=(o.차이일.abs()<=3).mean(); print(f"\nSOL 최저가 BTC 저점 ±3일 안: {same:.0%} ({(o.차이일.abs()<=3).sum()}/{len(o)}),  SOL이 그날보다 10% 이상 더 낮았던 경우: {(o.그날대비<-0.10).sum()}/{len(o)}")
x=o.dropna(subset=['SOLT최저']); print(f"SOLT 상장 후 {len(x)}번 중 SOLT 최저가 BTC 저점 ±3일 안: {(abs(pd.to_datetime(x.SOLT최저일)-pd.to_datetime(x.BTC저점)).dt.days<=3).sum()}번")
