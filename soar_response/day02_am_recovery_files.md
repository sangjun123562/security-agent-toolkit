# 11/10(화) 오전 · 5과목 자동 대응(SOAR) ② — 복구 파일 모음 (어제 파일이 없는 사람만)

오늘 2 · 3 · 4교시는 11/9 오후에 만든 파일을 불러 씁니다. <mark>그 파일을 이미 가지고 있으면 이 문서는 받지 않아도 됩니다.</mark> 11/9 오후에 결석했거나 파일을 지웠거나 완성하지 못한 사람만, **없는 파일만** 아래 순서로 만듭니다.

- 이 문서의 파일은 모두 `soar_response` 폴더 바로 아래에 둡니다.
- 오늘 안내(`day02_am_context_route_safety.md`)의 📎 줄에서 「복구 파일 모음」이라고 적힌 파일이 여기에 있습니다.
- 파일 내용은 어제 안내의 완성본과 같습니다. 이미 가진 파일은 건너뛰고, 내 파일과 비교하는 데만 써도 됩니다.

| 파일 | 만든 곳 | 오늘 쓰는 곳 | 이 문서에서 |
|---|---|---|---|
| `incident_samples.json` | 11/9 오후 시작하기 | 2 · 3 · 4교시 | 2번 |
| `incident.py` | 11/9 오후 6교시 | 2 · 3 · 4교시 | 3번 |
| `playbook_runner.py` | 11/9 오후 6교시 | 4교시 | 4번 |
| `config/playbook_registry.json` | 11/9 오후 5교시 | 4교시 | 이 문서에 없습니다. `complete_files.md` 의 1절로 만듭니다(오늘 안내의 시작하기 6번에서 값을 확인합니다) |

## 1. 위치 확인과 빈 파일 만들기

**[터미널]** 먼저 위치를 확인합니다.

```bash
pwd
ls
```

- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 이름 보기
- <mark>`pwd` 가 `…/soar_response` 로 끝나야</mark> 합니다. `soar_response` 폴더가 없으면 `security-agent-toolkit` 폴더에서 `mkdir soar_response` 로 만들고 `cd soar_response` 로 들어간 뒤 시작합니다.

**[터미널]** 빈 파일을 만듭니다. 이미 있는 파일은 `touch` 가 그대로 두고, `config` 폴더가 이미 있으면 `mkdir` 가 「File exists」(파일 이그지스츠: 이미 있다는 뜻의 영어 메시지)라고 알려 주는데 그대로 넘어갑니다.

```bash
mkdir config
touch incident_samples.json incident.py playbook_runner.py
ls
```

- 명령 풀이: `mkdir 폴더이름` 새 폴더 만들기 · `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 이름 보기
- 없는 파일만 열어 붙여 넣습니다. **같은 이름의 파일이 이미 있으면 건너뜁니다.**

## 2. 알림 5건 — `incident_samples.json`

4과목 점수 파일에 인시던트 번호(`id`)와 처음 상태(`status`)를 붙인 알림 5건입니다. 처음 상태는 모두 `탐지됨` 입니다.

```
[
  {
    "id": "INC-001",
    "entity": "dami",
    "grade": "high",
    "score": 60,
    "reasons": [
      "퇴사한 계정"
    ],
    "status": "탐지됨"
  },
  {
    "id": "INC-002",
    "entity": "seoyeon",
    "grade": "mid",
    "score": 45,
    "reasons": [
      "평소와 다른 IP",
      "대량 다운로드"
    ],
    "status": "탐지됨"
  },
  {
    "id": "INC-003",
    "entity": "gaeun",
    "grade": "mid",
    "score": 40,
    "reasons": [
      "규칙은 허용인데 서버가 거절",
      "여러 로그 연결"
    ],
    "status": "탐지됨"
  },
  {
    "id": "INC-004",
    "entity": "jiwoo",
    "grade": "mid",
    "score": 35,
    "reasons": [
      "업무 시간 밖 로그인",
      "평소와 다른 IP"
    ],
    "status": "탐지됨"
  },
  {
    "id": "INC-005",
    "entity": "198.51.100.90",
    "grade": "low",
    "score": 30,
    "reasons": [
      "경로 스캔"
    ],
    "status": "탐지됨"
  }
]
```

## 3. 도구 모음 — `incident.py`

상태 바꾸기 · 맞는 플레이북 찾기 · 액션 하나 실행하기 · 감사 기록(audit log, 오딧 로그: 누가 언제 무엇을 했는지 남긴 기록) 한 건 만들기 함수가 들어 있습니다. 학생이 쓰는 줄은 없습니다.

```python
import json                                                                       # JSON 파일을 읽고 쓰기 위해 json 을 불러온다
from datetime import datetime                                                     # 감사 기록에 시각을 적기 위해 datetime 을 불러온다

