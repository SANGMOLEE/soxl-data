import sys; sys.path.insert(0,"/home/claude/rv")
from base import *
s=SOXL[SOXL.index>="2010-06-01"].copy()
C=s.close.values;O=s.open.values;H=s.high.values;L=s.low.values;D=s.index;n=len(s)
r=np.r_[np.nan,C[1:]/C[:-1]-1]*100
c0=43.21; f=lambda p:p/c0          # 11/23 종가 대비 배수
def grid(ev,title):
    print(f"\n[{title}] {len(ev)}건 — 다음 날 모습 (11/23 기준 가격으로 환산)")
    rows=[]
    for i in ev:
        j=i+1; rows.append(dict(o=O[j]/C[i]*c0,h=H[j]/C[i]*c0,l=L[j]/C[i]*c0,c=C[j]/C[i]*c0))
    df=pd.DataFrame(rows)
    hit=df.h>=44.80
    for nm,m in (("고가 44.80 도달",hit),("고가 44.80 미달",~hit)):
        sub=df[m]
        b=pd.cut(sub.c,[0,36.73,41.8,43.21,44.8,48.5,999],labels=["≤36.7(-15%)","36.7~41.8","41.8~43.21","43.21~44.8","44.8~48.5","48.5↑"])
        print(f"  {nm}: {m.sum()}건 | 종가 분포 "+", ".join(f"{k} {v}" for k,v in b.value_counts().sort_index().items()))
    print(f"  시가 중앙 {df.o.median():.2f} | 고가 중앙 {df.h.median():.2f} | 저가 중앙 {df.l.median():.2f} | 종가 중앙 {df.c.median():.2f}")
    print(f"  저가 40.68 이하 {np.mean(df.l<=40.68)*100:.0f}% | 저가 38.00 이하 {np.mean(df.l<=38.0)*100:.0f}% | 고가 46.50 이상 {np.mean(df.h>=46.5)*100:.0f}%")
    return df
E15=[i for i in range(1,n-1) if r[i]>=15]; E20=[i for i in range(1,n-1) if r[i]>=20]
d15=grid(E15,"실제 SOXL +15%↑"); d20=grid(E20,"실제 SOXL +20%↑")

print("\n=== 숏 타점 A 근사 (일봉: 진입 45.00, 손절 46.50, 익절 절반 42.00·절반 40.85, 미달 시 종가 청산, 비용 0.3%)")
def shortA(df,pess=True):
    out=[]
    for _,x in df.iterrows():
        E=45.0; Sp=46.5; T1=42.0; T2=40.85
        if x.o>=Sp or x.h<E: continue            # 시작부터 손절선 위(돌파 안착) 또는 진입대 미도달 → 매매 없음
        e=max(x.o,E)
        stop_hit=x.h>=Sp; t1=x.l<=T1; t2=x.l<=T2
        if pess and stop_hit: out.append((e/Sp-1)*100-0.3); continue
        if (not pess) and stop_hit and not t1: out.append((e/Sp-1)*100-0.3); continue
        a=(e/T1-1) if t1 else (e/x.c-1); b=(e/T2-1) if t2 else (e/x.c-1)
        out.append((a+b)/2*100-0.3)
    return out
for nm,df in (("+15%↑",d15),("+20%↑",d20)):
    print(st(shortA(df,True),f"{nm} 비관(손절 먼저)")); print(st(shortA(df,False),f"{nm} 낙관(익절 먼저)"))
    print(f"   진입 기회 {sum(1 for _,x in df.iterrows() if not (x.o>=46.5 or x.h<45.0))}건 / {len(df)}일")
print("\n=== 롱 타점 A 근사 (진입 40.68, 손절 38.00, 익절 43.00, 미달 시 종가, 비용 0.2%)")
def longA(df,pess=True):
    out=[]
    for _,x in df.iterrows():
        E=40.68; Sp=38.0; T=43.0
        if x.l>E: continue
        e=min(x.o,E)
        if x.l<=Sp and (pess or x.h<T): out.append((Sp/e-1)*100-0.2); continue
        if (x.c>=T and pess) or (x.h>=T and not pess): out.append((T/e-1)*100-0.2); continue
        out.append((x.c/e-1)*100-0.2)
    return out
for nm,df in (("+15%↑",d15),("+20%↑",d20)):
    print(st(longA(df,True),f"{nm} 비관")); print(st(longA(df,False),f"{nm} 낙관"))
