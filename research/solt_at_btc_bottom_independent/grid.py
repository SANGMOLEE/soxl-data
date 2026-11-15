import numpy as np, pandas as pd, sys
sys.argv=['x']; exec(open('sim.py').read().split("tri=lambda")[0])
const=lambda x:(lambda m: np.full(m,float(x)))
Bs=[64000,62000,60000,57700,55000,53700,51000,48700,46000,40000]
rows=[]
for B in Bs:
    row={'BTC 저점':B}
    for k in [1.0,1.45,1.8]:
        r=simulate(1500,const(B),const(30),fixed=k)
        row[f'k={k} 중앙']=r.SOLT.median()
        if k==1.45: row['SOL(k=1.45)']=r.SOL.median(); row['k=1.45 P10']=r.SOLT.quantile(.1); row['k=1.45 P90']=r.SOLT.quantile(.9)
    for T in [10,60]:
        r=simulate(1500,const(B),const(T),fixed=1.45); row[f'T={T}일 (k=1.45)']=r.SOLT.median()
    rows.append(row)
g=pd.DataFrame(rows)[['BTC 저점','SOL(k=1.45)','k=1.0 중앙','k=1.45 중앙','k=1.8 중앙','k=1.45 P10','k=1.45 P90','T=10일 (k=1.45)','T=60일 (k=1.45)']]
pd.set_option('display.width',250); print(g.round(2).to_string(index=False)); g.round(2).to_csv('output/grid.csv',index=False)
print("SOLT 현재 환산가(월요일, SOL 72.35 유지 시): %.2f"%(SOLT_F*(1+2*(SOL0/SOL_F-1))))
