# -*- coding: utf-8 -*-
"""
SOXL 사이클 연구 - 데이터 수집기
GitHub Actions에서 매 거래일 실행. 로컬 실행도 동일하게 작동.

원칙
  1) 기존 행은 절대 덮어쓰지 않는다 (출처 혼입 방지)
  2) 신규 날짜만 추가한다
  3) 검증 통과 전에는 마스터 파일을 교체하지 않는다
  4) 수집 실패 시 이전 값을 복사하지 않는다 (빈 채로 둔다)
"""
import os, sys, json, time, shutil, traceback
from datetime import datetime, timezone, timedelta
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICE  = os.path.join(ROOT, "data", "prices")
MACRO  = os.path.join(ROOT, "data", "macro")
SENT   = os.path.join(ROOT, "data", "sentiment")
LOGS   = os.path.join(ROOT, "logs")
BACKUP = os.path.join(ROOT, ".backup")
for d in (PRICE, MACRO, SENT, LOGS, BACKUP):
    os.makedirs(d, exist_ok=True)

KST   = timezone(timedelta(hours=9))
NOW   = datetime.now(KST)
EVENT = []          # 로그 누적
STATUS = {}         # 상태파일용


def ev(level, target, msg):
    EVENT.append({"ts": NOW.isoformat(), "level": level, "target": target, "message": msg})
    print(f"  [{level}] {target}: {msg}")
    # v1.6 — 경고를 상태파일에 반영한다. 조용한 실패를 없애기 위함.
    if level == "WARN":
        STATUS.setdefault("warned", []).append(f"{target}: {msg[:80]}")


# ══════════════════════════════════════════════════════════════
#  검증
# ══════════════════════════════════════════════════════════════
def validate_ohlc(df, name):
    """반환: (통과여부, 문제목록). 치명적 오류만 False."""
    bad, fatal = [], False
    if df.empty:
        return False, ["빈 데이터프레임"]

    if df["date"].duplicated().any():
        n = int(df["date"].duplicated().sum())
        bad.append(f"날짜 중복 {n}건"); fatal = True

    if not df["date"].is_monotonic_increasing:
        bad.append("날짜 정렬 오류"); fatal = True

    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    if (c <= 0).any():
        bad.append(f"종가 0 이하 {int((c<=0).sum())}건"); fatal = True
    if (h < l).any():
        bad.append(f"고가<저가 {int((h<l).sum())}건"); fatal = True

    # 종가가 고저 범위 밖 (허용오차 0.5% — 제공처 반올림 감안)
    oob = ((c > h * 1.005) | (c < l * 0.995)).sum()
    if oob:
        bad.append(f"종가 범위 이탈 {int(oob)}건")

    if "volume" in df and (df["volume"].fillna(0) < 0).any():
        bad.append("거래량 음수"); fatal = True

    # 분할 의심 — v1.6: 최근 발생분은 별도 표시(소급 재조정 필요 가능성)
    chg = c.pct_change().abs()
    spike = chg[chg > C.MAX_DAILY_MOVE]
    if len(spike):
        dts = [str(d.date()) for d in df.loc[spike.index, "date"]]
        bad.append(f"급변 {len(spike)}건 (분할 소급 미조정 의심): " + ", ".join(dts[:5]))
        recent = [d for d in dts if d >= (NOW - timedelta(days=180)).strftime("%Y-%m-%d")]
        if recent:
            bad.append(f"★ 최근 180일 내 급변 {recent} — 제공처 분할 조정 확인 필요")

    return (not fatal), bad


def missing_trading_days(df, ref_dates):
    """기준 티커에는 있는데 이 티커엔 없는 날짜"""
    if df.empty or ref_dates is None:
        return []
    have = set(df["date"])
    start = df["date"].min()
    return sorted(str(d.date()) for d in ref_dates if d >= start and d not in have)


def compare_overlap(old, new, name):
    """기존/신규가 겹치는 구간의 종가 차이 점검 → 출처 불일치 탐지"""
    if old is None or old.empty or new.empty:
        return
    m = old.merge(new, on="date", suffixes=("_old", "_new"))
    if m.empty:
        return
    m = m.tail(C.OVERLAP_CHECK)
    diff = ((m["close_new"] - m["close_old"]).abs() / m["close_old"])
    worst = float(diff.max())
    if worst > C.OVERLAP_TOL:
        ev("WARN", name, f"출처 불일치 의심 — 겹침 {len(m)}일 중 최대 종가차 {worst:.2%}")
    else:
        ev("INFO", name, f"출처 교차검증 통과 (겹침 {len(m)}일, 최대차 {worst:.3%})")


