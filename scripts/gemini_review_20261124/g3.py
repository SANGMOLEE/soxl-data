import sys; sys.path.insert(0,"/home/claude/rv")
from base import *
s=SOXL[SOXL.index>="2011-01-01"].copy()
C=s.close.values;H=s.high.values;L=s.low.values;n=len(s)
B=bear.reindex(s.index).values
P=(H+L+C)/3; R1=2*P-L; S1=2*P-H
print("=== 3. '매물대·피벗 저항' 검증: 그 가격이 정말 특별한가 (위약 비교)")
print("  방법: 다음 날 고가가 기준선에 닿은 날 중, 종가가 그 아래로 끝난 비율(=막힘). 기준선을 ±1~5% 옮긴 가짜 선과 비교.")
def rej(level_fn,mask,shifts=(-0.05,-0.03,-0.01,0,0.01,0.03,0.05),up=True):
    out=[]
    for k in shifts:
        t=0;rj=0
        for i in range(1,n-1):
            if not mask[i]: continue
            lv=level_fn(i)*(1+k)
            if up:
                if lv<=C[i]: continue
                if H[i+1]>=lv: t+=1; rj+= C[i+1]<lv
            else:
                if lv>=C[i]: continue
                if L[i+1]<=lv: t+=1; rj+= C[i+1]>lv
        out.append(f"{k*100:+.0f}%: {rj/t*100:.0f}% ({t})" if t else f"{k*100:+.0f}%: -")
    return " | ".join(out)
allm=np.ones(n,bool); hv=B.copy()
for nm,m in (("전체 2011~",allm),("하락장",hv)):
    print(f"\n  [{nm}]")
    print("  피벗 R1 저항(닿은 뒤 아래 마감):   ",rej(lambda i:R1[i],m))
    print("  전일 고가 저항:                   ",rej(lambda i:H[i],m))
    print("  피벗 S1 지지(닿은 뒤 위 마감):     ",rej(lambda i:S1[i],m,up=False))
    print("  전일 저가 지지:                   ",rej(lambda i:L[i],m,up=False))
# 직전 급락일 범위 안의 '매물대' : 최근 10일 동안 거래량 가중 가격대(가장 거래가 많았던 가격 구간)
print("\n=== 4. 거래량 매물대: 최근 10거래일에 거래량이 가장 몰린 가격대(일봉 범위에 거래량을 고르게 배분)에 닿은 뒤 막힌 비율 vs 같은 거리의 가짜 선")
V=SOXL.reindex(s.index)
vol=pd.read_csv("/home/claude/soxl-data/data/prices/SOXL.csv",parse_dates=["date"]).set_index("date").volume.reindex(s.index).values
def poc(i):
    lo=L[i-9:i+1].min(); hi=H[i-9:i+1].max(); bins=np.linspace(lo,hi,41); w=np.zeros(40)
    for j in range(i-9,i+1):
        a=np.searchsorted(bins,L[j]); b=np.searchsorted(bins,H[j]); b=max(b,a+1)
        w[max(0,a-1):min(40,b)]+=vol[j]/max(1,(min(40,b)-max(0,a-1)))
    # 현재가 위쪽에서 가장 무거운 구간
    mids=(bins[:-1]+bins[1:])/2; m=mids>C[i]*1.02
    if not m.any(): return np.nan
    return mids[m][np.argmax(w[m])]
lvls=np.array([poc(i) if i>=10 else np.nan for i in range(n)])
for nm,m in (("전체",allm),("하락장",hv)):
    mm=m&~np.isnan(lvls)
    print(f"  [{nm}] 위쪽 최대 매물대 저항: ",rej(lambda i:lvls[i],mm))
