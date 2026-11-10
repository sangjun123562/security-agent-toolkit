# 11/10(화) 오후 · 5과목 자동 대응(SOAR, 쏘아: 정해 둔 절차대로 대응을 자동으로 실행하는 것) ③ — 담당자 승인 처리하기 · 외부 서비스가 실패하면 다시 시도하기 · 하루 흐름 한 번에 실행하기 — 실습

오전에 알림에 맥락을 붙이고(`enrichment.py`), 처리 경로를 나누고(`routing.py`), 실행 전에 중복과 한도를 확인하는 안전장치를 만들었습니다(`safe_runner.py`). 그 결과 VIP 계정 알림은 `승인 필요` 경로로 갔고, 플레이북이 승인을 요구하는 알림은 `승인 대기` 로 멈췄습니다. 오후에는 두 가지를 더합니다.

- **5교시**: 멈춰 있던 알림에 담당자의 결정(승인 또는 거절)을 적용합니다. 승인할 권한이 없는 사람의 승인은 막고, 모든 결정을 기록합니다.
- **6교시**: 티켓(ticket, 티켓: 처리할 일을 한 건씩 적어 담당자에게 맡기는 요청서) 서비스 같은 외부 서비스가 잠깐 응답하지 않으면 다시 시도하고, 그래도 안 되면 담당자가 확인할 목록에 올립니다. 그리고 오전부터 만든 것을 하루 흐름 하나로 이어서 실행합니다.

오후에 자주 나오는 말은 이렇습니다.

- **승인 권한**: 승인 단추를 눌러도 되는 사람입니다. 오늘 권한이 있는 사람은 `kim.sec` · `lee.soc` 입니다.
- **감사 기록**(audit log, 오딧 로그): 어떤 알림에 무슨 일을 했고 결과가 무엇인지 한 건씩 남긴 기록입니다. 사고가 난 뒤에 어떤 대응을 했는지 다시 확인할 때 씁니다.
- **재시도**(retry, 리트라이): 실패했을 때 같은 일을 다시 해 보는 것입니다.
- **연결 오류**(`ConnectionError`): 외부 서비스에 연결하지 못했을 때 파이썬이 내는 오류입니다.
- **모의 시스템**(`state`): 진짜 계정 · 방화벽(firewall, 파이어월: 허용하지 않은 접속을 막는 장비나 프로그램) 대신 잠긴 계정 · 차단한 IP · 티켓을 적어 두는 연습용 딕셔너리입니다.
- **하루 흐름**: 오전의 맥락 붙이기 · 경로 정하기 · 안전장치(이미 잠긴 계정 건너뛰기, 잠금 한도)와 오후의 승인 · 재시도를 합친 것입니다. 알림 한 건은 맥락 붙이기 → 경로 정하기를 거친 뒤, 경로에 따라 오탐 종료 · 승인 대기 · 재시도하며 실행(이때 안전장치가 함께 쓰입니다) 중 하나로 처리됩니다.

깃허브에 올리는 일은 6교시 마지막에 합니다. 새 문법은 6교시의 `try` / `except` 하나입니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기는 미리 채운 줄에 맞춥니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. 주석은 지우지 않습니다.

📎 **이전 파일**: 5교시는 어제 `incident.py` 만 씁니다. 6교시는 오전 파일(`enrichment.py` · `routing.py` · `safe_runner.py`)과, 오전에 쓴 데이터 파일(JSON, 제이슨: 이름과 값을 짝지어 적는 파일 형식. `users_info.json` · `source_ips.json` · `trusted_ips.json`)과 월요일의 `incident_samples.json` · `config/playbook_registry.json` 도 씁니다. 없는 파일은 `complete_files.md` 의 해당 절에서 복사합니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark>`ls` 결과에 `config` · `incident.py` · `incident_samples.json` · `enrichment.py` · `routing.py` · `safe_runner.py` · `users_info.json` · `source_ips.json` · `trusted_ips.json` 이 보이면</mark> 됩니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day02_pm_approval_retry_flow.md`, `day02_pm_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 데이터 파일 두 개를 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch pending.json decisions.json
   ls
   ```

**`pending.json`** — 승인을 기다리는 건 3건입니다(오전에 `승인 필요` 경로로 간 VIP 알림 1건과, 플레이북이 승인을 요구해 멈춘 2건). 번호는 **인시던트**(incident, 보안 알림 가운데 사람이 확인하고 대응해야 하는 사건 한 건)에 붙인 관리 번호입니다. 각 건에는 어떤 플레이북(playbook, 플레이북: 알림 종류별로 어떤 대응을 할지 적어 둔 절차) 때문에 멈췄는지, 승인되면 어떤 액션을 실행하는지, 왜 승인이 필요한지가 적혀 있습니다. 5교시는 이 파일을 읽어서 씁니다. 6교시 하루 흐름은 이 파일을 읽지 않고, 코드가 같은 내용을 직접 만듭니다.

```
[
  {"id": "INC-002", "entity": "seoyeon", "playbook": "PB-002", "actions": ["담당자 알림", "티켓 생성"], "why": "플레이북 승인 값이 담당자 승인 필요", "status": "분류됨"},
  {"id": "INC-003", "entity": "gaeun", "playbook": "VIP 확인", "actions": ["담당자 알림", "티켓 생성"], "why": "VIP 계정이라 경로가 승인 필요", "status": "분류됨"},
  {"id": "INC-005", "entity": "198.51.100.90", "playbook": "PB-003", "actions": ["IP 차단", "티켓 생성"], "why": "플레이북 승인 값이 담당자 승인 필요", "status": "분류됨"}
]
```

**`decisions.json`** — 담당자가 메신저에서 누른 승인 · 거절 결과를 파일로 흉내 낸 것입니다. 건마다 적힌 것은 세 가지입니다. 누가 눌렀는지(`approver`), 승인과 거절 중 무엇을 눌렀는지(`result`), 남긴 말(`comment`)입니다. 권한이 있는 담당자는 `kim.sec` · `lee.soc` 이고 `intern01` 은 권한이 없습니다. 5 · 6교시가 읽습니다.

```
{
  "INC-002": {"approver": "kim.sec", "result": "승인", "comment": "대량 다운로드 사유를 확인해야 함"},
  "INC-003": {"approver": "kim.sec", "result": "거절", "comment": "계정 관리자의 정상 작업으로 확인됨"},
  "INC-005": {"approver": "intern01", "result": "승인", "comment": "IP 차단 진행"}
}
```

5. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`). <mark>`3 3` 이 나와야</mark> 합니다.
   ```bash
   python -c "import json; print(len(json.load(open('pending.json', encoding='utf-8'))), len(json.load(open('decisions.json', encoding='utf-8'))))"
   ```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError` 는 <mark>`incident.py` · `enrichment.py` 같은 앞 파일이 이 폴더에 없다는 뜻</mark>입니다. `complete_files.md` 에서 복사합니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env`(API 키를 적어 둔 파일) · API 키(외부 서비스를 쓸 수 있게 확인하는 비밀 문자열)는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 담당자의 승인 · 거절 결정을 적용하고, 권한 없는 승인은 막기 (승인 처리)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 알림 5건 가운데 3건이 담당자의 허락(승인)을 기다리는 상태입니다. `INC-002`(`seoyeon` 의 대량 다운로드), `INC-003`(VIP 계정, 막히면 업무에 큰 영향을 주는 중요한 계정인 계정 관리자 `gaeun`), `INC-005`(경로 스캔, 서버의 여러 주소에 차례로 요청을 보내 약점을 찾는 일을 한 IP `198.51.100.90`)입니다. 오늘 담당자가 메신저에서 승인이나 거절을 눌렀습니다.
> - **문제**:
>   - 프로그램이 담당자가 누른 결과를 받지 못해서, 담당자가 계정 관리 화면을 열어 같은 일을 다시 해야 합니다.
>   - 결과를 받는 기능을 만들더라도 누른 사람을 확인하지 않으면, 승인 권한이 없는 인턴 계정 `intern01` 의 승인으로 IP 차단이 실행됩니다.
> - **부탁**: 승인 권한이 있는 담당자의 결정만 받아서, 승인이면 실행하고 거절이면 알림을 끝내 주세요. 누가 무엇을 결정했는지는 모두 기록해 주세요.
> - **바뀌는 점**: 담당자는 단추 한 번으로 끝납니다. 권한이 없는 승인은 실행되지 않고 기록으로만 남습니다. 오늘 샘플에서는 `INC-002` 는 실행되고, `INC-003` 은 거절로 끝나고, `INC-005` 는 권한이 없어 멈춥니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 5.1 승인 처리는 「권한 확인 → 실행 또는 종료 → 기록」 순서다

