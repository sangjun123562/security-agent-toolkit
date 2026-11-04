# 11/4(수) 오후 · 4과목 이상탐지 ③ — 요청이 늘어난 때 찾기 · 알림을 한 파일로 모으기 — 실습

오전에는 로그인 실패 규칙과 이벤트 유형 규칙을 만들었습니다. 오후에는 **요청이 갑자기 늘어난 때(트래픽 급증, traffic spike, 트래픽 스파이크)** 를 찾는 규칙을 하나 더 만들고, 오전과 오후의 탐지 결과를 **알림 한 파일**로 모읍니다. SIEM(심, 보안 로그를 모아 탐지 · 알림하는 시스템)의 네 단계 중 탐지를 마무리하고 마지막 단계인 **알림**을 처음 해 보는 날입니다.

- **5교시**: 웹 서버 요청을 분마다 세고, 지난 7일 평균의 3배 이상으로 늘어난 분을 찾습니다.
- **6교시**: 로그인 실패 알림과 트래픽 급증 알림을 같은 모양으로 만들어 `alerts.json` 한 파일에 저장합니다.

오늘은 오후 5 · 6교시이고, 깃허브에 올리는 일은 6교시 마지막에 합니다. 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널 · git** 입니다.
- 급증 기준은 **지난 7일 평균의 3배로 고정**하고, 값을 바꿔 가며 비교하지 않습니다.
- 샘플 이벤트의 날짜는 2026-11-02 이고, 이야기 속 「오늘」은 이 샘플을 기준으로 합니다. `baseline_traffic.csv` 의 숫자는 오전 9시대 값이고, 웹 서버 이벤트도 모두 9시대입니다(57개 중 웹 서버 28 · 판정 서버 15(`source` 가 `server`) · SaaS 14).
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, 내 화면의 값을 근거로 이유까지 서술합니다.
- 📎 **오늘 불러 쓰는 이전 파일**이 있습니다. 모두 오늘 오전에 만든 파일입니다.

| 파일 | 만든 곳 | 쓰는 곳 | 없거나 안 풀렸을 때 |
|---|---|---|---|
| `normalized_events.json` | 오전 안내(`day03_am_baseline_login.md`) 시작하기 5번 | 5 · 6교시 | 그 안내 시작하기 5번의 내용으로 파일을 만듭니다 |
| `login_detection.py` | 오전 3교시 문제 3-1 | 6교시 `day03_6-1_run.py` 가 불러옵니다 | 오전 안내 문제 3-1 의 `login_detection.py` 코드 칸을 붙여 넣고, 「정답 3-1」의 「채운 코드」를 빈칸 자리에 넣어 파일을 완성합니다. `pick_alert_ips` 는 주소와 횟수를 담은 결과(`Series`)를 리턴해야 합니다 |

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치와 오전 파일을 확인합니다. `pwd` 가 `…/anomaly_detection` 으로 끝나고, `ls` 결과에 `login_detection.py` 와 `normalized_events.json` 이 보여야 합니다.
   ```bash
   cd anomaly_detection
   pwd
   ls
   ```
3. **오늘 받은 파일 두 개**(`day03_pm_traffic_alerts.md`, `day03_pm_report.md`)를 `다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-04(수))` 의 `이름` 을 내 이름으로 바꿉니다. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[VS Code 또는 터미널]** `anomaly_detection` 폴더에 `baseline_traffic.csv` 파일을 만들어 아래 내용을 그대로 붙여 넣습니다(터미널에서는 `touch baseline_traffic.csv` 후 VS Code 에서 엽니다).

**`baseline_traffic.csv`** — 지난 7일 동안 오전 9시대에 웹 서버로 들어온 요청이 **1분에 평균 몇 번**이었는지 적은 연습용 숫자입니다. 첫 줄은 헤더(열 이름이 적힌 줄)이고, 둘째 줄부터 한 줄이 하루입니다.

```
date,requests_per_minute
2026-10-26,2
2026-10-27,2
2026-10-28,3
2026-10-29,2
2026-10-30,1
2026-10-31,2
2026-11-01,2
```

6. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`).
   ```bash
   python -c "print(len(open('baseline_traffic.csv', encoding='utf-8').read().splitlines()))"
   ```
   - `8`(헤더 줄 포함)이 나와야 합니다. 다르면 줄이 누락됐거나 빈 줄이 들어간 것이니 다시 붙여 넣습니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다.
- `No module named 'pandas'`: 가상환경이 활성화되지 않은 터미널입니다. `security-agent-toolkit` 폴더에서 `source .venv/Scripts/activate` 로 활성화한 뒤 `python -m pip install pandas` 를 입력합니다(맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 `.venv` 가 아니면 그 이름으로).
- `ImportError` · `No module named 'login_detection'`: 오전 `login_detection.py` 가 없거나 함수 이름이 문서와 다른 것입니다. 위 표의 「없거나 안 풀렸을 때」를 따릅니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 요청이 갑자기 늘어난 분 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 서버 담당자가 보낸 메시지입니다:
> 「오늘 오전 9시대에 홈페이지가 잠깐 느려졌다는 문의가 들어왔습니다. 웹 서버 이벤트 28개에서 요청이 갑자기 늘어난 때가 있는지 찾아 주세요.
>
> 지난 7일 같은 시간대에는 1분에 평균 2번쯤 요청이 들어왔습니다. 그 3배(6번) 이상이면 급증했다고 보기로 했습니다.」
> - **왜 중요한가**: <mark>요청이 갑자기 늘면 서버가 느려지거나 멈출 수 있고, 공격의 징후일 수도 있습니다.</mark> 하루 전체 요청 수로는 1분 동안의 급증이 보이지 않으므로, 분마다 세어 평소와 비교합니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 오전의 로그인 실패 규칙은 **같은 주소가 몇 번 실패했는가**를 봤습니다. 오후의 규칙은 **짧은 시간에 요청이 몇 개 들어왔는가**를 봅니다.
2. 짧은 시간의 요청 수를 세려면 이벤트를 **같은 분으로 그룹화해야** 합니다. 그런데 이벤트의 시각은 초까지 적혀 있어서(`09:12:03`, `09:12:06`) 그대로 두면 모두 다른 시각입니다.
3. 그래서 **시각에서 초를 버려** 분까지만 남기고, 같은 분으로 그룹화해 셉니다.

### 📖 5.1 트래픽 급증 규칙과 판다스 한 가지

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

| 말 | 뜻 | 오늘 예 |
|---|---|---|
| 트래픽 급증 | 짧은 시간에 요청이 평소보다 크게 늘어남 | 한 분에 요청이 많이 들어옴 |
| 평소 기준(baseline) | 지난 7일 같은 시간대의 분당 평균 요청 수 | 2번 |
| 급증 기준 | 평소 평균의 3배 | 6번 이상 |

지난 7일의 숫자는 이렇게 생겼습니다(연습용 숫자입니다).

| 날짜 | 1분 평균 요청 수 |
|---|---|
| 10/26 | 2 |
| 10/27 | 2 |
| 10/28 | 3 |
| 10/29 | 2 |
| 10/30 | 1 |
| 10/31 | 2 |
| 11/1 | 2 |

- 평균은 (2 + 2 + 3 + 2 + 1 + 2 + 2) ÷ 7 = **2.0**이고, 급증 기준은 2.0 × 3 = **6.0**번입니다.
- 오전 2교시와 같은 순서입니다: 평소를 구하고, 그 숫자에서 기준을 정합니다. 달라진 점은 「최댓값 + 1」 대신 「평균의 3배」를 쓴다는 것입니다. 1분 요청 수는 1 ~ 3개로 자주 달라져서, 평균의 3배 이상일 때만 급증으로 보기 위해서입니다.
- 오늘은 이 기준을 **고정**하고, 값을 바꿔 가며 비교하지 않습니다.
- 이 규칙은 분마다 요청이 **몇 개**인지만 봅니다. 요청의 내용(어떤 경로를 요청했는지)은 보지 않습니다.
- 급증은 이상 징후(평소 범위를 벗어난 일)의 한 종류입니다. 급증이 있다고 공격이 확정되는 것은 아니고, 먼저 확인할 대상이 정해질 뿐입니다.

**🐼 판다스 문법 상자 — 시각에서 초를 버려 분으로 맞추기**

**<mark>`시각.dt.floor("min")`</mark> 은 시각에서 초를 버리고 분까지만 남깁니다. `09:12:03` 도 `09:12:15` 도 `09:12:00` 이 되어, 같은 분의 이벤트가 같은 값을 갖습니다**

`pd.to_datetime` 으로 문자열 시각을 시각 값으로 바꾼 뒤에 `.dt` 를 붙여 씁니다. `.dt.hour` 는 「시」를 숫자 하나로 꺼냈지만, `.dt.floor("min")` 은 **시각 값 그대로** 두고 초만 0 으로 만듭니다. `floor` 는 「내림」(작은 쪽으로 맞춤)이라는 뜻이고, `"min"` 은 분(minute)의 줄임말입니다.

| 행 번호(고른 3개) | `time` 열(문자열) | `times`(시각 값) | `minutes`(`.dt.floor("min")`) |
|---|---|---|---|
| 1 | 2026-11-02 09:01:05 | 2026-11-02 09:01:05 | 2026-11-02 09:01:00 |
| 2 | 2026-11-02 09:01:06 | 2026-11-02 09:01:06 | 2026-11-02 09:01:00 |
| 18 | 2026-11-02 09:20:10 | 2026-11-02 09:20:10 | 2026-11-02 09:20:00 |

위 표의 첫 두 줄은 시각이 달랐지만 `minutes` 에서는 같은 값이 됩니다. 같은 값이 몇 번 나오는지(`value_counts`) 세어 차이를 봅니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

times = pd.to_datetime(events["time"])           # 문자열 시각을 시각 값으로 바꾼다
minutes = times.dt.floor("min")                  # 시각에서 초를 버린다 (09:12:03 → 09:12:00)

times_counts = times.value_counts()              # 같은 시각이 몇 번씩 나오는지 센다
times_max = times_counts.max()                   # 가장 많이 나온 횟수를 구한다
print(times_max)                                 # 1 — 초까지 같은 시각은 한 번뿐이다
```

