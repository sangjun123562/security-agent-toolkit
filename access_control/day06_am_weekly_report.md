# 11/2(월) 오전 · 3과목 접근통제 ⑥ — 점검 체크리스트 · 로그 집계 · 주간 보고서 — 실습

지난 금요일(10/30(금))까지 권한을 점검하고, 회수하고, 요청마다 조건을 확인하는 서버를 만들었습니다. 오늘 오전에는 그 결과가 **잘 지켜지고 있는지 매주 같은 기준으로 확인하고 한 장으로 보고**합니다. 3과목의 마지막 수업입니다.

- **2교시**: 퇴사자 · 만료 예외 · 부서와 역할, 세 가지를 **점검 체크리스트**로 점검해 통과와 실패를 가린다.
- **3교시**: 서버가 남기는 **요청 로그**를 집계해 허용과 거부, 거부율, 거부 사유를 구하고 **경고 기준**과 비교한 뒤, 2교시 점검 결과와 합친 **주간 보고서** 파일을 만듭니다.
- **4교시**: **3과목 총정리.** 새로 배우는 것 없이, 상황 8개마다 원인과 고치는 방법을 내 말로 정리합니다.

오늘은 오전 2 · 3 · 4교시이고, 오후부터는 4과목(이상탐지)을 시작합니다. 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다. 교시마다 문제는 하나입니다.

오늘 파일은 앞 수업 파일을 불러오지 않습니다. 필요한 데이터 세 개(점검할 데이터 · 경고 기준 · 일주일 치 샘플 로그)는 아래 「시작하기」에서 붙여 넣습니다. 그래서 앞 날에 결석했어도 오늘 수업을 따라올 수 있습니다.