INCIDENTS_PATH = "incident_samples.json"                                          # 읽을 인시던트 파일 이름
REGISTRY_PATH = "config/playbook_registry.json"                                   # 읽을 플레이북 등록 파일 이름
STATE_PATH = "system_state.json"                                                  # 실행 결과 상태를 저장할 파일 이름
LOG_PATH = "action_log.json"                                                      # 감사 기록을 저장할 파일 이름
GRADE_ORDER = {"low": 1, "mid": 2, "high": 3}                                     # 등급을 크기를 비교할 수 있는 숫자로 바꾸는 딕셔너리
TRANSITIONS = {                                                                   # 상태마다 다음에 갈 수 있는 상태의 리스트
    "탐지됨": ["분류됨"],
    "분류됨": ["조치됨", "종료"],
    "조치됨": ["보고됨"],
    "보고됨": ["종료"],
    "종료": [],
}


def load_json(path):                                                              # 파일 경로를 받는 함수
    """JSON 파일을 읽어 리스트나 딕셔너리로 리턴한다.
    인시던트와 플레이북 등록 파일을 읽을 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:                                    # 파일을 읽기 모드로 연다
        data = json.load(file)                                                    # JSON 글자를 파이썬 값으로 바꾼다
    return data                                                                   # 읽은 값을 리턴한다


def save_json(data, path):                                                        # 저장할 값과 파일 경로를 받는 함수
    """값을 JSON 파일로 저장한다.
    실행 결과 상태와 감사 기록을 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                               # 파일을 쓰기 모드로 연다
        json.dump(data, file, ensure_ascii=False, indent=2)                       # 한글은 그대로, 줄을 나눠 저장한다


def change_status(incident, new_status):                                          # 인시던트와 바꿀 상태를 받는 함수
    """허용된 이동이면 상태를 바꾸고 True, 아니면 바꾸지 않고 False 를 리턴한다.
    분류하지 않은 인시던트에 바로 조치하는 실수를 막을 때 쓴다.
    """
    current_status = incident["status"]                                           # 지금 상태
    allowed_statuses = TRANSITIONS[current_status]                                # 지금 상태에서 갈 수 있는 상태 리스트
    if new_status not in allowed_statuses:                                        # 갈 수 있는 상태 리스트에 없는 이동이면
        return False                                                              # 바꾸지 않고 False 를 리턴한다
    incident["status"] = new_status                                               # 허용된 이동이므로 상태를 바꾼다
    return True                                                                   # 상태를 바꿨으니 True 를 리턴한다


def is_grade_enough(incident_grade, min_grade):                                   # 인시던트 등급과 플레이북의 최소 등급을 받는 함수
    """인시던트 등급이 최소 등급 이상이면 True, 아니면 False 를 리턴한다.
    등급이 낮은 인시던트에 무거운 대응이 실행되지 않게 할 때 쓴다.
    """
    return GRADE_ORDER[incident_grade] >= GRADE_ORDER[min_grade]                  # 등급을 숫자로 바꿔 비교한 결과를 리턴한다


