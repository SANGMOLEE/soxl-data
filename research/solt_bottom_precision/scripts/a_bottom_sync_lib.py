import pandas as pd, numpy as np
def zigzag(h, th):
    """시간봉 고가/저가 기반 zigzag. 반환 [(kind, ts, price)]"""
    piv=[]; mode=None; hi=h.h.iloc[0]; hi_t=h.index[0]; lo=h.l.iloc[0]; lo_t=h.index[0]
    for t,(hh,ll) in zip(h.index, h[['h','l']].values):
        if hh>hi: hi,hi_t=hh,t
        if ll<lo: lo,lo_t=ll,t
        if mode!='down' and ll<=hi*(1-th):
            piv.append(('H',hi_t,hi)); mode='down'; lo,lo_t=ll,t
        elif mode!='up' and hh>=lo*(1+th):
            if mode is not None: piv.append(('L',lo_t,lo))
            mode='up'; hi,hi_t=hh,t
    return piv