- 샘플 로그(`week_log.jsonl`)는 금요일 서버가 남긴 `server_log.jsonl` 과 **같은 모양**입니다.
  - 금요일 로그는 8줄뿐이라 일주일 치로 쓰기에 모자라서, 같은 모양으로 40줄을 만든 샘플을 씁니다.
  - 10/26(월)부터 11/1(일)까지 서버가 받은 요청이라고 생각하고 읽습니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치를 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python --version
   ```
   - 맥북은 `python` 을 `python3` 로 바꿔 칩니다. `config` 폴더가 없어서 `ls config` 가 오류를 내도 괜찮습니다(오늘 쓸 json 파일은 6번에서 만듭니다).
3. **오늘 받은 파일 두 개를 `access_control` 폴더에 둡니다.** 이미 있으면 건너뜁니다. `다운로드` 폴더에서 VS Code 왼쪽의 그 폴더 위로 끌어다 놓습니다(안 되면 파일을 열어 **File › Save As…** 로 저장).
   - `day06_am_weekly_report.md` (이 파일) — 오전 실습 안내. 읽기만 합니다.
   - `day06_am_report.md` — **오전 보고서.** 2 · 3 · 4교시 답을 여기에 적습니다.
4. **[VS Code]** 안내 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다. 보고서 `day06_am_report.md` 는 오른쪽 클릭 › **Open to the Side** 로 옆에 열고, 맨 위 제목 `(이름 · 2026-11-02(월))` 의 `이름` 만 내 이름으로 바꿉니다.
5. 문제는 **할 일 → 순서**대로 하고, `[창 이름]` 이 지금 쓸 창입니다. 코드를 채울 때는 주석이 말하는 일을 하면 몇 줄이든 맞고, 막히면 맨 아래 「정답」을 봅니다.
6. **[VS Code 또는 터미널]** 오늘 쓸 데이터 파일 세 개를 만들어 아래 내용을 그대로 붙여 넣습니다. VS Code 에서는 `access_control` 폴더를 선택해 **새 파일**(New File)을 누르고(`config/…` 이름은 `config` 폴더 안에 만들어집니다. 이미 `config` 폴더가 있으면 그 안에 만듭니다), 터미널에서는 `config` 폴더가 없으면 `mkdir config` 후 `touch 이름` 으로 만들어 VS Code 에서 열어 붙여 넣습니다.

**`config/week_state.json`** — 점검할 데이터입니다. 사용자 여섯 명 · 역할별 부서 · 예외 네 개가 들어 있습니다.

```json
{
  "users": {
    "seoyeon": {"dept": "영업", "role": "sales", "employed": true},
    "junho": {"dept": "영업", "role": "finance", "employed": true},
    "gaeun": {"dept": "IT", "role": "account_admin", "employed": true},
    "dami": {"dept": "영업", "role": "sales", "employed": false},
    "batch-night": {"dept": "시스템", "role": "batch", "employed": true},
    "tester": {"dept": "인턴", "role": "intern", "employed": true}
  },
  "role_dept": {
    "sales": "영업",
    "finance": "재무",
    "account_admin": "IT",
    "batch": "시스템",
    "intern": "인턴"
  },
  "exceptions": [
    {"id": 3, "user": "dami", "permission": "SALES:QUERY", "expires": "2026-11-03 18:00"},
    {"id": 6, "user": "seoyeon", "permission": "SETTLE:QUERY", "expires": "2026-11-06 18:00"},
    {"id": 7, "user": "tester", "permission": "SALES:QUERY", "expires": "2026-11-04 09:00"},
    {"id": 8, "user": "gaeun", "permission": "SETTLE:QUERY", "expires": "2026-11-13 12:00"}
  ]
}
```

**`config/alert.json`** — 경고 기준입니다. 거부율이 0.3(30%) 이상이면 경고이고, 사용자 한 명이 4번 이상 거부되면 눈여겨봅니다.

```json
{"deny_rate_limit": 0.3, "user_denied_limit": 4}
```

**`week_log.jsonl`** — 일주일 치 샘플 로그입니다. 한 줄이 요청 한 개이고 JSON 한 줄입니다. `access_control` 폴더 바로 아래에 만듭니다.

```
{"time": "2026-10-26T09:10", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-26T09:40", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-26T10:05", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-26T10:30", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-26T14:20", "user": "tester", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "역할이 없음"}
{"time": "2026-10-26T23:10", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "external", "allowed": false, "reason": "업무 시간 밖"}
{"time": "2026-10-27T09:05", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-27T10:15", "user": "junho", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-27T11:00", "user": "dami", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-10-27T13:45", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-10-27T15:30", "user": "batch-night", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-27T22:40", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "external", "allowed": false, "reason": "업무 시간 밖"}
{"time": "2026-10-28T09:20", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-28T10:00", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-28T10:50", "user": "dami", "permission": "SALES:QUERY", "network": "vpn", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-10-28T14:10", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-28T16:25", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-28T20:30", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": false, "reason": "업무 시간 밖"}
{"time": "2026-10-29T09:00", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-29T09:35", "user": "junho", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-29T10:20", "user": "dami", "permission": "SALES:QUERY", "network": "external", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-10-29T11:10", "user": "tester", "permission": "SETTLE:QUERY", "network": "office", "allowed": false, "reason": "역할이 없음"}
{"time": "2026-10-29T13:00", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-10-29T15:45", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-29T18:00", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "office", "allowed": false, "reason": "업무 시간 밖"}
{"time": "2026-10-30T09:15", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-30T10:00", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-30T10:30", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "external", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-10-30T11:20", "user": "batch-night", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-30T14:00", "user": "dami", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "퇴사한 계정"}
{"time": "2026-10-30T19:30", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-31T09:10", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-31T09:50", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-31T10:40", "user": "junho", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-31T13:15", "user": "tester", "permission": "SALES:QUERY", "network": "office", "allowed": false, "reason": "역할이 없음"}
{"time": "2026-10-31T15:00", "user": "seoyeon", "permission": "SALES:CHANGE", "network": "external", "allowed": false, "reason": "허용되지 않은 접속 위치"}
{"time": "2026-10-31T17:20", "user": "batch-night", "permission": "SETTLE:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-10-31T19:50", "user": "junho", "permission": "SETTLE:QUERY", "network": "vpn", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-01T09:30", "user": "seoyeon", "permission": "SALES:QUERY", "network": "office", "allowed": true, "reason": "역할 권한"}
{"time": "2026-11-01T10:10", "user": "gaeun", "permission": "ACCOUNT:CHANGE", "network": "vpn", "allowed": false, "reason": "허용되지 않은 접속 위치"}
```

7. **[터미널]** 세 파일이 정상인지 확인합니다. `pwd` 결과가 `access_control` 로 끝나야 합니다(맥북은 `python3`).
   ```bash
   python -m json.tool config/week_state.json
   python -m json.tool config/alert.json
   python -c "print(len(open('week_log.jsonl', encoding='utf-8').read().splitlines()))"
   ```
   - 앞의 두 명령은 내용이 다시 출력되면 정상입니다(한글이 `\uc601…` 로 보여도 정상). 마지막은 `40` 이 나와야 합니다. 다르면 줄이 빠졌거나 빈 줄이 끼어든 것이니 위 내용과 비교해 다시 셉니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `access_control` 로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다.
  - `ModuleNotFoundError` · `FileNotFoundError`: 위치나 파일 이름이 틀렸습니다.
  - `JSONDecodeError`: 붙여 넣다가 쉼표나 괄호가 빠졌습니다. `python -m json.tool 파일이름` 으로 어느 줄인지 봅니다.
  - `IndentationError` · `NameError`: 직접 쓴 줄의 들여쓰기가 틀렸거나 빠뜨린 줄이 있습니다.
- AI 에게 물을 때는 운영체제와 터미널(예: Windows Git Bash), 친 명령 한 줄, 오류 전체를 함께 붙여 넣습니다. `.env` 내용이나 API 키가 보이면 지우고 붙여 넣습니다.
- AI 가 알려 준 명령은 뜻을 읽고 치고, `rm` · `del` 처럼 지우는 명령은 뜻을 되물은 뒤에 칩니다. 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다(맥북은 `python3`). **앞 수업의 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 점검 체크리스트로 어긋난 곳 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지:
> 「금요일에 회수를 마쳤는데, 월요일 아침이 되면 다시 불안합니다. 주말 사이에 퇴사 처리가 된 사람이 있는지, 만료 시각이 지났는데 남아 있는 예외가 있는지, 부서를 옮겼는데 역할은 그대로인 사람이 있는지를 저는 사용자 파일과 예외 파일을 열어 눈으로 맞춰 봅니다. 사용자가 여섯 명, 예외가 네 개뿐인데도 오래 걸립니다. 지난달에는 부서를 옮긴 사람의 역할 확인을 빠뜨려 감사팀에서 지적을 받았고, 회사가 커지면 이 방식은 쓸 수 없습니다.
>
> 퇴사자 계정 · 만료 예외 · 부서와 역할, 이 세 가지를 매주 같은 순서로 점검해서 걸린 사용자 이름이나 예외 번호를 알려 주세요. 점검은 찾기만 하고, 권한을 바로 지우지는 않습니다.」
> - **왜 중요한가**: 회수를 한 번 해도 사람은 계속 퇴사하고 부서를 옮깁니다. 눈으로 맞추면 오래 걸리고 한 명을 빠뜨릴 수 있는데, 코드가 같은 기준으로 한 번에 점검하면 걸린 대상의 이름이 바로 나옵니다. 이 결과는 3교시에서 만드는 주간 보고서에 그대로 들어갑니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 앞 수업 흐름 복습

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 날짜 | 한 일 | 오늘 이어지는 것 |
|---|---|---|
| 10/29(목) | 현황 리스트를 만들고, 규칙(퇴사 · 만료)과 사용 이력으로 안 쓰는 권한 후보를 찾고, 회수 제외를 가려냄 | 오늘 점검 세 가지 중 퇴사자 · 만료 예외 점검의 출발 |
| 10/30(금) 오전 | 회수 대상을 계획 → 승인 → 실행 순서로 회수하고 이력을 남김 | 회수한 뒤에도 생기는 어긋남을 매주 다시 점검 |
| 10/30(금) 오후 | 업무 시간 · 접속 위치 조건을 판정에 더하고, 판정을 서버로 열어 요청마다 `server_log.jsonl` 에 한 줄씩 남김 | 3교시 로그 집계의 입력. 오늘은 같은 모양의 일주일 치 샘플 40줄을 씁니다 |

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 권한 점검은 한 번 하고 끝내는 일이 아니라 **주기마다 같은 기준으로 반복**하는 일입니다.
2. 반복하려면 점검할 것을 미리 정해 둡니다. 이것을 **점검 체크리스트**라고 부릅니다.
   - 점검 한 가지는 문제가 있는 사용자나 예외를 **리스트로 모읍니다.**
   - 리스트가 비어 있으면 **통과**, 하나라도 있으면 **실패**입니다.
3. 오늘은 점검 세 가지를 함수로 만듭니다. 점검할 데이터는 `config/week_state.json` 하나에 모아 두었습니다.

### 📖 2.1 점검할 데이터와 세 가지 점검

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`config/week_state.json` 은 세 부분으로 이루어집니다.

| 키 | 담긴 것 | 값의 예 |
|---|---|---|
| `users` | 사용자 이름 → 사용자 항목(부서 · 역할 · 재직 여부) | `"dami": {"dept": "영업", "role": "sales", "employed": false}` |
| `role_dept` | 역할 → 그 역할이 속해야 하는 부서 | `"finance": "재무"` |
| `exceptions` | 예외 리스트(번호 · 사용자 · 권한 · 만료 시각) | `{"id": 3, "user": "dami", "permission": "SALES:QUERY", "expires": "2026-11-03 18:00"}` |

점검 세 가지는 아래와 같습니다.

| 점검 | 문제로 보는 경우 | 모으는 것 |
|---|---|---|
| 퇴사자 계정 점검 | `employed` 가 `false`(퇴사)인데 `users` 에 계정이 남아 있다 | 사용자 이름 |
| 만료 예외 점검 | 만료 시각이 지금과 같거나 지났는데 예외가 남아 있다 | 예외 번호(`id`) |
| 부서와 역할 점검 | 사용자의 부서가 그 사용자 역할이 속해야 하는 부서와 다르다 | 사용자 이름 |

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `check_employed` | 사용자 딕셔너리 | 퇴사한(`employed` 가 `false`) 사용자 이름의 리스트 |
| `check_expired` | 예외 리스트, 지금 시각 | 만료 시각이 지금과 같거나 지난 예외 번호의 리스트 |
| `check_dept` | 사용자 딕셔너리, 역할별 부서 딕셔너리 | 부서가 역할의 부서와 다른 사용자 이름의 리스트 |
| `run_checklist` | 읽은 데이터, 지금 시각 | 점검 이름과 문제 리스트를 묶은 딕셔너리의 리스트(미리 채움) |

- 점검하는 시각은 `2026-11-02 10:00` 으로 고정합니다.
- `for name, info in users.items():` 는 딕셔너리의 키(사용자 이름)와 값(사용자 항목)을 한꺼번에 꺼냅니다.
- JSON 의 `true` · `false` 는 파이썬으로 읽으면 `True` · `False` 가 됩니다.
- **직접 쓰는 곳은 세 함수**(번호 1 ~ 8)입니다. 함수마다 2 ~ 3줄만 쓰고, 나머지는 미리 채웠습니다.
  - `check_employed`(1 · 2번): 퇴사한 사용자의 이름을 모읍니다.
  - `check_expired`(3 ~ 5번): 만료된 예외의 번호를 모읍니다.
  - `check_dept`(6 ~ 8번): 부서가 다른 사용자의 이름을 모읍니다.
- **미리 채운 것**: `load_state`(파일 읽기)와 `run_checklist`(세 점검을 묶기)입니다.

```
+------------------------------------------------+
| load_state 가 config/week_state.json 을 읽는다 |
+------------------------------------------------+
   |
   v
+-----------------------------------------------------+
| run_checklist 가 점검 세 가지를 차례로 호출한다     |
+-----------------------------------------------------+
   |
   +--> check_employed(users)          --> 퇴사한 사용자 이름 리스트
   |
   +--> check_expired(exceptions, now) --> 만료된 예외 번호 리스트
   |
   +--> check_dept(users, role_dept)   --> 부서가 다른 사용자 이름 리스트
   |
   v
+------------------------------------------------------------+
| 점검마다 {"name": 점검 이름, "problems": 리스트} 로 묶는다 |
+------------------------------------------------------------+
   |
   v
+----------------------------------------------+
| 리스트가 비었으면 통과, 하나라도 있으면 실패 |
+----------------------------------------------+
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 퇴사자 · 만료 예외 · 부서와 역할을 점검해 통과와 실패 가리기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 점검은 사람이 `config/week_state.json` 같은 데이터 파일을 눈으로 읽어야 합니다. 사용자가 늘면 놓치기 쉽고, 지난주와 같은 기준으로 봤는지도 알 수 없습니다.
- **그래서 만드는 것**: `checklist.py` 입니다.
  - 점검 세 가지를 함수로 만들고, 문제가 있는 사용자 이름이나 예외 번호를 리스트로 모읍니다.
  - 예를 들어 dami 는 퇴사했는데 계정이 남아 있으므로 첫째 점검에서 걸립니다.
- **실행하면**: 단계 1은 점검 대상의 수, 단계 2는 점검 세 가지의 통과와 실패, 그리고 문제 리스트를 출력합니다.
- **현업에서는**: 접근 권한 점검도 항목을 정해 두고 주기마다 반복하며, 결과(통과 · 실패와 대상)를 보고서에 남깁니다.

**🎯 할 일**

1. `checklist.py` · `day06_2-1_run.py` 두 파일을 만들고, `checklist.py` 의 `check_employed` · `check_expired` · `check_dept` 에서 직접 쓰는 곳 세 군데를 씁니다.
2. 실행해서 <mark>점검 대상의 수</mark>(단계 1: 점검 대상)와 <mark>점검 세 가지의 결과</mark>(단계 2: 점검 결과)를 읽습니다.

**`checklist.py`**

```python
import json                                                      # JSON 파일을 읽는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 만료 시각 문자열의 형식 (예: 2026-11-03 18:00)


def load_state(path):                                            # 파일 경로를 받는 함수
    """점검할 데이터(사용자 · 역할의 부서 · 예외)를 읽어 딕셔너리로 리턴한다.
    정기 점검을 시작할 때 쓴다.
    """
    with open(path, encoding="utf-8") as json_file:                      # 파일을 연다
        return json.load(json_file)                                      # 읽은 내용을 바로 리턴한다


def check_employed(users):                                       # 사용자 딕셔너리를 받는 함수
    """퇴사했는데 계정이 남아 있는 사용자 이름 리스트를 리턴한다.
    정기 점검에서 퇴사자 계정을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. info["employed"] 가 거짓이면 (if not …)
        # 2.   name 을 problems 에 추가한다
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def check_expired(exceptions, now):                              # 예외 리스트와 지금 시각(datetime)을 받는 함수
    """만료 시각이 지났는데 남아 있는 예외의 번호 리스트를 리턴한다.
    정기 점검에서 기간이 끝난 예외를 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 예외 번호를 모을 리스트
    for exception in exceptions:                                       # 예외를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. exception["expires"] 를 TIME_FORMAT 으로 읽어 시각 expires_at 에 담는다 (datetime.strptime)
        # 4. expires_at 이 now 보다 이르거나 같으면 (<=)
        # 5.   exception["id"] 를 problems 에 추가한다
    return problems                                              # 문제가 있는 예외 번호를 리턴한다


def check_dept(users, role_dept):                                # 사용자 딕셔너리와 역할별 부서 딕셔너리를 받는 함수
    """부서가 역할의 부서와 다른 사용자 이름 리스트를 리턴한다.
    정기 점검에서 엉뚱한 부서에 역할이 남은 사람을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. role_dept 에서 info["role"] 의 부서를 찾아 expected_dept 에 담는다
        # 7. expected_dept 가 info["dept"] 와 다르면 (!=)
        # 8.   name 을 problems 에 추가한다
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def run_checklist(state, now):                                   # 읽은 데이터와 지금 시각을 받는 함수
    """점검 세 가지를 실행한다.
    점검 이름과 문제 리스트를 담은 딕셔너리의 리스트를 리턴한다.
    매주 어긋난 곳을 한 번에 찾을 때 쓴다.
    """
    users = state["users"]                                       # 사용자 딕셔너리를 꺼낸다
    exceptions = state["exceptions"]                             # 예외 리스트를 꺼낸다
    role_dept = state["role_dept"]                               # 역할별 부서 딕셔너리를 꺼낸다
    results = []                                                 # 점검 결과를 모을 리스트
    results.append({"name": "퇴사자 계정 점검", "problems": check_employed(users)})            # 첫째 점검 결과를 추가한다
    results.append({"name": "만료 예외 점검", "problems": check_expired(exceptions, now)})     # 둘째 점검 결과를 추가한다
    results.append({"name": "부서와 역할 점검", "problems": check_dept(users, role_dept)})     # 셋째 점검 결과를 추가한다
    return results                                               # 점검 결과 리스트를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다.
  - 세 함수 모두 `for` 안쪽이라 `if` · 변수 줄은 앞에 공백 8개이고, `if` 안쪽 `problems.append(…)` 는 4개 더(12개)입니다.
  - 나머지 줄은 미리 채워 두었으니 그대로 둡니다.
- 3번은 `datetime.strptime(문자열, TIME_FORMAT)` 으로 문자열을 시각으로 바꿉니다. 10/22(목)에 예외의 만료 시각을 읽을 때와 같은 방법입니다.
- 4번의 `<=` 는 「같거나 이전」입니다. 만료 시각 정각도 만료로 봅니다.
- 6번의 `role_dept[info["role"]]` 는 키가 `info["role"]` 인 값을 찾습니다. 사용자의 역할이 `finance` 이면 `"재무"` 가 나옵니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다(파이썬 버전에 따라 뒤에 `after 'for' statement on line …` 가 붙습니다). `for` 아래에 실행할 줄이 아직 없기 때문입니다.

**`day06_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 데이터 파일을 읽고 점검을 실행해 결과를 출력합니다.

```python
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from checklist import TIME_FORMAT, load_state, run_checklist     # 방금 만든 점검 함수를 불러온다

NOW = datetime.strptime("2026-11-02 10:00", TIME_FORMAT)         # 점검하는 시각을 2026-11-02 10:00 으로 고정한다
state = load_state("config/week_state.json")                     # 점검할 데이터 파일을 읽는다
users = state["users"]                                           # 사용자 딕셔너리를 꺼낸다
exceptions = state["exceptions"]                                 # 예외 리스트를 꺼낸다

user_count = len(users)                                          # 사용자가 몇 명인지 센다
exception_count = len(exceptions)                                # 예외가 몇 개인지 센다
print("--- 단계 1: 점검 대상 - 사용자", user_count, "명 · 예외", exception_count, "개")  # 단계 1 시작을 알리는 줄
results = run_checklist(state, NOW)                              # 점검 세 가지를 실행한다
print("--- 단계 2: 점검 결과")                                      # 단계 2 시작을 알리는 줄
for result in results:                                           # 점검 결과를 하나씩 꺼낸다
    name = result["name"]                                        # 점검 이름을 꺼낸다
    problems = result["problems"]                                # 문제가 있는 사용자 · 예외 리스트를 꺼낸다
    if len(problems) == 0:                                       # 문제가 하나도 없으면
        status = "통과"                                           # 통과라고 적는다
    else:                                                        # 문제가 있으면
        status = "실패"                                           # 실패라고 적는다
    print(name, "|", status, "|", problems)                      # 점검 이름 | 결과 | 문제 리스트를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `checklist.py` · `day06_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `checklist.py` 에서 직접 쓰는 곳 세 군데를 씁니다. 2.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day06_2-1_run.py
   ```
4. 출력은 두 단계입니다. 단계 1은 한 줄, 단계 2는 점검 이름 세 줄입니다.
5. **[보고서]** `day06_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 통과한 점검과 실패한 점검, 실패한 점검에서 나온 사용자 이름이나 예외 번호를 적어 주세요.
   - (나) 🔍 만료 예외 점검은 「통과」인데, 예외 3번은 퇴사한 dami 의 예외입니다. 「통과」를 「문제 없음」으로만 읽으면 안 되는 이유와, 이 예외를 볼 때 함께 읽어야 하는 다른 점검을 적어 주세요.
   - (다) 🔍 점검은 junho 가 영업 부서인데 역할은 `finance` 라고 알려 줍니다. 점검 코드가 알려 주는 것과 알려 주지 못하는 것을 구분하고, 이 결과를 받은 담당자가 무엇을 확인해야 하는지, 코드가 바로 권한을 회수하면 안 되는 이유가 무엇인지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 점검할 데이터 읽기 | `state = load_state("config/week_state.json")` (미리 채움) |
| 사용자 이름과 항목 꺼내기 | `for name, info in users.items():` (미리 채움) |
| 퇴사자 찾기 | `if not info["employed"]:` → `problems.append(name)` |
| 만료 예외 찾기 | `datetime.strptime(exception["expires"], TIME_FORMAT)` → `if expires_at <= now:` → `problems.append(exception["id"])` |
| 부서가 다른 사용자 찾기 | `role_dept[info["role"]]` → `if expected_dept != info["dept"]:` → `problems.append(name)` |
| 통과 · 실패 | 문제 리스트가 비었으면 통과, 아니면 실패 |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 서버 로그를 집계하고 주간 보고서 만들기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지:
> 「점검 결과 말고 하나 더 있습니다. 판정 서버는 요청마다 로그를 한 줄 남기는데, 그 로그를 제대로 읽어 본 사람이 없습니다. 지난주에 한 직원이 "자꾸 접근이 거부된다"고 문의했을 때 로그 파일을 열어 그 직원의 거부 횟수를 세는 데만 오래 걸렸습니다. 실제 서버의 일주일 치는 수천 줄이고, 오늘 쓰는 샘플은 40줄입니다.
>
> 일주일 동안 요청이 몇 번 허용되고 몇 번 거부됐는지, 거부 사유는 무엇이 많은지, 같은 사람이 반복해서 거부됐는지를 숫자로 알려 주세요. 거부 비율이 평소보다 높으면 먼저 알 수 있게 기준(예: 30%)을 정해 두고, 기준을 넘으면 「경고」라고 표시해 주세요. 점검 결과와 이 숫자를 합쳐 월요일 회의에 낼 한 장짜리 보고서까지 만들어 주세요.」
> - **왜 중요한가**: 거부가 갑자기 늘면 퇴사자 계정이나 밖에서 들어오는 시도가 늘었다는 신호일 수 있습니다. 로그를 사람이 세면 오래 걸리고 기준이 사람마다 달라집니다. 코드가 같은 기준으로 세고 경고를 붙이면 담당자는 경고가 붙은 곳부터 볼 수 있습니다. 경고는 공격이 확정됐다는 뜻이 아니라 먼저 살펴볼 곳이라는 뜻입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 서버 로그는 한 줄씩 쌓이기만 하고, 그대로는 「이번 주에 무슨 일이 있었나」를 알 수 없습니다.
2. 그래서 로그를 읽어 **세고(집계), 비율을 구하고, 기준과 비교**합니다.
   - 거부율 = 거부된 요청 수 ÷ 전체 요청 수
   - 거부율이 **경고 기준** 이상이면 경고입니다. 기준은 코드가 아니라 `config/alert.json` 에 둡니다.
3. 경고는 「살펴볼 필요가 있다」는 표시이고, 공격이 있었다는 뜻이 아닙니다.

### 📖 3.1 로그 한 줄과 집계 함수

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`week_log.jsonl` 의 한 줄은 요청 한 개이고, 아래 여섯 키로 이루어집니다.

| 키 | 뜻 | 값의 예 |
|---|---|---|
| `time` | 요청한 시각 | `"2026-10-26T09:10"` |
| `user` | 요청한 사용자 | `"seoyeon"` |
| `permission` | 요청한 권한(자원:행위) | `"SALES:QUERY"` |
| `network` | 접속 위치 | `"office"` |
| `allowed` | 허용 여부 | `true` · `false` |
| `reason` | 허용 또는 거부 이유 | `"퇴사한 계정"` |

- 이 샘플 로그의 허용 이유는 `역할 권한` 하나이고, 거부 이유는 네 가지입니다.
  - `퇴사한 계정` · `역할이 없음`(사용자의 역할이 역할 파일에 없음) · `업무 시간 밖` · `허용되지 않은 접속 위치`
**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `read_log` | 로그 파일 경로 | 요청 딕셔너리의 리스트 |
| `count_by` | 요청 리스트, 센 기준(키 이름) | `{값: 횟수}` 딕셔너리 |
| `filter_denied` | 요청 리스트 | 거부된 요청의 리스트 |
| `deny_rate` | 요청 리스트 | 거부율(0 ~ 1). 요청이 0개이면 0.0 |
| `find_heavy_users` | 사용자별 거부 횟수 딕셔너리, 기준 횟수 | 기준 이상 거부된 사용자 이름의 리스트 |

- **직접 쓰는 곳은 다섯 함수**(번호 1 ~ 11)입니다. 판단이 필요한 함수마다 2 ~ 3줄만 쓰고, 나머지는 미리 채웠습니다.
  - `read_log`(1 · 2번): 로그 파일의 JSON 한 줄을 딕셔너리로 바꿔 리스트에 추가합니다.
  - `count_by`(3 ~ 5번): 키의 값별로 횟수를 셉니다. 예를 들어 사용자별 · 사유별 횟수입니다.
  - `filter_denied`(6 · 7번): 거부된 요청만 모읍니다.
  - `deny_rate`(8 · 9번): 거부율을 구합니다. 요청이 하나도 없는 경우를 먼저 처리합니다.
  - `find_heavy_users`(10 · 11번): 거부 횟수가 기준 이상인 사용자를 찾습니다.
- **미리 채운 것**: 반복 구조, `deny_rate` 의 나눗셈 줄, 마지막 `return` 입니다.

```
+----------------------------------------+
| week_log.jsonl (한 줄이 요청 한 개)    |
+----------------------------------------+
   |
   v
+--------------------------------------------------+
| read_log: JSON 한 줄씩 읽어 요청 리스트로 만든다 |
+--------------------------------------------------+
   |
   +--> filter_denied: 거부된 요청만 모은다
   |       |
   |       +--> count_by(denied, "reason") --> 거부 사유별 횟수
   |       |
   |       +--> count_by(denied, "user")   --> 사용자별 거부 횟수
   |                |
   |                v
   |        find_heavy_users: 기준 횟수 이상인 사용자
   |
   +--> deny_rate: 거부 수 / 전체 수
            |
            v
   +-------------------------------------+
   | 거부율 >= 경고 기준 이면 경고         |
   +-------------------------------------+
```

**🐍 문법 상자 — JSON 한 줄 읽기 · 퍼센트 만들기 · 값별로 세기**

**① `json.loads` 는 JSON 문자열을 딕셔너리로 바꿉니다**

```python
import json                                                      # JSON 문자열을 딕셔너리로 바꾸는 모듈을 불러온다

line = '{"user": "dami", "allowed": false}\n'                     # 로그 파일에서 읽은 한 줄(끝에 줄바꿈 문자가 붙어 있다)
entry = json.loads(line)                                         # JSON 문자열을 딕셔너리로 바꾼다
print(entry["user"], entry["allowed"])                           # 사용자와 허용 여부를 출력한다
```

실행 결과:

```
dami False
```

- JSON 의 `false` 가 파이썬에서는 `False` 가 됩니다.
- 로그 파일을 `for line in log_file:` 로 읽으면 한 줄씩 꺼내지고, 각 줄을 `json.loads(line)` 으로 바꾸면 요청 한 개가 딕셔너리가 됩니다.

**② `round(숫자)` 는 소수를 가까운 정수로 만듭니다**

```python
rate = 16 / 40                                                   # 거부 16개를 전체 40개로 나눈 비율
print(rate)                                                      # 비율 그대로 출력한다

percent = round(rate * 100)                                      # 100 을 곱해 가까운 정수로 반올림한다
print(percent)                                                   # 퍼센트 숫자를 출력한다
```

실행 결과:

```
0.4
40
```

숫자 뒤에 `%` 를 붙여 문자열로 만들려면 f-문자열을 씁니다.

```python
percent = 40                                                     # 위에서 구한 퍼센트 숫자
percent_text = f"{percent}%"                                     # 숫자 뒤에 % 를 붙인 문자열을 만든다
print(percent_text)                                              # 만든 문자열을 출력한다
```

실행 결과:

```
40%
```

- 거부율은 0 ~ 1 사이 소수로 계산하고, 보여 줄 때만 100 을 곱해 퍼센트로 바꿉니다.
- 경고 기준과 비교할 때는 퍼센트가 아니라 소수(`rate >= limit`)를 그대로 비교합니다.

**③ `counts.get(값, 0)` 으로 값별 횟수를 셉니다**

```python
names = ["dami", "gaeun", "dami"]                               # 거부된 사용자 이름 리스트
counts = {}                                                      # 값별 횟수를 담을 딕셔너리

for name in names:                                               # 이름을 하나씩 꺼낸다
    old_count = counts.get(name, 0)                              # 지금까지 센 횟수를 꺼낸다(처음이면 0)
    counts[name] = old_count + 1                                 # 횟수를 1 늘려 넣는다

print(counts)                                                    # 이름별 횟수를 출력한다
junho_count = counts.get("junho", 0)                             # 없는 이름은 0 을 준다
print(junho_count)                                               # 없는 이름의 횟수를 출력한다
```

실행 결과:

```
{'dami': 2, 'gaeun': 1}
0
```

- `counts.get(name, 0)` 은 `name` 키의 값을 꺼내고, 키가 아직 없으면 0 을 줍니다. 처음 나온 이름도 같은 두 줄로 셀 수 있습니다.
- `count_by` 는 이 두 줄을 `entry[key]` 로 꺼낸 값에 그대로 씁니다.

**④ `"\n".join(리스트)` 는 리스트의 문자열을 줄바꿈으로 이어 붙입니다**

```python
lines = ["# 제목", "- 첫째 줄", "- 둘째 줄"]                          # 보고서 줄을 모은 리스트
text = "\n".join(lines)                                          # 줄바꿈 문자로 이어 붙여 문자열 하나로 만든다
print(text)                                                      # 이어 붙인 문자열을 출력한다
```

실행 결과:

```
# 제목
- 첫째 줄
- 둘째 줄
```

- `"\n"` 은 줄바꿈 문자 하나이고, 출력하면 다음 줄로 넘어갑니다.
- `weekly_report.py` 는 마지막에 `"\n".join(lines) + "\n"` 을 리턴합니다. 뒤의 `+ "\n"` 은 파일 맨 끝도 줄바꿈으로 끝나게 하려고 붙입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 서버 로그를 집계해 거부율과 경고 여부 구하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 로그 40줄을 사람이 하나씩 읽고 세야 합니다. 거부가 늘었는지, 누가 반복해서 거부됐는지 확인하려면 시간이 오래 걸립니다.
- **그래서 만드는 것**: `log_summary.py` 입니다.
  - 로그를 읽고, 거부된 요청을 모으고, 사유별 · 사용자별로 세고, 거부율을 구합니다.
  - 거부율이 경고 기준 이상이면 경고로 표시합니다.
  - 이어서 2교시 점검 결과와 합친 주간 보고서를 만듭니다. 보고서를 만드는 `weekly_report.py` 는 붙여 넣고 실행만 합니다.
- **실행하면**: 단계 1은 허용 · 거부 · 거부율, 단계 2는 거부 사유별 횟수, 단계 3은 경고 여부와 거부가 많은 사용자를 출력합니다. 보고서 실행은 모은 양, 저장한 파일 이름, 보고서 내용을 출력합니다.
- **현업에서는**: 로그를 집계하는 일은 관제의 기본이고, 경고 기준은 코드에 직접 적지 않고 설정 파일에 두어 운영하면서 바꿉니다.

**🎯 할 일**

1. `log_summary.py` · `day06_3-1_run.py` 두 파일을 만들고, `log_summary.py` 의 `read_log` · `count_by` · `filter_denied` · `deny_rate` · `find_heavy_users` 에서 직접 쓰는 곳 다섯 군데를 씁니다.
2. 실행해서 <mark>허용 · 거부 · 거부율</mark>(단계 1: 집계), <mark>거부 사유별 횟수</mark>(단계 2), <mark>경고 여부</mark>(단계 3: 경고 기준)를 읽습니다.
3. `weekly_report.py` · `day06_3-2_run.py` 를 붙여 넣어 실행하고, 2교시 점검 결과와 합친 <mark>주간 보고서</mark>(단계 3: 저장한 보고서 내용)를 읽습니다. 이 두 파일은 직접 쓰는 곳이 없습니다. 3교시 문제는 3-1 하나이고, `day06_3-2_run.py` 는 같은 문제의 두 번째 실행 파일입니다. 보고서 (가)의 「단계 3」은 `day06_3-1_run.py` 에서는 경고 여부, `day06_3-2_run.py` 에서는 저장한 보고서 내용입니다.

**`log_summary.py`**

```python
import json                                                      # JSON 문자열을 딕셔너리로 바꾸는 모듈을 불러온다


def read_log(path):                                              # 로그 파일 경로를 받는 함수
    """서버 로그 파일을 한 줄씩 읽어 요청 딕셔너리 리스트로 만든다.
    주간 로그를 집계하기 전에 파일을 읽을 때 쓴다.
    """
    entries = []                                                 # 요청 딕셔너리를 모을 리스트
    with open(path, encoding="utf-8") as log_file:                      # 파일을 연다
        for line in log_file:                                           # 파일에서 한 줄씩 꺼낸다
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 1. line 의 JSON 문자열을 json.loads 로 딕셔너리 entry 로 바꾼다
            # 2. entry 를 entries 에 추가한다
    return entries                                               # 요청 리스트를 리턴한다


def count_by(entries, key):                                      # 요청 리스트와 센 기준(키 이름)을 받는 함수
    """요청을 key 의 값별로 세어 {값: 횟수} 딕셔너리를 리턴한다.
    사용자별 · 이유별로 몇 번인지 알고 싶을 때 쓴다.
    예: count_by(entries, "user")
    """
    counts = {}                                                  # 값별 횟수를 담을 딕셔너리
    for entry in entries:                                        # 요청을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. entry[key] 를 value 에 담는다
        # 4. counts 에서 value 의 지금 횟수를 old_count 에 담는다 (없으면 0: counts.get(value, 0))
        # 5. counts[value] 에 old_count + 1 을 넣는다
    return counts                                                # 값별 횟수를 리턴한다


def filter_denied(entries):                                      # 요청 리스트를 받는 함수
    """거부된 요청만 모아 리스트로 리턴한다.
    거부 사유와 사용자를 따로 볼 때 쓴다.
    """
    denied = []                                                  # 거부된 요청을 모을 리스트
    for entry in entries:                                        # 요청을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. entry["allowed"] 가 거짓이면 (if not …)
        # 7.   entry 를 denied 에 추가한다
    return denied                                                # 거부된 요청 리스트를 리턴한다


def deny_rate(entries):                                          # 요청 리스트를 받는 함수
    """전체 요청 중 거부된 요청의 비율(0 ~ 1)을 리턴한다.
    주간 보고서에서 거부율을 구할 때 쓰며, 요청이 없으면 0.0 이다.
    """
    total = len(entries)                                         # 전체 요청 수
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. total 이 0 이면 (==)
    # 9.   0.0 을 리턴한다 (0 으로 나눌 수 없으므로)
    denied_entries = filter_denied(entries)                      # 거부된 요청 리스트
    denied = len(denied_entries)                                 # 거부된 요청 수
    return denied / total                                        # 거부 수를 전체 수로 나눈 비율을 리턴한다


def find_heavy_users(denied_counts, limit):                      # 사용자별 거부 횟수 딕셔너리와 기준 횟수를 받는 함수
    """거부 횟수가 limit 이상인 사용자 이름 리스트를 리턴한다.
    거부가 한 사람에게 몰렸는지 확인할 때 쓴다.
    """
    heavy = []                                                   # 기준에 걸린 사용자 이름을 모을 리스트
    for user, count in denied_counts.items():                    # 사용자 이름과 거부 횟수를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 10. count 가 limit 이상이면 (>=)
        # 11.   user 를 heavy 에 추가한다
    return heavy                                                 # 기준에 걸린 사용자 이름을 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다.
  - `read_log`(1 · 2번): `for line in log_file:` 안쪽이라 앞에 공백 12개입니다.
  - `count_by`(3 ~ 5번) · `filter_denied`(6번) · `find_heavy_users`(10번): `for` 안쪽이라 공백 8개이고, `if` 안쪽(7번 · 11번)은 4개 더(12개)입니다.
  - `deny_rate`(8 · 9번): 함수 안이라 공백 4개이고, `if` 안쪽 `return`(9번)은 8개입니다.
- 4번의 `counts.get(value, 0)` 은 문법 상자 ③의 `get` 과 같습니다. 처음 나온 값은 0 에서 시작합니다.
- 8 · 9번은 요청이 하나도 없을 때 0 으로 나누는 오류를 막는 줄입니다. 로그가 비는 경우의 결과는 문제 아래 정답에서 읽습니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다. 다만 `deny_rate` 의 8 · 9번만 비워 두면 오류가 나지 않습니다. 오늘 로그는 비어 있지 않아서 그렇고, 로그가 빈 날에만 문제가 드러납니다.

**`day06_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 샘플 로그를 집계해 세 단계로 출력합니다.

```python
import json                                                      # 경고 기준 파일을 읽는 데 쓴다
from log_summary import read_log, count_by, filter_denied, deny_rate, find_heavy_users   # 방금 만든 집계 함수를 불러온다

LOG_PATH = "week_log.jsonl"                                      # 집계할 로그 파일 이름
with open("config/alert.json", encoding="utf-8") as alert_file:           # 경고 기준 파일을 연다
    ALERT = json.load(alert_file)                                         # 경고 기준 딕셔너리로 읽는다

entries = read_log(LOG_PATH)                                     # 로그를 읽어 요청 리스트로 만든다
denied = filter_denied(entries)                                  # 거부된 요청만 모은다
rate = deny_rate(entries)                                        # 거부율(0 ~ 1)을 구한다
percent = round(rate * 100)                                      # 거부율을 퍼센트 숫자로 바꾼다
limit = ALERT["deny_rate_limit"]                                 # 거부율 경고 기준(0 ~ 1)
limit_percent = round(limit * 100)                               # 경고 기준을 퍼센트 숫자로 바꾼다
user_limit = ALERT["user_denied_limit"]                          # 사용자별 거부 횟수 기준

entry_count = len(entries)                                       # 요청이 모두 몇 건인지 센다
print("--- 단계 1: 집계 - 요청", entry_count, "건")              # 단계 1 시작을 알리는 줄
denied_count = len(denied)                                       # 거부된 요청이 몇 건인지 센다
allowed_count = entry_count - denied_count                       # 허용된 요청 수
print("허용", allowed_count, "· 거부", denied_count, "· 거부율", f"{percent}%")  # 허용 · 거부 · 거부율을 출력한다
print("--- 단계 2: 거부 사유별")                                    # 단계 2 시작을 알리는 줄
reason_counts = count_by(denied, "reason")                       # 거부된 요청을 사유별로 센다
for reason, count in reason_counts.items():                      # 사유와 횟수를 하나씩 꺼낸다
    print(reason, count)                                         # 거부 사유와 횟수를 출력한다
print("--- 단계 3: 경고 기준")                                      # 단계 3 시작을 알리는 줄
if rate >= limit:                                                # 거부율이 기준 이상이면
    print(f"거부율 {percent}% >= 기준 {limit_percent}% -> 경고")    # 경고라고 출력한다
else:                                                            # 기준보다 낮으면
    print(f"거부율 {percent}% < 기준 {limit_percent}% -> 경고 없음")   # 경고 없음이라고 출력한다
user_counts = count_by(denied, "user")                           # 거부된 요청을 사용자별로 센다
heavy = find_heavy_users(user_counts, user_limit)                # 기준 이상 거부된 사용자를 찾는다
print("거부", user_limit, "번 이상 사용자:", heavy)                  # 사용자 이름을 출력한다
```

**`weekly_report.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 점검 결과와 로그 집계를 합쳐 네 절의 보고서 문자열을 만들고, 날짜가 들어간 `.md` 파일로 저장합니다.

```python
from log_summary import count_by, filter_denied, deny_rate, find_heavy_users   # 3교시에 만든 집계 함수를 불러온다


def build_report(results, entries, alert, today):                # 점검 결과 · 요청 리스트 · 경고 기준 · 날짜 문자열을 받는 함수
    """점검 결과와 로그 집계를 합쳐 주간 보고서 문자열을 만든다.
    매주 정기 보고서를 만들 때 쓴다.
    """
    denied = filter_denied(entries)                              # 거부된 요청만 모은다
    total = len(entries)                                         # 전체 요청 수
    denied_count = len(denied)                                   # 거부된 요청 수
    allowed_count = total - denied_count                         # 허용된 요청 수
    rate = deny_rate(entries)                                    # 거부율(0 ~ 1)을 구한다
    percent = round(rate * 100)                                  # 거부율을 퍼센트 숫자로 바꾼다
    limit = alert["deny_rate_limit"]                             # 거부율 경고 기준(0 ~ 1)
    limit_percent = round(limit * 100)                           # 경고 기준을 퍼센트 숫자로 바꾼다
    status = "경고 없음"                                          # 먼저 경고 없음으로 둔다
    if rate >= limit:                                            # 거부율이 기준 이상이면
        status = "경고"                                           # 경고로 바꾼다
    user_limit = alert["user_denied_limit"]                      # 사용자별 거부 횟수 기준
    user_counts = count_by(denied, "user")                       # 거부된 요청을 사용자별로 센다
    heavy = find_heavy_users(user_counts, user_limit)            # 기준 이상 거부된 사용자를 찾는다

    lines = [f"# 접근통제 주간 보고서 ({today})", ""]            # 보고서 줄을 모을 리스트(제목과 빈 줄로 시작)
    lines.append("## 1. 요청 현황")                                # 첫째 절 제목
    lines.append(f"- 전체 요청: {total}건 (허용 {allowed_count}건 · 거부 {denied_count}건)")   # 요청 수
    lines.append(f"- 거부율: {percent}% (경고 기준 {limit_percent}%) -> {status}")             # 거부율과 경고 여부
    lines.append("")                                             # 빈 줄
    lines.append("## 2. 거부 사유")                                # 둘째 절 제목
    reason_counts = count_by(denied, "reason")                   # 거부된 요청을 사유별로 센다
    for reason, count in reason_counts.items():                  # 사유와 횟수를 하나씩 꺼낸다
        lines.append(f"- {reason}: {count}건")                    # 사유별 횟수를 추가한다
    lines.append("")                                             # 빈 줄
    lines.append("## 3. 점검 결과")                                # 셋째 절 제목
    for result in results:                                       # 점검 결과를 하나씩 꺼낸다
        name = result["name"]                                    # 점검 이름
        problems = result["problems"]                            # 문제가 있는 사용자 · 예외 리스트
        if len(problems) == 0:                                   # 문제가 없으면
            lines.append(f"- {name}: 통과")                       # 통과라고 추가한다
        else:                                                    # 문제가 있으면
            lines.append(f"- {name}: 실패 {problems}")            # 실패와 문제 리스트를 추가한다
    lines.append("")                                             # 빈 줄
    lines.append("## 4. 조치가 필요한 것")                          # 넷째 절 제목
    lines.append(f"- 거부 {user_limit}번 이상 사용자: {heavy}")     # 기준 이상 거부된 사용자
    for result in results:                                       # 점검 결과를 하나씩 꺼낸다
        name = result["name"]                                    # 점검 이름
        problems = result["problems"]                            # 문제가 있는 사용자 · 예외 리스트
        if len(problems) > 0:                                    # 문제가 있으면
            lines.append(f"- 확인: {name} -> {problems}")         # 확인할 것을 추가한다
    return "\n".join(lines) + "\n"                               # 줄들을 줄바꿈으로 이어 붙인 문자열을 리턴한다


def save_report(text, today):                                    # 보고서 문자열과 날짜 문자열을 받는 함수
    """보고서를 날짜가 들어간 .md 파일로 저장하고 파일 이름을 리턴한다.
    주간 보고서를 파일로 남길 때 쓴다.
    """
    file_name = f"access_control_weekly_report_{today}.md"       # 날짜가 들어간 파일 이름을 만든다
    with open(file_name, "w", encoding="utf-8") as report_file:            # 파일을 쓰기 모드("w")로 연다
        report_file.write(text)                                            # 보고서 문자열을 파일에 쓴다
    return file_name                                             # 저장한 파일 이름을 리턴한다
```

- 읽을 곳은 세 곳입니다.
  - `if rate >= limit:` 는 위의 경고 판단과 같은 비교입니다. 거부율은 0 ~ 1 사이 소수이고, 경고 기준도 같은 소수입니다.
  - 보고서 줄은 `lines.append(…)` 로 하나씩 모으고, 마지막에 `"\n".join(lines)` 로 한 문자열로 만듭니다(문법 상자 ④).
  - `save_report` 는 `"w"` 로 열어 새로 씁니다. 로그처럼 계속 덧붙이는 파일은 `"a"` 이고, 매주 새로 만드는 보고서는 `"w"` 입니다. 파일 이름에는 `f"…{today}.md"` 로 날짜를 넣습니다.

**`day06_3-2_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 2교시의 점검 함수와 3교시의 로그 읽기 함수로 데이터를 모아 보고서를 만들고 저장합니다.

```python
import json                                                      # 경고 기준 파일을 읽는 데 쓴다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from checklist import TIME_FORMAT, load_state, run_checklist     # 2교시에 만든 점검 함수를 불러온다
from log_summary import read_log                                 # 3교시에 만든 로그 읽기 함수를 불러온다
from weekly_report import build_report, save_report             # 붙여 넣은 보고서 함수를 불러온다

TODAY = "2026-11-02"                                             # 보고서 날짜
NOW = datetime.strptime(TODAY + " 10:00", TIME_FORMAT)           # 점검하는 시각
with open("config/alert.json", encoding="utf-8") as alert_file:           # 경고 기준 파일을 연다
    ALERT = json.load(alert_file)                                         # 경고 기준 딕셔너리로 읽는다

print("--- 단계 1: 모으기 - 점검 결과와 요청 로그")                    # 단계 1 시작을 알리는 줄
state = load_state("config/week_state.json")                     # 점검할 데이터 파일을 읽는다
results = run_checklist(state, NOW)                              # 점검 세 가지를 실행한다
entries = read_log("week_log.jsonl")                             # 요청 로그를 읽는다
result_count = len(results)                                      # 점검이 몇 가지인지 센다
entry_count = len(entries)                                       # 요청이 몇 건인지 센다
print("점검", result_count, "가지 · 요청", entry_count, "건")    # 모은 양을 출력한다
print("--- 단계 2: 보고서 만들기와 저장")                              # 단계 2 시작을 알리는 줄
text = build_report(results, entries, ALERT, TODAY)              # 보고서 문자열을 만든다
file_name = save_report(text, TODAY)                             # 파일로 저장한다
print("저장한 파일:", file_name)                                    # 저장한 파일 이름을 출력한다
print("--- 단계 3: 저장한 보고서 내용")                                # 단계 3 시작을 알리는 줄
print(text)                                                      # 보고서 내용을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `log_summary.py` · `day06_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `log_summary.py` 에서 직접 쓰는 곳 다섯 군데를 씁니다. 3.1 의 표와 그림, 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day06_3-1_run.py
   ```
4. 출력은 세 단계입니다. 단계 1은 한 줄, 단계 2는 거부 사유 네 줄, 단계 3은 두 줄입니다.
5. **[VS Code 또는 터미널]** 파일 `weekly_report.py` · `day06_3-2_run.py` 를 만들어 위 코드를 붙여 넣고 실행합니다. 2교시의 `checklist.py` 를 불러오므로 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.
   ```bash
   python day06_3-2_run.py
   ls
   ```
   - 단계 3의 보고서가 네 절로 출력되고, `ls` 에 `access_control_weekly_report_2026-11-02.md` 가 보여야 합니다.
6. **[터미널]** 보고서 4절에 나온 거부가 많은 사용자의 요청을 로그에서 직접 찾아 봅니다.
   ```bash
   grep gaeun week_log.jsonl
   grep dami week_log.jsonl
   ```
   - 명령 풀이: `grep 단어 파일` 파일에서 그 단어가 들어간 줄만 보여 줌
7. **[보고서]** `day06_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) `day06_3-1_run.py` 의 출력과 `day06_3-2_run.py` 의 보고서 내용을 붙여 넣고, 허용 · 거부 · 거부율, 경고 여부, 거부 사유 중 가장 많은 것을 적어 주세요.
   - (나) 🔍 보고서 4절에 거부가 4번 이상인 사용자로 gaeun 과 dami 가 나왔습니다. 6번에서 찾은 두 사람의 요청을 비교하고, 같은 조치를 하면 안 되는 이유와 각각 무엇부터 확인해야 하는지 적어 주세요.
   - (다) 🔍 서버가 멈춰서 로그가 빈 주에는 `deny_rate` 가 0.0 을 리턴해 보고서에 「거부율 0%」가 나옵니다. 이 보고서만 보고 「이번 주는 안전했다」고 판단해도 되는지, 보고서에서 함께 확인해야 하는 정보와 그 이유를 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 로그 한 줄을 딕셔너리로 | `entry = json.loads(line)` → `entries.append(entry)` (`read_log` 안) |
| 값별로 세기 | `value = entry[key]` → `old_count = counts.get(value, 0)` → `counts[value] = old_count + 1` |
| 거부된 요청만 모으기 | `if not entry["allowed"]:` → `denied.append(entry)` |
| 거부율 | `if total == 0:` → `return 0.0` 뒤에 `denied / total` |
| 거부가 많은 사용자 | `if count >= limit:` → `heavy.append(user)` |
| 경고 여부 | `rate >= limit` 이면 경고 (소수끼리 비교) |
| 퍼센트로 보여 주기 | `round(rate * 100)` |
| 보고서 줄 모으기 | `lines.append("…")` → `"\n".join(lines)` (`weekly_report.py`, 미리 채움) |
| 파일로 저장 | `open(file_name, "w", encoding="utf-8")` → `report_file.write(text)` (미리 채움) |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 3과목 총정리: 상황마다 원인과 고치는 방법 정리하기</mark>

> 📌 **이번 교시는 새로 배우는 것이 없습니다.** 3과목에서 만든 파일과 함수를 **상황별로 되짚으면서**, 각 상황의 원인과 고치는 방법을 내 말로 정리합니다. 정리한 글이 3과목의 총정리 문서(`day05_retrospective.md`)가 됩니다. 오늘은 6일 차이지만 파일 이름의 `day05` 는 강의계획서에 적힌 3과목 산출물 이름 그대로입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. 코드는 3과목에서 만든 파일에서 가져온 것이라, 앞 수업 파일이 없어도 읽을 수 있습니다.

### 📖 상황을 풀 때 쓰는 틀

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

상황이 생기면 같은 네 단계로 생각합니다.

- **확인**: 로그나 점검 결과로 무슨 일인지 알아봅니다.
- **원인**: 왜 이런 일이 생겼는지 가립니다. 원인은 보통 셋 중 하나입니다.
  - 사람의 일: 사람이 해야 할 일(입사, 퇴사, 부서 이동 등)이 일어났습니다.
  - 데이터 문제: 파일에 있어야 할 것이 없거나 틀려 있습니다.
  - 규칙 문제: 「무엇을 허용하고 무엇에 경고할지」 정해 둔 기준이 비어 있거나 현실과 맞지 않습니다(너무 느슨하거나 너무 엄격합니다). 이 수업에서 기준을 적어 둔 곳은 `conditions.json`(권한마다 몇 시에 어디서 접속하면 허용하는지), `alert.json`(거부율이 얼마 이상이면 경고하는지), 점검의 90일 기준(며칠 안 쓴 권한을 후보로 뽑는지), `sla.json`(요청을 몇 시간 안에 처리해야 하는지)입니다.
- **고치기**: 어느 파일을 열어서 어떻게 고칠지 정합니다. 방법은 셋 중 하나입니다.

| 방법 | 뜻 | 3과목에서 한 예 |
|---|---|---|
| 새로 넣는다(추가) | 없던 것을 파일에 적어 넣음 | `users.json` 에 새 직원 항목을 적음. `exceptions.json` 에 만료 시각이 있는 예외를 적음 |
| 값을 바꾼다(수정) | 있는 항목의 값을 다른 값으로 고침 | `"employed": true` 를 `false` 로 바꿈. `conditions.json` 의 허용 접속 위치에 `"vpn"` 을 넣음 |
| 지운다(삭제) | 있던 항목을 파일에서 없앰 | 퇴사자 항목을 `users.json` 에서 지움. 만료된 예외를 `exceptions.json` 에서 지움 |

- **다시 확인**: 고친 뒤에 무엇을 다시 실행하거나 어떤 출력을 보면 고쳐진 것을 알 수 있는지 정합니다.

### 📖 4.1 상황 8개와 읽을 핵심 코드

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

> 4교시는 코드를 실행하지 않고 읽고 글로 씁니다. 상황 표의 `users.json` · `exceptions.json` 은 3과목에서 쓰던 파일이고, 오늘 점검(2교시)은 같은 내용을 한 파일에 모은 `config/week_state.json` 을 읽습니다. 상황의 값은 3과목 때를 되짚은 것이라 오늘 `week_state.json` 과 다를 수 있습니다(예: 상황 3의 예외 번호). 앞 수업 파일이 없으면 문서의 코드 조각만 읽고 답합니다.

| # | 상황 (이렇게 알게 됐습니다) | 읽을 핵심 코드 |
|---|---|---|
| 1 | 새 직원 hana 가 입사했는데, hana 의 요청이 「등록되지 않은 사용자」로 거부된다 | `role_admin.py` 의 `assign_role`, `config/users.json` 의 사용자 항목 |
| 2 | 보고서에 dami 가 거부 4번으로 나오고 퇴사자 계정 점검이 실패한다. dami 는 퇴사했다 | `rbac.py` 의 `check_permission` 판정 순서, `config/users.json` |
| 3 | seoyeon 이 월말 정산 대조를 지원하게 되어 `SETTLE:QUERY` 가 잠시 필요한데 「권한 없음」으로 거부된다 | `exception_policy.py` 의 `find_exception`, `policy.py` 의 `evaluate_access` 순서, `config/exceptions.json` |
| 4 | junho 가 영업 실적 정정을 위해 `SALES:CHANGE` 를 달라고 하는데, 누가 언제까지 처리할지 정해진 방법이 없다 | `req_create.py` · `req_review.py` · `req_grant.py` · `req_sla.py` |
| 5 | 정기 점검에서 seoyeon 의 `SALES:CHANGE` 는 마지막 사용이 120일 전이고, gaeun 의 `ACCOUNT:CHANGE` 는 사용 이력이 없다 | `review_rules.py` 의 `find_stale`, `review_unused.py` 의 `find_unused`, `config/exclude_list.json` |
| 6 | 회수 대상에 쓰기 권한이 섞여 있고, 퇴사자의 역할을 비우면 권한 여러 개가 한꺼번에 사라진다 | `revoke_plan.py` · `revoke_approve.py` · `revoke.py`, `revocation_log.json` |
| 7 | 새벽에 밖에서 접속해도 요청이 허용된다. 한편 gaeun 은 VPN 으로 계정 변경을 하다가 3번 거부됐다 | `config/conditions.json`, `conditional.py` 의 `evaluate_conditional` |
| 8 | 사람이 로그를 눈으로 세는 데 오래 걸리고, 기준이 사람마다 다르다 | `access_server.py` 의 `check`, `server_log.jsonl`, `checklist.py`, `log_summary.py`, `weekly_report.py` |

- 파일들은 서로를 부릅니다. 상황 2 · 3 · 7 · 8은 요청 한 건이 같은 순서로 함수를 거칩니다. 아래 그림에서 `A -> B` 는 「A 가 B 를 부른다」는 뜻이고, 판정은 안쪽 B 부터 하고 바깥 A 가 그 결과에 조건을 더합니다.

```
요청 한 건이 거치는 순서 (상황 2 · 3 · 7 · 8)
access_server.py 의 check
   -> conditional.py 의 evaluate_conditional       (조건: 시간 · 접속 위치)
        -> policy.py 의 evaluate_access            (역할 -> 예외 -> 거부)
             -> rbac.py 의 check_permission        (사용자 · 퇴사 · 역할 · 권한)
             -> exception_policy.py 의 find_exception   (예외 만료)
   -> write_log -> server_log.jsonl                (요청마다 한 줄)
```

- 상황 4가 만든 예외가 상황 3의 `find_exception` 이 읽는 데이터가 됩니다. `req_grant.py` 의 `grant_request` 가 예외 리스트에 새 예외를 추가합니다.
- 상황 5 → 6은 점검 결과가 회수로 이어집니다. 점검이 찾은 회수 대상을 `plan_revocation` 이 받아 계획을 세우고, `mark_approvals` · `execute_revocation` 이 이어 처리합니다.
- 상황 1 · 4 는 함수가 함수를 부르는 관계가 아니라 같은 데이터(사용자 딕셔너리, 예외 리스트)를 읽고 쓰는 관계입니다.

아래는 상황마다 관련된 코드입니다. 각 코드 앞의 문장은 **이 코드를 왜 읽는지**를 알려 줍니다. 답을 알려 주는 것은 아니고, 코드에서 어디를 볼지만 짚어 줍니다. 읽고 나서 `day05_retrospective.md` 를 쓸 때 참고합니다.

#### 상황 1 · 새 직원이 들어옴

hana 를 시스템에 등록하는 일과 관련된 코드입니다.

`role_admin.py` 의 `assign_role` 은 사용자에게 역할을 주는 함수입니다. 역할을 먼저 확인하는지, 사용자 항목을 어떻게 만드는지 읽습니다.

```python
def assign_role(users, name, role):                              # 사용자 딕셔너리 · 이름 · 역할을 받는 함수
    """사용자에게 역할을 부여한다.
    신입이 입사하거나 부서를 옮겼을 때 쓰고 (성공 여부, 이유)를 리턴한다.
    """
    if role not in ROLES:                                        # 역할 파일에 없는 역할이면
        return False, "없는 역할"                                 # 부여하지 않고 거부한다
    users[name] = {"role": role, "employed": True}               # 사용자 항목을 새로 만들거나 덮어쓴다
    return True, "부여"                                           # 부여했다고 알린다
```

#### 상황 2 · 퇴사자 계정으로 요청이 계속 들어옴

퇴사한 dami 의 요청이 왜 거부되는지와 관련된 코드입니다.

`rbac.py` 의 `check_permission` 은 요청이 들어오면 허용할지 가리는 첫 함수입니다. 검사가 어떤 순서로 이루어지는지, 퇴사한 사용자는 어느 단계에서 걸리는지 읽습니다.

```python
def check_permission(user, resource, action):                    # 사용자 · 자원 · 행위를 받는 함수
    """요청을 허용할지 (허용 여부, 이유)로 리턴한다. 요청이 들어올 때 가장 먼저 쓰는 판정이고, 허용 리스트에 없으면 모두 거부한다."""   # 함수 첫 줄의 """ … """ 는 함수 설명 글이고 실행에는 영향이 없다
    if user not in USERS:                                        # 사용자 파일에 없는 계정이면
        return False, "등록되지 않은 사용자"                       # 바로 거부하고 함수를 끝낸다
    if not USERS[user]["employed"]:                              # 재직 중이 아니면
        return False, "퇴사한 계정"                                # 거부하고 함수를 끝낸다
    role = USERS[user]["role"]                                   # 이 사용자의 역할을 꺼낸다
    if role not in ROLES:                                        # 역할 파일에 없는 역할이면
        return False, "역할이 없음"                                # 거부하고 함수를 끝낸다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    if permission not in ROLES[role]:                            # 그 역할의 권한 리스트에 없으면
        return False, "권한 없음"                                  # 거부하고 함수를 끝낸다

    return True, "허용"                                          # 모든 검사를 지나면 허용한다
```

#### 상황 3 · 다른 팀 업무를 잠시 지원함

역할에 없는 권한을 잠시만 허용하는 일과 관련된 코드입니다.

`config/exceptions.json` 은 예외를 적어 두는 파일입니다. 예외 한 개가 어떤 값으로 이루어져 있는지 읽습니다.

```json
{"id": 1, "user": "seoyeon", "permission": "SETTLE:QUERY", "expires": "2026-10-22 18:00", "reason": "월말 정산 대조 지원"}
```

`policy.py` 의 `evaluate_access` 는 역할 판정과 예외 확인을 이어 붙인 함수입니다. 예외를 언제 확인하고 언제 확인하지 않는지 읽습니다.

```python
def evaluate_access(user, resource, action, now):                # 사용자 · 자원 · 행위 · 지금 시각을 받는 함수
    """(허용 여부, 이유)를 리턴한다.
    역할 권한 → 유효한 예외 → 거부 순서로 보며, 임시 예외까지 포함해 요청을 판정할 때 쓴다.
    """
    is_allowed, reason = check_permission(user, resource, action)        # 역할 판정을 먼저 한다
    if is_allowed:                                                       # 역할로 허용되면
        return True, "역할 권한"                                   # 역할 권한으로 허용한다
    if reason != "권한 없음":                                     # 사용자 자체가 거부 대상이면(없음 · 퇴사 · 역할이 없음)
        return False, reason                                     # 예외를 보지 않고 그 이유로 거부한다
    found, found_exception_id = find_exception(user, f"{resource}:{action}", now)   # 유효한 예외를 찾는다
    if found:                                                    # 있으면
        return True, f"예외 {found_exception_id}번"                            # 예외 번호와 함께 허용한다
    return False, "권한 없음"                                      # 둘 다 없으면 거부한다
```

`exception_policy.py` 의 `find_exception` 은 유효한 예외를 찾는 함수입니다. 예외가 언제까지 유효한지 어떻게 가리는지 읽습니다.

```python
def find_exception(user, permission, now):                       # 사용자 · "자원:행위" · 지금 시각을 받는 함수
    """now 시각에 유효한 예외가 있으면 (True, 예외 번호)를 리턴한다.
    없으면 (False, None)을 리턴한다.
    역할에 없는 권한을 임시로 허용해도 되는지 확인할 때 쓴다.
    """
    for exception in EXCEPTIONS:                                       # 예외를 하나씩 꺼낸다
        if exception["user"] == user and exception["permission"] == permission:   # 사람과 권한이 같으면
            expires = datetime.strptime(exception["expires"], TIME_FORMAT)  # 만료 시각을 시각으로 바꾸고
            if now < expires:                                    # 아직 만료 전이면
                return True, exception["id"]                           # 유효한 예외와 그 번호를 리턴한다
    return False, None                                           # 못 찾았으면 없다고 리턴한다
```

#### 상황 4 · 새 권한이 필요함

권한을 요청하고, 승인하고, 부여하는 절차와 관련된 코드입니다.

`req_review.py` 의 `approve_request` 는 요청서를 승인하는 함수입니다. 승인하지 않는 경우가 무엇인지, 승인하면 무엇이 바뀌는지 읽습니다.

```python
def approve_request(request, approver):                          # 요청서와 승인자 이름을 받는 함수
    """검토 중인 요청서를 승인한다.
    보안 담당자가 권한 요청을 처리할 때 쓰고 (성공 여부, 이유)를 리턴한다.
    """
    if request["status"] != "reviewing":                         # 검토 중이 아니면(이미 처리됐으면)
        return False, "검토 중이 아님"                             # 바꾸지 않고 이유를 알린다
    if request["user"] == approver:                              # 요청한 사람이 스스로 처리하려고 하면
        return False, "본인 요청은 처리할 수 없음"                  # 바꾸지 않고 이유를 알린다
    request["status"] = "approved"                               # 상태를 승인됨으로 바꾼다
    request["approver"] = approver                               # 누가 승인했는지 적어 둔다
    return True, "승인"                                          # 승인했다고 알린다
```

- 요청서의 상태(`status`)는 `reviewing` → `approved` → `granted` 순서로 바뀌고, 거절하면 `rejected` 입니다. 처리 기한은 `config/sla.json` 의 `hours`(4시간)이고 `req_sla.py` 의 `check_sla_breach` 가 기한을 넘긴 요청서를 찾습니다.
- 이 세 함수(`approve_request`, `grant_request`, `check_sla_breach`)는 서로 부르지 않습니다. 요청서 딕셔너리를 순서대로 넘겨 받으며 `status` 만 바꿉니다.

#### 상황 5 · 안 쓰는 권한이 쌓임

(앞 수업의 샘플 데이터 기준이고, 이번 주 로그와는 별개입니다.) 오래 안 쓴 권한을 찾아내는 일과 관련된 코드입니다.

`review_unused.py` 의 `find_unused` 는 권한을 마지막으로 쓴 시각을 보고 후보를 뽑는 함수입니다. 기준 일수와 비교하는 줄이 어디인지, 사용 이력이 없을 때는 어떻게 하는지 읽습니다.

```python
        used_text = last_used_map.get(key)                       # 마지막 사용 시각 문자열을 꺼낸다(이력이 없으면 None)
        if used_text is None:                                    # 사용 이력이 없으면
            unused_entry = make_unused(entry, None)              # 안 쓴 권한 한 건을 만든다
            unused.append(unused_entry)                          # 마지막 사용 시각을 None 으로 적은 복사본을 후보에 추가한다
        elif days_since(used_text, now) > limit_days:            # 사용 이력이 있고 기준 일 수보다 오래 안 썼으면
            unused_entry = make_unused(entry, used_text)         # 안 쓴 권한 한 건을 만든다
            unused.append(unused_entry)                          # 마지막 사용 시각을 적은 복사본을 후보에 추가한다
```

`config/exclude_list.json` 은 점검에 걸려도 회수하지 않을 권한을 적어 두는 파일입니다. 항목에 이유를 왜 함께 적는지 생각하며 읽습니다.

```json
{"user": "gaeun", "permission": "ACCOUNT:CHANGE", "reason": "계정에 사고가 났을 때만 쓰는 권한이라 평소에는 쓰지 않음"}
```

#### 상황 6 · 민감한 권한을 회수해야 함

(상황 5처럼 앞 수업의 샘플 데이터 기준입니다.) 권한을 안전하게 없애는 절차와 관련된 코드입니다.

`revoke_approve.py` 의 `needs_approval` 은 회수 계획 중 승인이 필요한 것을 가르는 함수입니다. 어떤 조건이 승인 대상이 되는지 읽습니다.

```python
def needs_approval(plan, sensitive):                             # 계획 한 건과 민감한 권한 리스트를 받는 함수
    """민감한 권한이거나 영향이 2개 이상이면 True, 아니면 False 를 리턴한다.
    승인이 필요한 회수를 가려낼 때 쓴다.
    """
    is_sensitive = plan["permission"] in sensitive               # 권한이 민감한 권한 리스트에 있는지(True 또는 False)
    is_big_impact = plan["impact"] >= 2                          # 영향이 2건 이상인지(True 또는 False)
    return is_sensitive or is_big_impact                         # 둘 중 하나라도 참이면 True 를 리턴한다
```

`revoke_plan.py` 의 `plan_revocation` 은 회수 대상마다 회수 방법을 정하는 함수입니다. 세 가지 방법이 어떤 조건에서 나뉘는지 읽습니다.

```python
        if "예외" in finding["source"]:                          # 예외로 받은 권한이면
            method = "예외 삭제"                                 # 그 예외를 지운다
        elif not info["employed"]:                               # 퇴사한 사용자의 역할 권한이면
            method = "역할 해제"                                 # 그 사용자의 역할을 해제한다
        else:                                                    # 재직 중인 사용자의 역할 권한이면
            method = "역할에서 권한 빼기"                        # 역할에서 그 권한을 뺀다
```

`revoke.py` 의 `execute_revocation` 은 계획을 실제로 실행하는 함수입니다. 승인 상태에 따라 실행하는 것과 하지 않는 것이 어떻게 나뉘는지, 결과를 어떻게 남기는지 읽습니다.

```python
        if plan["approval"] == "승인 대기":                      # 승인을 기다리는 계획이면
            result = "대기"                                      # 실행하지 않고 대기로 남긴다
        else:                                                    # 승인 불필요이거나 승인됨이면
            apply_plan(plan, users, roles, exceptions)           # 실제로 회수한다
            result = "실행"                                      # 실행했다고 남긴다
```

#### 상황 7 · 새벽 외부 접속, 그리고 정상 직원이 계속 거부됨

권한이 있어도 시간이나 접속 위치에 따라 막는 규칙과 관련된 코드입니다.

`config/conditions.json` 은 권한마다 허용하는 시간대와 접속 위치를 적어 둔 파일입니다. 어떤 권한에 어떤 조건이 걸려 있고, 조건이 없는 권한은 무엇인지 읽습니다.

```json
[
  {"permission": "SALES:CHANGE", "hours": [9, 18], "networks": ["office", "vpn"]},
  {"permission": "SETTLE:QUERY", "hours": [8, 20], "networks": ["office", "vpn"]},
  {"permission": "ACCOUNT:CHANGE", "hours": [9, 18], "networks": ["office"]}
]
```

`conditional.py` 의 `evaluate_conditional` 은 기본 판정이 허용일 때 위 조건을 적용하는 함수입니다. 조건에 어긋나면 어떤 이유로 거부하는지 읽습니다.

```python
    for rule in rules:                                           # 조건을 하나씩 꺼낸다
        if rule["permission"] == permission:                     # 이 권한에 걸린 조건이면
            if not is_work_time(rule, now):                      # 업무 시간 안이 아니면
                return False, "업무 시간 밖"                       # 거부한다
            if not is_allowed_network(rule, network):            # 허용된 접속 위치가 아니면
                return False, "허용되지 않은 접속 위치"            # 거부한다
    return True, reason                                          # 어긋나는 조건이 없으면 기본 판정의 이유로 허용한다
```

#### 상황 8 · 매주 어긋남을 확인해야 함

점검과 집계를 매주 같은 기준으로 하는 일과 관련된 코드입니다.

`access_server.py` 의 `check` 는 서버가 요청 한 건을 받아 판정하고 로그를 남기는 함수입니다. 값이 빠졌을 때, 허용일 때, 거부일 때 각각 어떤 숫자(상태 코드)로 답하는지 읽습니다.

```python
    now = parse_time(time_text)                                  # 시각으로 바꾼다(없거나 모양이 틀리면 None)
    if None in (user, resource, action, network, now):           # 빠졌거나 모양이 틀린 값이 하나라도 있으면
        return {"allowed": False, "reason": "입력이 잘못됨"}, 400   # 요청이 잘못됐다는 상태 코드 400 으로 답한다
    allowed, reason = evaluate_conditional(user, resource, action, network, now, RULES)   # 조건까지 판정한다
    log_entry = {                                                 # 로그 한 줄에 담을 값을 묶는다(여러 줄)
        "time": request.args.get("time"),                        # 시각
        "user": user,                                            # 사용자
        "permission": f"{resource}:{action}",                    # 권한
        "network": network,                                      # 접속 위치
        "allowed": allowed,                                      # 허용 여부
        "reason": reason,                                        # 이유
    }
    write_log(log_entry)                                         # 요청 로그를 한 줄 덧붙인다
    if allowed:                                                  # 허용이면
        return {"allowed": True, "reason": reason}, 200          # 상태 코드 200 으로 답한다
    return {"allowed": False, "reason": reason}, 403             # 거부이면 상태 코드 403 으로 답한다
```

아래 그림은 3교시에 만든 보고서가 어떤 파일의 어떤 함수에서 만들어지는지 보여 줍니다.

```
오늘 3교시에 보고서를 만든 순서 (day06_3-2_run.py 가 세 파일을 부릅니다)
day06_3-2_run.py
   -> checklist.py 의 run_checklist          (점검 결과)
   -> log_summary.py 의 read_log             (로그를 요청 리스트로)
   -> weekly_report.py 의 build_report       (두 결과를 합쳐 보고서 문자열)
   -> weekly_report.py 의 save_report        (날짜가 들어간 파일로 저장)
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 상황 8개의 원인과 고치는 방법을 내 말로 정리하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 3과목에서 파일과 함수를 하나씩 만들었지만, 상황이 생겼을 때 「무엇이 문제이고 어디를 어떻게 고치는지」를 한 번에 말하기는 어렵습니다.
- **그래서 하는 것**: 상황 8개마다 원인, 고칠 파일, 어떻게 고치는지, 고친 뒤 확인을 내 말로 정리합니다.
  - 상황 1 · 2 는 본보기가 있습니다. 먼저 읽고, 상황 3 ~ 8 중에서 내가 약하다고 느끼는 것부터 **4개 이상** 씁니다. 다 쓰고 싶으면 다 써도 됩니다.
  - 분량은 정하지 않습니다. 짧게 써도 되고, 더 공부하고 싶으면 깊게 써도 됩니다.
- **끝나면**: `day05_retrospective.md` 가 3과목 총정리 문서가 됩니다.
- **현업에서는**: 인수인계 문서는 「이런 일이 생기면 여기를 이렇게 고친다」를 상황별로 적어 둡니다.

**🎯 할 일**

1. `day05_retrospective.md` 를 만들어 아래 틀을 붙여 넣습니다. 상황 1 · 2 는 본보기라 이미 적혀 있습니다.
2. 상황 3 ~ 8 중 4개 이상을 골라 `-` 뒤를 채웁니다. 3과목에서 만든 내 파일을 열어 보면서 써도 됩니다.

**`day05_retrospective.md`**

```
# 3과목 총정리 (이름 · 2026-11-02(월))

## 상황 1 · 새 직원이 들어옴 (본보기)
- 원인: 데이터 문제입니다. hana 가 입사했는데 `users.json` 에 hana 가 아직 없습니다. 시스템은 사용자 파일에 없는 사람의 요청을 모두 「등록되지 않은 사용자」로 거부합니다.
- 고칠 파일: `config/users.json`
- 어떻게 고치나요: 새로 넣습니다. hana 를 `"hana": {"role": "sales", "employed": true}` 로 `users.json` 에 적습니다. `role` 은 hana 가 맡을 일에 맞는 역할로 정합니다.
- 고친 뒤 확인: hana 의 요청을 다시 판정해서 「등록되지 않은 사용자」가 사라지는지 봅니다.

## 상황 2 · 퇴사자 계정으로 요청이 계속 들어옴 (본보기)
- 원인: 데이터가 정리되지 않았습니다. dami 는 퇴사했는데 dami 의 항목이 `users.json` 에 그대로 남아 있어서 같은 시도가 계속 들어옵니다. `employed` 가 `false` 이면 요청은 거부되지만, 남은 항목 때문에 퇴사자 계정 점검에는 계속 걸립니다.
- 고칠 파일: `config/users.json`
- 어떻게 고치나요: dami 의 `"employed"` 가 `true` 로 남아 있다면 먼저 `false` 로 바꿉니다. 이미 `false` 이면 그대로 두고, dami 의 항목 전체를 `users.json` 에서 지웁니다.
- 고친 뒤 확인: 같은 요청이 「등록되지 않은 사용자」로 거부되고, 퇴사자 계정 점검이 통과로 바뀌는지 봅니다.
- 더 써 보고 싶은 것(선택): `check_permission` 이 퇴사 여부를 역할 확인보다 먼저 보는 이유는 무엇일까요?

## 상황 3 · 다른 팀 업무를 잠시 지원함
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):

## 상황 4 · 새 권한이 필요함
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):

