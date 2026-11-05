# 11/5(목) 오후 · 4과목 이상탐지 ④ — 서로 다른 로그를 한 사용자로 연결해 분석하기 · 위험 점수 매기기 — 실습

오전에는 판정 서버 · SaaS · 웹 로그에서 먼저 확인할 것을 따로 탐지했습니다. 오후에는 **같은 사용자의 서로 다른 로그에서 짧은 시간 안에 이벤트가 확인되는 사건**(함께 살펴볼 관련 기록)을 찾아 하나의 사건으로 연결하고(상관분석, correlation, 코렐레이션: 서로 다른 로그를 같은 기준으로 연결해 분석하는 것), 탐지된 규칙마다 **점수**를 매겨 high · mid · low 로 나눠 `day03_risk_scores.json` 한 파일에 저장합니다. 파일 이름의 `day03` 은 강의계획서가 정한 이름이라 그대로 씁니다.

- **5교시**: 웹 로그에는 사용자가 없어서 SaaS 성공 로그인의 IP 로 사용자를 찾고, 서버 · SaaS · 웹 로그를 한 표로 합쳐 사용자 · 시각 순으로 놓은 뒤 60분 안에 모인 사건을 찾습니다.
- **6교시**: 오전 탐지와 5교시 결과에서 탐지된 규칙을 모으고, 규칙마다 점수를 더해 등급과 이유를 파일로 저장합니다.

오늘은 오후 5 · 6교시이고, <mark>깃허브에 올리는 일은 6교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널 · git** 입니다.
- 코드 줄은 판다스로 쓰는 줄과 파이썬으로 쓰는 줄이 섞여 있습니다. 표를 합치고 정렬하고 합계를 내는 줄이 판다스이고, 판단 · 딕셔너리 · 문자열 연결이 파이썬입니다.
- 연결 기준(서로 다른 로그 2종류 이상 · 60분)과 점수 · 등급 기준(high 60 이상 · mid 35 이상)은 **고정**하고, <mark>값을 바꿔 가며 비교하지 않습니다</mark>.
- 샘플 이벤트의 날짜는 2026-11-02 입니다. 57개 중 웹 서버 28 · 판정 서버 15 · SaaS 14입니다.
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 화면의 값을 근거로 이유까지 서술합니다</mark>.
- 📎 **오늘 불러 쓰는 이전 파일**이 있습니다. 아래 표에서 <mark>`correlation.py` 만 오늘 5교시에 만들고, 나머지는 모두 오늘 오전에 만든 파일</mark>입니다.

| 파일 | 만든 곳 | 쓰는 곳 | 없거나 완성하지 못했을 때 |
|---|---|---|---|
| `normalized_events.json` · `rbac.py` · `config/users.json` · `config/roles.json` | 오전 안내(`day04_am_suspicious_logs.md`) 시작하기 6번 | 5 · 6교시 | 그 안내 시작하기 6번의 내용으로 파일을 만듭니다 |
| `access_detection.py` | 오전 2교시 문제 2-1 | 5 · 6교시가 불러옵니다 | 이 안내 맨 아래 「부록」의 완성본으로 파일을 만듭니다 |
| `saas_detection.py` | 오전 3교시 문제 3-1 | 5 · 6교시가 불러옵니다 | 이 안내 맨 아래 「부록」의 완성본으로 파일을 만듭니다 |
| `malicious_detection.py` | 오전 4교시 문제 4-1 | 5 · 6교시가 불러옵니다 | 이 안내 맨 아래 「부록」의 완성본으로 파일을 만듭니다 |
| `correlation.py` | 오늘 5교시 문제 5-1 | 6교시 `day04_6-1_run.py` 가 불러옵니다 | 이 안내 문제 5-1 의 코드 칸에 「정답 5-1」의 「채운 코드」를 넣어 완성합니다 |

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치와 오전 파일을 확인합니다(맥북은 `python3`). <mark>`pwd` 가 `…/anomaly_detection` 으로 끝나고, `ls` 결과에 위 표의 파일들이 보여야</mark> 합니다.
   ```bash
   cd anomaly_detection
   pwd
   ls
   ```
3. **오늘 받은 파일 두 개**(`day04_pm_correlation_risk.md`, `day04_pm_report.md`)를 <mark>`다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-05(목))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[터미널]** 오전 함수가 잘 불러와지는지 확인합니다. <mark>세 줄 모두 아무 오류도 나오지 않으면</mark> 됩니다. 오류가 나면 그 줄의 파일이 문제입니다.
   ```bash
   python -c "from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH"
   python -c "from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users"
   python -c "from malicious_detection import pick_web_failures, find_scan_ips"
   ```
   - `python -c "코드"` 는 파일을 만들지 않고 코드를 한 줄로 바로 실행합니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다.
- `No module named 'pandas'`: <mark>가상환경이 활성화되지 않은 터미널입니다</mark>. `security-agent-toolkit` 폴더에서 가상환경을 활성화한 뒤(`source .venv/Scripts/activate`, 맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 다르면 그 이름으로) `python -m pip install pandas` 를 칩니다.
- `ImportError` · `No module named 'access_detection'`: <mark>오전 파일이 없거나 함수 이름이 문서와 다른 것입니다</mark>. 위 표의 「없거나 완성하지 못했을 때」를 따릅니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 서로 다른 로그를 한 사용자로 연결해 분석하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「오전에 서버 · SaaS · 웹 로그를 각각 따로 탐지했더니 결과 목록이 세 개가 됐습니다. 목록을 번갈아 보다가 같은 사람 이름이 서버 결과에도, SaaS 결과에도 나오는 것을 봤습니다. 같은 사용자가 짧은 시간 안에 여러 로그에서 이상 징후를 보였다면 하나의 사건일 수 있습니다.
>
> 같은 사용자에게 서로 다른 로그의 이벤트가 짧은 시간 안에 모여 있으면 하나의 사건으로 연결해서 알려 주세요. 웹 로그에는 사용자 이름이 없고 IP 만 있으니, SaaS 에 로그인한 기록에서 IP 로 사용자를 찾아 연결해 주세요.」
> - **왜 중요한가**: <mark>로그 하나에서는 작은 이상 징후도 같은 사용자에게 짧은 시간 안에 여러 로그에서 겹치면 먼저 확인할 이유가 분명하지만, 아침과 저녁처럼 시간이 멀리 떨어진 기록까지 한 사건으로 보면 안 됩니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 서버 로그와 SaaS 로그에는 사용자(`user`)가 있고, 웹 로그에는 IP 만 있습니다. SaaS 의 <mark>**성공한 로그인**</mark>은 IP 와 사용자가 함께 있으므로 「IP → 사용자」 딕셔너리를 만들어 웹 로그의 IP 로 사용자를 찾습니다.
2. 세 로그를 표 하나로 합쳐 **사용자 순, 같은 사용자는 시각 순**으로 놓으면 <mark>사용자별 이벤트를 시각 순서로 확인할 수 있습니다.</mark>
3. 연결됐다고 보는 조건은 둘입니다. ① 서로 다른 로그(`source`)가 2종류 이상이다. ② 그 사용자의 첫 이벤트부터 마지막 이벤트까지가 60분 이내이다. <mark>하나만 맞으면 연결된 것으로 보지 않습니다.</mark>

### 📖 5.1 IP 로 사용자 채우기 · 표 잇기 · 두 열로 정렬하기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

SaaS 의 성공한 로그인에서 만든 「IP → 사용자」 딕셔너리는 이렇게 생깁니다(`make_ip_user_map` 이 만들며, 미리 채워져 있습니다).

| IP | 사용자 | 만들어진 곳 |
|---|---|---|
| 198.51.100.9 | seoyeon | 09:05 성공한 로그인 |
| 192.0.2.41 | junho | 09:30 성공한 로그인 |
| 198.51.100.77 | gaeun | 10:12 성공한 로그인 |
| 198.51.100.52 | jiwoo | 16:02 성공한 로그인 |
| 203.0.113.80 | seoyeon | 17:38 성공한 로그인 |

- 딕셔너리에는 <mark>**성공한 로그인**만</mark> 넣습니다. 02:14 에 jiwoo 가 203.0.113.80 으로 시도한 로그인은 실패였으므로 넣지 않고, 같은 IP 로 성공한 17:38 의 seoyeon 이 이 IP 의 사용자로 기록됩니다.
- 서버 로그는 실패 이벤트 **전체**(9개)를 씁니다. 먼저 확인할 이벤트만 고르면 어떤 사용자가 서버 로그에 나오는지가 오전 결과에 따라 달라지기 때문입니다.
- 웹 실패 이벤트의 IP 가 위 표에 있으면 그 사용자의 이벤트로 연결해 분석할 수 있고, <mark>딕셔너리에 IP 가 없으면 사용자를 확인할 수 없어 이번 연결에서 제외합니다.</mark>

**🐼 판다스 문법 상자 — 딕셔너리로 값을 바꾸기 `map`**

**<mark>`열.map(딕셔너리)`</mark> 은 열의 값을 딕셔너리에서 찾아, 짝지어진 값으로 바꿉니다. 딕셔너리에 없는 값은 `NaN`(연결할 값이 없다는 표시)이 됩니다**

11/3 오전에 배운 딕셔너리로 값 바꾸기를 열 전체에 한 번에 하는 것이 `map` 입니다. 아래에서는 웹 로그의 IP 를 사용자 이름으로 바꿉니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                    # 표에 넣을 내용(열 이름: 값들)
    "ip": ["203.0.113.80", "198.51.100.77", "192.0.2.15"],  # ip 열
    "action": ["GET /admin", "GET /admin", "GET /board"],   # action 열
}
df = pd.DataFrame(data)                                     # 내용으로 표(DataFrame)를 만든다
print(df)                                                   # 표를 출력한다
```

