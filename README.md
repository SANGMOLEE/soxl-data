# soxl-data

SOXL 반도체 사이클 연구용 시계열 데이터 저장소.
매 미국 거래일 자동 수집되며, 연구 에이전트가 `raw.githubusercontent.com`으로 직접 읽는다.

---

## 1. 설치 (최초 1회)

### 1-1. 저장소 만들기

1. GitHub → **New repository**
2. 이름 `soxl-data`, **Public** 선택 (비공개는 에이전트가 읽지 못함)
3. **Add a README file** 체크 → Create

### 1-2. 파일 올리기

내려받은 폴더의 내용을 저장소에 올린다. 웹에서 `Add file → Upload files`로 드래그해도 된다.

```
soxl-data/
├─ .github/workflows/daily.yml
├─ scripts/
│  ├─ config.py
│  ├─ collect.py
│  └─ seed.py
├─ requirements.txt
├─ .gitignore
└─ README.md
```

### 1-3. Actions 권한 열기

**Settings → Actions → General → Workflow permissions**
→ `Read and write permissions` 선택 → Save

이걸 안 하면 수집은 되지만 저장(커밋)이 실패한다.

### 1-4. 과거 데이터 심기

기존에 쓰던 investing.com CSV들을 로컬 `seed/` 폴더에 넣고:

```bash
pip install -r requirements.txt
python scripts/seed.py
```

`data/` 폴더가 생성된다. 이 폴더를 저장소에 올린다.
(`seed/`는 `.gitignore`에 있어 올라가지 않는다 — 의도된 것)

### 1-5. 첫 실행

**Actions → daily-collect → Run workflow** 클릭.
2~3분 후 `data/status.json`이 `SUCCESS`인지 확인한다.

---

## 2. 폴더 구조

```
data/
├─ status.json              ← 에이전트가 가장 먼저 읽는 파일
├─ prices/{티커}.csv        date,open,high,low,close,adj_close,volume,source
├─ macro/{시리즈}.csv       date,value,source
├─ sentiment/fear_greed.csv date,value,source,rating
├─ manual/                  ← 수동 수집분을 넣는 곳
└─ raw/fear_greed/          원본 JSON 보관 (구조 변경 대비)
logs/YYYYMM.csv             실행 로그
```

---

## 3. 설계 원칙

| 원칙 | 구현 |
|---|---|
| 기존 행 불변 | 신규 날짜만 append. 과거 행은 절대 덮어쓰지 않음 |
| 출처 추적 | 행마다 `source` 컬럼 (`investing` / `yahoo` / `stooq` / `fred` / `cnn`) |
| 출처 혼입 감지 | 겹치는 30일 종가 비교, 0.5% 초과 시 WARN |
| 실패 시 보존 | 검증 통과 전 마스터 교체 안 함. 이전 값 복사 금지 |
| 이중화 | Yahoo 실패 시 Stooq로 자동 전환 |
| 결측 탐지 | SPY에 있고 해당 티커에 없는 날 = 결측으로 기록 |
| 분할 감지 | 일간 60% 초과 변동 시 WARN |

---

## 4. 연구 에이전트용 접근 주소

```python
BASE = "https://raw.githubusercontent.com/{계정}/soxl-data/main/"

import pandas as pd, json, urllib.request

# 1) 신선도 먼저 확인
st = json.load(urllib.request.urlopen(BASE + "data/status.json"))
assert st["status"] != "FAILED", st["failed"]

# 2) 필요한 것만 읽기
sox  = pd.read_csv(BASE + "data/prices/SOX.csv",        parse_dates=["date"])
vix  = pd.read_csv(BASE + "data/macro/VIXCLS.csv",      parse_dates=["date"])
fg   = pd.read_csv(BASE + "data/sentiment/fear_greed.csv", parse_dates=["date"])
```

---

## 5. 주의사항

### 60일 비활성 시 자동 중단
GitHub는 저장소에 사람의 활동이 60일간 없으면 예약 워크플로를 끈다.
봇 커밋은 활동으로 치지 않을 수 있으므로, **2개월에 한 번은 직접 커밋하거나
Actions에서 Run workflow를 눌러 준다.** 중단되면 메일로 통지가 온다.

### yfinance는 비공식
Yahoo가 방어를 강화하면 멈출 수 있다. 그래서 Stooq 이중화를 넣었다.
둘 다 실패하면 `status.json`이 `FAILED`가 되고 기존 데이터는 그대로 남는다.
**조용한 실패가 없다는 것이 핵심이다.**

### `^SOX` 심볼
지수는 ETF보다 지원이 부실하다. 첫 실행 후 `data/prices/SOX.csv`의
2026-07-28 종가가 **11,035.7**과 일치하는지 반드시 확인한다.
어긋나면 SOX는 investing.com 수동 유지로 되돌린다.

### 시간대
`cron`은 UTC 기준. 서머타임에 따라 실행 시각이 1시간 밀린다.
22:30 UTC는 두 경우 모두 미국 마감 이후이므로 문제없다.
GitHub 예약 실행은 부하에 따라 수십 분 지연될 수 있다 (정상).
