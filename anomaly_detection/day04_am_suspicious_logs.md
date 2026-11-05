# 11/5(목) 오전 · 4과목 이상탐지 ④ — 서버가 거절한 요청 · SaaS 이상 사용 · 웹 경로 스캔 — 실습

어제는 로그인 실패 횟수로 알림 기준을 정하고, 이벤트의 유형을 나눴습니다. 오늘 오전에는 **로그 종류마다 먼저 확인할 일을 찾는 탐지**를 하나씩(서버 · SaaS · 웹) 만듭니다. 로그마다 의심스러운 기록의 특징이 다르기 때문에 탐지는 로그 종류마다 따로 만들고, <mark>**한 교시에 기준(질문) 하나씩만**</mark> 봅니다. 이렇게 기준을 나눠 두면 **오탐(false positive, 폴스 포지티브: 문제가 아닌데 알림이 난 것)** 을 줄이고 담당자가 확인할 순서를 정하기 쉽습니다.

- **2교시**: 판정 서버가 거절한 요청 9개 중 **한 사용자가 3번 이상 거절당한 기록**을 고르고, 3과목(접근통제)에서 만든 권한 판정 함수(`check_permission`)로 거절 이유를 붙여 **순서**를 정합니다.
- **3교시**: SaaS 로그에서 **업무 시간 밖 로그인 · 평소와 다른 IP · 파일 대량 다운로드**를 규칙마다 따로 찾습니다.
- **4교시**: 웹 로그에서 **스캔(scan, 스캔: 해킹 도구가 여러 경로를 차례로 요청해 접근할 수 있는 곳을 찾는 일)을 한 IP**를 찾습니다. 해킹 도구가 자주 요청하는 경로를 요청한 IP 만 고르고, 그런 경로가 없는 실패 요청은 제외합니다. 마지막에 오전 탐지 3개를 한 번에 돌려 봅니다.

오늘은 오전 2 · 3 · 4교시이고, <mark>깃허브에 올리는 일은 오후 6교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 오전에 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널**입니다.
- 코드 줄은 판다스로 쓰는 줄과 파이썬으로 쓰는 줄이 섞여 있습니다. 표를 읽고 필터링하고 세는 줄이 판다스이고, 판단 · 딕셔너리 · 리스트 · 함수 호출이 파이썬입니다.
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 출력이나 샘플 데이터의 값을 근거로 이유까지 서술합니다</mark>.
- 오늘 정하는 기준 숫자(`REPEAT_LIMIT` 3 · `DOWNLOAD_LIMIT` 5 · 업무 시간 8 ~ 20시)는 **고정**하고, <mark>값을 바꿔 가며 비교하지 않습니다</mark>.

📎 **오늘 불러 쓰는 이전 파일**

| 파일 | 어디서 만들었나 | 오늘 쓰는 곳 |
|---|---|---|
| `rbac.py` · `config/users.json` · `config/roles.json` | 3과목(접근통제) 10/21(수) 오후 (권한 판정) | 2교시 `judge_failure` 가 `check_permission` 을 불러 씁니다 |
| `normalized_events.json` | 4과목 11/3(화) 오전 (정규화한 이벤트 57개) | 2 · 3 · 4교시 모두 읽습니다 |

3과목(접근통제) 파일 세 개는 오늘 <mark>**완성본을 아래 시작하기에 그대로 제공**</mark>합니다. 3과목(접근통제)에서 직접 만들었어도, 못 만들었어도 아래 내용을 그대로 쓰면 됩니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치를 확인하고, 판다스가 설치돼 있는지 봅니다(맥북은 `python3`). <mark>`pwd` 가 `…/anomaly_detection` 으로 끝나고, 마지막에 버전 번호(예: `2.3.3`)가 나오면</mark> 됩니다. `No module named 'pandas'` 가 나오면 아래 「🆘」 둘째 줄을 따릅니다.
   ```bash
   cd anomaly_detection
   pwd
   python -c "import pandas; print(pandas.__version__)"
   ```
3. **오늘 받은 파일 두 개**(`day04_am_suspicious_logs.md`, `day04_am_report.md`)를 <mark>`다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-05(목))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[터미널]** 3과목(접근통제) 파일을 넣을 `config` 폴더를 만들고 확인합니다. 이미 `config` 폴더가 있으면 건너뜁니다.
   ```bash
   mkdir config
   ls
   ```
   - 명령 풀이: `mkdir config` 폴더 만들기 · `ls` 폴더 안의 파일 이름 보기
6. **[VS Code 또는 터미널]** `anomaly_detection` 폴더에 `normalized_events.json` · `rbac.py` · `config/users.json` · `config/roles.json` 파일을 만들어 아래 내용을 그대로 붙여 넣습니다(<mark>파일 네 개를 모두 붙인 뒤 맨 아래 7번으로 확인합니다</mark>). 터미널에서는 아래 명령으로 한 번에 만들고 VS Code 에서 엽니다(`config` 폴더는 위 5번에서 만들었습니다).
   ```bash
   touch normalized_events.json rbac.py config/users.json config/roles.json
   ls config
   ```

**`normalized_events.json`** — 11/3 에 만든 이벤트 샘플 57개입니다. 오늘은 모두 아래 내용으로 만듭니다. <mark>같은 이름의 파일이 이미 있으면 아래 내용으로 덮어씁니다</mark>(출력이 문서와 같아야 하기 때문입니다). 이벤트 날짜는 모두 2026-11-02 입니다. `null` 은 그 값이 로그에 없다는 뜻입니다.

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

**`rbac.py`** — 3과목(접근통제)에서 만든 권한 판정 파일의 완성본입니다. `check_permission(사용자, 자원, 행위)` 가 `(허용 여부, 이유)` 를 리턴합니다.

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

**`config/users.json`** — 3과목(접근통제)의 사용자 파일입니다. 사용자마다 역할과 재직 여부(`employed`)가 있습니다.

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

**`config/roles.json`** — 3과목(접근통제)의 역할 파일입니다. 역할마다 허용된 권한 리스트가 있습니다.

```
{
  "sales": ["SALES:QUERY", "SALES:CHANGE"],
  "account_admin": ["ACCOUNT:QUERY", "ACCOUNT:CHANGE"],
  "finance": ["SALES:QUERY", "SETTLE:QUERY"],
  "batch": ["SETTLE:QUERY"],
  "auditor": ["SALES:QUERY", "SETTLE:QUERY", "ACCOUNT:QUERY"]
}
```

7. **[터미널]** <mark>파일이 정상인지 확인합니다</mark>(맥북은 `python3`).
   ```bash
   python -c "import json; print(len(json.load(open('normalized_events.json', encoding='utf-8'))))"
   python -c "from rbac import check_permission; print(check_permission('dami', 'SALES', 'QUERY'))"
   ```
   - <mark>순서대로 `57` 과 `(False, '퇴사한 계정')` 이 나와야</mark> 합니다. 다르면 파일 내용이나 위치(`config` 폴더 안인지)를 다시 확인합니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `No module named 'pandas'`: <mark>가상환경이 활성화되지 않은 터미널입니다</mark>. `security-agent-toolkit` 폴더에서 가상환경을 활성화한 뒤(`source .venv/Scripts/activate`, 맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 다르면 그 이름으로) `python -m pip install pandas` 를 칩니다.
- `FileNotFoundError: config/roles.json` · `No module named 'rbac'`: <mark>`config` 폴더 안에 두 JSON 파일이 있는지</mark>, `rbac.py` 가 `anomaly_detection` 폴더 바로 아래에 있는지 `ls` 로 봅니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 서버가 거절한 요청 중 반복된 것 찾고 이유로 순서 정하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「11/2 에 판정 서버가 요청을 거절한 기록이 9건 있습니다. 판정 서버는 사용자가 누른 기능을 허용할지 정하는 서버입니다. 로그에는 `실패` 라고만 적혀 있어서 왜 거절했는지 알 수 없고, 9건을 하나씩 열어 볼 시간도 없습니다.
>
> 같은 사람이 여러 번 거절당한 기록부터 확인하고 싶습니다. 3과목(접근통제)에서 만든 권한 규칙으로 거절 이유도 붙여 주세요. 퇴사한 사람의 계정이면 가장 먼저 알려 주세요. 거절이 전부 문제는 아니니 공격이라고 단정하지는 말아 주세요.」
> - **왜 중요한가**: <mark>거절 이유를 알아야 퇴사한 계정을 정리할지, 서버 설정을 확인할지 정할 수 있습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 판정 서버는 요청을 거절할 때마다 `실패` 로 기록합니다. 어제 오전에는 웹 서버의 로그인 실패를 확인했습니다. 오늘은 **판정 서버 로그**의 거절 기록을 확인합니다.
2. 오늘 먼저 확인할 거절은 <mark>**한 사용자가 3번 이상 거절당한 기록**</mark>입니다. 질문은 이것 하나입니다.
3. 3과목(접근통제)의 권한 규칙(`check_permission`)으로 같은 요청을 다시 판정하면 **거절 이유**가 나옵니다. <mark>이유에 따라 할 일이 다릅니다.</mark>

| 거절 이유 | 뜻 | 할 일 | 순서 |
|---|---|---|---|
| 퇴사한 계정 | 퇴사했는데 계정이 남아 있음 | 계정 정리 | **1** |
| 권한 없음 | 그 역할에 허용되지 않은 행동을 요청함 | 요청한 이유 확인 | 2 |
| 허용 | 규칙으로는 허용인데 서버가 거절함 | 서버 설정 확인(공격이라고 확정할 수 없음) | 3 |

### 📖 2.1 먼저 확인할 거절

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

판정 서버 로그의 실패 9개입니다(샘플에서 `source` 가 `server` 이고 `result` 가 `실패` 인 이벤트).

**먼저 확인할 질문은 하나입니다.**

| 질문 | 「예」가 되는 때 |
|---|---|
| 그 사용자의 실패가 3번 이상인가? | 그날 그 사용자의 판정 서버 실패가 3번 이상입니다(`REPEAT_LIMIT` = 3). 행동의 종류와 상관없이 실패 횟수만 셉니다. |

- <mark>**「예」이면 먼저 확인합니다.**</mark> 「아니오」이면 이번에는 뺍니다.

| 시각 | 사용자 | 행동 | 그 사용자의 실패 횟수 | 먼저 확인 |
|---|---|---|---|---|
| 10:05 | gaeun | `ACCOUNT:CHANGE` | 3번 | **예** |
| 10:09 | gaeun | `ACCOUNT:CHANGE` | 3번 | **예** |
| 10:14 | gaeun | `ACCOUNT:CHANGE` | 3번 | **예** |
| 11:02 | dami | `SALES:QUERY` | 4번 | **예** |
| 11:03 | dami | `SALES:QUERY` | 4번 | **예** |
| 11:05 | dami | `SALES:CHANGE` | 4번 | **예** |
| 11:08 | dami | `SALES:QUERY` | 4번 | **예** |
| 11:40 | seoyeon | `SETTLE:QUERY` | 2번 | 아니오 |
| 18:20 | seoyeon | `SALES:CHANGE` | 2번 | 아니오 |

- 먼저 확인할 기록은 **7개**(gaeun 3 + dami 4)이고, seoyeon 의 2건만 빠집니다.
- 7개를 3과목(접근통제) 규칙으로 판정하면 dami 는 「퇴사한 계정」으로 1순위, gaeun 은 「허용」으로 3순위입니다.
- 이 판정은 거절이 규칙대로였는지 확인하는 것이고, **공격이라고 확정하는 것이 아닙니다.**

**🐼 판다스 문법 상자 — 목록에 있는 사용자인지 `isin`**

**<mark>`열.isin(리스트)`</mark> 는 열의 값이 리스트 안에 있으면 `True`, 없으면 `False` 를 줍니다**

아래는 로그인 기록입니다. 퇴사한 사용자를 차단 목록(`blocked_users`)에 적어 두었습니다. 이 목록에 있는 사용자의 기록만 찾아봅니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                    # 표에 넣을 내용(열 이름: 값들)
    "user": ["gaeun", "dami", "seoyeon", "junho", "dami"],  # user 열
    "result": ["성공", "실패", "성공", "실패", "실패"],     # result 열
}
df = pd.DataFrame(data)                                     # 내용으로 표(DataFrame)를 만든다
print(df)                                                   # 표를 출력한다
```