실행 결과:

```
1
```

앞 칸에 이어서 쓰는 다음 칸입니다.

```python
minutes_counts = minutes.value_counts()  # 같은 분이 몇 번씩 나오는지 센다
minutes_max = minutes_counts.max()       # 가장 많이 나온 횟수를 구한다
print(minutes_max)                       # 9 — 어떤 한 분에 이벤트가 9개 있다
```

실행 결과:

```
9
```

- 읽는 법: 초까지 있는 `times` 에서는 같은 시각이 한 번뿐이라 가장 많이 나온 횟수가 **1**입니다. 분까지만 남긴 `minutes` 에서는 같은 분이 여러 번 나와서 가장 많이 나온 횟수가 **9**입니다. 같은 분에 이벤트가 9개 모여 있는 것이 오늘 찾으려는 트래픽 급증입니다.
- 이 값(9)은 웹 서버뿐 아니라 모든 이벤트를 센 것입니다. 문제에서는 웹 서버 이벤트만 골라서 셉니다.
- `.dt` 없이 `times.floor("min")` 으로 쓰면 오류가 납니다(아래 「자주 틀리는 곳」). 어제 `times.dt.hour` 처럼 `.dt` 를 먼저 붙입니다.

**알아 둘 것 — 출력 맨 아래의 `dtype: int64`**

`value_counts()` 나 `groupby().size()` 로 센 결과의 맨 아래에는 `dtype: int64` 가 함께 나옵니다. `dtype` 은 data type(데이터 타입)의 줄임말로 값의 종류를 뜻하고, `int64` 는 정수(소수점 없는 숫자)입니다. 숫자 계산이 되는 정상 상태이므로 지금은 `int64` 가 보이면 됩니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

counts = events["source"].value_counts()         # source 열을 꺼내 바로 값별 개수를 센다
print(counts)                                    # 맨 아래에 dtype: int64 가 함께 나온다
```

실행 결과:

```
source
web       28
server    15
saas      14
Name: count, dtype: int64
```

| dtype | 뜻 | 예 |
|---|---|---|
| `int64` | 정수 | 5 · 200 |
| `float64` | 소수 | 2.4 |
| `object` | 문자열 | `"실패"` |
| `bool` | `True` · `False` | `is_fail` 열 |
| `datetime64[ns]` | 시각 값 | 2026-11-02 09:12:03 |

- 숫자인데 `object` 로 나오면 문자열로 읽힌 것이라 합계 · 비교가 맞지 않습니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` | 파일 경로 | 이벤트 표(미리 채움) |
| `add_minute_column` | 이벤트 표 | `minute` 열이 붙은 이벤트 표 |
| `count_web_per_minute` | `minute` 열이 있는 표 | 웹 서버 요청이 분마다 몇 개인지 |
| `make_traffic_limit` | 파일 경로와 3(배) | 급증 기준(평균 × 3) |
| `pick_spike_minutes` | 분마다 요청 수와 급증 기준 | 기준 이상인 분과 요청 수 |

- **직접 쓰는 곳은 네 함수**(번호 1 ~ 6)입니다.
  - `add_minute_column`(1번): 초를 버린 시각을 만듭니다. 그 시각을 `minute` 열로 붙이는 줄은 아직 배우지 않은 문법이라 미리 채웠습니다.
  - `count_web_per_minute`(2 · 3번): 웹 서버 이벤트만 걸러 냅니다. 분마다 그룹화해 세는 줄은 미리 채웠습니다.
  - `make_traffic_limit`(4번): 평균에 3을 곱해 급증 기준을 정합니다. 파일을 읽고 평균을 구하는 줄은 오전 2교시와 같아서 미리 채웠습니다.
  - `pick_spike_minutes`(5 · 6번): 기준 이상인 분만 남깁니다. 오전 3교시의 `pick_alert_ips` 와 같은 모양입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 웹 서버 요청을 분마다 세어 요청이 급증한 분 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 웹 서버 이벤트 28개가 초 단위로 흩어져 있어서, 어느 1분에 요청이 늘었는지 한눈에 안 보입니다.
