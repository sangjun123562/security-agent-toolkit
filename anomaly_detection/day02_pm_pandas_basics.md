# 11/3(화) 오후 · 4과목 이상탐지 ② — 판다스로 정규화된 이벤트 읽고 세기 · 시간대별로 묶기 — 실습

오전에는 웹 서버 · 판정 서버 · SaaS 로그 3종류를 같은 형식(정규화)으로 맞췄습니다. 오후에는 그렇게 맞춘 이벤트를 **판다스(pandas)** 로 표처럼 읽고 세는 법을 배웁니다. 이벤트를 세고 묶는 일은 SIEM(심)의 다음 단계인 탐지를 하기 위한 준비입니다.

- **5교시**: 정규화된 이벤트 파일을 표로 읽고, 실패한 이벤트만 골라 소스별로 셉니다.
- **6교시**: 실패를 사용자별 · 시간대별로 묶어 세고, 실패한 이벤트를 CSV 파일로 저장합니다.

오늘은 오후 5 · 6교시이고, 깃허브에 올리는 일은 6교시 마지막에 합니다. 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **파이썬 · VS Code · 터미널 · git** 이고, 판다스를 처음 씁니다. 도커는 11/6(금) 오후에 씁니다.
- 새로 나오는 판다스 문법은 읽을거리의 「판다스 문법 상자」에서 코드와 실행 결과, 표가 바뀌는 모양과 함께 설명합니다.
- 이벤트 데이터는 문서에 붙여 넣는 **샘플 파일**(`normalized_events.json`) 하나만 씁니다. 57개이고, 오전에 정규화한 결과와 같은 키로 되어 있습니다.
  - 📎 오늘 불러 쓰는 이전 파일은 없습니다. 오전 파일이 없어도 풀 수 있습니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 터미널 줄 맨 앞에 `(.venv)` 처럼 가상환경 이름이 보이는지 봅니다. 보이면 3번으로 가고, 안 보이면 아래를 칩니다(맥북은 `Scripts` 를 `bin` 으로, 가상환경 폴더 이름이 다르면 그 이름으로). 가상환경은 프로젝트마다 따로 패키지(판다스 같은 라이브러리)를 설치해 두는 파이썬 실행 환경입니다.
   ```bash
   source .venv/Scripts/activate
   ```
3. **[터미널]** `anomaly_detection` 폴더로 들어가 위치를 확인하고 판다스를 설치합니다(맥북은 `python3`).
   ```bash
   cd anomaly_detection
   pwd
   python -m pip install pandas
   python -c "import pandas; print(pandas.__version__)"
   ```
   - `pwd` 가 `…/anomaly_detection` 으로 끝나야 합니다.
   - 설치가 끝나면 `Successfully installed …` 또는 `Requirement already satisfied` 가 나옵니다. 마지막에 `WARNING: You are using pip version …` 이 나와도 무시합니다.
   - 마지막 명령에서 점이 든 숫자(예: `2.3.3`)가 나오면 판다스를 쓸 수 있습니다.
4. **오늘 받은 파일 두 개**(`day02_pm_pandas_basics.md`, `day02_pm_report.md`)를 `다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
5. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-03(화))` 의 `이름` 을 내 이름으로 바꿉니다. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
6. **[VS Code 또는 터미널]** `anomaly_detection` 폴더에 `normalized_events.json` 파일을 만들어 아래 내용을 그대로 붙여 넣습니다(터미널에서는 `touch normalized_events.json` 후 VS Code 에서 엽니다).

**`normalized_events.json`** — 정규화된 이벤트 샘플입니다. 한 줄이 이벤트 1개이고, 시간순으로 정렬되어 있습니다. `raw`(원래 로그 한 줄 전체)는 길어서 이 파일에서 뺐습니다. `null` 은 그 값이 로그에 없다는 뜻입니다.

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

7. **[터미널]** 이벤트가 57개인지 확인합니다(맥북은 `python3`).
   ```bash
   python -c "import json; print(len(json.load(open('normalized_events.json', encoding='utf-8'))))"
   ```
   - `57` 이 나와야 합니다. 아니면 붙여 넣다가 줄이 빠졌거나 `[` `]` 가 빠진 것입니다. 다시 붙여 넣습니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다.
- `No module named 'pandas'`: 판다스가 설치되지 않았거나 가상환경이 꺼진 터미널입니다. 위 2 · 3번을 같은 터미널에서 다시 합니다.
- `FileNotFoundError` · `ValueError`: 위치나 파일 이름이 틀렸거나, 붙여 넣은 JSON 의 `[` `]` · 쉼표가 틀렸습니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다(맥북은 `python3`).

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 정규화된 이벤트를 표로 읽고 실패만 골라 세기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다(3과목의 판정 서버가 아니라, 여러 로그를 같은 모양으로 맞춘 이벤트 이야기입니다):
> 「이벤트 파일이 생겼습니다. 오늘은 57개뿐이지만 실제로는 하루에 수만 개가 쌓입니다. 지금까지는 파이썬 리스트와 딕셔너리를 `for` 로 돌려 하나씩 세었는데, 이벤트가 늘수록 코드도 길어집니다.
>
> 이 파일을 표로 읽어 몇 개가 들어 있는지 알려 주세요. 성공과 실패가 각각 몇 개인지, 실패는 어느 소스(웹 서버 · 판정 서버 · SaaS)에서 몇 개씩 났는지도 알려 주세요.」
> - **왜 중요한가**: <mark>실패한 이벤트만 걸러 내고 소스별로 세는 일은 로그를 조사할 때마다 합니다.</mark> 표로 읽으면 이 일이 몇 줄로 끝나고, 이벤트가 57개든 5만 개든 같은 코드를 씁니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 지금까지 이벤트나 요청은 파이썬 **리스트와 딕셔너리**로 다뤘습니다. 값별로 세려면 `for` 로 하나씩 꺼내 딕셔너리에 더해 가야 했습니다.
2. **판다스(pandas)** 는 데이터를 표로 읽고, 짧은 코드로 걸러 내고 셀 수 있게 해 주는 파이썬 라이브러리입니다.
   - 판다스의 표를 **데이터프레임(DataFrame)** 이라고 부릅니다.
   - 가로 한 줄이 **행**, 세로 한 줄이 **열**입니다. 이 수업에서는 행 하나가 이벤트 1개이고, 열 하나는 `time` 같은 키 하나의 값 전체입니다.
3. 오늘 가르치는 판다스는 로그 분석에 실제로 자주 쓰는 것만 골랐습니다. 5교시는 읽기 · 걸러 내기 · 세기, 6교시는 묶기 · 시간 다루기 · 저장입니다.

**라이브러리(library)는 다른 사람이 미리 만들어 둔 파이썬 코드입니다. 판다스는 표 형태의 데이터를 다루는 라이브러리입니다.**

**파이썬과 판다스의 관계**

- **파이썬**: 프로그래밍 언어입니다. 변수, 리스트, 딕셔너리, 함수, 반복문 같은 기본 문법을 제공합니다.
- **판다스**: 먼저 설치(`pip install pandas`)하고, 코드 맨 위에서 `import pandas as pd` 로 불러와야 씁니다.
- 판다스 코드는 파이썬 파일 안에서만 실행됩니다.
  - 그래서 오늘 코드에는 지금까지 배운 파이썬 문법(함수, `for`, 딕셔너리)과 판다스 문법이 함께 나옵니다.
  - 판다스 문법은 두 가지 모양입니다. 하나는 `pd.read_json(...)` 처럼 `pd.` 로 시작하는 것이고, 다른 하나는 `events.shape` · `sources.value_counts()` 처럼 표나 열 뒤에 `.이름` 이 붙은 것입니다.