# ══════════════════════════════════════════════════════════════
#  안전 저장
# ══════════════════════════════════════════════════════════════
def safe_write(df, path, name):
    """검증 통과 시에만 교체. 실패 시 기존 파일 보존."""
    if os.path.exists(path):
        shutil.copy2(path, os.path.join(BACKUP, os.path.basename(path)))
    tmp = path + ".tmp"
    df.to_csv(tmp, index=False, encoding="utf-8")
    os.replace(tmp, path)
    ev("OK", name, f"{len(df)}행 저장  {df['date'].min().date()} ~ {df['date'].max().date()}")


def read_master(path):
    if not os.path.exists(path):
        return None
    d = pd.read_csv(path)
    d["date"] = pd.to_datetime(d["date"])
    return d.sort_values("date").reset_index(drop=True)


# ══════════════════════════════════════════════════════════════
#  제공처
# ══════════════════════════════════════════════════════════════
def fetch_yahoo(sym, start):
    import yfinance as yf
    raw = yf.download(sym, start=start, progress=False,
                      auto_adjust=False, threads=False)
    if raw is None or raw.empty:
        raise ValueError("빈 응답")
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    d = pd.DataFrame({
        "date":      pd.to_datetime(raw.index).tz_localize(None),
        "open":      raw["Open"].values,
        "high":      raw["High"].values,
        "low":       raw["Low"].values,
        "close":     raw["Close"].values,
        "adj_close": raw["Adj Close"].values if "Adj Close" in raw else raw["Close"].values,
        "volume":    raw["Volume"].values if "Volume" in raw else 0,
    })
    d["source"] = "yahoo"
    return d.dropna(subset=["close"]).reset_index(drop=True)


def fetch_stooq(sym, start):
    url = f"https://stooq.com/q/d/l/?s={sym}&d1={start.replace('-','')}&i=d"
    raw = pd.read_csv(url)
    if raw.empty or "Close" not in raw.columns:
        raise ValueError("빈 응답 / 형식 불일치")
    d = pd.DataFrame({
        "date":      pd.to_datetime(raw["Date"]),
        "open":      raw["Open"], "high": raw["High"],
        "low":       raw["Low"],  "close": raw["Close"],
        "adj_close": raw["Close"],
        "volume":    raw.get("Volume", 0),
    })
    d["source"] = "stooq"
    return d.dropna(subset=["close"]).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════
#  주가 수집
# ══════════════════════════════════════════════════════════════
def collect_prices():
    ref_dates = None
    results = {}

    order = [C.CALENDAR_REF] + [k for k in C.PRICES if k != C.CALENDAR_REF]
    for name in order:
        spec = C.PRICES[name]
        path = os.path.join(PRICE, f"{name}.csv")
        old  = read_master(path)
        start = (old["date"].max() - pd.Timedelta(days=45)).strftime("%Y-%m-%d") \
                if old is not None and len(old) else "2009-01-01"

        new, err = None, []
        for label, fn, sym in (("yahoo", fetch_yahoo, spec["yahoo"]),
                               ("stooq", fetch_stooq, spec["stooq"])):
            if not sym:
                continue
            try:
                new = fn(sym, start)
                if len(new) == 0:
                    raise ValueError("0행")
                break
            except Exception as e:
                err.append(f"{label}={type(e).__name__}")
                new = None
                time.sleep(2)

        if new is None:
            ev("FAIL", name, "전 제공처 실패 — " + " / ".join(err) + "  (기존 파일 유지)")
            STATUS.setdefault("failed", []).append(name)
            if old is not None:
                results[name] = old
                if name == C.CALENDAR_REF:
                    ref_dates = list(old["date"])
            continue

        compare_overlap(old, new, name)

        # 기존 행 보존 + 신규 날짜만 추가
        if old is not None and len(old):
            add = new[new["date"] > old["date"].max()]
            merged = pd.concat([old, add], ignore_index=True)
            ev("INFO", name, f"신규 {len(add)}행 추가")
        else:
            merged = new
            ev("INFO", name, f"최초 수집 {len(new)}행")

        merged = (merged.drop_duplicates("date", keep="first")
                        .sort_values("date").reset_index(drop=True))

        # ── v1.6 유령행 차단 ──────────────────────────────────
        # 거래일이 아닌 날짜의 행(휴일에 직전 종가가 채워진 것,
        # 액면분할 미조정가 등)을 상시 제거한다.
        # 2026-08-01 감사에서 34건 발견 — SOXL 연변동성 1,383% 유발.
        if ref_dates is not None and name != C.CALENDAR_REF:
            cal = set(ref_dates)
            cal_start = min(ref_dates)
            before = len(merged)
            ghost = merged[(~merged["date"].isin(cal)) & (merged["date"] >= cal_start)]
            if len(ghost):
                ev("WARN", name, f"유령행 {len(ghost)}건 제거 — "
                   + ", ".join(str(d.date()) for d in ghost["date"][:5]))
                merged = merged[merged["date"].isin(cal) | (merged["date"] < cal_start)]
                merged = merged.reset_index(drop=True)

        okflag, issues = validate_ohlc(merged, name)
        for i in issues:
            ev("WARN", name, i)
        if not okflag:
            ev("FAIL", name, "검증 실패 → 저장 취소, 기존 파일 유지")
            STATUS.setdefault("failed", []).append(name)
            continue

        if name == C.CALENDAR_REF:
            ref_dates = list(merged["date"])
        miss = missing_trading_days(merged, ref_dates)
        if miss:
            ev("WARN", name, f"결측 거래일 {len(miss)}건 (최근: {miss[-3:]})")

        safe_write(merged, path, name)
        results[name] = merged

    return results


