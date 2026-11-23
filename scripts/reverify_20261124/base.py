"""재검증용 독립 데이터 기반 (2026-11-24 새로 작성, 이전 core/common 코드 미사용)
- 2010-06-01 이전: SOX 일간 수익률 x3 (연 1% 비용) 합성 SOXL, x-3 합성 SOXS
- 이후: 실제 SOXL/SOXS 일봉. 3배 관계에서 6%p 넘게 벗어난 날은 데이터 결함으로 보고 합성으로 대체
- 시가/고가/저가는 '전일 종가 대비 비율'로 들고 다님 (합성 구간은 SOX 비율 x3)"""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings("ignore")
import os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","data")+"/"
def load(n):
    d=pd.read_csv(D+f"prices/{n}.csv",parse_dates=["date"]).set_index("date").sort_index()
    return d[~d.index.duplicated()][["open","high","low","close"]].astype(float)
def fred(n):
    s=pd.read_csv(D+f"macro/{n}.csv",parse_dates=["date"]).set_index("date")["value"]
    return pd.to_numeric(s,errors="coerce").dropna()
SOX=load("SOX"); SOXL=load("SOXL"); SOXS=load("SOXS"); QQQ=load("QQQ")
SOXS=SOXS.drop(pd.Timestamp("2026-05-26"),errors="ignore")      # 분할 소급 미조정일 (KNOWN_ISSUES 1)
VIX=fred("VIXCLS"); VIX.loc[pd.Timestamp("2026-11-20")]=35.54; VIX=VIX.sort_index()   # 11/20은 FRED 미반영 → 수기값
HY=fred("BAMLH0A0HYM2")
CUT=pd.Timestamp("2010-06-01"); FEE=0.01/252
cal=SOX.index[SOX.index<CUT].append(SOXL.index[SOXL.index>=CUT])
sx=SOX.close.reindex(cal).ffill(); rs=sx.pct_change()
def rel(df,col): return (df[col]/df.close.shift(1)-1).reindex(cal)
soxrel={c:rel(SOX,c) for c in ("open","high","low")}
def splice(real,sign,bad_extra=()):
    rr=real.close.pct_change().reindex(cal)
    syn=sign*3*rs-FEE
    ok_sox=SOX.close.reindex(cal).notna()&SOX.close.reindex(cal).shift(1).notna()
    dev=(rr-sign*3*rs).abs()
    use=(cal>=CUT)&rr.notna()&~((dev>0.06)&ok_sox)&~cal.isin(pd.to_datetime(list(bad_extra)))
    use=pd.Series(use,index=cal)
    r=pd.Series(np.where(use,rr,syn),index=cal); r.iloc[0]=0
    if sign>0: o,h,l=[pd.Series(np.where(use,rel(real,c),3*soxrel[c]),index=cal) for c in ("open","high","low")]
    else:
        o=pd.Series(np.where(use,rel(real,"open"),-3*soxrel["open"]),index=cal)
        h=pd.Series(np.where(use,rel(real,"high"),-3*soxrel["low"]),index=cal)
        l=pd.Series(np.where(use,rel(real,"low"),-3*soxrel["high"]),index=cal)
    # 범위가 종가를 포함하도록 보정 (합성 구간의 지수 시가 결함 대비)
    h=np.maximum(h,np.maximum(r,o)); l=np.minimum(l,np.minimum(r,o))
    return r,o,h,l,use
rL,oL,hL,lL,useL=splice(SOXL,+1); rS,oS,hS,lS,useS=splice(SOXS,-1)
CL=(1+rL).cumprod(); CS=(1+rS).cumprod()
# 레벨 배열
def lv(C,o,h,l):
    p=C.shift(1); return p*(1+o),p*(1+h),p*(1+l)
OL,HL,LL=lv(CL,oL,hL,lL); OS,HS,LS=lv(CS,oS,hS,lS)
pos=((rL-lL)/(hL-lL).replace(0,np.nan)).clip(0,1)                 # 종가의 당일 범위 위치
ma200=CL.rolling(200).mean(); bear=(CL<ma200)&ma200.notna()
dd252=sx/sx.rolling(252,min_periods=120).max()-1
vx=VIX.reindex(cal).ffill(); hy=HY.reindex(cal).ffill().shift(1)
qq=QQQ.close.reindex(cal).ffill(); q20=qq/qq.shift(20)-1
HIKE=[("1994-02-04","1995-07-05"),("1999-06-30","2000-12-31"),("2004-06-30","2006-12-31"),("2015-12-16","2019-06-30"),("2022-03-16","2024-01-31"),("2026-09-16","2027-12-31")]
CUTS=[("1995-07-06","1996-06-30"),("1998-09-29","1999-03-31"),("2001-01-03","2003-12-31"),("2007-09-18","2009-06-30"),("2019-07-31","2020-12-31"),("2024-09-18","2026-06-30")]
def win(lst):
    s=pd.Series(False,index=cal)
    for a,b in lst: s[(cal>=a)&(cal<=b)]=True
    return s
hike=win(HIKE); cutw=win(CUTS)
real=pd.Series(cal>=CUT,index=cal)
N=len(cal); I=np.arange(N)
c=CL.values; o=OL.values; h=HL.values; l=LL.values
cs=CS.values; os_=OS.values; hs=HS.values; ls_=LS.values
def st(x,nm="",w=34):
    x=np.sort(np.asarray([v for v in x if v==v],dtype=float))
    if len(x)==0: return f"  {nm:{w}s}   0건"
    ex=x[:-3].mean() if len(x)>3 else np.nan
    return f"  {nm:{w}s} {len(x):4d}건 | 이익 {(x>0).mean()*100:3.0f}% | 중앙 {np.median(x):+6.1f}% | 상위3뺀 {ex:+6.1f}% | 평균 {x.mean():+6.1f}% | 최악 {x.min():+6.1f}%"
def era(i):
    d=cal[i]; return "~2009" if d<CUT else ("2010~18" if d.year<=2018 else "2019~26")
if __name__=="__main__":
    print("달력",cal[0].date(),"~",cal[-1].date(),N,"일")
    print("실제 SOXL 대체일:",[str(d.date()) for d in cal[(cal>=CUT)&~useL.values]])
    print("실제 SOXS 대체일:",[str(d.date()) for d in cal[(cal>=CUT)&~useS.values]])
    j=pd.DataFrame({"l":rL,"s":rS,"x":rs})[cal>=CUT].dropna()
    print("기울기 SOXL/SOX %.3f, SOXS/SOX %.3f"%(np.polyfit(j.x,j.l,1)[0],np.polyfit(j.x,j.s,1)[0]))
    print("마지막:",cal[-1].date(),"SOXL 종가 비율 확인", round(CL.iloc[-1]/CL.iloc[-2]-1,4), "실제", round(SOXL.close.iloc[-1]/SOXL.close.iloc[-2]-1,4))
    print("bear",bool(bear.iloc[-1]),"dd252 %.3f VIX %.2f HY %.2f q20 %.3f hike %s"%(dd252.iloc[-1],vx.iloc[-1],hy.iloc[-1],q20.iloc[-1],hike.iloc[-1]))