실행 결과:

```
      user result
0    gaeun     성공
1     dami     실패
2  seoyeon     성공
3    junho     실패
4     dami     실패
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
blocked_users = ["dami", "junho"]            # 차단한 사용자 두 명을 리스트에 담는다
is_blocked = df["user"].isin(blocked_users)  # user 열의 각 값이 차단 목록에 있는지 확인한다
print(is_blocked)                            # True · False 를 출력한다
```

실행 결과:

```
0    False
1     True
2    False
3     True
4     True
Name: user, dtype: bool
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
blocked_df = df[is_blocked]  # True 인 행만 남긴다
print(blocked_df)            # 차단된 사용자의 기록을 출력한다
```

실행 결과:

```
    user result
1   dami     실패
3  junho     실패
4   dami     실패
```

- 읽는 법: 첫 번째 출력은 입력 표입니다. <mark>두 번째 출력에서 1번 행(dami) · 3번 행(junho) · 4번 행(dami)이 `True`</mark> 입니다. 세 번째 출력은 그 세 기록만 남은 표입니다. `Name: user, dtype: bool` 줄은 몰라도 됩니다.

**🐼 판다스 문법 상자 — 센 결과에서 이름만 꺼내기 `.index`**

**<mark>`센 결과.index`</mark> 는 `value_counts()` 로 센 결과에서 왼쪽에 나오는 이름들(인덱스)을 꺼냅니다. 사용자별로 센 결과라면 사용자 이름이 나옵니다**

아래는 로그인에 실패한 기록입니다. 사용자별 실패 횟수를 센 뒤, 2번 이상 실패한 사용자의 이름만 꺼냅니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                            # 표에 넣을 내용(열 이름: 값들)
    "user": ["dami", "gaeun", "dami", "seoyeon", "dami", "gaeun"],  # user 열
    "result": ["실패", "실패", "실패", "실패", "실패", "실패"],     # result 열
}
df = pd.DataFrame(data)                                             # 내용으로 표(DataFrame)를 만든다
print(df)                                                           # 표를 출력한다
```

실행 결과:

```
      user result
0     dami     실패
1    gaeun     실패
2     dami     실패
3  seoyeon     실패
4     dami     실패
5    gaeun     실패
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
counts = df["user"].value_counts()  # 같은 사용자가 몇 번 나왔는지 센다
print(counts)                       # 사용자(인덱스)와 실패 횟수를 출력한다
```

실행 결과:

```
user
dami       3
gaeun      2
seoyeon    1
Name: count, dtype: int64
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
many = counts[counts >= 2]  # 2번 이상인 사용자만 남긴다
names = list(many.index)    # 남은 결과의 인덱스(사용자 이름)만 꺼내 리스트로 만든다
print(names)                # 이름 리스트를 출력한다
```

실행 결과:

```
['dami', 'gaeun']
```

- 읽는 법: 첫 번째 출력은 입력 표입니다. 두 번째 출력은 사용자별 실패 횟수입니다(dami 3번 · gaeun 2번 · seoyeon 1번). <mark>세 번째 출력은 2번 이상 실패한 사용자 이름만 담은 리스트</mark>입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` | 파일 경로 | 이벤트 표(미리 채움) |
| `pick_server_failures` | 이벤트 표 | 판정 서버 실패 이벤트 표(미리 채움) |
| `pick_suspicious` | 서버 실패 표 | 실패가 반복된 사용자의 이벤트 표 |
| `judge_failure` | 사용자 · 행동 | 판정 이유와 우선순위 |

- **직접 쓰는 곳은 여섯 군데**(번호 1 ~ 6)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `pick_suspicious`(1 ~ 3번): 반복된 사용자의 이름을 꺼내고, `isin` 으로 그 사용자의 행을 골라 이벤트 표를 만듭니다. 사용자별 실패 횟수를 세는 줄은 미리 채웠습니다.
  - `judge_failure`(4 ~ 6번): 행동을 자원과 행위로 나누고, 3과목(접근통제) `check_permission` 으로 판정하고, 이유에서 우선순위를 꺼냅니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 서버가 거절한 요청 중 반복된 것을 찾고 이유로 순서 정하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>판정 서버의 거절 9건을 하나씩 읽어야 하고, 어느 것이 급한지 알 수 없습니다</mark>.
- **그래서 만드는 것**: `access_detection.py` 입니다.
  - 실패가 3번 이상 반복된 사용자의 이벤트를 고릅니다.
  - 고른 이벤트를 3과목(접근통제) `check_permission` 으로 다시 판정해 이유를 알아냅니다.
  - 이유로 순서를 정합니다.
- **실행하면**: <mark>단계 1: 서버 실패 이벤트 수, 단계 2: 먼저 확인할 이벤트 수, 단계 3: 순서대로 이벤트가 한 줄씩 나옵니다.</mark>
- **현업에서는**: 같은 계정의 요청이 반복해서 거절되면 먼저 확인할 근거가 됩니다. 이유별로 순서를 정해 두면 퇴사자 계정처럼 급한 것을 빠뜨리지 않고, 서버 설정 문제는 따로 점검합니다.