- **그래서 만드는 것**: `traffic_detection.py` 입니다.
  - 이벤트마다 초를 버린 시각(`minute`)을 붙입니다.
  - 웹 서버 이벤트만 골라 분마다 요청 수를 셉니다.
  - 지난 7일 평균의 3배를 급증 기준으로 정하고, 기준 이상인 분만 남깁니다.
- **실행하면**: 단계 1: 시각과 분 비교, 단계 2: 분당 요청 수, 단계 3: 급증 기준, 단계 4: 요청이 급증한 분이 나옵니다.
- **현업에서는**: 트래픽 급증 규칙은 서버 장애와 공격을 함께 탐지하는 기본 규칙입니다. 알림이 오면 그 분의 요청을 누가 보냈는지부터 봅니다.

**🎯 할 일**

1. `traffic_detection.py` · `day03_5-1_run.py` 두 파일을 만들고, `traffic_detection.py` 의 네 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>시각과 분의 차이</mark>(단계 1), <mark>분당 요청 수</mark>(단계 2), <mark>급증 기준</mark>(단계 3), <mark>요청이 급증한 분</mark>(단계 4)를 읽습니다.

**`traffic_detection.py`**

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
TRAFFIC_PATH = "baseline_traffic.csv"                 # 지난 7일 같은 시간대의 분당 요청 수 파일 이름
SPIKE_MULTIPLE = 3                                    # 평소 평균의 3배 이상이면 급증으로 본다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def add_minute_column(events):                        # 이벤트 표를 받는 함수
    """이벤트마다 시각에서 초를 버린 minute 열을 붙인다.
    분당 요청 수를 세기 전에 같은 분으로 그룹화할 기준을 만들 때 쓴다.
    """
    times = pd.to_datetime(events["time"])            # 문자열 시각을 시각 값으로 바꾼다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. times 에 .dt.floor("min") 을 붙여 초를 버린 시각을 minutes 에 담는다
    events["minute"] = minutes                        # 표에 minute 열을 붙인다 — 미리 채운 줄
    return events                                     # minute 열이 붙은 표를 리턴한다


def count_web_per_minute(events):                     # minute 열이 있는 이벤트 표를 받는 함수
    """웹 서버 이벤트만 골라 분마다 요청이 몇 개인지 센다.
    분당 요청 수를 평소와 비교하기 전에 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. events["source"] == "web" 으로 행마다 True 또는 False 를 구해 is_web 에 담는다 (웹 서버 이벤트이면 True)
    # 3. events 에서 is_web 이 True 인 행만 골라 web_events 에 담는다 (events[is_web])
    counts = web_events.groupby("minute").size()      # minute 값이 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지(그 분의 요청 수) 센다(size)
    return counts                                     # 분마다 요청 수를 리턴한다


def make_traffic_limit(path, multiple):               # 파일 경로와 몇 배인지를 받는 함수
    """지난 7일 분당 요청 평균의 multiple 배를 급증 기준으로 정한다.
    평소보다 요청이 크게 늘어난 분을 가려낼 급증 기준을 정할 때 쓴다.
    """
    baseline = pd.read_csv(path)                      # 지난 7일 파일을 표로 읽는다
    average = baseline["requests_per_minute"].mean()  # 분당 요청 수 열을 꺼내(["requests_per_minute"]) 바로 7개의 평균을 구한다(mean)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. average 에 multiple 을 곱해 limit 에 담는다
    return limit                                      # 급증 기준을 리턴한다


def pick_spike_minutes(counts, limit):                # 분마다 요청 수와 급증 기준을 받는 함수
    """요청 수가 급증 기준 이상인 분만 골라 리턴한다.
    알림을 보낼 분을 가릴 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. counts 가 limit 이상인지 비교한 결과(>=)를 is_spike 에 담는다
    # 6. counts 에서 is_spike 가 True 인 것만 골라 spike_minutes 에 담는다 (counts[is_spike])
    return spike_minutes                              # 요청이 급증한 분과 요청 수를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 미리 채운 두 줄은 동작 두 개를 점으로 이은 한 줄입니다. 왼쪽부터 차례로 읽습니다. `web_events.groupby("minute").size()` 는 ① minute 이 같은 행끼리 그룹을 만들고 ② 그룹마다 행 수를 세고, `baseline["requests_per_minute"].mean()` 은 ① 분당 요청 수 열을 꺼내 ② 평균을 구합니다.
- 번호 주석이 연달아 붙어 있어도(예: 5 · 6번), 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `NameError: name 'minutes' is not defined` 오류가 납니다. 1번을 아직 안 써서 `minutes` 가 없기 때문입니다.

**`day03_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `.head(3)` 는 열의 처음 3개만 꺼냅니다.

```python
from traffic_detection import load_events, add_minute_column, count_web_per_minute, make_traffic_limit, pick_spike_minutes, EVENTS_PATH, TRAFFIC_PATH, SPIKE_MULTIPLE  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                                    # 이벤트 파일을 표로 읽는다
events = add_minute_column(events)                                                   # 시각에서 초를 버린 minute 열을 붙인다
times = events["time"]                                                               # time 열만 꺼낸다
minutes = events["minute"]                                                           # minute 열만 꺼낸다
first_times = times.head(3)                                                          # 시각의 처음 3개만 꺼낸다
first_minutes = minutes.head(3)                                                      # 분의 처음 3개만 꺼낸다
print("--- 단계 1: time 열과 minute 열의 처음 3개 비교")                             # 단계 1 시작을 알리는 줄
print(first_times)                                                                   # 처음 3개의 시각을 출력한다
print(first_minutes)                                                                 # 처음 3개의 분을 출력한다

counts = count_web_per_minute(events)                                                # 웹 서버 요청을 분마다 센다
print("--- 단계 2: 웹 서버의 분당 요청 수")                                          # 단계 2 시작을 알리는 줄
print(counts)                                                                        # 분마다 요청 수를 출력한다

limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)                             # 지난 7일 평균으로 급증 기준을 정한다
print("--- 단계 3: 급증 기준(평소 평균의", SPIKE_MULTIPLE, "배)", limit, "번 이상")  # 단계 3 시작을 알리는 줄과 급증 기준

