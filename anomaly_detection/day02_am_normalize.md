# 11/3(화) 오전 · 4과목 이상탐지 ② — 서로 다른 로그 3종류를 같은 모양으로 맞추기(정규화) — 실습

어제는 웹 서버 접속 로그 한 줄을 읽고 이상 징후를 가르는 법을 배웠습니다. 오늘 오전에는 **서로 다른 모양의 로그 3종류를 같은 키로 맞추는 정규화**를 합니다. SIEM(심, 로그를 모아 분석하는 보안 도구)의 네 단계(수집 → 정규화 → 탐지 → 알림 · 조사) 중 두 번째 단계입니다.

- **2교시**: 웹 서버 로그 한 줄을 공통 이벤트(키는 2.1에서 설명)로 바꿉니다. 시각 모양을 맞추는 법을 처음 배웁니다.
- **3교시**: 판정 서버 로그(JSON)와 SaaS 로그(CSV)를 같은 공통 이벤트로 바꿉니다.
- **4교시**: 세 로그의 이벤트를 하나로 합쳐 시간순으로 정렬하고 `normalized_events.json` 파일로 저장합니다. 이 파일을 오후에 판다스로 읽습니다.

오늘은 오전 2 · 3 · 4교시이고, 깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 교시마다 문제는 하나입니다.

- 오늘 오전에 쓰는 도구는 **파이썬 · VS Code · 터미널**입니다. 판다스는 오후에 처음 씁니다.
- 새로 나오는 문법은 읽을거리의 「문법 상자」에서 코드와 실행 결과, 값이 바뀌는 모양과 함께 설명합니다.
- 📎 **오늘 불러 쓰는 이전 파일**

| 파일 | 어디서 | 오늘 쓰는 곳 | 없으면 |
|---|---|---|---|
| `log_parse.py` | 어제 5교시에 만든 파일 | 2교시 `normalize_web.py` 가 안의 함수 네 개를 불러 씁니다 | 문서 맨 아래 「앞 날 파일 완성본」으로 만듭니다 |
| `access_sample.log` | 어제 시작하기에서 만든 샘플 웹 서버 로그(30줄) | 2교시와 4교시에서 읽습니다 | 같은 곳의 완성본으로 만듭니다 |

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치와 어제 파일을 확인합니다(맥북은 `python3`). `pwd` 가 `…/anomaly_detection` 으로 끝나고, `ls` 결과에 `log_parse.py` 와 `access_sample.log` 가 보여야 합니다. 없으면 맨 아래 「앞 날 파일 완성본」으로 먼저 만듭니다. `cd` 가 「No such file or directory」 오류를 내면 `mkdir anomaly_detection` 으로 폴더부터 만들고 들어갑니다.
   ```bash
   cd anomaly_detection
   pwd
   ls
   ```
3. **오늘 받은 파일 두 개**(`day02_am_normalize.md`, `day02_am_report.md`)를 `다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-03(화))` 의 `이름` 을 내 이름으로 바꿉니다. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[VS Code 또는 터미널]** `anomaly_detection` 폴더에 `server_log.jsonl` 과 `saas_events.csv` 파일을 만들어 아래 내용을 그대로 붙여 넣습니다(터미널에서는 `touch 파일이름` 후 VS Code 에서 엽니다).

**`server_log.jsonl`** — 판정 서버가 남긴 로그 샘플입니다. 3과목에서 만든 서버의 로그와 같은 모양이고, 한 줄이 요청 1개인 JSON 입니다(15줄).

```
{"time": "2026-11-02T09:40", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T09:52", "user": "junho", "permission": "SALES:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T10:05", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-11-02T10:09", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-11-02T10:14", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-11-02T11:02", "user": "dami", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-11-02T11:03", "user": "dami", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-11-02T11:05", "user": "dami", "permission": "SALES:CHANGE", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-11-02T11:08", "user": "dami", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-11-02T11:40", "user": "seoyeon", "permission": "SETTLE:QUERY", "network": "office", "allowed": false, "reason": "권한 없음"}
{"time": "2026-11-02T13:15", "user": "junho", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T14:30", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T15:05", "user": "junho", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T16:10", "user": "gaeun", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-02T18:20", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "vpn", "allowed": false, "reason": "업무 시간 밖"}
```

**`saas_events.csv`** — SaaS 서비스가 내보낸 로그 샘플입니다. 첫 줄은 열 이름이고, 둘째 줄부터 한 줄이 이벤트 1개이며 값은 쉼표로 나뉩니다(첫 줄이 열 이름이라 이벤트는 14개이고, 파일은 15줄입니다). 시각은 내보낼 때 한국 시간으로 설정되어 있습니다.

```
time,account,event,ip_address,outcome
2026-11-02 02:14:08,jiwoo@a-corp.example,login,203.0.113.80,failure
2026-11-02 09:05:30,seoyeon@a-corp.example,login,198.51.100.9,success
2026-11-02 09:30:12,junho@a-corp.example,login,192.0.2.41,success
2026-11-02 10:12:55,gaeun@a-corp.example,login,198.51.100.77,success
2026-11-02 11:25:40,seoyeon@a-corp.example,file.download,198.51.100.9,success
2026-11-02 13:50:21,junho@a-corp.example,file.upload,192.0.2.41,success
2026-11-02 15:20:03,junho@a-corp.example,login,192.0.2.41,success
2026-11-02 16:02:18,jiwoo@a-corp.example,login,198.51.100.52,success
2026-11-02 17:38:10,seoyeon@a-corp.example,login,203.0.113.80,success
2026-11-02 17:40:02,seoyeon@a-corp.example,file.download,203.0.113.80,success
2026-11-02 17:40:31,seoyeon@a-corp.example,file.download,203.0.113.80,success
2026-11-02 17:41:05,seoyeon@a-corp.example,file.download,203.0.113.80,success
2026-11-02 17:41:48,seoyeon@a-corp.example,file.download,203.0.113.80,success
2026-11-02 17:42:20,seoyeon@a-corp.example,file.download,203.0.113.80,success
```

6. **[터미널]** 세 파일의 줄 수를 확인합니다.
   ```bash
   python -c "print(len(open('access_sample.log', encoding='utf-8').read().splitlines()))"
   python -c "print(len(open('server_log.jsonl', encoding='utf-8').read().splitlines()))"
   python -c "print(len(open('saas_events.csv', encoding='utf-8').read().splitlines()))"
   ```
   - 순서대로 `30` · `15` · `15` 가 나와야 합니다. 다르면 줄이 빠졌거나 빈 줄이 끼어든 것이니 다시 붙여 넣습니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다.
- `No module named 'log_parse'`: 어제 `log_parse.py` 가 이 폴더에 없는 것입니다. 맨 아래 「앞 날 파일 완성본」으로 만듭니다.
- `IndentationError` · `NameError`: 직접 쓴 줄의 들여쓰기가 틀렸거나 빠뜨린 줄이 있습니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 그 질문의 `답:` 에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다(맥북은 `python3`).

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 웹 서버 로그를 공통 이벤트로 바꾸기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다(웹 서버 · 판정 서버 · SaaS 서비스, 세 군데의 로그 이야기입니다):
> 「로그가 세 군데에서 쌓이는데 적는 방식이 다 다릅니다.
>
> - 시각
>   - 웹 서버: `02/Nov/2026:09:12:03 +0900`
>   - 판정 서버: `2026-11-02T09:40`
>   - SaaS: `2026-11-02 02:14:08`
> - 성공 · 실패
>   - 웹 서버: `200`
>   - 판정 서버: `true`
>   - SaaS: `success`
>
> 이대로는 같은 계정이 여러 곳에서 한 일을 시간 순서로 볼 수 없습니다. 먼저 웹 서버 로그 한 줄을 언제 · 누가 · 무엇을 · 결과를 같은 키에 담은 이벤트로 바꿔 주세요(키 이름은 아래 2.1 에서 설명합니다). 시각은 `2026-11-02 09:12:03` 모양으로 맞추고, 원래 줄은 그대로 남겨 주세요.」
> - **왜 중요한가**: <mark>모양이 다른 로그는 시간순으로 놓을 수도, 같은 기준으로 셀 수도 없습니다.</mark> 같은 키로 맞추면 탐지 규칙을 로그 종류마다 따로 만들지 않고 한 번만 만들면 됩니다. 원래 줄을 남겨 두면 변환이 틀렸을 때 원본과 대조할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. SIEM(심)은 여러 곳의 로그를 한곳에 모아 같은 기준으로 찾습니다. 모양이 다르면 같은 기준을 적용할 수 없습니다.
2. 그래서 로그를 모은 다음 **같은 키 · 같은 모양으로 맞추는 일**이 필요합니다. 이것을 **정규화(normalization, 노멀라이제이션)** 라고 합니다.
3. 오늘 오전에는 로그 3종류를 같은 키로 맞춘 **공통 이벤트**로 바꿉니다. 키는 아래 2.1 에서 설명합니다.

### 📖 2.1 세 로그의 모양과 공통 이벤트

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

세 로그는 모두 **언제 · 누가 · 어디서 · 무엇을 · 성공했나**를 적고 있지만, 적는 방식이 다릅니다.

- **웹 서버 로그**(`access_sample.log`): 웹 서비스를 돌리는 웹 서버(nginx)가 페이지를 열거나 로그인할 때마다 남깁니다.
- **판정 서버 로그**(`server_log.jsonl`): 3과목에서 만든 권한 판정 서버가 「이 권한을 써도 되나?」라는 물음을 받을 때마다 남깁니다.
- **SaaS 로그**(`saas_events.csv`): 회사가 빌려 쓰는 SaaS(인터넷으로 쓰는 소프트웨어, 예: 파일 보관 서비스)에서 로그인하거나 파일을 올리고 내려받을 때마다 남깁니다.

**① 실제 한 줄** — 세 줄이 얼마나 다르게 생겼는지만 봅니다.

| 로그 | 샘플의 실제 한 줄 |
|---|---|
| 웹 서버 | `203.0.113.50 - - [02/Nov/2026:09:12:03 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"` |
| 판정 서버 | `{"time": "2026-11-02T09:40", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}` |
| SaaS | `2026-11-02 02:14:08,jiwoo@a-corp.example,login,203.0.113.80,failure` |

**② 오늘 맞출 차이** — 형광펜으로 표시한 칸은 값이 없거나 메일 주소로 적힌 곳이고, 시각과 성공 · 실패 행은 로그마다 모양이 달라서 고칩니다. 마지막 열이 공통 이벤트에서의 모양입니다.

| 정보 | 웹 서버 | 판정 서버 | SaaS | 공통 이벤트에서는 |
|---|---|---|---|---|
| 시각 | `02/Nov/2026:09:12:03 +0900` | `2026-11-02T09:40` | `2026-11-02 02:14:08` | 모두 `2026-11-02 09:12:03` 모양 |
| 사용자 | <mark>없음</mark> | `seoyeon` | <mark>메일 주소</mark> `jiwoo@a-corp.example` | 이름만. 원래 없으면 `None` |
| 접속 주소 | 있음 | <mark>없음</mark> | 있음 | 원래 없으면 `None` |
| 성공 · 실패 | 상태 코드(`200` · `401` …) | `true` 또는 `false` | `success` 또는 `failure` | 모두 `성공` 또는 `실패` |