실행 결과:

```
              ip      action
0   203.0.113.80  GET /admin
1  198.51.100.77  GET /admin
2     192.0.2.15  GET /board
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
ip_user = {"203.0.113.80": "seoyeon", "198.51.100.77": "gaeun"}  # IP → 사용자 딕셔너리(세 번째 IP 는 없다)
users = df["ip"].map(ip_user)                                    # ip 열의 각 값을 딕셔너리에서 찾아 사용자 이름으로 바꾼다
print(users)                                                     # 바뀐 값을 출력한다
```

실행 결과:

```
0    seoyeon
1      gaeun
2        NaN
Name: ip, dtype: object
```

- 읽는 법: <mark style="background:#bde3ff">앞의 두 IP 는 딕셔너리에 있어서 `seoyeon` 과 `gaeun` 이 되고, 세 번째 IP 는 딕셔너리에 없어서 `NaN`</mark> 입니다. 맨 아래 `Name: ip, dtype: object` 줄은 몰라도 됩니다.

**🐼 판다스 문법 상자 — 표를 위아래로 이어 붙이기 `pd.concat`**

**<mark>`pd.concat([표1, 표2, …])`</mark> 는 열 이름이 같은 표 여러 개를 위아래로 이어 붙여 표 하나로 만듭니다. 표는 대괄호 `[ ]` 안의 리스트로 전달합니다**

아래에서는 판정 서버 로그 표와 SaaS 로그 표를 하나로 이어 붙입니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

server_data = {                                      # 판정 서버 로그에 넣을 내용
    "user": ["gaeun", "gaeun"],                      # user 열
    "action": ["ACCOUNT:CHANGE", "ACCOUNT:CHANGE"],  # action 열
}
server_logs = pd.DataFrame(server_data)              # 내용으로 표(DataFrame)를 만든다
print(server_logs)                                   # 판정 서버 표를 출력한다
```

실행 결과:

```
    user          action
0  gaeun  ACCOUNT:CHANGE
1  gaeun  ACCOUNT:CHANGE
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
saas_data = {                        # SaaS 로그에 넣을 내용 — 열 이름이 서버 표와 같다
    "user": ["gaeun"],               # user 열
    "action": ["login"],             # action 열
}
saas_logs = pd.DataFrame(saas_data)  # 내용으로 표(DataFrame)를 만든다
print(saas_logs)                     # SaaS 표를 출력한다
```

실행 결과:

```
    user action
0  gaeun  login
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
both = pd.concat([server_logs, saas_logs])  # 표 두 개를 위아래로 이어 붙여 표 하나로 만든다
print(both)                                 # 이어 붙인 표를 출력한다
```

실행 결과:

```
    user          action
0  gaeun  ACCOUNT:CHANGE
1  gaeun  ACCOUNT:CHANGE
0  gaeun           login
```

- 읽는 법: <mark style="background:#bde3ff">판정 서버 2행 아래에 SaaS 1행이 붙어 3행이 되었습니다.</mark> 왼쪽 번호는 원래 표의 번호를 그대로 가져와서 0 이 두 번 나옵니다.
- <mark>표를 대괄호 안에 넣지 않고 쉼표로 따로 전달하면 오류가 납니다.</mark>

**🐼 판다스 문법 상자 — 열 두 개로 정렬하기 `sort_values([열1, 열2])`**

**<mark>`표.sort_values(["열1", "열2"])`</mark> 는 열1 순으로 정렬하고, 열1 의 값이 같은 행은 열2 순으로 정렬합니다. 열 이름은 리스트로 전달합니다**

아래는 사용자 순서가 섞여 있는 로그입니다. 사용자(`user`) 순으로 먼저 정렬하고, 같은 사용자 안에서는 시각(`time`) 순으로 정렬합니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                               # 표에 넣을 내용(열 이름: 값들)
    "user": ["seoyeon", "gaeun", "seoyeon", "gaeun"],  # user 열
    "time": ["17:38", "10:14", "09:05", "10:05"],      # time 열
}
df = pd.DataFrame(data)                                # 내용으로 표(DataFrame)를 만든다
print(df)                                              # 표를 출력한다
```

실행 결과:

```
      user   time
0  seoyeon  17:38
1    gaeun  10:14
2  seoyeon  09:05
3    gaeun  10:05
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
sorted_df = df.sort_values(["user", "time"])  # user 순으로, 같은 user 는 time 순으로 정렬한다
print(sorted_df)                              # 정렬한 표를 출력한다
```

실행 결과:

```
      user   time
3    gaeun  10:05
1    gaeun  10:14
2  seoyeon  09:05
0  seoyeon  17:38
```

- 읽는 법: <mark style="background:#bde3ff">먼저 `user` 순(gaeun → seoyeon)으로 놓이고, 같은 사용자 안에서는 `time` 순(10:05 → 10:14, 09:05 → 17:38)으로 놓였습니다.</mark> 왼쪽 번호는 원래 행의 번호라서 바뀐 순서로 나옵니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `make_ip_user_map` | SaaS 로그인 표 | IP → 사용자 딕셔너리(미리 채움) |
| `attach_user_to_web` | 웹 실패 표 · 딕셔너리 | `user` 열이 붙은 웹 이벤트 표 |
| `build_timeline` | 서버 · SaaS · 웹 표 | 사용자 · 시각 순으로 정렬된 표 |
| `find_chains` | 정렬된 표 | 연결된 사건 리스트와 연결되지 않은 사용자 |
| `find_chains_in_events` | 이벤트 표 | 연결된 사건 리스트(미리 채움, 6교시에서 씀) |

- 미리 채운 줄 가운데 처음 보는 것은 이렇습니다.
  - `hours * 60 + minutes` 는 시각을 「자정부터 몇 분이 지났는지」로 바꿉니다(09:33 → 573). 사용자별로 가장 늦은 시각에서 가장 이른 시각을 빼면 첫 이벤트와 마지막 이벤트의 시간 차(분)가 나오고, 이 값을 60분 기준과 비교합니다. 분 단위로 계산하므로 초는 버립니다.
  - `times.dt.minute` 는 오전의 `.dt.hour` 처럼 시각 값에서 분(0~59)만 꺼냅니다. `latest - earliest` 는 사용자별로 가장 늦은 시각(분)에서 가장 이른 시각(분)을 뺍니다.
  - `source_counts.index` 는 사용자 이름들입니다. `source_counts[user]` 는 그 사용자의 값입니다.
  - `.copy()` 는 원본 표를 바꾸지 않도록 복사본을 만듭니다.
  - `grouped["source"].nunique()` 는 사용자별로 `source` 값이 몇 종류인지 세는 한 줄입니다. 왼쪽부터 ① `grouped["source"]` 가 `source` 열을 고르고 ② `.nunique()` 가 서로 다른 값의 수를 셉니다.
- **직접 쓰는 곳은 다섯 군데**(번호 1 ~ 5)이고, 함수 세 개 안에 나뉘어 있습니다.
  - `attach_user_to_web`(1번): IP 마다 사용자를 `map` 으로 채웁니다.
  - `build_timeline`(2 · 3번): 세 표를 연결하고 사용자 · 시각 순으로 정렬합니다.
  - `find_chains`(4 · 5번): 연결 조건을 확인하는 `if` 줄은 미리 채웠고, 그 안에서 이유 문장을 만들어 사건 리스트에 추가합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 서로 다른 로그를 한 사용자 기준으로 연결해 60분 안의 사건 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>서버 · SaaS · 웹 로그의 탐지 결과가 따로 있어서, 같은 사용자의 기록이 로그별로 나뉘어 있습니다</mark>.
- **그래서 만드는 것**: `correlation.py` 입니다.
  - 웹 이벤트에 IP 로 사용자를 채웁니다.
  - 세 로그를 한 표로 합쳐 사용자 · 시각 순으로 정렬합니다.
  - 서로 다른 로그가 2종류 이상이고 첫 이벤트부터 마지막 이벤트까지 60분 이내인 사용자를 하나의 사건으로 연결합니다.
- **실행하면**: <mark>단계 1: 사용자를 알 수 있는 웹 이벤트 수, 단계 2: 합친 이벤트 수와 한 사용자의 흐름, 단계 3: 연결된 사건, 단계 4: 로그가 2종류 이상이지만 시간 차가 60분을 넘어 연결되지 않은 사용자가 나옵니다.</mark>
- **현업에서는**: 이벤트 하나씩이 아니라 한 사용자 단위의 사건으로 연결하면 담당자가 읽을 양이 줄어듭니다. 시간 기준 밖에 있는 이벤트는 따로 두어 관계없는 일이 섞이지 않게 합니다.

**🎯 할 일**

1. `correlation.py` · `day04_5-1_run.py` 두 파일을 만들고, `correlation.py` 의 세 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>사용자를 알 수 있는 웹 이벤트 수</mark>(단계 1), <mark>합친 이벤트 수와 한 사용자의 흐름</mark>(단계 2), <mark>연결된 사건</mark>(단계 3), <mark>연결되지 않은 사용자</mark>(단계 4)를 읽습니다.

**`correlation.py`**