spike_minutes = pick_spike_minutes(counts, limit)                                    # 기준 이상인 분만 고른다
print("--- 단계 4: 요청이 급증한 분")                                                # 단계 4 시작을 알리는 줄
print(spike_minutes)                                                                 # 요청이 급증한 분과 요청 수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `traffic_detection.py` · `day03_5-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `traffic_detection.py` 에서 직접 쓰는 곳 여섯 군데를 씁니다. 위 판다스 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day03_5-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_5-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 네 단계입니다. `--- 단계` 제목 줄은 세지 않습니다. 단계 1은 시각 4줄과 분 4줄(각각 마지막은 `Name:` 줄), 단계 2는 16줄(`minute` 줄 · 분마다 14줄 · `dtype:` 줄), 단계 3은 제목 줄에 숫자가 함께 나오고, 단계 4는 3줄(`minute` 줄 · 급증한 분 한 줄 · `dtype:` 줄)입니다. (나) · (다)에서 이벤트를 찾을 때는 VS Code 로 `normalized_events.json` 을 열고 `Ctrl + F`(맥북은 `Cmd + F`)로 `09:12` 또는 `09:20` 을 검색하고, `source` 가 `web` 인 줄만 셉니다. 이벤트 하나의 키는 `time · source · user · ip · action · result` 입니다.
5. **[보고서]** `day03_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 급증 기준과 요청이 급증한 분(시각과 요청 수)을 적어 주세요.
   - (나) 🔍 `normalized_events.json` 에서 `time` 이 `2026-11-02 09:12` 로 시작하는 웹 서버(`source` 가 `web`) 줄을 찾아, ① 요청을 보낸 IP 주소와 ② 행동(`action`)별 횟수를 적어 주세요. 그리고 ③ 이 급증을 공격이라고 확정할 수 있는지 이유와 함께 적어 주세요.
   - (다) 🔍 09:20 에도 웹 서버 요청이 3개 있었지만 급증으로 탐지되지 않았습니다. ① 3개를 급증 기준과 비교해 왜 탐지되지 않았는지 적고, ② `normalized_events.json` 에서 09:20 의 `web` 줄 3개가 어떤 요청(IP 주소 · 행동 · 결과)인지 적고, ③ 요청 수만 보는 급증 규칙이 이 요청들을 놓치는 이유를 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 초를 버려 분으로 | `minutes = times.dt.floor("min")` → `events["minute"] = minutes` |
| 웹 서버 이벤트만 | `is_web = events["source"] == "web"` → `web_events = events[is_web]` |
| 급증 기준 | `limit = average * multiple` (평균 2.0 × 3 = 6.0) |
| 기준 이상인 분 | `is_spike = counts >= limit` → `spike_minutes = counts[is_spike]` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 알림을 한 파일로 모으기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「오전에 로그인 실패 알림 1건, 오후에 트래픽 급증 알림 1건이 나왔는데 형식이 달라서 담당자가 따로따로 처리해야 합니다.
>
> 두 알림을 `alerts.json` 한 파일에 같은 모양으로 모아 주세요. 알림마다 종류 · 대상 · 횟수 · 메모를 넣어 주세요. 공격으로 확정된 것은 아니니 처리 상태는 모두 「확인 필요」로 해 주세요.」
> - **왜 중요한가**: <mark>알림 형식이 종류마다 다르면 담당자가 하나씩 해석해야 합니다.</mark> 형식이 같으면 사람도 자동 대응 도구도 같은 방법으로 처리할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. SIEM(심, 보안 로그를 모아 탐지 · 알림하는 시스템)의 네 단계는 **수집 → 정규화 → 탐지 → 알림**입니다. 오늘 알림으로 모으는 탐지 결과는 오전의 로그인 실패 규칙과 오후의 트래픽 급증 규칙, 두 가지입니다. 이제 마지막 단계인 알림을 만듭니다.
2. 두 규칙의 결과는 모양이 다릅니다.
   - 로그인 실패 규칙은 「주소와 횟수」(`203.0.113.50` 이 5번)를 냅니다.
   - 트래픽 급증 규칙은 「분과 요청 수」(`09:12` 에 9개)를 냅니다.
3. 알림은 **종류 · 대상 · 횟수 · 메모 · 처리 상태**를 같은 키로 담아야 한 파일에 모을 수 있습니다.

### 📖 6.1 알림 한 건의 모양과 지킬 점 두 가지

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

알림 한 건은 딕셔너리 하나이고, 키 다섯 개를 가집니다.

| 키 | 뜻 | 로그인 실패 알림 | 트래픽 급증 알림 |
|---|---|---|---|
| `type` | 알림의 종류 | 비정상 로그인 | 트래픽 급증 |
| `target` | 무엇에 대한 알림인가 | `203.0.113.50`(주소) | `2026-11-02 09:12:00`(분) |
| `count` | 몇 번이었나 | 5 | 9 |
| `note` | 담당자에게 보일 메모 | 로그인 실패가 기준 이상 | 요청이 평소의 3배 이상 |
| `status` | 처리 상태 | 확인 필요 | 확인 필요 |

처리 상태는 담당자가 조사하면서 바꿉니다. 예를 들어 「확인 필요」 → 「조사 중」 → 「조사 완료」 순서로 바뀝니다.

알림을 다룰 때 지킬 점이 둘 있습니다.

| 지킬 점 | 뜻 | 이 문서에서 |
|---|---|---|
| 알림 있음 ≠ 공격 확정 | 알림은 「먼저 살펴볼 곳」일 뿐이고, 정상적인 일이 기준 이상이 될 수도 있습니다 | `status` 를 모두 「확인 필요」로 둠 |
| 알림 없음 ≠ 안전 | 알림이 없는 것은 규칙에 해당하지 않았다는 뜻일 뿐, 아무 일도 없었다는 뜻이 아닙니다 | 규칙에 해당하지 않으면 알림이 나지 않음 |

**🐼 판다스 문법 상자 — 인덱스와 값을 한 쌍씩 꺼내기**

**<mark>`결과.items()`</mark> 는 판다스로 센 결과(시리즈, Series: 인덱스와 값이 한 줄씩 있는 데이터)에서 「인덱스, 값」을 한 쌍씩 꺼냅니다. `for 인덱스, 값 in 결과.items():` 로 반복합니다**

`value_counts()` 나 `groupby().size()` 로 센 결과는 왼쪽이 인덱스(index)이고 오른쪽이 값입니다. 딕셔너리의 `.items()` 와 같은 모양으로, 한 줄이 한 쌍이 됩니다.

| 센 결과(`counts`) | 반복에서 꺼내는 쌍 |
|---|---|
| web 28 | `source` 는 `"web"`, `count` 는 28 |
| server 15 | `source` 는 `"server"`, `count` 는 15 |
| saas 14 | `source` 는 `"saas"`, `count` 는 14 |

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

counts = events["source"].value_counts()         # source 열을 꺼내(["source"]) 바로 값별 개수를 센다(value_counts) — 인덱스(web · server · saas)와 개수

for source, count in counts.items():             # 인덱스와 개수를 한 쌍씩 꺼낸다
    print(source, count)                         # 인덱스와 개수를 출력한다
```

실행 결과:

```
web 28
server 15
saas 14
```

- 읽는 법: 출력 세 줄이 센 결과의 세 줄에 하나씩 대응합니다. 인덱스가 `source` 에, 값이 `count` 에 들어옵니다.
- 오늘 문제에서는 이 인덱스가 주소(`203.0.113.50`)나 분(`2026-11-02 09:12:00`)이고, 값이 횟수입니다.

**🐼 판다스 문법 상자 — 시각 값을 문자열로 바꾸기**

**<mark>`str(시각 값)`</mark> 은 판다스의 시각 값을 `"2026-11-02 09:01:00"` 같은 문자열로 바꿉니다. JSON 파일에는 문자열 · 숫자 · 리스트 · 딕셔너리만 쓸 수 있어서, 시각 값은 문자열로 바꿔야 합니다**

분 단위로 맞춘 `minutes` 는 시각 값입니다. 알림의 `target` 에 넣어 JSON 으로 저장하려면 먼저 문자열로 바꿉니다.

| 이름 | 값 | 종류 | JSON 에 쓸 수 있나 |
|---|---|---|---|
| `first_minute` | 2026-11-02 09:01:00 | 판다스 시각 값 | 쓸 수 없음 |
| `text` (`str(first_minute)`) | `"2026-11-02 09:01:00"` | 문자열 | 쓸 수 있음 |

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

