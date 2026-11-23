from exits import *
r=rL.values*100; P=pos.values; V=vx.values; Bm=bear.values; R=real.values
COST=0.2
isD=np.array([i>=2 and r[i]<=-8 and P[i]<0.2 and r[i-1]<0 for i in range(N)])
Didx=[i for i in range(2,N) if isD[i]]
gap=oL.values*100
print("=== B2. E 규칙 (전일 -12%↓ & 시가 갭 -3%↓) — 일봉으로는 시가→종가로 근사 (원래 30분봉 2022~26: 10:30 ET 진입, 17건 승률 71% 중앙 +4.0%)")
y15=pd.Series(cal.year,index=cal).values>=2015
for nm,m in (("2015~ (시가 신뢰 구간)",y15),("2010~",R)):
    idx=[i for i in range(2,N) if m[i] and r[i-1]<=-12 and gap[i]<=-3]
    print(st([(c[i]/o[i]-1)*100-COST for i in idx],"E "+nm))
for g in (0,-3,-5,-8):
    for p in (-10,-12,-15):
        idx=[i for i in range(2,N) if y15[i] and r[i-1]<=p and gap[i]<=g]
        x=np.array([(c[i]/o[i]-1)*100-COST for i in idx]); 
        if len(x): print(f"   전일≤{p}% 갭≤{g}%: {len(x)}건 이익 {(x>0).mean()*100:.0f}% 중앙 {np.median(x):+.1f}% 평균 {x.mean():+.1f}% 최악 {x.min():+.1f}%")
idx=[i for i in range(2,N) if y15[i] and r[i-1]<=-12 and gap[i]>-3]; print(st([(c[i]/o[i]-1)*100-COST for i in idx],"대조: 갭 -3% 초과(얕은 갭·갭업)"))
idx=[i for i in range(2,N) if y15[i] and r[i-1]<=-12 and gap[i]<=-3]
print("   E 목록(2015~):",[(str(cal[i].date()),round(gap[i],1),round((c[i]/o[i]-1)*100,1)) for i in idx])
print("   10/31 이후:",[(str(cal[i].date()),round(gap[i],1),round((c[i]/o[i]-1)*100,1)) for i in idx if cal[i]>=pd.Timestamp('2026-10-31')])

print("\n=== B3. 반등 뒤 숏 (원래: 필터 통과 15건 승률 80% 평균 +3.9% 최악 -15.2% / 필터 없음 55건 51% -1.1%)")
def soxs_trade(j,tp=0.10,sl=0.15,W=5):
    e=cs[j]; T=e*(1+tp); S=e*(1-sl)
    for k in range(j+1,min(N,j+W+1)):
        if os_[k]<=S: return (os_[k]/e-1)*100
        if os_[k]>=T: return (os_[k]/e-1)*100
        if ls_[k]<=S: return -sl*100          # 같은 날 둘 다 닿으면 손절 우선
        if hs[k]>=T: return tp*100
    k=min(N-1,j+W); return (cs[k]/e-1)*100
def reb_short(filt,start=None):
    out=[];used=set()
    for i in Didx:
        if start is not None and cal[i]<start: continue
        for d in range(2,8):
            j=i+d
            if j>=N-1: break
            if c[j]>=c[i]*1.10:
                if j in used: break
                if filt and not (Bm[j] and V[j]<30): break
                used.add(j); out.append((j,soxs_trade(j)-COST)); break
    return out
for filt in (True,False):
    for nm,start in (("1994~",None),("2010~",pd.Timestamp("2010-06-01"))):
        x=reb_short(filt,start); print(st([v for _,v in x],("필터 통과 " if filt else "필터 없음 ")+nm))
x=reb_short(True); print("   필터 통과 목록:",[(str(cal[j].date()),round(v,1)) for j,v in x])
for e in ("~2009","2010~18","2019~26"):
    print(st([v for j,v in reb_short(True) if era(j)==e],"   필터 통과 "+e))
print("-- 주변값 (필터 통과, 1994~)")
for tp,sl in ((0.10,0.15),(0.08,0.15),(0.15,0.15),(0.10,0.10),(0.10,0.20)):
    out=[];used=set()
    for i in Didx:
        for d in range(2,8):
            j=i+d
            if j>=N-1: break
            if c[j]>=c[i]*1.10:
                if Bm[j] and V[j]<30 and j not in used: used.add(j); out.append(soxs_trade(j,tp,sl)-COST)
                break
    print(st(out,f"   익절 +{int(tp*100)}% 손절 -{int(sl*100)}%"))
for lvl in (1.05,1.15,1.20):
    out=[]
    for i in Didx:
        for d in range(2,8):
            j=i+d
            if j>=N-1: break
            if c[j]>=c[i]*lvl:
                if Bm[j] and V[j]<30: out.append(soxs_trade(j)-COST)
                break
    print(st(out,f"   반등 기준 +{int((lvl-1)*100)}%"))
for vth in (25,35,99):
    out=[]
    for i in Didx:
        for d in range(2,8):
            j=i+d
            if j>=N-1: break
            if c[j]>=c[i]*1.10:
                if Bm[j] and V[j]<vth: out.append(soxs_trade(j)-COST)
                break
    print(st(out,f"   VIX<{vth} (하락장)"))

print("\n=== B4. 급락 직후 SOXS (원래: 5일 뒤 17건 중 15건 손실, 중앙 -14.8%)")
for nm,idx in (("D 신호일 종가 SOXS → 5일",Didx),("SOXL -15%↓ 날 종가 SOXS → 5일",[i for i in range(2,N) if r[i]<=-15])):
    print(st([(cs[i+5]/cs[i]-1)*100-COST for i in idx if i+5<N],nm))
    print(st([(cs[i+5]/cs[i]-1)*100-COST for i in idx if i+5<N and cal[i]>=pd.Timestamp("2022-01-01")],"   2022~"))
print("\n=== B5. 선이 깨진 걸 보고 숏 (원래: 승률 10~32%)")
sxc=sx.values
brk=[i for i in range(61,N-5) if sxc[i]<sxc[i-60:i].min()]
first=[i for i in brk if not any(sxc[k]<sxc[k-60:k].min() for k in range(max(61,i-5),i))]
print(st([(cs[i+5]/cs[i]-1)*100-COST for i in first],"SOX 60일 최저 종가 이탈 첫날 → SOXS 5일"))
print(st([soxs_trade(i)-COST for i in first],"   같은 날, +10%/-15%/5일 청산"))
o1=[];o2=[]
for i in Didx:
    for j in range(i+1,min(N-5,i+11)):
        if c[j]<l[i]: o1.append((cs[j+5]/cs[j]-1)*100-COST); break
    for j in range(i+1,min(N-5,i+11)):
        if c[j]<c[i]: o2.append((cs[j+5]/cs[j]-1)*100-COST); break
print(st(o1,"D 신호일 저가를 종가로 깬 날 → SOXS 5일")); print(st(o2,"D 신호일 종가를 종가로 깬 날 → SOXS 5일"))