## 상황 5 · 안 쓰는 권한이 쌓임
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):

## 상황 6 · 민감한 권한을 회수해야 함
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):

## 상황 7 · 새벽 외부 접속, 그리고 정상 직원이 계속 거부됨
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):

## 상황 8 · 매주 어긋남을 확인해야 함
- 원인:
- 고칠 파일:
- 어떻게 고치나요:
- 고친 뒤 확인:
- 더 써 보고 싶은 것(선택):
```

- 칸마다 무엇을 쓰는지
  - **원인**: 사람의 일인지, 데이터 문제인지, 규칙 문제인지 고르고 이유를 씁니다.
  - **고칠 파일**: 어느 파일을 열어서 고치는지 씁니다.
  - **어떻게 고치나요**: 새로 넣는지, 값을 바꾸는지, 지우는지 고르고, 정확히 무엇을 넣거나 바꾸거나 지우는지 씁니다.
  - **고친 뒤 확인**: 무엇을 다시 실행하거나 어떤 출력을 보면 고쳐진 것을 알 수 있는지 씁니다.
- 상황 하나에서 답이 여러 개일 수 있습니다(예: 상황 7은 규칙을 추가하는 경우와 고치는 경우). 떠오르는 대로 모두 씁니다. 같은 칸에 케이스 A · B 를 쓸 때는 줄을 나눠 「케이스 A: …」 처럼 적습니다.

**순서**

1. **[VS Code 또는 터미널]** `access_control` 폴더에 `day05_retrospective.md` 를 만들어 위 틀을 붙여 넣습니다.
2. **[VS Code]** 4.1 의 상황 표와 코드를 보면서 상황 3 ~ 8 중 4개 이상의 `-` 뒤를 채웁니다. 막히면 3과목에서 만든 내 파일을 열어서 읽습니다.
3. **[보고서]** `day06_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 🔍 상황 8개를 「데이터를 고친 상황」과 「규칙을 고친 상황」으로 나눠 보면 각각 어떤 상황인가요? 어느 쪽에서 실수하면 더 위험한지 이유와 함께 적어 주세요.
   - (나) 🔍 3과목에서 가장 헷갈렸던 로직 하나와, 어떻게 이해했는지 적어 주세요.
   - (다) (선택) 1과목에서 만든 LLM 호출이나 알림과 이어 붙일 수 있는 곳을 적어 주세요. 예를 들어 `log_summary.py` 의 `read_log` 가 만든 요청 리스트를 LLM 호출에 넘겨 요약하는 것입니다.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 상황이 생기면 | 확인 → 원인 → 고치기(추가 · 수정 · 삭제) → 다시 확인 |