- 접속 주소(`ip`)는 사람이 아니라 **접속한 곳**의 주소입니다. 한 사무실의 여러 사람이 같은 주소로 보일 수 있고, 한 사람이 집과 회사에서 다른 주소로 접속할 수도 있습니다.
- 판정 서버 로그에는 주소 대신 접속 위치(`office` · `vpn` · `external`)만 있습니다. 이 수업의 `203.0.113.50` · `198.51.100.x` · `192.0.2.x` 는 문서에서 예시로 쓰라고 정해 둔 주소 범위라서 실제 장비를 가리키지 않습니다.

**③ 공통 이벤트의 키** — 로그 한 줄이 답하는 질문은 세 로그가 같습니다. **언제? 어느 로그에서? 누가? 어디서? 무엇을? 성공했나?** 이 여섯 질문의 답을 같은 키에 담고, 원래 줄을 보관하는 키 하나를 더한 것이 **공통 이벤트(키 7개)** 입니다. 이벤트는 「일어난 일 1개」입니다.

| 키 | 답하는 질문 | 값의 모양 |
|---|---|---|
| `time` | 언제? | `2026-11-02 09:12:03` 문자열(한국 시간) |
| `source` | 어느 로그에서? | `web` · `server` · `saas` |
| `user` | 누가? | 사용자 이름. 원래 없으면 `None` |
| `ip` | 어디서? | 주소 문자열. 원래 없으면 `None` |
| `action` | 무엇을? | `POST /login` · `SALES:CHANGE` · `file.download` |
| `result` | 성공했나? | `성공` 또는 `실패` |
| `raw` | (질문이 아니라 보관용) | 원래 줄(또는 원래 행) 그대로 |

**④ 바뀐 결과** — ①의 서로 다르던 세 줄이 같은 일곱 키가 됩니다. 이 표는 키가 세로입니다.

| 키 | 웹 서버 한 줄 | 판정 서버 한 줄 | SaaS 한 줄 |
|---|---|---|---|
| `time` | `2026-11-02 09:12:03` | `2026-11-02 09:40:00` | `2026-11-02 02:14:08` |
| `source` | `web` | `server` | `saas` |
| `user` | `None` | `seoyeon` | `jiwoo` |
| `ip` | `203.0.113.50` | `None` | `203.0.113.80` |
| `action` | `POST /login` | `SALES:QUERY` | `login` |
| `result` | `실패` | `성공` | `실패` |
| `raw` | ①의 원래 줄 | ①의 원래 줄 | ①의 원래 행(딕셔너리) |

- 원래 로그에 없는 값은 임의로 만들어 넣지 않고 `None` 으로 둡니다. 없는 값을 지어내면 분석 결과가 틀려집니다.
- `raw` 는 바꾸지 않은 원래 로그입니다. 정규화 과정에서 사라지는 정보를 나중에 찾아볼 수 있게 남깁니다.

### 📖 2.2 시각 문자열 바꾸기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 문법 상자의 코드는 눈으로 읽어도 되고, 따라 쳐 보아도 됩니다.

**🐍 문법 상자 — 시각 값을 원하는 모양의 문자열로**

**<mark>`.strftime(형식)`</mark> 은 시각 값을 원하는 모양의 문자열로 만듭니다. 형식에 적은 모양대로 시각이 문자열이 됩니다**

로그마다 시각 모양이 달라서, 먼저 시각 값으로 바꾼 뒤 공통 모양의 문자열로 다시 만듭니다. 문자열을 시각 값으로 바꾸는 `strptime` 은 3과목에서 쓴 방법 그대로라서 여기서는 설명하지 않습니다.

```python
from datetime import datetime                    # 날짜와 시각을 다루는 도구를 불러온다

time_text = "02/Nov/2026:09:12:03 +0900"         # nginx 시각 문자열
parsed = datetime.strptime(time_text, "%d/%b/%Y:%H:%M:%S %z")  # 문자열을 시각 값으로 바꾼다(모양을 형식으로 알려 준다)
print(parsed)                                    # 시각 값을 출력한다

time_out = parsed.strftime("%Y-%m-%d %H:%M:%S")  # 시각 값을 공통 모양의 문자열로 바꾼다
print(time_out)                                  # 문자열을 출력한다
```

실행 결과:

```
2026-11-02 09:12:03+09:00
2026-11-02 09:12:03
```

- 형식 코드는 `%Y`(년) · `%m`(월) 처럼 `%` 로 시작하는 기호로, 시각 문자열의 어느 부분이 일 · 달 · 연도인지 알려 줍니다. `%d` 일 · `%b` 영어 달 이름(Nov) · `%Y` 연도 4자리 · `%H` `%M` `%S` 시 · 분 · 초 · `%z` 시간대(+0900).

nginx 시각 문자열을 부분마다 형식 코드와 하나씩 맞춰 봅니다.

| 문자열 부분 | 형식 코드 | 뜻 |
|---|---|---|
| `02` | `%d` | 일 |
| `Nov` | `%b` | 영어 달 이름 |
| `2026` | `%Y` | 연도 4자리 |
| `09` | `%H` | 시 |
| `12` | `%M` | 분 |
| `03` | `%S` | 초 |
| `+0900` | `%z` | 시간대 |

- 문자열 `02/Nov/2026:09:12:03 +0900` 에서 부분 사이의 `/` · `:` · 공백은 형식에도 똑같이 적습니다. 그래서 형식은 `%d/%b/%Y:%H:%M:%S %z` 입니다.
- `.strftime(형식)` 은 반대로 시각 값을 같은 형식 코드로 문자열로 만듭니다. 위에서는 `2026-11-02 09:12:03` 모양입니다.
- 오늘 새로 나오는 것은 형식 코드 `%b` · `%z` 와, 시각 값을 문자열로 만드는 `strftime` 입니다.

**🐍 문법 상자 — 시간대 정보 떼기**

**시각 값에 붙은 시간대(`+0900`)는 <mark>`.replace(tzinfo=None)`</mark> 으로 떼어 낼 수 있고, 떼면 한국 시각만 남은 시각 값이 됩니다**

```python
from datetime import datetime             # 날짜와 시각을 다루는 도구를 불러온다

time_text = "02/Nov/2026:09:12:03 +0900"  # nginx 시각 문자열
parsed = datetime.strptime(time_text, "%d/%b/%Y:%H:%M:%S %z")  # 문자열을 시각 값으로 바꾼다
print(parsed.tzinfo)                      # 시간대 정보를 출력한다

local_time = parsed.replace(tzinfo=None)  # 시간대 정보를 떼고 한국 시각만 남긴다
print(local_time)                         # 시간대 없는 시각을 출력한다
```

실행 결과:

```
UTC+09:00
2026-11-02 09:12:03
```

- 시각 값이 `+0900`(한국 시간대)을 갖고 있으면 시간대 정보가 없는 시각 값과 직접 비교할 때 오류가 납니다.
- 세 로그의 시각은 모두 한국 시간이므로, 오늘은 시간대 정보를 떼고 한국 시각만 남겨 세 로그의 시각 값을 같은 종류로 맞춥니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `read_time_text` | 요청 앞 조각 | 대괄호 안의 시각 문자열(미리 채움) |
| `convert_time` | nginx 시각 문자열 | 공통 모양 시각 문자열 |
| `convert_result` | 상태 코드(정수) | `"성공"` 또는 `"실패"` |
| `normalize_web` | 로그 한 줄 | 공통 이벤트 딕셔너리. 깨진 줄이면 `None`(미리 채움) |

- **직접 쓰는 곳은 두 함수**(번호 1 ~ 6)입니다.
  - `convert_time`(1 ~ 3번): 문자열을 시각 값으로 바꾸고, 시간대를 떼고, 공통 모양 문자열로 만듭니다.
  - `convert_result`(4 ~ 6번): 상태 코드 400 이상이면 `"실패"`, 아니면 `"성공"` 입니다.
- **미리 채운 것**: 어제 함수를 불러 조각을 꺼내 공통 이벤트로 묶는 `normalize_web` 과 `read_time_text` 입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 웹 서버 로그 한 줄을 공통 이벤트로 바꾸기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 웹 서버 로그의 시각(`02/Nov/2026:09:12:03 +0900`)은 다른 로그와 나란히 놓기 어렵고, 성공 · 실패는 상태 코드라서 따로 판단해야 합니다.
- **그래서 만드는 것**: `normalize_web.py` 입니다.
  - 시각을 `2026-11-02 09:12:03` 모양으로 바꿉니다.
  - 상태 코드를 `성공` · `실패` 로 바꿉니다.
  - 원래 줄은 `raw` 에 남깁니다.
- **실행하면**: 단계 1: 이벤트 수와 첫 이벤트, 단계 2: 처음 나오는 실패 이벤트, 단계 3: 성공 · 실패별 개수가 나옵니다.
- **현업에서는**: 로그를 모으는 도구에는 로그 종류마다 이 변환을 하는 부분(파서)이 있습니다. 변환이 틀리면 그 로그 전체가 잘못 분석되므로 `raw` 와 대조합니다.

**🎯 할 일**

1. `normalize_web.py` · `day02_2-1_run.py` 두 파일을 만들고, `normalize_web.py` 의 `convert_time` · `convert_result` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>정규화한 이벤트 수와 읽기 실패한 줄</mark>(단계 1), <mark>처음 나오는 실패 이벤트</mark>(단계 2), <mark>성공 · 실패별 개수</mark>(단계 3)를 읽습니다.

**`normalize_web.py`**