### 📖 5.1 정규화된 이벤트의 모양

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

정규화는 서로 다른 모양의 로그를 같은 키로 맞추는 일입니다. 먼저 오늘 쓰는 이벤트가 **어느 로그에서 왔는지**부터 봅니다. 로그는 세 종류입니다.

| `source` | 무엇이 남기나 | 한 줄이 생기는 때 | 예 |
|---|---|---|---|
| `web` | 회사 게시판 같은 웹 서비스를 돌리는 웹 서버(nginx) | 누가 페이지를 열거나 로그인할 때 | 203.0.113.50 이 `POST /login` 을 요청함 |
| `server` | 3과목에서 만든 권한 판정 서버 | 누가 어떤 권한을 써도 되는지 물을 때 | seoyeon 이 `SALES:CHANGE` 를 요청해 거부됨 |
| `saas` | 회사가 빌려 쓰는 SaaS(인터넷으로 쓰는 소프트웨어, 예: 파일 보관 서비스) | 로그인하거나 파일을 올리고 내려받을 때 | seoyeon 이 `file.download` 를 함 |

이벤트 하나는 위 세 로그 중 한 곳의 로그 한 줄을 같은 형식으로 맞춘 것입니다. 오늘 쓰는 파일의 키는 여섯 개입니다. 오전의 공통 이벤트에는 `raw` 키가 하나 더 있었는데, 이 샘플 파일은 길어서 `raw` 를 뺐습니다.

| 키 | 뜻 | 예 |
|---|---|---|
| `time` | 일어난 시각(한국 시간) | `2026-11-02 09:12:03` |
| `source` | 어느 로그에서 왔는지 | `web`(웹 서버) · `server`(판정 서버) · `saas`(SaaS 서비스) |
| `user` | 누가 했는지 | `seoyeon`. 웹 서버 로그에는 사용자 이름이 없어서 `null` |
| `ip` | 어느 주소에서 왔는지 | `203.0.113.50`. 판정 서버 로그에는 주소가 없어서 `null` |
| `action` | 무엇을 했는지 | `POST /login` · `SALES:CHANGE` · `file.download` |
| `result` | 성공했는지 | `성공` 또는 `실패` |

**`ip` · `user` · `result` 는 로그마다 이렇게 정해집니다.**

| 키 | `web` | `server` | `saas` |
|---|---|---|---|
| `ip` | 웹 서버에 요청을 보낸 쪽의 주소 | 없음(`null`). 원래 로그에 주소가 없고 접속 위치만 있음 | 서비스에 로그인한 사람이 접속한 곳의 주소 |
| `user` | 없음(`null`). 웹 서버는 로그인한 계정을 모름 | 요청한 계정 | 메일 주소의 앞부분(`seoyeon@…` → `seoyeon`) |
| `result` | 상태 코드가 400 이상이면 `실패` | `allowed` 가 거짓이면 `실패` | `outcome` 이 `failure` 이면 `실패` |

- 주소(`ip`)는 사람이 아니라 **접속한 곳**입니다. 요청을 보낸 곳은 직원의 PC일 수도, 집이나 카페일 수도, 공격하는 쪽일 수도 있습니다.
  - 한 사무실의 여러 사람이 같은 주소로 보일 수 있습니다.
  - 한 사람이 집과 회사에서 다른 주소로 접속할 수도 있습니다.
  - 이 수업의 `203.0.113.50` · `198.51.100.x` · `192.0.2.x` 는 문서에서 예시로 쓰라고 정해 둔 주소 범위라서 실제 장비를 가리키지 않습니다.
- 원래 로그에 없는 값(결측값, missing value)은 임의로 채우지 않고 `null` 로 둡니다. 없는 값을 임의로 채우면 분석 결과가 틀려지기 때문입니다.
  - 이 값은 JSON 파일에서는 `null`, 파이썬과 판다스 표에서는 `None` 또는 `NaN` 으로 보이며, 모두 「값이 없다」는 같은 뜻입니다.
- 판다스로 읽으면 이 파일이 아래 같은 표가 됩니다. 맨 왼쪽 숫자는 판다스가 붙이는 행 번호(인덱스, index)입니다.

| 행 번호 | time | source | user | ip | action | result |
|---|---|---|---|---|---|---|
| 0 | 2026-11-02 02:14:08 | saas | jiwoo | 203.0.113.80 | login | 실패 |
| 1 | 2026-11-02 09:01:05 | web | None | 198.51.100.21 | GET / | 성공 |
| 2 | 2026-11-02 09:01:06 | web | None | 198.51.100.21 | GET /static/app.css | 성공 |

### 📖 5.2 판다스로 표 읽기 · 세기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽어도 되고, `normalized_events.json` 이 있는 폴더에서 따라 쳐 보아도 됩니다.

**🐼 판다스 문법 상자 — 파일을 표로 읽기**

**<mark>`pd.read_json(파일 이름)`</mark> 은 JSON 파일을 열어 「표」(데이터프레임, DataFrame)로 만듭니다**

표는 가로 한 줄(행)과 세로 한 줄(열)로 이루어집니다. 이 수업의 이벤트 표에서는 **행 하나가 이벤트 1개**이고, **열 하나가 같은 키**(`time` · `source` …)입니다. 지금까지는 `for` 로 이벤트를 하나씩 꺼내 확인했습니다. 파일을 표로 읽으면 걸러 내기와 세기를 코드 한 줄로 할 수 있습니다(아래에서 차례로 배웁니다).

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나
row_count = len(events)                          # 표의 행이 몇 개인지 센다 — 리스트의 길이를 세던 len 과 같다
print(row_count)                                 # 57 이 나온다 — 이벤트 57개
```

실행 결과:

```
57
```

- 읽는 법: `57` 은 표의 행 수이고, 행 하나가 이벤트 하나이므로 이벤트 57개라는 뜻입니다.
- `import pandas as pd` 는 판다스를 불러오고, 이름을 `pd` 로 줄여 쓰겠다는 뜻입니다. `read_json` 처럼 표를 만드는 판다스 함수는 앞에 `pd.` 를 붙여 부릅니다.
- `pd.read_json(파일 이름)` 은 JSON 파일의 이벤트 57개를 읽어 표 하나로 만들어 리턴합니다.

**알아 둘 것 — 표의 크기 보기**

`.shape` 는 표가 몇 행 몇 열인지 알려 줍니다. 문제 5-1 의 `describe_events` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

shape = events.shape                             # 표의 크기를 (행 수, 열 수) 로 구한다
print(shape)                                     # (57, 6) 이 나온다 — 이벤트 57개(행), 열 6개
```

실행 결과:

```
(57, 6)
```

- 읽는 법: `(57, 6)` 은 57행 6열, 이벤트 57개에 열 6개라는 뜻입니다.

**🐼 판다스 문법 상자 — 열 하나 꺼내기**

**<mark>`표["열 이름"]`</mark> 은 표에서 열 하나를 꺼냅니다. 꺼낸 열을 시리즈(Series)라고 합니다**

`events["source"]` 로 꺼낸 시리즈입니다. 값마다 그 값이 있던 행의 번호(인덱스)가 왼쪽에 함께 나옵니다. 아래는 앞 4개와 마지막 1개입니다.

| 행 번호 | `events["source"]` |
|---|---|
| 0 | saas |
| 1 | web |
| 2 | web |
| 3 | web |
| … | … |
| 56 | server |

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