**🎯 할 일**

1. `access_detection.py` · `day04_2-1_run.py` 두 파일을 만들고, `access_detection.py` 의 두 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>서버 실패 수</mark>(단계 1), <mark>먼저 확인할 이벤트 수</mark>(단계 2), <mark>이유별 순서</mark>(단계 3)를 읽습니다.

**`access_detection.py`**

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
    # 2. users 가 repeated_names 안에 있는지 isin 으로 구해 is_repeated_user 에 담는다
    # 3. server_failures 에서 is_repeated_user 가 True 인 행만 골라 suspicious 에 담는다
    return suspicious                                 # 먼저 확인할 실패 이벤트 표를 리턴한다


def judge_failure(user, action):                      # 사용자와 행동을 받는 함수
    """서버가 거절한 요청을 3과목(접근통제) 권한 규칙으로 다시 판정해 이유와 우선순위를 리턴한다.
    거절이 규칙대로인지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. action 을 ":" 기준으로 나눠 parts 에 담는다 (예: "SALES:QUERY" → ["SALES", "QUERY"]. 앞 조각이 자원, 뒤 조각이 행위)
    resource = parts[0]                               # 첫 번째 조각이 자원이다
    permission_action = parts[1]                      # 두 번째 조각이 행위이다

    # 5. check_permission 에 user, resource, permission_action 을 전달하고, 결과를 is_allowed 와 reason 에 나눠 담는다 (모양: is_allowed, reason = check_permission(...). is_allowed 는 이 문제에서 쓰지 않는다)
    # 6. PRIORITY 에서 reason 의 순서를 꺼내 priority 에 담는다 (딕셔너리에 없는 이유이면 4 — .get(reason, 4))
    return reason, priority                           # 판정 이유와 우선순위를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `NameError: name 'suspicious' is not defined` 오류가 납니다. 1 ~ 3번을 아직 안 썼기 때문입니다.

**`day04_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(표)` 는 표의 행 수입니다.

```python
from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH  # 방금 만든 함수를 불러온다

LABELS = {"퇴사한 계정": "퇴사한 계정", "권한 없음": "권한 없음", "허용": "규칙은 허용인데 서버가 거절"}  # 판정 이유를 담당자가 읽는 말로 바꾼다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
server_failures = pick_server_failures(events)               # 판정 서버의 실패 이벤트만 골라낸다
failure_count = len(server_failures)                         # 서버 실패가 모두 몇 개인지 센다
print("--- 단계 1: 판정 서버의 실패 이벤트", failure_count, "개")  # 단계 1 시작을 알리는 줄과 개수

suspicious = pick_suspicious(server_failures)                # 먼저 확인할 실패 이벤트만 골라낸다
suspicious_count = len(suspicious)                           # 먼저 확인할 이벤트가 몇 개인지 센다
print("--- 단계 2: 먼저 확인할 실패 이벤트", suspicious_count, "개")  # 단계 2 시작을 알리는 줄과 개수

suspicious_list = suspicious.to_dict("records")              # 표를 이벤트 딕셔너리 리스트로 바꾼다
judged_list = []                                             # 판정 결과를 담을 빈 리스트
for event in suspicious_list:                                # 이벤트를 하나씩 꺼낸다
    reason, priority = judge_failure(event["user"], event["action"])  # 3과목 규칙으로 다시 판정한다
    judged = {"priority": priority, "reason": reason, "event": event}  # 순서 · 이유 · 이벤트를 딕셔너리로 만든다
    judged_list.append(judged)                               # 판정 결과를 리스트에 추가한다

print("--- 단계 3: 우선순위")                            # 단계 3 시작을 알리는 줄
for priority in [1, 2, 3]:                                   # 우선순위대로 꺼낸다
    for judged in judged_list:                               # 판정 결과를 하나씩 꺼낸다
        if judged["priority"] == priority:                   # 지금 순서의 결과이면
            event = judged["event"]                          # 그 이벤트를 꺼낸다
            label = LABELS.get(judged["reason"], judged["reason"])  # 담당자가 읽는 말로 바꾼다
            print(priority, label, event["user"], event["action"], event["time"])  # 순서 · 이유 · 사용자 · 행동 · 시각을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `access_detection.py` · `day04_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `access_detection.py` 에서 <mark>직접 쓰는 곳 여섯 군데를 씁니다</mark>. 위 판다스 문법 상자와 2.1 의 표를 참고해 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day04_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_2-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **세 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1과 단계 2는 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없고, 단계 3은 7줄입니다.
5. **[보고서]** `day04_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 서버 실패 수와 먼저 확인할 이벤트 수, 1순위 사용자를 적어 주세요.
   - (나) 🔍 ① dami 의 실패 4개는 3과목(접근통제) 규칙으로 어떤 이유로 판정됐고, 왜 1순위일까요? ② gaeun 의 실패 3개는 규칙으로는 「허용」인데 서버가 거절했습니다. 공격이라고 확정할 수 있는지 적고, 먼저 무엇을 확인해야 하는지 적어 주세요.
   - (다) 🔍 seoyeon 의 서버 실패 2건(11:40 `SETTLE:QUERY` · 18:20 `SALES:CHANGE`)은 먼저 확인할 이벤트에 들어가지 않았습니다. 들어가지 않은 이유를 오늘 규칙(실패 3번 이상)으로 설명하고, 이 규칙 때문에 놓칠 수 있는 경우를 한 가지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 센 결과의 왼쪽 이름(인덱스) | `repeated_names = repeated_users.index` |
| 리스트 안에 있는지 | `is_repeated_user = users.isin(repeated_names)` |
| 3과목(접근통제) 규칙으로 판정 | `is_allowed, reason = check_permission(user, resource, permission_action)` |
| 순서 | `priority = PRIORITY.get(reason, 4)` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · SaaS 로그에서 이상 사용 세 가지 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「우리 회사는 파일 보관 서비스(SaaS)를 씁니다. 이 서비스는 회사 밖 어디서나 로그인할 수 있습니다. 11/2 에는 02:14 에 새벽 로그인 시도가 있었고, 17:38 에는 seoyeon 이 평소와 다른 IP 로 로그인한 뒤 파일을 5번 연속으로 내려받았습니다.
>
> 다음 세 가지를 각각 찾아서 어느 사용자가 해당하는지 알려 주세요. ① 업무 시간 밖 로그인 ② 평소와 다른 IP 로 로그인 ③ 파일 5번 이상 내려받기 평소 기록이 없는 사용자는 IP 를 비교할 수 없으니 IP 확인에서는 빼 주세요.」
> - **왜 중요한가**: <mark>SaaS 는 회사 밖에서도 로그인할 수 있어서 로그인에 성공했다는 것만으로는 본인인지 알 수 없고, 세 규칙을 따로 확인하면 담당자가 확인할 대상을 구분할 수 있습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 어제 2교시에서 **평소 기준**을 정했습니다. 오늘은 사용자마다 평소가 다르므로 **사용자별 평소 IP** 를 딕셔너리로 둡니다.
2. SaaS 이상 사용을 보는 규칙은 세 가지이고, <mark>세 규칙은 각각 따로 찾습니다.</mark>
   - **업무 시간 밖 로그인**: 로그인한 시각의 시(hour)가 8 보다 작거나 20 보다 큰 로그인 시도입니다(오전 8시 전, 오후 9시 이후). 20시대(20:00 ~ 20:59)는 업무 시간 안입니다.
   - **평소와 다른 IP**: 사용자의 평소 IP 와 다른 IP 로 로그인했습니다.
   - **대량 다운로드**: 파일을 5번 이상 내려받았습니다(이 규칙은 미리 채워져 있습니다).
3. 평소 IP 기록이 없는 사용자(`gaeun`)는 <mark>비교할 기준이 없으므로 「평소와 다른 IP」 규칙에서만 뺍니다.</mark> 다른 두 규칙에는 그대로 포함합니다.

### 📖 3.1 SaaS 로그와 세 규칙

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

샘플에서 `source` 가 `saas` 인 이벤트 14개입니다.

| 시각 | 사용자 | IP | 행동 | 결과 | 해당하는 규칙 |
|---|---|---|---|---|---|
| 02:14 | jiwoo | 203.0.113.80 | `login` | 실패 | 업무 시간 밖 · 평소와 다른 IP |
| 09:05 | seoyeon | 198.51.100.9 | `login` | 성공 | 해당 없음 |
| 09:30 | junho | 192.0.2.41 | `login` | 성공 | 해당 없음 |
| 10:12 | gaeun | 198.51.100.77 | `login` | 성공 | 평소 기록이 없어 IP 규칙에서 제외 |
| 11:25 | seoyeon | 198.51.100.9 | `file.download` | 성공 | 다운로드 1번 |
| 13:50 | junho | 192.0.2.41 | `file.upload` | 성공 | 해당 없음 |
| 15:20 | junho | 192.0.2.41 | `login` | 성공 | 해당 없음 |
| 16:02 | jiwoo | 198.51.100.52 | `login` | 성공 | 해당 없음 |
| 17:38 | seoyeon | 203.0.113.80 | `login` | 성공 | 평소와 다른 IP |
| 17:40 ~ 17:42 | seoyeon | 203.0.113.80 | `file.download` 5번 | 성공 | 다운로드 합계 6번(대량) |

- 파일 내려받기는 11:25 에 1번, 17:40 ~ 17:42 에 5번이라 합계 6번입니다. 팀장 메시지의 「5번 연속」은 17:40 ~ 17:42 에 기록된 다운로드 5건을 말합니다.
- `USUAL_IPS` 에 평소 IP 를 둔 사용자는 3명(seoyeon · junho · jiwoo)입니다.
- <mark>규칙에 해당한다고 계정이 도용됐다는 뜻은 아니고,</mark> **먼저 확인할 대상**이라는 뜻입니다.

**알아 둘 것 — 미리 채운 줄의 `pd.to_datetime` 과 `.dt.hour`**

`pd.to_datetime(열)` 로 문자열 시각을 시각 값으로 바꾼 뒤 `.dt.hour` 를 붙이면 시(0 ~ 23)만 숫자로 꺼냅니다(예: 21:40 의 시는 21). `.dt` 는 시각 값에만 쓸 수 있어서 문자열 시각을 먼저 바꿉니다. 문제에서는 이 두 줄이 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                                            # 표에 넣을 내용(열 이름: 값들)
    "user": ["jiwoo", "seoyeon", "junho"],                                          # user 열
    "time": ["2026-11-02 02:14:08", "2026-11-02 09:05:30", "2026-11-02 21:40:10"],  # time 열
}
df = pd.DataFrame(data)                                                             # 내용으로 표(DataFrame)를 만든다
print(df)                                                                           # 표를 출력한다
```

실행 결과:

```
      user                 time
0    jiwoo  2026-11-02 02:14:08
1  seoyeon  2026-11-02 09:05:30
2    junho  2026-11-02 21:40:10
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
times = pd.to_datetime(df["time"])  # 문자열 시각을 시각 값으로 바꾼다
print(times)                        # 시각 값을 출력한다
```

실행 결과:

```
0   2026-11-02 02:14:08
1   2026-11-02 09:05:30
2   2026-11-02 21:40:10
Name: time, dtype: datetime64[ns]
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
hours = times.dt.hour  # 시각 값에서 시(0~23)만 꺼낸다
print(hours)           # 시를 출력한다
```

실행 결과:

```
0     2
1     9
2    21
Name: time, dtype: int32
```

- 읽는 법: 첫 번째 출력은 시각 값이 된 `time` 열이고, 두 번째 출력은 거기서 시만 꺼낸 값입니다(<mark>02:14 → 2, 09:05 → 9, 21:40 → 21</mark>).

**🐼 판다스 문법 상자 — 범위 안인지 `between`**

**<mark>`열.between(작은 값, 큰 값)`</mark> 은 열의 값이 작은 값 이상이고 큰 값 이하이면 `True`, 아니면 `False` 를 줍니다. 작은 값과 큰 값 자체도 포함합니다**

아래는 로그인한 시(`hour`, 0 ~ 23)입니다. 8시부터 20시 사이이면 업무 시간 안입니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                            # 표에 넣을 내용(열 이름: 값들)
    "user": ["gaeun", "dami", "seoyeon", "junho"],  # user 열
    "hour": [9, 2, 20, 21],                         # hour 열
}
df = pd.DataFrame(data)                             # 내용으로 표(DataFrame)를 만든다
print(df)                                           # 표를 출력한다
```

실행 결과:

```
      user  hour
0    gaeun     9
1     dami     2
2  seoyeon    20
3    junho    21
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
in_hours = df["hour"].between(8, 20)  # hour 가 8 ~ 20 사이인지 확인한다
print(in_hours)                       # True · False 를 출력한다
```

실행 결과:

```
0     True
1    False
2     True
3    False
Name: hour, dtype: bool
```

- 읽는 법: 9시와 20시는 `True`, 2시와 21시는 `False` 입니다. <mark>20시도 `True` 인 것은 8 과 20 자체도 사이에 포함하기 때문입니다.</mark>

**🐼 판다스 문법 상자 — 조건 뒤집기 `~`**

**<mark>`~조건`</mark> 은 `True` 는 `False` 로, `False` 는 `True` 로 뒤집습니다**

아래에서는 업무 시간 **밖**에 로그인한 기록을 찾습니다. 위에서 만든 「업무 시간 안인지」를 뒤집으면 됩니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                            # 표에 넣을 내용(열 이름: 값들)
    "user": ["gaeun", "dami", "seoyeon", "junho"],  # user 열
    "hour": [9, 2, 20, 21],                         # hour 열
}
df = pd.DataFrame(data)                             # 내용으로 표(DataFrame)를 만든다
in_hours = df["hour"].between(8, 20)                # hour 가 8 ~ 20 사이인지 확인한다
print(in_hours)                                     # 업무 시간 안인지 출력한다
```

실행 결과:

```
0     True
1    False
2     True
3    False
Name: hour, dtype: bool
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
off_hours = ~in_hours  # True 와 False 를 서로 뒤집는다
print(off_hours)       # 업무 시간 밖인지 출력한다
```

실행 결과:

```
0    False
1     True
2    False
3     True
Name: hour, dtype: bool
```

- 읽는 법: <mark>두 출력이 서로 반대입니다.</mark> 업무 시간 안이던 0 · 2번 행은 `False` 가 되고, 밖이던 1 · 3번 행은 `True` 가 됩니다.

**🐍 문법 상자 — 다른지 `!=` 와 값이 있는지 `is not None`**

**<mark>`a != b`</mark> 는 두 값이 다르면 `True`, 같으면 `False` 입니다. <mark>`값 is not None`</mark> 은 값이 `None`(값이 없다는 표시)이 아니면 `True` 입니다**

`==` 의 반대가 `!=` 이고, `is None`(값이 없는가)의 반대가 `is not None`(값이 있는가)입니다.

```python
usual_ip = "198.51.100.9"   # 사용자의 평소 IP
ip = "203.0.113.80"         # 이번 로그인의 IP
is_new_ip = ip != usual_ip  # 이번 IP 가 평소 IP 와 다른지 구한다 (!=)
print(is_new_ip)            # True — 서로 다르다
```

실행 결과:

```
True
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
no_record = None                    # 평소 IP 기록이 없는 사용자는 값이 None 이다
has_record = no_record is not None  # 값이 있는지(None 이 아닌지) 구한다 (is not None)
print(has_record)                   # False — 평소 기록이 없다
```

실행 결과:

```
False
```

- 읽는 법: 평소 IP 와 이번 IP 가 달라서 `True` 이고, <mark>값이 `None`(평소 기록 없음)이라 「값이 있는가」를 묻는 결과는 `False`</mark> 입니다.
- `None` 은 어떤 IP 와도 같지 않아서 `ip != None` 은 항상 `True` 입니다. <mark>그래서 평소 기록이 없는 사용자는 `is not None` 으로 먼저 제외합니다.</mark>

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` · `pick_saas` · `pick_logins` | 파일 경로 · 이벤트 표 | 이벤트 표 · SaaS 표 · 로그인 표(미리 채움) |
| `find_off_hours_logins` | 로그인 표 | 업무 시간 밖 로그인 표 |
| `find_new_ip_users` | 로그인 표 | 평소와 다른 IP 로 로그인한 사용자 리스트 |
| `find_bulk_download_users` | SaaS 표 | 대량 다운로드 사용자 리스트(미리 채움) |

- **직접 쓰는 곳은 다섯 군데**(번호 1 ~ 5)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `find_off_hours_logins`(1 · 2번, 2곳): 시가 업무 시간 안인지 구하고 뒤집습니다. 시각을 시로 꺼내는 두 줄은 미리 채웠습니다.
  - `find_new_ip_users`(3 ~ 5번, 3곳): 평소 기록이 있는지, 평소와 다른 IP 인지 구하고, `if` 안에서 사용자를 리스트에 추가합니다. `if` 줄은 미리 채웠습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · SaaS 로그에서 이상 사용 세 가지 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>SaaS 로그 14개를 사람이 읽어서 이상 사용을 찾고 있고, 어떤 기준으로 볼지 정해져 있지 않습니다</mark>.
- **그래서 만드는 것**: `saas_detection.py` 입니다.
  - 업무 시간 밖 로그인을 찾습니다.
  - 평소와 다른 IP 로 로그인한 사용자를 찾습니다(평소 기록이 없는 사용자는 뺍니다).
  - 대량 다운로드 사용자를 찾습니다(미리 채워져 있습니다).
- **실행하면**: <mark>단계 1: 업무 시간 밖 로그인, 단계 2: 평소와 다른 IP 사용자, 단계 3: 대량 다운로드 사용자가 나옵니다.</mark>
- **현업에서는**: 규칙마다 따로 찾아 두면 6교시에서 규칙마다 점수를 줄 수 있습니다. 평소 기록이 없는 사용자는 기록이 쌓인 뒤에 규칙을 적용합니다.

**🎯 할 일**

1. `saas_detection.py` · `day04_3-1_run.py` 두 파일을 만들고, `saas_detection.py` 의 두 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>업무 시간 밖 로그인</mark>(단계 1), <mark>평소와 다른 IP 사용자</mark>(단계 2), <mark>대량 다운로드 사용자</mark>(단계 3)를 읽습니다.

**`saas_detection.py`**

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
    # 2. is_business_hour 의 반대를 ~ 로 구해 is_off_hours 에 담는다
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
        # 4. ip 가 usual_ip 와 다른지 != 로 구해 is_new_ip 에 담는다 (같은지는 ==, 다른지는 !=)
        if has_usual_ip and is_new_ip:                # 평소 IP 기록이 있고, 이번 IP 가 평소와 다르면
            # 5. new_ip_users 에 user 를 추가한다
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

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 · 2번은 함수 안이라 앞에 공백 4개이고, 3 · 4번은 `for` 안이라 8개이며, 5번은 `if` 안이라 12개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다(파이썬 버전에 따라 뒤에 `after 'if' statement on line …` 이 붙기도 합니다). `if` 안쪽의 5번이 비어 있기 때문입니다.

**`day04_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `list(열)` 은 열의 값을 리스트로 만듭니다.

```python
from saas_detection import load_events, pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
saas = pick_saas(events)                                     # SaaS 이벤트만 골라낸다
logins = pick_logins(saas)                                   # 로그인 이벤트만 골라낸다

off_hours_logins = find_off_hours_logins(logins)             # 업무 시간 밖 로그인만 골라낸다
off_hours_count = len(off_hours_logins)                      # 업무 시간 밖 로그인이 몇 건인지 센다
print("--- 단계 1: 업무 시간 밖 로그인", off_hours_count, "건")  # 단계 1 시작을 알리는 줄과 건수
print(off_hours_logins)                                      # 그 로그인 표를 출력한다

new_ip_users = find_new_ip_users(logins)                     # 평소와 다른 IP 로 로그인한 사용자를 찾는다
print("--- 단계 2: 평소와 다른 IP 로 로그인한 사용자", new_ip_users)  # 단계 2 시작을 알리는 줄과 사용자

bulk_users = find_bulk_download_users(saas)                  # 파일을 대량으로 내려받은 사용자를 찾는다
print("--- 단계 3: 파일을 5번 이상 내려받은 사용자", bulk_users)  # 단계 3 시작을 알리는 줄과 사용자
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `saas_detection.py` · `day04_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `saas_detection.py` 에서 <mark>직접 쓰는 곳 다섯 군데를 씁니다</mark>. 3.1 의 문법 상자를 보고 씁니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day04_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day04_3-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **세 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 표 2줄이고, 단계 2와 3은 사용자가 제목 줄에 함께 나오므로 그 아래 줄이 없습니다.
5. **[보고서]** `day04_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 규칙마다 해당한 사용자를 적어 주세요.
   - (나) 🔍 jiwoo 는 업무 시간 밖(02:14)과 평소와 다른 IP 두 규칙에 해당하지만 그 로그인은 실패였습니다. 이 기록만으로 계정 도용을 확정할 수 있나요? 그렇게 판단한 이유와, 샘플 로그에서 더 찾아볼 수 있는 것을 한 가지 적어 주세요.
   - (다) 🔍 gaeun 은 평소 IP 기록이 없어 「평소와 다른 IP」 규칙에서 제외됩니다. 제외하지 않으면 어떤 일이 생기고, 제외하면 어떤 위험이 남나요?

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 범위 안인지 | `is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)` |
| 조건 뒤집기 | `is_off_hours = ~is_business_hour` |
| 평소 기록이 있는지 | `has_usual_ip = usual_ip is not None` |
| 평소 IP 와 다른지 | `is_new_ip = ip != usual_ip` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 웹 로그에서 경로를 스캔한 IP 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「웹 서버(우리 서비스 화면을 보여 주는 서버)의 11/2 실패 기록이 13건 있습니다. 이 중에 `/.env` · `/phpmyadmin` 처럼 일반 사용자는 열 일이 없는 경로(아래에서 설명합니다)를 요청한 IP 가 있습니다. 해킹 도구가 접근할 수 있는 곳이 있는지 경로를 차례로 요청해 본 것 같습니다.
>
> 그런데 사용자가 경로를 잘못 입력하거나 없는 게시글을 요청해도 똑같이 실패로 기록됩니다. 해킹 도구가 자주 요청하는 경로를 요청한 IP 만 가려 주세요.」
> - **왜 중요한가**: <mark>실패를 모두 알림으로 보내면 알림이 너무 많아져서, 담당자가 진짜 경로 스캔을 놓칠 수 있습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 웹 서버는 요청이 처리되지 않으면 실패로 기록합니다(없는 경로를 요청하면 404 라는 HTTP 상태 코드가 남습니다. HTTP 상태 코드는 서버가 요청을 처리한 결과를 나타내는 숫자입니다).
2. 해킹 도구는 접근할 수 있는 곳을 찾으려고 <mark>**정해진 경로를 차례로 요청**</mark>합니다. 자주 요청하는 경로는 이렇습니다.
   - `/.env`(비밀번호와 키가 든 설정 파일)
   - `/wp-login.php`(워드프레스 로그인 화면)
   - `/phpmyadmin`(데이터베이스 관리 화면)
3. 오늘 질문은 하나입니다. <mark>실패한 요청 중에 이 경로를 요청한 IP 가 있는가?</mark> 이 경로 중 하나를 요청했으면 오늘 기준에서는 스캔으로 봅니다(공격으로 확정하는 것은 아닙니다).

### 📖 4.1 웹 실패 로그에서 스캔 찾기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

샘플에서 `source` 가 `web` 이고 `result` 가 `실패` 인 이벤트는 13개입니다. IP 별로 실패한 요청을 정리하면 이렇습니다.

| IP | 실패한 요청 | 스캐너 경로를 요청했나 | 오늘 규칙 결과 |
|---|---|---|---|
| 198.51.100.21 | `GET /board/99` | 아니오 | 제외 |
| 198.51.100.34 | `GET /report` | 아니오 | 제외 |
| 198.51.100.77 | `GET /admin` | 아니오 | 제외 |
| 198.51.100.90 | `GET /.env` · `GET /wp-login.php` · `GET /phpmyadmin` | **예** | **스캔** |
| 203.0.113.50 | `POST /login` 5번 · `GET /admin` · `GET /admin/users` | 아니오 | 제외 |

- `SCANNER_PATTERN` 은 `"/.env|/wp-login|/phpmyadmin"` 입니다. 따옴표 안의 `|` 는 「또는」이라는 뜻이라, <mark>셋 중 하나가 들어 있으면</mark> 해당합니다. 조건끼리 합치는 기호가 아니라, 문자열 안에 쓴 글자일 뿐입니다.
- 203.0.113.50 은 실패가 7번이지만 로그인과 관리자 화면 실패라서 스캐너 경로가 없습니다. 이 IP 는 로그인 실패 규칙에서 따로 다룹니다.

**🐼 판다스 문법 상자 — 문자열이 들어 있는지 `str.contains`**

**<mark>`열.str.contains("문자열")`</mark> 은 열의 값 안에 그 문자열이 들어 있으면 `True`, 없으면 `False` 를 줍니다**

`.str` 은 열의 각 값을 문자열로 다루겠다는 표시입니다. 문자열 안의 `|` 는 「또는」이라는 뜻입니다. 아래는 웹 서버가 받은 요청 경로이고, `/.env` 나 `/phpmyadmin` 이 들어 있는 요청을 찾습니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                                     # 표에 넣을 내용(열 이름: 값들)
    "ip": ["198.51.100.90", "192.0.2.15", "198.51.100.90", "203.0.113.50"],  # ip 열
    "path": ["/.env", "/board", "/phpmyadmin", "/board/12"],                 # path 열
}
df = pd.DataFrame(data)                                                      # 내용으로 표(DataFrame)를 만든다
print(df)                                                                    # 표를 출력한다
```

실행 결과:

```
              ip         path
0  198.51.100.90        /.env
1     192.0.2.15       /board
2  198.51.100.90  /phpmyadmin
3   203.0.113.50    /board/12
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
is_scanner = df["path"].str.contains("/.env|/phpmyadmin")  # path 에 둘 중 하나가 들어 있는지 확인한다
print(is_scanner)                                          # True · False 를 출력한다
```

실행 결과:

```
0     True
1    False
2     True
3    False
Name: path, dtype: bool
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
scanner_df = df[is_scanner]  # True 인 행만 남긴다
print(scanner_df)            # 남은 요청을 출력한다
```

실행 결과:

```
              ip         path
0  198.51.100.90        /.env
2  198.51.100.90  /phpmyadmin
```

- 읽는 법: <mark>`/.env` 가 든 0번 행과 `/phpmyadmin` 이 든 2번 행이 `True`</mark> 입니다. 세 번째 출력은 그 두 행만 남은 표입니다.
- 열의 문자열 기능은 `.str.` 을 먼저 쓰고 부릅니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` · `pick_web_failures` | 파일 경로 · 이벤트 표 | 이벤트 표 · 웹 실패 표(미리 채움) |
| `find_scan_ips` | 웹 실패 표 | 스캔 IP 리스트와 IP 별 요청 횟수 |
| `explain_scan` | IP · 요청 횟수 | 설명 딕셔너리 |

- **직접 쓰는 곳은 여섯 군데**(번호 1 ~ 6)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `find_scan_ips`(1 ~ 4번): 스캐너 경로가 있는지 구하고, 그 요청만 골라 IP 별로 몇 번 요청했는지 셉니다.
  - `explain_scan`(5 · 6번): 요청 횟수를 문자열로 바꿔 이유 문장을 만들고, IP 와 이유를 딕셔너리로 만듭니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 웹 실패 로그에서 경로를 스캔한 IP 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>웹 실패 로그 13개에서 사용자의 잘못된 경로 요청과 스캐너 경로 요청이 섞여 있어, 먼저 확인할 IP 를 구분하기 어렵습니다</mark>.
- **그래서 만드는 것**: `malicious_detection.py` 입니다.
  - 실패한 요청에서 스캐너가 요청하는 경로를 찾습니다.
  - 그 경로를 요청한 IP 와 횟수를 셉니다.
  - 스캔으로 본 IP 마다 이유 설명을 만듭니다.
- **실행하면**: <mark>단계 1: 웹 실패 수, 단계 2: 스캐너 경로를 요청한 IP 와 횟수, 단계 3: 스캔으로 본 IP 와 이유, 단계 4: 스캐너 경로가 없어 제외한 IP 가 나옵니다.</mark>
- **현업에서는**: 경로 스캔은 알림으로 남기고, 로그인 실패만 있는 IP 는 따로 봅니다. 제외한 IP 와 이유를 기록해 두면 이후에 규칙을 검토할 때 참고할 수 있습니다.

**🎯 할 일**

1. `malicious_detection.py` · `day04_4-1_run.py` 두 파일을 만들고, `malicious_detection.py` 의 두 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>웹 실패 수</mark>(단계 1), <mark>스캐너 경로를 요청한 IP</mark>(단계 2), <mark>스캔으로 본 IP</mark>(단계 3), <mark>제외한 IP</mark>(단계 4)를 읽습니다.
3. 마지막으로 `advanced_detection.py` 를 만들어 오전 탐지 3개를 한 번에 돌려 봅니다.

**`malicious_detection.py`**

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
    # 2. actions 에 .str.contains(SCANNER_PATTERN) 을 붙여 스캐너 경로가 들어 있는지 구해 is_scanner 에 담는다
    # 3. web_failures 에서 is_scanner 가 True 인 행만 골라 scanner_rows 에 담는다
    # 4. scanner_rows 의 "ip" 열에 .value_counts() 를 붙여 IP 별로 몇 번 요청했는지 세어 scan_counts 에 담는다
    scan_ips = list(scan_counts.index)                # 스캔으로 보는 IP 이름만 리스트로 만든다
    return scan_ips, scan_counts                      # 스캔 IP 리스트와 IP 별 요청 횟수를 리턴한다


def explain_scan(ip, request_count):                  # IP 와 스캐너 경로 요청 횟수를 받는 함수
    """스캔으로 본 IP 하나를 담당자가 읽을 설명 딕셔너리로 만든다.
    왜 의심했는지 이유를 알림에 남길 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. "스캐너 경로를 " 와 str(request_count) 와 "번 요청" 을 + 로 연결해 reason 에 담는다 (문구는 복사해 붙여도 된다)
    # 6. 키 "ip" 에 ip, 키 "reason" 에 reason 을 담은 딕셔너리를 scan_info 에 담는다
    return scan_info                                  # 설명 딕셔너리를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `NameError: name 'scan_counts' is not defined` 오류가 납니다. 1 ~ 4번을 아직 안 썼기 때문입니다.