```python
from datetime import datetime                  # 날짜와 시각을 다루는 도구를 불러온다
from log_parse import split_request, read_request, read_status, read_client  # 어제 만든 로그 읽기 함수를 불러온다

NGINX_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"     # nginx 시각의 모양(예: 02/Nov/2026:09:12:03 +0900)
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"       # 공통 시각의 모양(예: 2026-11-02 09:12:03)


def read_time_text(prefix):                    # 요청 앞 조각을 받는 함수
    """요청 앞 조각에서 대괄호 안의 시각 문자열을 꺼낸다.
    웹 서버 로그의 시각을 공통 모양으로 바꾸기 전에 쓴다.
    """
    parts = prefix.split()                     # 공백 기준으로 나눈다
    bracket_text = parts[3] + " " + parts[4]   # '[02/Nov/2026:09:12:03' 과 '+0900]' 를 이어 붙인다
    time_text = bracket_text.strip("[]")       # 양쪽 끝의 대괄호를 지운다
    return time_text                           # 대괄호 없는 시각 문자열을 리턴한다


def convert_time(time_text):                   # nginx 시각 문자열을 받는 함수
    """nginx 시각을 공통 모양의 문자열로 바꾼다.
    예: 02/Nov/2026:09:12:03 +0900 → 2026-11-02 09:12:03.
    웹 서버 로그를 공통 이벤트로 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. datetime.strptime(time_text, NGINX_TIME_FORMAT) 의 결과를 parsed 에 담는다
    # 2. parsed.replace(tzinfo=None) 의 결과를 local_time 에 담는다 (+0900 정보를 떼고 한국 시각만 남긴다)
    # 3. local_time.strftime(COMMON_TIME_FORMAT) 의 결과를 time_out 에 담는다
    return time_out                            # 공통 모양의 시각 문자열을 리턴한다


def convert_result(status):                    # 상태 코드(정수)를 받는 함수
    """상태 코드가 400 이상이면 「실패」, 아니면 「성공」을 리턴한다.
    웹 서버 로그의 결과를 공통 이벤트의 result 로 바꿀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. status 가 400 이상이면 (if)
    # 5.   "실패" 를 리턴한다
    # 6. 그 밖에는 "성공" 을 리턴한다


def normalize_web(line):                       # 로그 한 줄을 받는 함수
    """웹 서버 로그 한 줄을 공통 이벤트 딕셔너리로 바꾸고, 깨진 줄이면 None 을 리턴한다.
    웹 서버 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    if line.count('"') < 2:                    # 큰따옴표가 두 개보다 적은 깨진 줄이면
        return None                            # 읽지 않고 None 을 리턴한다
    prefix, request_text, suffix = split_request(line)  # 세 조각으로 나눈다
    method, path = read_request(request_text)  # 요청 조각에서 방법과 경로를 꺼낸다
    status = read_status(suffix)               # 뒤 조각에서 상태 코드를 꺼낸다
    client_ip = read_client(prefix)            # 앞 조각에서 접속자 주소를 꺼낸다
    time_text = read_time_text(prefix)         # 앞 조각에서 시각 문자열을 꺼낸다
    time_out = convert_time(time_text)         # 공통 모양의 시각으로 바꾼다
    result = convert_result(status)            # 상태 코드를 성공 · 실패로 바꾼다
    action = method + " " + path               # 방법과 경로를 하나의 행동으로 합친다
    raw_text = line.strip()                    # 원래 줄(양끝 공백과 줄바꿈 뺀 것)을 보관한다
    event = {                                  # 공통 이벤트의 키로 묶는다
        "time": time_out,                      # 일어난 시각
        "source": "web",                       # 어느 로그에서 왔는지
        "user": None,                          # 웹 서버 로그에는 사용자가 없다
        "ip": client_ip,                       # 접속자 주소
        "action": action,                      # 무엇을 했는지
        "result": result,                      # 성공인지 실패인지
        "raw": raw_text,                       # 원래 로그 줄
    }
    return event                               # 공통 이벤트를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개이고, 5번의 `return` 은 `if` 안쪽이라 공백 8개입니다.
- 번호 주석이 연달아 붙어 있어도(예: 1 · 2 · 3번), 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `NameError: name 'time_out' is not defined` 오류가 납니다. 1 ~ 3번을 아직 안 썼기 때문입니다.
- `convert_result` 는 6번까지 쓰면 끝나는 함수라서 아래에 미리 채운 `return` 이 없습니다. 5번과 6번의 `return` 을 직접 씁니다.

**`day02_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 샘플 로그를 한 줄씩 공통 이벤트로 바꿔 세 단계로 출력합니다. `len(리스트)` 는 리스트의 개수입니다.

```python
from normalize_web import normalize_web         # 방금 만든 웹 서버 로그 정규화 함수를 불러온다

events = []                                     # 정규화한 이벤트를 모을 리스트
fail_count = 0                                  # 읽기 실패한 줄 수를 0 으로 시작한다
with open("access_sample.log", encoding="utf-8") as log_file:  # 샘플 로그 파일을 연다
    for line in log_file:                       # 파일에서 한 줄씩 꺼낸다
        event = normalize_web(line)             # 한 줄을 공통 이벤트로 바꾼다
        if event is None:                       # 깨진 줄이라 읽지 못했으면
            fail_count = fail_count + 1         # 읽기 실패한 줄 수를 1 늘린다
        else:                                   # 바꿨으면
            events.append(event)                # 이벤트 리스트에 추가한다

event_count = len(events)                       # 정규화한 이벤트 수를 센다
print("--- 단계 1: 정규화한 이벤트", event_count, "개 · 읽기 실패", fail_count, "줄")  # 단계 1 시작을 알리는 줄
first_event = events[0]                         # 첫 이벤트를 꺼낸다
print(first_event)                              # 첫 이벤트를 출력한다

first_failed = None                             # 처음 나오는 실패 이벤트를 담을 변수(아직 없음)
for event in events:                            # 이벤트를 하나씩 꺼낸다
    if event["result"] == "실패" and first_failed is None:  # 실패 이벤트이고 아직 담은 것이 없으면
        first_failed = event                    # 이 이벤트를 담는다
print("--- 단계 2: 처음 나오는 실패 이벤트")    # 단계 2 시작을 알리는 줄
print(first_failed)                             # 처음 나오는 실패 이벤트를 출력한다

counts = {}                                     # 결과별 횟수를 담을 딕셔너리
for event in events:                            # 이벤트를 하나씩 꺼낸다
    result = event["result"]                    # 그 이벤트의 결과
    counts[result] = counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 3: 성공 · 실패별 개수")         # 단계 3 시작을 알리는 줄
print(counts)                                   # 성공 · 실패별 개수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `normalize_web.py` · `day02_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `normalize_web.py` 에서 직접 쓰는 곳 여섯 군데를 씁니다. 2.2 의 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day02_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_2-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 세 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1은 1줄, 단계 2는 1줄, 단계 3은 1줄입니다.
5. **[보고서]** `day02_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 정규화한 이벤트 수와 읽기 실패한 줄 수, 성공과 실패 개수를 적어 주세요.
   - (나) 🔍 시각을 `02/Nov/2026:09:00:00 +0900` 모양 그대로 문자열로 정렬하면 12월 1일 요청(`01/Dec/2026:…`)과 11월 2일 요청(`02/Nov/2026:…`) 중 어느 쪽이 앞에 놓일지 예상하고, 공통 모양(`2026-11-02 09:00:00`)으로 바꾸면 무엇이 달라지는지 이유와 함께 적어 주세요.
   - (다) 🔍 이벤트에 원래 로그 줄(`raw`)을 그대로 남겨 두는 이유는 무엇인가요? 정규화하면 사라지는 정보를 한 가지 예로 들어 함께 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 문자열 시각을 시각 값으로 | `parsed = datetime.strptime(time_text, NGINX_TIME_FORMAT)` |
| 시간대 정보 떼기 | `local_time = parsed.replace(tzinfo=None)` |
| 공통 모양 문자열로 | `time_out = local_time.strftime(COMMON_TIME_FORMAT)` |
| 상태 코드 → 결과 | `if status >= 400:` → `return "실패"` → `return "성공"` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 판정 서버 로그와 SaaS 로그를 공통 이벤트로 바꾸기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「웹 서버 로그는 공통 이벤트로 바꿨습니다. 나머지 두 로그도 같은 모양으로 맞춰 주세요.
>
> - 판정 서버 로그(3과목에서 만든 서버가 남기는 JSON): 접속 주소가 없습니다.
> - SaaS 로그(CSV): 사용자가 메일 주소(`seoyeon@a-corp.example`)로 적혀 있으니 이름만 꺼내 주세요.
> - 두 로그 모두 성공 · 실패를 웹 서버 로그처럼 `성공` · `실패` 로 통일해 주세요.」
> - **왜 중요한가**: <mark>같은 사람이 로그마다 `seoyeon` 과 `seoyeon@a-corp.example` 로 적히면 사용자별로 세거나 이어 볼 수 없습니다.</mark> 접속 주소가 원래 없는 로그에는 임의의 주소를 채우지 말고 `None` 으로 둡니다. 가짜 주소로 세어지는 이벤트가 생기기 때문입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 2교시에서는 웹 서버 로그 한 종류를 바꿨습니다. 같은 방법을 나머지 두 종류에 적용합니다.
2. 로그마다 어려운 곳이 다릅니다.
   - 판정 서버 로그: 시각이 `2026-11-02T09:40` 처럼 `T` 로 나뉘어 있고 초가 없습니다. 접속 주소가 없습니다.
   - SaaS 로그: 시각은 이미 공통 모양입니다. 사용자가 메일 주소입니다.

### 📖 3.1 CSV 읽기와 값 바꾸는 표

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 문법 상자의 코드는 눈으로 읽어도 되고, `saas_events.csv` 가 있는 폴더에서 따라 쳐 보아도 됩니다.

**🐍 문법 상자 — CSV 파일을 딕셔너리로 읽기**

**<mark>`csv.DictReader`</mark> 는 CSV 파일의 첫 줄을 열 이름으로 삼아, 둘째 줄부터 한 줄씩 「열 이름: 값」 딕셔너리로 읽어 줍니다**

```python
import csv                              # CSV 파일을 읽는 도구를 불러온다

rows = []                               # 행을 모을 리스트
with open("saas_events.csv", encoding="utf-8", newline="") as saas_file:  # CSV 파일을 연다
    reader = csv.DictReader(saas_file)  # 첫 줄을 열 이름으로 삼아 행마다 딕셔너리로 읽는다
    for row in reader:                  # 행을 하나씩 꺼낸다
        rows.append(row)                # 리스트에 추가한다
first_row = rows[0]                     # 첫 행을 꺼낸다
print(first_row)                        # 첫 행(딕셔너리)을 출력한다

row_count = len(rows)                   # 행이 몇 개인지 센다
print(row_count)                        # 행 수를 출력한다
```

실행 결과:

```
{'time': '2026-11-02 02:14:08', 'account': 'jiwoo@a-corp.example', 'event': 'login', 'ip_address': '203.0.113.80', 'outcome': 'failure'}
14
```

CSV 한 줄이 딕셔너리 하나로 바뀌는 모양입니다.

| | 모양 |
|---|---|
| CSV 첫 줄(열 이름) | `time,account,event,ip_address,outcome` |
| CSV 둘째 줄(값) | `2026-11-02 02:14:08,jiwoo@a-corp.example,login,203.0.113.80,failure` |
| `DictReader` 가 만든 딕셔너리 | `{"time": "2026-11-02 02:14:08", "account": "jiwoo@a-corp.example", "event": "login", "ip_address": "203.0.113.80", "outcome": "failure"}` |

- CSV(씨에스브이)는 값을 쉼표로 나눠 적은 표 파일입니다. 첫 줄은 열 이름(`time,account,event,…`)입니다.
- `csv.DictReader(saas_file)` 로 만든 `reader` 를 `for row in reader:` 로 돌리면 행마다 `{"time": …, "account": …}` 딕셔너리가 나옵니다. 그래서 `row["account"]` 처럼 이름으로 값을 꺼냅니다.
- CSV 파일을 열 때는 `newline=""` 을 함께 씁니다. 줄바꿈을 csv 도구가 직접 처리하게 하는 관례입니다.

**🐍 문법 상자 — 값을 다른 값으로 바꾸는 표**

**딕셔너리를 「바꾸는 표」로 쓰면 <mark>`표[키]`</mark> 한 줄로 값을 다른 값으로 바꿀 수 있습니다. 예: `"failure"` → `"실패"`**

```python
RESULT_MAP = {"success": "성공", "failure": "실패"}  # SaaS 의 outcome 을 바꾸는 표
outcome = "failure"                                  # 바꿀 값
result = RESULT_MAP[outcome]                         # 표에서 "failure" 에 짝지은 값을 꺼낸다
print(result)                                        # 바꾼 값을 출력한다