sources = events["source"]                       # source 열 하나를 꺼낸다 — web · server · saas 값이 57개 들어 있다
source_count = len(sources)                      # 꺼낸 열에 값이 몇 개 있는지 센다
print(source_count)                              # 57 이 나온다 — 행마다 값이 하나씩이라 행 수와 같다
```

실행 결과:

```
57
```

- 읽는 법: `57` 은 꺼낸 열에 든 값의 개수입니다. 행이 57개이므로 값도 57개입니다.
- `events["source"]` 는 표에서 `source` 열만 꺼냅니다(판다스에서는 열 하나를 Series, 시리즈라고 부릅니다).
- 열 이름은 파일에 적힌 키와 똑같이 써야 합니다. 없는 열 이름을 쓰면 `KeyError` 오류가 납니다.

**알아 둘 것 — 열의 앞 몇 개만 보기**

`열.head(3)` 은 열의 앞에서 3개만 남깁니다. 문제 5-1 의 `describe_events` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

times = events["time"]                           # 표에서 time 열만 꺼낸다 — 이벤트 57개의 시각이 한 줄로 나열된 열
first_times = times.head(3)                      # 그 열의 처음 3개(0 ~ 2번 행)만 남긴다
for time_text in first_times:                    # 처음 3개를 하나씩 꺼낸다
    print(time_text)                             # 시각 하나를 한 줄에 출력한다(모두 3줄)
```

실행 결과:

```
2026-11-02 02:14:08
2026-11-02 09:01:05
2026-11-02 09:01:06
```

- 읽는 법: 시각 57개 중 앞의 3개입니다.

**🐼 판다스 문법 상자 — 값별로 개수 세기**

**<mark>`.value_counts()`</mark> 는 열에서 같은 값이 몇 번 나왔는지 세어 많은 순서로 알려 줍니다**

`events["source"]` 열에 `.value_counts()` 를 하면 같은 값끼리 모아 개수를 세고, 많은 값부터 보여 줍니다.

| 값 | 개수 |
|---|---|
| web | 28 |
| server | 15 |
| saas | 14 |

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

sources = events["source"]                       # source 열 하나를 꺼낸다 — web · server · saas 값이 57개 들어 있다
counts = sources.value_counts()                  # 같은 값이 몇 번 나왔는지 센다 — 많은 값부터 정렬되어 나온다
print(counts)                                    # 값(web · server · saas)과 그 개수가 줄마다 나온다
```

실행 결과:

```
source
web       28
server    15
saas      14
Name: count, dtype: int64
```

- 읽는 법: 첫 줄 `source` 는 센 열의 이름이고, 아래 줄은 왼쪽이 값, 오른쪽이 나온 횟수입니다. 28 + 15 + 14 = 57 이라 이벤트 전체 개수와 같습니다.
- `value_counts()` 는 같은 값이 몇 번 나왔는지 세어 **많은 순서**로 리턴합니다. 맨 아래 `Name: count, dtype: int64` 줄은 읽지 않아도 됩니다.
- 3과목에서 딕셔너리로 값별 횟수를 세던 `counts[value] = counts.get(value, 0) + 1` 과 같은 일을 한 줄로 합니다.

**알아 둘 것 — 열 꺼내기와 값별 세기는 실무에서 한 줄로 씁니다**

앞의 두 줄(`sources = events["source"]` → `counts = sources.value_counts()`)은 실무에서 아래 한 줄로 자주 씁니다. 같은 일입니다. 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

counts = events["source"].value_counts()         # 열 꺼내기와 값별 세기를 한 줄로 쓴 모양 — 위 두 줄과 같은 결과
print(counts)                                    # 값(web · server · saas)과 그 개수가 줄마다 나온다
```

실행 결과:

```
source
web       28
server    15
saas      14
Name: count, dtype: int64
```

**알아 둘 것 — 조건에 맞는 행만 걸러 내기**

`표[조건]` 은 조건이 `True` 인 행만 남긴 새 표를 만듭니다. 이 일을 필터링(filtering)이라고 합니다. 여기서 조건은 행마다 `True` 또는 `False` 가 하나씩 있는 열입니다(아래 코드의 `is_fail`). 문제 5-1 의 `pick_failed` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다 — 성공 · 실패가 57개 나열된 열
is_fail = results == "실패"                      # result 열의 각 값이 "실패"와 같은지 비교해 행마다 True 또는 False 를 하나씩 만든다(57개)
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다
failed_shape = failed.shape                      # 새 표의 크기를 꺼낸다
print(failed_shape)                              # (23, 6) — 실패한 이벤트 23개, 열은 그대로 6개
```

실행 결과:

```
(23, 6)
```

- 읽는 법: 실패한 이벤트 23개만 남았다는 뜻입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` | 파일 경로 | 이벤트 표 |
| `describe_events` | 이벤트 표 | 표 크기 `(행 수, 열 수)` 와 `time` 열의 처음 3개 |
| `pick_failed` | 이벤트 표 | `result` 가 `실패` 인 행만 담은 표 |
| `count_values` | 표와 열 이름 | 그 열의 값별 개수 |

- **직접 쓰는 곳은 세 함수**(번호 1 ~ 4)입니다. 아직 배우지 않은 문법(`.shape` · `.head(3)` · 조건으로 걸러 내기)이 나오는 줄은 미리 채웠고, `import` 와 실행 파일도 미리 채웠습니다.
  - `load_events`(1번): 파일을 표로 읽습니다.
  - `describe_events`(2번): 시각 열을 꺼냅니다. 크기(`.shape`)와 앞 3개(`.head(3)`)는 미리 채웠습니다.
  - `count_values`(3 · 4번): 열 하나의 값별 개수를 셉니다.
  - `pick_failed`(미리 채움): 실패인 행만 걸러 냅니다. 읽어 보기만 합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 정규화된 이벤트 표를 읽어 실패한 이벤트를 소스별로 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 이벤트 파일에 57개가 있지만, 실패가 몇 개이고 어느 소스에서 났는지는 사람이 한 줄씩 읽어야 압니다.
- **그래서 만드는 것**: `events_basic.py` 입니다.
  - 파일을 표로 읽습니다.
  - 실패한 이벤트만 골라냅니다.
  - 열 하나의 값별 개수를 셉니다.
- **실행하면**: 단계 1: 표 크기(행 수, 열 수)와 처음 3개 시각, 단계 2: 성공 · 실패 개수, 단계 3: 실패한 이벤트의 소스별 개수, 단계 4: 전체 이벤트의 소스별 개수가 나옵니다.
- **현업에서는**: 관제 화면의 「실패 이벤트 수 · 소스별 분포」 그래프가 이 계산입니다. 어느 소스부터 조사할지 정할 때 봅니다.

**🎯 할 일**

1. `events_basic.py` · `day02_5-1_run.py` 두 파일을 만들고, `events_basic.py` 의 `load_events` · `describe_events` · `count_values` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>표 크기(행 수, 열 수)와 처음 3개 시각</mark>(단계 1), <mark>성공 · 실패 개수</mark>(단계 2), <mark>실패한 이벤트의 소스별 개수</mark>(단계 3), <mark>전체 이벤트의 소스별 개수</mark>(단계 4)를 읽습니다.

**`events_basic.py`**