times = pd.to_datetime(events["time"])           # 문자열 시각을 시각 값으로 바꾼다
minutes = times.dt.floor("min")                  # 시각에서 초를 버린다
first_minute = minutes[1]                        # 1번 행의 분을 꺼낸다 — 판다스 시각 값이다

text = str(first_minute)                         # 시각 값을 문자열로 바꾼다
message = text + " 에 이벤트가 있었음"           # 문자열이라 글을 이어 붙일 수 있다
print(message)                                   # 이어 붙인 글을 출력한다
```

실행 결과:

```
2026-11-02 09:01:00 에 이벤트가 있었음
```

- 읽는 법: `str()` 을 거치면 문자열이 되어 `+` 로 글을 이어 붙일 수 있습니다. 시각 값은 문자열이 아니라서 `+` 로 이어 붙이면 오류가 나고, JSON 에도 쓸 수 없습니다.
- 두 리스트를 하나로 이을 때는 `+` 를 씁니다: `[1, 2] + [3]` 은 `[1, 2, 3]` 입니다. 실행 파일이 로그인 실패 알림 리스트와 트래픽 급증 알림 리스트를 이어 붙일 때 씁니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `make_alert` | 종류 · 대상 · 횟수 · 메모 | 알림 한 건(딕셔너리) |
| `make_login_alerts` | 알림 대상 주소와 횟수 | 로그인 실패 알림 리스트 |
| `make_traffic_alerts` | 요청이 급증한 분과 요청 수 | 트래픽 급증 알림 리스트 |
| `save_alerts` | 알림 리스트와 파일 경로 | 저장한 알림 건수(파일에도 저장) |

- **직접 쓰는 곳은 네 함수**(번호 1 ~ 6)입니다.
  - `make_alert`(1번): 키 다섯 개를 딕셔너리로 만듭니다.
  - `make_login_alerts`(2번): 알림 한 건을 만듭니다. 반복문과 메모 문장은 미리 채웠습니다.
  - `make_traffic_alerts`(3 · 4번): 시각 값을 문자열로 바꾸고 알림 한 건을 만듭니다.
  - `save_alerts`(5 · 6번): 파일을 쓰기 위해 열고(5번), 알림 리스트를 JSON 파일에 저장합니다(6번). 저장한 건수를 세어 리턴하는 줄은 미리 채웠습니다. JSON 은 문자열과 숫자, 리스트, 딕셔너리를 담는 텍스트 파일 형식입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 로그인 실패 알림과 트래픽 급증 알림을 alerts.json 한 파일로 모으기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 오전 로그인 실패 결과와 오후 트래픽 급증 결과가 형식이 달라서, 담당자가 하나씩 열어 확인해야 합니다.
- **그래서 만드는 것**: `alerts.py` 입니다.
  - 알림 한 건을 종류 · 대상 · 횟수 · 메모 · 처리 상태 키 다섯 개로 만듭니다.
  - 두 종류의 알림을 같은 모양으로 만듭니다.
  - 알림을 리스트로 모아 `alerts.json` 에 저장합니다.
- **실행하면**: 단계 1: 로그인 실패 알림 건수, 단계 2: 트래픽 급증 알림 건수, 단계 3: 저장한 건수, 단계 4: 저장된 알림이 한 건씩 나옵니다.
- **현업에서는**: 알림 형식이 같으면 규칙이 늘어도 메신저 · 티켓 · 자동 대응 도구에 같은 방법으로 보낼 수 있습니다. 담당자는 「확인 필요」인 알림부터 확인합니다.

**🎯 할 일**

1. `alerts.py` · `day03_6-1_run.py` 두 파일을 만들고, `alerts.py` 의 네 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>알림 건수</mark>(단계 1 ~ 3)와 <mark>저장된 알림</mark>(단계 4)을 확인하고, 새로 생긴 `alerts.json` 을 VS Code 에서 열어 봅니다.

**`alerts.py`**

```python
import json                                                                             # 알림을 JSON 파일로 쓰기 위해 json 을 불러온다

ALERTS_PATH = "alerts.json"                                                             # 알림을 모아 저장할 파일 이름


def make_alert(alert_type, target, count, note):                                        # 종류 · 대상 · 횟수 · 메모를 받는 함수
    """알림 한 건을 딕셔너리로 만든다.
    알림마다 같은 모양으로 담아 한 파일에 모을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 딕셔너리를 alert 에 담는다: 키 "type" 에는 alert_type, "target" 에는 target, "count" 에는 count, "note" 에는 note, "status" 에는 "확인 필요" 를 넣는다 (여러 줄로 나눠 써도 된다)
    return alert                                                                        # 알림 한 건을 리턴한다


def make_login_alerts(alert_ips):                                                       # 알림 대상 주소와 횟수를 받는 함수
    """로그인 실패 알림 대상 주소마다 「비정상 로그인」 알림을 하나씩 만든다.
    3교시에서 추출한 주소를 알림 형식으로 바꿀 때 쓴다.
    """
    alerts = []                                                                         # 알림을 담을 빈 리스트
    for ip_address, count in alert_ips.items():                                         # 주소와 횟수를 한 쌍씩 꺼낸다
        note = "로그인 실패가 기준 이상 — 공격 확정이 아니라 먼저 살펴볼 곳"            # 담당자에게 보일 메모
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. make_alert 에 "비정상 로그인" · ip_address · count · note 를 전달해 alert 에 담는다
        alerts.append(alert)                                                            # 알림을 리스트에 추가한다
    return alerts                                                                       # 로그인 실패 알림 리스트를 리턴한다


def make_traffic_alerts(spike_minutes):                                                 # 요청이 급증한 분과 요청 수를 받는 함수
    """요청이 급증한 분마다 「트래픽 급증」 알림을 하나씩 만든다.
    5교시에서 추출한 분을 알림 형식으로 바꿀 때 쓴다.
    """
    alerts = []                                                                         # 알림을 담을 빈 리스트
    for minute, count in spike_minutes.items():                                         # 분과 요청 수를 한 쌍씩 꺼낸다
        note = "요청이 평소의 3배 이상으로 늘어남 — 공격 확정이 아니라 먼저 살펴볼 곳"  # 담당자에게 보일 메모
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. str(minute) 로 시각 값을 문자열로 바꿔 target 에 담는다
        # 4. make_alert 에 "트래픽 급증" · target · count · note 를 전달해 alert 에 담는다
        alerts.append(alert)                                                            # 알림을 리스트에 추가한다
    return alerts                                                                       # 트래픽 급증 알림 리스트를 리턴한다


def save_alerts(alerts, path):                                                          # 알림 리스트와 파일 경로를 받는 함수
    """알림 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다.
    담당자와 다른 프로그램이 같은 파일로 알림을 처리하게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. path 파일을 쓰기 모드("w")로 열고 file 변수로 쓴다 (with open(path, "w", encoding="utf-8") as file:)
    # 6. json.dump 에 alerts, file 을 이 순서로 전달하고, 뒤에 ensure_ascii=False, indent=2 를 붙여 쓴다 (한글은 그대로, 줄을 나눠 저장)
    saved_count = len(alerts)                                                           # 저장한 알림이 몇 건인지 센다
    return saved_count                                                                  # 저장한 건수를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1번은 함수 안이라 앞에 공백 4개이고, 2 ~ 4번은 `for` 안이라 8개이며, 5번은 함수 안이라 4개, 6번은 `with` 안이라 8개입니다.
