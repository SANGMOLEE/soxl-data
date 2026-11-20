# -*- coding: utf-8 -*-
"""bcps_series.csv 를 트레이딩뷰 Pine(BCPS v1.2)에 내장 문자열로 넣는다. 실행: python research/bcps/make_pine.py → BCPS_v1.2_TradingView.txt"""
import os, re, numpy as np, pandas as pd
R = os.path.dirname(os.path.abspath(__file__))
s = pd.read_csv(os.path.join(R, "bcps_series.csv"), parse_dates=["date"]).set_index("date")
o = pd.read_csv(os.path.join(R, "..", "..", "data", "crypto", "BTC_ONCHAIN.csv"), parse_dates=["date"]).set_index("date").mvrv
idx = pd.date_range("2016-05-15", s.index[-1]); b = s.bcps.reindex(idx); m = o.reindex(idx).ffill()
B = "".join("9999" if np.isnan(v) else f"{int(round(v * 100)):04d}" for v in b)
M = "".join("999" if np.isnan(v) else f"{min(int(round(v * 100)), 998):03d}" for v in m)
pine = open(os.path.join(R, "BCPS_v1.1_TradingView.pine"), encoding="utf-8").read()
pine = re.sub(r'BCPS_STR = "\d+"', f'BCPS_STR = "{B}"', pine); pine = re.sub(r'MVRV_STR = "\d+"', f'MVRV_STR = "{M}"', pine)
pine = pine.replace("BCPS v1.1 — 비트코인 사이클 위치 스코어 (0~100)", "BCPS v1.2 — 비트코인 사이클 위치 스코어 (0~100)")
pine = pine.replace("//  내장 자료 2016-05-15 ~ 2026-08-05. 이후는 표시하지 않는다.",
    f"//  내장 자료 2016-05-15 ~ {idx[-1].date()}.\n//  2026-08-05까지는 v1.1 원본값, 그 뒤는 저장소(soxl-data) 자료로 V·P·M 3요소 재계산값\n//  (내장 구간과 상관 0.984, 저점권 평균오차 2.8). 갱신: research/bcps/bcps_rebuild.py → make_pine.py\n//  저점 2026-06-30 21.6 | {idx[-1].date()} {b.iloc[-1]:.1f} (MVRV {m.iloc[-1]:.2f})")
pine = pine.replace('indicator("BCPS v1.1 비트코인 사이클 위치"', 'indicator("BCPS v1.2 비트코인 사이클 위치"').replace('"내장자료 만료\\n(2026-08-05까지)"', f'"내장자료 만료\\n({idx[-1].date()}까지)"')
open(os.path.join(R, "BCPS_v1.2_TradingView.txt"), "w", encoding="utf-8").write(pine); print("OK", idx[-1].date(), round(b.iloc[-1], 1))