**`day04_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

```python
from malicious_detection import load_events, pick_web_failures, find_scan_ips, explain_scan, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
web_failures = pick_web_failures(events)                     # 웹 서버의 실패 이벤트만 골라낸다
web_failure_count = len(web_failures)                        # 웹 실패가 모두 몇 개인지 센다
print("--- 단계 1: 웹 서버의 실패 이벤트", web_failure_count, "개")  # 단계 1 시작을 알리는 줄과 개수

scan_ips, scan_counts = find_scan_ips(web_failures)          # 스캔 IP 와 IP 별 요청 횟수를 찾는다
print("--- 단계 2: 스캐너 경로를 요청한 IP 와 횟수")          # 단계 2 시작을 알리는 줄
print(scan_counts)                                           # IP 와 요청 횟수를 출력한다

print("--- 단계 3: 스캔으로 본 IP 와 이유")                   # 단계 3 시작을 알리는 줄
for ip in scan_ips:                                          # 스캔 IP 를 하나씩 꺼낸다
    request_count = scan_counts[ip]                          # 그 IP 의 요청 횟수를 꺼낸다
    scan_info = explain_scan(ip, request_count)              # 이유 설명을 만든다
    print(scan_info)                                         # 설명을 출력한다

print("--- 단계 4: 스캐너 경로가 없어 제외한 IP")              # 단계 4 시작을 알리는 줄
all_ips = web_failures["ip"].unique()                        # 웹 실패 이벤트에 나온 IP 를 중복 없이 모은다
for ip in all_ips:                                           # IP 를 하나씩 꺼낸다
    if ip not in scan_ips:                                   # 스캔 IP 에 없으면
        print(ip)                                            # 제외한 IP 를 출력한다