- 번호 주석이 연달아 붙어 있어도(예: 3 · 4번), 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `NameError: name 'alert' is not defined` 오류가 납니다. 2번을 아직 안 써서 `alert` 가 만들어지지 않았기 때문입니다.

**`day03_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 오전 `login_detection.py` 와 5교시 `traffic_detection.py` 의 함수를 불러와 오늘의 알림을 만듭니다. `load_events` 는 두 파일에 같은 이름으로 있어서, 여기서는 오전 파일 것 하나만 불러옵니다.

```python
import json                                                                          # 저장한 파일을 다시 읽기 위해 json 을 불러온다
from login_detection import load_events, pick_login_failures, count_by_ip, pick_alert_ips, EVENTS_PATH, LOGIN_LIMIT  # 오전 3교시에 만든 함수를 불러온다
from traffic_detection import add_minute_column, count_web_per_minute, make_traffic_limit, pick_spike_minutes, TRAFFIC_PATH, SPIKE_MULTIPLE  # 5교시에 만든 함수를 불러온다
from alerts import make_login_alerts, make_traffic_alerts, save_alerts, ALERTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                                    # 이벤트 파일을 표로 읽는다
login_failures = pick_login_failures(events)                                         # 로그인 실패 이벤트만 골라낸다
login_counts = count_by_ip(login_failures)                                           # 주소별로 실패 횟수를 센다
alert_ips = pick_alert_ips(login_counts, LOGIN_LIMIT)                                # 알림 기준 이상인 주소만 고른다
login_alerts = make_login_alerts(alert_ips)                                          # 주소마다 알림 한 건을 만든다
login_alert_count = len(login_alerts)                                                # 로그인 실패 알림이 몇 건인지 센다
print("--- 단계 1: 로그인 실패 알림", login_alert_count, "건")                       # 단계 1 시작을 알리는 줄과 건수

events = add_minute_column(events)                                                   # 시각에서 초를 버린 minute 열을 붙인다
minute_counts = count_web_per_minute(events)                                         # 웹 서버 요청을 분마다 센다
limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)                             # 급증 기준을 정한다
spike_minutes = pick_spike_minutes(minute_counts, limit)                             # 요청이 급증한 분만 고른다
traffic_alerts = make_traffic_alerts(spike_minutes)                                  # 분마다 알림 한 건을 만든다
traffic_alert_count = len(traffic_alerts)                                            # 트래픽 급증 알림이 몇 건인지 센다
print("--- 단계 2: 트래픽 급증 알림", traffic_alert_count, "건")                     # 단계 2 시작을 알리는 줄과 건수

all_alerts = login_alerts + traffic_alerts                                           # 두 리스트를 이어 붙여 알림 하나의 리스트로 모은다
saved_count = save_alerts(all_alerts, ALERTS_PATH)                                   # 모은 알림을 파일에 저장하고 저장한 건수를 받는다
print("--- 단계 3:", ALERTS_PATH, "에 알림", saved_count, "건 저장")                 # 단계 3 시작을 알리는 줄과 건수

with open(ALERTS_PATH, encoding="utf-8") as file:                                    # 저장한 파일을 읽기 모드로 연다
    saved_alerts = json.load(file)                                                   # JSON 을 파이썬 리스트로 읽는다
print("--- 단계 4: 저장된 알림")                                                     # 단계 4 시작을 알리는 줄
for alert in saved_alerts:                                                           # 알림을 하나씩 꺼낸다
    print(alert)                                                                     # 알림 한 건을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `alerts.py` · `day03_6-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `alerts.py` 에서 직접 쓰는 곳 여섯 군데를 씁니다. 위 알림 한 건의 모양 표와 판다스 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day03_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_6-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 네 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1 ~ 3은 제목 줄에 숫자가 함께 나오고, 단계 4는 알림 한 건이 한 줄씩 2줄입니다.
5. **[VS Code]** 새로 생긴 `alerts.json` 을 열어 알림 두 건이 보이는지 확인합니다.
6. **[보고서]** `day03_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, `alerts.json` 의 내용도 붙여 넣은 뒤 알림이 모두 몇 건인지 적어 주세요.
   - (나) 🔍 ① 203.0.113.50 이 `normalized_events.json` 의 `source` 가 `web` 인 줄에 몇 시에 나오는지 찾고, ② 그 시각이 급증 알림의 분(09:12)과 같은지 비교하고, ③ 두 알림이 같은 일과 관련이 있는지 적고, 담당자가 두 건을 한 건으로 합쳐 조사할지 따로 조사할지 고른 이유를 적어 주세요.
   - (다) 🔍 203.0.113.50 알림을 조사해 보니 직원이 비밀번호를 잊어 반복해서 입력한 것이었습니다. ① `status` 를 어떤 값으로 바꿀지(안내 문서 6.1 의 처리 상태 순서를 참고), ② `note` 에 무엇을 더 적을지, ③ 알림을 지우지 않고 남겨 두는 편이 좋은 이유를 적어 주세요. 코드는 고치지 않고 글로만 적습니다.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 알림 한 건 | `alert = {"type": alert_type, "target": target, "count": count, "note": note, "status": "확인 필요"}` |
| 센 결과를 한 쌍씩 | `for ip_address, count in alert_ips.items():` (미리 채움) |
| 시각 값을 문자열로 | `target = str(minute)` |
| 파일에 저장 | `with open(path, "w", encoding="utf-8") as file:` → `json.dump(alerts, file, ensure_ascii=False, indent=2)` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다. 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, `pwd` 로 위치를 먼저 확인한 뒤 결과가 `anomaly_detection` 으로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: 팀장이 「오늘 만든 탐지 코드와 알림 파일을 저장소에 남겨 달라」고 합니다.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `anomaly_detection` 폴더에 오늘 오전과 오후에 만든 파일이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `anomaly_detection` 폴더에서 확인합니다. `day03_pm_report.md` 의 5 · 6교시 칸에서 `답:` 뒤와 코드 상자가 비어 있는 질문이 없는지도 봅니다(마무리 (가)는 3번에서 채웁니다).
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 의 결과가 `anomaly_detection` 으로 끝나야 합니다. 파일은 `baseline.py` · `login_detection.py` · `classify.py` · `traffic_detection.py` · `alerts.py` · `day03_2-1_run.py` ~ `day03_6-1_run.py` 다섯 개 · `normalized_events.json` · `baseline_logins.csv` · `baseline_traffic.csv` · `alerts.json` 과 안내 · 보고서 네 파일(`day03_am_baseline_login.md` · `day03_am_report.md` · `day03_pm_traffic_alerts.md` · `day03_pm_report.md`)이 보여야 합니다. `__pycache__` 폴더는 파이썬이 만든 임시 폴더라 있어도 됩니다. 빠진 파일이 있으면 그 문제를 다시 풀어 만들고, `pwd` 가 `security-agent-toolkit` 로 나오면 `cd anomaly_detection` 을 먼저 칩니다.
1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 결과가 `…/security-agent-toolkit` 으로 끝나야 합니다.
   ```bash
   cd ..
   pwd
   ```
   - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 있는 폴더의 위치 확인
   - 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. 빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 말고, 아래 안내대로 `.gitignore` 를 고친 뒤 `git status` 를 다시 봅니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 올릴 파일의 상태를 봄
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `anomaly_detection/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - 앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다. 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add anomaly detection day 3 baseline and alerts"
   git push
   ```
   - 명령 풀이: `git add .` 바뀐 파일을 올릴 대상에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림
   - `git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다. `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `anomaly_detection` 폴더를 열고, VS Code 왼쪽 목록의 `anomaly_detection` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. `__pycache__` 폴더는 없어도 됩니다.
   - 빠진 이름이 있으면 VS Code 왼쪽 목록의 `anomaly_detection` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `anomaly_detection` 안으로 옮기고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `anomaly_detection` 폴더와 파일이 있는지 확인 |

---

## 오늘 오후 마무리

| 확인 | 문제 |
|---|---|
| 웹 서버 요청을 분마다 세고 평소 평균의 3배 이상으로 늘어난 분을 찾았다 | 오후 5-1 |
| 로그인 실패 알림과 트래픽 급증 알림을 같은 모양으로 만들어 `alerts.json` 에 모았다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

다음 수업은 11/5(목)입니다. 오늘 만든 알림 형식에 SaaS 이상 사용과 악성 행위 징후 같은 유형을 더해 갑니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_5-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_5-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 네 함수입니다.

① `add_minute_column` 안

```python
    minutes = times.dt.floor("min")  # 시각에서 초를 버린다 (09:12:03 → 09:12:00)
