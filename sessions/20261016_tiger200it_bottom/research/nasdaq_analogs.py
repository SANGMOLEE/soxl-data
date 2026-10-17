# -*- coding: utf-8 -*-
"""나스닥 '고점 부근 첫 -4% 주' 유사 사례와 공포탐욕 극단 공포 첫 진입 뒤의 경로 (기록 조사)."""
import os, sys
import pandas as pd, numpy as np
pd.set_option("display.width", 250)
S = sys.argv[1]; P = os.path.join(S, "data", "prices"); R = os.path.dirname(os.path.dirname(S)); O = os.path.join(S, "research", "output")
nq = pd.read_csv(f"{P}/NASDAQ.csv", parse_dates=["date"]).set_index("date")["close"]
vix = pd.read_csv(f"{P}/VIX.csv", parse_dates=["date"]).set_index("date")["close"]
sox = pd.read_csv(f"{P}/SOX.csv", parse_dates=["date"]).set_index("date")["close"]
fg = pd.read_csv(f"{R}/data/sentiment/fear_greed.csv", parse_dates=["date"]).set_index("date")["value"]
w = nq.resample("W-FRI").last().dropna(); wr = w.pct_change(); hi52 = w.rolling(52, min_periods=26).max()
vw = vix.resample("W-FRI").last(); swr = sox.resample("W-FRI").last().pct_change(); fgw = fg.resample("W-FRI").last()
def fwd(i, h): return w.iloc[i + h] / w.iloc[i] - 1 if i + h < len(w) else np.nan
def mdd(i, h): return w.iloc[i + 1:i + 1 + h].min() / w.iloc[i] - 1 if i + h < len(w) else np.nan
rows = []
for i in range(52, len(w)):
    if wr.iloc[i] <= -0.04 and w.iloc[i - 1] / hi52.iloc[i - 1] >= 0.97 and (wr.iloc[i - 4:i] <= -0.04).sum() == 0:
        rows.append({"week": w.index[i].date(), "wk%": round(wr.iloc[i] * 100, 1), "from52wH": round((w.iloc[i] / hi52.iloc[i] - 1) * 100, 1),
                     "vix": round(vw.get(w.index[i], np.nan), 1), "sox_wk%": round(swr.get(w.index[i], np.nan) * 100, 1), "fg": round(fgw.get(w.index[i], np.nan), 0),
                     "+1w": round(fwd(i, 1) * 100, 1), "+2w": round(fwd(i, 2) * 100, 1), "+4w": round(fwd(i, 4) * 100, 1), "+8w": round(fwd(i, 8) * 100, 1), "+13w": round(fwd(i, 13) * 100, 1),
                     "mdd4w": round(mdd(i, 4) * 100, 1), "mdd13w": round(mdd(i, 13) * 100, 1),
                     "lowerlow4w": (w.iloc[i + 1:i + 5].min() < w.iloc[i]) if i + 4 < len(w) else np.nan,
                     "recov8w": (w.iloc[i + 1:i + 9].max() >= w.iloc[i - 1]) if i + 8 < len(w) else np.nan})
T = pd.DataFrame(rows); T.to_csv(os.path.join(O, "nasdaq_first_down_week.csv"), index=False)
done = T.dropna(subset=["+13w"])
print("고점(52주 최고 3% 이내)에서 첫 -4% 주 (직전 4주에 -4% 주 없음):", len(T), "(완료", len(done), ")")
print(T.to_string(index=False))
def summ(lab, sub):
    if len(sub) == 0: return
    print("%s: n=%d | +1w 중앙 %+.1f%% | +4w 중앙 %+.1f%% (플러스 %.0f%%) | +8w 중앙 %+.1f%% | +13w 중앙 %+.1f%% (플러스 %.0f%%) | 13주 최대낙폭 중앙 %.1f%% 최악 %.1f%% | 추가 -10%% 이상 %.0f%% | 4주내 더 낮은 주봉종가 %.0f%% | 8주내 하락전 고점 회복 %.0f%%"
          % (lab, len(sub), sub["+1w"].median(), sub["+4w"].median(), (sub["+4w"] > 0).mean() * 100, sub["+8w"].median(), sub["+13w"].median(), (sub["+13w"] > 0).mean() * 100,
             sub.mdd13w.median(), sub.mdd13w.min(), (sub.mdd13w <= -10).mean() * 100, sub.lowerlow4w.astype(float).mean() * 100, sub.recov8w.astype(float).mean() * 100))
summ("전체", done)
summ("VIX<25 (조용한 시작)", done[done.vix < 25]); summ("VIX>=25", done[done.vix >= 25])
summ("SOX 주간 -8% 이하 (반도체 주도)", done[done["sox_wk%"] <= -8]); summ("2000년 이후", done[pd.to_datetime(done.week) >= "2000-01-01"])
allw = pd.DataFrame({"+4w": [fwd(i, 4) for i in range(52, len(w) - 13)], "+13w": [fwd(i, 13) for i in range(52, len(w) - 13)], "mdd13w": [mdd(i, 13) for i in range(52, len(w) - 13)]})
print("기준(전체 주): +4w 중앙 %+.1f%% 플러스 %.0f%% | +13w 중앙 %+.1f%% 플러스 %.0f%% | 13주 최대낙폭 중앙 %.1f%% | -10%% 이하 %.0f%%"
      % (allw["+4w"].median() * 100, (allw["+4w"] > 0).mean() * 100, allw["+13w"].median() * 100, (allw["+13w"] > 0).mean() * 100, allw.mdd13w.median() * 100, (allw.mdd13w <= -0.10).mean() * 100))
# 공포탐욕 20 이하 첫 진입
fgd = fg.reindex(nq.index).ffill(); v = fgd.values; ev = []
for i in range(20, len(nq)):
    if v[i] <= 20 and (v[i - 20:i] > 20).all():
        g = lambda h: round((nq.iloc[i + h] / nq.iloc[i] - 1) * 100, 1) if i + h < len(nq) else np.nan
        ev.append({"date": nq.index[i].date(), "fg": round(v[i]), "nq_dd20": round((nq.iloc[i] / nq.iloc[i - 20:i + 1].max() - 1) * 100, 1), "vix": round(vix.reindex(nq.index).ffill().iloc[i], 1),
                   "+5d": g(5), "+20d": g(20), "+65d": g(65),
                   "mdd20d": round((nq.iloc[i + 1:i + 21].min() / nq.iloc[i] - 1) * 100, 1) if i + 20 < len(nq) else np.nan,
                   "mdd65d": round((nq.iloc[i + 1:i + 66].min() / nq.iloc[i] - 1) * 100, 1) if i + 65 < len(nq) else np.nan})
E = pd.DataFrame(ev); E.to_csv(os.path.join(O, "nasdaq_fg_extreme_fear.csv"), index=False)
Ed = E.dropna(subset=["+65d"])
print("\n공포탐욕 20 이하 첫 진입 (2011~):", len(E)); print(E.to_string(index=False))
print("요약(완료 %d): +5d 중앙 %+.1f%% | +20d 중앙 %+.1f%% (플러스 %.0f%%) | +65d 중앙 %+.1f%% (플러스 %.0f%%) | 65일 최대낙폭 중앙 %.1f%% 최악 %.1f%% | 20일내 추가 -5%% 이상 %.0f%%"
      % (len(Ed), Ed["+5d"].median(), Ed["+20d"].median(), (Ed["+20d"] > 0).mean() * 100, Ed["+65d"].median(), (Ed["+65d"] > 0).mean() * 100, Ed.mdd65d.median(), Ed.mdd65d.min(), (Ed.mdd20d <= -5).mean() * 100))