```

**`advanced_detection.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 오전 2 · 3 · 4교시에서 만든 함수를 모두 불러 한 번에 돌립니다. 2 · 3교시 파일을 아직 완성하지 못했다면 지금은 이 파일을 건너뛰고, 완성한 뒤에 실행합니다.

```python
from access_detection import load_events, pick_server_failures, pick_suspicious, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users  # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures, find_scan_ips  # 4교시 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다

server_failures = pick_server_failures(events)               # 판정 서버 실패 이벤트를 고른다
suspicious = pick_suspicious(server_failures)                # 실패가 반복된 사용자의 이벤트를 고른다
suspicious_count = len(suspicious)                           # 그 이벤트가 몇 개인지 센다
print("판정 서버: 먼저 확인할 실패 이벤트", suspicious_count, "개")  # 판정 서버 탐지 결과를 출력한다

saas = pick_saas(events)                                     # SaaS 이벤트를 고른다
logins = pick_logins(saas)                                   # 로그인 이벤트를 고른다
off_hours_logins = find_off_hours_logins(logins)             # 업무 시간 밖 로그인을 찾는다
off_hours_users = list(off_hours_logins["user"])             # 그 로그인의 사용자 이름만 리스트로 만든다
new_ip_users = find_new_ip_users(logins)                     # 평소와 다른 IP 로 로그인한 사용자를 찾는다
bulk_users = find_bulk_download_users(saas)                  # 대량 다운로드 사용자를 찾는다
print("SaaS: 업무 시간 밖", off_hours_users, "· 평소와 다른 IP", new_ip_users, "· 대량 다운로드", bulk_users)  # SaaS 탐지 결과를 출력한다

web_failures = pick_web_failures(events)                     # 웹 서버 실패 이벤트를 고른다
scan_ips, scan_counts = find_scan_ips(web_failures)          # 스캔으로 본 IP 를 찾는다
print("웹 서버: 스캔으로 본 IP", scan_ips)                   # 웹 탐지 결과를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `malicious_detection.py` · `day04_4-1_run.py` · `advanced_detection.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `malicious_detection.py` 에서 <mark>직접 쓰는 곳 여섯 군데를 씁니다</mark>. 4.1 의 판다스 문법 상자와 표를 보고 씁니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day04_4-1_run.py
   python advanced_detection.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행
