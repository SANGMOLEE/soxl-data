# -*- coding: utf-8 -*-
"""거시 조건별 SOX 이후 경로 — 하이일드 급확대, VIX 미폭발, NVDA 비율, 공포탐욕"""
import pandas as pd, numpy as np, load
p = load.panel(); s = p["sox"]
fut_min60 = s[::-1].rolling(60, min_periods=1).min()[::-1].shift(-1)
p["more60"] = (fut_min60 / s - 1).clip(upper=0)
p["f60"] = s.shift(-60) / s - 1
p["f20"] = s.shift(-20) / s - 1

def ep(mask, gap=40):
    idx, last = [], None
    for t in p.index[mask.fillna(False)]:
        if last is None or (t - last).days > gap * 1.45:
            idx.append(t)
        last = t
    return idx

def show(name, idx):
    d = p.loc[[t for t in idx if not np.isnan(p.at[t, "f60"])]]
    print(f"\n[{name}] 에피소드 n={len(d)}")
    if len(d):
        print("  ", ", ".join(str(t.date()) for t in d.index))
        print(f"   60일 내 추가하락 중앙 {d.more60.median():.1%}, 하위25% {d.more60.quantile(.25):.1%} | 20일뒤 + {(d.f20>0).mean():.0%} | 60일뒤 중앙 {d.f60.median():.1%}, + {(d.f60>0).mean():.0%}")

base = p.dropna(subset=["f60"])
print(f"무조건 기준선(1997~): 60일 내 추가하락 중앙 {base.loc['1997':].more60.median():.1%}, 60일뒤 + {(base.loc['1997':].f60>0).mean():.0%}")

show("HY 20일 +0.5%p 이상 확대 & 수준 4% 미만", ep((p.hy_chg20 >= 0.5) & (p.hy.shift(20) < 4.0)))
show("HY 3.41% 상향 돌파 (20일 전 3.0% 미만)", ep((p.hy >= 3.41) & (p.hy.shift(1) < 3.41) & (p.hy.shift(20) < 3.0)))
show("SOX 60일 -14%↓ & VIX 60일 최고 < 25 (공포 없는 섹터 급락)", ep((p.dd60 <= -0.14) & (p.vix60max < 25)))
show("SOX 60일 -14%↓ & VIX 60일 최고 >= 30 (공포 동반)", ep((p.dd60 <= -0.14) & (p.vix60max >= 30)))
show("SOX 60일 -14%↓ & NVDA 비율 < 0.8 (대장주 미동참)", ep((p.dd60 <= -0.14) & (p.nvda_ratio < 0.8) & (p.nvda_ratio > 0)))
show("SOX 60일 -14%↓ & 공포탐욕 <= 20", ep((p.dd60 <= -0.14) & (p.fg <= 20)))
show("SOX 60일 -14%↓ & SPY 60일 -3% 이내 (시장 멀쩡)", ep((p.dd60 <= -0.14) & (p.spy_dd60 > -0.03)))

# 과거 큰 급락 바닥일의 VIX·공포탐욕·HY 수준 — 바닥은 보통 어떤 모습이었나
z = []
x = s.loc["2011":]
lows = [t for t in x.index if x[t] == x[t - pd.Timedelta(days=60):t + pd.Timedelta(days=60)].min()]
for t in lows:
    pk = s[:t].iloc[-80:].max()
    if s[t]/pk - 1 <= -0.15:
        z.append(dict(low=t.date(), dd_from_80d_high=s[t]/pk-1, vix=p.at[t, "vix"], vix60max=p.at[t, "vix60max"], fg=p.at[t, "fg"],
                      fg_min20=p.fg[:t].iloc[-20:].min(), hy=p.at[t, "hy"], hy_chg20=p.at[t, "hy_chg20"], nvda_ratio=p.at[t, "nvda_ratio"], rsi=p.at[t, "rsi"]))
Z = pd.DataFrame(z)
pd.set_option("display.width", 250)
print("\n2011년 이후 SOX 주요 저점(±60일 최저, 80일 고점 대비 -15% 이상)의 지표 모습")
print(Z.round(2).to_string(index=False))
print("\n중앙값:", Z.drop(columns="low").median().round(2).to_dict())
print("현재  :", {k: round(float(p[k].iloc[-1]), 2) for k in ["dd60", "vix", "vix60max", "fg", "hy", "hy_chg20", "nvda_ratio", "rsi"]}, "fg_min20", p.fg.iloc[-20:].min())