def match_playbooks(incident, registry):                                          # 인시던트와 플레이북 리스트를 받는 함수
    """트리거 규칙과 조건 등급이 모두 맞는 플레이북을 리스트로 리턴한다.
    알림이 올 때 어떤 대응 절차를 쓸지 찾을 때 쓴다.
    """
    matched = []                                                                  # 맞는 플레이북을 담을 빈 리스트
    for playbook in registry:                                                     # 플레이북을 하나씩 꺼낸다
        has_rule = playbook["trigger_rule"] in incident["reasons"]                # 트리거 규칙이 탐지된 규칙 리스트 안에 있는지 구한다
        grade_ok = is_grade_enough(incident["grade"], playbook["min_grade"])      # 인시던트 등급이 최소 등급 이상인지 구한다
        if has_rule and grade_ok:                                                 # 트리거와 조건이 모두 맞으면
            matched.append(playbook)                                              # 맞는 플레이북을 리스트에 추가한다
    return matched                                                                # 맞는 플레이북 리스트를 리턴한다


def run_action(action, incident, state):                                          # 액션 · 인시던트 · 시스템 상태를 받는 함수
    """액션 하나를 모의 시스템(state)에서 실행하고 결과 문장을 리턴한다.
    대상 종류와 맞지 않는 액션은 실행하지 않고 건너뛴 이유를 리턴한다.
    """
    entity = incident["entity"]                                                   # 대응할 대상(사용자 이름 또는 IP)
    is_ip = "." in entity                                                         # 점이 있으면 IP 로 본다
    if action == "계정 잠금":                                                     # 계정 잠금이면
        if is_ip:                                                                 # 대상이 IP 이면
            return "건너뜀: 대상이 IP 라서 계정 잠금을 할 수 없습니다"            # 실행하지 않고 이유를 리턴한다
        state["locked_users"].append(entity)                                      # 잠긴 계정 리스트에 추가한다
        return "계정 " + entity + " 잠금 완료"                                    # 결과 문장을 리턴한다
    if action == "IP 차단":                                                       # IP 차단이면
        if not is_ip:                                                             # 대상이 사용자 계정이면
            return "건너뜀: 대상이 사용자라서 IP 차단을 할 수 없습니다"           # 실행하지 않고 이유를 리턴한다
        state["blocked_ips"].append(entity)                                       # 차단한 IP 리스트에 추가한다
        return "IP " + entity + " 차단 완료"                                      # 결과 문장을 리턴한다
    if action == "티켓 생성":                                                     # 티켓 생성이면
        ticket_id = "TCK-" + str(len(state["tickets"]) + 1)                       # 지금까지 만든 티켓 수에 1 을 더해 번호를 만든다
        ticket = {"id": ticket_id, "incident": incident["id"], "target": entity}  # 티켓 한 건을 딕셔너리로 만든다
        state["tickets"].append(ticket)                                           # 티켓 리스트에 추가한다
        return "티켓 " + ticket_id + " 생성"                                      # 결과 문장을 리턴한다
    if action == "담당자 알림":                                                   # 담당자 알림이면
        message = "인시던트 " + incident["id"] + " 확인 요청"                     # 알림 문장을 만든다
        state["notifications"].append(message)                                    # 알림 리스트에 추가한다
        return "담당자 알림 전송"                                                 # 결과 문장을 리턴한다
    return "알 수 없는 액션: " + action                                           # 어느 액션도 아니면 이유를 리턴한다


def make_log_entry(incident, playbook, action, result):                           # 인시던트 · 플레이북 · 액션 · 결과를 받는 함수
    """감사 기록 한 건을 딕셔너리로 만든다.
    어떤 인시던트에 어떤 플레이북이 무엇을 했는지 나중에 증명할 때 쓴다.
    """
    now_text = datetime.now().strftime("%H:%M:%S")                                # 지금 시각을 시:분:초 글자로 만든다
    entry = {"time": now_text, "incident": incident["id"], "playbook": playbook["id"], "action": action, "result": result}  # 기록 한 건
    return entry                                                                  # 기록을 리턴한다