4. 출력은 **두 번** 나옵니다. `day04_4-1_run.py` 는 네 단계입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않고, 단계 1은 숫자가 제목 줄에 함께 나오며, 단계 2는 3줄, 단계 3은 1줄, 단계 4는 4줄입니다. `advanced_detection.py` 는 3줄입니다.
5. **[보고서]** `day04_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 스캔으로 본 IP 와 이유를 적어 주세요.
   - (나) 🔍 203.0.113.50 은 실패한 요청이 7번 있지만 스캔에서 제외됐습니다. 제외된 이유와, 제외하지 않으면 담당자에게 어떤 일이 생기는지 적어 주세요.
   - (다) 🔍 198.51.100.21 의 `GET /board/99` 실패 1건은 이 규칙에서 어떤 조건 때문에 제외되나요? 그리고 해킹 도구가 `SCANNER_PATTERN` 에 없는 경로(예: `/backup.zip`)를 요청하면 이 규칙이 탐지하지 못한다는 점을 설명해 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 문자열이 들어 있는지 | `is_scanner = actions.str.contains(SCANNER_PATTERN)` |
| 조건에 맞는 행만 | `scanner_rows = web_failures[is_scanner]` |
| 이름별 개수 | `scan_counts = scanner_rows["ip"].value_counts()` |
| 문자열 연결 | `reason = "스캐너 경로를 " + str(request_count) + "번 요청"` |

---

### 마무리 · 오전 작업 확인하기

오전 작업을 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다. <mark>오전에는 파일이 모두 있는지만 확인합니다</mark>.

**순서**

1. **[터미널]** `anomaly_detection` 폴더에서 <mark>오늘 만든 파일이 있는지 확인합니다.</mark>
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - `access_detection.py` · `saas_detection.py` · `malicious_detection.py` · `advanced_detection.py` · `day04_2-1_run.py` · `day04_3-1_run.py` · `day04_4-1_run.py` · `rbac.py` · `config` 폴더 · `normalized_events.json` 과 이 안내 · 보고서 두 파일이 보여야 합니다.
2. **[보고서]** `day04_am_report.md` 의 2 · 3 · 4교시 칸에서 <mark>`답:` 뒤가 비어 있는 질문이 없는지</mark> 봅니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 서버 거절 9건 중 반복된 7건을 3과목(접근통제) 판정 함수로 판정하고 이유로 순서를 정했다 | 오전 2-1 |
| SaaS 로그에서 업무 시간 밖 로그인 · 평소와 다른 IP · 대량 다운로드를 각각 찾았다 | 오전 3-1 |
| 웹 실패 로그에서 스캐너 경로를 요청한 IP 를 찾고 나머지 실패를 제외했다 | 오전 4-1 |

오후에는 오전 탐지 결과를 <mark>**같은 사용자의 기록끼리 이어서 함께 보고**</mark>(상관분석), 위험 점수를 매겨 등급으로 나눕니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `pick_suspicious` 안

```python
    repeated_names = repeated_users.index             # 반복된 사용자의 이름들(인덱스)을 꺼낸다
    is_repeated_user = users.isin(repeated_names)     # 각 행의 사용자가 반복된 사용자 이름 안에 있는지 구해 True 또는 False 를 만든다
    suspicious = server_failures[is_repeated_user]    # True 인 행만 골라 새 표로 만든다