```python
import pandas as pd                                    # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins      # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures      # 4교시 함수를 불러온다

MIN_SOURCES = 2                                        # 서로 다른 로그(source)가 이 개수 이상이면 연결된 것으로 본다
WINDOW_MINUTES = 60                                    # 한 사용자의 이벤트가 이 분 안에 모여 있어야 연결된 것으로 본다


def make_ip_user_map(logins):                          # SaaS 로그인 표를 받는 함수
    """성공한 SaaS 로그인에서 IP 마다 사용자를 찾아 딕셔너리로 만든다.
    웹 서버 로그에는 사용자가 없어서 IP 로 사용자를 찾을 때 쓴다.
    """
    ip_user = {}                                       # IP → 사용자 딕셔너리
    login_list = logins.to_dict("records")             # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                           # 로그인을 하나씩 꺼낸다
        if login["result"] == "성공":                  # 성공한 로그인이면
            ip_user[login["ip"]] = login["user"]       # 그 IP 의 사용자를 딕셔너리에 담는다
    return ip_user                                     # IP → 사용자 딕셔너리를 리턴한다


def attach_user_to_web(web_failures, ip_user):         # 웹 실패 표와 IP → 사용자 딕셔너리를 받는 함수
    """IP 로 사용자를 알 수 있는 웹 실패 이벤트에 user 열을 붙인다.
    웹 로그를 서버 · SaaS 로그와 같은 사용자 기준으로 연결해 분석할 때 쓴다.
    """
    ips = web_failures["ip"]                           # ip 열만 꺼낸다
    known_ips = list(ip_user)                          # 딕셔너리의 키(IP)만 리스트로 만든다
    is_known = ips.isin(known_ips)                     # 행마다 사용자를 아는 IP 인지 구해 True 또는 False 를 만든다
    known_web = web_failures[is_known]                 # True 인 행만 골라 새 표를 만든다
    web_part = known_web.copy()                        # 원본을 바꾸지 않도록 복사한다 — 미리 채운 줄

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web_part 의 "ip" 열을 꺼내 .map(ip_user) 를 붙여 IP 마다 사용자를 구해 users 에 담는다
    web_part["user"] = users                           # 표에 user 열을 붙인다 — 미리 채운 줄
    return web_part                                    # user 열이 붙은 웹 이벤트 표를 리턴한다


def build_timeline(server_part, saas_part, web_part):  # 세 로그의 표를 받는 함수
    """세 로그의 표를 하나로 합쳐 사용자 · 시각 순으로 정렬하고, 하루 중 몇 분인지 열을 붙인다.
    사용자마다 서로 다른 로그의 이벤트를 시간순으로 놓고 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. pd.concat 에 [server_part, saas_part, web_part] 리스트를 전달해 timeline 에 담는다
    # 3. timeline 에 .sort_values 를 붙이고 ["user", "time"] 리스트를 전달해 사용자 순, 같은 사용자는 시각 순으로 정렬한 결과를 timeline 에 담는다
    times = pd.to_datetime(timeline["time"])           # 문자열 시각을 시각 값으로 바꾼다
    hours = times.dt.hour                              # 시각 값에서 시(0~23)만 꺼낸다
    minutes = times.dt.minute                          # 시각 값에서 분(0~59)만 꺼낸다
    timeline["minute_of_day"] = hours * 60 + minutes   # 자정부터 몇 분이 지났는지 열을 붙인다 — 미리 채운 줄
    return timeline                                    # 정렬된 이벤트 표를 리턴한다


def find_chains(timeline):                             # 정렬된 이벤트 표를 받는 함수
    """서로 다른 로그가 짧은 시간 안에 한 사용자에게 모여 있는 사건을 찾는다.
    이벤트 하나씩이 아니라 한 사용자의 사건으로 연결해 분석할 때 쓴다.
    """
    grouped = timeline.groupby("user")                 # user 가 같은 행끼리 그룹으로 만든다
    source_counts = grouped["source"].nunique()        # 그룹마다 서로 다른 로그(source)가 몇 종류인지 센다
    latest = grouped["minute_of_day"].max()            # 그룹마다 가장 늦은 시각(분)을 구한다
    earliest = grouped["minute_of_day"].min()          # 그룹마다 가장 이른 시각(분)을 구한다
    spans = latest - earliest                          # 그룹마다 처음부터 마지막까지 몇 분인지 구한다

    chains = []                                        # 연결된 사건을 담을 빈 리스트
    not_chained = []                                   # 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자 정보
    for user in source_counts.index:                   # 사용자를 하나씩 꺼낸다
        source_count = source_counts[user]             # 그 사용자의 로그 종류 수
        span = spans[user]                             # 그 사용자의 처음부터 마지막까지 분
        has_many_sources = source_count >= MIN_SOURCES  # 로그 종류가 기준 이상인지 구한다
        is_close = span <= WINDOW_MINUTES              # 시간 간격이 기준 이내인지 구한다
        if has_many_sources and is_close:              # 로그 종류도 충분하고 60분 이내이면 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 4. "서로 다른 로그 " 와 str(source_count) 와 "종류 · " 와 str(span) 과 "분 안" 을 + 로 연결해 reason 에 담는다
            # 5. chains 에 키 "user" 에 user, 키 "reason" 에 reason 을 담은 딕셔너리를 추가한다
        if has_many_sources and not is_close:          # 로그 종류는 여럿인데 시간 차가 60분을 초과하면 — 미리 채운 줄
            not_chained.append({"user": user, "source_count": int(source_count), "span_minutes": int(span)})  # 연결되지 않은 사용자와 두 숫자를 추가한다
    return chains, not_chained                         # 연결된 사건과 연결되지 않은 사용자를 리턴한다


def find_chains_in_events(events):                     # 이벤트 표를 받는 함수
    """이벤트 표 하나로 위 함수를 차례로 불러 연결된 사건 리스트를 만든다.
    6교시에서 점수를 매기기 전에 한 번에 쓴다.
    """
    server_failures = pick_server_failures(events)     # 판정 서버 실패 이벤트를 고른다
    server_part = server_failures                      # 서버 실패 이벤트 전체를 쓴다
    saas_part = pick_saas(events)                      # SaaS 이벤트를 고른다
    logins = pick_logins(saas_part)                    # 로그인 이벤트를 고른다
    ip_user = make_ip_user_map(logins)                 # IP → 사용자 딕셔너리를 만든다
    web_failures = pick_web_failures(events)           # 웹 실패 이벤트를 고른다
    web_part = attach_user_to_web(web_failures, ip_user)  # 사용자를 아는 웹 이벤트에 user 열을 붙인다
    timeline = build_timeline(server_part, saas_part, web_part)  # 세 로그를 합쳐 정렬한다
    chains, not_chained = find_chains(timeline)        # 연결된 사건을 찾는다
    return chains                                      # 연결된 사건 리스트를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 3번은 함수 안이라 앞에 공백 4개이고, 4 · 5번은 `for` 와 `if` 안이라 12개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 정렬은 새 표를 만들어 주므로 3번은 <mark>`timeline = timeline.sort_values(…)` 로 다시 담아야</mark> 합니다. `timeline.sort_values(…)` 만 쓰면 정렬한 결과가 사라집니다.
- 4번의 완성 모양은 `서로 다른 로그 2종류 · 30분 안` 입니다(숫자는 사용자마다 다릅니다). <mark>공백 하나까지 같아야 출력이 같습니다.</mark>
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다. `if` 안쪽의 4 · 5번이 비어 있기 때문입니다.

**`day04_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