| 원인 | 사람의 일 · 데이터 문제 · 규칙 문제 |
| 고칠 파일 | 데이터는 `users.json` · `exceptions.json` · `exclude_list.json`, 규칙은 `conditions.json` · `alert.json` |
| 퇴사자 · 일시 지원 | `employed` 수정 · 계정 삭제, 만료 시각이 있는 예외 추가 |
| 새 권한 · 안 쓰는 권한 | 요청 → 승인 → 부여, 점검 후 회수 또는 회수 제외 |
| 회수 · 조건 · 매주 확인 | 계획 → 승인 → 실행 → 이력, 시간 · 접속 위치 조건, 점검 + 집계 + 보고서 |

---

## 오늘 마무리

| 확인 | 문제 |
|---|---|
| 퇴사자 · 만료 예외 · 부서와 역할을 점검해 통과와 실패를 가렸다 | 오전 2-1 |
| 서버 로그를 집계해 거부율과 경고 여부를 구하고, 점검과 합쳐 주간 보고서 파일을 만들었다 | 오전 3-1 |
| 상황 8개의 원인과 고치는 방법을 내 말로 정리해 3과목 총정리 문서를 만들었다 | 오전 4-1 |

오후에는 4과목 이상탐지를 시작합니다. 오늘 만든 「로그 한 줄을 읽고, 세고, 기준과 비교하는」 방식이 4과목에서 로그를 분석할 때의 바탕이 됩니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_2-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `check_employed` 안