```

② `judge_failure` 안

```python
    parts = action.split(":")                         # ":" 로 나눠 두 조각의 리스트로 만든다
    is_allowed, reason = check_permission(user, resource, permission_action)  # 3과목(접근통제) 판정 결과를 허용 여부와 이유로 나눠 받는다
    priority = PRIORITY.get(reason, 4)                # 이유의 우선순위를 꺼낸다(없으면 4)
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 서버 실패는 <mark>**9개**</mark>, 먼저 확인할 이벤트는 <mark>**7개**</mark>, 1순위 사용자는 <mark>**dami**</mark> 입니다.

```
--- 단계 1: 판정 서버의 실패 이벤트 9 개
--- 단계 2: 먼저 확인할 실패 이벤트 7 개
--- 단계 3: 우선순위
1 퇴사한 계정 dami SALES:QUERY 2026-11-02 11:02:00
1 퇴사한 계정 dami SALES:QUERY 2026-11-02 11:03:00
1 퇴사한 계정 dami SALES:CHANGE 2026-11-02 11:05:00
1 퇴사한 계정 dami SALES:QUERY 2026-11-02 11:08:00
3 규칙은 허용인데 서버가 거절 gaeun ACCOUNT:CHANGE 2026-11-02 10:05:00
3 규칙은 허용인데 서버가 거절 gaeun ACCOUNT:CHANGE 2026-11-02 10:09:00
3 규칙은 허용인데 서버가 거절 gaeun ACCOUNT:CHANGE 2026-11-02 10:14:00
```

- (나) ① dami 의 실패 4개는 3과목(접근통제) 규칙으로 <mark>「퇴사한 계정」</mark>으로 판정됩니다.
  - 퇴사한 계정이 서버에 4번 요청했다는 것은 <mark>계정이 정리되지 않았다는 뜻이라 1순위</mark>입니다.
  - 실패 4번은 `SALES:QUERY` 3번과 `SALES:CHANGE` 1번이고, 모두 11:02 ~ 11:08 에 있습니다.
- ② gaeun 의 `ACCOUNT:CHANGE` 실패 3개는 규칙으로는 <mark>「허용」</mark>입니다(역할 `account_admin` 에 `ACCOUNT:CHANGE` 가 있습니다).
  - 규칙과 서버의 판단이 어긋난 것이라 <mark>공격이라고 확정할 수 없습니다.</mark>
  - 먼저 서버가 이 요청을 거절한 이유(서버 설정 · 다른 조건)를 확인합니다.
- (다) seoyeon 의 서버 실패는 11:40 `SETTLE:QUERY` 와 18:20 `SALES:CHANGE` 두 번이라 <mark>반복 기준(3번)에 못 미쳐서</mark> 먼저 확인할 이벤트에서 빠졌습니다.
  - 놓칠 수 있는 경우: 11:40 `SETTLE:QUERY`(정산 조회)는 3과목(접근통제) 규칙으로 「권한 없음」이었습니다. 정산처럼 중요한 자원을 권한 없이 건드렸는데 <mark>횟수 기준만 보면 한 번씩이라서 놓칩니다.</mark>
  - 그래서 현업에서는 횟수 기준과 함께 민감한 행동을 따로 보는 규칙을 더합니다.

**왜**

- <mark>거절 기록을 이유별로 다시 판정하면 급한 것부터 읽을 수 있습니다.</mark> 퇴사자 계정은 정리 작업, 권한 없음은 시도 이유 확인, 규칙은 허용인데 거절은 서버 점검으로 해야 할 일이 다릅니다.

**자주 틀리는 곳**

- `isin` 에 `repeated_users` 를 그대로 넣고 `.index` 를 빼면 오류는 나지 않지만 **단계 2가 7개가 아니라 0개로 줄어듭니다.** `repeated_users` 의 값은 횟수이고 사용자 이름은 왼쪽 인덱스에 있어서, 이름을 담은 `.index` 를 넣어야 합니다.
- `.index` 뒤에 괄호를 붙여 `.index()` 라고 쓰면 `TypeError` 오류가 납니다. **`.index` 는 괄호 없이 씁니다.**
  - 실행하면 다음 오류가 납니다(<mark>`'Index' object is not callable`</mark> 이 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day04_2-1_run.py", line 10, in <module>
    suspicious = pick_suspicious(server_failures)                # 먼저 확인할 실패 이벤트만 골라낸다
  File "…/anomaly_detection/access_detection.py", line 41, in pick_suspicious
    repeated_names = repeated_users.index()  # 반복된 사용자의 이름들(인덱스)을 꺼낸다
TypeError: 'Index' object is not callable
```

  - 줄 번호는 사람마다 다릅니다.

**관제에서는**

- 서버가 거절한 요청을 권한 규칙으로 다시 판정하면, 그 거절이 규칙대로였는지 확인할 수 있습니다. <mark>「규칙은 허용인데 거절」이 반복되면 공격이 아니라 설정 오류일 수 있어,</mark> 점검 대상으로 따로 분류합니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `find_off_hours_logins` 안

```python
    is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)  # 시가 업무 시간 안인지 구해 True 또는 False 를 만든다
    is_off_hours = ~is_business_hour                  # True 와 False 를 뒤집어 업무 시간 밖인 행을 True 로 만든다