```python
from access_detection import load_events, pick_server_failures, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins      # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures      # 4교시 함수를 불러온다
from correlation import make_ip_user_map, attach_user_to_web, build_timeline, find_chains, WINDOW_MINUTES  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                      # 이벤트 파일을 표로 읽는다
server_failures = pick_server_failures(events)         # 판정 서버 실패 이벤트를 고른다
server_part = server_failures                           # 서버 실패 이벤트 전체를 쓴다
saas_part = pick_saas(events)                          # SaaS 이벤트를 고른다
logins = pick_logins(saas_part)                        # 로그인 이벤트를 고른다
ip_user = make_ip_user_map(logins)                     # 성공한 로그인에서 IP → 사용자 딕셔너리를 만든다

web_failures = pick_web_failures(events)               # 웹 실패 이벤트를 고른다
web_part = attach_user_to_web(web_failures, ip_user)   # 사용자를 아는 웹 이벤트에 user 열을 붙인다
web_count = len(web_part)                              # 그 이벤트가 몇 개인지 센다
print("--- 단계 1: IP 로 사용자를 알 수 있는 웹 실패 이벤트", web_count, "개")  # 단계 1 시작을 알리는 줄과 개수

timeline = build_timeline(server_part, saas_part, web_part)  # 세 로그를 합쳐 사용자 · 시각 순으로 정렬한다
timeline_count = len(timeline)                         # 합친 이벤트가 몇 개인지 센다
print("--- 단계 2: 사용자별로 시간순으로 놓은 이벤트", timeline_count, "개")  # 단계 2 시작을 알리는 줄과 개수
print("gaeun 의 이벤트 (시각 · 로그 · 행동 · 결과)")  # 아래 줄들이 gaeun 의 이벤트라는 것을 알리는 줄

users = timeline["user"]                               # user 열만 꺼낸다
is_gaeun = users == "gaeun"                            # 행마다 gaeun 인지 비교해 True 또는 False 를 만든다
gaeun_rows = timeline[is_gaeun]                        # True 인 행만 골라 gaeun 의 이벤트 표를 만든다
gaeun_list = gaeun_rows.to_dict("records")             # 표를 이벤트 딕셔너리 리스트로 바꾼다
for event in gaeun_list:                               # gaeun 의 이벤트를 시간순으로 하나씩 꺼낸다
    print(event["time"], event["source"], event["action"], event["result"])  # 시각 · 로그 · 행동 · 결과를 출력한다

chains, not_chained = find_chains(timeline)            # 연결된 사건과 연결되지 않은 사용자를 찾는다
print("--- 단계 3:", WINDOW_MINUTES, "분 안에 서로 다른 로그로 연결된 사건")  # 단계 3 시작을 알리는 줄
for chain in chains:                                   # 연결된 사건을 하나씩 꺼낸다
    print(chain)                                       # 사건을 출력한다

print("--- 단계 4: 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자")  # 단계 4 시작을 알리는 줄
for item in not_chained:                               # 연결되지 않은 사용자를 하나씩 꺼낸다
    print(item)                                        # 사용자 · 로그 종류 수 · 첫 이벤트부터 마지막 이벤트까지의 분을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `correlation.py` · `day04_5-1_run.py` 를 `anomaly_detection` 폴더에 만들어 위 코드를 붙여 넣습니다. 터미널에서는 `touch` 로 만든 뒤 VS Code 에서 엽니다.
   ```bash
   pwd
   touch correlation.py day04_5-1_run.py
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
2. **[VS Code]** `correlation.py` 에서 <mark>직접 쓰는 곳 다섯 군데를 씁니다</mark>. 5.1 의 문법 상자를 보고 쓰고, 막히면 아래 「5교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day04_5-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_5-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **네 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없고, 단계 2는 제목 아래 6줄(`gaeun 의 이벤트 …` 안내 줄 1줄과 gaeun 의 이벤트 5줄), 단계 3은 1줄, 단계 4는 제목 아래 1줄입니다.
5. **[보고서]** `day04_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 연결된 사건의 사용자와 이유를 적어 주세요.
   - (나) 🔍 단계 2에 나온 gaeun 의 이벤트 5개는 어느 로그(`source`)에서 왔고, 왜 한 사건으로 연결됐나요? 이 사건만으로 공격이라고 확정할 수 있는지도 적어 주세요.
   - (다) 🔍 seoyeon 은 서로 다른 로그에 나오지만 연결되지 않았습니다. 단계 4 의 두 숫자(로그 종류 수와 처음부터 마지막까지의 분)로 두 조건을 비교해 연결되지 않은 이유를 설명하고, 하나의 사건으로 연결하지 않아서 탐지하지 못할 수 있는 것을 오전 3교시 출력에서 seoyeon 이 나온 규칙과 연결해 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| IP 로 사용자 채우기 | `users = web_part["ip"].map(ip_user)` |
| 표 위아래로 잇기 | `timeline = pd.concat([server_part, saas_part, web_part])` |
| 열 두 개로 정렬 | `timeline = timeline.sort_values(["user", "time"])` |
| 이유 문장 만들기 | `reason = "서로 다른 로그 " + str(source_count) + "종류 · " + str(span) + "분 안"` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 위험 점수를 매겨 등급과 이유 저장하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「오전과 5교시에서 탐지된 규칙이 여러 개인데, 결과가 모두 `탐지됨` 이라고만 나와서 어느 대상부터 확인할지 정할 수 없습니다. 퇴사한 계정이 계속 시도한 것과 파일을 한 번 더 내려받은 것이 같은 무게일 수는 없습니다.
>
> 탐지된 규칙마다 점수를 정하고 대상(사용자 또는 IP)마다 더해서 high · mid · low 로 나눠 주세요. 담당자가 왜 그 등급인지 알 수 있게, 탐지된 규칙 이름도 같이 파일에 적어 주세요.」
> - **왜 중요한가**: <mark>점수만 있고 이유가 없으면 담당자가 근거를 확인하기 어려워서, 탐지된 규칙 이름을 이유로 함께 저장합니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 규칙마다 **점수**를 주고, 대상(사용자 또는 IP)마다 탐지된 규칙의 점수를 **더합니다**. <mark>같은 규칙이 한 대상의 여러 이벤트에서 탐지되어도 그 규칙의 점수는 대상마다 한 번만 더합니다.</mark>
2. 합계를 high · mid · low 로 나누고, <mark>탐지된 규칙 이름을 함께 저장하면 담당자가 점수가 나온 근거를 확인할 수 있습니다.</mark>

### 📖 6.1 규칙마다 점수와 등급 기준

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

| 탐지된 규칙 | 점수 | 어느 단계에서 탐지되나 |
|---|---|---|
| 퇴사한 계정 | 60 | 오전 2교시: 서버가 거절한 요청을 `check_permission` 으로 다시 판정했을 때 나온 이유 단어 |
| 권한 없음 | 20 | 오전 2교시 |
| 규칙은 허용인데 서버가 거절 | 10 | 오전 2교시 |
| 업무 시간 밖 로그인 | 15 | 오전 3교시 |
| 평소와 다른 IP | 20 | 오전 3교시 |
| 대량 다운로드 | 25 | 오전 3교시 |
| 경로 스캔 | 30 | 오전 4교시: 대상이 사용자가 아니라 IP |
| 여러 로그 연결 | 30 | 5교시 |

- 등급 기준은 점수가 **60 이상이면 high, 35 이상 60 미만이면 mid, 35 미만이면 low** 입니다. 「이상」은 `>=` 이고, <mark>높은 기준(high)부터 먼저 검사합니다.</mark> 등급은 위험이 없다는 판정이 아니라 **확인할 순서를 정하는 기준**입니다.
- 표의 「규칙」은 **탐지 규칙의 이름**입니다. 서버 거절은 판정 이유 단어(`퇴사한 계정` · `권한 없음` · `허용`)를 그대로 이름으로 쓰고, `허용` 은 「규칙은 허용인데 서버가 거절」이라는 이름으로 바꿔 씁니다.
- 대상은 사용자(`seoyeon` · `dami` …)와 IP(경로 스캔)입니다. 코드의 `entity`(엔티티, 점수를 매길 대상)가 이 대상입니다. 이 숫자들은 <mark>오늘 정해 고정한 값</mark>이고, 현업에서는 조직이 정합니다.
- 출력 맨 아래의 `dtype: int64` 는 값이 정수라는 표시이고 읽지 않아도 됩니다(11/3 오후와 11/4 오후에 본 줄과 같습니다).

**🐼 판다스 문법 상자 — 그룹마다 합계 `sum`**

**<mark>`그룹["열"].sum()`</mark> 은 `groupby` 로 만든 그룹마다 그 열의 숫자를 모두 더합니다**

오전에 같은 값끼리 묶는 `groupby` 를 썼습니다. 아래는 탐지된 규칙마다 점수를 적은 표이고, 대상(`entity`)마다 점수를 더합니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                       # 표에 넣을 내용(열 이름: 값들)
    "entity": ["seoyeon", "seoyeon", "dami"],  # entity 열
    "points": [20, 25, 60],                    # points 열
}
df = pd.DataFrame(data)                        # 내용으로 표(DataFrame)를 만든다
print(df)                                      # 표를 출력한다
```

실행 결과:

```
    entity  points
0  seoyeon      20
1  seoyeon      25
2     dami      60
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
grouped = df.groupby("entity")    # entity 가 같은 행끼리 그룹으로 묶는다
totals = grouped["points"].sum()  # 그룹에서 points 열을 골라 바로 합계를 구한다
print(totals)                     # 대상별 점수 합계를 출력한다
```

실행 결과:

```
entity
dami       60
seoyeon    45
Name: points, dtype: int64
```

- 읽는 법: <mark style="background:#bde3ff">`seoyeon` 은 20 과 25 를 더한 45, `dami` 는 60</mark> 입니다. 문제에서는 딕셔너리 리스트로 표를 만드는 `pd.DataFrame(리스트)` 줄이 미리 채워져 있습니다.
- <mark>`groupby` 결과는 이름순(dami → seoyeon)으로 나옵니다.</mark> 문제에서는 미리 채운 줄이 점수가 높은 순으로 다시 정렬합니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `collect_findings` | 이벤트 표 · 연결된 사건 | 탐지된 규칙 리스트(미리 채움) |
| `score_findings` | 탐지된 규칙 리스트 | 대상별 점수(높은 순) |
| `make_grade` | 점수 | `"high"` · `"mid"` · `"low"` |
| `collect_reasons` · `save_records` | 탐지된 규칙 · 기록 리스트 | 대상별 규칙 이름 · 저장한 건수(미리 채움) |
| `make_records` | 대상별 점수 · 이유 | 점수 · 등급 · 이유 기록 리스트 |

- `make_records` 의 `totals.items()` 는 점수 집계 결과(시리즈)에서 「대상, 점수」를 한 쌍씩 꺼냅니다. 딕셔너리의 `.items()` 와 같은 모양입니다.
- **직접 쓰는 곳은 다섯 군데**(번호 1 ~ 5)이고, 함수 세 개 안에 나뉘어 있습니다.
  - `score_findings`(1 · 2번): 규칙마다 점수를 `map` 으로 채우고 대상마다 `sum` 으로 더합니다.
  - `make_grade`(3 · 4번): 점수가 high 기준 이상이면 `"high"` 를 리턴합니다. mid 와 low 는 같은 모양이라 미리 채웠습니다.
  - `make_records`(5번): 대상 · 점수 · 등급 · 이유를 딕셔너리로 만듭니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 탐지된 규칙에 점수를 매겨 등급과 이유를 day03_risk_scores.json 에 저장하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>오전과 5교시에서 탐지된 규칙이 8건 있지만 대상별 우선순위가 정해져 있지 않습니다</mark>.
- **그래서 만드는 것**: `risk_scores.py` 입니다.
  - 규칙마다 점수를 채우고 대상마다 더합니다.
  - 점수로 high · mid · low 등급을 정합니다.
  - 대상 · 점수 · 등급 · 이유를 `day03_risk_scores.json` 한 파일에 저장합니다.