ALLOWED_MAP = {True: "성공", False: "실패"}          # 판정 서버의 allowed 를 바꾸는 표
allowed = True                                       # 바꿀 값
allowed_result = ALLOWED_MAP[allowed]                # 표에서 True 에 짝지은 값을 꺼낸다
print(allowed_result)                                # 바꾼 값을 출력한다
```

실행 결과:

```
실패
성공
```

- `RESULT_MAP = {"success": "성공", "failure": "실패"}` 처럼 왼쪽(키)과 오른쪽(바꾼 값)을 짝지어 둡니다. `RESULT_MAP["failure"]` 는 `"실패"` 입니다.
- 판정 서버의 `allowed` 는 `true` / `false` 이고 파이썬에서는 `True` / `False` 입니다. `ALLOWED_MAP = {True: "성공", False: "실패"}` 로 만들면 `ALLOWED_MAP[True]` 가 `"성공"` 입니다.
- 표에 없는 키로 꺼내면 `KeyError` 오류가 납니다. 예상 못 한 값(`pending` 등)이 들어오면 멈추기 때문에 오류가 나는 것이 오히려 단서가 됩니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `convert_server_time` | 판정 서버 시각 문자열 | 공통 모양 시각 문자열 |
| `normalize_server` | 판정 서버 로그 한 줄(JSON 문자열) | 공통 이벤트(`ip` 는 `None`) |
| `normalize_saas` | CSV 한 행(딕셔너리) | 공통 이벤트(`user` 는 메일에서 꺼낸 이름) |
| `load_server` · `load_saas` | 파일 경로 | 공통 이벤트 리스트(미리 채움) |

- **직접 쓰는 곳은 세 함수**(번호 1 ~ 6)입니다.
  - `convert_server_time`(1 · 2번): 2교시와 같은 방식으로 시각 모양을 바꿉니다(시간대가 없어서 `replace` 는 필요 없습니다).
  - `normalize_server`(3번): 표에서 `allowed` 를 `"성공"` / `"실패"` 로 바꿉니다.
  - `normalize_saas`(4 ~ 6번): 메일 주소에서 이름을 꺼내고, 표에서 `outcome` 을 바꿉니다.
- **미리 채운 것**: 파일을 읽어 이벤트 리스트로 만드는 `load_server` · `load_saas` 와 이벤트를 묶는 줄입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 판정 서버 로그와 SaaS 로그를 공통 이벤트로 바꾸기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 판정 서버 로그는 시각 가운데에 `T` 가 있고 접속 주소가 없습니다. SaaS 로그는 사용자가 메일 주소이고 결과가 `success` / `failure` 입니다.
- **그래서 만드는 것**: `normalize_json_csv.py` 입니다.
  - 판정 서버: 시각을 공통 모양으로, `allowed` 를 `성공` · `실패` 로 바꿉니다.
  - SaaS: 메일 주소에서 이름만 꺼내고, `outcome` 을 `성공` · `실패` 로 바꿉니다.
- **실행하면**: 단계 1: 판정 서버 이벤트 수와 성공 · 실패별 개수, 단계 2: SaaS 이벤트 수와 성공 · 실패별 개수, 단계 3: 각 로그의 첫 이벤트가 나옵니다.
- **현업에서는**: 로그 종류가 늘면 변환 코드를 하나 더 만듭니다. 결과 모양이 같아서 뒤의 탐지 코드는 고치지 않아도 됩니다.

**🎯 할 일**

1. `normalize_json_csv.py` · `day02_3-1_run.py` 두 파일을 만들고, `normalize_json_csv.py` 의 `convert_server_time` · `normalize_server` · `normalize_saas` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>판정 서버 이벤트 수와 성공 · 실패별 개수</mark>(단계 1), <mark>SaaS 이벤트 수와 성공 · 실패별 개수</mark>(단계 2), <mark>각 로그의 첫 이벤트</mark>(단계 3)를 읽습니다.

**`normalize_json_csv.py`**

```python
import csv                                           # CSV 파일을 읽는 도구를 불러온다
import json                                          # JSON 문자열을 딕셔너리로 바꾸는 도구를 불러온다
from datetime import datetime                        # 날짜와 시각을 다루는 도구를 불러온다

SERVER_TIME_FORMAT = "%Y-%m-%dT%H:%M"                # 판정 서버 시각의 모양(예: 2026-11-02T09:40)
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"             # 공통 시각의 모양(예: 2026-11-02 09:40:00)
ALLOWED_MAP = {True: "성공", False: "실패"}          # 판정 서버의 allowed 값을 공통 결과로 바꾸는 표
RESULT_MAP = {"success": "성공", "failure": "실패"}  # SaaS 의 outcome 값을 공통 결과로 바꾸는 표


def convert_server_time(time_text):                  # 판정 서버 시각 문자열을 받는 함수
    """판정 서버 시각을 공통 모양의 문자열로 바꾼다.
    예: 2026-11-02T09:40 → 2026-11-02 09:40:00.
    판정 서버 로그를 공통 이벤트로 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. datetime.strptime(time_text, SERVER_TIME_FORMAT) 의 결과를 parsed 에 담는다
    # 2. parsed.strftime(COMMON_TIME_FORMAT) 의 결과를 time_out 에 담는다
    return time_out                                  # 공통 모양의 시각 문자열을 리턴한다


def normalize_server(line):                          # 판정 서버 로그 한 줄(JSON 문자열)을 받는 함수
    """판정 서버 로그 한 줄을 공통 이벤트 딕셔너리로 바꾼다.
    판정 서버 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    item = json.loads(line)                          # JSON 문자열을 딕셔너리로 바꾼다
    time_out = convert_server_time(item["time"])     # 공통 모양의 시각으로 바꾼다
    allowed = item["allowed"]                        # 허용이었는지(True 또는 False)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. ALLOWED_MAP 에서 allowed 에 해당하는 값을 꺼내 result 에 담는다 (ALLOWED_MAP[allowed])
    raw_text = line.strip()                          # 원래 줄(양끝 공백과 줄바꿈 뺀 것)을 보관한다
    event = {                                        # 공통 이벤트의 키로 묶는다
        "time": time_out,                            # 일어난 시각
        "source": "server",                          # 어느 로그에서 왔는지
        "user": item["user"],                        # 요청한 사용자
        "ip": None,                                  # 판정 서버 로그에는 접속 주소가 없다
        "action": item["permission"],                # 요청한 권한
        "result": result,                            # 성공인지 실패인지
        "raw": raw_text,                             # 원래 로그 줄
    }
    return event                                     # 공통 이벤트를 리턴한다


def normalize_saas(row):                             # SaaS CSV 한 행(딕셔너리)을 받는 함수
    """SaaS 로그 한 행을 공통 이벤트 딕셔너리로 바꾼다.
    SaaS 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. row["account"] 를 "@" 기준으로 나눠 account_parts 에 담는다 (account 예: seoyeon@a-corp.example)
    # 5. account_parts 의 첫 값을 user 에 담는다
    outcome = row["outcome"]                         # success 또는 failure
    # 6. RESULT_MAP 에서 outcome 에 해당하는 값을 꺼내 result 에 담는다
    event = {                                        # 공통 이벤트의 키로 묶는다
        "time": row["time"],                         # SaaS 시각은 이미 공통 모양이라 그대로 쓴다
        "source": "saas",                            # 어느 로그에서 왔는지
        "user": user,                                # 메일 주소에서 꺼낸 사용자 이름
        "ip": row["ip_address"],                     # 접속 주소
        "action": row["event"],                      # 무엇을 했는지
        "result": result,                            # 성공인지 실패인지
        "raw": row,                                  # 원래 CSV 행(딕셔너리)을 보관한다
    }
    return event                                     # 공통 이벤트를 리턴한다


def load_server(path):                               # 판정 서버 로그 파일 경로를 받는 함수
    """판정 서버 로그 파일의 모든 줄을 공통 이벤트 리스트로 바꾼다.
    판정 서버 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                      # 결과를 담을 리스트
    with open(path, encoding="utf-8") as server_file:  # 파일을 연다
        for line in server_file:                     # 한 줄씩 꺼낸다
            event = normalize_server(line)           # 공통 이벤트로 바꾼다
            events.append(event)                     # 리스트에 추가한다
    return events                                    # 이벤트 리스트를 리턴한다