담당자가 승인이나 거절을 누르면 프로그램이 그 결정을 받아 처리해야 합니다. 순서는 세 단계입니다.

1. **권한 확인**: 누른 사람이 승인 권한이 있는 사람인지 먼저 봅니다. 권한이 없는 사람의 승인으로 실행되면 안 되기 때문입니다.
2. **실행 또는 종료**: 승인이면 멈춰 있던 액션을 실행하고, 거절이면 알림을 종료합니다.
3. **기록**: 어느 경우든 누가 무엇을 했는지 감사 기록에 남깁니다. 나중에 누가 허락했는지 확인하려면 기록이 필요하기 때문입니다.

오늘 담당자 결정은 세 건입니다.

| 알림 | 결정한 사람 | 결과 | 기대하는 처리 |
|---|---|---|---|
| INC-002 | `kim.sec` (권한 있음) | 승인 | 액션을 실행하고 상태를 `조치됨` 으로 바꾼다 |
| INC-003 | `kim.sec` (권한 있음) | 거절 | 실행하지 않고 `종료` 로 옮기고 사유를 기록한다 |
| INC-005 | `intern01` (권한 없음) | 승인 | <mark>결과가 승인이어도 실행하지 않고</mark> 「권한 없는 사람이 승인하려 했다」는 기록만 남긴다 |

- **`item`**: 승인 대기 알림 한 건입니다. `pending.json` 에 들어 있는 알림 하나입니다.
- **`decision`**: 담당자의 결정 한 건입니다. 누가 · 승인인지 거절인지 · 한마디가 들어 있습니다.
- **`APPROVERS`**: 승인 권한이 있는 담당자 이름 리스트입니다.
- **`action_log`**: 감사 기록 한 건씩을 추가해 모으는 리스트입니다.

함수는 파일 세 곳에 나뉘어 있고, 직접 쓰는 곳은 **아홉 군데**입니다.

```
audit.py        log_line          : 기록 한 건을 딕셔너리로 만든다 (1번)
approvals.py    is_authorized     : 승인한 사람이 권한 목록에 있는지 확인한다 (2번)
                execute_actions   : 액션을 하나씩 실행한다 (3번)
                apply_decision    : 권한이 없으면 기록만 남기고 멈춘다 (4 · 5번)
                finish_decision   : 승인이면 실행하고 끝낸다 (6 · 7번) / 아니면 종료하고 거절 사유를 기록한다 (미리 채움)
실행 파일       day02_5-1_run.py  : 대기 건마다 결정이 있으면 apply_decision 을 호출한다 (8 · 9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 5-1 · 감사 기록을 만들고, 권한을 확인해 담당자 결정을 적용하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>승인 대기 3건이 멈춰 있고, 담당자 결정 3건(승인 · 거절 · 권한 없는 승인)이 들어와 있습니다</mark>.
- **만드는 것**: 기록 한 건 만들기(`audit.py`), 권한 확인 · 실행 · 종료(`approvals.py`), 결정을 적용하는 함수를 부르는 실행 파일(`day02_5-1_run.py`).
- **실행하면**: <mark>단계 1: 승인 대기 건, 단계 2: 결정 적용 결과, 단계 3: 처리 뒤 모의 시스템 상태, 단계 4: 감사 기록이 나옵니다.</mark>

**🎯 할 일**: 파일 세 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 ~ 4 를 읽습니다.

**`audit.py`** — 감사 기록 한 건을 만듭니다. `approvals.py` 와 6교시 `flow.py` 가 불러다 씁니다. 직접 쓰는 곳은 1번입니다.

```python
def log_line(item, action, text):  # 인시던트 · 액션 · 결과 문장을 받는 함수
    """감사 기록(어떤 알림에 · 어떤 액션을 해서 · 결과가 무엇인지) 한 건을 딕셔너리로 만들어 리턴한다.
    모든 대응을 같은 모양으로 남겨 두면 나중에 한 목록으로 되짚을 수 있어서 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 키 "incident"(item 의 "id"), "playbook"(item 의 "playbook"), "action"(action), "result"(text) 를 가진 딕셔너리를 entry 에 담는다
    return entry                   # 기록 한 건을 리턴한다
```

**`approvals.py`** — 권한을 확인하고 결정을 적용합니다. 6교시 `flow.py` 도 불러다 씁니다. 직접 쓰는 곳은 2 ~ 7번입니다.

```python
from incident import change_status, run_action                                           # 어제 파일의 함수를 불러온다
from audit import log_line                                                               # 방금 만든 기록 함수를 불러온다

APPROVERS = ["kim.sec", "lee.soc"]                                                       # 승인할 권한이 있는 담당자 이름 리스트


def hold_for_approval(incident, playbook_id, actions, why, action_log):                  # 승인 대기로 멈출 인시던트와 정보를 받는 함수
    """알림의 상태를 분류됨으로 바꾸고 승인 대기 기록을 남긴 뒤, 담당자에게 보여 줄 대기 건 한 건으로 리턴한다.
    승인이 필요한 알림을 실행하지 않고 담당자에게 넘길 때 쓴다(6교시 하루 흐름에서 호출한다).
    """
    incident["playbook"] = playbook_id                                                   # 어떤 플레이북 때문인지 적고
    incident["actions"] = actions                                                        # 승인되면 실행할 액션을 적고
    incident["why"] = why                                                                # 승인이 필요한 이유를 적는다
    change_status(incident, "분류됨")                                                    # 대응을 시작했으니 분류됨으로 옮기고
    action_log.append(log_line(incident, "전체", "승인 대기 — " + why))                  # 승인 대기 기록을 남긴다
    return incident                                                                      # 대기 건을 리턴한다


def is_authorized(approver):                                                             # 승인한 사람 이름을 받는 함수
    """승인한 사람이 승인 권한이 있는 담당자 목록(APPROVERS)에 있으면 True, 없으면 False 를 리턴한다.
    권한이 없는 사람이 누른 승인을 걸러 낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. approver 가 APPROVERS 안에 있는지(in)의 결과를 리턴한다


def execute_actions(item, state, action_log, approver):                                  # 대기 건 · 모의 시스템 · 기록 리스트 · 승인자를 받는 함수
    """대기 건에 적힌 액션을 하나씩 실행하고 누가 승인했는지 붙여 기록한 뒤, 알림을 조치됨으로 바꾸고 「실행 완료」를 리턴한다.
    담당자가 승인한 알림을 실제로 처리할 때 쓴다.
    """
    for action in item["actions"]:                                                       # 액션을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. run_action(action, item, state) 의 결과를 result 에 담는다
        action_log.append(log_line(item, action, result + " (승인: " + approver + ")"))  # 승인자를 붙여 기록한다 — 미리 채운 줄
    change_status(item, "조치됨")                                                        # 모두 실행했으니 조치됨으로 옮긴다
    return "실행 완료"                                                                   # 실행 완료를 리턴한다


def reject_unauthorized(item, approver, action_log):                                     # 대기 건 · 승인자 · 기록 리스트를 받는 함수
    """권한 없는 사람이 승인하려 한 사실을 기록에 남기고 「권한 없음」을 리턴한다. 알림의 상태는 바꾸지 않는다.
    누가 권한 없이 승인하려 했는지 보안 기록으로 남길 때 쓴다.
    """
    action_log.append(log_line(item, "전체", "권한 없음 — 승인 시도: " + approver))      # 권한 없음 기록을 남기고
    return "권한 없음"                                                                   # 권한 없음을 리턴한다


def apply_decision(item, decision, state, action_log):                                   # 대기 건 · 담당자 결정 · 모의 시스템 · 기록 리스트를 받는 함수
    """담당자의 결정(승인 또는 거절)을 알림에 적용한다. 먼저 결정한 사람에게 권한이 있는지 확인한다.
    담당자의 결정을 받아 처리할 때 쓰고, 결과는 「권한 없음」 · 「실행 완료」 · 「거절 처리」 중 하나로 리턴한다.
    """
    approver = decision["approver"]                                                      # 결정한 담당자 이름 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. is_authorized(approver) 가 거짓이면 (if, not)
    # 5.   reject_unauthorized(item, approver, action_log) 의 결과를 리턴한다
    return finish_decision(item, decision, state, action_log)                            # 권한이 있으면 결정을 적용한다 — 미리 채운 줄


