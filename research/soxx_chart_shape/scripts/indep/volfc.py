from feat import *
d=load()
r2=d.r**2
for w in (5,20,60):
    d[f'rv{w}']=np.sqrt(r2.rolling(w).mean())
for h in (5,20,60):
    d[f'frv{h}']=np.sqrt(r2[::-1].rolling(h).mean()[::-1].shift(-1))  # mean of r^2 over t+1..t+h
X=np.log(d[['rv5','rv20','rv60']]); 
res={}
for h in (5,20,60):
    y=np.log(d[f'frv{h}'])
    m=X.notna().all(1)&y.notna()
    A=np.c_[np.ones(m.sum()),X[m].values]
    b,*_=np.linalg.lstsq(A,y[m].values,rcond=None)
    e=y[m].values-A@b
    xnow=np.r_[1,X.iloc[-1].values]
    fc=np.exp(xnow@b+0.5*e.var())  # approx mean correction for RV level (sqrt of mean r2)
    print(h,'coef',b.round(3),'resid sd',e.std().round(3),'fc vol',np.exp(xnow@b).round(4),'meancorr',fc.round(4))
    # expanding OOS check: fit up to 2015, test after
    tr=m&(d.date<'2016-01-01'); te=m&(d.date>='2016-01-01')
    A1=np.c_[np.ones(tr.sum()),X[tr].values]; b1,*_=np.linalg.lstsq(A1,y[tr].values,rcond=None)
    A2=np.c_[np.ones(te.sum()),X[te].values]
    print('  OOS R2',1-((y[te].values-A2@b1)**2).mean()/((y[te].values-y[te].mean())**2).mean(), 'coef_pre2016',b1.round(3),'fc_pre2016',np.exp(xnow@b1).round(4))
# Empirical: days with rv20 in [5%,7.5%] and rv60 in [3.3,5]%
m=(d.rv20.between(0.05,0.075))&(d.rv60.between(0.033,0.05))
print('similar-vol days',m.sum(), d.loc[m,'date'].dt.year.value_counts().sort_index().to_dict())
print(d.loc[m,['frv5','frv20','frv60']].describe().round(4))