def load_saas(path):                                 # SaaS CSV 파일 경로를 받는 함수
    """SaaS CSV 파일의 모든 행을 공통 이벤트 리스트로 바꾼다.
    SaaS 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                      # 결과를 담을 리스트
    with open(path, encoding="utf-8", newline="") as saas_file:  # 파일을 연다(CSV 는 newline="" 을 붙인다)
        reader = csv.DictReader(saas_file)           # 첫 줄을 열 이름으로 삼아 행마다 딕셔너리로 읽는다
        for row in reader:                           # 행을 하나씩 꺼낸다
            event = normalize_saas(row)              # 공통 이벤트로 바꾼다
            events.append(event)                     # 리스트에 추가한다
    return events                                    # 이벤트 리스트를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 4번의 `split("@")` 는 어제 `split('"', 2)` 처럼 구분 문자로 나눈 리스트를 만듭니다. `seoyeon@a-corp.example` 은 `["seoyeon", "a-corp.example"]` 이 되고, 5번에서 첫 값(`account_parts[0]`)을 씁니다.
- 번호 주석이 연달아 붙어 있어도(예: 4 · 5번), 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `UnboundLocalError` 또는 `NameError` 가 납니다. 예를 들어 1 · 2번을 아직 안 썼으면 `time_out` 을 찾지 못합니다.

**`day02_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 두 로그를 공통 이벤트로 바꿔 세 단계로 출력합니다.

```python
from normalize_json_csv import load_server, load_saas  # 방금 만든 파일 읽기 함수를 불러온다

server_events = load_server("server_log.jsonl")     # 판정 서버 로그를 공통 이벤트로 바꾼다
saas_events = load_saas("saas_events.csv")          # SaaS 로그를 공통 이벤트로 바꾼다

server_count = len(server_events)                   # 판정 서버 이벤트 수를 센다
server_counts = {}                                  # 결과별 횟수를 담을 딕셔너리
for event in server_events:                         # 이벤트를 하나씩 꺼낸다
    result = event["result"]                        # 그 이벤트의 결과
    server_counts[result] = server_counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 1: 판정 서버 이벤트", server_count, "개")  # 단계 1 시작을 알리는 줄
print(server_counts)                                # 성공 · 실패별 개수를 출력한다

saas_count = len(saas_events)                       # SaaS 이벤트 수를 센다
saas_counts = {}                                    # 결과별 횟수를 담을 딕셔너리
for event in saas_events:                           # 이벤트를 하나씩 꺼낸다
    result = event["result"]                        # 그 이벤트의 결과
    saas_counts[result] = saas_counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 2: SaaS 이벤트", saas_count, "개")  # 단계 2 시작을 알리는 줄
print(saas_counts)                                  # 성공 · 실패별 개수를 출력한다

first_server = server_events[0]                     # 판정 서버 첫 이벤트를 꺼낸다
first_saas = saas_events[0]                         # SaaS 첫 이벤트를 꺼낸다
print("--- 단계 3: 각 로그의 첫 이벤트")            # 단계 3 시작을 알리는 줄
print(first_server)                                 # 판정 서버 첫 이벤트를 출력한다
print(first_saas)                                   # SaaS 첫 이벤트를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `normalize_json_csv.py` · `day02_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `normalize_json_csv.py` 에서 직접 쓰는 곳 여섯 군데를 씁니다. 3.1 의 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day02_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_3-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 세 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1은 1줄, 단계 2는 1줄, 단계 3은 2줄입니다.
5. **[보고서]** `day02_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 판정 서버와 SaaS 이벤트의 수와 성공 · 실패별 개수를 적어 주세요.
   - (나) 🔍 판정 서버 로그에는 접속 주소가 없어서 `ip` 를 `None` 으로 두었습니다. `None` 대신 가짜 주소 `0.0.0.0` 을 넣으면 주소별로 셀 때 어떤 문제가 생길까요? 이유도 함께 적어 주세요.
   - (다) 🔍 정규화하면서 공통 이벤트의 키에 들어가지 않은 정보를 판정 서버 로그에서 찾아 적고, 그 정보를 나중에 어디서 찾을 수 있는지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 판정 서버 시각 바꾸기 | `parsed = datetime.strptime(time_text, SERVER_TIME_FORMAT)` → `time_out = parsed.strftime(COMMON_TIME_FORMAT)` |
| `allowed` → 성공 · 실패 | `result = ALLOWED_MAP[allowed]` |
| 메일 주소에서 이름 꺼내기 | `account_parts = row["account"].split("@")` → `user = account_parts[0]` |
| `outcome` → 성공 · 실패 | `result = RESULT_MAP[outcome]` |
| CSV 를 딕셔너리로 읽기 | `reader = csv.DictReader(saas_file)` → `for row in reader:` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 세 로그를 하나로 합쳐 시간순으로 저장하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「세 로그가 같은 모양이 되었습니다. 하나로 합쳐 시간 순서로 정렬해 파일로 저장해 주세요. 오후에 이 파일로 실패가 몇 번 났는지 세겠습니다.
>
> 소스별로 이벤트가 몇 개씩인지, 사용자나 주소가 비어 있는 이벤트가 몇 개인지도 알려 주세요. 합친 결과로 gaeun 이 오늘 한 일을 시간순으로 보여 주세요.」
> - **왜 중요한가**: <mark>로그가 따로 있을 때는 보이지 않던 같은 계정의 일이 시간순으로 합치면 보입니다.</mark> 값이 비어 있는 이벤트 수는 분석에서 빠지는 이벤트가 얼마나 되는지 미리 알려 줍니다. 저장한 파일은 오후 분석의 입력이 됩니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 2 · 3교시에서 만든 함수는 로그 한 종류씩 공통 이벤트 리스트를 만듭니다. 이제 세 리스트를 **합치고, 시간순으로 정렬하고, 파일로 저장**합니다.
2. 순서는 이렇습니다.
   - 웹 서버 이벤트 28개 · 판정 서버 이벤트 15개 · SaaS 이벤트 14개를 각각 만듭니다.
   - 하나의 리스트로 이어 붙입니다(57개).
   - `time` 문자열 순서로 정렬합니다. 공통 모양(`2026-11-02 09:12:03`)은 연 · 월 · 일 · 시 · 분 · 초 순서라서 문자열 순서가 곧 시간 순서입니다.
   - `normalized_events.json` 파일로 저장합니다.

### 📖 4.1 이어 붙이기 · 정렬하기 · 저장하기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 문법 상자의 코드는 눈으로 읽어도 되고, 따라 쳐 보아도 됩니다.

**🐍 문법 상자 — 리스트를 함수가 알려 주는 값으로 정렬하기**

**<mark>`리스트.sort(key=함수)`</mark> 는 각 이벤트를 함수에 넣어 나온 값의 순서로 리스트를 정렬합니다**

두 리스트를 `+` 로 이어 붙이는 것은 파이썬에서 배운 대로입니다. 새로 나오는 것은 `sort(key=함수)` 하나입니다.

```python
web_events = [{"time": "2026-11-02 11:00:00", "source": "server"}, {"time": "2026-11-02 09:12:03", "source": "web"}]  # 이벤트 두 개
saas_events = [{"time": "2026-11-02 10:12:55", "source": "saas"}]  # 이벤트 한 개
merged = web_events + saas_events          # 리스트 두 개를 이어 붙인다


def get_time(event):                       # 이벤트 하나를 받는 함수
    """정렬 기준으로 쓸 시각 문자열을 리턴한다.
    이벤트를 시간순으로 정렬할 때 쓴다.
    """
    return event["time"]                   # 이벤트의 time 값을 리턴한다


merged.sort(key=get_time)                  # get_time 이 알려 주는 time 이 이른 것부터(오름차순) 정렬한다
for event in merged:                       # 이벤트를 하나씩 꺼낸다
    print(event["time"], event["source"])  # 시각과 소스를 출력한다
```

실행 결과:

```
2026-11-02 09:12:03 web
2026-11-02 10:12:55 saas
2026-11-02 11:00:00 server
```

- `a + b` 는 리스트 `a` 뒤에 `b` 를 이어 붙인 새 리스트입니다(배운 대로입니다).
- `events.sort(key=get_time)` 은 리스트 `events` 의 각 이벤트를 `get_time` 함수에 넣어 나온 값(`time`) 순서로 정렬합니다. `get_time` 뒤에 괄호를 붙이지 않습니다(함수를 부르는 것이 아니라 함수 자체를 알려 주는 것입니다).

위 코드의 `sort(key=get_time)` 이 하는 일을 따라가 봅니다.

| 정렬 전 순서 | `get_time` 이 리턴하는 값 |
|---|---|
| 1. `server` 이벤트 | `2026-11-02 11:00:00` |
| 2. `web` 이벤트 | `2026-11-02 09:12:03` |
| 3. `saas` 이벤트 | `2026-11-02 10:12:55` |

- `sort` 는 이 값을 서로 비교해 **작은 값부터 큰 값 순서(오름차순)** 로 놓습니다. 시각 문자열은 이른 시각일수록 작은 값이라서 이른 시각이 앞, 늦은 시각이 뒤에 옵니다. 결과는 `web`(09:12:03) → `saas`(10:12:55) → `server`(11:00:00) 순서입니다.
- `sort` 는 리스트 자체를 바꾸고 **아무것도 리턴하지 않습니다.** `events = events.sort(…)` 라고 쓰면 `events` 가 `None` 이 됩니다.

**🐍 문법 상자 — 리스트를 JSON 파일로 저장하기**

**<mark>`json.dump(값, 파일)`</mark> 은 파이썬 값을 JSON 형식으로 파일에 씁니다. `ensure_ascii=False` 는 한글을 그대로, `indent=2` 는 보기 좋게 들여쓰기를 합니다**

```python
import json                                       # JSON 도구를 불러온다

events = [{"user": "seoyeon", "result": "성공"}]  # 저장할 값
with open("demo_events.json", "w", encoding="utf-8") as demo_file:  # 쓰기 모드("w")로 파일을 연다
    json.dump(events, demo_file, ensure_ascii=False, indent=2)  # 한글은 그대로, 들여쓰기를 해서 파일에 쓴다
with open("demo_events.json", encoding="utf-8") as demo_file:  # 방금 쓴 파일을 다시 연다
    text = demo_file.read()                       # 내용을 문자열로 읽는다
print(text)                                       # 파일 내용을 출력한다
```

실행 결과:

```
[
  {
    "user": "seoyeon",
    "result": "성공"
  }
]
```

- `json.dumps` 는 값을 JSON **문자열**로 만들고, `json.dump` 는 값을 JSON **파일**에 바로 씁니다(`s` 가 없습니다).
- `ensure_ascii=False` 를 빼면 한글이 `성공` 같은 코드로 저장됩니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_web` | 웹 서버 로그 파일 경로 | 공통 이벤트 리스트(미리 채움) |
| `merge_events` | 이벤트 리스트 세 개 | 하나로 합쳐 시간순으로 정렬한 리스트 |
| `count_by_source` | 이벤트 리스트 | `{소스: 개수}` 딕셔너리 |
| `count_missing` | 이벤트 리스트와 키 이름 | 그 키의 값이 `None` 인 이벤트 수(미리 채움) |
| `save_events` | 이벤트 리스트와 파일 이름 | 없음(파일로 저장) |

- **직접 쓰는 곳은 세 함수**(번호 1 ~ 5)입니다.
  - `merge_events`(1 · 2번): 이어 붙이고 시간순으로 정렬합니다.
  - `count_by_source`(3 · 4번): 소스별 이벤트 수를 셉니다. 값별 횟수를 세는 `counts.get(…, 0) + 1` 은 3과목에서 쓴 방식과 같습니다.
  - `save_events`(5번): JSON 파일로 저장합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 세 로그의 이벤트를 합쳐 시간순으로 저장하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 공통 이벤트가 로그 종류별로 따로 있어서, 같은 계정이 여러 곳에서 한 일을 시간순으로 볼 수 없습니다.
- **그래서 만드는 것**: `normalize.py` 입니다.
  - 세 리스트를 하나로 이어 붙여 시간순으로 정렬합니다.
  - 소스별 이벤트 수를 셉니다.
  - `normalized_events.json` 파일로 저장합니다.
- **실행하면**: 단계 1: 소스별 이벤트 수, 단계 2: `user` · `ip` 가 비어 있는 이벤트 수, 단계 3: gaeun 의 이벤트(시간순), 단계 4: 저장한 이벤트 수가 나옵니다.
- **현업에서는**: 같은 모양으로 맞춘 이벤트를 한곳에 쌓아 두면 탐지 규칙은 그곳만 읽으면 됩니다. 이렇게 쌓아 두는 곳이 SIEM(심)의 저장소입니다.

**🎯 할 일**

1. `normalize.py` · `day02_4-1_run.py` 두 파일을 만들고, `normalize.py` 의 `merge_events` · `count_by_source` · `save_events` 에서 직접 쓰는 곳을 씁니다. 2교시의 `normalize_web.py` 와 3교시의 `normalize_json_csv.py` 가 필요합니다.
2. 실행해서 <mark>소스별 이벤트 수</mark>(단계 1), <mark>값이 비어 있는 이벤트 수</mark>(단계 2), <mark>gaeun 의 이벤트</mark>(단계 3), <mark>저장된 이벤트 수</mark>(단계 4)를 읽습니다.

**`normalize.py`**

```python
import json                                         # 파일에 JSON 으로 저장하는 도구를 불러온다
from normalize_web import normalize_web             # 웹 서버 로그 정규화 함수를 불러온다
from normalize_json_csv import load_server, load_saas  # 판정 서버 · SaaS 로그 읽기 함수를 불러온다

EVENTS_PATH = "normalized_events.json"              # 정규화한 이벤트를 저장할 파일 이름


def load_web(path):                                 # 웹 서버 로그 파일 경로를 받는 함수
    """웹 서버 로그 파일의 모든 줄을 공통 이벤트 리스트로 바꾸고 깨진 줄은 건너뛴다.
    웹 서버 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                     # 결과를 담을 리스트
    with open(path, encoding="utf-8") as web_file:  # 파일을 연다
        for line in web_file:                       # 한 줄씩 꺼낸다
            event = normalize_web(line)             # 공통 이벤트로 바꾼다
            if event is not None:                   # 읽을 수 있는 줄이면
                events.append(event)                # 리스트에 추가한다
    return events                                   # 이벤트 리스트를 리턴한다


