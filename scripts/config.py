# -*- coding: utf-8 -*-
"""SOXL 사이클 연구 - 수집 대상 정의"""

# ── 기준 티커 ────────────────────────────────────────────────
# 미국 거래일 판정의 기준. 이 티커에 있고 다른 티커에 없으면 '결측'.
CALENDAR_REF = "SPY"

# ── 주가 / 지수 ──────────────────────────────────────────────
# key = 저장 파일명, yahoo/stooq = 각 제공처 심볼(없으면 None)
PRICES = {
    "SOX":  {"yahoo": "^SOX",  "stooq": "^sox",    "role": "핵심", "note": "필라델피아 반도체지수. A블록 전 항목의 기준"},
    "SOXL": {"yahoo": "SOXL",  "stooq": "soxl.us", "role": "핵심", "note": "3x 롱. 매매 대상"},
    "SOXS": {"yahoo": "SOXS",  "stooq": "soxs.us", "role": "보조", "note": "3x 숏. 인버스 감쇠 실측용"},
    "SOXX": {"yahoo": "SOXX",  "stooq": "soxx.us", "role": "핵심", "note": "ICE지수 1x 대용. 2021-08 이후 SOXL 실제 기초지수"},
    "NVDA": {"yahoo": "NVDA",  "stooq": "nvda.us", "role": "핵심", "note": "NVDA 필터(낙폭비율 >= 0.80)"},
    "MU":   {"yahoo": "MU",    "stooq": "mu.us",   "role": "보조", "note": "메모리 사이클 대표"},
    "SPY":  {"yahoo": "SPY",   "stooq": "spy.us",  "role": "기준", "note": "거래일 달력 기준"},
    "QQQ":  {"yahoo": "QQQ",   "stooq": "qqq.us",  "role": "참고", "note": "상대강도 비교"},

    # ── GDXU 금광주 사이클 연구 (2026-10-30 추가) ──────────────────
    # optional=True : 수집 실패 시 FAILED 가 아니라 WARN 으로 기록한다.
    #                 SOXL 연구 에이전트의 status 판정을 깨뜨리지 않기 위함.
    "GDXU": {"yahoo": "GDXU",  "stooq": "gdxu.us", "role": "핵심", "optional": True,
             "note": "3x 롱 ETN(BMO). 매매 대상. 2022-10-31 1:10 역분할(제공처 소급조정 확인 필요)"},
    "GDXD": {"yahoo": "GDXD",  "stooq": "gdxd.us", "role": "보조", "optional": True,
             "note": "3x 인버스 ETN. 감쇠 실측용. 2025-10-22 1:20 역분할"},
    "GDX":  {"yahoo": "GDX",   "stooq": "gdx.us",  "role": "핵심", "optional": True, "start": "1990-01-01",
             "note": "대형 금광주 1x. GDXU 기초지수의 주 구성. A블록 기준"},
    "GDXJ": {"yahoo": "GDXJ",  "stooq": "gdxj.us", "role": "핵심", "optional": True,
             "note": "중소형 금광주 1x. GDXU 기초지수의 부 구성"},
    "GLD":  {"yahoo": "GLD",   "stooq": "gld.us",  "role": "핵심", "optional": True, "start": "1990-01-01",
             "note": "금 현물 대용. GDX/GLD 비율(광산주 상대강도) 계산용"},
    "SLV":  {"yahoo": "SLV",   "stooq": "slv.us",  "role": "보조", "optional": True,
             "note": "은. 금은비율·선행 신호(2026-10-29 은이 먼저 연저점)"},
    "NEM":  {"yahoo": "NEM",   "stooq": "nem.us",  "role": "핵심", "optional": True, "start": "1990-01-01",
             "note": "NEM 필터 — SOXL 연구의 NVDA 필터와 동일 역할"},
    "HUI":  {"yahoo": "^HUI",  "stooq": None,      "role": "참고", "optional": True, "start": "1990-01-01",
             "note": "NYSE Arca Gold BUGS 지수. 1996~ 장기 사이클 저점 식별용"},
    "XAU":  {"yahoo": "^XAU",  "stooq": None,      "role": "참고", "optional": True, "start": "1990-01-01",
             "note": "필라델피아 금은지수. 1983~ 최장 이력"},
    "GOLD": {"yahoo": "GC=F",  "stooq": "xauusd",  "role": "핵심", "optional": True, "start": "1990-01-01",
             "note": "금 선물 연속물(야후) / 금 현물(stooq). 2000~"},
}

# ── FRED 거시지표 (API키 불필요) ─────────────────────────────
FRED = {
    "VIXCLS":       {"role": "핵심", "note": "B1 채점. 60거래일 최고치 사용"},
    "NFCI":         {"role": "핵심", "note": "D1 채점. 주간 발표(수요일)"},
    "BAMLH0A0HYM2": {"role": "감시", "note": "하이일드 스프레드. 3.41% 돌파 감시"},
    "T10Y2Y":       {"role": "참고", "note": "장단기 금리차. 미편입"},
    "DEXKOUS":      {"role": "참고", "note": "원달러. 미편입"},
    # ── GDXU 연구용 (2026-10-30 추가) ────────────────────────────
    "DFII10":       {"role": "핵심", "note": "10년 TIPS 실질금리. 금 가격의 제1 거시 변수", "optional": True},
    "T10YIE":       {"role": "참고", "note": "10년 기대인플레이션(BEI)", "optional": True},
    "DTWEXBGS":     {"role": "핵심", "note": "광의 달러지수(FRED). DXY 대용", "optional": True},
    "DGS10":        {"role": "참고", "note": "10년 명목금리", "optional": True},
}

# ── 심리지표 ────────────────────────────────────────────────
FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# FRED 그래프 API는 시리즈에 따라 기본 조회창이 최근 몇 년으로 잘린다.
# (2026-08-01 확인: BAMLH0A0HYM2 가 27년치 → 3년치로 절단됨)
# cosd/coed 를 명시해 전 기간을 강제한다.
FRED_START = "1776-07-04"

# ── 검증 임계값 ─────────────────────────────────────────────
MAX_DAILY_MOVE   = 0.60   # 일간 60% 초과 변동 = 분할 의심 → 경고
OVERLAP_CHECK    = 30     # 기존/신규 겹침 비교 일수
OVERLAP_TOL      = 0.005  # 0.5% 초과 차이 = 출처 불일치 경고
STALE_DAYS       = 4      # 최신일이 이보다 뒤처지면 STALE 판정

# 발표 지연이 정상인 시리즈 — STALE 판정에서 제외
#   NFCI     : 주간(수요일) 발표
#   DEXKOUS  : 주 단위 갱신, 최대 7일 지연
#   BAMLH0A0HYM2 : 1~2 영업일 지연
STALE_EXEMPT = ("NFCI", "DEXKOUS", "BAMLH0A0HYM2", "DTWEXBGS", "DFII10", "T10YIE", "DGS10")

# 축소 경보 — 신규 수집분이 기존 대비 이 비율 미만이면 절단으로 간주
SHRINK_GUARD = 0.90
