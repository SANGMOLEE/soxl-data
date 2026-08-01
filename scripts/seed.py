# -*- coding: utf-8 -*-
"""
초기 적재 — 기존 investing.com CSV를 마스터 형식으로 변환.
최초 1회만 실행. seed/ 폴더에 기존 파일을 넣고 실행.

  python scripts/seed.py

기존 파일이 investing.com 출처이므로 source='investing' 으로 기록되며,
이후 collect.py 는 이 행들을 절대 덮어쓰지 않는다.
"""
import os, sys, glob
import pandas as pd

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED  = os.path.join(ROOT, "seed")
PRICE = os.path.join(ROOT, "data", "prices")
MACRO = os.path.join(ROOT, "data", "macro")
SENT  = os.path.join(ROOT, "data", "sentiment")
for d in (PRICE, MACRO, SENT):
    os.makedirs(d, exist_ok=True)

# 기존 파일명 조각 → 마스터 이름
MAP = {
    "Philadelphia_Semiconductor": "SOX",
    "SOXL":     "SOXL",
    "SOXX":     "SOXX",
    "SOXS":     "SOXS",
    "NVIDIA":   "NVDA",
    "Micron":   "MU",
}


def num(s):
    return pd.to_numeric(
        s.astype(str).str.replace(",", "", regex=False)
                     .str.replace('"', "", regex=False).str.strip(),
        errors="coerce")


def conv_price(path, name):
    d = pd.read_csv(path)
    d.columns = [c.strip().strip('"').replace("\ufeff", "") for c in d.columns]
    d["date"] = pd.to_datetime(d["Date"], format="%m/%d/%Y", errors="coerce")
    if d["date"].isna().all():
        d["date"] = pd.to_datetime(d["Date"], errors="coerce")

    out = pd.DataFrame({
        "date":  d["date"],
        "open":  num(d["Open"]), "high": num(d["High"]),
        "low":   num(d["Low"]),  "close": num(d["Price"]),
    })
    out["adj_close"] = out["close"]

    v = d.get("Vol.")
    if v is not None:
        def pv(x):
            x = str(x).strip().upper()
            if x in ("-", "", "NAN"):
                return 0
            m = {"K": 1e3, "M": 1e6, "B": 1e9}
            try:
                return float(x[:-1]) * m[x[-1]] if x[-1] in m else float(x)
            except Exception:
                return 0
        out["volume"] = v.apply(pv)
    else:
        out["volume"] = 0

    out["source"] = "investing"
    out = (out.dropna(subset=["date", "close"])
              .drop_duplicates("date", keep="last")
              .sort_values("date").reset_index(drop=True))
    dst = os.path.join(PRICE, f"{name}.csv")

    # SOX 처럼 기간별로 2개 파일이면 병합
    if os.path.exists(dst):
        old = pd.read_csv(dst); old["date"] = pd.to_datetime(old["date"])
        out = (pd.concat([old, out], ignore_index=True)
                 .drop_duplicates("date", keep="last")
                 .sort_values("date").reset_index(drop=True))
    out.to_csv(dst, index=False, encoding="utf-8")
    print(f"  [가격] {name:<6} {len(out):>6}행  {out.date.min().date()} ~ {out.date.max().date()}")


def conv_fred(path):
    d = pd.read_csv(path)
    d.columns = [c.replace("\ufeff", "").strip() for c in d.columns]
    dc = d.columns[0]
    vc = d.columns[1]
    out = pd.DataFrame({"date": pd.to_datetime(d[dc], errors="coerce"),
                        "value": pd.to_numeric(d[vc], errors="coerce")})
    out = out.dropna().sort_values("date").reset_index(drop=True)
    out["source"] = "fred"
    out.to_csv(os.path.join(MACRO, f"{vc}.csv"), index=False, encoding="utf-8")
    print(f"  [거시] {vc:<14} {len(out):>6}행  {out.date.min().date()} ~ {out.date.max().date()}")


def conv_fg(path):
    d = pd.read_csv(path)
    d.columns = [c.replace("\ufeff", "").strip() for c in d.columns]
    out = pd.DataFrame({"date": pd.to_datetime(d["Date"], errors="coerce"),
                        "value": pd.to_numeric(d["Fear_Greed_Index"], errors="coerce")})
    out = out.dropna().drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
    out["source"] = "cnn_master"
    out["rating"] = out["value"].apply(
        lambda v: "Extreme Fear" if v < 25 else "Fear" if v < 45 else
                  "Neutral" if v < 55 else "Greed" if v < 75 else "Extreme Greed")
    out.to_csv(os.path.join(SENT, "fear_greed.csv"), index=False, encoding="utf-8")
    print(f"  [심리] FearGreed     {len(out):>6}행  {out.date.min().date()} ~ {out.date.max().date()}")


if __name__ == "__main__":
    files = glob.glob(os.path.join(SEED, "*.csv"))
    if not files:
        print(f"seed/ 폴더가 비어 있습니다. 기존 CSV를 넣고 다시 실행하십시오.\n  경로: {SEED}")
        sys.exit(1)

    print(f"초기 적재 시작 — {len(files)}개 파일\n")
    for f in sorted(files):
        base = os.path.basename(f)
        try:
            if "Fear_Greed" in base:
                conv_fg(f); continue
            hit = next((v for k, v in MAP.items() if k in base), None)
            if hit:
                conv_price(f, hit); continue
            head = pd.read_csv(f, nrows=1)
            cols = [c.replace("\ufeff", "").strip() for c in head.columns]
            if len(cols) == 2 and ("date" in cols[0].lower() or "DATE" in cols[0]):
                conv_fred(f); continue
            print(f"  [건너뜀] {base} — 형식 미인식")
        except Exception as e:
            print(f"  [오류] {base} — {type(e).__name__}: {e}")

    print("\n완료. 이제 scripts/collect.py 를 실행하면 신규분만 누적됩니다.")