def get_time(event):                                # 이벤트 하나를 받는 함수
    """정렬 기준으로 쓸 시각 문자열을 리턴한다.
    이벤트를 시간순으로 정렬할 때 쓴다.
    """
    return event["time"]                            # 이벤트의 time 값을 리턴한다


def merge_events(web, server, saas):                # 세 이벤트 리스트를 받는 함수
    """이벤트 리스트 세 개를 하나로 이어 붙이고 시간순으로 정렬한다.
    여러 로그에서 같은 계정이 한 일을 시간순으로 함께 보고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web, server, saas 를 + 로 이어 붙여 events 에 담는다
    # 2. events.sort(key=get_time) 로 time 이 이른 것부터(오름차순) 정렬한다 (sort 는 events 자체를 바꾸고 아무것도 리턴하지 않는다)
    return events                                   # 시간순으로 정렬한 이벤트 리스트를 리턴한다


def count_by_source(events):                        # 이벤트 리스트를 받는 함수
    """소스별 이벤트 수를 {소스: 개수} 딕셔너리로 센다.
    합친 이벤트가 로그 종류마다 몇 개씩 들어왔는지 확인할 때 쓴다.
    """
    counts = {}                                     # 결과를 담을 딕셔너리
    for event in events:                            # 이벤트를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. event 의 "source" 값을 source 에 담는다
        # 4. counts 에서 source 의 현재 횟수(없으면 0)에 1 을 더해 counts[source] 에 담는다 (counts.get)
    return counts                                   # 소스별 개수를 리턴한다


def count_missing(events, key):                     # 이벤트 리스트와 키 이름을 받는 함수
    """key 키의 값이 비어 있는(None) 이벤트 수를 리턴한다.
    분석에서 빠질 이벤트가 얼마나 되는지 미리 알아볼 때 쓴다.
    """
    missing = 0                                     # 비어 있는 개수를 0 으로 시작한다
    for event in events:                            # 이벤트를 하나씩 꺼낸다
        if event[key] is None:                      # 그 키의 값이 비어 있으면
            missing = missing + 1                   # 비어 있는 개수를 1 늘린다
    return missing                                  # 비어 있는 개수를 리턴한다


def save_events(events, path):                      # 이벤트 리스트와 저장할 파일 이름을 받는 함수
    """이벤트 리스트를 JSON 파일로 저장한다.
    정규화 결과를 다음 분석의 입력으로 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as events_file:  # 파일을 쓰기 모드("w")로 연다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. json.dump(events, events_file, ensure_ascii=False, indent=2) 로 events 를 events_file 에 저장한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 · 2번은 함수 안이라 앞에 공백 4개이고, 3 · 4번은 `for` 안쪽이라 8개이고, 5번은 `with` 안쪽이라 8개입니다.
- 번호 주석이 연달아 붙어 있어도(예: 3 · 4번), 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다. `for` 아래와 `with` 아래가 주석뿐이기 때문입니다.

**`day02_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 세 로그를 읽어 합치고 네 단계로 출력합니다.

```python
from normalize import load_web, merge_events, count_by_source, count_missing, save_events, EVENTS_PATH  # 방금 만든 함수를 불러온다
from normalize_json_csv import load_server, load_saas  # 판정 서버 · SaaS 로그 읽기 함수를 불러온다
import json                                           # 저장한 파일을 다시 읽을 수 있게 불러온다


def show_user(events, name):                          # 이벤트 리스트와 사용자 이름을 받는 함수
    """한 사용자의 이벤트를 시각 · 소스 · 행동 · 결과로 한 줄씩 출력한다.
    같은 사용자가 여러 로그에서 한 일을 시간순으로 볼 때 쓴다.
    """
    for event in events:                              # 이벤트를 하나씩 꺼낸다
        if event["user"] == name:                     # 그 사용자의 이벤트이면
            time_text = event["time"]                 # 시각
            source = event["source"]                  # 소스
            action = event["action"]                  # 행동
            result = event["result"]                  # 결과
            print(time_text, source, action, result)  # 한 줄로 출력한다


web = load_web("access_sample.log")                   # 웹 서버 로그를 공통 이벤트로 바꾼다
server = load_server("server_log.jsonl")              # 판정 서버 로그를 공통 이벤트로 바꾼다
saas = load_saas("saas_events.csv")                   # SaaS 로그를 공통 이벤트로 바꾼다
events = merge_events(web, server, saas)              # 하나로 합쳐 시간순으로 정렬한다

source_counts = count_by_source(events)               # 소스별 개수를 센다
print("--- 단계 1: 소스별 이벤트 수")                  # 단계 1 시작을 알리는 줄
print(source_counts)                                   # 소스별 개수를 출력한다

user_missing = count_missing(events, "user")           # user 가 비어 있는 이벤트 수를 센다
ip_missing = count_missing(events, "ip")               # ip 가 비어 있는 이벤트 수를 센다
print("--- 단계 2: 값이 None 인 이벤트 수")            # 단계 2 시작을 알리는 줄
print("user 가 비어 있는 이벤트", user_missing, "개")  # user 가 비어 있는 개수를 출력한다
print("ip 가 비어 있는 이벤트", ip_missing, "개")      # ip 가 비어 있는 개수를 출력한다

print("--- 단계 3: gaeun 의 이벤트를 시간순으로")     # 단계 3 시작을 알리는 줄
show_user(events, "gaeun")                            # gaeun 의 이벤트를 출력한다

save_events(events, EVENTS_PATH)                      # 이벤트를 JSON 파일로 저장한다
with open(EVENTS_PATH, encoding="utf-8") as events_file:  # 저장한 파일을 다시 연다
    saved_events = json.load(events_file)             # JSON 을 리스트로 읽는다
saved_count = len(saved_events)                       # 저장된 이벤트 수를 센다
print("--- 단계 4: 저장한 파일", EVENTS_PATH)         # 단계 4 시작을 알리는 줄
print("저장된 이벤트", saved_count, "개")             # 저장된 이벤트 수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `normalize.py` · `day02_4-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `normalize.py` 에서 직접 쓰는 곳 다섯 군데를 씁니다. 4.1 의 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day02_4-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_4-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 네 단계입니다. `--- 단계` 제목 줄은 세지 않고, 단계 1은 1줄, 단계 2는 2줄, 단계 3은 5줄, 단계 4는 1줄입니다.
5. **[VS Code]** 새로 생긴 `normalized_events.json` 을 열어 이벤트 하나가 7개 키(`time` · `source` · `user` · `ip` · `action` · `result` · `raw`)로 되어 있는지 봅니다.
6. **[보고서]** `day02_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 소스별 이벤트 수와 `user` · `ip` 가 비어 있는 이벤트 수, 저장된 이벤트 수를 적어 주세요.
   - (나) 🔍 단계 3의 gaeun 이벤트를 시간순으로 보고, 서로 다른 소스에서 나온 이벤트가 어떻게 이어지는지 적고, 로그를 따로 볼 때와 무엇이 달라지는지 적어 주세요.
   - (다) 🔍 `user` 가 비어 있는 이벤트가 28개입니다. 어느 로그(소스)의 이벤트이고 왜 비어 있는지 적어 주세요. 그리고 사용자 이름별로 개수를 세면 이 28개가 어떻게 될지 예상해 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 리스트 세 개를 하나로 | `events = web + server + saas` |
| 시간순으로 정렬(이른 시각이 앞, 오름차순) | `events.sort(key=get_time)` (`sort` 는 리턴값이 없음) |
| 소스별 개수 | `source = event["source"]` → `counts[source] = counts.get(source, 0) + 1` |
| JSON 파일로 저장 | `json.dump(events, f, ensure_ascii=False, indent=2)` |

---

### 마무리 · 오전 작업 확인하기

오전 작업을 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다. 오전에는 파일이 모두 있는지만 확인합니다.

**순서**

1. **[터미널]** `anomaly_detection` 폴더에서 오늘 만든 파일이 있는지 확인합니다.
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - `normalize_web.py` · `normalize_json_csv.py` · `normalize.py` · `day02_2-1_run.py` · `day02_3-1_run.py` · `day02_4-1_run.py` · `normalized_events.json` · `server_log.jsonl` · `saas_events.csv` 와 이 안내 · 보고서 두 파일이 보여야 합니다.
2. **[보고서]** `day02_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지 봅니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 웹 서버 로그 한 줄을 공통 이벤트로 바꿨다 | 오전 2-1 |
| 판정 서버 로그와 SaaS 로그를 공통 이벤트로 바꿨다 | 오전 3-1 |
| 세 로그를 합쳐 시간순으로 정렬하고 `normalized_events.json` 으로 저장했다 | 오전 4-1 |

오후에는 이 `normalized_events.json` 과 같은 모양의 파일을 **판다스**로 읽어서 실패한 이벤트를 골라 세고, 사용자별 · 시간대별로 묶습니다. 판다스 설치는 어제 미리 했다면 확인만 합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_2-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `convert_time` 안

```python
    parsed = datetime.strptime(time_text, NGINX_TIME_FORMAT)  # 문자열을 시각 값으로 바꾼다(시간대 +0900 포함)
    local_time = parsed.replace(tzinfo=None)  # 시간대 정보를 떼고 한국 시각만 남긴다
    time_out = local_time.strftime(COMMON_TIME_FORMAT)  # 공통 모양의 문자열로 바꾼다
```

② `convert_result` 안