```

## 4. 플레이북 실행기 — `playbook_runner.py`

어제 6교시의 완성본입니다. `run_playbook` 이 승인을 확인하고, 액션을 차례로 실행하고, 감사 기록을 남깁니다.

```python
from incident import change_status, match_playbooks, run_action, make_log_entry     # 제공받은 함수를 불러온다


def run_playbook(incident, playbook, state, action_log):                            # 인시던트 · 플레이북 · 시스템 상태 · 감사 기록 리스트를 받는 함수
    """플레이북의 액션을 차례로 실행하고 감사 기록을 남긴다. 승인이 필요하면 실행하지 않고 승인 대기로 기록한다.
    실행했으면 True, 승인 대기로 멈췄으면 False 를 리턴한다.
    """
    change_status(incident, "분류됨")                                               # 대응을 시작하기 전에 분류됨 상태로 옮긴다 — 미리 채운 줄
    if playbook["approval"] != "자동":                                              # 승인 값이 자동이 아니면
        action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))  # 승인 대기로 기록하고
        return False                                                                # 실행하지 않고 끝낸다
    for action in playbook["actions"]:                                              # 액션을 하나씩 꺼낸다
        result = run_action(action, incident, state)                                # 액션을 실행하고 결과 문장을 받는다
        action_log.append(make_log_entry(incident, playbook, action, result))       # 결과를 감사 기록에 추가한다
    change_status(incident, "조치됨")                                               # 실행이 끝났으니 조치됨으로 옮긴다
    return True                                                                     # 모두 실행했으니 True 를 리턴한다


def process_incidents(incidents, registry, state, action_log):                      # 인시던트 리스트 · 플레이북 리스트 · 시스템 상태 · 감사 기록을 받는 함수
    """인시던트마다 맞는 플레이북을 찾아 실행하고 결과를 한 줄씩 출력한다.
    승인 대기로 멈춘 건의 리스트를 리턴한다.
    """
    pending = []                                                                    # 승인 대기로 멈춘 건을 담을 빈 리스트
    for incident in incidents:                                                      # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                             # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                          # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                                  # 맞는 플레이북을 하나씩 꺼낸다
            done = run_playbook(incident, playbook, state, action_log)              # 플레이북을 실행한다
            if done:                                                                # 실행했으면
                result_text = playbook["id"] + " 실행 완료"                         # 실행 완료라고 적는다
            else:                                                                   # 승인 대기로 멈췄으면
                result_text = playbook["id"] + " 승인 대기"                         # 승인 대기라고 적는다
                waiting = {"incident": incident["id"], "entity": incident["entity"], "playbook": playbook["id"], "approval": playbook["approval"]}  # 대기 건 한 건
                pending.append(waiting)                                             # 승인 대기 리스트에 추가한다
        status_text = "(상태: " + incident["status"] + ")"                          # 지금 상태를 괄호 글자로 만든다
        print(incident["id"], incident["entity"], incident["grade"], "->", result_text, status_text)  # 번호 · 대상 · 등급 · 결과 · 상태를 출력한다
    return pending                                                                  # 승인 대기 리스트를 리턴한다
```

## 5. 확인

**[터미널]** 파일이 있는지 확인한 뒤, 오늘 안내의 시작하기로 돌아가 이어서 합니다.

```bash
ls
```

- 명령 풀이: `ls` 폴더 안의 이름 보기
- `config` · `incident.py` · `incident_samples.json` · `playbook_runner.py` 가 보이면 됩니다. <mark>`config` 폴더 안의 `playbook_registry.json` 은 어제 만든 파일이고, 오늘 안내의 시작하기 6번에서 값을 확인합니다.</mark>