```python
        if not info["employed"]:                                 # 퇴사했으면
            problems.append(name)                                # 이름을 문제 리스트에 추가한다
```

② `check_expired` 안

```python
        expires_at = datetime.strptime(exception["expires"], TIME_FORMAT)   # 만료 시각 문자열을 시각으로 바꾼다
        if expires_at <= now:                                    # 만료 시각이 지금과 같거나 지났으면
            problems.append(exception["id"])                           # 예외 번호를 문제 리스트에 추가한다
```

③ `check_dept` 안

```python
        expected_dept = role_dept[info["role"]]                  # 이 역할이 속해야 하는 부서를 찾는다
        if expected_dept != info["dept"]:                        # 사용자의 부서와 다르면
            problems.append(name)                                # 이름을 문제 리스트에 추가한다
```

**결과**

- (가) 출력은 다음과 같고, 통과는 **1개**(만료 예외 점검), 실패는 **2개**입니다.
  - 퇴사자 계정 점검은 `dami`, 부서와 역할 점검은 `junho` 가 걸렸습니다.

```
--- 단계 1: 점검 대상 - 사용자 6 명 · 예외 4 개
--- 단계 2: 점검 결과
퇴사자 계정 점검 | 실패 | ['dami']
만료 예외 점검 | 통과 | []
부서와 역할 점검 | 실패 | ['junho']
```