```

② `count_web_per_minute` 안

```python
    is_web = events["source"] == "web"  # 행마다 웹 서버 이벤트인지 비교해 True 또는 False 를 만든다
    web_events = events[is_web]         # True 인 행만 골라 웹 서버 이벤트의 표를 만든다
```

③ `make_traffic_limit` 안

```python
    limit = average * multiple  # 평소 평균에 3 을 곱한 값이 급증 기준이다
```

④ `pick_spike_minutes` 안

```python
    is_spike = counts >= limit        # 분마다 「기준 이상인가?」를 비교해 True 또는 False 를 만든다
    spike_minutes = counts[is_spike]  # True 인 분만 남긴다
```

**결과**

- (가) 출력은 다음과 같고, 급증 기준은 <mark>**6.0번 이상**</mark>, 요청이 급증한 분은 <mark>**09:12(요청 9개)**</mark> 한 분입니다.

```
--- 단계 1: time 열과 minute 열의 처음 3개 비교
0    2026-11-02 02:14:08
1    2026-11-02 09:01:05
2    2026-11-02 09:01:06
Name: time, dtype: object
0   2026-11-02 02:14:00
1   2026-11-02 09:01:00
2   2026-11-02 09:01:00
Name: minute, dtype: datetime64[ns]
--- 단계 2: 웹 서버의 분당 요청 수
minute
2026-11-02 09:01:00    2
2026-11-02 09:03:00    2
2026-11-02 09:04:00    1
2026-11-02 09:05:00    2
2026-11-02 09:12:00    9
2026-11-02 09:20:00    3
2026-11-02 09:22:00    1
2026-11-02 09:25:00    1
2026-11-02 09:26:00    1
2026-11-02 09:28:00    2
2026-11-02 09:31:00    1
2026-11-02 09:33:00    1
2026-11-02 09:35:00    1
2026-11-02 09:36:00    1
dtype: int64
--- 단계 3: 급증 기준(평소 평균의 3 배) 6.0 번 이상
--- 단계 4: 요청이 급증한 분
minute
2026-11-02 09:12:00    9
dtype: int64
```

- (나) 09:12 에 들어온 요청 9개는 모두 **203.0.113.50** 이 보낸 것입니다. 이 분의 이벤트는 다음과 같습니다.

| 시각 | 주소 | 행동 | 결과 |
|---|---|---|---|
| 09:12:01 | 203.0.113.50 | `GET /login` | 성공 |
| 09:12:03 | 203.0.113.50 | `POST /login` | 실패 |
| 09:12:06 | 203.0.113.50 | `POST /login` | 실패 |
| 09:12:09 | 203.0.113.50 | `POST /login` | 실패 |
| 09:12:12 | 203.0.113.50 | `POST /login` | 실패 |
| 09:12:15 | 203.0.113.50 | `POST /login` | 실패 |
| 09:12:18 | 203.0.113.50 | `POST /login` | 성공 |
| 09:12:25 | 203.0.113.50 | `GET /admin` | 실패 |
| 09:12:27 | 203.0.113.50 | `GET /admin/users` | 실패 |

  - 로그인 화면을 열고(`GET /login`), 로그인 정보를 6번 보냈고(`POST /login`, 5번 실패 뒤 1번 성공), 관리자 경로를 2번 요청했습니다(`/admin`, `/admin/users`).
  - 이 급증이 공격이라고 확정할 수는 없습니다. 하지만 오전 3교시에서 로그인 실패 5번으로 알림 대상이 된 주소와 같은 IP 주소입니다. 한 주소가 1분도 안 되는 사이에 로그인을 반복하다 성공하고 관리자 경로를 요청한 것은 먼저 살펴볼 일입니다.
  - 확정하려면 이 주소가 회사 직원의 주소인지, 성공한 계정이 누구인지 판정 서버 · SaaS 로그와 시각을 맞춰 봐야 합니다.
- (다) 09:20 의 요청 3개는 급증 기준(6.0번 이상)보다 적어서 탐지되지 않았습니다.
  - 그 3개는 모두 198.51.100.90 이 09:20:10 ~ 09:20:12 에 보낸 `GET /.env` · `GET /wp-login.php` · `GET /phpmyadmin` 이고 모두 실패했습니다. 서로 다른 경로를 차례로 요청한 모양입니다.
  - 급증 규칙은 요청의 **수**만 보기 때문에, 수가 적으면 요청의 내용과 상관없이 알리지 못합니다. 이런 경로 스캔(취약한 경로를 하나씩 찾아보는 시도)은 11/5(목)에 다른 규칙으로 찾습니다.

**왜**

- <mark>「짧은 시간에 늘어난 요청」은 시간을 일정한 구간(여기서는 1분)으로 나눠 구간마다 세어야 보입니다.</mark> 구간 길이를 정하는 일이 초를 버리는 일입니다.

**자주 틀리는 곳**

- `times.dt.floor("min")` 에서 `.dt` 를 빠뜨리고 `times.floor("min")` 으로 쓰면 오류가 납니다.
  - 실행하면 다음 오류가 납니다(<mark>`'Series' object has no attribute 'floor'`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day03_5-1_run.py", line 4, in <module>
    events = add_minute_column(events)  # 시각에서 초를 버린 minute 열을 붙인다
  File "…/anomaly_detection/traffic_detection.py", line 23, in add_minute_column
    minutes = times.floor("min")  # .dt 를 빼먹었다
AttributeError: 'Series' object has no attribute 'floor'
```

  - 줄 번호는 사람마다 다릅니다.