def finish_decision(item, decision, state, action_log):                                  # 대기 건 · 담당자 결정 · 모의 시스템 · 기록 리스트를 받는 함수
    """권한 확인을 통과한 결정을 처리한다. 승인이면 액션을 실행하고, 거절이면 알림을 종료하고 거절 사유를 기록한다.
    권한이 확인된 뒤 결정 내용에 따라 나눠 처리할 때 쓴다.
    """
    approver = decision["approver"]                                                      # 결정한 담당자 이름 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. decision["result"] 가 "승인" 이면 (if, ==)
    # 7.   execute_actions(item, state, action_log, approver) 의 결과를 리턴한다
    change_status(item, "종료")                                                          # 승인이 아니면 거절로 보고 종료로 옮긴다 — 미리 채운 줄
    action_log.append(log_line(item, "전체", "거절됨 (승인: " + approver + " — " + decision["comment"] + ")"))  # 거절 사유를 기록한다 — 미리 채운 줄
    return "거절 처리"                                                                   # 거절 처리를 리턴한다 — 미리 채운 줄
```

**`day02_5-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 실행하면 결과를 출력합니다.

```python
from incident import load_json                                                              # 어제 파일의 함수를 불러온다
from approvals import apply_decision                                                        # 방금 만든 결정 적용 함수를 불러온다

pending = load_json("pending.json")                                                         # 승인 대기 3건을 읽는다
decisions = load_json("decisions.json")                                                     # 담당자 결정을 읽는다
state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}         # 깨끗한 모의 시스템 상태
action_log = []                                                                             # 감사 기록을 담을 빈 리스트

print("--- 단계 1: 승인 대기 건")                                                           # 단계 1 시작을 알리는 줄
for item in pending:                                                                        # 대기 건을 하나씩 꺼낸다
    print(item["id"], item["entity"], "·", item["playbook"], "·", item["why"])              # 번호 · 대상 · 플레이북 · 이유를 출력한다

print("--- 단계 2: 담당자 결정 처리")                                                       # 단계 2 시작을 알리는 줄
for item in pending:                                                                        # 대기 건을 하나씩 꺼낸다
    result_text = "결정 없음"                                                               # 결정이 없으면 이 글자가 남는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. item["id"] 가 decisions 안에 있으면 (if, in)
    # 9.   apply_decision(item, decisions[item["id"]], state, action_log) 의 결과를 result_text 에 담는다
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 3: 처리 뒤 모의 시스템 상태")                                               # 단계 3 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                                  # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                   # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 4: 감사 기록")                                                              # 단계 4 시작을 알리는 줄
for entry in action_log:                                                                    # 기록을 하나씩 꺼낸다
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])      # 인시던트 · 플레이북 · 액션 · 결과를 출력한다
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch audit.py approvals.py day02_5-1_run.py
   ls
   ```
2. **[VS Code]** `audit.py` 1번, `approvals.py` 2 ~ 7번, `day02_5-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「5교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day02_5-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 3줄, 단계 2 도 3줄, 단계 3 은 3줄, 단계 4 는 감사 기록 4줄입니다.
5. **[보고서]** `day02_pm_report.md` 의 `## 5교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 처리 뒤 티켓 수 · 담당자 알림 수 · `분류됨` 으로 남은 알림의 번호를 각각 적어 주세요.
   - (나) 🔍 INC-005 는 결정이 `승인` 인데 실행되지 않았습니다. 단계 2 와 단계 4 의 출력을 근거로 그 이유를 적어 주세요. 그리고 권한 확인이 없을 때 생길 위험도 적어 주세요.
   - (다) 🔍 INC-003 이 승인 대기가 된 이유(단계 1), 거절된 뒤의 상태, 감사 기록에 남은 내용을 각각 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 딕셔너리를 만들어 변수에 저장하기 | `entry = {"incident": item["id"], ..., "result": text}` |
| 리스트 안에 있는지 확인해 참(`True`) 또는 거짓(`False`)을 리턴한다 | `return approver in APPROVERS` |
| 함수 결과를 변수에 담기 | `result = run_action(action, item, state)` |
| 거짓이면 | `if not is_authorized(approver):` |
| 다른 함수의 결과를 그대로 리턴 | `return reject_unauthorized(item, approver, action_log)` · `return execute_actions(item, state, action_log, approver)` |
| 값이 같으면 | `if decision["result"] == "승인":` |
| 키가 있으면 | `if item["id"] in decisions:` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 연결 오류가 나면 최대 3번 시도하고, 실패한 건을 목록으로 모으고, 오늘 만든 하루 흐름 전체 읽기 (실패 처리)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 어젯밤 티켓 서비스가 3분 동안 응답하지 않았습니다. 그 사이 들어온 알림 4건은 계정을 막는 데까지는 됐지만 티켓 생성은 오류로 끝났습니다.
> - **문제**: 프로그램은 알림 한 건을 처리하다 오류가 나면 그 건의 처리가 그대로 멈췄고, 실패했다는 기록도 남기지 않았습니다. 그래서 티켓이 없다는 사실을 다음 날 아침 담당자가 직접 찾기 전까지 아무도 몰랐습니다.
> - **부탁**: 잠깐의 오류는 자동으로 최대 3번까지 다시 시도하고, 그래도 안 되면 「실패」로 기록해서 담당자가 확인할 목록에 올려 주세요.
> - **바뀌는 점**: 요청 한두 번만 연결되지 않는 순간적인 오류는 사람이 처리하지 않아도 자동 재시도로 해결되고, 계속되는 장애만 담당자 확인 목록에 올라옵니다(오늘 실습은 기다림 없이 3번 시도하고, 실제 제품은 시도 사이에 기다립니다). 오늘 샘플에서는 `INC-001` 의 티켓 생성이 3번 모두 실패해서 담당자 확인 목록에 올라갑니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 6.1 실패 처리는 「다시 시도 → 안 되면 기록하고 사람에게 넘기기」다

티켓 서비스 같은 외부 서비스는 가끔 잠깐 응답하지 않습니다. 이럴 때 바로 포기하지 않고 몇 번 다시 해 보는 것이 재시도입니다. 다만 지킬 규칙이 네 가지 있습니다.

| 규칙 | 오늘 실습에서 |
|---|---|
| 잠깐 생긴 오류만 다시 시도한다 (권한이 없다는 오류는 몇 번을 해도 같은 결과다) | 연결 오류(`ConnectionError`)가 날 때만 다시 시도한다 |
| 최대 횟수를 정한다 (서비스가 계속 멈춰 있어도 끝없이 반복하지 않는다) | 처음 시도를 포함해 `MAX_TRIES` 3번 |
| 다시 해도 안전해야 한다 (같은 계정을 두 번 잠그면 안 된다) | 오전의 `safe_run_action` 이 이미 잠긴 계정은 건너뛴다 |
| 끝내 실패하면 숨기지 않는다 | 실패를 기록하고 담당자 확인 목록에 올린다 |

- 오늘 실습은 <mark>서비스가 요청을 받기 전에 실패하는 경우만 흉내 냅니다.</mark> 실제로는 서비스가 티켓을 이미 만들었는데 「만들었다」는 응답만 우리 프로그램에 도착하지 않는 일도 있습니다. 프로그램은 실패로 알고 같은 요청을 다시 보내므로 티켓이 두 개 만들어질 수 있습니다. 이를 막으려면 같은 요청인지 알아보는 장치가 따로 필요합니다.
- **`fail_plan`**: 실습에서 일부러 실패를 일으키려고, 어떤 알림의 어떤 액션이 몇 번 실패할지 미리 적어 둔 딕셔너리입니다. 예: `{"INC-001|티켓 생성": 2}` 는 INC-001 의 티켓 생성이 2번 실패한다는 뜻입니다.
- **`MAX_TRIES`**: 한 액션을 시도하는 최대 횟수이고 값은 3입니다. 처음 시도도 한 번으로 셉니다.

**🐍 문법 상자 — `try` / `except` 는 오류가 나도 정해 둔 줄을 실행해 프로그램이 멈추지 않게 한다**