```python
import pandas as pd                     # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"  # 읽을 정규화 이벤트 파일 이름


def load_events(path):                  # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. pd.read_json 으로 path 의 파일을 읽어 events 에 담는다
    return events                       # 표를 리턴한다


def describe_events(events):            # 표를 받는 함수
    """표의 크기와 앞 시각 3개를 구한다.
    새 파일을 받았을 때 내용이 제대로 들어 있는지 확인하는 데 쓴다.
    """
    shape = events.shape                # 표의 크기 (행 수, 열 수) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. events 의 "time" 열을 꺼내 times 에 담는다 (events["time"])
    first_times = times.head(3)         # 그 열의 앞 3개만 남긴다 — 미리 채운 줄
    return shape, first_times           # 크기와 처음 3개를 리턴한다


def pick_failed(events):                # 표를 받는 함수
    """실패한 이벤트만 골라 새 표로 만든다.
    무엇이 잘못됐는지 조사할 때 성공한 이벤트는 빼고 보는 데 쓴다.
    """
    results = events["result"]          # result 열 하나를 꺼낸다
    is_fail = results == "실패"         # 행마다 실패면 True, 아니면 False
    failed = events[is_fail]            # True 인 행만 남긴다
    return failed                       # 실패한 행만 담은 표를 리턴한다


def count_values(table, column):        # 표와 열 이름을 받는 함수
    """한 열의 값별 개수를 센다.
    소스별 · 결과별 · 사용자별로 몇 개인지 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. table 의 column 열을 꺼내 values 에 담는다
    # 4. values 에서 값별 개수를 value_counts() 로 세어 counts 에 담는다
    return counts                       # 값별 개수를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 4번은 모두 함수 안이라 앞에 공백 4개입니다.
- 번호 주석이 연달아 붙어 있어도(예: 3 · 4번), 주석 3번 아래에 코드 한 줄, 주석 4번 아래에 코드 한 줄을 씁니다.
- 채우기 전에 실행하면 `NameError: name 'events' is not defined` 오류가 납니다. `events` 를 만드는 1번 줄이 비어 있기 때문입니다. 다른 번호가 비어 있어도 비슷한 오류가 납니다.
- 2번의 `events["time"]` 과 3번의 `table[column]` 은 같은 열 꺼내기이고, 3번은 열 이름을 `column` 이라는 변수로 받는 것이 다릅니다.

**`day02_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 이벤트 파일을 읽어 네 단계로 출력합니다. `len(표)` 는 표의 행 수입니다.

```python
from events_basic import load_events, describe_events, pick_failed, count_values, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                   # 이벤트 파일을 표로 읽는다
shape, first_times = describe_events(events)        # 표 크기와 time 열의 처음 3개를 구한다
print("--- 단계 1: 표 크기(행 수, 열 수)와 처음 3개 시각")  # 단계 1 시작을 알리는 줄
print(shape)                                        # (행 수, 열 수)를 출력한다
for time_text in first_times:                       # 처음 3개 시각을 하나씩 꺼낸다
    print(time_text)                                # 시각 하나를 한 줄에 출력한다(모두 3줄)

result_counts = count_values(events, "result")      # result 열의 값별 개수를 센다
print("--- 단계 2: 성공 · 실패별 개수")             # 단계 2 시작을 알리는 줄
print(result_counts)                                # 성공 · 실패 개수를 출력한다

failed = pick_failed(events)                        # 실패한 이벤트만 골라낸다
failed_count = len(failed)                          # 실패한 이벤트가 몇 개인지 센다
source_counts = count_values(failed, "source")      # 실패한 이벤트의 소스별 개수를 센다
print("--- 단계 3: 실패한 이벤트", failed_count, "개의 소스별 개수")  # 단계 3 시작을 알리는 줄
print(source_counts)                                # 소스별 개수를 출력한다

all_source_counts = count_values(events, "source")  # 전체 이벤트의 소스별 개수를 센다
print("--- 단계 4: 전체 이벤트의 소스별 개수")      # 단계 4 시작을 알리는 줄
print(all_source_counts)                            # 소스별 전체 개수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `events_basic.py` · `day02_5-1_run.py` 를 만들어 위 코드를 붙여 넣습니다(터미널에서는 `touch events_basic.py day02_5-1_run.py` 후 VS Code 에서 엽니다).
2. **[VS Code]** `events_basic.py` 에서 직접 쓰는 곳 네 군데를 씁니다. 5.2 의 판다스 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day02_5-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_5-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 네 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1은 4줄, 단계 2는 4줄, 단계 3은 5줄, 단계 4는 5줄입니다.
5. **[보고서]** `day02_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 표의 행 수와 열 수, 성공과 실패 개수, 실패한 이벤트의 소스별 개수를 적어 주세요.
   - (나) 🔍 실패 개수만 보면 web 이 가장 많습니다. 그렇다면 web 이 가장 문제가 큰 소스라고 말할 수 있을까요? 단계 4의 전체 이벤트 수와 함께 보고 이유를 적어 주세요.
   - (다) 🔍 web 이벤트에는 `user` 가 비어 있습니다. 사용자 이름으로 실패를 세려 할 때 web 의 실패 13개는 어떻게 될지 예상하고, 사용자 대신 어떤 열을 보면 같은 대상이 반복했는지 알 수 있을지 이유와 함께 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 판다스 불러오기 | `import pandas as pd` |
| JSON 파일을 표로 읽기 | `events = pd.read_json(path)` (`load_events`) |
| 표 크기 | `shape = events.shape` (`describe_events`) |
| 열 하나 꺼내기 | `times = events["time"]` |
| 처음 3개만 보기 | `first_times = times.head(3)` |
| 실패한 행만 걸러 내기 | `results = events["result"]` → `is_fail = results == "실패"` → `failed = events[is_fail]` (`pick_failed`) |
| 값별 개수 | `values = table[column]` → `counts = values.value_counts()` (`count_values`) |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 실패를 사용자별 · 시간대별로 묶어 세고 저장하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「실패한 이벤트가 23개라는 것은 알았습니다. 이제 두 가지를 알려 주세요.
>
> - 누가 얼마나 실패했는지: 사용자별로, 많은 순서대로
> - 하루 중 언제 많이 났는지: 몇 시에 몇 개인지
>
> 그리고 실패한 이벤트만 따로 파일로 저장해 주세요. 담당자가 엑셀로 열어 근거를 확인합니다.」
> - **왜 중요한가**: <mark>실패 23개를 전체 합계로만 보면 평범한 숫자입니다.</mark> 사용자별 · 시간대별로 묶으면 한 사용자나 한 시간대에 많이 난 실패가 드러납니다. 근거 이벤트를 파일로 저장해야 담당자가 알림이 왜 났는지 확인할 수 있습니다. 11/4(수)에 평소 기준을 세우는 기초 계산이기도 합니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 5교시에는 열 하나의 값별 개수를 셌습니다(`value_counts`). 이번에는 **조건에 맞는 행들을 다른 열 기준으로 묶어** 셉니다. 예를 들어 「실패한 이벤트를 사용자별로」입니다.
2. `time` 열의 `"2026-11-02 09:01:05"` 는 문자열이라서 「시」만 꺼낼 수 없습니다. 그래서 먼저 날짜·시간 값으로 바꾼 뒤 「시」(예: 9)를 꺼냅니다.
3. 분석한 결과(실패한 이벤트)는 **CSV(씨에스브이, 값을 쉼표(,)로 구분해 적은 텍스트 파일)** 로 저장하면 엑셀 같은 도구로 열어 볼 수 있습니다.

### 📖 6.1 묶고 세기 · 시간 다루기 · 저장하기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽어도 되고, `normalized_events.json` 이 있는 폴더에서 따라 쳐 보아도 됩니다.

**🐼 판다스 문법 상자 — 같은 값끼리 묶기**

**<mark>`groupby("열")`</mark> 는 그 열의 값이 같은 줄끼리 묶습니다**

「소스별로 실패가 몇 개인가」를 알려면 먼저 `source` 값이 같은 행끼리 그룹(group)으로 묶어야 합니다. `groupby` 는 이 묶기만 하고, 개수는 세지 않습니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다 — 실패한 이벤트만 담긴다

