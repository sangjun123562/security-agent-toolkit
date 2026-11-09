# 11/9(월) 오전 · 4과목 이상탐지 ⑥ — 복구 파일 모음 (앞 수업 파일이 없는 사람만)

오늘 3교시(`pipeline.py`)는 11/5 에 만든 파일을 불러 씁니다. <mark>그 파일을 이미 가지고 있으면 이 문서는 받지 않아도 됩니다.</mark> 11/5 에 결석했거나 파일을 지웠거나 완성하지 못한 사람만, **없는 파일만** 아래 순서로 만듭니다.

- 이 문서의 파일은 모두 `anomaly_detection` 폴더 바로 아래에 둡니다. `config` 폴더 안의 두 파일만 예외입니다.
- 오늘 안내(`day06_am_ai_summary_pipeline.md`)의 📎 표에서 「복구 파일 모음」이라고 적힌 파일이 여기에 있습니다.
- 파일 내용은 11/5 안내의 완성본과 같습니다. 이미 가진 파일은 건너뛰고, 내 파일과 비교하는 데만 써도 됩니다.

| 파일 | 만든 곳 | 오늘 쓰는 곳 | 이 문서에서 |
|---|---|---|---|
| `normalized_events.json` | 11/3 에 만들고 11/5 오전에 다시 받은 이벤트 57개 | 3교시 | 2번 |
| `rbac.py` · `config/users.json` · `config/roles.json` | 3과목 권한 판정(11/5 오전 시작하기 6번) | 3교시 | 2번 |
| `access_detection.py` · `saas_detection.py` · `malicious_detection.py` | 11/5 오전 2 · 3 · 4교시 | 3교시 | 3번 |
| `correlation.py` · `risk_scores.py` | 11/5 오후 5 · 6교시 | 3교시 | 4번 |
| `llm_client.py` | 1과목 (`agent_core` 폴더) | 2 · 3교시 | 5번 (`agent_core` 에도 없을 때만) |

## 1. 폴더와 빈 파일 만들기

**[터미널]** 먼저 위치를 확인한 뒤 빈 파일을 만듭니다. 이미 있는 파일은 `touch` 가 그대로 두고, `config` 폴더가 이미 있으면 `mkdir` 가 「File exists」 라고 알려 주는데 그대로 넘어갑니다.

```bash
pwd
mkdir config
touch normalized_events.json rbac.py config/users.json config/roles.json
touch access_detection.py saas_detection.py malicious_detection.py correlation.py risk_scores.py
ls
```

- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `mkdir 폴더이름` 새 폴더 만들기 · `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 이름 보기
- <mark>`pwd` 가 `…/anomaly_detection` 으로 끝나야</mark> 합니다. 아니면 `cd anomaly_detection` 으로 이동한 뒤 다시 합니다.
- 없는 파일만 열어 붙여 넣습니다. **같은 이름의 파일이 이미 있으면 건너뜁니다.**

## 2. 이벤트와 권한 판정 파일 (11/5 오전 시작하기 6번)

**`normalized_events.json`** — 이벤트 샘플 57개입니다. 이벤트 날짜는 모두 2026-11-02 이고, `null` 은 그 값이 로그에 없다는 뜻입니다. 웹 서버 28 · 판정 서버 15 · SaaS 14 입니다.

```
[
  {"time": "2026-11-02 02:14:08", "source": "saas", "user": "jiwoo", "ip": "203.0.113.80", "action": "login", "result": "실패"},
  {"time": "2026-11-02 09:01:05", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /", "result": "성공"},
  {"time": "2026-11-02 09:01:06", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /static/app.css", "result": "성공"},
  {"time": "2026-11-02 09:03:47", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /login", "result": "성공"},
  {"time": "2026-11-02 09:03:59", "source": "web", "user": null, "ip": "198.51.100.34", "action": "POST /login", "result": "성공"},
  {"time": "2026-11-02 09:04:00", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:05:21", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /board?page=2", "result": "성공"},
  {"time": "2026-11-02 09:05:30", "source": "saas", "user": "seoyeon", "ip": "198.51.100.9", "action": "login", "result": "성공"},
  {"time": "2026-11-02 09:05:40", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /board/12", "result": "성공"},
  {"time": "2026-11-02 09:12:01", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /login", "result": "성공"},
  {"time": "2026-11-02 09:12:03", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:06", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:09", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:12", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:15", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:18", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "성공"},
  {"time": "2026-11-02 09:12:25", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /admin", "result": "실패"},
  {"time": "2026-11-02 09:12:27", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /admin/users", "result": "실패"},
  {"time": "2026-11-02 09:20:10", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /.env", "result": "실패"},
  {"time": "2026-11-02 09:20:11", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /wp-login.php", "result": "실패"},
  {"time": "2026-11-02 09:20:12", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /phpmyadmin", "result": "실패"},
  {"time": "2026-11-02 09:22:30", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board/99", "result": "실패"},
  {"time": "2026-11-02 09:25:02", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /report", "result": "실패"},
  {"time": "2026-11-02 09:26:44", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /search?q=network", "result": "성공"},
  {"time": "2026-11-02 09:28:13", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /", "result": "성공"},
  {"time": "2026-11-02 09:28:20", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:30:12", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "login", "result": "성공"},
  {"time": "2026-11-02 09:31:15", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:33:51", "source": "web", "user": null, "ip": "198.51.100.77", "action": "GET /admin", "result": "실패"},
  {"time": "2026-11-02 09:35:02", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /logout", "result": "성공"},
  {"time": "2026-11-02 09:36:10", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board/12", "result": "성공"},
  {"time": "2026-11-02 09:40:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 09:52:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:CHANGE", "result": "성공"},
  {"time": "2026-11-02 10:05:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 10:09:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 10:12:55", "source": "saas", "user": "gaeun", "ip": "198.51.100.77", "action": "login", "result": "성공"},
  {"time": "2026-11-02 10:14:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 11:02:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:03:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:05:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:CHANGE", "result": "실패"},
  {"time": "2026-11-02 11:08:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:25:40", "source": "saas", "user": "seoyeon", "ip": "198.51.100.9", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 11:40:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SETTLE:QUERY", "result": "실패"},
  {"time": "2026-11-02 13:15:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 13:50:21", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "file.upload", "result": "성공"},
  {"time": "2026-11-02 14:30:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:CHANGE", "result": "성공"},
  {"time": "2026-11-02 15:05:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 15:20:03", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "login", "result": "성공"},
  {"time": "2026-11-02 16:02:18", "source": "saas", "user": "jiwoo", "ip": "198.51.100.52", "action": "login", "result": "성공"},
  {"time": "2026-11-02 16:10:00", "source": "server", "user": "gaeun", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 17:38:10", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "login", "result": "성공"},
  {"time": "2026-11-02 17:40:02", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:40:31", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:41:05", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:41:48", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:42:20", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 18:20:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:CHANGE", "result": "실패"}
]
```

**`rbac.py`** — 3과목에서 만든 권한 판정 함수입니다.

```python
import json                                                      # JSON 파일을 읽는 모듈을 불러온다

with open("config/roles.json", encoding="utf-8") as roles_file:  # 역할 파일을 연다
    ROLES = json.load(roles_file)                                # 역할 → 권한 리스트 딕셔너리로 읽는다
with open("config/users.json", encoding="utf-8") as users_file:  # 사용자 파일을 연다
    USERS = json.load(users_file)                                # 사용자 → 정보 딕셔너리로 읽는다


def check_permission(user, resource, action):                    # 사용자 · 자원 · 행위를 받는 함수
    """요청을 허용할지 (허용 여부, 이유)로 리턴한다. 요청이 들어올 때 가장 먼저 쓰는 판정이고, 허용 리스트에 없으면 모두 거부한다."""
    if user not in USERS:                                        # 사용자 파일에 없는 계정이면
        return False, "등록되지 않은 사용자"                     # 바로 거부하고 함수를 끝낸다
    if not USERS[user]["employed"]:                              # 재직 중이 아니면
        return False, "퇴사한 계정"                              # 거부하고 함수를 끝낸다
    role = USERS[user]["role"]                                   # 이 사용자의 역할을 꺼낸다
    if role not in ROLES:                                        # 역할 파일에 없는 역할이면
        return False, "역할이 없음"                              # 거부하고 함수를 끝낸다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    if permission not in ROLES[role]:                            # 그 역할의 권한 리스트에 없으면
        return False, "권한 없음"                                # 거부하고 함수를 끝낸다
    return True, "허용"                                          # 모든 검사를 지나면 허용한다
```

**`config/users.json`**

```
{
  "seoyeon": {"role": "sales", "employed": true},
  "junho": {"role": "finance", "employed": true},
  "gaeun": {"role": "account_admin", "employed": true},
  "dami": {"role": "sales", "employed": false},
  "batch-night": {"role": "batch", "employed": true},
  "tester": {"role": "intern", "employed": true}
}
```

**`config/roles.json`**

```
{
  "sales": ["SALES:QUERY", "SALES:CHANGE"],
  "account_admin": ["ACCOUNT:QUERY", "ACCOUNT:CHANGE"],
  "finance": ["SALES:QUERY", "SETTLE:QUERY"],
  "batch": ["SETTLE:QUERY"],
  "auditor": ["SALES:QUERY", "SETTLE:QUERY", "ACCOUNT:QUERY"]
}
```

## 3. 탐지 파일 세 개 (11/5 오전 2 · 3 · 4교시 완성본)

**`access_detection.py`**

```python
import pandas as pd                                                           # 판다스를 pd 라는 짧은 이름으로 불러온다
from rbac import check_permission                                             # 3과목(접근통제)에서 만든 권한 판정 함수를 불러온다

EVENTS_PATH = "normalized_events.json"                                        # 읽을 정규화 이벤트 파일 이름
REPEAT_LIMIT = 3                                                              # 한 사용자의 실패가 이 횟수 이상이면 먼저 확인한다
PRIORITY = {"퇴사한 계정": 1, "권한 없음": 2, "허용": 3}                      # 판정 이유별로 우선순위(작을수록 먼저)


def load_events(path):                                                        # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                                               # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                                             # 이벤트 표를 리턴한다


def pick_server_failures(events):                                             # 이벤트 표를 받는 함수
    """판정 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    서버가 거절한 요청을 조사하기 전에 쓴다.
    """
    sources = events["source"]                                                # source 열만 꺼낸다
    is_server = sources == "server"                                           # 각 행이 판정 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                                                # result 열만 꺼낸다
    is_fail = results == "실패"                                               # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_server & is_fail                                           # 두 조건이 모두 True 인 행만 True 로 만든다
    server_failures = events[both_true]                                       # True 인 행만 골라 새 표로 만든다
    return server_failures                                                    # 서버 실패 이벤트 표를 리턴한다


def pick_suspicious(server_failures):                                         # 서버 실패 표를 받는 함수
    """실패가 반복된 사용자의 이벤트만 골라 새 표로 만든다.
    같은 사용자가 여러 번 거절당했는지 볼 때 쓴다.
    """
    users = server_failures["user"]                                           # user 열만 꺼낸다
    user_counts = users.value_counts()                                        # 사용자마다 실패가 몇 번인지 센다
    is_many = user_counts >= REPEAT_LIMIT                                     # 사용자마다 실패 횟수가 REPEAT_LIMIT 이상인지 비교해 True 또는 False 를 만든다
    repeated_users = user_counts[is_many]                                     # 반복된 사용자와 횟수만 남긴다

    repeated_names = repeated_users.index                                     # 반복된 사용자의 이름들(인덱스)을 꺼낸다
    is_repeated_user = users.isin(repeated_names)                             # 각 행의 사용자가 반복된 사용자 이름 안에 있는지 구해 True 또는 False 를 만든다
    suspicious = server_failures[is_repeated_user]                            # True 인 행만 골라 새 표로 만든다
    return suspicious                                                         # 먼저 확인할 실패 이벤트 표를 리턴한다


def judge_failure(user, action):                                              # 사용자와 행동을 받는 함수
    """서버가 거절한 요청을 3과목(접근통제) 권한 규칙으로 다시 판정해 이유와 우선순위를 리턴한다.
    거절이 규칙대로인지 확인할 때 쓴다.
    """
    parts = action.split(":")                                                 # ":" 로 나눠 두 조각의 리스트로 만든다
    resource = parts[0]                                                       # 첫 번째 조각이 자원이다
    permission_action = parts[1]                                              # 두 번째 조각이 행위이다

    is_allowed, reason = check_permission(user, resource, permission_action)  # 3과목(접근통제) 판정 결과를 허용 여부와 이유로 나눠 받는다
    priority = PRIORITY.get(reason, 4)                                        # 이유의 우선순위를 꺼낸다(없으면 4)
    return reason, priority                                                   # 판정 이유와 우선순위를 리턴한다
```

**`saas_detection.py`**

```python
import pandas as pd                                                                       # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                                                    # 읽을 정규화 이벤트 파일 이름
USUAL_IPS = {"seoyeon": "198.51.100.9", "junho": "192.0.2.41", "jiwoo": "198.51.100.52"}  # 사용자별 평소 IP. gaeun 은 평소 기록이 없어 넣지 않았다
BUSINESS_START = 8                                                                        # 업무 시간이 시작하는 시
BUSINESS_END = 20                                                                         # 업무 시간이 끝나는 시(20시대, 20:59 까지가 업무 시간)
DOWNLOAD_LIMIT = 5                                                                        # 파일을 이 횟수 이상 내려받으면 대량 다운로드로 본다


def load_events(path):                                                                    # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                                                           # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                                                         # 이벤트 표를 리턴한다


def pick_saas(events):                                                                    # 이벤트 표를 받는 함수
    """SaaS 로그의 이벤트만 골라 새 표로 만든다.
    SaaS 이상 사용을 찾기 전에 쓴다.
    """
    sources = events["source"]                                                            # source 열만 꺼낸다
    is_saas = sources == "saas"                                                           # 각 행이 SaaS 이벤트인지 비교해 True 또는 False 를 만든다
    saas = events[is_saas]                                                                # True 인 행만 골라 새 표로 만든다
    return saas                                                                           # SaaS 이벤트 표를 리턴한다


def pick_logins(saas):                                                                    # SaaS 이벤트 표를 받는 함수
    """로그인 이벤트만 골라 새 표로 만든다.
    로그인 시각과 IP 를 살펴보기 전에 쓴다.
    """
    actions = saas["action"]                                                              # action 열만 꺼낸다
    is_login = actions == "login"                                                         # 각 행이 로그인인지 비교해 True 또는 False 를 만든다
    logins = saas[is_login]                                                               # True 인 행만 골라 새 표로 만든다
    return logins                                                                         # 로그인 이벤트 표를 리턴한다


def find_off_hours_logins(logins):                                                        # 로그인 표를 받는 함수
    """업무 시간 밖에 시도한 로그인만 골라 새 표로 만든다.
    새벽 로그인처럼 평소에 없는 시각을 찾을 때 쓴다.
    """
    times = pd.to_datetime(logins["time"])                                                # 문자열 시각을 시각 값으로 바꾼다 — 미리 채운 줄
    hours = times.dt.hour                                                                 # 시각 값에서 시(0~23)만 꺼낸다 — 미리 채운 줄

    is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)                        # 시가 업무 시간 안인지 구해 True 또는 False 를 만든다
    is_off_hours = ~is_business_hour                                                      # True 와 False 를 뒤집어 업무 시간 밖인 행을 True 로 만든다
    off_hours_logins = logins[is_off_hours]                                               # True 인 행만 골라 새 표로 만든다
    return off_hours_logins                                                               # 업무 시간 밖 로그인 표를 리턴한다


def find_new_ip_users(logins):                                                            # 로그인 표를 받는 함수
    """평소와 다른 IP 로 로그인한 사용자를 골라 리스트로 만든다.
    계정을 다른 사람이 쓰는지 의심할 때 쓴다.
    """
    new_ip_users = []                                                                     # 사용자를 담을 빈 리스트
    login_list = logins.to_dict("records")                                                # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                                                              # 로그인을 하나씩 꺼낸다
        user = login["user"]                                                              # 그 로그인의 사용자
        ip = login["ip"]                                                                  # 그 로그인의 IP
        usual_ip = USUAL_IPS.get(user)                                                    # 그 사용자의 평소 IP(기록이 없으면 None)
        has_usual_ip = usual_ip is not None                                               # 평소 IP 기록이 있는지 구한다
        is_new_ip = ip != usual_ip                                                        # 이번 IP 가 평소 IP 와 다른지 구한다
        if has_usual_ip and is_new_ip:                                                    # 평소 IP 기록이 있고, 이번 IP 가 평소와 다르면
            new_ip_users.append(user)                                                     # 리스트에 사용자를 추가한다
    return new_ip_users                                                                   # 평소와 다른 IP 로 로그인한 사용자를 리턴한다


def find_bulk_download_users(saas):                                                       # SaaS 이벤트 표를 받는 함수
    """파일을 기준 횟수 이상 내려받은 사용자를 리스트로 만든다.
    자료를 한꺼번에 빼 가는 사용자를 찾을 때 쓴다.
    """
    actions = saas["action"]                                                              # action 열만 꺼낸다
    is_download = actions == "file.download"                                              # 각 행이 다운로드인지 비교해 True 또는 False 를 만든다
    downloads = saas[is_download]                                                         # True 인 행만 골라 새 표로 만든다
    counts = downloads.groupby("user").size()                                             # user 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size) — 사용자별 다운로드 횟수
    is_bulk = counts >= DOWNLOAD_LIMIT                                                    # 사용자마다 횟수가 기준 이상인지 비교해 True 또는 False 를 만든다
    bulk_counts = counts[is_bulk]                                                         # 기준 이상인 사용자와 횟수만 남긴다
    bulk_users = list(bulk_counts.index)                                                  # 사용자 이름만 리스트로 만든다
    return bulk_users                                                                     # 대량 다운로드 사용자를 리턴한다
```

**`malicious_detection.py`**

```python
import pandas as pd                                             # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                          # 읽을 정규화 이벤트 파일 이름
SCANNER_PATTERN = "/.env|/wp-login|/phpmyadmin"                 # 스캐너가 자주 요청하는 경로. | 는 「또는」이라는 뜻이다


def load_events(path):                                          # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                                 # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                               # 이벤트 표를 리턴한다


def pick_web_failures(events):                                  # 이벤트 표를 받는 함수
    """웹 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    경로 스캔 요청을 찾기 전에 쓴다.
    """
    sources = events["source"]                                  # source 열만 꺼낸다
    is_web = sources == "web"                                   # 각 행이 웹 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                                  # result 열만 꺼낸다
    is_fail = results == "실패"                                 # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_web & is_fail                                # 두 조건이 모두 True 인 행만 True 로 만든다
    web_failures = events[both_true]                            # True 인 행만 골라 새 표로 만든다
    return web_failures                                         # 웹 실패 이벤트 표를 리턴한다


def find_scan_ips(web_failures):                                # 웹 실패 표를 받는 함수
    """스캐너가 요청하는 경로를 요청한 IP 와 요청 횟수를 찾는다.
    한 번의 오타 요청이나 로그인 실패만 있는 IP 를 거르고 경로 스캔만 가려낼 때 쓴다.
    """
    actions = web_failures["action"]                            # action 열만 꺼낸다
    is_scanner = actions.str.contains(SCANNER_PATTERN)          # 각 행에 스캐너 경로가 들어 있는지 구해 True 또는 False 를 만든다
    scanner_rows = web_failures[is_scanner]                     # True 인 행만 골라 새 표로 만든다
    scan_counts = scanner_rows["ip"].value_counts()             # IP 별로 스캐너 경로를 몇 번 요청했는지 센다
    scan_ips = list(scan_counts.index)                          # 스캔으로 보는 IP 이름만 리스트로 만든다
    return scan_ips, scan_counts                                # 스캔 IP 리스트와 IP 별 요청 횟수를 리턴한다


def explain_scan(ip, request_count):                            # IP 와 스캐너 경로 요청 횟수를 받는 함수
    """스캔으로 본 IP 하나를 담당자가 읽을 설명 딕셔너리로 만든다.
    왜 의심했는지 이유를 알림에 남길 때 쓴다.
    """
    reason = "스캐너 경로를 " + str(request_count) + "번 요청"  # 문자열을 연결해 이유 문장을 만든다
    scan_info = {"ip": ip, "reason": reason}                    # IP 와 이유를 딕셔너리로 만든다
    return scan_info                                            # 설명 딕셔너리를 리턴한다
```

## 4. 연결과 점수 파일 두 개 (11/5 오후 5 · 6교시 완성본)

**`correlation.py`**

```python
import pandas as pd                                                          # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins                            # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures                            # 4교시 함수를 불러온다

MIN_SOURCES = 2                                                              # 서로 다른 로그(source)가 이 개수 이상이면 연결된 것으로 본다
WINDOW_MINUTES = 60                                                          # 한 사용자의 이벤트가 이 분 안에 모여 있어야 연결된 것으로 본다


def make_ip_user_map(logins):                                                # SaaS 로그인 표를 받는 함수
    """성공한 SaaS 로그인에서 IP 마다 사용자를 찾아 딕셔너리로 만든다.
    웹 서버 로그에는 사용자가 없어서 IP 로 사용자를 찾을 때 쓴다.
    """
    ip_user = {}                                                             # IP → 사용자 딕셔너리
    login_list = logins.to_dict("records")                                   # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                                                 # 로그인을 하나씩 꺼낸다
        if login["result"] == "성공":                                        # 성공한 로그인이면
            ip_user[login["ip"]] = login["user"]                             # 그 IP 의 사용자를 딕셔너리에 담는다
    return ip_user                                                           # IP → 사용자 딕셔너리를 리턴한다


def attach_user_to_web(web_failures, ip_user):                               # 웹 실패 표와 IP → 사용자 딕셔너리를 받는 함수
    """IP 로 사용자를 알 수 있는 웹 실패 이벤트에 user 열을 붙인다.
    웹 로그를 서버 · SaaS 로그와 같은 사용자 기준으로 연결해 분석할 때 쓴다.
    """
    ips = web_failures["ip"]                                                 # ip 열만 꺼낸다
    known_ips = list(ip_user)                                                # 딕셔너리의 키(IP)만 리스트로 만든다
    is_known = ips.isin(known_ips)                                           # 행마다 사용자를 아는 IP 인지 구해 True 또는 False 를 만든다
    known_web = web_failures[is_known]                                       # True 인 행만 골라 새 표를 만든다
    web_part = known_web.copy()                                              # 원본을 바꾸지 않도록 복사한다 — 미리 채운 줄

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    users = web_part["ip"].map(ip_user)
    web_part["user"] = users                                                 # 표에 user 열을 붙인다 — 미리 채운 줄
    return web_part                                                          # user 열이 붙은 웹 이벤트 표를 리턴한다


def build_timeline(server_part, saas_part, web_part):                        # 세 로그의 표를 받는 함수
    """세 로그의 표를 하나로 합쳐 사용자 · 시각 순으로 정렬하고, 하루 중 몇 분인지 열을 붙인다.
    사용자마다 서로 다른 로그의 이벤트를 시간순으로 놓고 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    timeline = pd.concat([server_part, saas_part, web_part])
    timeline = timeline.sort_values(["user", "time"])
    times = pd.to_datetime(timeline["time"])                                 # 문자열 시각을 시각 값으로 바꾼다
    hours = times.dt.hour                                                    # 시각 값에서 시(0~23)만 꺼낸다
    minutes = times.dt.minute                                                # 시각 값에서 분(0~59)만 꺼낸다
    timeline["minute_of_day"] = hours * 60 + minutes                         # 자정부터 몇 분이 지났는지 열을 붙인다 — 미리 채운 줄
    return timeline                                                          # 정렬된 이벤트 표를 리턴한다


def find_chains(timeline):                                                   # 정렬된 이벤트 표를 받는 함수
    """서로 다른 로그가 짧은 시간 안에 한 사용자에게 모여 있는 사건을 찾는다.
    이벤트 하나씩이 아니라 한 사용자의 사건으로 연결해 분석할 때 쓴다.
    """
    grouped = timeline.groupby("user")                                       # user 가 같은 행끼리 그룹으로 만든다
    source_counts = grouped["source"].nunique()                              # 그룹마다 서로 다른 로그(source)가 몇 종류인지 센다
    latest = grouped["minute_of_day"].max()                                  # 그룹마다 가장 늦은 시각(분)을 구한다
    earliest = grouped["minute_of_day"].min()                                # 그룹마다 가장 이른 시각(분)을 구한다
    spans = latest - earliest                                                # 그룹마다 처음부터 마지막까지 몇 분인지 구한다

    chains = []                                                              # 연결된 사건을 담을 빈 리스트
    not_chained = []                                                         # 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자 정보
    for user in source_counts.index:                                         # 사용자를 하나씩 꺼낸다
        source_count = source_counts[user]                                   # 그 사용자의 로그 종류 수
        span = spans[user]                                                   # 그 사용자의 처음부터 마지막까지 분
        has_many_sources = source_count >= MIN_SOURCES                       # 로그 종류가 기준 이상인지 구한다
        is_close = span <= WINDOW_MINUTES                                    # 시간 간격이 기준 이내인지 구한다
        if has_many_sources and is_close:                                    # 로그 종류도 충분하고 60분 이내이면 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            reason = "서로 다른 로그 " + str(source_count) + "종류 · " + str(span) + "분 안"
            chains.append({"user": user, "reason": reason})
        if has_many_sources and not is_close:                                # 로그 종류는 여럿인데 시간 차가 60분을 초과하면 — 미리 채운 줄
            not_chained.append({"user": user, "source_count": int(source_count), "span_minutes": int(span)})  # 연결되지 않은 사용자와 두 숫자를 추가한다
    return chains, not_chained                                               # 연결된 사건과 연결되지 않은 사용자를 리턴한다


def find_chains_in_events(events):                                           # 이벤트 표를 받는 함수
    """이벤트 표 하나로 위 함수를 차례로 불러 연결된 사건 리스트를 만든다.
    6교시에서 점수를 매기기 전에 한 번에 쓴다.
    """
    server_failures = pick_server_failures(events)                           # 판정 서버 실패 이벤트를 고른다
    server_part = server_failures                                            # 서버 실패 이벤트 전체를 쓴다
    saas_part = pick_saas(events)                                            # SaaS 이벤트를 고른다
    logins = pick_logins(saas_part)                                          # 로그인 이벤트를 고른다
    ip_user = make_ip_user_map(logins)                                       # IP → 사용자 딕셔너리를 만든다
    web_failures = pick_web_failures(events)                                 # 웹 실패 이벤트를 고른다
    web_part = attach_user_to_web(web_failures, ip_user)                     # 사용자를 아는 웹 이벤트에 user 열을 붙인다
    timeline = build_timeline(server_part, saas_part, web_part)              # 세 로그를 합쳐 정렬한다
    chains, not_chained = find_chains(timeline)                              # 연결된 사건을 찾는다
    return chains                                                            # 연결된 사건 리스트를 리턴한다
```

**`risk_scores.py`**

```python
import json                                                               # 점수를 JSON 파일로 쓰기 위해 json 을 불러온다
import pandas as pd                                                       # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users  # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures, find_scan_ips          # 4교시 함수를 불러온다

RISK_PATH = "day03_risk_scores.json"                                      # 점수를 저장할 파일 이름
HIGH_LIMIT = 60                                                           # 점수가 이 값 이상이면 high
MID_LIMIT = 35                                                            # 점수가 이 값 이상이면 mid, 그보다 낮으면 low
WEIGHTS = {"퇴사한 계정": 60, "권한 없음": 20, "규칙은 허용인데 서버가 거절": 10,
           "업무 시간 밖 로그인": 15, "평소와 다른 IP": 20, "대량 다운로드": 25,
           "경로 스캔": 30, "여러 로그 연결": 30}                         # 탐지된 규칙마다 점수
SERVER_RULES = {"퇴사한 계정": "퇴사한 계정", "권한 없음": "권한 없음", "허용": "규칙은 허용인데 서버가 거절"}  # 서버 판정 이유를 규칙 이름으로 바꾼다


def add_finding(findings, entity, rule):                                  # 리스트 · 대상 · 규칙 이름을 받는 함수
    """대상과 탐지된 규칙을 한 건 추가하되 같은 건은 한 번만 추가한다.
    같은 규칙이 여러 이벤트에 해당해도 점수가 중복되지 않게 할 때 쓴다.
    """
    finding = {"entity": entity, "rule": rule}                            # 대상과 규칙을 딕셔너리로 만든다
    if finding not in findings:                                           # 아직 없는 건이면
        findings.append(finding)                                          # 리스트에 추가한다


def collect_findings(events, chains):                                     # 이벤트 표와 연결된 사건을 받는 함수
    """오전 탐지 3개와 5교시 연결 결과를 (대상, 탐지된 규칙) 리스트로 모은다.
    점수를 매기기 전에 한 번에 쓴다.
    """
    findings = []                                                         # 탐지된 규칙을 담을 빈 리스트

    server_failures = pick_server_failures(events)                        # 판정 서버 실패 이벤트를 고른다
    suspicious = pick_suspicious(server_failures)                         # 먼저 확인할 서버 이벤트를 고른다
    suspicious_list = suspicious.to_dict("records")                       # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for event in suspicious_list:                                         # 이벤트를 하나씩 꺼낸다
        reason, priority = judge_failure(event["user"], event["action"])  # 3과목 규칙으로 다시 판정한다
        rule = SERVER_RULES.get(reason, reason)                           # 판정 이유를 규칙 이름으로 바꾼다
        add_finding(findings, event["user"], rule)                        # 사용자와 규칙을 추가한다

    saas = pick_saas(events)                                              # SaaS 이벤트를 고른다
    logins = pick_logins(saas)                                            # 로그인 이벤트를 고른다
    off_hours_logins = find_off_hours_logins(logins)                      # 업무 시간 밖 로그인을 찾는다
    off_hours_users = list(off_hours_logins["user"])                      # 그 로그인의 사용자 이름만 리스트로 만든다
    new_ip_users = find_new_ip_users(logins)                              # 평소와 다른 IP 로 로그인한 사용자를 찾는다
    bulk_users = find_bulk_download_users(saas)                           # 대량 다운로드 사용자를 찾는다
    for user in off_hours_users:                                          # 업무 시간 밖 로그인 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "업무 시간 밖 로그인")                # 사용자와 규칙을 추가한다
    for user in new_ip_users:                                             # 평소와 다른 IP 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "평소와 다른 IP")                     # 사용자와 규칙을 추가한다
    for user in bulk_users:                                               # 대량 다운로드 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "대량 다운로드")                      # 사용자와 규칙을 추가한다

    web_failures = pick_web_failures(events)                              # 웹 실패 이벤트를 고른다
    scan_ips, many_kinds = find_scan_ips(web_failures)                    # 경로 스캔 IP 를 찾는다
    for ip in scan_ips:                                                   # 스캔 IP 를 하나씩 꺼낸다
        add_finding(findings, ip, "경로 스캔")                            # IP 와 규칙을 추가한다

    for chain in chains:                                                  # 연결된 사건을 하나씩 꺼낸다
        add_finding(findings, chain["user"], "여러 로그 연결")            # 사용자와 규칙을 추가한다
    return findings                                                       # 탐지된 규칙 리스트를 리턴한다


def score_findings(findings):                                             # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙의 점수를 더해 점수가 높은 순으로 정렬한다.
    어느 대상부터 볼지 순서를 정할 때 쓴다.
    """
    findings_table = pd.DataFrame(findings)                               # 딕셔너리 리스트를 표로 만든다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    points = findings_table["rule"].map(WEIGHTS)
    findings_table["points"] = points                                     # 표에 points 열을 붙인다 — 미리 채운 줄
    grouped = findings_table.groupby("entity")                            # entity 가 같은 행끼리 그룹으로 만든다
    totals = grouped["points"].sum()
    totals = totals.sort_values(ascending=False)                          # 점수가 높은 순으로 정렬한다 — 미리 채운 줄
    return totals                                                         # 대상별 점수를 리턴한다


def make_grade(score):                                                    # 점수를 받는 함수
    """점수로 high · mid · low 등급을 정한다.
    점수가 높은 대상부터 먼저 보게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    if score >= HIGH_LIMIT:
        return "high"
    if score >= MID_LIMIT:                                                # 점수가 mid 기준 이상이면 — 미리 채운 줄 (위 high 와 같은 모양)
        return "mid"                                                      # mid 이다 — 미리 채운 줄
    return "low"                                                          # 둘 다 아니면 low 이다


def collect_reasons(findings):                                            # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙 이름을 모아 딕셔너리로 만든다.
    왜 그 등급인지 이유를 함께 저장할 때 쓴다.
    """
    reasons = {}                                                          # 대상 → 규칙 이름 리스트 딕셔너리
    for finding in findings:                                              # 탐지된 규칙을 하나씩 꺼낸다
        entity = finding["entity"]                                        # 그 건의 대상
        if entity not in reasons:                                         # 처음 나온 대상이면
            reasons[entity] = []                                          # 빈 리스트를 만든다
        reasons[entity].append(finding["rule"])                           # 그 대상의 규칙 이름을 추가한다
    return reasons                                                        # 대상별 규칙 이름을 리턴한다


def make_records(totals, reasons):                                        # 대상별 점수와 이유를 받는 함수
    """대상마다 점수 · 등급 · 이유를 담은 딕셔너리 리스트를 만든다.
    담당자가 읽을 파일의 내용을 만들 때 쓴다.
    """
    records = []                                                          # 기록을 담을 빈 리스트
    for entity, score in totals.items():                                  # 대상과 점수를 한 쌍씩 꺼낸다
        grade = make_grade(score)                                         # 점수로 등급을 정한다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        record = {"entity": entity, "score": int(score), "grade": grade, "reasons": reasons[entity]}
        records.append(record)                                            # 기록을 리스트에 추가한다
    return records                                                        # 기록 리스트를 리턴한다


def save_records(records, path):                                          # 기록 리스트와 파일 경로를 받는 함수
    """기록 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다.
    담당자와 다른 프로그램이 같은 파일을 읽게 할 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                       # path 파일을 쓰기 모드로 연다
        json.dump(records, file, ensure_ascii=False, indent=2)            # 한글은 그대로, 줄을 나눠 저장한다
    saved_count = len(records)                                            # 저장한 기록이 몇 건인지 센다
    return saved_count                                                    # 저장한 건수를 리턴한다
```

## 5. LLM 호출 파일 (1과목, `agent_core` 에도 없을 때만)

먼저 `cp ../agent_core/llm_client.py .` 로 복사해 봅니다. <mark>복사되지 않을 때만</mark> 아래 코드로 `llm_client.py` 를 만듭니다. API 키는 `security-agent-toolkit` 폴더 바로 아래의 `.env` 에 있어야 하고, 이 문서로는 만들 수 없습니다.

**`llm_client.py`**

```python
import json                                                       # JSON 문자열 ↔ 딕셔너리를 바꾸는 도구
import os                                                         # 폴더 · 파일을 다루는 도구
import requests                                                   # 인터넷으로 요청을 보내는 도구 (9/30)

# Gemini 에 요청을 보낼 주소
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.5-flash-lite"                                   # 쓸 모델 이름


def find_env():                                                   # .env 를 지금 폴더부터 위쪽으로 찾는 함수
    folder = os.getcwd()                                          # 지금 폴더에서 시작한다
    for i in range(5):                                            # 지금 폴더에서 다섯 칸 위까지 찾습니다
        path = os.path.join(folder, ".env")                       # 그 폴더 안의 .env 경로를 만든다
        if os.path.exists(path):                                  # 그 파일이 있으면
            return path                                           # 찾은 경로를 리턴한다
        folder = os.path.dirname(folder)                          # 한 칸 위 폴더
    return None                                                   # None 을 리턴하고 여기서 끝낸다


def read_api_key():                                               # .env 에서 키를 읽어 리턴하는 함수
    api_key = None                                                # 키를 못 찾으면 None 으로 남는다
    with open(find_env(), encoding="utf-8") as f:                 # .env 를 찾아 읽기로 연다
        for line in f:                                            # 파일을 한 줄씩 꺼낸다
            parts = line.strip().split("=", 1)                    # 줄 끝 공백을 지우고 = 에서 둘로 나눈다
            if parts[0] == "GEMINI_API_KEY":                      # = 앞부분이 키 이름이면
                api_key = parts[1]                                # = 뒷부분이 키 값이다
    return api_key                                                # 읽은 키를 리턴한다


def call_llm(question):                                           # 질문을 받아 답 문장을 리턴하는 함수
    # 요청 헤더 — .env 에서 읽은 키를 넣는다
    headers = {"Authorization": "Bearer " + read_api_key(), "Content-Type": "application/json"}
    # 요청 본문 — 모델 · temperature 0 · 질문
    body = {"model": MODEL, "temperature": 0, "messages": [{"role": "user", "content": question}]}
    # POST 요청을 보낸다. 30초 안에 답이 없으면 멈춘다
    response = requests.post(URL, headers=headers, json=body, timeout=30)
    if response.status_code != 200:                               # 200(성공)이 아니면
        print("[LLM 호출 실패] 상태 코드", response.status_code)  # 429 면 1분 기다린 뒤 다시 실행
        return ""                                                 # 실패하면 빈 문자열을 리턴한다
    data = response.json()                                        # 응답(JSON 문자열)을 딕셔너리로 바꾼다
    return data["choices"][0]["message"]["content"]               # 답 문장만 리턴한다


def parse_llm_json(text):                                         # LLM 의 답을 딕셔너리로 바꾸는 함수. 못 읽으면 None
    clean = text.replace("```json", "")                           # 코드 블록 표시 ```json 을 지운다
    clean = clean.replace("```", "")                              # 남은 ``` 를 지운다
    clean = clean.strip()                                         # 앞뒤 공백 · 줄바꿈을 지운다

    try:                                                          # 아래 줄을 해 본다
        return json.loads(clean)                                  # 문자열을 딕셔너리로 바꿔 리턴한다
    except json.JSONDecodeError:                                  # JSON 으로 읽지 못하면 여기로 온다
        return None                                               # None 을 리턴하고 여기서 끝낸다
```

## 6. 확인하기

**[터미널]** 아래 네 명령을 하나씩 칩니다(맥북은 `python3`). 결과가 나온 줄과 같으면 됩니다.

```bash
python -c "import json; print(len(json.load(open('normalized_events.json', encoding='utf-8'))))"
```

- <mark>`57` 이 나와야</mark> 합니다.

```bash
python -c "from access_detection import load_events, EVENTS_PATH; from saas_detection import pick_saas; from malicious_detection import pick_web_failures"
```

- 아무것도 나오지 않으면 됩니다. `ModuleNotFoundError` 가 나오면 그 파일이 없거나 이름이 다른 것입니다.

```bash
python -c "from correlation import find_chains_in_events; from risk_scores import collect_findings, save_records"
```

- 아무것도 나오지 않으면 됩니다.

```bash
python -c "from access_detection import load_events, EVENTS_PATH; from correlation import find_chains_in_events; from risk_scores import collect_findings; events = load_events(EVENTS_PATH); chains = find_chains_in_events(events); findings = collect_findings(events, chains); print(len(findings))"
```

- <mark>`8` 이 나와야</mark> 합니다. 11/5 오후에 탐지된 규칙이 8건이었던 것과 같습니다. 다르면 위 2 ~ 4번의 파일 가운데 붙여 넣은 내용이 빠졌거나 다른 곳이 있는지 봅니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다. `config` 안의 두 파일은 `ls config` 로 봅니다.
- `No module named 'pandas'`: <mark>가상환경이 활성화되지 않은 터미널입니다</mark>. `security-agent-toolkit` 폴더에서 가상환경을 활성화한 뒤(`source .venv/Scripts/activate`, 맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 다르면 그 이름으로) `python -m pip install pandas` 를 칩니다.
- `json.decoder.JSONDecodeError` 나 `ValueError`: 붙여 넣은 JSON 파일의 쉼표나 대괄호가 빠진 것입니다. 파일을 지우고 다시 붙여 넣습니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 풀리지 않으면 오늘 안내의 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.