```python
try:
    raise ConnectionError("티켓 서비스가 응답하지 않음")
except ConnectionError as error:
    print("실패:", error)
print("다음 줄도 실행됨")
```

| 코드 | 뜻 |
|---|---|
| `try:` | 오류가 날 수 있는 부분을 시작한다 |
| `raise ConnectionError(문장)` | 일부러 연결 오류를 일으킨다. 오늘은 장애를 흉내 낼 때만 쓰고 직접 쓰지 않는다 |
| `except ConnectionError as error:` | 그 오류가 나면 여기로 오고, 오류 내용이 `error` 에 저장된다 |
| 위 코드의 출력 | `실패: 티켓 서비스가 응답하지 않음` 다음에 `다음 줄도 실행됨` |

- 오류가 나도 `except` 가 같은 종류의 오류를 받으면 프로그램이 멈추지 않고 다음 줄을 계속 실행합니다.
- `str(error)` 는 오류 내용을 문자열(글자로 된 값)로 바꿉니다.

함수는 파일 네 곳에 나뉘어 있고, 직접 쓰는 곳은 **아홉 군데**(`retry_runner.py` 1 ~ 3번 · `flow.py` 4 · 5번 · `failure_report.py` 6 · 7번 · 실행 파일 8 · 9번)입니다. `try:` 와 `except …:` 줄은 미리 채워져 있고, 그 아래에 들여쓴 줄만 씁니다.

```
retry_runner.py     run_with_retry          : 실행해 보고(1번), 성공하면 시도 횟수를 붙여 리턴한다(2번) / 연결 오류면 오류 문장을 기억한다(3번)
flow.py             run_playbook_with_retry : 결과가 「실패」로 시작하면 실패 표시를 한다 (4 · 5번)
failure_report.py   collect_failures        : 기록에서 「실패」로 시작하는 것만 모은다 (6 · 7번)
실행 파일           day02_6-1_run.py        : 실패 목록을 받고(8번) 출력한다(9번)

하루 흐름(flow.py 의 run_day_flow, 미리 채움) : 알림 하나가 아래 순서로 지나갑니다
  ① 맥락 붙이기(오전 2교시) → ② 경로 정하기(오전 3교시)
  → ③ 경로에 따라 셋 중 하나를 한다: 오탐 종료 | 승인 대기로 멈추기(5교시) | 재시도하며 실행(오전 4교시 + 6교시)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 6-1 · 연결 오류가 나면 최대 3번 시도하고, 실패한 건을 목록으로 모으기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>티켓 서비스가 잠깐 멈추면 프로그램이 그대로 멈추고, 실패한 일이 어디에도 남지 않습니다</mark>.
- **만드는 것**: 재시도(`retry_runner.py`), 실패 표시(`flow.py`), 실패 목록(`failure_report.py`), 목록 출력(`day02_6-1_run.py`).
- **실행하면**: <mark>단계 1: 일시 장애, 단계 2: 서비스 중단, 단계 3: 하루 흐름, 단계 4: 담당자 결정 처리, 단계 5: 하루가 끝난 뒤 모의 시스템 상태, 단계 6: 담당자 확인이 필요한 건의 목록이 나옵니다.</mark>

**🎯 할 일**: 파일 네 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 1 · 2 와 단계 6 을 읽습니다.

**`retry_runner.py`** — 실패를 흉내 내고 다시 시도합니다. 직접 쓰는 곳은 1 ~ 3번입니다.

```python
from safe_runner import safe_run_action                                            # 오전 4교시에 만든 안전한 액션 실행 함수를 불러온다

MAX_TRIES = 3                                                                      # 한 액션을 시도하는 최대 횟수


def flaky_run_action(action, incident, state, fail_plan):                          # 액션 · 인시던트 · 모의 시스템 · 실패 계획을 받는 함수
    """실패 계획에 이 액션이 앞으로 실패할 횟수가 남아 있으면 연결 오류를 일으키고, 없으면 오전의 safe_run_action 으로 실행한다.
    외부 서비스가 잠깐 응답하지 않는 상황을 흉내 낼 때 쓴다.
    """
    key = incident["id"] + "|" + action                                            # 실패 계획에서 찾을 이름 (인시던트 번호 | 액션)
    remaining = fail_plan.get(key, 0)                                              # 이 액션이 앞으로 실패해야 하는 횟수 (없으면 0)
    if remaining > 0:                                                              # 아직 실패해야 하면
        fail_plan[key] = remaining - 1                                             # 남은 실패 횟수를 1 줄이고
        raise ConnectionError("연결 실패: " + action + " 서비스가 응답하지 않음")  # 연결 오류를 일으킨다
    return safe_run_action(action, incident, state)                                # 실패 계획에 없으면 정상으로 실행한다


def run_with_retry(action, incident, state, fail_plan, max_tries):                 # 액션 · 인시던트 · 모의 시스템 · 실패 계획 · 최대 시도 횟수를 받는 함수
    """액션을 실행해 보고, 연결 오류가 나면 최대 횟수까지 다시 시도한다. 성공하면 결과를, 모두 실패하면 실패 문장을 리턴한다.
    외부 서비스가 잠깐 멈춰도 자동 대응이 끝까지 가게 할 때 쓴다.
    """
    last_error = ""                                                                # 마지막 오류 문장 : 처음에는 비어 있다
    for attempt in range(1, max_tries + 1):                                        # 1 번부터 최대 횟수까지 시도 번호를 하나씩 꺼낸다
        try:                                                                       # 오류가 날 수 있는 부분을 시작한다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 1. flaky_run_action(action, incident, state, fail_plan) 의 결과를 result 에 담는다
            # 2. result + " (시도 " + str(attempt) + "회)" 를 리턴한다 (성공하면 여기서 끝난다)
        except ConnectionError as error:                                           # 연결 오류가 나면 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 3. str(error) 를 last_error 에 담는다 (오류 문장을 기억해 두고 다음 시도로 간다)
    return "실패: " + last_error + " (" + str(max_tries) + "회 모두 실패)"         # 모든 시도가 실패했으면 실패 문장을 리턴한다 — 미리 채운 줄
```

**`flow.py`** — 하루 흐름 파일입니다. 줄 끝의 `[오전 2교시]` 같은 표시로 어느 교시에 만든 함수인지 알 수 있습니다. 직접 쓰는 곳은 4 · 5번입니다.

```python
from incident import change_status, match_playbooks                             # 어제 파일의 함수를 불러온다
from enrichment import enrich_incident                                          # 오전 2교시 : 맥락 붙이기
from routing import decide_route, apply_route                                   # 오전 3교시 : 경로 정하기
from approvals import hold_for_approval                                         # 5교시 : 승인 대기로 멈추기
from audit import log_line                                                      # 5교시 : 감사 기록 한 건 만들기
from retry_runner import run_with_retry, MAX_TRIES                              # 6교시 : 재시도하며 실행하기

VIP_REVIEW_ACTIONS = ["담당자 알림", "티켓 생성"]                               # VIP 계정 알림을 담당자가 승인하면 실행할 액션


def run_playbook_with_retry(incident, playbook, state, action_log, fail_plan):  # 인시던트 · 플레이북 · 모의 시스템 · 기록 · 실패 계획을 받는 함수
    """자동으로 해도 되는 플레이북의 액션을 하나씩, 실패하면 다시 시도하며 실행하고 기록한다.
    모두 성공하면 조치됨으로 바꾸고 「실행 완료」를, 하나라도 끝내 실패하면 상태를 그대로 두고 「일부 실패」를 리턴한다.
    """
    incident["playbook"] = playbook["id"]                                       # 기록에 남길 플레이북 번호를 적고
    change_status(incident, "분류됨")                                           # 대응을 시작하기 전에 분류됨으로 옮긴다
    failed = False                                                              # 실패한 액션이 있는지 : 처음에는 없다
    for action in playbook["actions"]:                                          # 액션을 하나씩 꺼낸다
        result = run_with_retry(action, incident, state, fail_plan, MAX_TRIES)  # 재시도하며 실행한다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. result 가 "실패" 로 시작하면 (if, startswith)
        # 5.   failed 에 True 를 담는다 (실패한 액션이 있다고 적는다)
        action_log.append(log_line(incident, action, result))                   # 결과를 기록에 추가한다 — 미리 채운 줄
    if failed:                                                                  # 실패한 액션이 있으면
        return "일부 실패"                                                      # 조치됨으로 옮기지 않고 일부 실패를 리턴한다
    change_status(incident, "조치됨")                                           # 모두 성공했으니 조치됨으로 옮긴다
    return "실행 완료"                                                          # 실행 완료를 리턴한다