grouped = failed.groupby("source")               # source 값이 같은 줄끼리 묶는다 — 아직 개수가 아니라 그룹만 만든 상태
print(grouped)                                   # 묶은 결과를 출력한다 — 개수가 아니라 `DataFrameGroupBy` 라는 이름이 나온다
```

실행 결과:

```
<pandas.core.groupby.generic.DataFrameGroupBy object at 0x1027020d0>
```

- 읽는 법: 이 출력에는 그룹의 개수나 내용이 없습니다. 묶기만 했고 아직 세지 않았기 때문입니다. `0x` 로 시작하는 부분은 실행할 때마다 달라도 괜찮습니다.
- 그룹이 몇 개인지는 `len(grouped)` 로 셉니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다 — 실패한 이벤트만 담긴다

grouped = failed.groupby("source")               # source 값이 같은 줄끼리 묶는다 — 아직 개수가 아니라 그룹만 만든 상태
group_count = len(grouped)                       # 그룹이 몇 개인지 센다
print(group_count)                               # 3 이 나온다 — saas · server · web 세 그룹
```

실행 결과:

```
3
```

- 읽는 법: `3` 은 그룹이 3개라는 뜻입니다. `source` 값이 `saas` · `server` · `web` 세 가지이기 때문입니다.
- 묶기만 해서는 그룹마다 몇 개인지 알 수 없습니다. 개수는 다음 상자의 `.size()` 로 셉니다.

**🐼 판다스 문법 상자 — 그룹마다 행 수 세기**

**<mark>`.size()`</mark> 는 그룹마다 행이 몇 개인지 셉니다**

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다 — 실패한 이벤트만 담긴다
grouped = failed.groupby("source")               # source 값이 같은 줄끼리 묶는다

counts = grouped.size()                          # 그룹마다 행이 몇 개인지 센다 — 그룹 이름이 왼쪽에 나온다
print(counts)                                    # saas 1 · server 9 · web 13 (그룹 이름 순서)
```

실행 결과:

```
source
saas       1
server     9
web       13
dtype: int64
```

- 읽는 법: 왼쪽이 그룹 이름(`source` 값), 오른쪽이 그 그룹의 행 수입니다. 그룹 이름은 가나다 · 알파벳 순서로 나옵니다. 1 + 9 + 13 = 23 이라 실패한 이벤트 전체 개수와 같습니다.
- 개수만 세려면 5교시의 `value_counts()` 로도 같은 결과가 나옵니다. 그래도 `groupby` 를 배우는 것은 내일 그룹마다 평균 같은 다른 계산도 하기 때문입니다. 오늘은 개수(`size`)만 씁니다.

**알아 둘 것 — 묶고 세기를 한 줄로 쓰기**

`failed.groupby("source").size()` 처럼 묶기와 세기를 한 줄로 이어 쓰기도 합니다. 문제 6-1 에서는 줄마다 하나씩 나눠 쓰고, 이 모양은 읽기만 합니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다 — 실패한 이벤트만 담긴다

counts = failed.groupby("source").size()         # 묶고(groupby) 바로 이어서 그룹마다 행 수를 센다(size) — 앞의 두 줄과 같은 일이다
print(counts)                                    # saas 1 · server 9 · web 13 (그룹 이름 순서)
```

실행 결과:

```
source
saas       1
server     9
web       13
dtype: int64
```

- 읽는 법: 두 줄로 나눠 쓴 앞의 결과와 같습니다. `failed.groupby("source")` 가 만든 그룹에 바로 `.size()` 를 붙여서, 중간 이름(`grouped`)을 따로 만들지 않을 뿐입니다.

**🐼 판다스 문법 상자 — 큰 값부터 정렬하기**

**<mark>`.sort_values(ascending=False)`</mark> 는 값이 큰 것부터 다시 정렬합니다**

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다 — 실패한 이벤트만 담긴다
grouped = failed.groupby("source")               # source 값이 같은 줄끼리 묶는다
counts = grouped.size()                          # 그룹마다 행이 몇 개인지 센다 — saas 1 · server 9 · web 13

sorted_counts = counts.sort_values(ascending=False)  # 개수가 큰 그룹부터 다시 정렬한다(ascending=False 는 큰 값부터 정렬)
print(sorted_counts)                             # web 13 · server 9 · saas 1
```

실행 결과:

```
source
web       13
server     9
saas       1
dtype: int64
```

- 읽는 법: 값은 앞의 묶어 세기와 같고 행 순서만 바뀐 것입니다. 그룹 이름 순서(saas → server → web)에서 개수가 큰 순서(web → server → saas)가 되었습니다.
- `ascending=False` 는 큰 값부터 정렬하라는 뜻이고, 이 부분을 빼면 작은 값부터 나옵니다.

**알아 둘 것 — 정렬까지 이어 쓴 모양도 읽을 수 있어야 합니다**

묶기, 세기, 정렬은 실무에서 아래처럼 점으로 이어 한 줄에 쓰기도 합니다. 왼쪽부터 차례로 하나씩 일어난다고 읽으면 됩니다. 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

results = events["result"]                       # result 열만 꺼낸다
is_fail = results == "실패"                      # 행마다 실패면 True, 아니면 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다

sorted_counts = failed.groupby("source").size().sort_values(ascending=False)  # 묶기 → 세기 → 큰 값부터 정렬을 한 줄로 이은 모양
print(sorted_counts)                             # web 13 · server 9 · saas 1
```

실행 결과:

```
source
web       13
server     9
saas       1
dtype: int64
```

**알아 둘 것 — 문자열 시각을 시각 값으로 바꾸기**

`pd.to_datetime` 은 `"2026-11-02 09:01:05"` 같은 문자열을 날짜·시간 값으로 바꿉니다. 날짜·시간 값이어야 「시」나 「분」 같은 부분만 꺼낼 수 있습니다. 문제 6-1 의 `add_hour` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

time_texts = events["time"]                      # time 열만 꺼낸다 — 문자열 시각 57개
times = pd.to_datetime(time_texts)               # 문자열 시각 57개를 시각 값으로 바꾼다
first_times = times.head(3)                      # 처음 3개만 남긴다
print(first_times)                               # 시각 3개와 열 이름, 종류(datetime64)가 나온다
```

실행 결과:

```
0   2026-11-02 02:14:08
1   2026-11-02 09:01:05
2   2026-11-02 09:01:06
Name: time, dtype: datetime64[ns]
```

- 읽는 법: 겉모습은 같지만, 맨 아래 `datetime64` 는 이 열이 날짜·시간 값으로 바뀌었다는 표시입니다.

**알아 둘 것 — 시각 값에서 「시」만 꺼내기**

`.dt.hour` 는 시각 값에서 「시」만 숫자로 꺼냅니다. 문제 6-1 의 `add_hour` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

time_texts = events["time"]                      # time 열만 꺼낸다
times = pd.to_datetime(time_texts)               # 문자열 시각을 시각 값으로 바꾼다

hours = times.dt.hour                            # 시각 값에서 「시」만 숫자로 꺼낸다(02:14 → 2, 09:01 → 9)
first_hours = hours.head(3)                      # 처음 3개만 남긴다
for hour in first_hours:                         # 처음 3개를 하나씩 꺼낸다
    print(hour)                                  # 2, 9, 9 가 한 줄씩 나온다
```

실행 결과:

```
2
9
9
```

- 읽는 법: 첫 이벤트(02:14)는 2, 둘째와 셋째(09:01)는 9입니다.

**알아 둘 것 — 표에 새 열 붙이기**