- 요청이 하나도 없던 분은 결과에 나오지 않습니다. 분당 요청 수 14줄은 요청이 있던 분만 센 것입니다.

**관제에서는**

- 급증 기준은 요일 · 시간대마다 평소가 다르므로 시간대별 평소 평균을 따로 둡니다. 이 문서의 `baseline_traffic.csv`(지난 7일, 오전 9시대)는 연습용 하나뿐입니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_6-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 네 함수입니다.

① `make_alert` 안

```python
    alert = {"type": alert_type, "target": target, "count": count, "note": note, "status": "확인 필요"}  # 알림 한 건의 키 다섯 개
```

② `make_login_alerts` 안

```python
        alert = make_alert("비정상 로그인", ip_address, count, note)  # 로그인 실패 알림 한 건을 만든다
```

③ `make_traffic_alerts` 안

```python
        target = str(minute)                                    # 시각 값을 문자열로 바꾼다 — JSON 에는 시각 값을 그대로 쓸 수 없다
        alert = make_alert("트래픽 급증", target, count, note)  # 트래픽 급증 알림 한 건을 만든다
```

④ `save_alerts` 안

```python
    with open(path, "w", encoding="utf-8") as file:            # 파일을 쓰기 위해 열고 file 변수로 쓴다
        json.dump(alerts, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 들여쓰기를 해서 파일에 쓴다
```

**결과**

- (가) 출력은 다음과 같고, 알림은 모두 <mark>**2건**</mark>(로그인 실패 1건 + 트래픽 급증 1건)입니다.

```
--- 단계 1: 로그인 실패 알림 1 건
--- 단계 2: 트래픽 급증 알림 1 건
--- 단계 3: alerts.json 에 알림 2 건 저장
--- 단계 4: 저장된 알림
{'type': '비정상 로그인', 'target': '203.0.113.50', 'count': 5, 'note': '로그인 실패가 기준 이상 — 공격 확정이 아니라 먼저 살펴볼 곳', 'status': '확인 필요'}
{'type': '트래픽 급증', 'target': '2026-11-02 09:12:00', 'count': 9, 'note': '요청이 평소의 3배 이상으로 늘어남 — 공격 확정이 아니라 먼저 살펴볼 곳', 'status': '확인 필요'}
```

  - `alerts.json` 의 내용은 다음과 같습니다.

```
[
  {
    "type": "비정상 로그인",
    "target": "203.0.113.50",
    "count": 5,
    "note": "로그인 실패가 기준 이상 — 공격 확정이 아니라 먼저 살펴볼 곳",
    "status": "확인 필요"
  },
  {
    "type": "트래픽 급증",
    "target": "2026-11-02 09:12:00",
    "count": 9,
    "note": "요청이 평소의 3배 이상으로 늘어남 — 공격 확정이 아니라 먼저 살펴볼 곳",
    "status": "확인 필요"
  }
]
```

- (나) 두 알림은 같은 일과 관련이 있어 보입니다.
  - 겹치는 단서: 로그인 실패 알림의 주소 `203.0.113.50` 이 09:12:03 ~ 09:12:15 에 로그인(`POST /login`)을 5번 실패했고, 트래픽 급증 알림의 분 `09:12` 에 들어온 요청 9개도 모두 이 주소의 것입니다.
  - 다루는 법: 알림 두 건을 따로 처리하지 않고 「203.0.113.50 이 09:12 에 로그인을 반복한 한 사건」으로 통합해 한 번에 조사합니다. 성공한 로그인 계정과 뒤이은 관리자 경로 요청까지 함께 봅니다.
- (다) `status` 를 「조사 완료」로 바꾸고, `note` 에 「직원이 비밀번호를 잊어 반복 입력함」과 확인한 사람 · 날짜를 적습니다.
  - 알림을 지우지 않고 남겨 두면, 같은 주소에서 다시 알림이 났을 때 이전 조사 결과를 보고 빨리 판단할 수 있습니다. 같은 일이 자주 생기면 알림 기준을 고칠 근거도 됩니다.
  - 알림이 있어도 공격으로 확정된 것이 아니므로 조사 결과가 정상이든 공격이든 처리 상태는 「조사 완료」이고, 정상인지 대응이 필요한지는 `note` 에 적습니다.

**왜**

- <mark>알림의 모양을 하나로 맞추면 탐지 규칙이 늘어도 담당자의 처리 방법과 알림을 보내는 코드가 그대로입니다.</mark> `make_login_alerts` · `make_traffic_alerts` 처럼 규칙마다 알림을 만드는 함수 하나만 더 만들면 됩니다.

**자주 틀리는 곳**

- `target = str(minute)` 대신 `target = minute` 으로 두면 `json.dump` 에서 오류가 납니다. 판다스의 시각 값은 JSON 에 쓸 수 없습니다.
  - 실행하면 다음 오류가 납니다(<mark>`Object of type Timestamp is not JSON serializable`</mark> 이 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day03_6-1_run.py", line 23, in <module>
    saved_count = save_alerts(all_alerts, ALERTS_PATH)  # 모은 알림을 파일에 저장하고 저장한 건수를 받는다
  File "…/anomaly_detection/alerts.py", line 54, in save_alerts
    json.dump(alerts, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 들여쓰기를 해서 파일에 쓴다
TypeError: Object of type Timestamp is not JSON serializable
```

  - 줄 번호는 사람마다 다릅니다.
- `json.dump` 에서 `ensure_ascii=False` 를 빼면 한글이 `\ube44\uc815\uc0c1` 같은 코드(「비정상」을 코드로 쓴 모양)로 저장됩니다. 오류는 나지 않지만 파일을 열어 보면 알림 내용을 알아볼 수 없습니다.
- `with` 줄 아래의 6번 코드는 공백 8개로 씁니다. 4개로 쓰면 `IndentationError` 오류가 납니다. `with` 줄 끝의 `:` 도 빠뜨리지 않습니다.

**관제에서는**

- 알림 파일에는 처리 상태 키(`status`)가 있어서, 담당자가 「확인 필요」 → 「조사 중」 → 「조사 완료」처럼 바꿔 가며 어디까지 봤는지 남깁니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
cd ..
pwd
git status
```
- 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 있는 폴더의 위치 확인 · `git status` 올릴 파일의 상태를 봄

`.env` 나 `.venv` 가 없는 것을 확인한 뒤에 아래를 칩니다.

```bash
git add .
git commit -m "Add anomaly detection day 3 baseline and alerts"
git push
```
- 명령 풀이: `git add .` 바뀐 파일을 올릴 대상에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림

**결과**

- (가) 한 예: 「`.env` · `.venv` 는 보이지 않았다」. 보였다면 `.gitignore` 에 `.env`(또는 `.venv`) 한 줄을 적고 저장한 뒤 `git status` 를 다시 쳤다고 적습니다.

**왜**

- <mark>올리기 전에 올라갈 파일을 확인해야 비밀 키가 섞이지 않습니다.</mark>

**자주 틀리는 곳**

- `.env` 가 보이는데 그대로 `git add .` 를 하는 실수가 가장 위험합니다.
  - `cd ..` 를 두 번 쳐서 `security-agent-toolkit` 바깥으로 나가는 경우도 있습니다. `pwd` 로 확인합니다.
