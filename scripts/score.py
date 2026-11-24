#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
예측 원장 자동 채점기 (표준 라이브러리만 사용)

  python scripts/score.py            원장 전체 재채점 → ledger/scoreboard.md, ledger/status.json 갱신
  python scripts/score.py add ...    새 예측 1건 등록   (python scripts/score.py add -h)
  python scripts/score.py check      원장 형식만 검사 (채점 안 함)

원칙
  1. 자동 판정 건은 실행할 때마다 처음부터 다시 계산한다.
     추정 가격(ledger/manual_prices.csv)으로 판정된 건도, 공식 가격이 들어오면 저절로 다시 판정된다.
  2. prob = "예측 문장이 참일 확률".
     0.5 초과면 '참'에, 0.5 미만이면 '거짓'에 건 것으로 보고 맞음/틀림을 매긴다.
     정확히 0.5는 동전으로 보아 적중 집계에서 빼고 Brier 점수만 계산한다.
  3. source=retro (과거 수기 채점) 건은 score(1 / 0.5 / 0)를 그대로 쓴다.
"""
import csv
import re, json, os, sys, argparse, datetime as dt
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "ledger", "predictions.csv")
MANUAL = os.path.join(ROOT, "ledger", "manual_prices.csv")
BOARD = os.path.join(ROOT, "ledger", "scoreboard.md")
STATUS = os.path.join(ROOT, "ledger", "status.json")
PRICES = os.path.join(ROOT, "data", "prices")
MACRO = os.path.join(ROOT, "data", "macro")

FIELDS = ["id", "made_kst", "room", "ticker", "cat", "statement", "check", "level", "level2", "level_pct",
          "ref_date", "horizon_td", "end_date", "prob", "basis", "invalidation", "source",
          "outcome", "score", "brier", "resolved_on", "est", "note"]
CATS = {"A": "위험 회피", "B": "큰 방향·국면", "C": "가격 목표·시점", "D": "숏 관련", "E": "규칙 판정·연구", "F": "이벤트·장중 구조"}
CHECKS = {
    "touch_high": "기간 안 장중 고가가 level 이상",
    "touch_low": "기간 안 장중 저가가 level 이하",
    "close_ge": "기간 마지막 날 종가가 level 이상",
    "close_le": "기간 마지막 날 종가가 level 이하",
    "first_up": "level(장중 고가) 도달이 level2(종가 이하) 이탈보다 먼저",
    "first_dn": "level2(종가 이하) 이탈이 level(장중 고가) 도달보다 먼저",
    "manual": "사람이 outcome(1/0)을 직접 기입",
}
# 미국 휴장일 (마감일 '예상' 표시에만 사용, 판정은 실제 데이터의 거래일로 함)
US_HOLIDAYS = {"2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26",
               "2027-05-31", "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}
KST = dt.timezone(dt.timedelta(hours=9))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- 가격
_cache = {}


def load_series(ticker):
    """{date: dict(o,h,l,c,est)} — 공식 데이터 우선, 없는 날만 manual_prices로 보충"""
    t = ticker.upper()
    if t in _cache:
        return _cache[t]
    s = {}
    if t in ("VIX", "VIXCLS"):
        p = os.path.join(MACRO, "VIXCLS.csv")
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                v = fnum(r.get("value"))
                if v is not None:
                    s[r["date"]] = dict(o=v, h=v, l=v, c=v, est=False)
    else:
        p = os.path.join(PRICES, f"{t}.csv")
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                c = fnum(r.get("close"))
                if c is None:
                    continue
                o, h, l = fnum(r.get("open")) or c, fnum(r.get("high")) or c, fnum(r.get("low")) or c
                s[r["date"]] = dict(o=o, h=h, l=l, c=c, est=False)
    if os.path.exists(MANUAL):
        for r in csv.DictReader(open(MANUAL, encoding="utf-8")):
            if r["ticker"].upper() != t or r["date"] in s:
                continue
            c = fnum(r.get("close"))
            if c is None:
                continue
            s[r["date"]] = dict(o=fnum(r.get("open")) or c, h=fnum(r.get("high")) or c,
                                l=fnum(r.get("low")) or c, c=c, est=True)
    _cache[t] = dict(sorted(s.items()))
    return _cache[t]


def resolve_level(tok, pct, ref):
    """level 칸: 숫자 또는 ref_close / ref_high / ref_low. level_pct가 있으면 기준값에 곱한다."""
    tok = (tok or "").strip()
    p = fnum(pct)
    if tok == "":
        return ref["c"] * (1 + p) if p is not None else None
    if tok in ("ref_close", "ref_high", "ref_low"):
        base = ref[{"ref_close": "c", "ref_high": "h", "ref_low": "l"}[tok]]
        return base * (1 + p) if p is not None else base
    return fnum(tok)


def window(row, s):
    """(ref_bar, [(date,bar)...], complete, last_date) 또는 오류 문자열"""
    ref_d = row["ref_date"]
    if ref_d not in s:
        return f"기준일 {ref_d} 가격 없음"
    after = [(d, b) for d, b in s.items() if d > ref_d]
    last = next(reversed(s)) if s else ""
    h = row.get("horizon_td", "").strip()
    e = row.get("end_date", "").strip()
    if h:
        n = int(float(h))
        win = after[:n]
        return s[ref_d], win, len(win) >= n, last
    if e:
        win = [(d, b) for d, b in after if d <= e]
        return s[ref_d], win, last >= e, last
    return "horizon_td 또는 end_date 필요"


def evaluate(row):
    """(outcome 1/0, 판정일, 추정가격사용) / None(진행중) / 오류 문자열"""
    s = load_series(row["ticker"])
    w = window(row, s)
    if isinstance(w, str):
        return w
    ref, win, complete, _ = w
    est = ref["est"] or any(b["est"] for _, b in win)
    lv = resolve_level(row.get("level"), row.get("level_pct"), ref)
    ck = row["check"]
    if ck in ("touch_high", "touch_low"):
        for d, b in win:
            if (ck == "touch_high" and b["h"] >= lv) or (ck == "touch_low" and b["l"] <= lv):
                return 1, d, est
        return (0, win[-1][0] if win else row["ref_date"], est) if complete else None
    if ck in ("close_ge", "close_le"):
        if not complete or not win:
            return None
        d, b = win[-1]
        ok = b["c"] >= lv if ck == "close_ge" else b["c"] <= lv
        return int(ok), d, est
    if ck in ("first_up", "first_dn"):
        dn = resolve_level(row.get("level2"), None, ref)
        for d, b in win:
            winner = "up" if b["h"] >= lv else ("dn" if b["c"] <= dn else None)  # 같은 날이면 장중 고가가 종가보다 먼저
            if winner:
                return int((winner == "up") == (ck == "first_up")), d, est
        return (0, win[-1][0] if win else row["ref_date"], est) if complete else None
    return f"알 수 없는 check: {ck}"


def score_row(row):
    src = row.get("source", "live")
    if src == "retro":                     # 과거 수기 채점: score를 그대로 둔다
        p, o = fnum(row.get("prob")), fnum(row.get("outcome"))
        row["brier"] = f"{(p - o) ** 2:.4f}" if p is not None and o is not None else ""
        return
    p = fnum(row.get("prob"))
    if row["check"] == "manual":
        o = fnum(row.get("outcome"))
        res = (int(o), row.get("resolved_on", ""), row.get("est") == "1") if o is not None else None
    else:
        res = evaluate(row)
    base_note = re.sub(r"(^| \| )오류: .*$", "", row.get("note", "")).strip(" |")
    if isinstance(res, str):
        row["note"] = (base_note + " | 오류: " + res).strip(" |")
        res = None
    else:
        row["note"] = base_note  # 가격이 들어와 판정되면 이전 오류 문구 제거
    if res is None:
        for k in ("outcome", "score", "brier", "resolved_on", "est"):
            if not (row["check"] == "manual" and k in ("outcome", "resolved_on")):
                row[k] = ""
        return
    o, d, est = res
    row["outcome"], row["resolved_on"], row["est"] = str(o), d, "1" if est else ""
    if p is None:
        row["score"], row["brier"] = "", ""
        return
    row["brier"] = f"{(p - o) ** 2:.4f}"
    row["score"] = "" if abs(p - 0.5) < 1e-9 else str(int((p > 0.5) == (o == 1)))


# ---------------------------------------------------------------- 원장 입출력
def read_ledger():
    if not os.path.exists(LEDGER):
        return []
    return [dict({k: "" for k in FIELDS}, **{k: (v or "") for k, v in r.items() if k in FIELDS})
            for r in csv.DictReader(open(LEDGER, encoding="utf-8"))]


def write_ledger(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def validate(rows):
    errs, seen = [], set()
    for r in rows:
        i = r["id"]
        if not i or i in seen:
            errs.append(f"id 비었거나 중복: {i!r}")
        seen.add(i)
        if r["cat"] not in CATS:
            errs.append(f"{i}: cat은 A~F")
        if r.get("source") != "retro":
            if r["check"] not in CHECKS:
                errs.append(f"{i}: check 값 오류 {r['check']!r}")
            if r["check"] != "manual" and not (r["horizon_td"] or r["end_date"]):
                errs.append(f"{i}: horizon_td 또는 end_date 필요")
            p = fnum(r["prob"])
            if p is None or not 0 <= p <= 1:
                errs.append(f"{i}: prob는 0~1")
    return errs


# ---------------------------------------------------------------- 마감일 예상
def add_trading_days(start, n):
    d = dt.date.fromisoformat(start)
    while n > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d.isoformat() not in US_HOLIDAYS:
            n -= 1
    return d.isoformat()


def deadline(row):
    if row.get("end_date"):
        return row["end_date"]
    h = row.get("horizon_td", "")
    if not h:
        return ""
    s = load_series(row["ticker"])
    after = [d for d in s if d > row["ref_date"]]
    n = int(float(h))
    if len(after) >= n:
        return after[n - 1]
    base = after[-1] if after else row["ref_date"]
    return "약 " + add_trading_days(base, n - len(after))


def status_now(row):
    """진행중 건의 현재 상태 한 줄"""
    s = load_series(row["ticker"])
    w = window(row, s)
    if isinstance(w, str):
        return w
    ref, win, _, last = w
    lv = resolve_level(row.get("level"), row.get("level_pct"), ref)
    cur = s[last]
    tag = "(추정)" if cur["est"] else ""
    if row["check"] in ("first_up", "first_dn"):
        dn = resolve_level(row.get("level2"), None, ref)
        return f"{last} 종가 {cur['c']:.2f}{tag} · 위 {lv:.2f} / 아래(종가) {dn:.2f} · 경과 {len(win)}일"
    hi = max([b["h"] for _, b in win], default=None)
    lo = min([b["l"] for _, b in win], default=None)
    ext = ""
    if row["check"] == "touch_high" and hi is not None:
        ext = f" · 기간 최고 {hi:.2f}"
    if row["check"] == "touch_low" and lo is not None:
        ext = f" · 기간 최저 {lo:.2f}"
    return f"{last} 종가 {cur['c']:.2f}{tag} · 기준선 {lv:.2f}{ext} · 경과 {len(win)}일"


# ---------------------------------------------------------------- 성적표
def pct(x):
    return f"{x * 100:.0f}%"


def build_board(rows):
    now = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    soxl = load_series("SOXL")
    last = next(reversed(soxl)) if soxl else "-"
    done = [r for r in rows if r["score"] != ""]
    pend = [r for r in rows if r["source"] != "retro" and r["outcome"] == ""]
    coin = [r for r in rows if r["source"] != "retro" and r["outcome"] != "" and r["score"] == ""]
    live = [r for r in rows if r["source"] != "retro" and r["brier"] != ""]

    def agg(rs):
        sc = [float(r["score"]) for r in rs if r["score"] != ""]
        b = [float(r["brier"]) for r in rs if r["brier"] != ""]
        return dict(n=len(sc), hit=sum(1 for x in sc if x == 1), half=sum(1 for x in sc if x == 0.5),
                    miss=sum(1 for x in sc if x == 0), pts=(sum(sc) / len(sc)) if sc else None,
                    brier=(sum(b) / len(b)) if b else None, nb=len(b))

    L = [f"# 예측 성적표 (자동 생성 — 직접 고치지 말 것)", "",
         f"- 갱신: {now} · SOXL 가격 최신일: {last}" + (" (추정 가격 포함)" if soxl and soxl[last]["est"] else ""),
         "- 점수 = 맞음 1, 부분 0.5, 틀림 0의 평균 · Brier = (확률 − 결과)² 평균, 낮을수록 좋음 (항상 50%라고 말하면 0.25)", ""]
    def fmt(g):
        return (pct(g["pts"]) if g["pts"] is not None else "-",
                f"{g['brier']:.3f}" if g["brier"] is not None else "-")

    a = agg(rows)
    ap_, ab = fmt(a)
    L += ["## 1. 전체", "",
          f"| 채점 완료 | 맞음 | 부분 | 틀림 | 점수 | Brier (확률 제시 {a['nb']}건) | 진행중 | 동전(50%) |",
          "|---|---|---|---|---|---|---|---|",
          f"| {a['n']} | {a['hit']} | {a['half']} | {a['miss']} | {ap_} | {ab} | {len(pend)} | {len(coin)} |"]
    L += ["", "## 2. 유형별", "", "| 유형 | 건수 | 맞음 | 부분 | 틀림 | 점수 | Brier | 진행중 |", "|---|---|---|---|---|---|---|---|"]
    for c, nm in CATS.items():
        g = agg([r for r in rows if r["cat"] == c])
        pc = sum(1 for r in pend if r["cat"] == c)
        if g["n"] == 0 and pc == 0:
            continue
        gp, gb = fmt(g)
        L.append(f"| {c}. {nm} | {g['n']} | {g['hit']} | {g['half']} | {g['miss']} | {gp} | {gb} | {pc} |")
    # 확률 보정표
    L += ["", "## 3. 확률 보정 (말한 확률 vs 실제로 일어난 비율)", "",
          "| 말한 확률 구간 | 건수 | 말한 확률 평균 | 실제 참 비율 |", "|---|---|---|---|"]
    bins = [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.0001)]
    for lo, hi in bins:
        rs = [r for r in rows if r["outcome"] != "" and fnum(r["prob"]) is not None and lo <= float(r["prob"]) < hi]
        if not rs:
            continue
        mp = sum(float(r["prob"]) for r in rs) / len(rs)
        fo = sum(float(r["outcome"]) for r in rs) / len(rs)
        L.append(f"| {lo * 100:.0f}~{min(hi, 1) * 100:.0f}% | {len(rs)} | {pct(mp)} | {pct(fo)} |")
    L += ["", "## 4. 진행중", "", "| id | 종목 | 내용 | 확률 | 판정 기준 | 마감 | 현재 |", "|---|---|---|---|---|---|---|"]
    for r in sorted(pend, key=lambda r: deadline(r).replace("약 ", "")):
        L.append(f"| {r['id']} | {r['ticker']} | {r['statement']} | {pct(float(r['prob'])) if r['prob'] else '-'} | "
                 f"{CHECKS.get(r['check'], r['check'])} | {deadline(r)} | {status_now(r)} |")
    rec = sorted([r for r in rows if r["source"] != "retro" and r["outcome"] != ""],
                 key=lambda r: r["resolved_on"], reverse=True)[:15]
    if rec:
        L += ["", "## 5. 최근 판정", "", "| 판정일 | id | 종목 | 내용 | 확률 | 결과 | 채점 | 비고 |", "|---|---|---|---|---|---|---|---|"]
        for r in rec:
            res = "일어남" if r["outcome"] == "1" else "안 일어남"
            sc = {"1": "맞음", "0": "틀림", "": "동전"}[r["score"]]
            L.append(f"| {r['resolved_on']} | {r['id']} | {r['ticker']} | {r['statement']} | {r['prob']} | {res} | {sc} | "
                     f"{'추정 가격으로 판정 — 공식 가격 들어오면 재판정' if r['est'] == '1' else ''} |")
    errs = [r for r in rows if "오류:" in r.get("note", "")]
    if errs:
        L += ["", "## 6. 판정 오류", ""] + [f"- {r['id']}: {r['note']}" for r in errs]
    stat = dict(updated_kst=now, soxl_last=last, scored=a["n"], points=a["pts"], brier=a["brier"],
                pending=len(pend), by_cat={c: agg([r for r in rows if r["cat"] == c]) for c in CATS})
    return "\n".join(L) + "\n", stat


# ---------------------------------------------------------------- 명령
def cmd_score():
    rows = read_ledger()
    errs = validate(rows)
    for e in errs:
        print("형식 경고:", e)
    for r in rows:
        score_row(r)
    write_ledger(rows)
    md, stat = build_board(rows)
    open(BOARD, "w", encoding="utf-8").write(md)
    json.dump(stat, open(STATUS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"채점 완료: {stat['scored']}건 · 진행중 {stat['pending']}건 · 점수 "
          f"{pct(stat['points']) if stat['points'] is not None else '-'}")


def cmd_add(argv):
    ap = argparse.ArgumentParser(prog="score.py add", description="예측 1건 등록")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--cat", required=True, choices=list(CATS))
    ap.add_argument("--statement", required=True, help="참/거짓이 갈리는 한 문장")
    ap.add_argument("--check", required=True, choices=list(CHECKS))
    ap.add_argument("--level", default="", help="숫자 또는 ref_close/ref_high/ref_low")
    ap.add_argument("--level2", default="", help="first_up/first_dn의 아래 기준(종가)")
    ap.add_argument("--level-pct", default="", help="기준값 대비 비율 (예: 0.05)")
    ap.add_argument("--ref", required=True, help="기준일(마지막으로 본 종가의 날짜, 미국 거래일)")
    ap.add_argument("--horizon", default="", help="기준일 다음 거래일부터 N거래일")
    ap.add_argument("--end", default="", help="또는 마감일 YYYY-MM-DD")
    ap.add_argument("--prob", required=True, type=float, help="문장이 참일 확률 0~1")
    ap.add_argument("--basis", default="")
    ap.add_argument("--invalidation", default="")
    ap.add_argument("--room", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--made", default="", help="기록 시각 KST (기본: 지금)")
    a = ap.parse_args(argv)
    rows = read_ledger()
    made = a.made or dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    day = made[:10].replace("-", "")
    n = 1 + sum(1 for r in rows if r["id"].startswith(f"L{day}-"))
    row = {k: "" for k in FIELDS}
    row.update(id=f"L{day}-{n:02d}", made_kst=made, room=a.room, ticker=a.ticker.upper(), cat=a.cat,
               statement=a.statement, check=a.check, level=a.level, level2=a.level2, level_pct=a.level_pct,
               ref_date=a.ref, horizon_td=a.horizon, end_date=a.end, prob=f"{a.prob:g}", basis=a.basis,
               invalidation=a.invalidation, source="live", note=a.note)
    errs = validate(rows + [row])
    if errs:
        sys.exit("등록 거부: " + "; ".join(errs))
    rows.append(row)
    write_ledger(rows)
    print("등록:", row["id"], row["statement"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        cmd_add(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        e = validate(read_ledger())
        print("\n".join(e) if e else "형식 이상 없음")
        sys.exit(1 if e else 0)
    else:
        cmd_score()