`표["새 열 이름"] = 값` 은 표 맨 오른쪽에 새 열을 붙입니다. 문제 6-1 의 `add_hour` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 이벤트 파일을 표로 읽는다

time_texts = events["time"]                      # time 열만 꺼낸다
times = pd.to_datetime(time_texts)               # 문자열 시각을 시각 값으로 바꾼다
hours = times.dt.hour                            # 시각 값에서 「시」만 숫자로 꺼낸다

events["hour"] = hours                           # 표 맨 오른쪽에 hour 라는 새 열을 붙인다
shape = events.shape                             # 붙인 뒤 표의 크기를 꺼낸다
print(shape)                                     # (57, 7) — 열이 6개에서 7개가 되었다
```

실행 결과:

```
(57, 7)
```

- 읽는 법: 행은 그대로 57개이고, 열이 6개에서 7개로 늘었습니다.

**알아 둘 것 — 표를 CSV 파일로 저장하기**

`표.to_csv(파일 이름, index=False)` 는 표를 엑셀로도 열 수 있는 CSV 파일(값을 쉼표(,)로 구분해 적은 텍스트 파일)로 저장합니다. 문제 6-1 의 `save_failed` 에 미리 채워져 있어서 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
failed.to_csv("failed_events.csv", index=False)  # 표를 failed_events.csv 파일로 저장한다 — index=False 는 행 번호를 저장하지 않는다는 뜻
```

- 실행하면 같은 폴더에 `failed_events.csv` 파일이 생깁니다. VS Code 로 열면 첫 줄은 열 이름이고, 둘째 줄부터 이벤트가 한 줄씩 있습니다.
- 엑셀로 열었을 때 한글이 깨져 보이면 VS Code 로 열어 확인합니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` · `pick_failed` | (5교시와 같아서 미리 채움) | 이벤트 표 · 실패한 행만 담은 표 |
| `count_by_user` | 실패한 이벤트 표 | 사용자별 실패 횟수(많은 순서) |
| `add_hour` | 이벤트 표 | `hour` 열이 더해진 표 |
| `count_by_hour` | 실패한 이벤트 표 | 시간대별 실패 횟수 |
| `save_failed` | 표와 파일 이름 | 없음(파일로 저장) |

- **직접 쓰는 곳은 두 함수**(번호 1 ~ 5)입니다. 나머지는 미리 채웠습니다. `load_events` 와 `pick_failed` 는 5교시와 같고, `add_hour` 와 `save_failed` 는 아직 배우지 않은 문법이라 읽기만 합니다.
  - `count_by_user`(1 ~ 3번): 사용자별로 묶어 세고 큰 순서로 정렬합니다.
  - `count_by_hour`(4 · 5번): 시간대별로 묶어 셉니다. 묶기와 세기는 1 · 2번과 같고 열 이름만 다릅니다.
  - `add_hour` · `save_failed`(미리 채움): 시각을 바꿔 `hour` 열을 더하고, 실패한 이벤트를 CSV 로 저장합니다. 읽어 보기만 합니다.

### 📖 6.2 묶을 때 비어 있는 값은 빠집니다

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- `groupby("user")` 는 `user` 가 비어 있는 행(`null`)을 그룹에 넣지 않고 **제외합니다.** 웹 서버 이벤트는 `user` 가 없어서 사용자별 개수에 들어가지 않습니다.
- 그래서 사용자별 개수를 모두 더하면 실패한 이벤트 전체 개수보다 작아질 수 있습니다. 숫자를 읽을 때 「빠진 행이 있는가」를 함께 봅니다.
- 오류 메시지는 나오지 않으므로 모르고 지나치기 쉽습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 실패한 이벤트를 사용자별 · 시간대별로 묶어 세고 CSV 로 저장하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 실패가 23개라는 것만 알고, 누구에게 많이 났는지, 언제 많이 났는지는 모릅니다.
- **그래서 만드는 것**: `events_time.py` 입니다.
  - 실패를 사용자별로 묶어 많은 순서로 셉니다.
  - 시각에서 「시」를 꺼내 시간대별로 셉니다.
  - 실패한 이벤트를 CSV 파일로 저장합니다.
- **실행하면**: 단계 1: 사용자별 실패 횟수, 단계 2: 시간대별 실패 횟수, 단계 3: 저장한 행 수가 나오고 `failed_events.csv` 파일이 만들어집니다.
- **현업에서는**: 알림이 나면 근거 이벤트를 파일로 남겨 담당자가 열어 봅니다. 사용자별 · 시간대별 집계는 평소와 비교할 때의 출발점입니다.

**🎯 할 일**

1. `events_time.py` · `day02_6-1_run.py` 두 파일을 만들고, `events_time.py` 의 `count_by_user` · `count_by_hour` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>사용자별 실패 횟수</mark>(단계 1), <mark>시간대별 실패 횟수</mark>(단계 2), <mark>저장한 파일의 행 수</mark>(단계 3)를 읽습니다.

**`events_time.py`**

```python
import pandas as pd                     # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"  # 읽을 정규화 이벤트 파일 이름
FAILED_PATH = "failed_events.csv"       # 실패한 이벤트를 저장할 파일 이름


def load_events(path):                  # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)         # 파일을 읽어 표로 만든다
    return events                       # 표를 리턴한다


def pick_failed(events):                # 표를 받는 함수
    """실패한 이벤트만 골라 새 표로 만든다.
    무엇이 잘못됐는지 조사할 때 성공한 이벤트는 빼고 보는 데 쓴다.
    """
    results = events["result"]          # result 열 하나를 꺼낸다
    is_fail = results == "실패"         # 행마다 실패면 True, 아니면 False
    failed = events[is_fail]            # True 인 행만 남긴다
    return failed                       # 실패한 행만 담은 표를 리턴한다


def count_by_user(failed):              # 실패한 이벤트 표를 받는 함수
    """실패 횟수를 사용자별로 세어 많은 순서로 리턴한다.
    누구에게 실패가 많이 났는지 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. failed 를 "user" 열 기준으로 묶어(groupby) grouped 에 담는다
    # 2. grouped.size() 의 결과를 counts 에 담는다
    # 3. counts 를 큰 값부터 정렬해(sort_values, ascending=False) sorted_counts 에 담는다
    return sorted_counts                # 많은 순서로 정렬한 개수를 리턴한다


def add_hour(events):                   # 표를 받는 함수
    """time 열을 시각으로 바꾸고 「시」만 담은 hour 열을 더한다.
    시간대별로 세기 전에 쓴다.
    """
    times = pd.to_datetime(events["time"])  # 문자열 시각을 시각 값으로 바꾼다
    hours = times.dt.hour               # 시각에서 「시」(0~23)만 꺼낸다
    events["hour"] = hours              # hour 라는 새 열로 표에 더한다
    return events                       # hour 열이 더해진 표를 리턴한다


def count_by_hour(failed):              # 실패한 이벤트 표를 받는 함수
    """실패 횟수를 시간대별로 센다.
    실패가 몇 시에 많이 났는지 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. failed 를 "hour" 열 기준으로 묶어 grouped 에 담는다
    # 5. grouped.size() 의 결과를 counts 에 담는다
    return counts                       # 시간대별 개수를 리턴한다


def save_failed(failed, path):          # 표와 저장할 파일 이름을 받는 함수
    """실패한 이벤트 표를 CSV 파일로 저장한다.
    담당자가 엑셀로 근거를 확인하게 할 때 쓴다.
    """
    failed.to_csv(path, index=False)    # 표를 CSV 파일로 저장한다 — 미리 채운 줄
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 5번은 모두 함수 안이라 앞에 공백 4개입니다.
- 번호 주석이 연달아 붙어 있어도(예: 1 · 2 · 3번), 주석 1번 아래에 코드 한 줄, 주석 2번 아래에 코드 한 줄을 씁니다.
- 채우기 전에 실행하면 `NameError: name 'sorted_counts' is not defined` 오류가 납니다. 3번까지 쓰지 않았기 때문입니다.