- **실행하면**: <mark>단계 1: 탐지된 규칙 수, 단계 2: 대상별 점수, 단계 3: 저장한 건수, 단계 4: 저장된 기록이 한 건씩 나옵니다.</mark>
- **현업에서는**: 점수와 이유를 함께 남기면 등급이 올라간 근거를 설명할 수 있습니다. 조직은 필요에 따라 점수 기준을 바꿀 수 있고, 바꾼 날짜와 이유를 기록합니다.

**🎯 할 일**

1. `risk_scores.py` · `day04_6-1_run.py` 두 파일을 만들고, `risk_scores.py` 의 세 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>탐지된 규칙 수</mark>(단계 1), <mark>대상별 점수</mark>(단계 2), <mark>저장한 건수</mark>(단계 3), <mark>저장된 기록</mark>(단계 4)를 읽고, 새로 생긴 `day03_risk_scores.json` 을 VS Code 에서 열어 봅니다.

`collect_findings` 는 읽기만 하는 미리 채운 함수입니다. 오전 탐지 결과를 (대상, 규칙) 쌍으로 모으는 일이라 직접 쓰는 곳이 없습니다.

**`risk_scores.py`**

```python
import json                                        # 점수를 JSON 파일로 쓰기 위해 json 을 불러온다
import pandas as pd                                    # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users  # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures, find_scan_ips  # 4교시 함수를 불러온다

RISK_PATH = "day03_risk_scores.json"                   # 점수를 저장할 파일 이름
HIGH_LIMIT = 60                                        # 점수가 이 값 이상이면 high
MID_LIMIT = 35                                         # 점수가 이 값 이상이면 mid, 그보다 낮으면 low
WEIGHTS = {"퇴사한 계정": 60, "권한 없음": 20, "규칙은 허용인데 서버가 거절": 10,
           "업무 시간 밖 로그인": 15, "평소와 다른 IP": 20, "대량 다운로드": 25,
           "경로 스캔": 30, "여러 로그 연결": 30}      # 탐지된 규칙마다 점수
SERVER_RULES = {"퇴사한 계정": "퇴사한 계정", "권한 없음": "권한 없음", "허용": "규칙은 허용인데 서버가 거절"}  # 서버 판정 이유를 규칙 이름으로 바꾼다


def add_finding(findings, entity, rule):               # 리스트 · 대상 · 규칙 이름을 받는 함수
    """대상과 탐지된 규칙을 한 건 추가하되 같은 건은 한 번만 추가한다.
    같은 규칙이 여러 이벤트에 해당해도 점수가 중복되지 않게 할 때 쓴다.
    """
    finding = {"entity": entity, "rule": rule}         # 대상과 규칙을 딕셔너리로 만든다
    if finding not in findings:                        # 아직 없는 건이면
        findings.append(finding)                       # 리스트에 추가한다


def collect_findings(events, chains):                  # 이벤트 표와 연결된 사건을 받는 함수
    """오전 탐지 3개와 5교시 연결 결과를 (대상, 탐지된 규칙) 리스트로 모은다.
    점수를 매기기 전에 한 번에 쓴다.
    """
    findings = []                                      # 탐지된 규칙을 담을 빈 리스트

    server_failures = pick_server_failures(events)     # 판정 서버 실패 이벤트를 고른다
    suspicious = pick_suspicious(server_failures)      # 먼저 확인할 서버 이벤트를 고른다
    suspicious_list = suspicious.to_dict("records")    # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for event in suspicious_list:                      # 이벤트를 하나씩 꺼낸다
        reason, priority = judge_failure(event["user"], event["action"])  # 3과목 규칙으로 다시 판정한다
        rule = SERVER_RULES.get(reason, reason)        # 판정 이유를 규칙 이름으로 바꾼다
        add_finding(findings, event["user"], rule)     # 사용자와 규칙을 추가한다

    saas = pick_saas(events)                           # SaaS 이벤트를 고른다
    logins = pick_logins(saas)                         # 로그인 이벤트를 고른다
    off_hours_logins = find_off_hours_logins(logins)   # 업무 시간 밖 로그인을 찾는다
    off_hours_users = list(off_hours_logins["user"])   # 그 로그인의 사용자 이름만 리스트로 만든다
    new_ip_users = find_new_ip_users(logins)           # 평소와 다른 IP 로 로그인한 사용자를 찾는다
    bulk_users = find_bulk_download_users(saas)        # 대량 다운로드 사용자를 찾는다
    for user in off_hours_users:                       # 업무 시간 밖 로그인 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "업무 시간 밖 로그인")  # 사용자와 규칙을 추가한다
    for user in new_ip_users:                          # 평소와 다른 IP 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "평소와 다른 IP")  # 사용자와 규칙을 추가한다
    for user in bulk_users:                            # 대량 다운로드 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "대량 다운로드")   # 사용자와 규칙을 추가한다

    web_failures = pick_web_failures(events)           # 웹 실패 이벤트를 고른다
    scan_ips, many_kinds = find_scan_ips(web_failures)  # 경로 스캔 IP 를 찾는다
    for ip in scan_ips:                                # 스캔 IP 를 하나씩 꺼낸다
        add_finding(findings, ip, "경로 스캔")         # IP 와 규칙을 추가한다

    for chain in chains:                               # 연결된 사건을 하나씩 꺼낸다
        add_finding(findings, chain["user"], "여러 로그 연결")  # 사용자와 규칙을 추가한다
    return findings                                    # 탐지된 규칙 리스트를 리턴한다


def score_findings(findings):                          # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙의 점수를 더해 점수가 높은 순으로 정렬한다.
    어느 대상부터 볼지 순서를 정할 때 쓴다.
    """
    findings_table = pd.DataFrame(findings)            # 딕셔너리 리스트를 표로 만든다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. findings_table 의 "rule" 열을 꺼내 .map(WEIGHTS) 를 붙여 규칙마다 점수를 구해 points 에 담는다
    findings_table["points"] = points                  # 표에 points 열을 붙인다 — 미리 채운 줄
    grouped = findings_table.groupby("entity")         # entity 가 같은 행끼리 그룹으로 만든다
    # 2. grouped 에서 "points" 열을 골라 .sum() 을 붙여 그룹마다 점수 합계를 구해 totals 에 담는다
    totals = totals.sort_values(ascending=False)       # 점수가 높은 순으로 정렬한다 — 미리 채운 줄
    return totals                                      # 대상별 점수를 리턴한다


def make_grade(score):                                 # 점수를 받는 함수
    """점수로 high · mid · low 등급을 정한다.
    점수가 높은 대상부터 먼저 보게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. if 로 시작한다: score 가 HIGH_LIMIT 이상이면
    # 4.   그 if 안쪽에서 "high" 를 리턴한다
    if score >= MID_LIMIT:                             # 점수가 mid 기준 이상이면 — 미리 채운 줄 (위 high 와 같은 모양)
        return "mid"                                   # mid 이다 — 미리 채운 줄
    return "low"                                       # 둘 다 아니면 low 이다


def collect_reasons(findings):                         # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙 이름을 모아 딕셔너리로 만든다.
    왜 그 등급인지 이유를 함께 저장할 때 쓴다.
    """
    reasons = {}                                       # 대상 → 규칙 이름 리스트 딕셔너리
    for finding in findings:                           # 탐지된 규칙을 하나씩 꺼낸다
        entity = finding["entity"]                     # 그 건의 대상
        if entity not in reasons:                      # 처음 나온 대상이면
            reasons[entity] = []                       # 빈 리스트를 만든다
        reasons[entity].append(finding["rule"])        # 그 대상의 규칙 이름을 추가한다
    return reasons                                     # 대상별 규칙 이름을 리턴한다


def make_records(totals, reasons):                     # 대상별 점수와 이유를 받는 함수
    """대상마다 점수 · 등급 · 이유를 담은 딕셔너리 리스트를 만든다.
    담당자가 읽을 파일의 내용을 만들 때 쓴다.
    """
    records = []                                       # 기록을 담을 빈 리스트
    for entity, score in totals.items():               # 대상과 점수를 한 쌍씩 꺼낸다
        grade = make_grade(score)                      # 점수로 등급을 정한다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. 키 "entity" 에 entity, "score" 에 int(score), "grade" 에 grade, "reasons" 에 reasons[entity] 를 담은 딕셔너리를 record 에 담는다 (int 는 JSON 저장용)
        records.append(record)                         # 기록을 리스트에 추가한다
    return records                                     # 기록 리스트를 리턴한다


def save_records(records, path):                       # 기록 리스트와 파일 경로를 받는 함수
    """기록 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다.
    담당자와 다른 프로그램이 같은 파일을 읽게 할 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:    # path 파일을 쓰기 모드로 연다
        json.dump(records, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 줄을 나눠 저장한다
    saved_count = len(records)                         # 저장한 기록이 몇 건인지 센다
    return saved_count                                 # 저장한 건수를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 · 2번은 함수 안이라 앞에 공백 4개이고, 3 · 4번도 함수 안이라 `if` 는 4개, `return` 은 8개이며, 5번은 `for` 안이라 8개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 5번의 `int(score)` 는 <mark>JSON 으로 저장하려고 판다스의 숫자를 파이썬 정수로 바꾸는 것</mark>입니다. 빼면 저장할 때 `TypeError: Object of type int64 is not JSON serializable` 오류가 납니다.
- `collect_findings` 는 읽기만 하는 미리 채운 함수입니다. `SERVER_RULES.get(reason, reason)` 은 딕셔너리에서 reason 을 찾고, 없으면 reason 을 그대로 쓴다는 뜻입니다.
- 채우기 전에 실행하면 `NameError: name 'points' is not defined` 오류가 납니다. 1번을 아직 안 썼기 때문입니다.

**`day04_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(리스트)` 는 리스트의 개수입니다.

```python
from access_detection import load_events, EVENTS_PATH  # 2교시 함수를 불러온다
from correlation import find_chains_in_events          # 5교시 함수를 불러온다
from risk_scores import collect_findings, score_findings, collect_reasons, make_records, save_records, RISK_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                      # 이벤트 파일을 표로 읽는다
chains = find_chains_in_events(events)                 # 5교시에서 만든 연결된 사건을 찾는다
findings = collect_findings(events, chains)            # 오전 탐지와 연결 결과에서 탐지된 규칙을 모은다
finding_count = len(findings)                          # 탐지된 규칙이 모두 몇 건인지 센다
print("--- 단계 1: 탐지된 규칙", finding_count, "건")    # 단계 1 시작을 알리는 줄과 건수