```python
    if status >= 400:  # 400 이상이면 요청이 실패한 것이다
        return "실패"  # 실패를 리턴한다
    return "성공"      # 그 밖에는 성공을 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 정규화한 이벤트는 <mark>**28개**</mark>, 읽기 실패는 <mark>**2줄**</mark>, 결과는 성공 <mark>**15**</mark> · 실패 <mark>**13**</mark> 입니다.

```
--- 단계 1: 정규화한 이벤트 28 개 · 읽기 실패 2 줄
{'time': '2026-11-02 09:01:05', 'source': 'web', 'user': None, 'ip': '198.51.100.21', 'action': 'GET /', 'result': '성공', 'raw': '198.51.100.21 - - [02/Nov/2026:09:01:05 +0900] "GET / HTTP/1.1" 200 1204 "-" "Mozilla/5.0"'}
--- 단계 2: 처음 나오는 실패 이벤트
{'time': '2026-11-02 09:12:03', 'source': 'web', 'user': None, 'ip': '203.0.113.50', 'action': 'POST /login', 'result': '실패', 'raw': '203.0.113.50 - - [02/Nov/2026:09:12:03 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"'}
--- 단계 3: 성공 · 실패별 개수
{'성공': 15, '실패': 13}
```

- (나) 시각을 `02/Nov/2026:09:00:00 +0900` 같은 모양 그대로 문자열로 정렬하면 시간 순서가 틀립니다.
  - 문자열은 앞 문자부터 차례로 비교하므로, 맨 앞이 일(`02`, `01`)입니다. 12월 1일(`01/Dec/…`)이 11월 2일(`02/Nov/…`)보다 앞에 놓입니다.
  - 공통 모양 `2026-11-02 09:00:00` 은 연 · 월 · 일 · 시 · 분 · 초 순서라서, 문자열 순서가 곧 시간 순서입니다.
  - 아래 코드로 확인할 수 있습니다.

```python
december_first = "01/Dec/2026:09:00:00 +0900"   # nginx 모양의 12월 1일 시각
november_second = "02/Nov/2026:09:00:00 +0900"  # nginx 모양의 11월 2일 시각
print(december_first < november_second)         # 문자열 순서로 12월 1일이 앞인지 비교한다
common_december = "2026-12-01 09:00:00"         # 공통 모양의 12월 1일 시각
common_november = "2026-11-02 09:00:00"         # 공통 모양의 11월 2일 시각
print(common_december < common_november)        # 문자열 순서로 12월 1일이 앞인지 비교한다
```

실행 결과:

```
True
False
```

- (다) `raw` 는 정규화 코드가 틀렸는지 확인하고 알림의 근거를 보여 주기 위해 남깁니다.
  - 정규화는 원래 정보 일부를 바꾸거나 버립니다(예: 상태 코드 `401` 이 `실패` 로 바뀌면 어떤 오류였는지 사라집니다). 원래 줄이 있으면 `401` 이었는지 `500` 이었는지 다시 볼 수 있습니다.
  - 정규화 결과가 이상할 때 원본과 나란히 놓고 어디서 틀렸는지 찾을 수 있습니다.

**왜**

- <mark>모양이 다른 시각은 나란히 놓을 수도 정렬할 수도 없습니다.</mark> 하나의 모양으로 맞추면 이후 모든 단계가 같은 기준을 씁니다.
  - 성공 · 실패도 `401` · `true` · `success` 를 `실패` / `성공` 두 가지로 줄이면 규칙을 한 번만 만듭니다.

**자주 틀리는 곳**

- `strptime` 에 nginx 형식(`NGINX_TIME_FORMAT`) 대신 공통 형식(`COMMON_TIME_FORMAT`)을 넣으면 문자열 모양과 형식이 달라 `ValueError` 오류가 납니다. 두 형식 이름을 헷갈리지 않습니다.
  - 실행하면 다음 오류가 납니다(<mark>`does not match format`</mark> 이면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day02_2-1_run.py", line 7, in <module>
    event = normalize_web(line)  # 한 줄을 공통 이벤트로 바꾼다
  File "…/anomaly_detection/normalize_web.py", line 57, in normalize_web
    time_out = convert_time(time_text)  # 공통 모양의 시각으로 바꾼다
  File "…/anomaly_detection/normalize_web.py", line 25, in convert_time
    parsed = datetime.strptime(time_text, COMMON_TIME_FORMAT)  # 문자열을 시각 값으로 바꾼다(시간대 +0900 포함)
ValueError: time data '02/Nov/2026:09:01:05 +0900' does not match format '%Y-%m-%d %H:%M:%S'
```

  - 줄 번호는 사람마다 다릅니다.
- `replace(tzinfo=None)` 를 빼도 오류는 나지 않고 `strftime` 결과도 같습니다. 이 수업에서는 세 로그의 시각 값을 같은 종류(시간대 없음)로 맞춰 두려고 떼어 둡니다.

**관제에서는**

- 로그 수집 도구의 파서 설정은 시각 형식을 직접 적습니다. 로그 형식이 바뀌면 파서가 읽지 못하고, 읽지 못한 줄이 갑자기 늘면 수집이 깨졌다는 신호입니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_3-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `convert_server_time` 안

```python
    parsed = datetime.strptime(time_text, SERVER_TIME_FORMAT)  # 문자열을 시각 값으로 바꾼다
    time_out = parsed.strftime(COMMON_TIME_FORMAT)  # 공통 모양의 문자열로 바꾼다(초는 00 이 된다)
```

② `normalize_server` 안(`allowed` 를 꺼낸 줄 아래)

```python
    result = ALLOWED_MAP[allowed]  # True 면 "성공", False 면 "실패"
```

③ `normalize_saas` 안

```python
    account_parts = row["account"].split("@")  # 메일 주소를 @ 앞뒤로 나눈다
    user = account_parts[0]                    # @ 앞이 사용자 이름이다
    result = RESULT_MAP[outcome]               # success 면 "성공", failure 면 "실패"
```

**결과**

- (가) 출력은 다음과 같고, 판정 서버 이벤트는 <mark>**15개**</mark>(성공 6 · 실패 9), SaaS 이벤트는 <mark>**14개**</mark>(성공 13 · 실패 1)입니다.

```
--- 단계 1: 판정 서버 이벤트 15 개
{'성공': 6, '실패': 9}
--- 단계 2: SaaS 이벤트 14 개
{'실패': 1, '성공': 13}
--- 단계 3: 각 로그의 첫 이벤트
{'time': '2026-11-02 09:40:00', 'source': 'server', 'user': 'seoyeon', 'ip': None, 'action': 'SALES:QUERY', 'result': '성공', 'raw': '{"time": "2026-11-02T09:40", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}'}
{'time': '2026-11-02 02:14:08', 'source': 'saas', 'user': 'jiwoo', 'ip': '203.0.113.80', 'action': 'login', 'result': '실패', 'raw': {'time': '2026-11-02 02:14:08', 'account': 'jiwoo@a-corp.example', 'event': 'login', 'ip_address': '203.0.113.80', 'outcome': 'failure'}}
```

- (나) 판정 서버 로그에는 접속 주소가 원래 없기 때문에 `ip` 를 `None` 으로 둡니다.
  - 임의의 주소(예: `0.0.0.0`)를 채우면 이후 주소별로 셀 때 그 가짜 주소가 이벤트 15개를 가진 주소로 세어집니다.
  - 그러면 없는 주소에서 15번 요청이 온 것처럼 보이는 잘못된 분석이 됩니다. 없다는 사실 자체를 `None` 으로 남겨야 이후 코드가 「이 이벤트는 주소가 없다」고 판단할 수 있습니다.
- (다) 정규화하면 비교하기 쉬워지는 대신 로그 종류만 갖고 있던 정보 일부가 공통 이벤트의 키에 들어가지 않습니다.
  - 판정 서버 로그의 `reason`(거부 이유)과 `network`(접속 위치)는 공통 이벤트의 키에 없습니다.
  - 잃은 정보는 `raw` 에 그대로 있으므로 필요할 때 원래 줄에서 찾습니다. 그래서 `raw` 를 남깁니다.

**왜**

- <mark>로그마다 사용자 · 결과를 다르게 적기 때문에, 공통 이벤트로 바꿔야 같은 규칙으로 셀 수 있습니다.</mark>
  - 값 바꾸는 표(`ALLOWED_MAP` · `RESULT_MAP`)를 쓰면 바꾸는 규칙이 한곳에 모이고, 예상 못 한 값이 오면 `KeyError` 로 바로 드러납니다.

**자주 틀리는 곳**

