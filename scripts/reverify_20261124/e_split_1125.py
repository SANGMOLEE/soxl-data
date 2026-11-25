from exits import *
r=rL.values*100; P=pos.values; R=real.values
COST=0.2
gap=oL.values*100
y15=pd.Series(cal.year,index=cal).values>=2015
isD=np.array([i>=2 and r[i]<=-8 and P[i]<0.2 and r[i-1]<0 for i in range(N)])
def oc(i): return (c[i]/o[i]-1)*100-COST
for nm,m in (("2015~",y15),("2010~",R)):
    print("==",nm)
    E=[i for i in range(2,N) if m[i] and r[i-1]<=-12 and gap[i]<=-3]
    print(st([oc(i) for i in E],"E 전체"))
    print(st([oc(i) for i in E if r[i-1]>-15],"E 전일 -12~-15%"))
    print(st([oc(i) for i in E if r[i-1]<=-15],"E 전일 -15%↓"))
    print(st([oc(i) for i in E if r[i-1]<=-20],"E 전일 -20%↓"))
    print(st([oc(i) for i in E if gap[i]<=-10],"E 갭 -10%↓"))
    print(st([oc(i) for i in E if r[i-1]<=-15 and gap[i]<=-10],"E 전일-15%↓ & 갭-10%↓"))
    Ed=[i for i in E if isD[i] and i+1<N]
    print(f"   E일 중 같은날 D(일봉근사) 발생: {len(Ed)}/{len(E)}")
    print(st([oc(i) for i in Ed],"  그날 E만(시가→종가)"))
    print(st([(c[i+1]/c[i]-1)*100-COST for i in Ed],"  그날 D만(종가→다음날 종가)"))
    print(st([(c[i+1]/o[i]-1)*100-COST for i in Ed],"  E→D 연결(시가→다음날 종가)"))
    En=[i for i in E if not isD[i]]
    print(st([oc(i) for i in En],"  D 없는 E일(시가→종가)"))
    if nm=="2015~":
        print("   전일-15%↓ 목록:",[(str(cal[i].date()),round(r[i-1],1),round(gap[i],1),round(oc(i),1),bool(isD[i])) for i in E if r[i-1]<=-15])
