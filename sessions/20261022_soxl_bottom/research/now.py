# -*- coding: utf-8 -*-
"""마지막 종가일 기준 현재 판독 — 보고서 2장 표의 원자료"""
import pandas as pd, numpy as np, load
p = load.panel(); s = p["sox"]; t = p.index[-1]
D = "/".join(load.D.split("/"))
w = s.resample("W-FRI").last()
hi60_t = s.iloc[-60:].idxmax()
since = s.loc[hi60_t:]
hi80 = s.iloc[-81:-1].max()
spy = p["spy"]; spy63lo = spy.iloc[-63:].min()
hy = p["hy"].dropna(); hy10 = hy.loc[t - pd.Timedelta(days=3652):]
streak = 0
for v in s.diff().iloc[::-1]:
    if v < 0: streak += 1
    else: break
print(f"기준일 {t.date()}")
rows = [
    ("SOX 종가", f"{s.iat[-1]:,.2f}  (전일 {s.iat[-1]/s.iat[-2]-1:+.2%})"),
    ("SOXL 종가", f"{p['soxl'].iat[-1]:,.2f}  (전일 {p['soxl'].iat[-1]/p['soxl'].iat[-2]-1:+.2%})"),
    ("SOX 스윙고점(60일 최고)", f"{s[hi60_t]:,.2f} ({hi60_t.date()}) → {s.iat[-1]/s[hi60_t]-1:+.1%}"),
    ("스윙고점 이후 SOX 종가 최저", f"{since.min():,.2f} ({since.idxmin().date()}) / 현재가는 그 대비 {s.iat[-1]/since.min()-1:+.1%}"),
    ("SOXL 스윙고점 이후 종가 최저", f"{p['soxl'].loc[hi60_t:].min():,.2f} ({p['soxl'].loc[hi60_t:].idxmin().date()})"),
    ("SOX 80일 고점 대비", f"{s.iat[-1]/hi80-1:+.1%} (80일 고점 {hi80:,.0f})"),
    ("SOX ATH 대비", f"{p['dd_ath'].iat[-1]:+.1%}"),
    ("SOXL ATH 대비", f"{p['soxl'].iat[-1]/p['soxl'].cummax().iat[-1]-1:+.1%}"),
    ("SOX RSI14 일/주", f"{p['rsi'].iat[-1]:.1f} / {load.rsi(w).iat[-1]:.1f}"),
    ("SOX 200일선 / 이격", f"{s.rolling(200).mean().iat[-1]:,.0f} / {p['ma200'].iat[-1]:+.1%}"),
    ("SOX 50일선 / 이격", f"{s.rolling(50).mean().iat[-1]:,.0f} / {p['ma50'].iat[-1]:+.1%}"),
    ("SOX 현재 연속하락일", f"{streak}"),
    ("VIX / 60일 최고", f"{p['vix'].iat[-1]:.2f} / {p['vix60max'].iat[-1]:.2f}"),
    ("공포탐욕 / 20일 최저", f"{p['fg'].iat[-1]:.2f} / {p['fg'].iloc[-20:].min():.2f}"),
    ("HY / 20일 변화 / 10년 백분위", f"{p['hy'].iat[-1]:.2f} / {p['hy_chg20'].iat[-1]:+.2f} / {(hy10 <= hy10.iat[-1]).mean()*100:.0f}"),
    ("NFCI", f"{p['nfci'].iat[-1]:.3f}"),
    ("SPY 60일 고점 대비 / 63일 저점 대비", f"{p['spy_dd60'].iat[-1]:+.1%} / {spy.iat[-1]/spy63lo-1:+.1%} (63일 저점 {spy63lo:,.2f})"),
    ("NVDA 비율(504일)", f"{p['nvda_ratio'].iat[-1]:.2f}"),
]
for k, v in rows:
    print(f"  {k:28s} {v}")
print("\n최근 8일")
pd.set_option("display.width", 250)
print(p.iloc[-8:][["sox", "soxl", "dd60", "rsi", "vix", "hy", "fg", "spy_dd60", "nvda_ratio"]].round(3).to_string())