# ══════════════════════════════════════════════════════════════
#  FRED
# ══════════════════════════════════════════════════════════════
def collect_fred():
    """
    주의: FRED 그래프 API는 시리즈에 따라 기본 조회창이 잘린다.
    따라서 (1) cosd 로 전 기간을 강제하고 (2) 그래도 짧게 오면
    기존 데이터를 절대 덮어쓰지 않고 신규분만 append 한다.
    """
    out = {}
    for sid in C.FRED:
        path = os.path.join(MACRO, f"{sid}.csv")
        old  = read_master(path)
        try:
            url = (f"https://fred.stlouisfed.org/graph/fredgraph.csv"
                   f"?id={sid}&cosd={C.FRED_START}&coed={NOW:%Y-%m-%d}")
            raw = pd.read_csv(url)
            raw.columns = ["date", "value"]
            raw["date"]  = pd.to_datetime(raw["date"])
            raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
            new = raw.dropna().sort_values("date").reset_index(drop=True)
            new["source"] = "fred"
            if new.empty:
                raise ValueError("전량 결측")

            if old is not None and len(old):
                # 절단 탐지 — 신규가 기존 시작일보다 늦게 시작하면 경고
                if new["date"].min() > old["date"].min():
                    ev("WARN", sid,
                       f"제공처 절단 감지 — 수신 시작일 {new['date'].min().date()} > "
                       f"보유 시작일 {old['date'].min().date()}. 기존 이력 보존하고 신규분만 추가")
                if len(new) < len(old) * C.SHRINK_GUARD:
                    ev("WARN", sid, f"수신 {len(new)}행 < 보유 {len(old)}행 — 덮어쓰기 금지 적용")

                add = new[new["date"] > old["date"].max()]
                merged = pd.concat([old, add], ignore_index=True)
                ev("INFO", sid, f"신규 {len(add)}행 추가")
            else:
                merged = new
                ev("INFO", sid, f"최초 수집 {len(new)}행")

            merged = (merged.drop_duplicates("date", keep="first")
                            .sort_values("date").reset_index(drop=True))

            # 최종 안전장치 — 어떤 경우에도 행수가 줄면 저장하지 않는다
            if old is not None and len(merged) < len(old):
                raise ValueError(f"병합 후 행수 감소 {len(old)}→{len(merged)}")

            safe_write(merged, path, sid)
            out[sid] = merged
        except Exception as e:
            ev("FAIL", sid, f"{type(e).__name__}: {str(e)[:60]} (기존 파일 유지)")
            STATUS.setdefault("failed", []).append(sid)
            if old is not None:
                out[sid] = old
        time.sleep(0.8)
    return out


