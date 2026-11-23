from base import *
sxh=SOX.high.reindex(cal).ffill().values; sxl=SOX.low.reindex(cal).ffill().values; sxc=sx.values
rx=rs.values*100; DD=dd252.values; H=hike.values; Cw=cutw.values; V=vx.values
print("=== A6-c. 큰 변곡점인가 다시 빠지나 (원래: SOX +8% 약세장 40건, 직전 저점 재이탈 60일 52% / 120일 72%; 인상기 73% 인하기 44%; 10일째 SOX가 랠리 종가 위→재이탈 50%, 아래→83%; 20일째 47% vs 75%)")
ev=[i for i in range(260,N) if rx[i]>=8 and DD[i-1]<=-0.25]
def rebreak(i,k,use_close=False):
    pl=(sxc[i-20:i].min() if use_close else sxl[i-20:i].min())
    seg=(sxc[i+1:i+1+k] if use_close else sxl[i+1:i+1+k])
    if i+k>=N: return None
    return bool((seg<pl).any())
for uc in (False,True):
    for k in (20,60,120):
        v=[rebreak(i,k,uc) for i in ev]; v=[x for x in v if x is not None]
        print(f"  {'종가' if uc else '저가'} 기준, {k}일 안 직전 20일 저점 재이탈: {np.mean(v)*100:.0f}% ({len(v)}건)")
print("  -- 금리 국면별 (저가, 60일)")
for nm,m in (("인상기",H),("인하기",Cw),("그 외",~(H|Cw))):
    v=[rebreak(i,60) for i in ev if m[i]]; v=[x for x in v if x is not None]
    print(f"    {nm}: {np.mean(v)*100:.0f}% ({len(v)}건)" if v else f"    {nm}: 0건")
print("  -- 인상기 사례 연도:",sorted(set(cal[i].year for i in ev if H[i])))
print("  -- 추적 신호 (저가 기준, 이후 재이탈 = 신호일 이후 120일 안)")
for t in (10,20):
    above=[];below=[]
    for i in ev:
        if i+t+120>=N: continue
        pl=sxl[i-20:i].min()
        if (sxl[i+1:i+t+1]<pl).any(): continue   # 추적일 전에 이미 깨진 사례 제외
        later=bool((sxl[i+t+1:i+t+121]<pl).any())
        (above if sxc[i+t]>sxc[i] else below).append(later)
    print(f"    {t}일째 SOX가 랠리 종가 위: 이후 재이탈 {np.mean(above)*100:.0f}% ({len(above)}건) | 아래: {np.mean(below)*100:.0f}% ({len(below)}건)")
print("  -- VIX별 (60일)")
for a,b in ((0,30),(30,40),(40,50),(50,99)):
    v=[rebreak(i,60) for i in ev if a<=V[i]<b]; v=[x for x in v if x is not None]
    print(f"    VIX {a}~{b}: {np.mean(v)*100:.0f}% ({len(v)}건)" if v else f"    VIX {a}~{b}: 0건")
print("  -- 시대별 (60일)")
for e in ("~2009","2010~18","2019~26"):
    v=[rebreak(i,60) for i in ev if era(i)==e]; v=[x for x in v if x is not None]
    print(f"    {e}: {np.mean(v)*100:.0f}% ({len(v)}건)" if v else f"    {e}: 0건")
print("  -- 성공(60일 재이탈 없음) 사례:",[str(cal[i].date()) for i in ev if rebreak(i,60) is False])
print("  -- 2020년 이후 사례 상세")
for i in ev:
    if cal[i].year>=2020:
        pl=sxl[i-20:i].min(); k=min(60,N-1-i)
        brk=[j for j in range(i+1,min(N,i+121)) if sxl[j]<pl]
        print(f"    {cal[i].date()} SOX {rx[i]:+.1f}% VIX {V[i]:.1f} 금리 {'인상' if H[i] else ('인하' if Cw[i] else '-')} | 직전저점 {pl:.0f} | 재이탈 {'없음(120일)' if not brk else str(cal[brk[0]].date())+f' ({brk[0]-i}일째)'} | 남은 일수 {N-1-i}")