def run_day_flow(incidents, registry, users_info, source_ips, trusted_ips, state, action_log, fail_plan):  # 하루 흐름 전체를 받는 함수
    """알림마다 맥락 붙이기 → 경로 정하기 → 경로에 따라 처리하기(오탐 종료 · 승인 대기 · 재시도하며 실행)를 차례로 한다.
    알림마다 결과를 한 줄씩 출력하고, 승인 대기 건의 리스트를 리턴한다.
    """
    pending = []                                                                # 승인 대기 건을 담을 빈 리스트
    route_log = []                                                              # 경로 기록을 담을 빈 리스트
    for incident in incidents:                                                  # 인시던트를 하나씩 꺼낸다
        enrich_incident(incident, users_info, source_ips, trusted_ips)          # [오전 2교시] 맥락을 붙인다
        route, reason = decide_route(incident)                                  # [오전 3교시] 처리 경로와 이유를 정한다
        apply_route(incident, route, reason, route_log)                         # [오전 3교시] 경로를 적용한다 (오탐 종료이면 여기서 닫힌다)
        result_text = "맞는 플레이북 없음"                                      # 처음에는 없다고 적어 둔다
        if route == "오탐 종료":                                                # 오탐으로 닫았으면
            result_text = "오탐 종료"                                           # 오탐 종료라고 적는다
        elif route == "승인 필요":                                              # VIP 계정이라 담당자 승인이 필요하면
            pending.append(hold_for_approval(incident, "VIP 확인", VIP_REVIEW_ACTIONS, "VIP 계정이라 경로가 승인 필요", action_log))  # [5교시] 승인 대기로 멈춘다
            result_text = "승인 대기"                                           # 승인 대기라고 적는다
        else:                                                                   # 기본 경로이면
            for playbook in match_playbooks(incident, registry):                # 맞는 플레이북을 하나씩 꺼낸다
                if playbook["approval"] != "자동":                              # 플레이북이 승인을 요구하면
                    pending.append(hold_for_approval(incident, playbook["id"], playbook["actions"], "플레이북 승인 값이 " + playbook["approval"], action_log))  # [5교시] 승인 대기로 멈춘다
                    result_text = "승인 대기"                                   # 승인 대기라고 적는다
                else:                                                           # 자동이면
                    result_text = run_playbook_with_retry(incident, playbook, state, action_log, fail_plan)  # [6교시] 재시도하며 실행한다
        print(incident["id"], incident["entity"], "->", result_text, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다
    return pending                                                              # 승인 대기 리스트를 리턴한다
```

**`failure_report.py`** — 실패한 기록만 모읍니다. 직접 쓰는 곳은 6 · 7번입니다.

```python
def collect_failures(action_log):  # 감사 기록 리스트를 받는 함수
    """감사 기록에서 결과가 「실패」로 시작하는 기록만 골라 리스트로 리턴한다.
    담당자가 아침에 가장 먼저 볼 「확인이 필요한 건」 목록을 만들 때 쓴다.
    """
    failures = []                  # 실패한 기록을 담을 빈 리스트
    for entry in action_log:       # 기록을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. entry["result"] 가 "실패" 로 시작하면 (if, startswith)
        # 7.   failures 에 entry 를 추가한다 (append)
    return failures                # 실패한 기록 리스트를 리턴한다
```

**`day02_6-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, INCIDENTS_PATH                                              # 어제 파일의 함수를 불러온다
from approvals import apply_decision                                                        # 5교시에 만든 결정 적용 함수를 불러온다
from retry_runner import run_with_retry, MAX_TRIES                                          # 방금 만든 재시도 함수를 불러온다
from flow import run_day_flow                                                               # 하루 흐름 함수를 불러온다
from failure_report import collect_failures                                                 # 실패한 기록을 모으는 함수를 불러온다


def new_state():                                                                            # 인자가 없는 함수
    """잠긴 계정 · 차단한 IP · 티켓이 모두 비어 있는 모의 시스템 상태를 새로 만들어 리턴한다.
    실험마다 깨끗한 상태에서 시작하고 싶을 때 쓴다.
    """
    state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}     # 비어 있는 상태 딕셔너리
    return state                                                                            # 상태를 리턴한다


incidents = load_json(INCIDENTS_PATH)                                                       # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                                                   # 계정 정보 파일을 읽는다
source_ips = load_json("source_ips.json")                                                   # 접속 IP 파일을 읽는다
trusted_ips = load_json("trusted_ips.json")                                                 # 신뢰 IP 파일을 읽는다
registry = load_json("config/playbook_registry.json")                                       # 플레이북 세 건을 읽는다
decisions = load_json("decisions.json")                                                     # 담당자 결정을 읽는다

print("--- 단계 1: 일시 장애 — 티켓 서비스가 2번 실패한 뒤 복구")                           # 단계 1 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
fail_plan = {"INC-001|티켓 생성": 2}                                                        # INC-001 의 티켓 생성이 2번 실패하게 한다
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)             # 재시도하며 실행한다
print(result)                                                                               # 결과 문장을 출력한다
print("만든 티켓:", len(state["tickets"]), "건")                                            # 만든 티켓 수를 출력한다

print("--- 단계 2: 서비스 중단 — 티켓 서비스가 계속 실패")                                  # 단계 2 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
fail_plan = {"INC-001|티켓 생성": 99}                                                       # INC-001 의 티켓 생성이 계속 실패하게 한다
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)             # 재시도하며 실행한다
print(result)                                                                               # 결과 문장을 출력한다
print("만든 티켓:", len(state["tickets"]), "건")                                            # 만든 티켓 수를 출력한다

print("--- 단계 3: 하루 흐름 — 티켓 서비스가 계속 실패하는 상황")                           # 단계 3 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
action_log = []                                                                             # 감사 기록을 담을 빈 리스트
fail_plan = {"INC-001|티켓 생성": 99}                                                       # INC-001 의 티켓 생성이 계속 실패하게 한다
pending = run_day_flow(incidents, registry, users_info, source_ips, trusted_ips, state, action_log, fail_plan)  # 하루 흐름을 실행한다

print("--- 단계 4: 담당자 결정 처리")                                                       # 단계 4 시작을 알리는 줄
for item in pending:                                                                        # 승인 대기 건을 하나씩 꺼낸다
    result_text = apply_decision(item, decisions[item["id"]], state, action_log)            # 담당자 결정을 적용한다
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 5: 하루가 끝난 뒤 모의 시스템 상태")                                        # 단계 5 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                                  # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                   # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 6: 담당자 확인이 필요한 건")                                                # 단계 6 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. collect_failures(action_log) 의 결과를 failures 에 담는다
for entry in failures:                                                                      # 실패한 기록을 하나씩 꺼낸다
    incident_id = entry["incident"]                                                         # 실패한 인시던트 번호
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 9. incident_id · entry["action"] · ":" · entry["result"] 를 출력한다 (print)
for item in pending:                                                                        # 승인 대기 건을 하나씩 꺼낸다
    if item["status"] == "분류됨":                                                          # 아직 처리되지 않았으면
        print(item["id"], "승인 대기 :", item["why"])                                       # 승인 대기 건과 이유를 출력한다
```

**순서**

1. **[터미널]** 파일 네 개를 만들고 붙여 넣습니다. <mark>5교시의 `audit.py` · `approvals.py` 가 완성돼 있어야(`flow.py` 가 이 두 파일을 불러오기 때문)</mark> 합니다.
   ```bash
   pwd
   touch retry_runner.py flow.py failure_report.py day02_6-1_run.py
   ls
   ```
2. **[VS Code]** `retry_runner.py` 1 ~ 3번, `flow.py` 4 · 5번, `failure_report.py` 6 · 7번, `day02_6-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「6교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day02_6-1_run.py
   ```
4. 출력은 여섯 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 2줄, 단계 2 도 2줄, 단계 3 은 5줄, 단계 4 는 3줄, 단계 5 는 3줄, 단계 6 은 2줄입니다.
5. **[보고서]** `day02_pm_report.md` 의 `## 6교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 단계 3 에서 `일부 실패` · `승인 대기` · `오탐 종료`(오탐: 위험하지 않은데 위험하다고 잘못 알린 경우) 인 알림의 번호를 각각 적어 주세요.
   - (나) 🔍 단계 1 과 2 는 같은 `run_with_retry` 인데 결과가 다릅니다. 두 단계의 `fail_plan` 값을 근거로 이유를 적어 주세요. 그리고 최대 횟수가 없으면 서비스가 계속 멈춰 있을 때 어떤 문제가 생기는지도 적어 주세요.
   - (다) 🔍 단계 3 에서 INC-001 은 계정은 잠겼는데 상태가 `조치됨` 이 아닙니다. 그 이유를 적어 주세요. 또 단계 6 의 출력이 담당자에게 무엇을 알려 주는지 적어 주세요. 마지막으로, 같은 `state` 로 다시 처리해도 `dami` 가 두 번 잠기지 않는 이유를 오전 4교시에서 만든 장치와 연결해 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 함수 결과를 변수에 담기 | `result = flaky_run_action(action, incident, state, fail_plan)` |