totals = score_findings(findings)                      # 대상마다 점수를 더한다
print("--- 단계 2: 대상별 점수")                       # 단계 2 시작을 알리는 줄
print(totals)                                          # 점수가 높은 순으로 출력한다

reasons = collect_reasons(findings)                    # 대상마다 탐지된 규칙 이름을 모은다
records = make_records(totals, reasons)                # 점수 · 등급 · 이유를 담은 기록을 만든다
saved_count = save_records(records, RISK_PATH)         # 기록을 파일에 저장한다
print("--- 단계 3:", RISK_PATH, "에", saved_count, "건 저장")  # 단계 3 시작을 알리는 줄과 건수

print("--- 단계 4: 등급 · 대상 · 점수 · 이유")         # 단계 4 시작을 알리는 줄
for record in records:                                 # 기록을 하나씩 꺼낸다
    print(record["grade"], record["entity"], record["score"], record["reasons"])  # 등급 · 대상 · 점수 · 이유를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `risk_scores.py` · `day04_6-1_run.py` 를 `anomaly_detection` 폴더에 만들어 위 코드를 붙여 넣습니다. 터미널에서는 `touch risk_scores.py day04_6-1_run.py` 로 만든 뒤 VS Code 에서 엽니다.
2. **[VS Code]** `risk_scores.py` 에서 <mark>직접 쓰는 곳 다섯 군데를 씁니다</mark>. 6.1 의 표와 문법 상자를 보고 씁니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day04_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_6-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **네 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1과 단계 3은 숫자가 제목 줄에 함께 나오고, 단계 2는 제목 아래 7줄(맨 위 `entity`, 대상 5줄, 맨 아래 `Name: points, dtype: int64`), 단계 4는 5줄입니다.
5. **[VS Code]** 새로 생긴 `day03_risk_scores.json` 을 열어 <mark>대상 5개가 점수 순으로 들어 있는지</mark> 확인합니다.
6. **[보고서]** `day04_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, high · mid · low 에 각각 어떤 대상이 들어갔는지 적어 주세요.
   - (나) 🔍 seoyeon 의 점수가 어떤 규칙의 점수를 더해 나왔는지 적고, 점수만 저장하지 않고 이유(`reasons`)를 함께 저장하는 까닭을 적어 주세요.
   - (다) 🔍 198.51.100.90 은 경로 스캔 하나에 해당하지만 low 입니다. low 는 점수 기준상 낮은 등급이라는 뜻입니다. low 인 이유를 점수와 기준으로 설명하고, 이 IP 의 기록을 무시해도 되는지 샘플의 값(그 IP 의 요청 3개의 `result`)으로 판단해 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 규칙마다 점수 채우기 | `points = findings_table["rule"].map(WEIGHTS)` |
| 대상마다 점수 더하기 | `totals = grouped["points"].sum()` |
| 등급 정하기 | `if score >= HIGH_LIMIT:` → `return "high"` |
| 기록 만들기 | `record = {"entity": entity, "score": int(score), …}` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다.</mark> 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, `pwd` 로 위치를 먼저 확인한 뒤 결과가 `anomaly_detection` 으로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「오늘 만든 탐지 코드와 점수 파일을 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `anomaly_detection` 폴더에 오늘 오전과 오후에 만든 파일이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `anomaly_detection` 폴더에서 확인합니다. `day04_pm_report.md` 의 5 · 6교시 칸에서 `답:` 뒤와 코드 상자가 비어 있는 질문이 없는지도 봅니다(마무리 (가)는 3번에서 채웁니다).
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나야 합니다.</mark> 오전 파일(`access_detection.py` · `saas_detection.py` · `malicious_detection.py` · `advanced_detection.py`)과 오후 파일(`correlation.py` · `risk_scores.py` · `day04_5-1_run.py` · `day04_6-1_run.py` · `day03_risk_scores.json`)이 보이면 됩니다. `advanced_detection.py` 는 오전 4교시에서 만든 파일입니다.
1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 0번의 `pwd` 결과가 `anomaly_detection` 으로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.
   ```bash
   cd ..
   pwd
   ```
   - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 있는 폴더의 위치 확인
   - <mark>결과가 다르면</mark> VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark>빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 말고,</mark> 아래 안내대로 `.gitignore` 를 고친 뒤 `git status` 를 다시 봅니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 올릴 파일의 상태를 봄
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `anomaly_detection/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add anomaly detection day 4 detections, correlation and risk scores"
   git push
   ```
   - 명령 풀이: `git add .` 바뀐 파일을 올릴 대상에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림
   - <mark>`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `anomaly_detection` 폴더를 열고, VS Code 왼쪽 목록의 `anomaly_detection` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
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
| 세 로그를 한 사용자 기준으로 연결해 60분 안에 모인 사건을 찾았다 | 오후 5-1 |
| 탐지된 규칙에 점수를 매겨 등급과 이유를 `day03_risk_scores.json` 에 저장했다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

다음 수업은 11/6(금)입니다. <mark>오늘 만든 탐지가 맞았는지를 직접 세어 봅니다.</mark> 알림이 났는데 문제가 아니었던 것(오탐)과 알림이 나야 하는데 안 난 것(미탐)을 찾습니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_5-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_5-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `attach_user_to_web` 안

```python
    users = web_part["ip"].map(ip_user)                # ip 열을 꺼내 바로 IP 마다 사용자를 찾아 채운다(map)
```

② `build_timeline` 안

```python
    timeline = pd.concat([server_part, saas_part, web_part])  # 세 표를 위아래로 연결해 표 하나로 만든다
    timeline = timeline.sort_values(["user", "time"])  # user 순으로, 같은 user 는 time 순으로 정렬한다
```

③ `find_chains` 안

```python
        if has_many_sources and is_close:             # 로그 종류도 충분하고 60분 이내이면 — 미리 채운 줄
            reason = "서로 다른 로그 " + str(source_count) + "종류 · " + str(span) + "분 안"  # 문자열을 연결해 이유 문장을 만든다
            chains.append({"user": user, "reason": reason})  # 연결된 사건에 사용자와 이유를 추가한다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 연결된 사건은 <mark style="background:#bde3ff">**gaeun**</mark> 한 명이며 이유는 「서로 다른 로그 3종류 · 41분 안」입니다.

```
--- 단계 1: IP 로 사용자를 알 수 있는 웹 실패 이벤트 1 개
--- 단계 2: 사용자별로 시간순으로 놓은 이벤트 24 개
gaeun 의 이벤트 (시각 · 로그 · 행동 · 결과)
2026-11-02 09:33:51 web GET /admin 실패
2026-11-02 10:05:00 server ACCOUNT:CHANGE 실패
2026-11-02 10:09:00 server ACCOUNT:CHANGE 실패
2026-11-02 10:12:55 saas login 성공
2026-11-02 10:14:00 server ACCOUNT:CHANGE 실패
--- 단계 3: 60 분 안에 서로 다른 로그로 연결된 사건
{'user': 'gaeun', 'reason': '서로 다른 로그 3종류 · 41분 안'}
--- 단계 4: 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자
{'user': 'seoyeon', 'source_count': 2, 'span_minutes': 555}
```

- (나) gaeun 의 이벤트 5개는 <mark>웹(`web`) 1개 · 판정 서버(`server`) 3개 · SaaS(`saas`) 1개</mark>이고, 서로 다른 로그가 3종류이며 09:33 부터 10:14 까지 41분 안에 모여 있어서 연결됐습니다.
  - <mark>공격이라고 확정할 수 없습니다.</mark> 서버의 거절 3개는 3과목(접근통제) 규칙으로는 「허용」이었고, 웹의 `/admin` 실패는 1건이며, SaaS 로그인은 성공했습니다. 같은 시간대에 여러 로그가 확인될 뿐, 원인은 이 기록만으로 알 수 없습니다.
- (다) seoyeon 은 단계 4 에서 <mark>로그 종류 2</mark>(서버 · SaaS)로 조건 ①(2 이상)을 만족하지만, 처음부터 마지막까지가 <mark>555분</mark>(09:05 ~ 18:20)으로 조건 ②(60분 이내)를 만족하지 못해 연결되지 않았습니다.
  - 하나의 사건으로 연결하지 않으면 서버의 `SETTLE:QUERY` 거절(권한 없음)과 오전 3교시에서 본 평소와 다른 IP · 대량 다운로드가 같은 사용자의 기록이라는 점을 <mark>탐지 결과에서 확인하기 어렵습니다.</mark>

**왜**

- <mark>서로 다른 로그와 짧은 시간, 두 조건이 함께 있어야 하나의 사건으로 연결합니다.</mark> 로그 종류만 보면 하루 종일 흩어진 일까지 연결되고, 시간만 보면 한 로그의 반복만 연결됩니다.

**자주 틀리는 곳**

- `pd.concat` 에 표를 쉼표로 따로 전달하면 `TypeError` 오류가 납니다. **표는 대괄호 `[ ]` 안에 넣어 리스트로 전달합니다.**
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`concat() takes 1 positional argument but 3 were given`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day04_5-1_run.py", line 18, in <module>
    timeline = build_timeline(server_part, saas_part, web_part)  # 세 로그를 합쳐 사용자 · 시각 순으로 정렬한다
  File "…/anomaly_detection/correlation.py", line 45, in build_timeline
    timeline = pd.concat(server_part, saas_part, web_part)  # 세 표를 위아래로 연결해 표 하나로 만든다
TypeError: concat() takes 1 positional argument but 3 were given
```

  - 줄 번호는 사람마다 다릅니다.
