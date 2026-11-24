import sys; sys.path.insert(0,"/home/claude/rv")
from base import *
s=SOXL[SOXL.index>="2010-06-01"].copy()
C=s.close.values;O=s.open.values;H=s.high.values;L=s.low.values;D=s.index;n=len(s)
r=np.r_[np.nan,C[1:]/C[:-1]-1]*100
def S(x,nm,w=40): return st(x,nm,w)
print("=== 1. 제미나이 '+20% 폭등 11건 다음 날 하락 72.7%, 중앙 -1.43%, 평균 -5.70% / +27% 5건 80%, 중앙 -4.0%, 평균 -11.8%'")
for th in (20,27):
    ev=[i for i in range(1,n-1) if r[i]>=th]
    nx=[(C[i+1]/C[i]-1)*100 for i in ev]
    print(f"  +{th}%↑ {len(ev)}건: 다음 날 하락 {np.mean(np.array(nx)<0)*100:.1f}% 중앙 {np.median(nx):+.2f}% 평균 {np.mean(nx):+.2f}%")
    print("   ",[(str(D[i].date()),round(r[i],1),round(v,1)) for i,v in zip(ev,nx)])
print("\n=== 2. 내일 시나리오 확률 대조 (11/23 종가 43.21 기준 비율로 환산)")
c0=43.21
lv=lambda p:p/c0-1
def scen(ev,title):
    cnt={k:0 for k in "12345x"}; rows=[]
    for i in ev:
        j=i+1; o=O[j]/C[i]-1; hh=H[j]/C[i]-1; ll=L[j]/C[i]-1; cc=C[j]/C[i]-1
        if cc<=-0.15: k="5"
        elif cc>=lv(48.5): k="3"
        elif o<=lv(42.5): k="2"
        elif hh>=lv(44.8) and cc<=lv(41.8): k="1"
        elif hh<=lv(44.5) and ll>=lv(42.5): k="4"
        else: k="x"
        cnt[k]+=1
    N_=len(ev); print(f"  [{title}] {N_}건: ①반짝후 눌림 {cnt['1']/N_*100:.0f}% ②하락 출발 {cnt['2']/N_*100:.0f}% ③48.5↑ 마감 {cnt['3']/N_*100:.0f}% ④42.5~44.5 박스 {cnt['4']/N_*100:.0f}% ⑤-15%↓ {cnt['5']/N_*100:.0f}% 기타 {cnt['x']/N_*100:.0f}%")
for th in (15,20):
    scen([i for i in range(1,n-1) if r[i]>=th],f"실제 SOXL +{th}%↑ 다음 날")
scen([i for i in range(1,n-1) if r[i]>=15 and bear.reindex(D).values[i]],"실제 SOXL +15%↑ & 하락장")
print("  제미나이 제시: ① 40% ② 25% ③ 15% ④ 10% ⑤ 10%")
print("  (기준선: ① 고가 44.80↑ & 종가 41.80↓ / ② 시가 42.50↓ / ③ 종가 48.50↑ / ④ 고가 44.50↓ & 저가 42.50↑ / ⑤ 종가 -15%↓)")
