from exits import *
r=rL.values*100; P=pos.values; Lr=lL.values*100; Bm=bear.values
COST=0.2
isD=np.array([i>=2 and r[i]<=-8 and P[i]<0.2 and r[i-1]<0 for i in range(N)])
print("마지막:",cal[-1].date(), "r %.1f low %.1f pos %.2f"%(r[-1],Lr[-1],P[-1]))
for lowth,posth in ((-15,0.8),(-20,0.8),(-15,0.9)):
    idx=[i for i in range(2,N-2) if Lr[i]<=lowth and P[i]>=posth]
    print(f"== 장중 저가 {lowth}%↓ & 종가 위치 {posth}↑ : {len(idx)}일")
    print(st([(c[i+1]/c[i]-1)*100-COST for i in idx],"종가 매수 → 다음 날 종가"))
    print(st([(o[i+1]/c[i]-1)*100 for i in idx],"다음 날 시가 갭"))
    print(st([(c[i+1]/o[i+1]-1)*100-COST for i in idx],"다음 날 시가→종가"))
    print(st([(c[min(N-1,i+5)]/c[i]-1)*100-COST for i in idx],"종가 매수 → 5일 뒤 종가"))
    nd=[i for i in idx if isD[i+1]]
    print(f"   다음 날 D 발생: {len(nd)}/{len(idx)}", [str(cal[i+1].date()) for i in nd])
    print(st([r[i+1] for i in idx],"다음 날 등락(종가)"))
    print(f"   다음 날 -8%↓: {sum(r[i+1]<=-8 for i in idx)}/{len(idx)}")
    if lowth==-20: print("   목록:",[(str(cal[i].date()),round(Lr[i],1),round(r[i],1),round(r[i+1],1)) for i in idx])