- (나) 만료 예외 점검이 통과인 것은 「예외 네 개 모두 만료 시각이 아직 오지 않았다」는 뜻일 뿐입니다.
  - 예외 3번은 퇴사한 dami 의 것이라, 만료 시각(2026-11-03 18:00)이 오지 않았어도 이미 필요 없는 권한입니다.
  - 만료 점검은 시각만 보고 사용자의 상태는 보지 않아서 이 문제를 잡지 못합니다.
  - 퇴사자 계정 점검(`dami` 실패)과 함께 읽어야 「dami 의 예외 3번을 지워야 한다」는 결론이 나옵니다.
- (다) 점검 코드가 알려 주는 것은 「junho 의 부서(영업)가 `finance` 역할이 속해야 하는 부서(재무)와 다르다」까지입니다.
  - 어느 쪽이 잘못됐는지는 알려 주지 못합니다. 영업으로 옮겼는데 역할을 안 바꿨을 수도 있고, 재무 업무를 계속하는데 부서 표기만 바뀐 것일 수도 있습니다.
  - 담당자는 junho 와 팀장에게 지금 하는 일을 확인하고, 부서와 역할 중 하나를 고쳐야 합니다.
  - 코드가 바로 회수하면 junho 가 하던 정산 조회가 갑자기 막혀 업무가 멈출 수 있습니다.

**왜**

- 점검은 사람이 눈으로 읽는 대신 같은 기준으로 반복하려고 함수로 만듭니다.
  - 점검마다 문제 리스트를 리턴하게 하면 비어 있는지만 보고 통과와 실패를 가릴 수 있고, 보고서에 대상을 그대로 적을 수 있습니다.

**자주 틀리는 곳**

- `check_expired` 의 부등호 방향을 거꾸로 `>=` 로 쓰면 오류는 나지 않고 아직 만료되지 않은 예외가 모두 실패로 나옵니다.
  - 실행하면 다음처럼 됩니다(만료 예외 점검이 실패로 나오고 예외 번호가 네 개 모두 보이면 이 실수입니다).

```
--- 단계 1: 점검 대상 - 사용자 6 명 · 예외 4 개
--- 단계 2: 점검 결과
퇴사자 계정 점검 | 실패 | ['dami']
만료 예외 점검 | 실패 | [3, 6, 7, 8]
부서와 역할 점검 | 실패 | ['junho']
```

**관제에서는**

- 정기 점검 도구는 어긋난 곳을 **찾는 데까지** 자동으로 하고, 회수는 사람이 계획과 승인을 거쳐 합니다.
  - 점검이 모두 통과여도 「이 기준으로는 문제가 없다」는 뜻이므로, 점검 기준이 현실과 맞는지 주기마다 다시 봅니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_3-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 다섯 함수입니다.

① `read_log` 안

```python
            entry = json.loads(line)                             # JSON 한 줄을 딕셔너리로 바꾼다
            entries.append(entry)                                # 요청 리스트에 추가한다
```

② `count_by` 안

```python
        value = entry[key]                                       # 이 요청의 기준 값을 꺼낸다
        old_count = counts.get(value, 0)                         # 지금까지 센 횟수를 꺼낸다(처음이면 0)
        counts[value] = old_count + 1                            # 횟수를 1 늘려 넣는다
```

③ `filter_denied` 안

```python
        if not entry["allowed"]:                                 # 거부된 요청이면
            denied.append(entry)                                 # 거부 리스트에 추가한다
```

④ `deny_rate` 안

```python
    if total == 0:                                               # 요청이 하나도 없으면
        return 0.0                                               # 0.0 을 리턴한다(0 으로 나누지 않는다)
```

⑤ `find_heavy_users` 안

```python
        if count >= limit:                                       # 거부 횟수가 기준 이상이면
            heavy.append(user)                                   # 사용자 이름을 추가한다
```

**결과**

- (가) 3-1 의 출력은 다음과 같고, 허용 **24**, 거부 **16**, 거부율 **40%** 입니다.
  - 거부 사유 중 가장 많은 것은 `허용되지 않은 접속 위치`(5개)입니다.

```
--- 단계 1: 집계 - 요청 40 건
허용 24 · 거부 16 · 거부율 40%
--- 단계 2: 거부 사유별
역할이 없음 3
업무 시간 밖 4
퇴사한 계정 4
허용되지 않은 접속 위치 5
--- 단계 3: 경고 기준
거부율 40% >= 기준 30% -> 경고
거부 4 번 이상 사용자: ['dami', 'gaeun']
```

  - `day06_3-2_run.py` 의 출력은 다음과 같고, 거부율 40% 는 경고 기준 30% 이상이라 **경고**입니다. 실패한 점검은 퇴사자 계정 점검과 부서와 역할 점검입니다.

```
--- 단계 1: 모으기 - 점검 결과와 요청 로그
점검 3 가지 · 요청 40 건
--- 단계 2: 보고서 만들기와 저장
저장한 파일: access_control_weekly_report_2026-11-02.md
--- 단계 3: 저장한 보고서 내용
# 접근통제 주간 보고서 (2026-11-02)

## 1. 요청 현황
- 전체 요청: 40건 (허용 24건 · 거부 16건)
- 거부율: 40% (경고 기준 30%) -> 경고

## 2. 거부 사유
- 역할이 없음: 3건
- 업무 시간 밖: 4건
- 퇴사한 계정: 4건
- 허용되지 않은 접속 위치: 5건

## 3. 점검 결과
- 퇴사자 계정 점검: 실패 ['dami']
- 만료 예외 점검: 통과
- 부서와 역할 점검: 실패 ['junho']

## 4. 조치가 필요한 것
- 거부 4번 이상 사용자: ['dami', 'gaeun']
- 확인: 퇴사자 계정 점검 -> ['dami']
- 확인: 부서와 역할 점검 -> ['junho']
```

- (나) 두 사람의 요청은 다음과 같이 다릅니다.
  - dami 는 4번 모두 `퇴사한 계정` 으로 거부됐고, 접속 위치가 `office` · `vpn` · `external` 로 바뀝니다. 퇴사한 사람의 계정이 정리되지 않고 남아 있어 누군가 계속 시도하고 있다는 신호입니다.
    - 먼저 퇴사자 계정 점검 결과(dami 실패)를 근거로 남은 계정을 정리하고, 누가 어디서 시도했는지 조사해야 합니다.
  - gaeun 은 5번 거부됐지만 사유가 `허용되지 않은 접속 위치` 4번과 `업무 시간 밖` 1번이고, 사내망(`office`)에서는 3번 모두 허용됐습니다.
    - 계정 관리 권한(`ACCOUNT:CHANGE`)을 사내망에서만 허용하는 규칙에 VPN · 외부 접속이 걸린 것일 수 있습니다.
    - 먼저 gaeun 에게 재택이나 외근 중이었는지 확인하고, 규칙이 실제 일하는 방식과 맞는지 검토해야 합니다.
  - dami 는 계정 차단과 조사, gaeun 은 확인과 규칙 검토가 먼저라서 같은 조치를 하면 안 됩니다.
- (다) 아니요, 로그가 비어서 나온 「거부율 0%」는 안전하다는 뜻이 아닙니다.
  - 요청이 하나도 없으면 거부율은 계산할 수 없는데, 0.0 을 리턴하도록 막아 두었기 때문에 0% 로 나온 것입니다.
  - 그래서 보고서 1절의 「전체 요청: 0건」을 함께 봐야 합니다. 요청이 0건이면 서버가 멈췄거나 로그를 못 모은 것일 수 있어서 서버와 로그 수집부터 확인합니다.
  - 0 으로 나누는 것을 막지 않으면 `ZeroDivisionError` 가 나서 보고서 자체가 만들어지지 않고, 담당자는 「요청이 없었다」가 아니라 「프로그램이 고장 났다」로 받아들입니다. 아래 「자주 틀리는 곳」에서 실제로 확인합니다.

**왜**

- 로그는 한 줄씩 쌓이기만 하므로 읽고 세어 비율로 바꿔야 의미가 생깁니다.
  - 경고 기준은 `config/alert.json` 에 두어서 기준만 바꿀 때 코드를 고치지 않습니다.

**자주 틀리는 곳**

- `count_by` 에서 `old_count` 를 쓰지 않고 `counts[value] = 1` 로 쓰면 오류는 나지 않지만 모든 횟수가 1 이 됩니다.
  - 실행하면 다음처럼 됩니다(거부 사유가 모두 1 이고 「거부 4 번 이상 사용자」가 비면 이 실수입니다).

```
--- 단계 1: 집계 - 요청 40 건
허용 24 · 거부 16 · 거부율 40%
--- 단계 2: 거부 사유별
역할이 없음 1
업무 시간 밖 1
퇴사한 계정 1
허용되지 않은 접속 위치 1
--- 단계 3: 경고 기준
거부율 40% >= 기준 30% -> 경고
거부 4 번 이상 사용자: []
```

- `deny_rate` 의 8 · 9번을 빼먹으면 오늘 로그에서는 잘 되지만, 빈 로그 파일(`empty.jsonl`)로 실행하면 다음 오류가 납니다.

```
Traceback (most recent call last):
  File "…/access_control/day06_3-1_run.py", line 10, in <module>
    rate = deny_rate(entries)                                        # 거부율(0 ~ 1)을 구한다
  File "…/access_control/log_summary.py", line 47, in deny_rate
    return denied / total                                        # 거부 수를 전체 수로 나눈 비율을 리턴한다
ZeroDivisionError: division by zero
```

  - 줄 번호(`line 37`)는 사람마다 다릅니다. `ZeroDivisionError: division by zero` 가 같으면 이 실수입니다.

  - 8 · 9번을 쓰고 같은 빈 로그로 실행하면 다음처럼 오류 없이 끝납니다.

```
--- 단계 1: 집계 - 요청 0 건
허용 0 · 거부 0 · 거부율 0%
--- 단계 2: 거부 사유별
--- 단계 3: 경고 기준
거부율 0% < 기준 30% -> 경고 없음
거부 4 번 이상 사용자: []
```

**관제에서는**

- 로그 집계는 관제의 기본이고, 거부율이 갑자기 오르면 먼저 거부 사유와 사용자를 봅니다.
  - 경고는 공격이라는 뜻이 아니라 「먼저 살펴볼 곳」입니다.
  - 요청이 0개인 주는 로그 수집이 끊겼을 수 있으므로 따로 알립니다.

---

### 정답 4-1

한 예입니다. 같은 뜻이면 표현이 달라도, 더 짧거나 더 깊어도 맞습니다. 상황마다 생길 수 있는 경우(케이스)를 나눠 적었고, 모든 케이스에 원인 · 고칠 파일 · 어떻게 고치나요 · 고친 뒤 확인을 같은 순서로 썼습니다.

용어를 한 번 더 정리합니다.

- **데이터 문제**: 사용자, 역할, 예외처럼 사실을 적어 둔 파일에 있어야 할 내용이 없거나 틀린 것입니다. 예를 들어 입사한 사람이 파일에 없는 경우입니다.
- **규칙 문제**: 「무엇을 허용하고 무엇에 경고할지」 정해 둔 기준이 비어 있거나 현실과 맞지 않는 것입니다. 이 수업에서 기준을 적어 둔 곳은 네 군데입니다.
  - `conditions.json`: 이 권한은 몇 시에 어디서 접속해야 허용하는지
  - `alert.json`: 거부율이 얼마 이상이면 경고하는지
  - 점검의 90일 기준: 며칠 안 쓴 권한을 회수 후보로 뽑는지
  - `sla.json`: 요청을 몇 시간 안에 처리해야 하는지
- **사람의 일**: 입사, 퇴사, 부서 이동처럼 사람에게 생긴 일 때문에 파일을 고쳐야 하는 것입니다.

원인은 「무슨 일이 일어났고, 왜 그렇게 되는지」를 쉬운 말로 먼저 쓰고, 코드에서 어느 함수가 그렇게 움직이는지는 `(코드: …)` 로 뒤에 붙였습니다.

---

**상황 1 · 새 직원이 들어옴**

- 케이스 A. 필요한 역할이 `roles.json` 에 이미 있는 경우
  - 원인: 데이터 문제입니다. hana 가 입사했는데 `users.json` 에 hana 가 아직 없습니다.
    - 시스템은 사용자 파일에 없는 사람의 요청을 모두 거부합니다.
    - 그래서 hana 의 요청이 「등록되지 않은 사용자」로 거부됩니다. (코드: `check_permission`)
  - 고칠 파일: `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 새로 넣습니다.
    - hana 를 `"hana": {"role": "sales", "employed": true}` 로 적습니다.
    - `role` 은 hana 가 맡을 일에 맞는 역할로 정하고, `employed: true` 는 재직 중이라는 뜻입니다.
    - 코드로는 `assign_role(users, "hana", "sales")` 가 같은 일을 합니다.
  - 고친 뒤 확인: hana 가 같은 요청을 다시 보내서 「등록되지 않은 사용자」가 사라지고, `sales` 역할이 가진 권한만 허용되는지 봅니다.
- 케이스 B. 필요한 역할이 `roles.json` 에 없는 경우
  - 원인: 데이터 문제입니다. hana 에게 줄 역할이 `roles.json`(역할마다 가진 권한을 적은 파일)에 없습니다.
    - 없는 역할은 줄 수 없어서 `assign_role` 이 「없는 역할」이라며 막습니다.
  - 고칠 파일: 먼저 `config/roles.json` 을, 그다음 `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 새로 넣습니다.
    - `roles.json` 에 새 역할의 이름과, 그 역할이 가질 권한 리스트를 적습니다. 일에 꼭 필요한 권한만 넣습니다.
    - 그다음 케이스 A 처럼 `users.json` 에 hana 를 적습니다.
  - 고친 뒤 확인: `assign_role` 이 「부여」를 리턴하고, hana 의 요청이 새 역할의 권한 안에서만 허용되는지 봅니다.

