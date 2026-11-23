from base import *
r=rL.values*100; V=vx.values; DD=dd252.values; Bm=bear.values
print("=== A6-b. 지금 국면 반등의 모양 (원래 64건: 고점 중앙 6일째, 6~10일 55%, 고점 중앙 +33%, 고점 뒤 -29% 되밀림, 10일 종가 중앙 +7%)")
def shape(idx,title):
    pk_day=[];pk=[];ret_after=[];c10=[];early=[];late=[]
    for i in idx:
        hh=h[i+1:i+11]; j=int(np.argmax(hh)); pk_day.append(j+1); pv=hh[j]; pk.append((pv/c[i]-1)*100)
        after=l[i+1+j:i+11]; ret_after.append((after.min()/pv-1)*100 if len(after) else np.nan)
        c10.append((c[i+10]/c[i]-1)*100)
        (early if j+1<=2 else late).append((pv/c[i]-1)*100)
    pk_day=np.array(pk_day)
    print(f"\n[{title}] {len(idx)}건")
    print(f"  고점 날짜 중앙 {np.median(pk_day):.0f}일째 | 1~2일 {np.mean(pk_day<=2)*100:.0f}% | 3~5일 {np.mean((pk_day>=3)&(pk_day<=5))*100:.0f}% | 6~10일 {np.mean(pk_day>=6)*100:.0f}%")
    print(st(pk,"10일 안 최고(고가)")); print(st(ret_after,"고점 뒤 10일 창 안 최저(고점 대비)")); print(st(c10,"10일째 종가"))
    print(st(early,"고점이 1~2일째인 경우 크기")); print(st(late,"고점이 3일째 이후인 경우 크기"))
    # 제미나이 주장: 5일 고점이 1~2일째인 비율
    p5=[int(np.argmax(h[i+1:i+6]))+1 for i in idx]; print(f"  5일 창 고점이 1~2일째: {np.mean(np.array(p5)<=2)*100:.0f}%")
for th in (-15,-12,-20):
    idx=[i for i in range(260,N-11) if r[i]<=th and Bm[i] and V[i]>=30 and DD[i]<=-0.25]
    shape(idx,f"SOXL 하루 {th}%↓ & 하락장 & VIX≥30 & SOX -25%↓")