| 숫자를 글자로 바꿔 이어 붙이기 | `result + " (시도 " + str(attempt) + "회)"` |
| 오류 내용을 문자열로 바꿔 저장하기 | `last_error = str(error)` |
| 글자가 어떤 말로 시작하면 | `if result.startswith("실패"):` |
| 리스트에 추가 | `failures.append(entry)` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 오늘 한 일을 저장소(repository, 리포지터리: 깃허브에 코드를 모아 두는 곳)에 올리는 마무리입니다.</mark> 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, 먼저 `pwd` 로 위치를 확인합니다. 결과가 `soar_response` 로 끝날 때만 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「오늘 만든 맥락 붙이기 · 경로 정하기 · 안전장치 · 승인 · 재시도 코드를 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add`(올릴 파일 고르기) → `git commit`(설명을 붙여 저장) → `git push`(깃허브로 올리기) 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `soar_response` 폴더에 `enrichment.py` · `routing.py` · `safe_runner.py` · `audit.py` · `approvals.py` · `retry_runner.py` · `flow.py` · `failure_report.py` 가 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `soar_response` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day02_am_report.md` 와 `day02_pm_report.md` 의 모든 질문에서 `답:` 뒤와 코드 상자가 모두 채워져 있는지도 봅니다. 단, 마무리 (가)는 3번에서 채우니 지금은 비어 있어도 됩니다.

   ① 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark>`soar_response` 로 끝나야</mark> 합니다.

   ② 폴더 안의 파일을 봅니다.

   ```bash
   ls
   ```

   - 하는 일: 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: `enrichment.py` · `routing.py` · `safe_runner.py` · `audit.py` · `approvals.py` · `retry_runner.py` · `flow.py` · `failure_report.py` · `decisions.json` · `config` 가 보이면 됩니다.

1. **[터미널]** 깃허브 저장소는 `security-agent-toolkit` 폴더 전체이므로, 그 폴더로 옮깁니다. 0번의 `pwd` 결과가 `soar_response` 로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.

   ① 한 단계 위 폴더로 이동합니다.

   ```bash
   cd ..
   ```

   - 하는 일: 한 단계 위 폴더로 이동합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark>`…/security-agent-toolkit` 으로 끝나면</mark> 됩니다. 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark>빨간 글씨 줄에 `.env`(API 키가 들어 있는 파일)나 `.venv`(내 PC 에서만 쓰는 가상환경 폴더)가 보이면 올리지 말고(`.env` 를 올리면 키가 인터넷에 공개되기 때문입니다),</mark> 아래 안내대로 `.gitignore` 를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다. `soar_response/` 아래의 새 파일들이 보이면 됩니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore`(깃이 올리지 않을 파일 이름을 적어 두는 파일)를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `soar_response/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.

3. **[보고서]** `day02_pm_report.md` 의 `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 올릴 목록에 추가하고(`add`), 설명을 붙여 저장하고(`commit`), 깃허브로 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 올릴 목록에 추가합니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 이번에 올릴 목록에 추가합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add SOAR enrichment, routing, safety guards, approvals and retry"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark>`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull`(깃허브의 새 기록을 내 PC 로 받아 오는 명령)을 입력해 받아 온 뒤 `git push` 를 다시 합니다.
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다.

5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `soar_response` 폴더를 열고, VS Code 왼쪽 목록의 `soar_response` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
   - 빠진 이름이 있으면 VS Code 왼쪽 목록의 `soar_response` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `soar_response` 안으로 옮기고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `soar_response` 폴더와 파일이 있는지 확인 |

---

## 오늘 오후 마무리

| 확인 | 문제 |
|---|---|
| 담당자 결정을 적용하고 권한 없는 승인은 막았다 | 오후 5-1 |
| 연결 오류가 나면 최대 3번 시도하고, 하루 흐름 전체를 한 번에 읽었다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

오늘은 모의 시스템에서 실행했습니다. <mark>다음 수업에서는 계정 잠금 · IP 차단을 모의 시스템에서 실제로 하고, 확인하고, 되돌리는 것까지 만듭니다.</mark> 오늘 만든 맥락 붙이기와 경로 정하기는 11/11 오후에 다시 씁니다.

---


---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 5-1

**채운 코드** (한 예)

`audit.py` 의 1번입니다.

```python
    # 1. 키 "incident"(item 의 "id"), "playbook"(item 의 "playbook"), "action"(action), "result"(text) 를 가진 딕셔너리를 entry 에 담는다
    entry = {"incident": item["id"], "playbook": item["playbook"], "action": action, "result": text}  # 기록 한 건을 딕셔너리로 만든다
```

`approvals.py` 의 2 ~ 7번입니다.

```python
    # 2. approver 가 APPROVERS 안에 있는지(in)의 결과를 리턴한다
    return approver in APPROVERS                                   # 권한 목록 안에 있는지 확인한 결과를 리턴한다
        # 3. run_action(action, item, state) 의 결과를 result 에 담는다
        result = run_action(action, item, state)                   # 액션을 실행해 결과 문장을 받는다
    # 4. is_authorized(approver) 가 거짓이면 (if, not)
    if not is_authorized(approver):                                # 승인 권한이 없으면
    # 5.   reject_unauthorized(item, approver, action_log) 의 결과를 리턴한다
        return reject_unauthorized(item, approver, action_log)     # 기록만 남기고 멈춘다
    # 6. decision["result"] 가 "승인" 이면 (if, ==)
    if decision["result"] == "승인":                               # 결정이 승인이면
    # 7.   execute_actions(item, state, action_log, approver) 의 결과를 리턴한다
        return execute_actions(item, state, action_log, approver)  # 액션을 실행하고 그 결과를 리턴한다
```

`day02_5-1_run.py` 의 8 · 9번입니다.

```python
    # 8. item["id"] 가 decisions 안에 있으면 (if, in)
    if item["id"] in decisions:                                                       # 이 건에 대한 담당자 결정이 있으면
    # 9.   apply_decision(item, decisions[item["id"]], state, action_log) 의 결과를 result_text 에 담는다
        result_text = apply_decision(item, decisions[item["id"]], state, action_log)  # 결정을 적용한다