**상황 2 · 퇴사자 계정으로 요청이 계속 들어옴**

- 케이스 A. `employed` 가 이미 `false` 인 경우 (지금의 dami)
  - 원인: 데이터가 정리되지 않았습니다.
    - dami 는 퇴사했고 `employed` 도 `false`(재직 아님)라서, 요청은 이미 「퇴사한 계정」으로 거부되고 있습니다.
    - 그런데 dami 가 `users.json` 에 그대로 남아 있어서 같은 시도가 계속 들어오고, 퇴사자 계정 점검에도 계속 걸립니다.
  - 고칠 파일: `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 지웁니다. dami 의 항목 전체를 `users.json` 에서 지웁니다.
  - 고친 뒤 확인: 같은 요청이 이제 「등록되지 않은 사용자」로 거부되고, 퇴사자 계정 점검이 통과로 바뀌는지 봅니다.
- 케이스 B. `employed` 가 아직 `true` 인 경우
  - 원인: 데이터가 틀렸습니다. 가장 위험한 경우입니다.
    - dami 는 퇴사했는데 `users.json` 에는 아직 `"employed": true`(재직 중)로 적혀 있습니다.
    - 시스템은 파일을 믿기 때문에 dami 를 재직자로 보고, `sales` 역할의 권한으로 요청을 **허용**합니다.
    - 퇴사한 사람이 계속 시스템을 쓰는 셈입니다. (코드: `check_permission` 의 퇴사 검사가 이 값을 봅니다.)
  - 고칠 파일: `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 먼저 값을 바꿉니다. dami 의 `"employed": true` 를 `false` 로 고칩니다. 그다음 케이스 A 처럼 dami 의 항목을 지웁니다.
  - 고친 뒤 확인: 같은 요청이 허용에서 「퇴사한 계정」 거부로 바뀌고, 항목을 지운 뒤에는 「등록되지 않은 사용자」로 거부되는지 봅니다.
- 케이스 C. 퇴사자에게 아직 만료되지 않은 예외가 남아 있는 경우
  - 원인: 데이터가 정리되지 않았습니다.
    - dami 앞으로 적힌 예외(예: 인수인계용)가 `exceptions.json` 에 만료 시각 전까지 남아 있습니다.
    - 퇴사한 사람은 예외를 보기 전에 먼저 거부되므로, 요청이 허용되지는 않습니다. (코드: `evaluate_access`)
    - 하지만 예외가 파일에 남아 있어서 점검에 계속 나옵니다.
  - 고칠 파일: `config/exceptions.json` 을 엽니다.
  - 어떻게 고치나요: 지웁니다. dami 앞으로 된 예외 항목을 지우고, 케이스 A 처럼 `users.json` 의 dami 항목도 함께 지웁니다.
  - 고친 뒤 확인: 점검에서 dami 의 예외가 더는 나오지 않는지 봅니다.
- 생각해 볼 것: `check_permission` 은 왜 역할을 보기 전에 퇴사 여부부터 볼까요?
  - 순서가 바뀌면 퇴사한 사람도 역할 권한으로 허용될 수 있기 때문입니다.

**상황 3 · 다른 팀 업무를 잠시 지원함**

- 케이스 A. 기간이 정해진 지원인 경우 (seoyeon 의 월말 정산 대조)
  - 원인: 사람의 일 때문에 잠깐 필요한 권한입니다. 파일이 틀린 것은 아닙니다.
    - seoyeon 의 `sales` 역할에는 정산 조회 권한(`SETTLE:QUERY`)이 원래 없습니다.
    - 이번 달만 정산 대조를 도와야 해서 이 권한이 잠깐 필요한데, 지금은 「권한 없음」으로 거부됩니다. (코드: `evaluate_access`)
  - 고칠 파일: `config/exceptions.json` 을 엽니다.
  - 어떻게 고치나요: 새로 넣습니다.
    - 예외 1개를 `{"id": 6, "user": "seoyeon", "permission": "SETTLE:QUERY", "expires": "2026-11-05 18:00", "reason": "월말 정산 대조 지원"}` 처럼 적습니다.
    - 번호(`id`)는 아직 쓰지 않은 다음 번호로 정하고, `expires` 는 지원이 끝나는 시각입니다.
    - 잠깐만 필요하므로 seoyeon 의 역할은 바꾸지 않습니다.
  - 고친 뒤 확인: 만료 시각 전에는 요청이 「예외 6번」으로 허용되고, 만료 시각이 되면 다시 「권한 없음」으로 거부되는지 봅니다.
- 케이스 B. 지원이 끝나서 예외 기간이 지난 경우
  - 원인: 데이터가 정리되지 않았습니다.
    - 지원이 끝나 만료 시각이 지났는데, 그 예외가 `exceptions.json` 에 그대로 남아 있습니다.
    - 만료된 예외는 판정에서 이미 무시하므로 요청은 거부됩니다. (코드: `find_exception`)
    - 하지만 만료 예외 점검에는 계속 걸립니다.
  - 고칠 파일: `config/exceptions.json` 을 엽니다.
  - 어떻게 고치나요: 지웁니다. 만료된 예외 항목을 지웁니다.
  - 고친 뒤 확인: 만료 예외 점검이 통과로 바뀌는지 봅니다.
- 케이스 C. 지원이 아니라 업무 자체가 바뀐 경우
  - 원인: 사람의 일(부서 이동)입니다.
    - 잠깐이 아니라 앞으로 계속 다른 일을 하게 된 것입니다.
    - 이럴 때 예외로 풀면 만료 시각마다 같은 요청이 다시 들어와서, 예외를 계속 새로 만들어야 합니다.
  - 고칠 파일: `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 값을 바꿉니다. 그 사용자의 `role` 을 새 역할로 바꿉니다. 코드로는 `assign_role` 이 같은 일을 합니다.
  - 고친 뒤 확인: 새 역할이 가진 권한으로 허용되고, 이전 역할의 권한은 더 이상 허용되지 않는지 봅니다.

**상황 4 · 새 권한이 필요함**

- 케이스 A. 정상적인 요청 (junho 의 영업 실적 정정)
  - 원인: 권한을 달라는 요청을 처리하는 정해진 순서(절차)가 없습니다.
    - junho 가 `SALES:CHANGE` 를 달라고 하는데, 누가 승인하고 언제까지 처리할지 정해져 있지 않습니다.
    - 순서가 없으면 담당자가 파일을 직접 고쳐서 권한을 주게 되고, 누가 언제 왜 승인했는지 기록이 남지 않습니다.
  - 고칠 파일: 새로 만드는 `req_create.py`(요청서 만들기), `req_review.py`(승인하기), `req_grant.py`(부여하기)입니다.
  - 어떻게 고치나요: 새로 넣습니다. 절차를 코드로 만듭니다.
    - `create_request` 로 요청서를 만듭니다.
    - 검토하는 사람이 `approve_request` 로 승인합니다.
    - 승인된 요청서만 `grant_request` 로 부여하고, 부여하면 예외 리스트에 새 예외가 추가됩니다.
  - 고친 뒤 확인: 요청서의 `status` 가 `reviewing` → `approved` → `granted` 로 바뀌고, junho 의 `SALES:CHANGE` 요청이 예외로 허용되는지 봅니다.
- 케이스 B. 요청한 사람이 자기 요청을 승인하려는 경우
  - 원인: 규칙은 이미 있고 코드가 막고 있습니다.
    - 요청한 사람이 스스로 승인하면 검토하는 의미가 없어집니다.
    - 그래서 `approve_request` 는 요청한 사람과 승인하는 사람이 같으면 승인하지 않습니다.
  - 고칠 파일: 고칠 파일이 없습니다.
  - 어떻게 고치나요: 다른 사람이 승인하도록 합니다.
  - 고친 뒤 확인: 본인이 승인하면 「본인 요청은 처리할 수 없음」이 나오고, 다른 사람이 승인하면 「승인」이 나오는지 봅니다.
- 케이스 C. 요청이 오래 처리되지 않는 경우
  - 원인: 검토 중인 요청서가 정해진 처리 기한을 넘겼습니다.
    - 기한은 `config/sla.json` 에 적힌 4시간입니다.
    - 기한을 넘기면 요청한 사람이 계속 기다리게 됩니다.
  - 고칠 파일: 기한이 현실에 맞지 않을 때만 `config/sla.json` 을 엽니다.
  - 어떻게 고치나요:
    - 먼저 `check_sla_breach` 로 기한을 넘긴 요청서를 찾아 담당자에게 알립니다.
    - 4시간이 현실에 맞지 않으면 `hours` 의 값을 바꿉니다.
  - 고친 뒤 확인: 접수한 지 6시간이 지난 검토 중 요청서가 기한을 넘긴 요청서 리스트에 나오는지 봅니다.

**상황 5 · 안 쓰는 권한이 쌓임**

- 케이스 A. 오래 안 썼고 정말 필요 없는 권한 (junho 의 `SALES:QUERY`, 91일째 안 씀)
  - 원인: 안 쓰는 권한이 남아 있습니다.
    - 점검은 마지막으로 쓴 지 90일이 넘은 권한을 회수 후보로 뽑습니다.
    - 이 권한은 91일째 안 써서 후보에 걸렸습니다. 이런 점검이 없으면 한 번 준 권한이 계속 남습니다. (코드: `find_unused`)
  - 고칠 파일: 점검 코드는 `review_unused.py`, 마지막 사용 시각은 `config/access_log.json` 에 있습니다.
  - 어떻게 고치나요: 후보로 뽑힌 권한을 회수 대상으로 넘깁니다. 실제 회수는 상황 6에서 합니다.
  - 고친 뒤 확인: 점검을 다시 돌리면 이 권한이 후보에 나옵니다. 정확히 90일째 안 쓴 junho 의 `SETTLE:QUERY` 는 후보가 아닙니다. 기준이 「90일을 넘으면」이기 때문입니다.
- 케이스 B. 평소에 안 써도 필요한 권한 (seoyeon 의 `SALES:CHANGE`, 120일째 안 씀)
  - 원인: 사람의 일 때문에 쓰는 때가 드문 권한입니다.
    - seoyeon 은 6월 말과 12월 말 결산 때만 이 권한을 씁니다.
    - 120일 안 썼으니 점검에는 걸리지만, 회수하면 결산 때 일을 못 합니다.
  - 고칠 파일: `config/exclude_list.json` 을 엽니다.
  - 어떻게 고치나요: 새로 넣습니다.
    - 사용자, 권한, 제외하는 이유를 적습니다.
    - 이유를 적어 두어야 나중에 왜 제외했는지 알 수 있습니다.
  - 고친 뒤 확인: 이 권한이 회수 대상에서 빠지고 회수 제외로 분리되는지 봅니다.
- 케이스 C. 사용 이력이 아예 없는 권한 (gaeun 의 `ACCOUNT:CHANGE`)
  - 원인: 계정에 사고가 났을 때만 쓰는 권한이라, 평소에는 사용 기록이 남지 않습니다.
    - 점검은 기록이 없는 권한도 안 쓴 권한으로 뽑습니다.
  - 고칠 파일: `config/exclude_list.json` 을 엽니다.
  - 어떻게 고치나요: 케이스 B 와 같이 새로 넣습니다. 이유에 「계정에 사고가 났을 때만 쓰는 권한」이라고 적습니다.
  - 고친 뒤 확인: 케이스 B 와 같습니다.
- 케이스 D. 제외 리스트에 있어도 사용자가 퇴사한 경우 (dami 의 `SALES:QUERY`)
  - 원인: 퇴사한 사람의 권한은 제외 리스트에 있어도 제외하지 않습니다.
    - 이 권한은 「일을 넘겨받을 사람이 정해질 때까지 필요」라는 이유로 제외 리스트에 있습니다.
    - 하지만 dami 가 퇴사했으므로 코드가 제외하지 않고 회수 대상으로 둡니다. (코드: `can_exclude`)
  - 고칠 파일: 고칠 파일이 없습니다. 코드가 이미 처리합니다.
  - 어떻게 고치나요: 이 권한은 회수 대상으로 둡니다. 필요하면 제외 리스트의 dami 항목은 지웁니다.
  - 고친 뒤 확인: 이 권한이 회수 제외가 아니라 회수 대상으로 나오는지 봅니다.

**상황 6 · 민감한 권한을 회수해야 함**

수업에서는 프로그램 안의 데이터를 바꾸고 회수 이력 파일(`revocation_log.json`)만 저장합니다. 실제 서비스에서는 아래 데이터 파일을 직접 고칩니다.

- 케이스 A. 예외로 받은 권한을 회수하는 경우 (seoyeon 의 정산 조회, 예외 1번)
  - 원인: 데이터가 정리되지 않았습니다. 지원이 끝났는데 그 예외가 남아 있습니다.
  - 고칠 파일: `config/exceptions.json` 을 엽니다.
  - 어떻게 고치나요: 지웁니다.
    - 그 예외 항목을 지웁니다.
    - 영향받는 권한이 1개이고 쓰기 권한이 아니라서, 승인 없이 실행해도 됩니다.
  - 고친 뒤 확인: 회수 전과 후의 판정을 비교하면 이미 거부였던 요청은 「그대로」입니다. 이력에는 「실행」으로 남습니다.
- 케이스 B. 퇴사자의 역할을 비우는 경우 (dami 의 `sales` 역할)
  - 원인: 데이터가 정리되지 않았습니다.
    - 퇴사한 dami 에게 `sales` 역할이 남아 있습니다.
    - 역할을 비우면 dami 가 그 역할로 받던 권한 2개가 한꺼번에 사라지므로 영향이 큽니다.
  - 고칠 파일: `config/users.json` 을 엽니다.
  - 어떻게 고치나요: 값을 바꿉니다. dami 의 역할을 비웁니다. 영향이 2개라서 보안 책임자의 승인을 먼저 받습니다.
  - 고친 뒤 확인: 승인 상태가 「승인됨」이면 실행되고 이력에 남는지 봅니다.
- 케이스 C. 쓰기 권한을 회수하는데 승인이 아직 없는 경우 (junho 의 `SALES:CHANGE`, 예외 2번)
  - 원인: 사람의 판단이 필요한 일입니다.
    - 쓰기 권한(`CHANGE`)을 잘못 없애면, 일하던 사람이 데이터를 바꾸지 못합니다.
    - 그래서 민감한 권한 리스트(`sensitive.json`)에 있는 권한은 보안 책임자의 승인이 있어야 회수합니다.
  - 고칠 파일: 파일을 고치지 않습니다. 승인 상태를 정하는 `revoke_approve.py` 의 결과를 봅니다.
  - 어떻게 고치나요: 승인이 아직 없으면 실행하지 않고 「승인 대기」로 둡니다.
  - 고친 뒤 확인: 이력에 「대기」로 남고, 승인이 나면 실행되는지 봅니다.
- 케이스 D. 재직 중인 사용자의 역할에서 권한을 빼는 경우 (junho 의 `SALES:QUERY`, `finance` 역할)
  - 원인: `finance` 역할이 필요한 것보다 많은 권한을 갖고 있습니다.
  - 고칠 파일: `config/roles.json` 을 엽니다.
  - 어떻게 고치나요: 지웁니다.
    - `finance` 역할의 권한 리스트에서 그 권한을 뺍니다.
    - `finance` 역할을 가진 모든 사용자에게 적용되므로, 먼저 사용자가 몇 명인지 확인합니다.
  - 고친 뒤 확인: junho 의 `SALES:QUERY` 판정이 허용에서 거부(권한 없음)로 바뀌는지 봅니다.
- 케이스 E. 보안 책임자가 승인을 거절한 경우
  - 원인: 사람이 「승인」이 아닌 결정을 내렸습니다.
    - 승인이 필요한 회수 계획을 보안 책임자가 거절했습니다.
    - 코드는 결정이 「승인」일 때만 「승인됨」으로 적고, 거절이거나 결정이 없으면 모두 「승인 대기」로 둡니다. (코드: `mark_approvals`)
  - 고칠 파일: 고칠 파일이 없습니다. 결정을 담은 딕셔너리(`DECISIONS`)만 확인합니다.
  - 어떻게 고치나요: 거절된 계획은 실행하지 않고 대기로 둡니다. 다시 회수하려면 거절 이유를 해결한 뒤 승인을 새로 받습니다.
  - 고친 뒤 확인: 이력에 「대기」로 남고 권한은 그대로 유지되는지 봅니다.

**상황 7 · 새벽 외부 접속, 그리고 정상 직원이 계속 거부됨**

- 케이스 A. 새벽에 밖에서 보낸 요청이 허용되는 경우
  - 원인: 규칙 문제입니다. 조건 파일에서 `SALES:CHANGE`(데이터를 바꾸는 권한) 줄이 빠져 있었다고 가정합니다(위 4.1 의 파일에는 이 줄이 이미 들어 있습니다). 그러면 「몇 시에, 어디서 접속해야 하는지」 기준이 없습니다.
    - 기준이 없는 권한은 시간과 접속 위치를 확인하지 않습니다.
    - 그래서 밤 22시에 밖(`external`)에서 보낸 요청도, 역할만 맞으면 허용됩니다. (코드: `evaluate_conditional`)
  - 고칠 파일: `config/conditions.json` 을 엽니다.
  - 어떻게 고치나요: 빠진 줄을 새로 넣습니다.
    - `{"permission": "SALES:CHANGE", "hours": [9, 18], "networks": ["office", "vpn"]}` 를 적습니다.
    - 뜻은 「이 권한은 9시부터 18시 전까지, 사내망(`office`)이나 VPN 에서만 허용한다」입니다.
  - 고친 뒤 확인: 같은 요청(밖, 22시)이 「업무 시간 밖」으로 거부되는지 봅니다.
- 케이스 B. 정상 직원이 계속 거부되는 경우 (gaeun 이 VPN 으로 계정 변경)
  - 원인: 규칙이 현실과 맞지 않습니다.
    - gaeun 은 VPN(밖에서 회사망으로 안전하게 들어오는 연결)으로 일합니다.
    - 그런데 `ACCOUNT:CHANGE` 는 접속 위치가 `["office"]`(사내망)뿐이라서, VPN 요청이 「허용되지 않은 접속 위치」로 계속 거부됩니다.
  - 고칠 파일: `config/conditions.json` 을 엽니다.
  - 어떻게 고치나요: 값을 바꿉니다.
    - `ACCOUNT:CHANGE` 의 접속 위치 `["office"]` 를 `["office", "vpn"]` 으로 고칩니다.
    - `external`(밖)은 넣지 않습니다. 넣으면 계정을 훔친 사람이 밖에서 보낸 요청도 허용되어 위험합니다.
  - 고친 뒤 확인: gaeun 의 VPN 요청이 허용으로 바뀌는지 봅니다. 규칙을 풀었으니 다른 요청이 같이 허용되지 않는지도 봅니다.
- 케이스 C. 업무 시간 끝 시각 정각의 요청이 거부되는 경우 (seoyeon 의 18시 정각 요청)
  - 원인: 끝 시각을 포함하지 않는 약속 때문입니다.
    - 시간대 `[9, 18]` 은 「9시 이상 18시 미만」이라서 18시 정각은 업무 시간이 아닙니다.
    - 그래서 18시 정각에 보낸 요청이 「업무 시간 밖」으로 거부됩니다.
    - 실제로 18시 이후에도 일하는 부서라면, 규칙이 현실과 맞지 않는 것입니다.
  - 고칠 파일: `config/conditions.json` 을 엽니다.
  - 어떻게 고치나요: 값을 바꿉니다.
    - `SALES:CHANGE` 의 `"hours": [9, 18]` 을 `[9, 20]` 으로 고칩니다.
    - 늘린 시간에는 쓰기 요청이 모두 허용되므로, 정말 필요한 업무인지 확인한 뒤에 고칩니다.
  - 고친 뒤 확인: 18시 정각 요청이 허용되고, 20시 정각 요청은 여전히 「업무 시간 밖」으로 거부되는지 봅니다.
- 케이스 D. 조건이 없는 권한이 밖에서도 허용되는 경우 (seoyeon 의 `SALES:QUERY`, 밖 22시)
  - 원인: 문제가 아닙니다.
    - `SALES:QUERY` 는 조회만 하는 권한이라 `conditions.json` 에 조건을 걸지 않았습니다.
    - 조건이 없는 권한은 시간과 접속 위치를 보지 않고 역할 판정 결과를 그대로 따릅니다.
  - 고칠 파일: 고칠 것이 없습니다.
  - 어떻게 고치나요: 조회 권한에도 조건이 필요하다고 판단하면 케이스 A 처럼 `conditions.json` 에 새로 넣습니다. 필요 없다고 판단하면 그대로 둡니다.
  - 고친 뒤 확인: 조건을 넣은 경우에만 같은 요청이 거부로 바뀌는지 봅니다.
- 생각해 볼 것: 규칙을 풀면 정상 직원의 불편은 줄지만 위험한 접속도 같이 허용될 수 있습니다. 고치기 전에 무엇을 확인하면 좋을까요?

**상황 8 · 매주 어긋남을 확인해야 함**

- 케이스 A. 사람이 눈으로 확인하는 경우
  - 원인: 눈으로 세면 사람마다 기준이 다르고 시간도 오래 걸립니다.
    - 로그를 세는 데 오래 걸립니다.
    - 지난주와 같은 기준으로 봤는지도 알 수 없습니다.
  - 고칠 파일: 새로 만드는 `checklist.py`(점검), `log_summary.py`(로그 집계), `weekly_report.py`(보고서)입니다.
  - 어떻게 고치나요: 새로 넣습니다. 점검 세 가지, 로그 집계, 주간 보고서를 코드로 만들어 같은 기준으로 한 번에 돌립니다.
  - 고친 뒤 확인: 보고서 4절에 조치가 필요한 것이 나오고, 지난주와 같은 기준으로 비교할 수 있는지 봅니다.
- 케이스 B. 경고 기준이 현실과 맞지 않는 경우
  - 원인: 규칙 문제입니다. 경고를 띄우는 기준이 너무 낮거나 너무 높습니다.
    - 거부율이 `alert.json` 의 `deny_rate_limit` 이상이면 경고를 띄웁니다.
    - 기준이 너무 낮으면 경고가 매주 떠서 아무도 보지 않게 되고, 너무 높으면 위험을 놓칩니다.
  - 고칠 파일: `config/alert.json` 을 엽니다.
  - 어떻게 고치나요: 값을 바꿉니다. `deny_rate_limit` 의 값을 바꾸고, 바꾼 이유도 기록합니다.
  - 고친 뒤 확인: 같은 로그의 거부율 40% 는 기준이 30% 이면 경고이고, 기준을 50% 로 올리면 경고 없음으로 바뀝니다. 거부된 요청 수는 그대로이므로, 안전해진 것이 아니라 기준이 바뀐 것입니다.
- 케이스 C. 로그가 비어 있는 경우
  - 원인: 데이터가 모이지 않았습니다.
    - 서버가 멈췄거나 로그를 모으지 못했을 수 있습니다.
    - 요청이 0개면 거부율을 0% 로 계산하므로, 보고서만 보면 안전해 보입니다.
  - 고칠 파일: 서버와 로그 파일 수집을 확인합니다.
  - 어떻게 고치나요: 보고서 1절의 전체 요청 수가 0개인지 먼저 봅니다. 거부율 0% 만 보고 안전하다고 판단하지 않습니다.
  - 고친 뒤 확인: 수집이 복구되면 요청 수가 다시 보이는지 봅니다.

---

**보고서 질문**

- (가) 한 예: 데이터를 고친 상황은 1, 2, 3, 5, 6이고, 규칙을 고친 상황은 7과 8(케이스 B)입니다. 4는 요청 절차를 새로 만든 상황입니다. 규칙을 고치는 쪽이 위험이 더 큽니다.
  - 데이터를 잘못 고치면 한 사람의 권한 안에서 끝납니다.
  - 규칙을 잘못 풀면 그 규칙에 해당하는 모든 요청이 한꺼번에 영향을 받아, 위험한 접속도 같이 허용될 수 있습니다.
  - 그래서 규칙은 고치기 전에 과거 로그로 영향을 확인하는 것이 좋습니다.
- (나) 사람마다 다릅니다. 헷갈린 로직과, 읽고 쓰면서 이해한 방법(내 파일을 열어 보기, 출력을 비교하기 등)을 적으면 맞습니다.
- (다) 한 예: 보고서 문자열이나 요청 리스트를 1과목에서 만든 LLM 호출에 넘겨 요약하거나, 경고가 나오면 알림으로 보내는 곳에 이을 수 있습니다.

**왜**

- 상황이 생겼을 때 「원인 → 고칠 곳 → 방법 → 확인」 순서로 생각하는 습관을 만들기 위해서입니다.
  - 데이터를 고치는 일과 규칙을 고치는 일은 영향 범위가 다릅니다.

**자주 틀리는 곳**

- 원인을 정하지 않고 바로 파일을 고치는 경우가 많습니다. 예를 들어 gaeun 이 거부되었을 때 사용자 항목부터 고치면 해결되지 않습니다. 거부 이유가 「허용되지 않은 접속 위치」이면 고칠 곳은 `conditions.json` 입니다.
- 고친 뒤 확인을 빼먹으면, 고쳤다고 생각했지만 다른 요청이 같이 허용되는 것을 놓칩니다.

**관제에서는**

- 인수인계 문서는 이 틀(원인 → 고칠 파일 → 방법 → 확인)로 상황별 대응을 적어 둡니다.
  - 새 담당자는 코드를 처음부터 읽지 않고, 상황에서 시작해 파일을 찾아갑니다.

---

### 앞 교시 파일 완성본

앞 교시 파일이 없거나 잘 안 될 때 이 코드로 만듭니다. 데이터 파일 세 개는 「시작하기」 6번의 내용입니다.

**`checklist.py`** (2교시 완성본)

```python
import json                                                      # JSON 파일을 읽는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 만료 시각 문자열의 형식 (예: 2026-11-03 18:00)


