# -*- coding: utf-8 -*-
"""일회성 수집: BTC-USD, SOL-USD, BITU, SOLT 일봉 (연구용, data/crypto/ 에 분리 저장).
collect.py 의 검증 파이프라인과 독립. 기존 파일이 있으면 신규 날짜만 append."""
import os, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from collect import fetch_yahoo, fetch_stooq

TARGETS = {
    "BTCUSD": {"yahoo": "BTC-USD", "stooq": "btcusd", "start": "2014-01-01"},
    "SOLUSD": {"yahoo": "SOL-USD", "stooq": "solusd", "start": "2020-04-01"},
    "BITU":   {"yahoo": "BITU",    "stooq": "bitu.us", "start": "2024-04-01"},
    "SOLT":   {"yahoo": "SOLT",    "stooq": "solt.us", "start": "2025-03-01"},
    "IBIT":   {"yahoo": "IBIT",    "stooq": "ibit.us", "start": "2024-01-01"},
}
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "crypto")
os.makedirs(OUT, exist_ok=True)
ok = {}
for name, spec in TARGETS.items():
    df = None; err = []
    for label, fn, sym in (("yahoo", fetch_yahoo, spec["yahoo"]), ("stooq", fetch_stooq, spec["stooq"])):
        for attempt in range(3):
            try:
                df = fn(sym, spec["start"]); break
            except Exception as e:
                err.append(f"{label}#{attempt+1}: {e}"); time.sleep(3)
        if df is not None and not df.empty: break
    if df is None or df.empty:
        print(f"[FAIL] {name}: {err}"); continue
    path = os.path.join(OUT, f"{name}.csv")
    if os.path.exists(path):
        old = pd.read_csv(path, parse_dates=["date"])
        df = pd.concat([old, df[df["date"] > old["date"].max()]], ignore_index=True)
    df = df.sort_values("date").drop_duplicates("date")
    df.to_csv(path, index=False)
    ok[name] = (len(df), str(df["date"].min().date()), str(df["date"].max().date()))
    print(f"[OK] {name}: {ok[name]}")
if not ok: sys.exit(1)
