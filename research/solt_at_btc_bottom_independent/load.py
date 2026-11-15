# 원자료 로더. data/*.csv 는 브랜치 ccr-d4b3886b-gvci67 의 data/crypto/ 원시 일봉(Yahoo)을 그대로 복사한 것.
import os, pandas as pd, numpy as np
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')+os.sep
def px(name):
    return pd.read_csv(D+name+'.csv',parse_dates=['date']).drop_duplicates('date').set_index('date').sort_index()
btc=px('BTCUSD').close; sol=px('SOLUSD').close
s=px('SOLT'); solt=s.adj_close; solt_raw=s.close