```

② `find_new_ip_users` 안

```python
        has_usual_ip = usual_ip is not None           # 평소 IP 기록이 있는지 구한다
        is_new_ip = ip != usual_ip                    # 이번 IP 가 평소 IP 와 다른지 구한다
        if has_usual_ip and is_new_ip:                # 평소 IP 기록이 있고, 이번 IP 가 평소와 다르면 — 미리 채운 줄
            new_ip_users.append(user)                 # 리스트에 사용자를 추가한다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 업무 시간 밖 로그인은 <mark>**jiwoo**</mark>, 평소와 다른 IP 는 <mark>**jiwoo · seoyeon**</mark>, 대량 다운로드는 <mark>**seoyeon**</mark> 입니다.

```
--- 단계 1: 업무 시간 밖 로그인 1 건
                  time source   user            ip action result
0  2026-11-02 02:14:08   saas  jiwoo  203.0.113.80  login     실패
--- 단계 2: 평소와 다른 IP 로 로그인한 사용자 ['jiwoo', 'seoyeon']
--- 단계 3: 파일을 5번 이상 내려받은 사용자 ['seoyeon']
```

- (나) <mark>확정할 수 없습니다.</mark>
  - jiwoo 의 02:14 로그인은 실패였고, 같은 날 16:02 에는 평소 IP(198.51.100.52)로 성공했습니다. 다른 IP 에서 실패한 시도가 있었을 뿐이라 <mark>계정이 도용됐다는 근거가 부족합니다.</mark>
  - 더 확인할 정보의 예: 같은 IP(203.0.113.80)가 17:38 에 seoyeon 으로 로그인했으므로, 이 IP 의 다른 활동이 더 있는지 봅니다.
- (다) 제외하지 않으면 gaeun 의 로그인(198.51.100.77)이 「평소와 다른 IP」로 탐지되어 <mark>오탐 알림이 늘어납니다</mark>.
  - 제외하면 다른 사람이 gaeun 계정을 쓰고 있어도 이 규칙으로는 찾지 못하는 <mark>위험이 남습니다</mark>.
  - 그래서 평소 기록을 수집한 뒤에 규칙을 적용합니다.

**왜**

- <mark>세 규칙을 따로 찾아 두면 사용자마다 어떤 기준에 해당하는지 바로 보입니다.</mark> jiwoo 와 seoyeon 은 두 규칙에 해당하고, 6교시에서 규칙마다 점수를 더하면 먼저 볼 순서가 정해집니다.

**자주 틀리는 곳**

- `~is_business_hour` 대신 `not is_business_hour` 라고 쓰면 `ValueError` 오류가 납니다. **열에는 `~` 를 씁니다.**
  - 실행하면 다음 오류가 납니다(<mark>`The truth value of a Series is ambiguous`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day04_3-1_run.py", line 7, in <module>
    off_hours_logins = find_off_hours_logins(logins)             # 업무 시간 밖 로그인만 골라낸다
  File "…/anomaly_detection/saas_detection.py", line 49, in find_off_hours_logins
    is_off_hours = not is_business_hour  # True 와 False 를 뒤집어 업무 시간 밖인 행을 True 로 만든다
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

  - 줄 번호는 사람마다 다릅니다.
- `ip != usual_ip` 대신 `ip == usual_ip` 라고 쓰면 오류는 나지 않지만 **평소 IP 로 로그인한 사용자가 나옵니다.** 단계 2에 junho 가 두 번 나오는 것이 이 실수의 모습입니다.

**관제에서는**

- <mark>규칙 하나마다 알림을 내면 오탐이 쌓여서 담당자가 알림을 무시하게 됩니다.</mark> 해당하는 규칙 수를 점수로 쓰면 먼저 볼 순서를 정할 수 있습니다. 내일(11/6(금))에는 오탐과 미탐을 직접 세어 봅니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_4-1_run.py
python advanced_detection.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `find_scan_ips` 안

```python
    actions = web_failures["action"]                  # action 열만 꺼낸다
    is_scanner = actions.str.contains(SCANNER_PATTERN)  # 각 행에 스캐너 경로가 들어 있는지 구해 True 또는 False 를 만든다
    scanner_rows = web_failures[is_scanner]           # True 인 행만 골라 새 표로 만든다
    scan_counts = scanner_rows["ip"].value_counts()   # IP 별로 스캐너 경로를 몇 번 요청했는지 센다
```

② `explain_scan` 안

```python
    reason = "스캐너 경로를 " + str(request_count) + "번 요청"  # 문자열을 연결해 이유 문장을 만든다
    scan_info = {"ip": ip, "reason": reason}          # IP 와 이유를 딕셔너리로 만든다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 스캔으로 본 IP 는 <mark>**198.51.100.90**</mark> 하나입니다. 이유는 「스캐너 경로를 3번 요청」입니다.

```
--- 단계 1: 웹 서버의 실패 이벤트 13 개
--- 단계 2: 스캐너 경로를 요청한 IP 와 횟수
ip
198.51.100.90    3
Name: count, dtype: int64
--- 단계 3: 스캔으로 본 IP 와 이유
{'ip': '198.51.100.90', 'reason': '스캐너 경로를 3번 요청'}
--- 단계 4: 스캐너 경로가 없어 제외한 IP
203.0.113.50
198.51.100.21
198.51.100.34
198.51.100.77
```

`advanced_detection.py` 의 출력은 다음과 같습니다.

```
판정 서버: 먼저 확인할 실패 이벤트 7 개
SaaS: 업무 시간 밖 ['jiwoo'] · 평소와 다른 IP ['jiwoo', 'seoyeon'] · 대량 다운로드 ['seoyeon']
웹 서버: 스캔으로 본 IP ['198.51.100.90']
```

- (나) 203.0.113.50 은 실패한 요청이 7번(`POST /login` 5번 · `GET /admin` · `GET /admin/users`)이지만 <mark>스캐너 경로가 하나도 없어서</mark> 제외됩니다.
  - 제외하지 않으면 경로 스캔 알림에 로그인과 관리자 화면 실패가 섞여, 담당자가 경로 스캔과 로그인 실패를 구분하기 어려워집니다.
  - 이 IP 는 어제 오전의 로그인 규칙에서 따로 다룬 대상입니다.
- (다) 198.51.100.21 의 `GET /board/99` 는 <mark>`SCANNER_PATTERN` 의 세 경로(`/.env` · `/wp-login` · `/phpmyadmin`) 중 어느 것도 아니라서</mark> `is_scanner` 가 `False` 가 되어 제외됩니다.
  - 해킹 도구가 `/backup.zip` 처럼 목록에 없는 경로를 요청하면 `str.contains` 가 `False` 라서 이 규칙은 놓칩니다. 경로 목록을 정해 두었기 때문에 생기는 한계입니다.
  - 그래서 현업에서는 경로 목록을 새 위협에 맞춰 갱신합니다.

**왜**

- <mark>해킹 도구가 자주 요청하는 경로를 요청한 IP 만 골라 알리면 오타 실패와 섞이지 않습니다.</mark> 대신 목록에 없는 경로는 놓치므로, 내일 오탐과 미탐을 세면서 확인합니다.

**자주 틀리는 곳**

- `.str.contains` 에서 `.str` 을 빼고 `actions.contains(…)` 라고 쓰면 `AttributeError` 오류가 납니다. **열의 문자열 메서드는 `.str.` 뒤에 씁니다.**
  - 실행하면 다음 오류가 납니다(<mark>`'Series' object has no attribute 'contains'`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day04_4-1_run.py", line 8, in <module>
    scan_ips, scan_counts = find_scan_ips(web_failures)          # 스캔 IP 와 IP 별 요청 횟수를 찾는다
  File "…/anomaly_detection/malicious_detection.py", line 36, in find_scan_ips
    is_scanner = actions.contains(SCANNER_PATTERN)  # 각 행에 스캐너 경로가 들어 있는지 구해 True 또는 False 를 만든다
AttributeError: 'Series' object has no attribute 'contains'
```

  - 줄 번호는 사람마다 다릅니다.
- 4번에서 `scanner_rows["ip"]` 대신 `web_failures["ip"]` 로 세면 오류는 나지 않지만 **스캐너 경로와 상관없이 모든 IP 가 스캔으로 나옵니다.** 203.0.113.50 이 7번으로 나오는 것이 이 실수의 모습입니다.

**관제에서는**

- 경로 스캔은 대응이 정해져 있는 편입니다(해당 IP 를 막을지 판단). <mark>조건을 정해 오탐을 줄인 알림은 담당자가 근거를 확인할 수 있습니다.</mark>

---

### 정답 마무리

- `ls` 결과에 오늘 파일들과 `config` 폴더, 이 안내 · 보고서 두 파일이 모두 보이면 됩니다.
- 보고서에 빈 `답:` 이 없으면 됩니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.