**`day02_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 이벤트를 읽어 실패만 골라 묶고 저장한 뒤 세 단계로 출력합니다. 단계 3에서 `pd.read_csv(파일)` 은 저장한 CSV 를 다시 표로 읽고, `len(표)` 는 그 표의 행 수입니다. 저장이 잘 됐는지 행 수로 확인하는 줄이라 읽기만 합니다.

```python
import pandas as pd                            # 저장한 파일을 다시 읽을 수 있게 판다스를 불러온다
from events_time import load_events, add_hour, pick_failed, count_by_user, count_by_hour, save_failed, EVENTS_PATH, FAILED_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)              # 이벤트 파일을 표로 읽는다
events = add_hour(events)                      # 시각을 바꾸고 hour 열을 더한다
failed = pick_failed(events)                   # 실패한 이벤트만 골라낸다

by_user = count_by_user(failed)                # 실패 횟수를 사용자별로 센다
print("--- 단계 1: 사용자별 실패 횟수")        # 단계 1 시작을 알리는 줄
print(by_user)                                 # 많은 순서로 출력한다

by_hour = count_by_hour(failed)                # 실패 횟수를 시간대별로 센다
print("--- 단계 2: 시간대별 실패 횟수")        # 단계 2 시작을 알리는 줄
print(by_hour)                                 # 시간대 순서로 출력한다

save_failed(failed, FAILED_PATH)               # 실패한 이벤트를 CSV 로 저장한다
saved = pd.read_csv(FAILED_PATH)               # 저장한 파일을 다시 읽어 확인한다
saved_count = len(saved)                       # 저장된 행이 몇 개인지 센다
print("--- 단계 3: 저장한 파일", FAILED_PATH)  # 단계 3 시작을 알리는 줄
print("저장된 행", saved_count, "개")          # 저장된 행 수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `events_time.py` · `day02_6-1_run.py` 를 만들어 위 코드를 붙여 넣습니다(터미널에서는 `touch events_time.py day02_6-1_run.py` 후 VS Code 에서 엽니다).
2. **[VS Code]** `events_time.py` 에서 직접 쓰는 곳 다섯 군데를 씁니다. 6.1 의 판다스 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day02_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_6-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 세 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1은 6줄, 단계 2는 7줄, 단계 3은 1줄입니다.
5. **[VS Code]** 새로 생긴 `failed_events.csv` 를 열어 첫 줄이 열 이름(`time,source,user,ip,action,result,hour`)인지 보고, `hour` 가 9 인 행의 `source` 를 봅니다.
6. **[보고서]** `day02_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 실패가 가장 많은 사용자와 횟수, 실패가 가장 많이 난 시간대와 횟수, 저장된 행 수를 적어 주세요.
   - (나) 🔍 시간대별 결과에서 실패가 가장 많이 난 시간대의 개수를 보세요. 이 개수는 5교시 단계 3의 어느 소스 개수와 같은가요? 그 실패가 어느 소스에서 났는지 적고(근거는 숫자가 같다는 것까지 쓰면 됩니다), 이어서 확인할 것도 적어 주세요.
   - (다) 🔍 사용자별 실패 횟수를 모두 더하면 실패한 이벤트 전체보다 적습니다. 몇 개가 모자라고 왜 모자란지 적어 주세요. 그리고 이 차이를 모르고 사용자별 숫자만 보면 어떤 잘못된 판단을 할 수 있을지도 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 같은 값끼리 묶어 개수 세기 | `grouped = failed.groupby("user")` → `counts = grouped.size()` |
| 큰 값부터 정렬 | `sorted_counts = counts.sort_values(ascending=False)` |
| 문자열 시각을 시각 값으로 | `times = pd.to_datetime(events["time"])` |
| 「시」만 꺼내 새 열로 | `hours = times.dt.hour` → `events["hour"] = hours` |
| CSV 로 저장 | `failed.to_csv(path, index=False)` |
| 비어 있는 값 | `groupby` 는 비어 있는 값(`null`)의 행을 빼고 센다 |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다. 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, `pwd` 로 위치를 먼저 확인한 뒤 결과가 `anomaly_detection` 으로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: 팀장이 「오늘 만든 집계 코드와 실패 이벤트 파일을 저장소에 남겨 달라」고 합니다.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `anomaly_detection` 폴더에 오늘 만든 파일이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `anomaly_detection` 폴더에서 확인합니다. `day02_pm_report.md` 의 5 · 6교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지도 봅니다.
   ```bash
   ls
   ```
   - 명령 풀이: `ls` 폴더 안의 파일 이름 보기
   - `normalized_events.json` · `events_basic.py` · `events_time.py` · `day02_5-1_run.py` · `day02_6-1_run.py` · `failed_events.csv` 와 이 안내 · 보고서 두 파일이 보여야 합니다.
1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 결과가 `…/security-agent-toolkit` 으로 끝나야 합니다.
   ```bash
   cd ..
   pwd
   ```
   - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 위치 확인
   - 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. 빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 말고, 아래 안내대로 `.gitignore` 를 고친 뒤 `git status` 를 다시 봅니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 올릴 파일의 상태를 봄
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 도 같은 방법으로 합니다.
   - `anomaly_detection/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - 앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다. 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add anomaly detection day 2 pandas basics"
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

## 오늘 마무리

| 확인 | 문제 |
|---|---|
| 이벤트 파일을 표로 읽고, 실패한 이벤트를 골라 소스별로 셌다 | 오후 5-1 |
| 실패를 사용자별 · 시간대별로 묶어 세고 CSV 로 저장했다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

다음 수업은 11/4(수)입니다. 오늘 센 숫자를 **평소 기준(baseline)** 과 비교해서, 평소보다 많은 로그인 실패와 요청 급증을 찾는 탐지 규칙을 만듭니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_5-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_5-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `load_events` 안

```python
    events = pd.read_json(path)  # 파일을 읽어 표로 만든다
```

② `describe_events` 안

```python
    times = events["time"]  # time 열 하나를 꺼낸다
```

③ `count_values` 안

```python
    values = table[column]          # column 열 하나를 꺼낸다
    counts = values.value_counts()  # 값별 개수를 센다
```

**결과**

- (가) 출력은 다음과 같고, 표는 <mark>**57행 6열**</mark>, 성공 <mark>**34**</mark> · 실패 <mark>**23**</mark>, 실패한 이벤트의 소스별 개수는 web <mark>**13**</mark> · server <mark>**9**</mark> · saas <mark>**1**</mark> 입니다.

```
--- 단계 1: 표 크기(행 수, 열 수)와 처음 3개 시각
(57, 6)
2026-11-02 02:14:08
2026-11-02 09:01:05
2026-11-02 09:01:06
--- 단계 2: 성공 · 실패별 개수
result
성공    34
실패    23
Name: count, dtype: int64
--- 단계 3: 실패한 이벤트 23 개의 소스별 개수
source
web       13
server     9
saas       1
Name: count, dtype: int64
--- 단계 4: 전체 이벤트의 소스별 개수
source
web       28
server    15
saas      14
Name: count, dtype: int64
```

- 읽는 법: 첫 줄 `source` 는 센 열의 이름이고, 아래 줄은 왼쪽이 값, 오른쪽이 나온 횟수입니다. 28 + 15 + 14 = 57 이라 이벤트 전체 개수와 같습니다.

