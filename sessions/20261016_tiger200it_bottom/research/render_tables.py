# -*- coding: utf-8 -*-
"""보고서용 표 생성: research/output/*.csv, output/daily.csv → research/output/report_tables.md"""
import os, sys, json
import numpy as np, pandas as pd
S = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(S, "research", "output"); d = pd.read_csv(os.path.join(S, "output", "daily.csv"), index_col=0, parse_dates=True)
st = json.load(open(os.path.join(S, "output", "status.json")))
b = pd.read_csv(os.path.join(O, "short_bottoms.csv"), index_col=0, parse_dates=True)
T = pd.read_csv(os.path.join(O, "threshold_table.csv")); E = pd.read_csv(os.path.join(O, "episodes_all.csv"))
C = pd.read_csv(os.path.join(O, "crash_bottom_paths.csv")); I = pd.read_csv(os.path.join(O, "item_predictive.csv"))
md = []
def pct(x, s="+"): return "—" if pd.isna(x) else f"{x:{s}.1%}"

# 1. 이번 하락 경로
md += ["### 표 1. 이번 하락의 일별 점수 (2026-10-06 고점 이후)", "", "| 날짜 | 종가 | 등락 | 표시 | P | V | S | G | 20일 낙폭 | RSI14 | 5일 수익률 | 거래량/20일 | V2 백분위 | V3 백분위 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
w = d.loc["2026-10-06":]; r0 = d.close.pct_change()
for t, r in w.iterrows():
    md.append(f"| {t.date()} | {r.close:,.0f} | {r0[t]:+.1%} | **{r.display:.0f}** | {r.P:.0f} | {r.V:.0f} | {r.S:.0f} | {r.G:.0f} | {r.p1_dd20:+.1%} | {r.p2_rsi14:.0f} | {r.p4_ret5:+.1%} | {r.v1_volratio:.1f} | {'—' if pd.isna(r.v2_pct) else f'{r.v2_pct:.0f}'} | {'—' if pd.isna(r.v3_pct) else f'{r.v3_pct:.0f}'} |")

# 2. 단기 저점 분포
md += ["", "### 표 2. 단기 저점(정의 §4) 저점일 표시점수 분포", "", f"- 단기 저점 {len(b)}개 (2011-06~2026-09). 저점일 표시점수 중앙 {b.display.median():.0f} (25% {b.display.quantile(.25):.0f} · 75% {b.display.quantile(.75):.0f} · 최소 {b.display.min():.0f})",
       f"- 30일 고점 대비 −17% 이하의 **급락형 저점 {int((b.drop_from_30d_high<=-0.17).sum())}개**: 표시점수 중앙 {b[b.drop_from_30d_high<=-0.17].display.median():.0f} (최소 {b[b.drop_from_30d_high<=-0.17].display.min():.0f} · 최대 {b[b.drop_from_30d_high<=-0.17].display.max():.0f})",
       f"- 얕은 저점(−17% 초과) {int((b.drop_from_30d_high>-0.17).sum())}개: 중앙 {b[b.drop_from_30d_high>-0.17].display.median():.0f}", "",
       "| 저점일 표시 | 전체 저점 중 | 급락형 저점 중 |", "|---|---:|---:|"]
deep = b[b.drop_from_30d_high <= -0.17]
for thr in (70, 65, 60, 55, 50, 45, 40):
    md.append(f"| ≤{thr} | {int((b.display<=thr).sum())}/{len(b)} ({(b.display<=thr).mean():.0%}) | {int((deep.display<=thr).sum())}/{len(deep)} ({(deep.display<=thr).mean():.0%}) |")

# 3. 급락형 저점 경로
md += ["", "### 표 3. 급락형 저점 9개의 점수 경로 (저점 −7일 ~ +5일, 굵은 값이 저점일)", "", "| 저점 | 종가 | 30일 낙폭 | 20일 반등 | 저점일 표시 | 경로 −7…+5 | 처음 ≤60 (며칠 전 · 저점 대비 가격) | 처음 ≤50 | 처음 ≤45 |", "|---|---:|---:|---:|---:|---|---|---|---|"]
for _, r in C.iterrows():
    path = json.loads(r.path_m7_p5) if isinstance(r.path_m7_p5, str) else r.path_m7_p5
    ps = " ".join(f"**{v}**" if i == 7 else str(v) for i, v in enumerate(path))
    def f(th):
        rel = r[f"first_le{th}_rel"]; px = r[f"close_at_first_le{th}_vs_bottom"]
        return "없음" if pd.isna(rel) else f"{int(rel):+d}일 · {px:+.1%}"
    md.append(f"| {r.bottom} | {r.close:,.0f} | {r.drop30:+.1%} | {r.rebound20:+.1%} | {int(r.display_at_bottom)} | {ps} | {f(60)} | {f(50)} | {f(45)} |")

# 4. 기준선표 (full)
md += ["", "### 표 4. 기준선별 에피소드 성과 (전 블록, 신호 다음날 시가 체결)", "", "| 기준 | n | 5일 중앙 | 10일 중앙 | 20일 중앙 | 20일 승률 | 20일 내 추가 하락 중앙 | 최악 | 신호 ±5일에 단기 저점 (95% CI) | 다음 저점까지 거래일 중앙 | 저점 종가/체결가 중앙 |", "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|"]
full = T[(T.variant == "full") & (T.period.isna())]
for _, r in full.iterrows():
    md.append(f"| ≤{int(r.thr)} | {int(r.n)} | {pct(r.ret5_med)} | {pct(r.ret10_med)} | {pct(r.ret20_med)} | {r.win20:.0%} | {pct(r.mae20_med)} | {pct(r.mae20_worst)} | {r.bottom5_rate:.0%} ({r.bottom5_ci}) | {r.days_to_bottom_med:.0f} | {pct(r.bottom_vs_fill_med)} |")
base = T[T.variant == "all_days"].iloc[0]
md.append(f"| (전체 거래일) | {int(base.n)} | {pct(base.ret5_med)} | {pct(base.ret10_med)} | {pct(base.ret20_med)} | {base.win20:.0%} | {pct(base.mae20_med)} | {pct(base.mae20_worst)} | {base.bottom5_rate:.0%} ({base.bottom5_ci}) | {base.days_to_bottom_med:.0f} | {pct(base.bottom_vs_fill_med)} |")

# 5. 블록 조합 비교 (≤50, ≤45)
md += ["", "### 표 5. 블록 조합별 비교 (기준 ≤55 / ≤50 / ≤45)", "", "| 조합 | 기준 | n | 10일 중앙 | 20일 승률 | 추가 하락 중앙 | ±5일 저점 비율 |", "|---|---:|---:|---:|---:|---:|---:|"]
for v in ["full", "P+S+G", "P+S", "P+G", "P_only"]:
    for thr in (55, 50, 45):
        q = T[(T.variant == v) & (T.thr == thr) & (T.period.isna())]
        if len(q) == 0 or q.iloc[0].n == 0: md.append(f"| {v} | ≤{thr} | 0 | — | — | — | — |"); continue
        r = q.iloc[0]; md.append(f"| {v} | ≤{thr} | {int(r.n)} | {pct(r.ret10_med)} | {r.win20:.0%} | {pct(r.mae20_med)} | {r.bottom5_rate:.0%} ({r.bottom5_ci}) |")

# 6. 기간 분할
md += ["", "### 표 6. 기간 분할 안정성 (전 블록)", "", "| 기준 | 기간 | n | 10일 중앙 | 20일 승률 | 추가 하락 중앙 | ±5일 저점 비율 |", "|---|---|---:|---:|---:|---:|---:|"]
for thr in (60, 55, 50, 45):
    for per in ("2011-2018", "2019-2026"):
        q = T[(T.variant == "full") & (T.thr == thr) & (T.period == per)]
        if len(q) == 0 or q.iloc[0].n == 0: md.append(f"| ≤{thr} | {per} | 0 | — | — | — | — |"); continue
        r = q.iloc[0]; md.append(f"| ≤{thr} | {per} | {int(r.n)} | {pct(r.ret10_med)} | {r.win20:.0%} | {pct(r.mae20_med)} | {r.bottom5_rate:.0%} ({r.bottom5_ci}) |")

# 7. ≤45 사례 나열
md += ["", "### 표 7. 기준 ≤45 신호 전수 (사례 나열)", "", "| 신호일 | 표시 | 체결가 | 5일 | 10일 | 20일 | 20일 내 최저 | ±5일 저점 | 저점까지 | 저점/체결 |", "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|"]
for _, r in E[E.set == "full<= 45"].iterrows():
    md.append(f"| {r.signal} | {r.display:.0f} | {r.fill_px:,.0f} | {pct(r.ret5)} | {pct(r.ret10)} | {pct(r.ret20)} | {pct(r.mae20)} | {'예' if r.bottom_within5 else '아니오'} | {'—' if pd.isna(r.days_to_bottom) else int(r.days_to_bottom)} | {pct(r.bottom_vs_fill)} |")

# 8. 항목별 단독 예측력
md += ["", "### 표 8. 항목별 단독 예측력 (점수 구간별 이후 10일 수익률 중앙 · 저점 ±5일 안에 있을 비율)", "", "| 항목 | 점수 | 일수 | 10일 중앙 | 10일 평균 | 저점 근접률 |", "|---|---:|---:|---:|---:|---:|"]
for _, r in I.iterrows():
    md.append(f"| {r['item']} | {int(r.points)} | {int(r.n_days)} | {r.fwd10_med:+.2%} | {r.fwd10_mean:+.2%} | {r.near_bottom_rate:.0%} |")

# 9. 과거 급락형 저점 환경 vs 현재
md += ["", "### 표 9. 급락형 저점일의 환경과 현재", "", "| 날짜 | 종가 | 표시 | 20일 낙폭 | RSI14 | 20일선 | 5일 | 거래량/20일 | 코스피 실현변동성 | VIX 20일 최고 | 공포탐욕 | 원달러 20일 | SOX 20일 낙폭 | SOX RSI |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for dt in list(C.bottom) + [str(d.index[-2].date()), str(d.index[-1].date())]:
    r = d.loc[dt]
    md.append(f"| {dt} | {r.close:,.0f} | {r.display:.0f} | {r.p1_dd20:+.1%} | {r.p2_rsi14:.0f} | {r.p3_ma20:+.1%} | {r.p4_ret5:+.1%} | {r.v1_volratio:.1f} | {r.s1_vkospi:.0f} | {r.s2_vix20max:.0f} | {r.s3_fg:.0f} | {r.s4_krw20:+.1%} | {r.g1_soxdd20:+.1%} | {r.g2_soxrsi:.0f} |")
open(os.path.join(O, "report_tables.md"), "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