- 정렬 결과를 다시 담지 않고 `timeline.sort_values(["user", "time"])` 만 쓰면 오류는 나지 않지만 **정렬한 결과가 사라져서** 단계 2 의 gaeun 이벤트가 시각 순서가 아닙니다(10:14 다음에 10:12 가 아니라 서버 이벤트가 먼저 나옵니다).

**관제에서는**

- <mark>이벤트 하나씩이 아니라 사용자 단위의 사건으로 연결하면 담당자가 읽을 양이 줄어듭니다.</mark> 시간 기준 밖에 있는 이벤트는 따로 두고, 다른 사건과 섞이지 않게 합니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_6-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `score_findings` 안

```python
    points = findings_table["rule"].map(WEIGHTS)       # rule 열을 꺼내 바로 규칙마다 점수를 채운다(map)
    totals = grouped["points"].sum()                   # 그룹에서 points 열을 골라 바로 합계를 구한다(sum)
```

② `make_grade` 안

```python
    if score >= HIGH_LIMIT:                            # 점수가 high 기준 이상이면
        return "high"                                  # high 이다
```

③ `make_records` 안

```python
        record = {"entity": entity, "score": int(score), "grade": grade, "reasons": reasons[entity]}  # 대상 · 점수 · 등급 · 이유를 딕셔너리로 만든다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, high 는 <mark style="background:#bde3ff">**dami**</mark>, mid 는 <mark style="background:#bde3ff">**seoyeon · gaeun · jiwoo**</mark>, low 는 <mark style="background:#bde3ff">**198.51.100.90**</mark> 입니다.

```
--- 단계 1: 탐지된 규칙 8 건
--- 단계 2: 대상별 점수
entity
dami             60
seoyeon          45
gaeun            40
jiwoo            35
198.51.100.90    30
Name: points, dtype: int64
--- 단계 3: day03_risk_scores.json 에 5 건 저장
--- 단계 4: 등급 · 대상 · 점수 · 이유
high dami 60 ['퇴사한 계정']
mid seoyeon 45 ['평소와 다른 IP', '대량 다운로드']
mid gaeun 40 ['규칙은 허용인데 서버가 거절', '여러 로그 연결']
mid jiwoo 35 ['업무 시간 밖 로그인', '평소와 다른 IP']
low 198.51.100.90 30 ['경로 스캔']
```

- (나) seoyeon 의 45점은 <mark>평소와 다른 IP 20 + 대량 다운로드 25</mark> 를 더한 값입니다.
  - 이유를 함께 저장하는 까닭은 담당자가 점수만으로는 왜 올라왔는지 알 수 없기 때문입니다. 규칙 이름이 있으면 「평소와 다른 IP · 대량 다운로드(SaaS)」로 근거를 바로 설명하고, 기준을 바꿀 때 어떤 규칙이 영향을 주는지도 따질 수 있습니다.
- (다) 198.51.100.90 은 경로 스캔 30점뿐이라 <mark>mid 기준 35에 못 미쳐 low</mark> 입니다.
  - <mark>low 는 점수 기준상 낮은 등급이라는 뜻이고, 기록을 무시해도 된다는 뜻은 아닙니다.</mark> 샘플에서 이 IP 는 09:20:10 ~ 09:20:12 에 스캐너 경로 3종류를 요청했고 모두 실패했습니다. IP 에 적용되는 규칙은 경로 스캔(30점) 하나뿐이라 mid 기준 35 에 닿을 수 없어서 항상 low 입니다. 그래도 이 IP 의 이벤트는 다시 확인할 수 있게 남깁니다.

**왜**

- <mark>규칙이 겹칠수록 점수가 오릅니다.</mark> 사용자 하나에 여러 규칙이 겹치면 먼저 볼 이유가 늘고, 하나뿐이면 순서가 뒤로 갑니다. 이유를 같이 저장해 두면 그 순서를 설명할 수 있습니다.

**자주 틀리는 곳**

- `.sum()` 에서 괄호를 빼면 오류가 납니다. 괄호 없는 `grouped["points"].sum` 은 값이 아니라 메서드라서 다음 줄의 `totals.sort_values` 에서 `AttributeError` 가 납니다.
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`'function' object has no attribute 'sort_values'`</mark> 또는 비슷한 문구가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day04_6-1_run.py", line 11, in <module>
    totals = score_findings(findings)                      # 대상마다 점수를 더한다
  File "…/anomaly_detection/risk_scores.py", line 74, in score_findings
    totals = totals.sort_values(ascending=False)       # 점수가 높은 순으로 정렬한다 — 미리 채운 줄
AttributeError: 'function' object has no attribute 'sort_values'
```

  - 줄 번호는 사람마다 다릅니다.
- `make_grade` 는 **높은 기준부터 차례로 확인합니다.** high 기준을 먼저 확인하고, 아니면 mid 기준을 확인하는 순서입니다. 순서를 바꿔 mid 를 먼저 확인하면 높은 점수도 mid 가 됩니다.

**관제에서는**

- <mark>점수와 등급 기준은 정해 둔 날과 이유를 남깁니다.</mark> 기준을 바꾸면 같은 로그에서 등급이 달라지기 때문입니다. 내일(11/6(금))에는 이 등급이 맞았는지 오탐과 미탐을 직접 세어 봅니다.

---

### 정답 마무리

- (가) 예: 「`git status` 에 `.env` 와 `.venv` 는 보이지 않았다」. 보였다면 `.gitignore` 맨 아래에 한 줄을 적고 저장한 뒤 `git status` 를 다시 쳐서 사라졌는지 확인했다고 적습니다.
- 깃허브의 `anomaly_detection` 폴더에 오늘 오전과 오후 파일이 보이면 됩니다.

---

## 부록 · 오전 파일 완성본 (오전 파일을 완성하지 못했을 때만 씁니다)

오전 2 · 3 · 4교시 파일이 없거나 완성하지 못했다면 아래 완성본으로 파일을 만들어 오후를 이어 갑니다. 오전에 직접 풀었다면 이 부분은 건너뜁니다.

**`access_detection.py`** (오전 2교시 완성본)

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다
from rbac import check_permission                     # 3과목(접근통제)에서 만든 권한 판정 함수를 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
REPEAT_LIMIT = 3                                      # 한 사용자의 실패가 이 횟수 이상이면 먼저 확인한다
PRIORITY = {"퇴사한 계정": 1, "권한 없음": 2, "허용": 3}  # 판정 이유별로 우선순위(작을수록 먼저)


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_server_failures(events):                     # 이벤트 표를 받는 함수
    """판정 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    서버가 거절한 요청을 조사하기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_server = sources == "server"                   # 각 행이 판정 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                        # result 열만 꺼낸다
    is_fail = results == "실패"                       # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_server & is_fail                   # 두 조건이 모두 True 인 행만 True 로 만든다
    server_failures = events[both_true]               # True 인 행만 골라 새 표로 만든다
    return server_failures                            # 서버 실패 이벤트 표를 리턴한다


def pick_suspicious(server_failures):                 # 서버 실패 표를 받는 함수
    """실패가 반복된 사용자의 이벤트만 골라 새 표로 만든다.
    같은 사용자가 여러 번 거절당했는지 볼 때 쓴다.
    """
    users = server_failures["user"]                   # user 열만 꺼낸다
    user_counts = users.value_counts()                # 사용자마다 실패가 몇 번인지 센다
    is_many = user_counts >= REPEAT_LIMIT             # 사용자마다 실패 횟수가 REPEAT_LIMIT 이상인지 비교해 True 또는 False 를 만든다
    repeated_users = user_counts[is_many]             # 반복된 사용자와 횟수만 남긴다

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. repeated_users 의 .index 를 repeated_names 에 담는다
    repeated_names = repeated_users.index             # 반복된 사용자의 이름들(인덱스)을 꺼낸다
    # 2. users 가 repeated_names 안에 있는지 isin 으로 구해 is_repeated_user 에 담는다
    is_repeated_user = users.isin(repeated_names)     # 각 행의 사용자가 반복된 사용자 이름 안에 있는지 구해 True 또는 False 를 만든다
    # 3. server_failures 에서 is_repeated_user 가 True 인 행만 골라 suspicious 에 담는다
    suspicious = server_failures[is_repeated_user]    # True 인 행만 골라 새 표로 만든다
    return suspicious                                 # 먼저 확인할 실패 이벤트 표를 리턴한다


def judge_failure(user, action):                      # 사용자와 행동을 받는 함수
    """서버가 거절한 요청을 3과목(접근통제) 권한 규칙으로 다시 판정해 이유와 우선순위를 리턴한다.
    거절이 규칙대로인지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. action 을 ":" 기준으로 나눠 parts 에 담는다 (예: "SALES:QUERY" → ["SALES", "QUERY"]. 앞 조각이 자원, 뒤 조각이 행위)
    parts = action.split(":")                         # ":" 로 나눠 두 조각의 리스트로 만든다
    resource = parts[0]                               # 첫 번째 조각이 자원이다
    permission_action = parts[1]                      # 두 번째 조각이 행위이다

    # 5. check_permission 에 user, resource, permission_action 을 전달하고, 결과를 is_allowed 와 reason 에 나눠 담는다 (모양: is_allowed, reason = check_permission(...). is_allowed 는 이 문제에서 쓰지 않는다)
    is_allowed, reason = check_permission(user, resource, permission_action)  # 3과목(접근통제) 판정 결과를 허용 여부와 이유로 나눠 받는다
    # 6. PRIORITY 에서 reason 의 순서를 꺼내 priority 에 담는다 (딕셔너리에 없는 이유이면 4 — .get(reason, 4))
    priority = PRIORITY.get(reason, 4)                # 이유의 우선순위를 꺼낸다(없으면 4)
    return reason, priority                           # 판정 이유와 우선순위를 리턴한다