```

**결과**

- (가) 출력은 다음과 같습니다. 티켓은 <mark style="background:#bde3ff">**1건**</mark>, 담당자 알림은 <mark style="background:#bde3ff">**1건**</mark>이고, `분류됨` 으로 남은 건은 <mark style="background:#bde3ff">**INC-005**</mark> 입니다.

```
--- 단계 1: 승인 대기 건
INC-002 seoyeon · PB-002 · 플레이북 승인 값이 담당자 승인 필요
INC-003 gaeun · VIP 확인 · VIP 계정이라 경로가 승인 필요
INC-005 198.51.100.90 · PB-003 · 플레이북 승인 값이 담당자 승인 필요
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 실행 완료 (상태: 조치됨)
INC-003 gaeun -> 거절 처리 (상태: 종료)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
--- 단계 3: 처리 뒤 모의 시스템 상태
잠긴 계정: []
차단한 IP: []
티켓: 1 건 · 담당자 알림: 1 건
--- 단계 4: 감사 기록
INC-002 PB-002 담당자 알림 : 담당자 알림 전송 (승인: kim.sec)
INC-002 PB-002 티켓 생성 : 티켓 TCK-1 생성 (승인: kim.sec)
INC-003 VIP 확인 전체 : 거절됨 (승인: kim.sec — 계정 관리자의 정상 작업으로 확인됨)
INC-005 PB-003 전체 : 권한 없음 — 승인 시도: intern01
```

- (나) INC-005 는 결정한 `intern01` 이 <mark style="background:#bde3ff">`APPROVERS` 에 없어서</mark> 실행되지 않았습니다.
  - 근거: 단계 2 에 `권한 없음 (상태: 분류됨)`, 단계 3 에 `차단한 IP: []`, 단계 4 에 `권한 없음 — 승인 시도: intern01` 이 나옵니다.
  - 위험: 이 확인이 없으면 권한 없는 사람이 `승인` 만 눌러도 IP 가 차단됩니다.
  - 같은 IP 를 여러 사람이 쓰면 정상 사용자의 업무가 막힙니다.
  - 승인 권한이 있는 담당자의 허락 없이 차단한 것이라, 왜 차단했는지 나중에 설명할 수 없습니다.
- (다) INC-003 은 `pending.json` 의 이유가 <mark style="background:#bde3ff">`VIP 계정이라 경로가 승인 필요`</mark> 입니다. 오전 3교시에서 VIP 계정(막히면 업무에 큰 영향을 주는 중요한 계정)은 담당자가 확인하기 전에는 처리하지 않도록 `승인 필요` 경로로 보냈기 때문입니다.
  - 거절된 뒤 상태는 <mark style="background:#bde3ff">`종료`</mark> 이고, 감사 기록에 `거절됨 (승인: kim.sec — 계정 관리자의 정상 작업으로 확인됨)` 이 남습니다. 누가 어떤 사유로 닫았는지 사고 뒤에 설명할 수 있습니다.

**왜**: <mark>승인은 「누가 눌렀는지 확인」과 「누가 눌렀는지 기록」이 둘 다 있어야 믿을 수 있습니다.</mark> 누른 사람이 누구인지 확인하지 않고 실행하면, 아무나 자동 대응을 실행시킬 수 있습니다. 누가 허락했는지 기록이 없으면, 나중에 누구 책임인지 설명할 수 없습니다.

**자주 틀리는 곳**

- 1번을 비워 두면 기록 한 건을 만들지 못해 오류가 납니다. <mark>**`entry` 변수에 딕셔너리를 저장해 두지 않으면 `return entry` 가 실패합니다.**</mark>

```
--- 단계 2: 담당자 결정 처리
NameError: name 'entry' is not defined
```

- 2번을 비워 두면 `is_authorized` 가 `return` 이 없어 `None`(값 없음)을 리턴하고, `if not None` 이 참이 되어 <mark>**권한 있는 담당자도 모두 「권한 없음」이 됩니다.**</mark>

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 권한 없음 (상태: 분류됨)
INC-003 gaeun -> 권한 없음 (상태: 분류됨)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
```

- 4 · 5번을 비워 두면 오류는 나지 않지만 <mark>**권한 없는 `intern01` 의 승인으로 IP 가 차단됩니다.**</mark> 이 실수를 하면 단계 2 에서 INC-005 가 `실행 완료` 로 나옵니다.

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 실행 완료 (상태: 조치됨)
INC-003 gaeun -> 거절 처리 (상태: 종료)
INC-005 198.51.100.90 -> 실행 완료 (상태: 조치됨)
--- 단계 3: 처리 뒤 모의 시스템 상태
잠긴 계정: []
차단한 IP: ['198.51.100.90']
티켓: 2 건 · 담당자 알림: 1 건
```

- 6 · 7번을 비워 두면 <mark>**승인한 건도 모두 거절 처리됩니다.**</mark>

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 거절 처리 (상태: 종료)
INC-003 gaeun -> 거절 처리 (상태: 종료)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
```

- 7번에서 `return` 을 빼고 `execute_actions(…)` 만 호출하면 <mark>**`return` 이 없으면 함수가 거기서 끝나지 않습니다. 그래서 실행한 다음 줄도 실행되어 거절 기록까지 남습니다.**</mark> INC-002 가 `거절 처리` 인데 상태는 `조치됨` 이고, 단계 4 에 실행 기록과 거절 기록이 함께 남습니다. 서로 맞지 않는 이런 결과가 나오면 이 실수입니다.

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 거절 처리 (상태: 조치됨)
INC-003 gaeun -> 거절 처리 (상태: 종료)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
…
--- 단계 4: 감사 기록
INC-002 PB-002 담당자 알림 : 담당자 알림 전송 (승인: kim.sec)
INC-002 PB-002 티켓 생성 : 티켓 TCK-1 생성 (승인: kim.sec)
INC-002 PB-002 전체 : 거절됨 (승인: kim.sec — 대량 다운로드 사유를 확인해야 함)
INC-003 VIP 확인 전체 : 거절됨 (승인: kim.sec — 계정 관리자의 정상 작업으로 확인됨)
INC-005 PB-003 전체 : 권한 없음 — 승인 시도: intern01
```

- 6번에서 `==` 대신 `!=` 를 쓰면 거꾸로 동작합니다. <mark>**승인한 건은 종료되고, 거절한 건이 실행됩니다.**</mark>

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 거절 처리 (상태: 종료)
INC-003 gaeun -> 실행 완료 (상태: 조치됨)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
```

- 8 · 9번을 비워 두면 <mark>**모든 건이 「결정 없음」으로 남습니다.**</mark>

```
--- 단계 2: 담당자 결정 처리
INC-002 seoyeon -> 결정 없음 (상태: 분류됨)
INC-003 gaeun -> 결정 없음 (상태: 분류됨)
INC-005 198.51.100.90 -> 결정 없음 (상태: 분류됨)
```

**관제에서는**: 승인 요청을 받으면 가장 먼저 「누른 사람이 승인 권한이 있는가」를 확인합니다. <mark>승인 · 거절 · 권한 없는 시도를 같은 감사 기록에 남기면</mark> 사고가 난 뒤에 누가 무엇을 허락했는지 한 목록에서 다시 확인할 수 있습니다.

---

### 정답 6-1

**채운 코드** (한 예)

`retry_runner.py` 의 1 ~ 3번입니다.

```python
            # 1. flaky_run_action(action, incident, state, fail_plan) 의 결과를 result 에 담는다
            result = flaky_run_action(action, incident, state, fail_plan)  # 액션을 실행해 결과를 받는다
            # 2. result + " (시도 " + str(attempt) + "회)" 를 리턴한다 (성공하면 여기서 끝난다)
            return result + " (시도 " + str(attempt) + "회)"               # 성공하면 시도 횟수를 붙여 리턴하고 끝낸다
            # 3. str(error) 를 last_error 에 담는다 (오류 문장을 기억해 두고 다음 시도로 간다)
            last_error = str(error)                                        # 오류 문장을 기억해 두고 다음 시도로 간다
```

`flow.py` 의 4 · 5번입니다.

```python
        # 4. result 가 "실패" 로 시작하면 (if, startswith)
        if result.startswith("실패"):  # 결과 문장이 「실패」로 시작하면
        # 5.   failed 에 True 를 담는다 (실패한 액션이 있다고 적는다)
            failed = True              # 실패한 액션이 있다고 적는다
```

`failure_report.py` 의 6 · 7번입니다.

```python
        # 6. entry["result"] 가 "실패" 로 시작하면 (if, startswith)
        if entry["result"].startswith("실패"):  # 결과 문장이 「실패」로 시작하면
        # 7.   failures 에 entry 를 추가한다 (append)
            failures.append(entry)              # 실패한 기록을 리스트에 추가한다
```

`day02_6-1_run.py` 의 8 · 9번입니다.