- (나) 개수만 보면 web 이 13개로 가장 많지만, 그것만으로 web 이 가장 문제가 큰 소스라고 말할 수는 없습니다.
  - 소스마다 전체 이벤트 수가 다릅니다(web 28 · server 15 · saas 14). 전체 중 실패의 비율로 보면 web 13/28 = 약 46%, server 9/15 = 60%, saas 1/14 = 약 7% 입니다.
  - 비율로는 server 가 가장 높습니다. 개수는 전체 규모의 영향을 받으므로, 소스끼리 비교할 때는 전체 대비 비율도 함께 봅니다.
- (다) 예상은 이렇습니다.
  - 사용자 이름으로 세려 해도 web 실패 13개는 `user` 가 비어 있어서 들어갈 사용자가 없습니다. web 실패 13개가 사용자별로 세어지지 않는다는 것을 6교시에서 확인합니다.
  - 대신 `ip` 열을 봅니다. 같은 주소에서 실패가 여러 번 난 것을 찾으면 누구인지는 몰라도 같은 대상이 반복했는지 알 수 있습니다.

**왜**

- <mark>이벤트를 표로 읽으면 「걸러 내기 → 세기」가 몇 줄로 끝나고, 이벤트가 57개일 때나 5만 개일 때나 같은 코드를 씁니다.</mark>
  - 조건 비교(`==`)는 줄마다 `True` 또는 `False` 를 만들고, `표[조건]` 은 `True` 인 행만 남깁니다.

**자주 틀리는 곳**

- 열 이름을 틀리면 `KeyError` 오류가 납니다. `events["time"]` 을 `events["times"]` 처럼 쓰면 표에 없는 열 이름이라서 `KeyError` 가 납니다.
  - 실행하면 다음 오류가 납니다(<mark>`KeyError: 'times'`</mark> 처럼 틀린 열 이름이 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day02_5-1_run.py", line 4, in <module>
    shape, first_times = describe_events(events)  # 표 크기와 time 열의 처음 3개를 구한다
  File "…/anomaly_detection/events_basic.py", line 23, in describe_events
    times = events["times"]  # time 열 하나를 꺼낸다
KeyError: 'times'
```

  - 줄 번호는 사람마다 다릅니다. 열 이름은 파일에 적힌 키와 똑같이 써야 합니다. 판다스 안쪽 파일의 줄은 길어서 생략했습니다.
- `count_values` 에서 `values.value_counts()` 의 괄호를 빼면 오류는 나지 않지만 개수가 아니라 `<bound method …>` 가 나옵니다. `value_counts` 는 뒤에 괄호를 붙여 호출하는 메서드입니다.

**관제에서는**

- 관제 도구의 「실패 이벤트 수 · 소스별 분포」 화면은 이 계산을 계속 다시 합니다. 분포를 보고 어느 소스부터 조사할지 정합니다.
  - 숫자는 「살펴볼 곳」을 알려 줄 뿐이고, 개수가 많다고 곧 공격이라는 뜻은 아닙니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_6-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `count_by_user` 안

```python
    grouped = failed.groupby("user")  # user 가 같은 행끼리 묶는다
    counts = grouped.size()           # 그룹마다 행이 몇 개인지 센다
    sorted_counts = counts.sort_values(ascending=False)  # 큰 값부터 순서대로 정렬한다
```

② `count_by_hour` 안

```python
    grouped = failed.groupby("hour")  # hour 가 같은 행끼리 묶는다
    counts = grouped.size()           # 그룹마다 행이 몇 개인지 센다
```

**결과**

- (가) 출력은 다음과 같고, 실패가 가장 많은 사용자는 <mark>**dami(4번)**</mark>, 가장 많이 난 시간대는 <mark>**9시(13번)**</mark>, 저장된 행은 <mark>**23개**</mark>입니다.

```
--- 단계 1: 사용자별 실패 횟수
user
dami       4
gaeun      3
seoyeon    2
jiwoo      1
dtype: int64
--- 단계 2: 시간대별 실패 횟수
hour
2      1
9     13
10     3
11     5
18     1
dtype: int64
--- 단계 3: 저장한 파일 failed_events.csv
저장된 행 23 개
```

- (나) 9시의 13개는 5교시 단계 3의 web 실패 13개와 같은 숫자입니다. 웹 서버에서 난 실패가 모두 9시에 났다는 단서입니다.
  - 숫자가 같다는 것만으로는 확정할 수 없습니다. 확정하려면 `failed_events.csv` 를 열어 `hour` 가 9인 행의 `source` 를 봅니다(실제로 13개 모두 `web` 입니다).
  - 웹 서버 로그에는 사용자가 없으므로, 먼저 확인할 것은 같은 시간대의 `ip` 입니다. 같은 주소가 로그인 실패를 반복했는지, 없는 주소를 차례로 요청했는지 봅니다.
  - 한 시간대에 실패가 많이 났을 때는 그 소스, 같은 주소 · 같은 사용자의 반복, 그 직후 성공이 있는지를 이어서 봅니다.
- (다) 사용자별 합계는 4 + 3 + 2 + 1 = 10이고 실패한 이벤트는 23개라서 **13개**가 빠졌습니다.
  - 빠진 13개는 `user` 가 비어 있는 웹 서버 이벤트입니다. `groupby("user")` 가 비어 있는 값의 행을 그룹에 넣지 않았기 때문입니다.
  - 모르고 사용자별 숫자만 보면 「실패가 10개뿐」이라고 잘못 판단하거나, 가장 많은 실패(웹 서버 13개)를 아예 놓칩니다.

**왜**

- <mark>묶어서 세면 전체 합계 숫자에서는 보이지 않던 차이가 드러납니다.</mark> 사용자별 · 시간대별 집계는 평소 기준과 비교할 때의 출발점입니다.
  - 시각은 문자열이면 「시」를 꺼낼 수 없으므로 시각 값으로 바꾼 뒤에 `.dt.hour` 를 씁니다.

**자주 틀리는 곳**

- 열 이름을 틀리면 `KeyError` 오류가 납니다. `groupby("user")` 를 `groupby("users")` 처럼 쓰면 표에 없는 열 이름이라서 `KeyError` 가 납니다.
  - 실행하면 다음 오류가 납니다(<mark>`KeyError: 'users'`</mark> 처럼 틀린 열 이름이 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day02_6-1_run.py", line 8, in <module>
    by_user = count_by_user(failed)  # 실패 횟수를 사용자별로 센다
  File "…/anomaly_detection/events_time.py", line 31, in count_by_user
    grouped = failed.groupby("users")  # user 가 같은 행끼리 묶는다
KeyError: 'users'
```

  - 줄 번호는 사람마다 다릅니다. 판다스 안쪽 파일의 줄은 길어서 생략했습니다.
- `sort_values` 에서 `ascending=False` 를 빼면 오류는 나지 않지만 작은 값부터 나옵니다. 단계 1 의 첫 줄이 dami 가 아니라 jiwoo 가 됩니다.

**관제에서는**

- 집계 결과는 알림을 만들 때 근거가 되는 숫자입니다. 근거가 된 이벤트를 파일로 남기면 담당자가 알림이 왜 났는지 확인할 수 있습니다.
  - 집계에서 빠진 값(`null`)이 있는지 함께 확인하는 것이 습관입니다.

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
git commit -m "Add anomaly detection day 2 pandas basics"
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

**관제에서는**

- 분석 코드와 샘플 데이터는 같은 저장소에 함께 남겨, 어느 코드로 어떤 데이터를 분석했는지 이력으로 추적합니다.