```

**`saas_detection.py`** (오전 3교시 완성본)

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
USUAL_IPS = {"seoyeon": "198.51.100.9", "junho": "192.0.2.41", "jiwoo": "198.51.100.52"}  # 사용자별 평소 IP. gaeun 은 평소 기록이 없어 넣지 않았다
BUSINESS_START = 8                                    # 업무 시간이 시작하는 시
BUSINESS_END = 20                                     # 업무 시간이 끝나는 시(20시대, 20:59 까지가 업무 시간)
DOWNLOAD_LIMIT = 5                                    # 파일을 이 횟수 이상 내려받으면 대량 다운로드로 본다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_saas(events):                                # 이벤트 표를 받는 함수
    """SaaS 로그의 이벤트만 골라 새 표로 만든다.
    SaaS 이상 사용을 찾기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_saas = sources == "saas"                       # 각 행이 SaaS 이벤트인지 비교해 True 또는 False 를 만든다
    saas = events[is_saas]                            # True 인 행만 골라 새 표로 만든다
    return saas                                       # SaaS 이벤트 표를 리턴한다


def pick_logins(saas):                                # SaaS 이벤트 표를 받는 함수
    """로그인 이벤트만 골라 새 표로 만든다.
    로그인 시각과 IP 를 살펴보기 전에 쓴다.
    """
    actions = saas["action"]                          # action 열만 꺼낸다
    is_login = actions == "login"                     # 각 행이 로그인인지 비교해 True 또는 False 를 만든다
    logins = saas[is_login]                           # True 인 행만 골라 새 표로 만든다
    return logins                                     # 로그인 이벤트 표를 리턴한다


def find_off_hours_logins(logins):                    # 로그인 표를 받는 함수
    """업무 시간 밖에 시도한 로그인만 골라 새 표로 만든다.
    새벽 로그인처럼 평소에 없는 시각을 찾을 때 쓴다.
    """
    times = pd.to_datetime(logins["time"])            # 문자열 시각을 시각 값으로 바꾼다 — 미리 채운 줄
    hours = times.dt.hour                             # 시각 값에서 시(0~23)만 꺼낸다 — 미리 채운 줄

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. hours 가 BUSINESS_START 이상 BUSINESS_END 이하인지 between 으로 구해 is_business_hour 에 담는다
    is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)  # 시가 업무 시간 안인지 구해 True 또는 False 를 만든다
    # 2. is_business_hour 의 반대를 ~ 로 구해 is_off_hours 에 담는다
    is_off_hours = ~is_business_hour                  # True 와 False 를 뒤집어 업무 시간 밖인 행을 True 로 만든다
    off_hours_logins = logins[is_off_hours]           # True 인 행만 골라 새 표로 만든다
    return off_hours_logins                           # 업무 시간 밖 로그인 표를 리턴한다


def find_new_ip_users(logins):                        # 로그인 표를 받는 함수
    """평소와 다른 IP 로 로그인한 사용자를 골라 리스트로 만든다.
    계정을 다른 사람이 쓰는지 의심할 때 쓴다.
    """
    new_ip_users = []                                 # 사용자를 담을 빈 리스트
    login_list = logins.to_dict("records")            # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                          # 로그인을 하나씩 꺼낸다
        user = login["user"]                          # 그 로그인의 사용자
        ip = login["ip"]                              # 그 로그인의 IP
        usual_ip = USUAL_IPS.get(user)                # 그 사용자의 평소 IP(기록이 없으면 None)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. usual_ip 가 None 이 아닌지 구해 has_usual_ip 에 담는다 (None 인지는 is None, 아닌지는 is not None)
        has_usual_ip = usual_ip is not None           # 평소 IP 기록이 있는지 구한다
        # 4. ip 가 usual_ip 와 다른지 != 로 구해 is_new_ip 에 담는다 (같은지는 ==, 다른지는 !=)
        is_new_ip = ip != usual_ip                    # 이번 IP 가 평소 IP 와 다른지 구한다
        if has_usual_ip and is_new_ip:                # 평소 IP 기록이 있고, 이번 IP 가 평소와 다르면
            # 5. new_ip_users 에 user 를 추가한다
            new_ip_users.append(user)                 # 리스트에 사용자를 추가한다
    return new_ip_users                               # 평소와 다른 IP 로 로그인한 사용자를 리턴한다


def find_bulk_download_users(saas):                   # SaaS 이벤트 표를 받는 함수
    """파일을 기준 횟수 이상 내려받은 사용자를 리스트로 만든다.
    자료를 한꺼번에 빼 가는 사용자를 찾을 때 쓴다.
    """
    actions = saas["action"]                          # action 열만 꺼낸다
    is_download = actions == "file.download"          # 각 행이 다운로드인지 비교해 True 또는 False 를 만든다
    downloads = saas[is_download]                     # True 인 행만 골라 새 표로 만든다
    counts = downloads.groupby("user").size()         # user 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size) — 사용자별 다운로드 횟수
    is_bulk = counts >= DOWNLOAD_LIMIT                # 사용자마다 횟수가 기준 이상인지 비교해 True 또는 False 를 만든다
    bulk_counts = counts[is_bulk]                     # 기준 이상인 사용자와 횟수만 남긴다
    bulk_users = list(bulk_counts.index)              # 사용자 이름만 리스트로 만든다
    return bulk_users                                 # 대량 다운로드 사용자를 리턴한다
```

**`malicious_detection.py`** (오전 4교시 완성본)

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
SCANNER_PATTERN = "/.env|/wp-login|/phpmyadmin"       # 스캐너가 자주 요청하는 경로. | 는 「또는」이라는 뜻이다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_web_failures(events):                        # 이벤트 표를 받는 함수
    """웹 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    경로 스캔 요청을 찾기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_web = sources == "web"                         # 각 행이 웹 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                        # result 열만 꺼낸다
    is_fail = results == "실패"                       # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_web & is_fail                      # 두 조건이 모두 True 인 행만 True 로 만든다
    web_failures = events[both_true]                  # True 인 행만 골라 새 표로 만든다
    return web_failures                               # 웹 실패 이벤트 표를 리턴한다


def find_scan_ips(web_failures):                      # 웹 실패 표를 받는 함수
    """스캐너가 요청하는 경로를 요청한 IP 와 요청 횟수를 찾는다.
    한 번의 오타 요청이나 로그인 실패만 있는 IP 를 거르고 경로 스캔만 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web_failures 의 "action" 열을 꺼내 actions 에 담는다
    actions = web_failures["action"]                  # action 열만 꺼낸다
    # 2. actions 에 .str.contains(SCANNER_PATTERN) 을 붙여 스캐너 경로가 들어 있는지 구해 is_scanner 에 담는다
    is_scanner = actions.str.contains(SCANNER_PATTERN)  # 각 행에 스캐너 경로가 들어 있는지 구해 True 또는 False 를 만든다
    # 3. web_failures 에서 is_scanner 가 True 인 행만 골라 scanner_rows 에 담는다
    scanner_rows = web_failures[is_scanner]           # True 인 행만 골라 새 표로 만든다
    # 4. scanner_rows 의 "ip" 열에 .value_counts() 를 붙여 IP 별로 몇 번 요청했는지 세어 scan_counts 에 담는다
    scan_counts = scanner_rows["ip"].value_counts()   # IP 별로 스캐너 경로를 몇 번 요청했는지 센다
    scan_ips = list(scan_counts.index)                # 스캔으로 보는 IP 이름만 리스트로 만든다
    return scan_ips, scan_counts                      # 스캔 IP 리스트와 IP 별 요청 횟수를 리턴한다


def explain_scan(ip, request_count):                  # IP 와 스캐너 경로 요청 횟수를 받는 함수
    """스캔으로 본 IP 하나를 담당자가 읽을 설명 딕셔너리로 만든다.
    왜 의심했는지 이유를 알림에 남길 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. "스캐너 경로를 " 와 str(request_count) 와 "번 요청" 을 + 로 연결해 reason 에 담는다 (문구는 복사해 붙여도 된다)
    reason = "스캐너 경로를 " + str(request_count) + "번 요청"  # 문자열을 연결해 이유 문장을 만든다
    # 6. 키 "ip" 에 ip, 키 "reason" 에 reason 을 담은 딕셔너리를 scan_info 에 담는다
    scan_info = {"ip": ip, "reason": reason}          # IP 와 이유를 딕셔너리로 만든다
    return scan_info                                  # 설명 딕셔너리를 리턴한다
```
