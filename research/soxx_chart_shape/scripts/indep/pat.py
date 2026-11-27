from feat import *
d=pd.read_pickle('d.pkl'); n=len(d)
s=d.sfc.values; sp=d.sfc.shift(1)
for N in (5,10,20):
    d[f'PL{N}']=d.low.shift(1).rolling(N).min()
d['rallyH5']=d.high.shift(1).rolling(5).max()          # max high t-5..t-1
d['maxr4']=d.r.shift(1).rolling(4).max()               # max 1d return t-4..t-1
d['maxr4z']=(d.r/sp).shift(1).rolling(4).max()        # in units of ex-ante sfc
def feats(N):
    PL=d[f'PL{N}']
    uc=d.low<PL
    depth=np.log(PL/d.low)/d.sfc
    recl=d.close>PL
    rallyz=np.log(d.rallyH5/PL)/d.sfc
    return uc,depth,recl,rallyz
uc,depth,recl,rallyz=feats(10)
print(pd.DataFrame({'date':d.date,'uc':uc,'depth':depth,'recl':recl,'rallyz':rallyz,'maxr4z':d.maxr4z,'clv':d.clv,'dd':d.dd,'sfc':d.sfc}).tail(4).to_string())
d.to_pickle('d2.pkl')