```python
# 8. collect_failures(action_log) 의 결과를 failures 에 담는다
failures = collect_failures(action_log)                        # 실패한 기록을 모은다
    # 9. incident_id · entry["action"] · ":" · entry["result"] 를 출력한다 (print)
    print(incident_id, entry["action"], ":", entry["result"])  # 실패한 액션을 출력한다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 3 에서 `일부 실패` 는 <mark style="background:#bde3ff">**INC-001**</mark>, `승인 대기` 는 <mark style="background:#bde3ff">**INC-002 · INC-003 · INC-005**</mark>, `오탐 종료` 는 <mark style="background:#bde3ff">**INC-004**</mark> 입니다.

```
--- 단계 1: 일시 장애 — 티켓 서비스가 2번 실패한 뒤 복구
티켓 TCK-1 생성 (시도 3회)
만든 티켓: 1 건
--- 단계 2: 서비스 중단 — 티켓 서비스가 계속 실패
실패: 연결 실패: 티켓 생성 서비스가 응답하지 않음 (3회 모두 실패)
만든 티켓: 0 건
--- 단계 3: 하루 흐름 — 티켓 서비스가 계속 실패하는 상황
INC-001 dami -> 일부 실패 (상태: 분류됨)
INC-002 seoyeon -> 승인 대기 (상태: 분류됨)
INC-003 gaeun -> 승인 대기 (상태: 분류됨)
INC-004 jiwoo -> 오탐 종료 (상태: 종료)
INC-005 198.51.100.90 -> 승인 대기 (상태: 분류됨)
--- 단계 4: 담당자 결정 처리
INC-002 seoyeon -> 실행 완료 (상태: 조치됨)
INC-003 gaeun -> 거절 처리 (상태: 종료)
INC-005 198.51.100.90 -> 권한 없음 (상태: 분류됨)
--- 단계 5: 하루가 끝난 뒤 모의 시스템 상태
잠긴 계정: ['dami']
차단한 IP: []
티켓: 1 건 · 담당자 알림: 1 건
--- 단계 6: 담당자 확인이 필요한 건
INC-001 티켓 생성 : 실패: 연결 실패: 티켓 생성 서비스가 응답하지 않음 (3회 모두 실패)
INC-005 승인 대기 : 플레이북 승인 값이 담당자 승인 필요
```

- (나) 단계 1 의 `fail_plan` 은 <mark style="background:#bde3ff">`{"INC-001|티켓 생성": 2}`</mark> 라서 2번 실패한 뒤 3번째 시도에서 성공합니다(`시도 3회`). 단계 2 의 값은 <mark style="background:#bde3ff">`99`</mark> 라서 3번 모두 실패합니다. 같은 코드라도 서비스 상태에 따라 결과가 다릅니다.
  - 최대 횟수가 없으면 서비스가 계속 멈춰 있을 때 같은 요청을 끝없이 보내서 대응 전체가 멈춥니다.
  - 이미 멈춘 서비스에 요청을 계속 보내면 복구도 늦어집니다.
  - 실제로는 서비스가 복구될 시간을 주려고, 시도 사이의 기다리는 시간을 점점 늘립니다. 오늘 실습은 기다림 없이 횟수만 정합니다.
- (다) INC-001 은 계정 잠금은 성공했고 티켓 생성은 3번 모두 실패했습니다. <mark style="background:#bde3ff">모든 액션이 성공한 것이 아니므로 `조치됨` 으로 옮기지 않고 `분류됨` 에 남기며 `일부 실패` 를 리턴합니다.</mark>
  - 단계 6 의 `INC-001 티켓 생성 : 실패: …` 줄은 담당자에게 「이 알림의 티켓이 아직 없다」는 사실과 이유를 알려 줍니다.
  - 같은 `state` 에서 다시 처리해도 `dami` 가 두 번 잠기지 않는 이유는, 오전 4교시의 `safe_run_action` 이 이미 잠긴 계정을 <mark style="background:#bde3ff">「건너뜀: 이미 잠겨 있음」</mark> 으로 리턴하기 때문입니다.
  - 오늘 실행 파일은 실행할 때마다 `state` 를 새로 만듭니다. 그래서 `dami` 가 두 번 잠기지 않는 모습은 같은 `state` 로 한 번 더 처리할 때만 볼 수 있습니다.
  - 티켓과 담당자 알림은 오늘 코드가 중복을 막지 않습니다. 같은 `state` 로 다시 처리하면 한 번 더 만들어집니다.

**왜**: <mark>잠깐 생긴 실패는 정해진 횟수까지 다시 시도해서 해결하고, 끝내 실패하면 숨기지 않고 기록해 사람에게 넘겨야 합니다.</mark> 그래야 자동 대응이 일부만 실행된 채 아무도 모르게 남는 일이 없습니다.

**자주 틀리는 곳**

- `try` 아래를 비워 둔 채 실행하면 파이썬이 실행 전에 멈춥니다. `IndentationError`(인덴테이션 에러: 들여쓰기 오류)로 시작하는 오류입니다(문구는 버전마다 다릅니다).
- 3번 자리에 `pass`(아무 일도 하지 않는 파이썬 문장)만 써 두면 오류는 나지 않지만 <mark>**실패 문장에 이유가 비어 나옵니다.**</mark> 담당자가 왜 실패했는지 알 수 없습니다. 아예 비워 두면 `except` 아래가 비어 `IndentationError` 가 납니다.

```
--- 단계 2: 서비스 중단 — 티켓 서비스가 계속 실패
실패:  (3회 모두 실패)
```

- 2번에서 `return` 대신 `print(result)` 를 쓰면 <mark>**성공했는데도 함수가 끝나지 않습니다. `print` 는 화면에 보여 줄 뿐 함수를 끝내지 않으므로, 반복이 계속되다가 마지막에 실패 문장을 리턴합니다.**</mark> 단계 1 에서 `티켓 TCK-1 생성` 다음에 `실패: …` 가 이어서 나오는 것이 이 실수의 결과입니다.

```
--- 단계 1: 일시 장애 — 티켓 서비스가 2번 실패한 뒤 복구
티켓 TCK-1 생성
실패: 연결 실패: 티켓 생성 서비스가 응답하지 않음 (3회 모두 실패)
만든 티켓: 1 건
```

- 4 · 5번을 비워 두면 오류는 나지 않지만 <mark>**티켓 생성이 실패했는데도 INC-001 이 `실행 완료 (상태: 조치됨)` 으로 나옵니다.**</mark> 단계 3 은 성공이라고 하는데 단계 6 은 실패라고 합니다. 서로 맞지 않는 이런 결과가 나오면 이 실수입니다.

```
--- 단계 3: 하루 흐름 — 티켓 서비스가 계속 실패하는 상황
INC-001 dami -> 실행 완료 (상태: 조치됨)
INC-002 seoyeon -> 승인 대기 (상태: 분류됨)
INC-003 gaeun -> 승인 대기 (상태: 분류됨)
INC-004 jiwoo -> 오탐 종료 (상태: 종료)
INC-005 198.51.100.90 -> 승인 대기 (상태: 분류됨)
…
--- 단계 6: 담당자 확인이 필요한 건
INC-001 티켓 생성 : 실패: 연결 실패: 티켓 생성 서비스가 응답하지 않음 (3회 모두 실패)
INC-005 승인 대기 : 플레이북 승인 값이 담당자 승인 필요
```

- 6 · 7번 자리에 `pass` 만 써 두면 <mark>**실패한 액션이 담당자 확인 목록에서 빠집니다.**</mark> 단계 6 에 `승인 대기` 한 건만 나옵니다. 아예 비워 두면 `for` 아래가 비어 `IndentationError` 가 납니다.

```
--- 단계 6: 담당자 확인이 필요한 건
INC-005 승인 대기 : 플레이북 승인 값이 담당자 승인 필요
```

- 8번을 비워 두면 `failures` 가 만들어지지 않아 오류가 납니다(`NameError`, 네임 에러: 만들지 않은 이름을 쓸 때 나는 오류). 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 붙을 수 있습니다.

```
NameError: name 'failures' is not defined
```

**관제에서는**: 자동 대응을 켤 때는 「외부 서비스가 실패하면 어디까지 다시 시도하고, 그 뒤에는 누구에게 알리는가」를 먼저 정합니다. <mark>실패한 건의 목록은 담당자가 아침에 가장 먼저 보는 목록</mark>입니다. 실제 제품에서도 정해진 시간 안에 응답이 오지 않거나(타임아웃) 서버 오류(서비스 쪽 문제로 요청을 처리하지 못했다는 응답)가 나면, 정해 둔 규칙대로 같은 요청을 다시 보냅니다. 예를 들어 Microsoft Sentinel(보안 관제 제품)의 플레이북이 쓰는 Azure Logic Apps(자동화 서비스)가 그렇게 합니다.

---

### 정답 마무리

- (가) 한 예: <mark>`git status` 에서 `.env` 와 `.venv` 가 보이지 않았습니다.</mark> `__pycache__` 가 보여서 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 다시 확인했습니다.
- 깃허브 `soar_response` 폴더에 오늘 만든 `.py` 파일이 보이면 됩니다.
