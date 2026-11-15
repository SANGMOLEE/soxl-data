# 공통: 자료 로드, 미국 거래일 표본, 2배 일일재조정 합성 NAV
import os, numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')+os.sep
def _px(n): return pd.read_csv(D+n+'.csv',parse_dates=['date']).drop_duplicates('date').set_index('date').sort_index()
btc_y=_px('BTCUSD').close; sol=_px('SOLUSD').close
_s=_px('SOLT'); solt=_s.adj_close; solt_raw=_s.close
cm=pd.read_csv(D+'CM_PRICES.csv',parse_dates=['date']).set_index('date').sort_index()
bst=_px('BTC_BITSTAMP_1D').close
btc=pd.concat([bst[bst.index<btc_y.index[0]],btc_y]).sort_index()   # 2014-09 이전은 Bitstamp
def funding_ann(sym='SOLUSDT'):
    f=pd.read_csv(D+f'FUNDING_{sym}.csv' if sym!='BTC' else D+'FUNDING_BINANCE.csv',parse_dates=['date'])
    f=f.set_index('date').rate.resample('D').sum()*365     # 8h x3 -> 일합 -> 연율
    return f
# 미국 거래일(근사: 평일 - 연방공휴일 + 성금요일 무시)
_hol=USFederalHolidayCalendar().holidays('2010-01-01','2028-12-31')
def us_days(idx):
    idx=pd.DatetimeIndex(idx); return idx[(idx.weekday<5)&(~idx.isin(_hol))]
def sess(series):
    """암호화폐 일봉(00:00 UTC 종가)을 미국 거래일로 표본화"""
    s=series.dropna(); return s.reindex(us_days(s.index)).dropna()
def lev2(p, cost_ann=0.10, L=2.0):
    """p: 거래일 표본 가격. cost_ann: 상수 또는 같은 인덱스의 연율 시리즈. 반환: NAV(시작 1)"""
    r=p.pct_change().fillna(0)
    dt=p.index.to_series().diff().dt.days.fillna(0)
    c=cost_ann if np.isscalar(cost_ann) else cost_ann.reindex(p.index).ffill().fillna(0.10)
    g=(1+L*r).clip(lower=0)*np.exp(-c*dt/365)
    return g.cumprod()