# ══════════════════════════════════════════════════════════════
#  공포탐욕지수
# ══════════════════════════════════════════════════════════════
def collect_fear_greed():
    import requests
    path = os.path.join(SENT, "fear_greed.csv")
    old  = read_master(path)
    try:
        r = requests.get(C.FEAR_GREED_URL, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json",
        })
        r.raise_for_status()
        js = r.json()

        # 원본 보관 (구조 변경 대비)
        raw_dir = os.path.join(ROOT, "data", "raw", "fear_greed")
        os.makedirs(raw_dir, exist_ok=True)
        with open(os.path.join(raw_dir, f"{NOW:%Y%m%d}.json"), "w") as f:
            json.dump(js, f)

        rec = js["fear_and_greed_historical"]["data"]
        new = pd.DataFrame(rec)
        new["date"] = pd.to_datetime(new["x"], unit="ms").dt.normalize()
        new = new[["date", "y"]].rename(columns={"y": "value"})
        new["value"] = pd.to_numeric(new["value"], errors="coerce").round(2)
        new = new.dropna()

        bad = new[(new["value"] < 0) | (new["value"] > 100)]
        if len(bad):
            raise ValueError(f"범위 이탈 {len(bad)}건")

        new["source"] = "cnn"
        if old is not None and len(old):
            add = new[new["date"] > old["date"].max()]
            merged = pd.concat([old, add], ignore_index=True)
            ev("INFO", "FearGreed", f"신규 {len(add)}행 추가")
        else:
            merged = new

        merged = (merged.drop_duplicates("date", keep="first")
                        .sort_values("date").reset_index(drop=True))
        merged["rating"] = merged["value"].apply(
            lambda v: "Extreme Fear" if v < 25 else "Fear" if v < 45 else
                      "Neutral" if v < 55 else "Greed" if v < 75 else "Extreme Greed")
        safe_write(merged, path, "FearGreed")
        return merged
    except Exception as e:
        ev("FAIL", "FearGreed", f"{type(e).__name__}: {str(e)[:80]} (기존 파일 유지)")
        STATUS.setdefault("failed", []).append("FearGreed")
        return old


# ══════════════════════════════════════════════════════════════
#  상태파일
# ══════════════════════════════════════════════════════════════
def write_status(prices, macro, fg):
    ref = prices.get(C.CALENDAR_REF)
    last_session = str(ref["date"].max().date()) if ref is not None and len(ref) else None

    series = {}
    for k, v in prices.items():
        series[k] = {"last": str(v["date"].max().date()), "rows": len(v),
                     "type": "price"}
    for k, v in macro.items():
        series[k] = {"last": str(v["date"].max().date()), "rows": len(v),
                     "type": "macro"}
    if fg is not None and len(fg):
        series["FEAR_GREED"] = {"last": str(fg["date"].max().date()),
                                "rows": len(fg), "type": "sentiment"}

    failed = STATUS.get("failed", [])
    # 신선도 판정 — 발표 지연이 정상인 시리즈는 제외
    stale = []
    if last_session:
        cut = pd.Timestamp(last_session) - pd.Timedelta(days=C.STALE_DAYS)
        for k, v in series.items():
            if k in C.STALE_EXEMPT:
                continue
            if pd.Timestamp(v["last"]) < cut:
                stale.append(k)

    warned = STATUS.get("warned", [])
    st = {
        "status": ("FAILED" if failed else
                   "WARN"   if warned else      # v1.6 — 경고도 상태로 드러낸다
                   "STALE"  if stale  else "SUCCESS"),
        "warned": warned,
        "updated_at_kst": NOW.strftime("%Y-%m-%d %H:%M:%S"),
        "last_us_session": last_session,
        "failed": failed,
        "stale": stale,
        "series": series,
        "manual_required": {
            "korea_semi_export": "관세청 무역통계 — 월 1회. data/manual/korea_export.csv",
            "finra_margin":      "FINRA 신용융자잔고 — 월 1회. data/manual/finra_margin.csv",
            "etf_flows":         "SOXL/SOXS 자금흐름 — 공개 API 없음",
        },
    }
    with open(os.path.join(ROOT, "data", "status.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)

    pd.DataFrame(EVENT).to_csv(
        os.path.join(LOGS, f"{NOW:%Y%m}.csv"), mode="a", index=False,
        header=not os.path.exists(os.path.join(LOGS, f"{NOW:%Y%m}.csv")),
        encoding="utf-8")
    return st


if __name__ == "__main__":
    print("=" * 64)
    print(f"  SOXL 연구 데이터 수집  {NOW:%Y-%m-%d %H:%M} KST")
    print("=" * 64)
    try:
        print("\n[1/3] 주가·지수")
        p = collect_prices()
        print("\n[2/3] FRED 거시지표")
        m = collect_fred()
        print("\n[3/3] 공포탐욕지수")
        f = collect_fear_greed()
    except Exception:
        traceback.print_exc()
        p, m, f = {}, {}, None
        ev("FATAL", "runner", "예기치 못한 중단")

    st = write_status(p, m, f)
    print("\n" + "=" * 64)
    print(f"  상태: {st['status']}   최종 미국 거래일: {st['last_us_session']}")
    if st["failed"]:
        print(f"  실패: {', '.join(st['failed'])}")
    if st["stale"]:
        print(f"  지연: {', '.join(st['stale'])}")
    print("=" * 64)
    sys.exit(0)   # 일부 실패해도 커밋은 진행 (성공분 보존)