def load_state(path):                                            # 파일 경로를 받는 함수
    """점검할 데이터(사용자 · 역할의 부서 · 예외)를 읽어 딕셔너리로 리턴한다.
    정기 점검을 시작할 때 쓴다.
    """
    with open(path, encoding="utf-8") as json_file:                      # 파일을 연다
        return json.load(json_file)                                      # 읽은 내용을 바로 리턴한다


def check_employed(users):                                       # 사용자 딕셔너리를 받는 함수
    """퇴사했는데 계정이 남아 있는 사용자 이름 리스트를 리턴한다.
    정기 점검에서 퇴사자 계정을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        if not info["employed"]:                                 # 퇴사했으면
            problems.append(name)                                # 이름을 문제 리스트에 추가한다
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def check_expired(exceptions, now):                              # 예외 리스트와 지금 시각(datetime)을 받는 함수
    """만료 시각이 지났는데 남아 있는 예외의 번호 리스트를 리턴한다.
    정기 점검에서 기간이 끝난 예외를 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 예외 번호를 모을 리스트
    for exception in exceptions:                                       # 예외를 하나씩 꺼낸다
        expires_at = datetime.strptime(exception["expires"], TIME_FORMAT)   # 만료 시각 문자열을 시각으로 바꾼다
        if expires_at <= now:                                    # 만료 시각이 지금과 같거나 지났으면
            problems.append(exception["id"])                           # 예외 번호를 문제 리스트에 추가한다
    return problems                                              # 문제가 있는 예외 번호를 리턴한다


def check_dept(users, role_dept):                                # 사용자 딕셔너리와 역할별 부서 딕셔너리를 받는 함수
    """부서가 역할의 부서와 다른 사용자 이름 리스트를 리턴한다.
    정기 점검에서 엉뚱한 부서에 역할이 남은 사람을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        expected_dept = role_dept[info["role"]]                  # 이 역할이 속해야 하는 부서를 찾는다
        if expected_dept != info["dept"]:                        # 사용자의 부서와 다르면
            problems.append(name)                                # 이름을 문제 리스트에 추가한다
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def run_checklist(state, now):                                   # 읽은 데이터와 지금 시각을 받는 함수
    """점검 세 가지를 실행한다.
    점검 이름과 문제 리스트를 담은 딕셔너리의 리스트를 리턴한다.
    매주 어긋난 곳을 한 번에 찾을 때 쓴다.
    """
    users = state["users"]                                       # 사용자 딕셔너리를 꺼낸다
    exceptions = state["exceptions"]                             # 예외 리스트를 꺼낸다
    role_dept = state["role_dept"]                               # 역할별 부서 딕셔너리를 꺼낸다
    results = []                                                 # 점검 결과를 모을 리스트
    results.append({"name": "퇴사자 계정 점검", "problems": check_employed(users)})            # 첫째 점검 결과를 추가한다
    results.append({"name": "만료 예외 점검", "problems": check_expired(exceptions, now)})     # 둘째 점검 결과를 추가한다
    results.append({"name": "부서와 역할 점검", "problems": check_dept(users, role_dept)})     # 셋째 점검 결과를 추가한다
    return results                                               # 점검 결과 리스트를 리턴한다
```

**`log_summary.py`** (3교시 완성본)

```python
import json                                                      # JSON 문자열을 딕셔너리로 바꾸는 모듈을 불러온다


def read_log(path):                                              # 로그 파일 경로를 받는 함수
    """서버 로그 파일을 한 줄씩 읽어 요청 딕셔너리 리스트로 만든다.
    주간 로그를 집계하기 전에 파일을 읽을 때 쓴다.
    """
    entries = []                                                 # 요청 딕셔너리를 모을 리스트
    with open(path, encoding="utf-8") as log_file:                      # 파일을 연다
        for line in log_file:                                           # 파일에서 한 줄씩 꺼낸다
            entry = json.loads(line)                             # JSON 한 줄을 딕셔너리로 바꾼다
            entries.append(entry)                                # 요청 리스트에 추가한다
    return entries                                               # 요청 리스트를 리턴한다


def count_by(entries, key):                                      # 요청 리스트와 센 기준(키 이름)을 받는 함수
    """요청을 key 의 값별로 세어 {값: 횟수} 딕셔너리를 리턴한다.
    사용자별 · 이유별로 몇 번인지 알고 싶을 때 쓴다.
    예: count_by(entries, "user")
    """
    counts = {}                                                  # 값별 횟수를 담을 딕셔너리
    for entry in entries:                                        # 요청을 하나씩 꺼낸다
        value = entry[key]                                       # 이 요청의 기준 값을 꺼낸다
        old_count = counts.get(value, 0)                         # 지금까지 센 횟수를 꺼낸다(처음이면 0)
        counts[value] = old_count + 1                            # 횟수를 1 늘려 넣는다
    return counts                                                # 값별 횟수를 리턴한다


def filter_denied(entries):                                      # 요청 리스트를 받는 함수
    """거부된 요청만 모아 리스트로 리턴한다.
    거부 사유와 사용자를 따로 볼 때 쓴다.
    """
    denied = []                                                  # 거부된 요청을 모을 리스트
    for entry in entries:                                        # 요청을 하나씩 꺼낸다
        if not entry["allowed"]:                                 # 거부된 요청이면
            denied.append(entry)                                 # 거부 리스트에 추가한다
    return denied                                                # 거부된 요청 리스트를 리턴한다


def deny_rate(entries):                                          # 요청 리스트를 받는 함수
    """전체 요청 중 거부된 요청의 비율(0 ~ 1)을 리턴한다.
    주간 보고서에서 거부율을 구할 때 쓰며, 요청이 없으면 0.0 이다.
    """
    total = len(entries)                                         # 전체 요청 수
    if total == 0:                                               # 요청이 하나도 없으면
        return 0.0                                               # 0.0 을 리턴한다(0 으로 나누지 않는다)
    denied_entries = filter_denied(entries)                      # 거부된 요청 리스트
    denied = len(denied_entries)                                 # 거부된 요청 수
    return denied / total                                        # 거부 수를 전체 수로 나눈 비율을 리턴한다


def find_heavy_users(denied_counts, limit):                      # 사용자별 거부 횟수 딕셔너리와 기준 횟수를 받는 함수
    """거부 횟수가 limit 이상인 사용자 이름 리스트를 리턴한다.
    거부가 한 사람에게 몰렸는지 확인할 때 쓴다.
    """
    heavy = []                                                   # 기준에 걸린 사용자 이름을 모을 리스트
    for user, count in denied_counts.items():                    # 사용자 이름과 거부 횟수를 하나씩 꺼낸다
        if count >= limit:                                       # 거부 횟수가 기준 이상이면
            heavy.append(user)                                   # 사용자 이름을 추가한다
    return heavy                                                 # 기준에 걸린 사용자 이름을 리턴한다
```