- `account_parts[0]` 대신 `account_parts[1]` 을 쓰면 사용자 이름이 아니라 `a-corp.example` 이 나옵니다. `@` 앞이 이름입니다.
- 판정 서버의 `allowed` 를 바꿀 때 `ALLOWED_MAP` 대신 `RESULT_MAP` 을 쓰면 `KeyError: True` 오류가 납니다. 두 표는 키가 다릅니다(`True` · `False` 와 `"success"` · `"failure"`).
  - 실행하면 다음 오류가 납니다(<mark>`KeyError: True`</mark> 이면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day02_3-1_run.py", line 3, in <module>
    server_events = load_server("server_log.jsonl")  # 판정 서버 로그를 공통 이벤트로 바꾼다
  File "…/anomaly_detection/normalize_json_csv.py", line 78, in load_server
    event = normalize_server(line)  # 공통 이벤트로 바꾼다
  File "…/anomaly_detection/normalize_json_csv.py", line 33, in normalize_server
    result = RESULT_MAP[allowed]  # True 면 "성공", False 면 "실패"
KeyError: True
```

  - 줄 번호는 사람마다 다릅니다.

**관제에서는**

- 로그 종류가 새로 늘 때는 파서 하나를 더 만들고 같은 공통 이벤트를 리턴하게 합니다. 탐지 규칙은 고치지 않습니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day02_4-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `merge_events` 안

```python
    events = web + server + saas  # 리스트 세 개를 이어 붙여 하나로 만든다
    events.sort(key=get_time)     # time 이 이른 것부터(오름차순, = 시간순) 정렬한다
```

② `count_by_source` 안(`for` 안쪽)

```python
        source = event["source"]                    # 이 이벤트의 소스
        counts[source] = counts.get(source, 0) + 1  # 그 소스의 횟수를 1 늘린다
```

③ `save_events` 안(`with` 안쪽)

```python
        json.dump(events, events_file, ensure_ascii=False, indent=2)   # 한글은 그대로, 들여쓰기를 해서 저장한다
```

**결과**

- (가) 출력은 다음과 같고, 소스별 이벤트는 web <mark>**28**</mark> · server <mark>**15**</mark> · saas <mark>**14**</mark>, `user` 가 비어 있는 이벤트는 <mark>**28개**</mark>, `ip` 가 비어 있는 이벤트는 <mark>**15개**</mark>, 저장된 이벤트는 <mark>**57개**</mark>입니다.

```
--- 단계 1: 소스별 이벤트 수
{'saas': 14, 'web': 28, 'server': 15}
--- 단계 2: 값이 None 인 이벤트 수
user 가 비어 있는 이벤트 28 개
ip 가 비어 있는 이벤트 15 개
--- 단계 3: gaeun 의 이벤트를 시간순으로
2026-11-02 10:05:00 server ACCOUNT:CHANGE 실패
2026-11-02 10:09:00 server ACCOUNT:CHANGE 실패
2026-11-02 10:12:55 saas login 성공
2026-11-02 10:14:00 server ACCOUNT:CHANGE 실패
2026-11-02 16:10:00 server SALES:QUERY 성공
--- 단계 4: 저장한 파일 normalized_events.json
저장된 이벤트 57 개
```

- (나) gaeun 의 이벤트를 시간순으로 놓으면 판정 서버와 SaaS 의 일이 번갈아 나옵니다.
  - 10:05 · 10:09 판정 서버에서 `ACCOUNT:CHANGE` 가 실패하고, 10:12 SaaS 에 로그인이 성공하고, 10:14 판정 서버에서 다시 실패합니다.
  - 정규화 전에는 판정 서버 로그와 SaaS 로그를 따로 열어야 해서 이 순서를 이어서 볼 수 없습니다.
  - 이 순서만으로 원인을 알 수는 없습니다. 같은 사용자가 두 곳에서 어떤 일을 했는지 이어서 확인할 단서가 생겼다고 보면 됩니다.
- (다) `user` 가 비어 있는 이벤트 28개는 웹 서버 이벤트 전부입니다. 웹 서버 로그에는 사용자 이름이 원래 없기 때문입니다.
  - 사용자 이름으로 세거나 묶는 분석을 하면 이 28개는 어느 사용자에도 들어가지 못하고 빠집니다.
  - 그래서 사용자별 숫자만 보면 웹 서버에서 난 일을 놓칩니다. 오후에 판다스로 직접 확인합니다.

**왜**

- <mark>로그가 시간순으로 함께 보이면 여러 로그에 걸친 같은 계정의 일이 보입니다.</mark>
  - 시간순 정렬은 `time` 문자열이 연 · 월 · 일 · 시 · 분 · 초 순서라서 문자열 정렬만으로 됩니다.

**자주 틀리는 곳**

- `events = events.sort(key=get_time)` 처럼 `sort` 의 결과를 변수에 담으면 `events` 가 `None` 이 되어 다음 줄에서 오류가 납니다. `sort` 는 리스트 자체를 바꾸고 아무것도 리턴하지 않습니다.
  - 실행하면 다음 오류가 납니다(<mark>`'NoneType'`</mark> 이 들어간 오류이면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day02_4-1_run.py", line 24, in <module>
    source_counts = count_by_source(events)  # 소스별 개수를 센다
  File "…/anomaly_detection/normalize.py", line 45, in count_by_source
    for event in events:  # 이벤트를 하나씩 꺼낸다
TypeError: 'NoneType' object is not iterable
```

  - 줄 번호는 사람마다 다릅니다.
- `json.dump` 에서 `ensure_ascii=False` 를 빼면 오류는 나지 않지만 한글이 `\uc131\uacf5` 같은 코드로 저장됩니다.

**관제에서는**

- 정규화된 이벤트를 한곳에 모으는 것이 SIEM(심)의 수집 · 정규화 단계의 결과입니다. 이 저장소를 기준으로 탐지 규칙과 조사가 이어집니다.
  - 값이 비어 있는 이벤트 수는 분석에서 빠지는 이벤트가 얼마나 되는지 알려 주는 품질 점검입니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
pwd
ls
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기

**결과**

- 오늘 만든 파일 아홉 개와 안내 · 보고서 두 파일이 보여야 합니다. 깃허브에 올리는 일은 오후 6교시 마지막에 합니다.

---

### 앞 날 파일 완성본

어제 파일이 없거나 잘 안 될 때 이 코드로 만듭니다. `anomaly_detection` 폴더 바로 아래에 같은 이름으로 만듭니다.

**`log_parse.py`** (어제 5교시 완성본)

```python
def split_request(line):                           # 로그 한 줄(문자열)을 받는 함수
    """로그 한 줄을 큰따옴표 기준으로 앞 · 요청 · 뒤 세 조각으로 나눈다.
    나뉘지 않은 하나의 문자열인 로그에서 값을 꺼내기 시작할 때 쓴다.
    """
    prefix, request_text, suffix = line.split('"', 2)  # 큰따옴표 두 개를 기준으로 앞 · 요청 · 뒤 세 조각으로 나눈다
    return prefix, request_text, suffix            # 세 조각을 리턴한다


def read_request(request_text):                    # 요청 조각(예: GET /login HTTP/1.1)을 받는 함수
    """요청 조각에서 방법(method)과 경로(path)를 꺼낸다.
    무엇을 요청했는지 알고 싶을 때 쓴다.
    """
    method, path, protocol = request_text.split()  # 공백 기준으로 나눈 세 값을 세 이름에 한꺼번에 담는다
    return method, path                            # 방법과 경로를 리턴한다


def read_status(suffix):                           # 요청 뒤 조각(예:  401 312 "-" "Mozilla/5.0")을 받는 함수
    """요청 뒤 조각에서 상태 코드를 꺼내 정수로 리턴한다.
    요청이 성공했는지 실패했는지 가를 때 쓴다.
    """
    parts = suffix.split()                         # 공백 기준으로 나눈 조각 리스트를 만든다
    status_text = parts[0]                         # 첫 조각이 상태 코드 문자열이다
    status = int(status_text)                      # 숫자로 바꿔야 400 이상인지 비교할 수 있다
    return status                                  # 상태 코드(정수)를 리턴한다


def read_client(prefix):                           # 요청 앞 조각(예: 203.0.113.50 - - [02/Nov/2026:09:12:03 +0900] )을 받는 함수
    """요청 앞 조각에서 접속자 주소를 꺼낸다.
    어느 주소가 요청했는지 알고 싶을 때 쓴다.
    """
    parts = prefix.split()                         # 공백 기준으로 나눈 조각 리스트를 만든다
    client_ip = parts[0]                           # 첫 조각이 접속자 주소이다
    return client_ip                               # 접속자 주소를 리턴한다


def parse_line(line):                              # 로그 한 줄을 받는 함수
    """로그 한 줄을 ip · method · path · status 딕셔너리로 바꾼다.
    깨진 줄이면 None 을 리턴한다.
    접속 로그를 분석하기 전에 한 줄을 값으로 나눌 때 쓴다.
    """
    if line.count('"') < 2:                        # 큰따옴표가 두 개보다 적은 줄이면(잘렸거나 깨진 줄이면)
        return None                                # 읽을 수 없으니 None 을 리턴한다
    prefix, request_text, suffix = split_request(line)  # 세 조각으로 나눈다
    method, path = read_request(request_text)      # 요청 조각에서 방법과 경로를 꺼낸다
    status = read_status(suffix)                   # 뒤 조각에서 상태 코드를 꺼낸다
    client_ip = read_client(prefix)                # 앞 조각에서 접속자 주소를 꺼낸다
    entry = {                                      # 꺼낸 값을 딕셔너리로 묶는다
        "ip": client_ip,                           # 접속자 주소
        "method": method,                          # 요청 방법
        "path": path,                              # 요청 경로
        "status": status,                          # 상태 코드(정수)
    }
    return entry                                   # 딕셔너리를 리턴한다
```

**`access_sample.log`** (어제 시작하기 5번의 샘플 로그, 30줄) — 끝이 잘린 줄과 마지막 줄의 `-` 는 일부러 깨뜨린 줄이니 지우지 않습니다.

```
198.51.100.21 - - [02/Nov/2026:09:01:05 +0900] "GET / HTTP/1.1" 200 1204 "-" "Mozilla/5.0"
198.51.100.21 - - [02/Nov/2026:09:01:06 +0900] "GET /static/app.css HTTP/1.1" 200 3120 "-" "Mozilla/5.0"
198.51.100.34 - - [02/Nov/2026:09:03:47 +0900] "GET /login HTTP/1.1" 200 1830 "-" "Mozilla/5.0"
198.51.100.34 - - [02/Nov/2026:09:03:59 +0900] "POST /login HTTP/1.1" 302 0 "-" "Mozilla/5.0"
198.51.100.34 - - [02/Nov/2026:09:04:00 +0900] "GET /board HTTP/1.1" 200 5410 "-" "Mozilla/5.0"
192.0.2.15 - - [02/Nov/2026:09:05:21 +0900] "GET /board?page=2 HTTP/1.1" 200 5322 "-" "Mozilla/5.0"
192.0.2.15 - - [02/Nov/2026:09:05:40 +0900] "GET /board/12 HTTP/1.1" 200 2210 "-" "Mozilla/5.0"
203.0.113.50 - - [02/Nov/2026:09:12:01 +0900] "GET /login HTTP/1.1" 200 1830 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:03 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:06 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:09 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:12 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:15 +0900] "POST /login HTTP/1.1" 401 312 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:18 +0900] "POST /login HTTP/1.1" 302 0 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:25 +0900] "GET /admin HTTP/1.1" 403 287 "-" "python-requests/2.31.0"
203.0.113.50 - - [02/Nov/2026:09:12:27 +0900] "GET /admin/users HTTP/1.1" 403 287 "-" "python-requests/2.31.0"
198.51.100.90 - - [02/Nov/2026:09:20:10 +0900] "GET /.env HTTP/1.1" 404 153 "-" "curl/8.4.0"
198.51.100.90 - - [02/Nov/2026:09:20:11 +0900] "GET /wp-login.php HTTP/1.1" 404 153 "-" "curl/8.4.0"
198.51.100.90 - - [02/Nov/2026:09:20:12 +0900] "GET /phpmyadmin HTTP/1.1" 404 153 "-" "curl/8.4.0"
198.51.100.21 - - [02/Nov/2026:09:22:30 +0900] "GET /board/99 HTTP/1.1" 404 153 "-" "Mozilla/5.0"
198.51.100.34 - - [02/Nov/2026:09:25:02 +0900] "GET /report HTTP/1.1" 500 177 "-" "Mozilla/5.0"
192.0.2.15 - - [02/Nov/2026:09:26:44 +0900] "GET /search?q=network HTTP/1.1" 200 4010 "-" "Mozilla/5.0"
192.0.2.88 - - [02/Nov/2026:09:28:13 +0900] "GET / HTTP/1.1" 200 1204 "-" "Mozilla/5.0"
192.0.2.88 - - [02/Nov/2026:09:28:20 +0900] "GET /board HTTP/1.1" 200 5410 "-" "Mozilla/5.0"
198.51.100.21 - - [02/Nov/2026:09:31:15 +0900] "GET /board HTTP/1.1" 301 169 "-" "Mozilla/5.0"
198.51.100.21 - - [02/Nov/2026:09:31:40 +0900] "GET /board/5 HTTP/1.1
198.51.100.77 - - [02/Nov/2026:09:33:51 +0900] "GET /admin HTTP/1.1" 403 287 "-" "Mozilla/5.0"
192.0.2.88 - - [02/Nov/2026:09:35:02 +0900] "GET /logout HTTP/1.1" 302 0 "-" "Mozilla/5.0"
198.51.100.21 - - [02/Nov/2026:09:36:10 +0900] "GET /board/12 HTTP/1.1" 200 2210 "-" "Mozilla/5.0"
-
```
