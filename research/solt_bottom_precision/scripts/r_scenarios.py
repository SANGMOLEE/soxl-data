# R4. BTC가 실현가격 구간에 오면: ETH·SOL 예상가와 SOLT 예상가 (즉시/30일/60일)
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250)
E='data/ext/'
dly={a:m1(a).c.resample('D').last() for a in ['BTC','ETH','SOL']}
w=pd.DataFrame(dly).resample('W-SUN').last()['2025-10-06':]; lw=np.log(w).diff().dropna()
beta={a:np.polyfit(lw.BTC,lw[a],1)[0] for a in ['ETH','SOL']}
dn=lw[lw.BTC<0]; beta_dn={a:np.polyfit(dn.BTC,dn[a],1)[0] for a in ['ETH','SOL']}
# 하락 구간 배율 (이번 약세장의 큰 하락 구간들: 로그 이동비)
legs=[('2025-10-06','2026-02-06'),('2026-05-10','2026-06-30'),('2026-09-21','2026-11-21')]
k={a:[np.log(dly[a][b]/dly[a][a_])/np.log(dly['BTC'][b]/dly['BTC'][a_]) for a_,b in legs] for a in ['ETH','SOL']}
print("이번 약세장 주간 베타:",{a:round(v,2) for a,v in beta.items()},"하락주 베타:",{a:round(v,2) for a,v in beta_dn.items()})
print("큰 하락 구간별 배율:",{a:[round(x,2) for x in v] for a,v in k.items()})
now={a:m1(a).c.iloc[-1] for a in ['BTC','ETH','SOL']}
rb=pd.read_csv(E+'CM_BTC_REALIZED.csv',parse_dates=['date']).set_index('date').realized_price.iloc[-1]
re_=pd.read_csv(E+'CM_ETH_REALIZED.csv',parse_dates=['date']).set_index('date').realized_price.iloc[-1]
lth=float(pd.read_csv(E+'BG_lth-realized-price.csv').lthRealizedPrice.astype(float).iloc[-1])
# SOL 변동성 (최근 60일, 연율)
sv=np.log(m1('SOL').c.resample('D').last()).diff().dropna()[-60:].std()*np.sqrt(365)
P0,S0=24.82,70.62    # SOLT 11/25 정규장 마지막 체결, 그 시각 SOL
def solt_inst(S): return P0*(1+2*(S/S0-1))
fair_now=solt_inst(now['SOL'])
def solt_grad(S,T,c=0.10): return fair_now*(S/now['SOL'])**2*np.exp(-(sv**2+c)*T/365)
print(f"현재 BTC ${now['BTC']:,.0f} ETH ${now['ETH']:,.0f} SOL ${now['SOL']:.2f}; SOLT 이론가 ${fair_now:.2f}; SOL 60일 변동성 {sv:.0%}")
print(f"BTC 실현가격 ${rb:,.0f}, 장기보유자 실현가격 ${lth:,.0f}; ETH 실현가격 ${re_:,.0f}")
targets=[('실현가격 (MVRV 1.0)',rb),('장기보유자 실현가격',lth),('MVRV 0.9',rb*0.9),('MVRV 0.8',rb*0.8),('MVRV 0.76 (2022 바닥 수준)',rb*0.76),('MVRV 0.68 (2018 바닥 수준)',rb*0.68)]
rows=[]
for nm,B in targets:
    r=B/now['BTC']; L=np.log(r)
    eth=[now['ETH']*np.exp(kk*L) for kk in (1.0,1.25,1.5)]
    sol=[now['SOL']*np.exp(kk*L) for kk in (1.0,1.45,1.8)]
    s_mid=sol[1]
    inst=(f"{solt_inst(sol[2]):.1f}~{solt_inst(sol[0]):.1f} (중심 {solt_inst(s_mid):.1f})" if sol[2]/now['SOL']-1>-0.25 else "청산 위험 (하루 -25% 초과)")
    g21=[solt_grad(s,21,0.10) for s in (sol[2],s_mid,sol[0])]
    g60=[solt_grad(s,60,0.10) for s in (sol[2],s_mid,sol[0])]
    sv_save=globals()['sv']; globals()['sv']=0.80
    g60h=[solt_grad(s,60,0.10) for s in (sol[2],s_mid,sol[0])]; globals()['sv']=sv_save
    rows.append(dict(시나리오=nm,BTC=round(B),BTC하락=f"{r-1:+.0%}",ETH=f"{eth[1]:,.0f} ({eth[2]:,.0f}~{eth[0]:,.0f})",ETH_MVRV=f"{eth[1]/re_:.2f}",
                     SOL=f"{s_mid:.1f} ({sol[2]:.1f}~{sol[0]:.1f})",SOLT_즉시=inst,
                     SOLT_3주=f"{g21[1]:.1f} ({g21[0]:.1f}~{g21[2]:.1f})",SOLT_2개월=f"{g60[1]:.1f} ({g60[0]:.1f}~{g60[2]:.1f})",
                     SOLT_2개월_고변동=f"{g60h[1]:.1f} ({g60h[0]:.1f}~{g60h[2]:.1f})"))
T=pd.DataFrame(rows); print(T.to_string(index=False)); T.to_csv('output/r_scenarios.csv',index=False)
# ETH·SOL 자체 기준 (각자의 실현가격/역대 바닥 MVRV)
print("\n== 자산별 자체 기준")
for nm,m in [('MVRV 1.0',1.0),('MVRV 0.53 (ETH 2022 바닥)',0.53),('MVRV 0.40 (ETH 2020 바닥)',0.40)]:
    print(f"  ETH {nm}: ${re_*m:,.0f}")
for nm,R in [('SOL 실현가격 추정 하단',95),('SOL 실현가격 추정 중심',115),('SOL 실현가격 추정 상단',140)]:
    print(f"  {nm} ${R} → 현재 SOL은 그 {now['SOL']/R-1:+.0%}")
