# 11/12(목) 오전 · 5과목 자동 대응(SOAR) ⑥ — 인시던트 티케팅(ticketing) · 알림 병합(중복 제거)과 티켓 상태 전이 · 담당자 알림 전파와 재시도(retry)

<mark style="background:#e0d4ff">어제까지는 알림에 맞는 대응 조치를 실행하고</mark>, 롤백(rollback: 조치 이전 상태로 복원하는 일)하는 것까지 구현했습니다. 오늘은 그 결과를 <mark>**담당자에게 인계하고 통지하는 단계**</mark>를 구현합니다. 보안 관제 조직은 티켓과 알림 메시지로 사건 처리를 인수인계하기 때문입니다. 이 단계는 인시던트 관리(incident management)의 일부에 해당합니다. 오늘은 그중 사건 등록 · 중복 제거 · 상태 관리 · 담당자 통지를 구현합니다.

- **2교시**: 알림 한 건으로 담당자가 즉시 판단할 수 있는 **티켓을 생성**(ticketing, 티케팅: 알림을 추적 가능한 티켓으로 등록하는 일)합니다. 티켓에는 응답 기한(SLA)을 계산해 기재합니다. 사후 검증에 실패한 조치는 수동 확인 대상으로 별도 표시합니다(`ticketing.py`).
- **3교시**: 같은 사건의 알림을 티켓 한 장으로 **병합**(merge)합니다. 병합하면 중복 제거(deduplication: 같은 사건의 알림을 한 건으로 처리하는 일)가 됩니다. 예를 들어 `dami` 의 알림 네 건이 TCK-1 한 장에 병합됩니다. 이어서 허용된 순서로만 티켓 **상태를 전이**(status transition: 상태를 정해진 규칙에 따라 다른 값으로 바꾸는 일)합니다(`ticket_merge.py`).
- **4교시**: 등급에 맞는 수신자에게 알림을 **전파**(notification, 노티피케이션: 사건 발생을 담당자에게 통지하는 일)합니다. 이때 1과목에서 만든 알림 함수를 가져와 사용(import)합니다. 같은 티켓에 알림을 보내는 간격을 제한해 알림 피로(alert fatigue, 얼럿 퍼티그: 알림이 지나치게 많아 담당자가 반응하지 않게 되는 현상)를 줄입니다. 전송에 실패하면 **재시도**(retry, 리트라이: 실패한 전송을 다시 시도하는 일)합니다(`ticket_notice.py`).

깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 새 문법은 3교시의 `return None` 과 `is None` 두 가지입니다(`None` 값 자체는 화요일에 나왔습니다). 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기는 미리 채운 줄에 맞춥니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. <mark style="background:#ffc4d6">주석은 지우지 않습니다</mark>.

📎 **이전 파일**: 오늘 가져와 사용(import)하는 파일은 두 묶음입니다. 하나는 <mark style="background:#e0d4ff">월요일에 만든 `incident.py` 의 `load_json` · `save_json`</mark> 입니다. 다른 하나는 <mark style="background:#e0d4ff">1과목에서 만든 `notifier.py` · `alert_server.py`</mark> 입니다. 없는 파일은 아래 시작하기의 「🛟 이전 파일이 없을 때」 코드 상자로 만듭니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark style="background:#bde3ff">`ls` 결과에 `config` 와 `incident.py` 가 보이면</mark> 됩니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day04_am_ticket_notice.md`, `day04_am_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 데이터 파일과 설정 파일을 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   mkdir -p config
   touch alerts_thu.json config/escalation_rules.json
   ls config
   ```

**`alerts_thu.json`** — 오늘 오전 근무 3시간 동안 들어온 알림 11건입니다.

- **무엇인가**:
  - 알림 한 건은 `id`(알림 번호), `minute`(알림 수신 시각), `entity`(대상: 사용자 이름 또는 IP), `rule`(탐지 규칙), `grade`(심각도 등급, severity)로 구성됩니다.
  - 알림에는 처리 정보도 들어 있습니다. `status` 는 알림 처리 상태입니다. `playbook` 은 실행한 플레이북(playbook: 알림 유형별로 정해 둔 대응 절차)입니다. `done` 은 이미 수행한 조치 내역을 문장으로 적은 리스트입니다.
  - `minute` 은 근무를 시작한 때를 0분으로 센 분 단위 숫자입니다. `INC-201` 은 0분, `INC-211` 은 160분에 왔습니다.
- **어디에 쓰나**: 2 · 3 · 4교시 실행 파일이 이 파일을 읽어 알림을 하나씩 처리합니다.

```
[
  {"id": "INC-201", "minute": 0, "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "조치됨", "playbook": "PB-001", "done": ["계정 잠금: 잠기지 않음 → 잠김", "세션 종료: 세션 2개 → 세션 0개"]},
  {"id": "INC-202", "minute": 3, "entity": "198.51.100.90", "rule": "경로 스캔", "grade": "low", "status": "조치됨", "playbook": "PB-003", "done": ["IP 차단: 차단되지 않음 → 차단됨"]},
  {"id": "INC-203", "minute": 8, "entity": "gaeun", "rule": "규칙은 허용인데 서버가 거절", "grade": "mid", "status": "승인 대기", "playbook": "VIP 확인", "done": []},
  {"id": "INC-204", "minute": 12, "entity": "seoyeon", "rule": "대량 다운로드", "grade": "mid", "status": "승인 대기", "playbook": "PB-002", "done": []},
  {"id": "INC-205", "minute": 14, "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "조치됨", "playbook": "PB-001", "done": ["계정 잠금: 잠김 → 잠김 (이미 잠겨 있어 변경 없음)"]},
  {"id": "INC-206", "minute": 20, "entity": "198.51.100.90", "rule": "경로 스캔", "grade": "low", "status": "조치됨", "playbook": "PB-003", "done": ["IP 차단: 차단됨 → 차단됨 (이미 차단되어 변경 없음)"]},
  {"id": "INC-207", "minute": 30, "entity": "203.0.113.250", "rule": "경로 스캔", "grade": "low", "status": "조치됨", "playbook": "PB-003", "done": ["IP 차단: 차단되지 않음 → 차단되지 않음 (확인 실패)"]},
  {"id": "INC-208", "minute": 35, "entity": "hana", "rule": "업무 시간 밖 로그인", "grade": "mid", "status": "조치 없음", "playbook": "없음", "done": []},
  {"id": "INC-209", "minute": 40, "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "조치됨", "playbook": "PB-001", "done": ["계정 잠금: 잠김 → 잠김 (이미 잠겨 있어 변경 없음)"]},
  {"id": "INC-210", "minute": 95, "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "조치됨", "playbook": "PB-001", "done": ["계정 잠금: 잠김 → 잠김 (이미 잠겨 있어 변경 없음)"]},
  {"id": "INC-211", "minute": 160, "entity": "dami", "rule": "퇴사한 계정", "grade": "high", "status": "조치됨", "playbook": "PB-001", "done": ["계정 잠금: 잠김 → 잠김 (이미 잠겨 있어 변경 없음)"]}
]
```

**`config/escalation_rules.json`** — 티켓 생성 · 병합 · 알림 전파에 적용하는 정책 설정(policy configuration, 폴리시 컨피규레이션: 코드를 수정하지 않고 값만 바꿔 동작을 조정하는 설정 파일)입니다.

- **무엇인가**:
  - `sla_minutes` 는 등급별 응답 기한(SLA, 서비스 수준 협약)입니다. 알림을 수신한 뒤 담당자가 응답해야 하는 시간이며, 단위는 분입니다.
  - `recipients` 는 등급별 알림 수신자(recipient, 리서피언트: 알림을 받는 사람)입니다.
  - `merge_window_minutes` 는 병합 시간 범위(merge window, 머지 윈도우: 이 시간 안에 수신된 같은 사건의 알림만 병합하는 기준)이며 단위는 분입니다. 오늘 값은 60이므로, 티켓이 마지막으로 갱신된 뒤 60분 이내에 수신된 같은 사건의 알림만 그 티켓에 병합합니다.
  - `send_gap_minutes` 는 같은 티켓에 알림을 다시 전송하기까지 두는 최소 간격이며 단위는 분입니다. 오늘 값은 30이므로, <mark style="background:#ffdcb0">마지막으로 알린 뒤 30분이 지나야</mark> 같은 티켓에 다시 전송합니다.
  - `alert_url` 은 알림 서버 주소입니다. 알림 서버는 4교시 순서에서 두 번째 터미널로 켭니다.
  - `escalation_steps` 는 응답 기한이 지난 티켓을 상급자에게 올리는 에스컬레이션(escalation, 에스컬레이션: 미처리 사건을 상위 담당자에게 넘기는 일) 단계로, 오후에 사용합니다.
- **어디에 쓰나**: 코드를 바꾸지 않고 이 파일만 고쳐도 응답 시간과 수신자(알림을 받는 사람)가 바뀝니다.

```
{
  "sla_minutes": {"high": 15, "mid": 60, "low": 240},
  "recipients": {
    "high": ["kim.sec", "lee.soc", "team.lead"],
    "mid": ["kim.sec", "lee.soc"],
    "low": ["kim.sec"]
  },
  "merge_window_minutes": 60,
  "send_gap_minutes": 30,
  "alert_url": "http://127.0.0.1:5001/alert",
  "escalation_steps": [
    {"overdue_minutes": 0, "notify": "team.lead"},
    {"overdue_minutes": 30, "notify": "soc.head"}
  ]
}
```

5. **[터미널]** 1과목에서 만든 알림 파일 두 개를 이 폴더로 복사합니다.
   ```bash
   cp ../agent_core/notifier.py .
   cp ../agent_core/alert_server.py .
   ls
   ```
   - 명령 풀이: `cp 원본 복사본` 파일 복사하기(`.` 은 지금 폴더)
   - `No such file` 이 나오면 `ls ..` 로 `agent_core` 폴더 이름이 맞는지 봅니다. 그래도 없으면 아래 「🛟 이전 파일이 없을 때」의 `notifier.py` · `alert_server.py` 코드 상자를 같은 이름의 파일로 붙여 넣습니다.
6. **[터미널]** 파일이 정상인지 확인합니다. 먼저 데이터 파일입니다(맥북은 `python3`). <mark style="background:#bde3ff">`11 6` 이 나와야</mark> 합니다(알림이 11건, 규칙 파일의 키가 6개라는 뜻입니다).
   ```bash
   python -c "import json; print(len(json.load(open('alerts_thu.json', encoding='utf-8'))), len(json.load(open('config/escalation_rules.json', encoding='utf-8'))))"
   ```
7. **[터미널]** 알림 함수를 불러올 수 있는지 확인합니다(맥북은 `python3`). <mark style="background:#bde3ff">`notifier 불러오기 성공` 이 나와야</mark> 합니다.
   ```bash
   python -c "import notifier; print('notifier 불러오기 성공')"
   ```

### 🛟 이전 파일이 없을 때 (월요일 · 1과목 파일)

월요일에 결석했거나 파일을 지운 경우에만 만듭니다. **이미 있는 파일은 건너뜁니다.** 먼저 **[터미널]** 에서 빈 파일을 만듭니다. 이미 있는 파일은 `touch` 가 그대로 둡니다.

```bash
touch incident.py notifier.py alert_server.py
ls
```

- 명령 풀이: `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
- 아래 코드 상자 세 개를 **[VS Code]** 에서 같은 이름의 파일에 붙여 넣고 저장합니다. 이미 있는 파일은 붙여 넣지 않습니다.

**`incident.py`** — 월요일 파일에서 오늘 쓰는 두 함수(`load_json` · `save_json`)만 담았습니다. 월요일 파일 전체가 있으면 그것을 그대로 씁니다.

```python
import json                                                  # JSON 파일을 읽고 쓰기 위해 json 을 불러온다


def load_json(path):                                         # 파일 경로를 받는 함수
    """JSON 파일을 읽어 리스트나 딕셔너리로 리턴한다.
    인시던트와 플레이북 등록 파일을 읽을 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:               # 파일을 읽기 모드로 연다
        data = json.load(file)                               # JSON 글자를 파이썬 값으로 바꾼다
    return data                                              # 읽은 값을 리턴한다


def save_json(data, path):                                   # 저장할 값과 파일 경로를 받는 함수
    """값을 JSON 파일로 저장한다.
    실행 결과 상태와 감사 기록을 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:          # 파일을 쓰기 모드로 연다
        json.dump(data, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 줄을 나눠 저장한다
```

**`notifier.py`** — 1과목 알림 함수 `notify` 입니다. 메시지를 알림 서버로 보냅니다.

```python
import requests                                                # 인터넷으로 요청을 보내는 도구 (9/30)


def notify(message, url):                                      # 메시지를 알림 서버로 보내는 함수
    try:                                                       # 아래 줄을 해 본다
        requests.post(url, json={"text": message}, timeout=5)  # 메시지를 POST 한다 — 5초만 기다린다
        return True                                            # 보냈다
    except Exception as e:                                     # 에러가 나면 e 에 담아 여기로 온다
        print("[알림 실패]", type(e).__name__)                 # 에러 이름을 알린다 — 숨기지 않는다
        return False                                           # 못 보냈다 — 부른 쪽은 계속 간다
```

**`alert_server.py`** — 1과목 알림 서버입니다. 4교시와 오후에 알림을 받는 쪽입니다.

```python
from flask import Flask, request        # 10/2 에 쓴 웹 서버 도구

app = Flask(__name__)                   # 서버를 하나 만든다


@app.route("/alert", methods=["POST"])  # /alert 로 POST 가 오면 아래 함수가 받는다
def alert():                            # 알림을 받는 함수
    data = request.get_json()           # 보낸 JSON 을 딕셔너리로 꺼낸다
    print("[알림 받음]", data["text"])  # 터미널에 알림 내용을 보여 준다
    return {"ok": True}                 # 받았다고 답한다 (상태 코드 200)


app.run(port=5001)                      # 5001 번 포트에서 기다린다
```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'incident'` 는 <mark style="background:#ffc4d6">월요일에 만든 `incident.py` 가 이 폴더에 없다는 뜻</mark>입니다. `No module named 'notifier'` 는 5번 복사를 하지 않았다는 뜻입니다. 둘 다 위 「🛟 이전 파일이 없을 때」의 코드 상자로 만듭니다. `No module named 'requests'` 나 `No module named 'flask'` 가 나오면, 터미널(가상환경이 켜진 상태)에서 `pip install requests` 또는 `pip install flask` 를 입력합니다.
- 오류 전체와 입력한 명령을 AI 에게 붙여 넣어 물어봅니다. 이때 <mark style="background:#ffc4d6">`.env` 와 API 키는 지웁니다</mark>. 그래도 막히면 맨 아래 「정답」을 봅니다. 그래도 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 실행할 때마다 처음 상태에서 시작해 같은 결과가 나옵니다.

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 알림 한 건으로 티켓을 생성하고, 응답 기한(SLA)을 계산하며, 조치 확인에 실패한 건을 수동 확인 대상으로 표시하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">어제까지 만든 흐름은 조치를 실행한 뒤</mark> 「조치 완료」라는 기록 한 줄만 남겼습니다. 오늘 오전 3시간 동안 알림 11건이 수신됩니다. `INC-201` 은 퇴사한 `dami` 의 계정을 잠그는 조치를 했습니다. `INC-207` 은 IP `203.0.113.250` 의 차단을 시도했습니다. 조치 뒤에 실제 상태를 다시 조회해 확인하는 일을 사후 검증이라고 합니다. <mark style="background:#ffc4d6">사후 검증에서 실제로는 차단되지 않은 것으로 확인됐습니다</mark>.
> - **문제**: 기록 한 줄만으로는 담당자가 네 가지를 알 수 없습니다. 어떤 사건인지, 이미 어떤 조치를 했는지, 이어서 무엇을 해야 하는지, 언제까지 응답해야 하는지입니다. 또한 사후 검증에 실패한 `INC-207` 이 정상 조치된 알림과 구별되지 않습니다. 그래서 후속 확인이 누락되고, 차단되지 않은 IP 가 그대로 남습니다.
> - **부탁**: 알림이 수신되면 <mark>제목 · 조치 내역 · 후속 조치 · 응답 기한(SLA)을 기재한 티켓을 자동으로 생성해 주세요</mark>. 티켓은 사건 한 건의 처리 상태를 적어 두는 기록입니다. 응답 기한(SLA)은 알림을 수신한 뒤 담당자가 몇 분 안에 응답해야 하는지 정한 기한입니다. 사후 검증에 실패한 건은 담당자가 직접 확인하도록 표시해 주세요.
> - **바뀌는 점**: 담당자는 티켓만 읽고 바로 대응을 시작할 수 있습니다. 예를 들어 `INC-201` 은 high 등급이라 티켓에 응답 기한 15분이 적힙니다. 오늘 샘플에서는 `INC-207` 한 건이 「직접 확인」 대상으로 별도 표시됩니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 2.1 티켓은 담당자의 네 가지 질문 「사건 개요 · 이미 수행한 조치 · 후속 조치 · 응답 기한」에 답해야 한다

**티켓**(ticket)은 사건 한 건의 처리 상태 · 담당자 · 조치 이력을 추적하는 기록입니다. 월요일에는 `id` · `incident` · `target` 세 가지만 담긴 간단한 티켓을 만들었습니다. 알림으로 티켓을 생성해 등록하는 일을 **티케팅**(ticketing)이라고 합니다. 오늘은 티켓에 어떤 정보를 기재할지 정합니다. 담당자는 티켓을 열면 아래 네 가지를 확인하려 합니다.

| 담당자의 질문 | 티켓의 키 | 값을 정하는 방법 |
|---|---|---|
| 무슨 일인가 | `title` | 등급 · 대상 · 탐지 규칙을 이어 붙여 제목을 만든다 (1번). 예: `[high] dami — 퇴사한 계정` |
| 이미 무엇을 했나 | `done` | 알림에 기재된 조치 내역을 그대로 복사한다 |
| 다음에 무엇을 하나 | `next_step` | 알림 상태별로 정해 둔 후속 조치 문장을 선택한다 (2번). 사후 검증에 실패했으면 직접 확인을 지시하는 문장으로 교체한다 (3 · 4번) |
| 언제까지 응답하나 | `sla_due` | <mark style="background:#ffdcb0">알림 수신 시각 + 등급별 응답 기한</mark> (5 · 6번). 예: 0분 + 15분 = 15분 |

- **응답 기한**(SLA, Service Level Agreement, 에스엘에이: 서비스 수준 협약)은 알림을 수신한 뒤 담당자가 응답해야 하는 시간의 약속입니다. `escalation_rules.json` 의 `sla_minutes` 에 등급별로 정의되어 있으며, <mark style="background:#ffdcb0">high 는 15분, mid 는 60분, low 는 240분</mark>입니다. 응답 기한은 시간의 길이이고, 티켓의 `sla_due` 에 적는 **응답 기한 시각**은 알림 수신 시각에 응답 기한을 더한 값입니다. 예를 들어 `INC-201` 은 0분에 수신된 high 알림이라 15분 안에 응답해야 하므로, TCK-1 의 응답 기한 시각은 0 + 15 = 15분입니다. `INC-202` 는 3분에 수신된 low 알림이라, TCK-2 의 응답 기한 시각은 3 + 240 = 243분입니다.
- 알림 상태(`status`)는 `조치됨`(자동 조치 완료) · `승인 대기`(담당자의 승인을 기다리는 중) · `조치 없음`(자동 조치 대상 아님) 세 가지입니다. 상태별로 담당자가 수행할 후속 조치가 다르므로, 후속 조치 문장(`next_step`)도 상태별로 따로 정의합니다.
- `done` 문장 끝에 「(확인 실패)」가 붙은 조치가 있습니다. 조치는 실행했지만, 사후 검증에서 실제 상태가 바뀌지 않은 것으로 확인된 조치입니다. 예를 들어 `INC-207` 의 `IP 차단: 차단되지 않음 → 차단되지 않음 (확인 실패)` 가 그렇습니다. <mark style="background:#e0d4ff">수요일에 구현한 조치 후 확인(사후 검증)</mark>이 이 결과를 기록합니다. 이런 조치는 담당자가 수동 검증(manual verification: 사람이 실제 상태를 직접 조회해 확인하는 일)으로 직접 확인해야 하므로, 티켓에 별도로 표시합니다.
- 정의되지 않은 상태가 입력될 수 있습니다. 그래도 프로그램이 중단되지 않도록, 딕셔너리에서 키가 없을 때 기본값을 리턴하는 `.get(키, 기본값)` 을 사용합니다(수요일에 배웠습니다).

함수 네 개와 실행 파일에서 직접 쓰는 곳은 **아홉 군데**입니다.

```
ticketing.py   make_title         : 등급 · 대상 · 규칙으로 티켓 제목을 만든다 (1번)
               find_next_step     : 알림 상태에 맞는 다음 할 일 문장을 고른다 (2번)
               has_failed_action  : 조치 내역에 「확인 실패」가 있는지 확인한다 (3 · 4번)
               make_ticket        : 응답 기한을 계산해 티켓 한 장을 만든다 (5 · 6번)
실행 파일      day04_2-1_run.py   : 알림마다 티켓을 만들고 (7번), 리스트에 모으고 (8번), 직접 확인이 필요한 티켓 수를 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 2-1 · 알림 11건으로 티켓을 생성하고, 응답 기한(SLA)을 계산하며, 조치 확인에 실패한 건을 수동 확인 대상으로 표시하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 11건에는 조치 기록만 있고, 담당자의 후속 조치와 응답 기한이 기재되어 있지 않습니다</mark>.
- **만드는 것**: 제목 · 후속 조치 · 수동 확인 표시 · 응답 기한(SLA)을 기재한 티켓을 생성하는 코드(`ticketing.py`)와, 알림마다 티켓을 생성해 리스트에 저장하는 코드(`day04_2-1_run.py`)입니다.
- **실행하면**: <mark>단계 1: 불러온 알림 수, 단계 2: 알림마다 만든 티켓, 단계 3: 티켓 본문 예, 단계 4: 직접 확인이 필요한 티켓이 나옵니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 ~ 4 를 읽습니다.

**`ticketing.py`** — 알림으로 티켓을 생성합니다. 3 · 4교시도 가져와 사용(import)합니다. 직접 쓰는 곳은 1 ~ 6번입니다.

```python
DEFAULT_NEXT_STEP = "담당자가 알림 내용을 읽고 필요한 일을 정한다"                      # 알림 상태를 모를 때 쓰는 다음 할 일
MANUAL_STEP = "조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다"  # 조치 확인에 실패한 티켓의 다음 할 일
NEXT_STEPS = {                                                                          # 알림 상태마다 담당자가 할 다음 일
    "조치됨": "조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다",                # 자동 조치가 끝난 알림
    "승인 대기": "승인할지 거절할지 정하고 정한 사람의 이름을 남긴다",                  # 승인을 기다리는 알림
    "조치 없음": "자동 조치가 없는 알림이니 직접 보고 조치가 필요한지 정한다",          # 자동 조치 대상이 아닌 알림
}


def make_title(alert):                                                                  # 알림 한 건을 받는 함수
    """티켓 제목(등급 · 대상 · 규칙)을 문자열로 만들어 리턴한다.
    티켓 목록에서 제목만 봐도 무슨 일인지 알 수 있게 할 때 쓴다.
    """
    grade = alert["grade"]                                                              # 알림 등급 — 미리 채운 줄
    entity = alert["entity"]                                                            # 알림 대상(사용자 이름 또는 IP) — 미리 채운 줄
    rule = alert["rule"]                                                                # 탐지된 규칙 이름 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. "[" + grade + "] " + entity + " — " + rule 을 이어 붙인 문자열를 리턴한다


def find_next_step(alert, next_steps):                                                  # 알림 한 건과 다음 할 일 딕셔너리를 받는 함수
    """알림 상태에 맞는 다음 할 일 문장을 리턴한다. 정해 둔 문장이 없으면 기본 문장을 리턴한다.
    담당자가 티켓을 열자마자 무엇부터 할지 알게 할 때 쓴다.
    """
    status = alert["status"]                                                            # 알림 상태(조치됨 · 승인 대기 · 조치 없음) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. next_steps.get(status, DEFAULT_NEXT_STEP) 의 결과를 리턴한다 (키가 없으면 기본 문장)


def has_failed_action(done_list):                                                       # 조치 내역 문장 리스트를 받는 함수
    """조치 내역에 「확인 실패」가 들어 있는 문장이 하나라도 있으면 True, 없으면 False 를 리턴한다.
    조치했다고 했지만 실제로 바뀌지 않은 알림을 사람이 직접 보게 할 때 쓴다.
    """
    for text in done_list:                                                              # 조치 내역 문장을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. text 안에 "확인 실패" 가 들어 있으면 (if, in)
            # 4. True 를 리턴한다
    return False                                                                        # 하나도 없으면 False 를 리턴한다 — 미리 채운 줄


def make_ticket(alert, ticket_no, rules, next_steps):                                   # 알림 · 티켓 번호 · 규칙 · 다음 할 일 딕셔너리를 받는 함수
    """알림 한 건으로 티켓 한 장(딕셔너리)을 만들어 리턴한다. 만든 시각과 응답 기한(SLA)을 함께 적는다.
    알림이 오면 바로 담당자가 읽을 수 있는 티켓을 만들 때 쓴다.
    """
    sla_table = rules["sla_minutes"]                                                    # 등급마다 정한 응답 기한(분) 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. sla_table[alert["grade"]] 를 sla_minutes 에 저장한다 (이 알림 등급의 응답 기한)
    # 6. alert["minute"] + sla_minutes 를 sla_due 에 저장한다 (응답해야 하는 시각)
    needs_manual = has_failed_action(alert["done"])                                     # 조치 확인에 실패한 내역이 있는지 — 미리 채운 줄
    next_step = find_next_step(alert, next_steps)                                       # 다음 할 일 문장 — 미리 채운 줄
    if needs_manual:                                                                    # 확인 실패가 있으면 — 미리 채운 줄
        next_step = MANUAL_STEP                                                         # 직접 확인하라는 문장으로 바꾼다 — 미리 채운 줄
    ticket = {                                                                          # 티켓 한 장 — 미리 채운 줄
        "id": "TCK-" + str(ticket_no),                                                  # 티켓 번호
        "title": make_title(alert),                                                     # 제목
        "entity": alert["entity"],                                                      # 대상
        "rule": alert["rule"],                                                          # 규칙
        "grade": alert["grade"],                                                        # 등급
        "playbook": alert["playbook"],                                                  # 실행한 플레이북
        "done": alert["done"],                                                          # 조치 내역
        "status": "열림",                                                               # 티켓 상태 : 처음에는 열림
        "next_step": next_step,                                                         # 다음 할 일
        "needs_manual": needs_manual,                                                   # 직접 확인이 필요한지
        "created_at": alert["minute"],                                                  # 만든 시각(분)
        "updated_at": alert["minute"],                                                  # 마지막으로 갱신한 시각(분)
        "sla_due": sla_due,                                                             # 응답 기한 시각(분)
        "count": 1,                                                                     # 합쳐진 알림 수 : 처음에는 1
        "incidents": [alert["id"]],                                                     # 합쳐진 알림 번호
        "notified_count": 0,                                                            # 알림을 보낸 횟수
        "last_notified": -1,                                                            # 마지막으로 알림을 보낸 시각(분) : 아직 없음
        "acked_at": -1,                                                                 # 담당자가 처음 확인한 시각(분) : 아직 없음
        "resolved_at": -1,                                                              # 해결한 시각(분) : 아직 없음
        "escalation_level": 0,                                                          # 상급자에게 올린 단계 : 아직 없음
        "comments": [],                                                                 # 상태를 바꾼 기록
    }
    return ticket                                                                       # 만든 티켓을 리턴한다
```

**`day04_2-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 월요일의 `incident.py` 가 같은 폴더에 있어야 합니다.

```python
from incident import load_json                                                                # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticketing import make_ticket, NEXT_STEPS                                                 # 방금 만든 티켓 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                         # 오늘 오전 알림 파일을 리스트로 읽는다
rules = load_json("config/escalation_rules.json")                                             # 응답 기한 규칙 파일을 딕셔너리로 읽는다
sla_count = len(rules["sla_minutes"])                                                         # 응답 기한을 정한 등급이 몇 개인지 센다
print("--- 단계 1: 불러온 알림", len(alerts), "건 · 응답 기한을 정한 등급", sla_count, "개")  # 단계 1 시작을 알리는 줄

tickets = []                                                                                  # 만든 티켓을 저장할 빈 리스트
manual_count = 0                                                                              # 직접 확인이 필요한 티켓 수 : 처음에는 0
print("--- 단계 2: 알림마다 만든 티켓")                                                       # 단계 2 시작을 알리는 줄
for alert in alerts:                                                                          # 알림을 하나씩 읽는다
    ticket_no = len(tickets) + 1                                                              # 티켓 번호는 지금까지 만든 수 + 1
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. make_ticket(alert, ticket_no, rules, NEXT_STEPS) 의 결과를 ticket 에 저장한다
    # 8. tickets 리스트에 ticket 을 추가한다 (append)
    print(ticket["id"], ticket["title"], "· 만든 시각", ticket["created_at"], "분 · 기한", ticket["sla_due"], "분")  # 티켓 한 줄을 출력한다
    if ticket["needs_manual"]:                                                                # 직접 확인이 필요하면
        # 9. manual_count 에 manual_count + 1 을 저장한다 (1 늘린다)

print("--- 단계 3: 티켓 본문 예 (TCK-1)")                                                     # 단계 3 시작을 알리는 줄
first = tickets[0]                                                                            # 첫 번째 티켓을 꺼낸다
print("제목:", first["title"])                                                                # 제목을 출력한다
print("조치 내역:")                                                                           # 조치 내역 제목을 출력한다
for text in first["done"]:                                                                    # 조치 내역 문장을 하나씩 읽는다
    print(" -", text)                                                                         # 문장 앞에 - 를 붙여 출력한다
print("다음 할 일:", first["next_step"])                                                      # 다음 할 일을 출력한다
print("응답 기한:", first["sla_due"], "분 (만든 시각", first["created_at"], "분)")            # 응답 기한을 출력한다

print("--- 단계 4: 직접 확인이 필요한 티켓", manual_count, "건")                              # 단계 4 시작을 알리는 줄과 건수
for ticket in tickets:                                                                        # 티켓을 하나씩 읽는다
    if ticket["needs_manual"]:                                                                # 직접 확인이 필요하면
        print(ticket["id"], ticket["title"], "→", ticket["next_step"])                        # 티켓과 다음 할 일을 출력한다
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch ticketing.py day04_2-1_run.py
   ls
   ```
2. **[VS Code]** `ticketing.py` 1 ~ 6번, `day04_2-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day04_2-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다. 단계 2 는 11줄, 단계 3 은 6줄, 단계 4 는 숫자가 제목 줄에 함께 나오고 그 아래 1줄입니다.
5. **[보고서]** `day04_am_report.md` 의 `## 2교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣어 주세요. 그리고 단계 4 에 나온 직접 확인이 필요한 티켓 번호를 적어 주세요. 마지막으로 응답 기한 시각(담당자가 응답해야 하는 시각)이 가장 이른 티켓 번호를 적어 주세요.
   - (나) 🔍 `INC-207` 은 상태가 `조치됨` 인데, 티켓의 후속 조치(`next_step`)는 「조치됨」용 문장이 아닙니다. `done` 의 문장을 근거로 그 사유를 적어 주세요. 그다음 이 표시가 없으면 담당자가 무엇을 놓칠 수 있는지 적어 주세요.
   - (다) 🔍 TCK-1 의 응답 기한 시각은 15분이고 TCK-2 는 243분입니다. 두 티켓의 등급과 만든 시각을 근거로 응답 기한 시각을 계산하는 방법을 적어 주세요. 그다음 모든 티켓에 같은 응답 기한을 적용하면 어떤 문제가 생기는지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 문자열 이어 붙이기 | `"[" + grade + "] " + entity` |
| 키가 없으면 기본값을 주며 읽기 | `next_steps.get(status, DEFAULT_NEXT_STEP)` |
| 문자열 안에 있으면 | `if "확인 실패" in text:` |
| 딕셔너리에서 값을 읽어 변수에 저장 | `sla_minutes = sla_table[alert["grade"]]` |
| 더해서 변수에 저장 | `sla_due = alert["minute"] + sla_minutes` |
| 함수 결과를 변수에 저장 | `ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)` |
| 1 늘려 다시 저장 | `manual_count = manual_count + 1` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 같은 사건의 알림을 티켓 한 장으로 병합(중복 제거)하고, 티켓 상태를 허용된 순서로 전이하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 2교시 방식대로 하면 알림 수만큼 티켓이 생성되므로, 알림 11건이 티켓 11장이 됩니다. 그런데 같은 사건이 반복해서 발생해 중복된 알림이 많습니다.
>   - 퇴사한 `dami` 의 계정 알림이 다섯 번(`INC-201` · `INC-205` · `INC-209` · `INC-210` · `INC-211`) 수신됐습니다. 그중 네 건(`INC-201` → `INC-205` → `INC-209` → `INC-210`)은 티켓의 <mark style="background:#ffdcb0">마지막 갱신 뒤 60분 이내</mark>에 이어서 수신됐습니다. 마지막 갱신은 새 알림이 합쳐지거나 상태가 바뀌어 티켓 내용이 마지막으로 바뀐 때입니다. 예를 들어 `INC-205` 는 14분에, `INC-209` 는 40분에 수신되어 직전 알림과 각각 14분 · 26분 간격입니다.
>   - `INC-211` 은 160분에 수신되어 마지막 갱신(95분)보다 65분 늦습니다. 60분을 넘으므로 이어진 알림이 아닙니다.
>   - 경로 스캔(서버의 여러 주소에 차례로 요청을 보내 약점을 찾는 일) IP `198.51.100.90` 의 알림이 두 번(`INC-202` · `INC-206`) 수신됐습니다.
> - **문제**: 같은 사건의 티켓이 여러 장이면 세 가지 문제가 생깁니다. 첫째, 어느 티켓이 최신인지 알 수 없습니다. 둘째, 한 장을 처리해도 나머지는 열린 상태로 남습니다. 셋째, 티켓이 늘어나서 새로 발생한 사건을 찾기 어렵습니다.
> - **부탁**: 다음 두 가지를 만들어 주세요.
>   - 첫째, 병합(merge)입니다. 병합은 새 티켓을 만들지 않고 기존 티켓에 알림을 합치는 일입니다. 같은 대상에 같은 규칙으로 수신된 알림이 티켓의 마지막 갱신 후 60분 이내에 수신되면 기존 티켓에 병합해 주세요.
>   - 둘째, 상태 전이(status transition)입니다. 상태 전이는 티켓 상태를 정해진 규칙에 따라 바꾸는 일입니다. 티켓 상태는 <mark style="background:#ffdcb0">허용된 순서(열림 → 확인 중 → 해결, 또는 열림 → 해결)로만 전이하고</mark>, 누가 언제 전이했는지 기록해 주세요.
> - **바뀌는 점**: <mark style="background:#bde3ff">알림 11건이 티켓 7장으로 정리됩니다</mark>. `dami` 의 같은 알림 네 건(`INC-201` · `INC-205` · `INC-209` · `INC-210`)은 TCK-1 한 장에 「합쳐진 알림 4건」으로 집계됩니다. `INC-211` 은 새 티켓이 되고, `198.51.100.90` 의 두 건은 TCK-2 한 장에 합쳐집니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 3.1 병합 기준은 「같은 대상 · 같은 규칙 · 미해결 · 60분 이내」이다

같은 사건의 알림이 새 티켓을 만들지 않고 기존 티켓에 합쳐지는 것을 **병합**(merge)이라고 합니다. 병합은 중복 제거의 한 방식이고, 실행 결과에도 `병합` 으로 나옵니다. 예를 들어 `INC-205` 는 14분에 수신되어 새 티켓 대신 TCK-1 에 병합되고, TCK-1 의 합쳐진 알림이 2건이 됩니다. 병합할지는 아래 <mark style="background:#ffdcb0">네 가지 조건을 모두 확인해 판정합니다</mark>.

| 확인 | 충족하는 경우 |
|---|---|
| 같은 대상 | 티켓의 `entity` 가 알림의 `entity` 와 같다 |
| 같은 규칙 | 티켓의 `rule` 이 알림의 `rule` 과 같다 |
| 끝나지 않음 | 티켓 상태가 `해결` 이 아니다 (<mark style="background:#ffdcb0">해결된 티켓에는 병합하지 않고 새 티켓을 생성한다</mark>) |
| 60분 안 | 알림 수신 시각에서 티켓의 마지막 갱신 시각을 뺀 값(경과 시간, 분)이 <mark style="background:#ffdcb0">`merge_window_minutes`(60) 이하다</mark> |

- <mark>경과 시간은 티켓 생성 시각이 아니라 마지막 갱신 시각을 기준으로 계산합니다.</mark> `INC-209`(40분)가 병합되면 티켓의 마지막 갱신 시각이 40분이 됩니다. `INC-210`(95분)은 마지막 갱신 시각 40분보다 55분 뒤에 수신되므로 병합됩니다. 병합되면 갱신 시각이 95분으로 바뀝니다. `INC-211`(160분)은 마지막 갱신 시각 95분보다 <mark style="background:#bde3ff">65분 뒤에 수신되어 60분을 넘으므로, 새 티켓이 생성됩니다</mark>.
- 상태 전이도 갱신으로 간주합니다. 따라서 상태를 전이하면 갱신 시각이 바뀝니다.
- 같은 대상 · 규칙인데 등급이 다른 알림이 수신되어도, 오늘은 기존 티켓의 등급과 응답 기한을 변경하지 않습니다. 더 높은 등급의 알림이 병합될 때 티켓의 등급을 상향 조정할지는 팀마다 정책으로 정하기도 합니다.
- 시간 범위 기준이 없으면 <mark style="background:#ffc4d6">하루 전에 수신된 알림과 오늘 수신된 알림이 티켓 한 장으로 병합됩니다</mark>. 그러면 오늘 새로 발생한 사건을 식별하기 어렵습니다.
- 해결된 티켓에 새 알림이 병합되면, 상태가 「해결」 그대로여서 아무도 그 티켓을 다시 확인하지 않습니다. 그래서 <mark style="background:#ffc4d6">새로 수신된 알림이 누락됩니다</mark>.
- 티켓 상태 전이(status transition, 스테이터스 트랜지션: 티켓 상태가 한 값에서 다른 값으로 바뀌는 일)는 <mark style="background:#e0d4ff">월요일에 알림 상태를 바꾸던 방식과 같습니다</mark>. 티켓이 생성부터 종료까지 거치는 상태의 흐름을 티켓 수명주기(lifecycle, 라이프사이클)라고 합니다. 오늘은 아래 표에 정의한 전이만 허용합니다.
- 티켓 상태는 세 가지이며, 티켓 도구에서 흔히 쓰는 이름과 뜻이 같습니다. 열림(open, 오픈)은 새로 생성되어 아직 아무도 확인하지 않은 상태입니다. 확인 중(acknowledged, 애크날리지드)은 담당자가 확인하고 처리하기 시작한 상태입니다. 해결(resolved, 리졸브드)은 조치가 끝나 사건이 해소된 상태입니다. 예를 들어 TCK-1 은 생성될 때 열림이고, 단계 3 에서 `kim.sec` 이 50분에 확인 중으로 바꿉니다.
- 상태를 전이할 때 최초 확인 시각(`acked_at`)과 해결 시각(`resolved_at`)도 기록합니다. 오후에 평균 확인 시간과 평균 해결 시간을 계산할 때 사용합니다.

| 지금 상태 | 갈 수 있는 상태 |
|---|---|
| 열림 | 확인 중 · 해결 |
| 확인 중 | 해결 |
| 해결 | 없음 (재개하지 않고 새 티켓을 생성한다) |

**🐍 문법 상자 — `None` 은 「없다」는 값이고, `is None` 으로 확인한다**

```python
def find_name(names, target):
    for name in names:
        if name == target:
            return name
    return None

found = find_name(["dami", "hana"], "gaeun")
print(found)
print(found is None)
```

| 코드 | 뜻 |
|---|---|
| `return None` | 「찾는 것이 없다」는 값을 리턴한다 |
| `found is None` | `found` 가 `None` 이면 `True`, 아니면 `False` 다. `None` 인지 확인할 때는 `==` 대신 `is` 를 쓴다 |
| 위 코드의 출력 | `None` 다음 줄에 `True` |

함수 세 개에서 직접 쓰는 곳은 **아홉 군데**이고 모두 `ticket_merge.py` 안에 있습니다.

```
ticket_merge.py   find_open_ticket     : 합칠 수 있는 티켓을 찾는다 (1 ~ 3번). 없으면 None 을 리턴한다
                  merge_alert          : 찾은 티켓에 알림을 합친다 (4 ~ 6번). 새 알림의 조치 내역과 확인 실패 표시도 옮긴다 (미리 채움)
                  handle_alert         : 합칠 티켓을 찾아 (7번), 없으면 (8번) 새 티켓을 만들고, 있으면 합친다 (9번)
                  change_ticket_status : 허용된 이동일 때만 상태를 바꾸고, 확인 · 해결 시각과 댓글을 남긴다 (미리 채움)
실행 파일         day04_3-1_run.py     : 알림 11건을 처리하고 (미리 채움), TCK-1 의 상태를 바꿔 본다
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 3-1 · 같은 사건의 알림을 티켓 한 장으로 병합(중복 제거)하고, 티켓 상태를 허용된 순서로 전이하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 수만큼 티켓이 생성되므로 같은 사건의 티켓이 여러 장입니다. 또한 티켓 상태를 전이하는 방법도 없습니다</mark>.
- **만드는 것**: 병합할 티켓 찾기 · 병합 · 알림 한 건 처리(`ticket_merge.py`). 상태 전이와 실행 파일은 미리 채워져 있습니다.
- **실행하면**: <mark>단계 1: 알림 11건의 처리 결과, 단계 2: 알림 수와 티켓 수 · 티켓 목록, 단계 3: TCK-1 의 상태 바꾸기와 댓글이 나옵니다.</mark>

**🎯 할 일**: 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행 파일은 그대로 붙여 넣습니다. 실행해서 단계 1 ~ 3 을 읽습니다.

**`ticket_merge.py`** — 같은 사건의 알림을 티켓 한 장으로 병합합니다. 4교시도 가져와 사용(import)합니다. 2교시의 `ticketing.py` 가 같은 폴더에 있어야 합니다. 직접 쓰는 곳은 1 ~ 9번입니다.

- 1번 아래에는 `if` 한 줄을 씁니다.
- 2번 아래에는 `if` 한 줄을 씁니다. 1번 아래에 쓰는 `if` 안쪽에는 미리 채운 `if` 가 이미 한 단계 들어가 있습니다. 그래서 2번은 1번보다 두 단계 오른쪽에서 시작합니다.
- 3번 아래에는 2번보다 한 단계 오른쪽에 `return` 한 줄을 씁니다.
- 8번도 `if` 한 줄만 씁니다. 그 아래 미리 채운 줄들이 `if` 안쪽입니다.

```python
from ticketing import make_ticket, has_failed_action, NEXT_STEPS, MANUAL_STEP        # 2교시에 만든 함수와 문장을 불러온다

ALLOWED_MOVES = {                                                                    # 티켓 상태마다 옮겨 갈 수 있는 상태의 리스트
    "열림": ["확인 중", "해결"],                                                     # 열림에서는 확인 중이나 해결로 갈 수 있다
    "확인 중": ["해결"],                                                             # 확인 중에서는 해결로만 갈 수 있다
    "해결": [],                                                                      # 해결에서는 어디로도 갈 수 없다
}


def find_open_ticket(tickets, alert, window):                                        # 티켓 리스트 · 알림 · 병합 시간(분)을 받는 함수
    """같은 대상 · 같은 규칙이고, 해결되지 않았고, window 분 안에 갱신된 티켓을 찾아 리턴한다. 없으면 None 을 리턴한다.
    같은 사건의 알림이 티켓 여러 장이 되는 것을 막을 때 쓴다.
    """
    for ticket in tickets:                                                           # 티켓을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. ticket 의 "entity" 가 alert 의 "entity" 와 같고(and) ticket 의 "rule" 도 alert 의 "rule" 과 같으면 (if, ==)
            if ticket["status"] != "해결":                                           # 해결되지 않은 티켓이면 — 미리 채운 줄
                gap = alert["minute"] - ticket["updated_at"]                         # 마지막 갱신 뒤 몇 분 지났는지 — 미리 채운 줄
                # 2. gap 이 window 이하이면 (if, <=)
                    # 3. ticket 을 리턴한다
    return None                                                                      # 맞는 티켓이 없으면 None 을 리턴한다 — 미리 채운 줄


def merge_alert(ticket, alert):                                                      # 티켓과 새 알림을 받는 함수
    """이미 있는 티켓에 새 알림을 합친다. 합친 알림 수를 1 늘리고, 알림 번호를 더하고, 갱신 시각을 알림이 온 시각으로 바꾼다.
    같은 사건이 되풀이될 때 새 티켓 대신 기존 티켓에 기록을 더할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. ticket 의 "count" 에 ticket["count"] + 1 을 저장한다 (1 늘린다)
    # 5. ticket 의 "incidents" 리스트에 alert 의 "id" 를 추가한다 (append)
    # 6. ticket 의 "updated_at" 에 alert 의 "minute" 을 저장한다
    ticket["done"] = ticket["done"] + alert["done"]                                  # 새 알림의 조치 내역을 티켓의 조치 내역 뒤에 이어 붙인다 — 미리 채운 줄
    if has_failed_action(alert["done"]):                                             # 새 알림의 조치 확인이 실패했으면 — 미리 채운 줄
        ticket["needs_manual"] = True                                                # 직접 확인이 필요하다고 표시하고 — 미리 채운 줄
        ticket["next_step"] = MANUAL_STEP                                            # 다음 할 일도 직접 확인하라는 문장으로 바꾼다 — 미리 채운 줄


def handle_alert(alert, tickets, rules):                                             # 알림 · 티켓 리스트 · 규칙을 받는 함수
    """알림 한 건을 처리한다. 합칠 티켓이 있으면 합치고, 없으면 새 티켓을 만든다. 처리한 티켓과 「새 티켓」 또는 「병합」을 함께 리턴한다.
    알림이 올 때마다 부른다.
    """
    window = rules["merge_window_minutes"]                                           # 같은 사건으로 보는 시간(분) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. find_open_ticket(tickets, alert, window) 의 결과를 existing 에 저장한다
    # 8. existing 이 None 이면 (if, is)
        ticket_no = len(tickets) + 1                                                 # 새 티켓 번호 — 미리 채운 줄
        ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)                    # 새 티켓을 만들고 — 미리 채운 줄
        tickets.append(ticket)                                                       # 티켓 리스트에 추가한다 — 미리 채운 줄
        return ticket, "새 티켓"                                                     # 티켓과 「새 티켓」을 함께 리턴하고 끝낸다 — 미리 채운 줄
    # 9. merge_alert(existing, alert) 를 호출한다 (합칠 티켓이 있을 때만 여기까지 온다)
    return existing, "병합"                                                          # 티켓과 「병합」을 함께 리턴한다 — 미리 채운 줄


def change_ticket_status(ticket, new_status, minute, who):                           # 티켓 · 바꿀 상태 · 시각(분) · 바꾼 사람을 받는 함수
    """허용된 이동이면 티켓 상태를 바꾸고 True, 아니면 바꾸지 않고 False 를 리턴한다. 바꾼 사람과 시각을 댓글로 남긴다.
    담당자가 티켓을 확인하기 시작했는지 끝냈는지 추적할 때 쓴다.
    """
    old_status = ticket["status"]                                                    # 지금 상태
    if new_status not in ALLOWED_MOVES[old_status]:                                  # 갈 수 없는 이동이면
        return False                                                                 # 바꾸지 않고 False 를 리턴한다
    ticket["status"] = new_status                                                    # 상태를 바꾼다
    if ticket["acked_at"] == -1:                                                     # 처음 확인하는 것이면
        ticket["acked_at"] = minute                                                  # 확인한 시각을 적는다
    if new_status == "해결":                                                         # 해결로 바꾸는 것이면
        ticket["resolved_at"] = minute                                               # 해결한 시각을 적는다
    ticket["updated_at"] = minute                                                    # 갱신 시각을 적는다
    comment = who + " · " + str(minute) + "분 · " + old_status + " → " + new_status  # 누가 언제 무엇을 했는지 문자열로 만든다
    ticket["comments"].append(comment)                                               # 댓글 리스트에 추가한다
    return True                                                                      # 바꿨다고 True 를 리턴한다
```

**`day04_3-1_run.py`** — 쓰는 줄이 없습니다. 그대로 붙여 넣습니다.

```python
from incident import load_json                                                              # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticket_merge import handle_alert, change_ticket_status                                 # 방금 만든 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                       # 오늘 오전 알림 파일을 읽는다
rules = load_json("config/escalation_rules.json")                                           # 규칙 파일을 읽는다
tickets = []                                                                                # 만든 티켓을 저장할 빈 리스트

window = rules["merge_window_minutes"]                                                      # 같은 사건으로 보는 시간(분)을 꺼낸다
print("--- 단계 1: 알림", len(alerts), "건 처리 (합치는 시간", window, "분)")               # 단계 1 시작을 알리는 줄과 개수
for alert in alerts:                                                                        # 알림을 하나씩 읽는다
    ticket, action = handle_alert(alert, tickets, rules)                                    # 알림을 처리하고 티켓과 처리 방식을 함께 받는다
    print(alert["id"], "->", ticket["id"], action, "· 합쳐진 알림", ticket["count"], "건")  # 알림 한 건의 결과를 출력한다

print("--- 단계 2: 알림", len(alerts), "건 → 티켓", len(tickets), "장")                     # 단계 2 시작을 알리는 줄과 개수
for ticket in tickets:                                                                      # 티켓을 하나씩 읽는다
    print(ticket["id"], ticket["title"], "· 알림", ticket["incidents"], "· 상태", ticket["status"])  # 티켓 한 줄을 출력한다

print("--- 단계 3: TCK-1 상태 바꾸기")                                                      # 단계 3 시작을 알리는 줄
first = tickets[0]                                                                          # 첫 번째 티켓을 꺼낸다
moves = [("확인 중", "kim.sec", 50), ("해결", "kim.sec", 65), ("열림", "lee.soc", 70)]      # 바꿀 상태 · 바꾼 사람 · 시각을 모은 리스트
for new_status, who, minute in moves:                                                       # 세 값을 한 번에 받아 하나씩 읽는다
    changed = change_ticket_status(first, new_status, minute, who)                          # 상태를 바꿔 본다
    if changed:                                                                             # 바뀌었으면
        print(first["id"], "→", new_status, "· 바꾼 사람", who)                             # 바뀐 상태를 출력한다
    else:                                                                                   # 안 바뀌었으면
        reason = first["status"] + "에서는 갈 수 없음"                                      # 거절한 이유를 문자열로 만든다
        print(first["id"], "→", new_status, "· 거절됨 ·", reason)                           # 거절한 이유를 출력한다
print("댓글 기록:")                                                                         # 댓글 제목을 출력한다
for comment in first["comments"]:                                                           # 댓글을 하나씩 읽는다
    print(" -", comment)                                                                    # 댓글을 출력한다
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch ticket_merge.py day04_3-1_run.py
   ls
   ```
2. **[VS Code]** `ticket_merge.py` 1 ~ 9번을 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day04_3-1_run.py
   ```
4. 출력은 세 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 11줄, 단계 2 는 티켓 목록 7줄, 단계 3 은 상태 바꾸기 3줄과 `댓글 기록:` 줄, 댓글 2줄입니다. 단계 3 은 알림 처리와 별개입니다. TCK-1 에 대해 담당자가 50분과 65분에 상태를 바꾸는 동작을 했다고 가정하고, 상태 전이만 보여 줍니다.
5. **[보고서]** `day04_am_report.md` 의 `## 3교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣어 주세요. 그리고 단계 2 의 티켓 수와 TCK-1 에 병합된 알림 번호를 적어 주세요.
   - (나) 🔍 `INC-210` 은 TCK-1 에 병합됐고 `INC-211` 은 새 티켓이 생성됐습니다. 각각 그렇게 처리된 사유를 적어 주세요. 근거는 두 알림이 수신된 시각과 TCK-1 의 마지막 갱신 시각입니다. 그다음 60분을 티켓 생성 시각(0분)부터 계산한다면 `INC-210` 이 어떻게 처리될지 적어 주세요.
   - (다) 🔍 단계 3 에서 `해결 → 열림` 전이가 거절됐습니다. 이 전이를 허용하면 어떤 문제가 생기는지 적어 주세요. 그다음 병합 조건에서 `해결` 확인을 제외한다고 가정합니다. 이때 해결 후에 수신된 같은 알림이 어떻게 처리되는지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 조건이 모두 맞으면 | `if ticket["entity"] == alert["entity"] and ticket["rule"] == alert["rule"]:` |
| 이하이면 | `if gap <= window:` |
| 딕셔너리의 숫자를 1 늘리기 | `ticket["count"] = ticket["count"] + 1` |
| 딕셔너리 안의 리스트에 추가 | `ticket["incidents"].append(alert["id"])` |
| 함수 결과를 변수에 저장 | `existing = find_open_ticket(tickets, alert, window)` |
| 없는 값인지 | `if existing is None:` |
| 함수 호출만 하기 | `merge_alert(existing, alert)` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 등급별 수신자에게 알림을 전파하고, 전송 간격을 제한해 알림 피로를 줄이며, 실패하면 재시도하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 티켓을 생성해도 담당자에게는 별도로 통지되지 않습니다. 그래서 담당자는 티켓 목록을 직접 조회하기 전에는 새 티켓이 생성된 것을 알 수 없습니다. 따라서 티켓을 생성하거나 병합할 때마다 담당자에게 알림을 보내야 합니다. 관제 팀은 알림 서버로 담당자에게 알림을 전달합니다. <mark style="background:#e0d4ff">1과목에서 만든 `notifier.py` 의 `notify` 함수가 메시지를 그 알림 서버로 전송합니다</mark>.
> - **문제**: 두 가지입니다.
>   - 병합된 알림마다 메시지를 전송하면 같은 알림이 반복해서 전달됩니다. 예를 들어 퇴사한 `dami` 계정 하나 때문에 TCK-1 알림이 네 번 전달됩니다. 그러면 담당자가 알림을 무시하게 됩니다. 이를 알림 피로(alert fatigue: 알림이 너무 많아 중요한 알림에도 반응이 둔해지는 현상)라고 합니다.
>   - 알림 서버가 일시적으로 응답하지 않으면 알림이 전달되지 않습니다. 이때 프로그램이 다시 전송하지 않으면, 담당자는 사건이 발생한 사실조차 알지 못합니다.
> - **부탁**: 다음 세 가지를 만들어 주세요.
>   - 등급별로 수신자를 정해 주세요.
>   - 같은 티켓에 새 알림이 병합됐을 때는 <mark style="background:#ffdcb0">마지막으로 알린 후 30분이 지난 경우에만 다시 알려 주세요</mark>.
>   - 알림 서버 전송이 실패하면 최대 3번까지 재시도(실패한 전송을 다시 시도하는 일)해 주세요.
> - **바뀌는 점**: <mark style="background:#bde3ff">알림 11건 가운데 9건은 담당자에게 전송하고, 2건은 전송을 생략합니다</mark>(출력에서는 `건너뜀`). 생략하는 알림은 `INC-205` 와 `INC-206` 입니다. 예를 들어 `INC-205` 는 TCK-1 에 마지막으로 알린 0분에서 14분이 지났고 30분보다 짧으므로 건너뜁니다. `INC-209` 는 40분이 지나 30분 이상이므로 전송합니다. high 는 `team.lead`(팀장)까지 3명에게, low 는 `kim.sec` 한 명에게만 전달됩니다. 3번 모두 실패한 알림은 「실패」로 표시됩니다(실패 기록을 파일에 저장하는 기능은 이 수업에 없습니다). 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 4.1 알림 전파는 「수신자 · 전송 간격 · 실패 시 재시도」를 정해야 운영할 수 있다

알림 전파에서는 세 가지를 정해야 합니다. <mark>누구에게 보낼지, 얼마나 자주 보낼지, 실패하면 어떻게 할지</mark>입니다. 오늘 적용한 정책은 아래 표와 같습니다.

| 정할 것 | 오늘 적용한 정책 | 규칙 파일의 키 |
|---|---|---|
| 누구에게 | 등급별로 수신자 리스트가 다르다. <mark style="background:#ffdcb0">high 는 `kim.sec` · `lee.soc` · `team.lead`, mid 는 `kim.sec` · `lee.soc`, low 는 `kim.sec`</mark> | `recipients` |
| 얼마나 자주 | 처음 전송하는 알림은 즉시 전송한다. 같은 티켓은 마지막 전송 후 30분이 지나야 다시 전송한다 | `send_gap_minutes` |
| 실패하면 | 실패하면 다시 보내 보며, 처음 전송을 포함해 최대 3번 시도한다. 3번 모두 실패하면 「실패」로 처리한다 | `ticket_notice.py` 의 `MAX_TRIES` |

- 알림이 너무 많아 담당자가 알림을 무시하게 되는 현상을 **알림 피로**(alert fatigue, 얼럿 퍼티그)라고 합니다. 이 문제를 줄이는 방법 가운데 하나가 같은 티켓에 알림을 전송하는 사이에 최소 간격을 두는 것입니다. 예를 들어 `dami` 의 알림 네 건이 TCK-1 에 병합되지만, 30분 간격 때문에 담당자에게는 <mark style="background:#bde3ff">`INC-201` · `INC-209` · `INC-210` 세 번만 전송됩니다</mark>.
- 1과목의 `notify(message, url)` 는 메시지를 알림 서버 주소(`url`)로 전송합니다. 성공하면 `True` 를 리턴합니다. 실패하면 `[알림 실패]` 와 오류 이름을 출력하고 `False` 를 리턴합니다. `ConnectionError`(연결 오류)는 서버에 연결하지 못했을 때 발생하는 오류 이름입니다.
- `notify` 는 서버에 요청을 전송하기만 하면 `True` 를 리턴합니다. <mark style="background:#ffc4d6">서버가 반환한 HTTP 응답 코드(예: 200 은 성공)는 확인하지 않습니다</mark>. 실제 제품에서는 응답 코드까지 검증합니다.
- 알림 서버는 1과목에서 만든 `alert_server.py` 입니다. 터미널 하나에서 실행해 두면, 알림이 수신될 때마다 그 터미널에 `[알림 받음]` 과 메시지가 출력됩니다. 주소는 `alert_url` 입니다. 이 서버는 요청을 수신하는 번호인 5001번 포트(port, 포트)를 사용합니다.
- 메시지는 `[등급] 대상 — 규칙 · 티켓 번호 · 알림 N건 · 기한 M분 · 수신: 이름들` 모양입니다.
- 전송이 모두 실패했을 때의 대응은 보고서 (다)에서 다룹니다.

함수 네 개와 실행 파일에서 직접 쓰는 곳은 **아홉 군데**입니다.

```
ticket_notice.py   pick_recipients     : 등급에 맞는 수신자 리스트를 고른다 (1번)
                   should_send         : 지금 알려도 되는지 정한다. 처음이거나 간격이 지났으면 True (2 ~ 4번)
                   send_with_retry     : 최대 3번 보내 보고, 성공한 시도 번호를 리턴한다. 모두 실패하면 0 (5 · 6번)
                   send_ticket_notice  : 위 세 함수로 티켓 알림을 보내고 「전송」 · 「건너뜀」 · 「실패」를 리턴한다 (미리 채움)
실행 파일          day04_4-1_run.py    : 알림마다 티켓 알림을 보내고 (7번), 보냈으면 센다 (8 · 9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 4-1 · 등급별 수신자에게 알림을 전파하고, 전송 간격을 제한해 알림 피로를 줄이며, 실패하면 재시도하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>티켓은 생성되지만 담당자에게 알림을 전파하는 단계가 없습니다. 그래서 담당자가 티켓 목록을 직접 조회하기 전에는 새 티켓이 생성된 것을 알 수 없습니다</mark>.
- **만드는 것**: 수신자 선택 · 전송 여부 판정 · 최대 3번 재시도 전송(`ticket_notice.py`), 알림마다 담당자에게 알림을 전파하고 집계한 결과(`day04_4-1_run.py`).
- **실행하면**: <mark>단계 1: 알림 11건의 처리와 담당자 알리기 결과, 단계 2: 전송과 건너뜀 건수 · 티켓별 알린 횟수, 단계 3: 꺼진 주소로 3번 보내 보기, 단계 4: 저장한 티켓이 나옵니다.</mark>

**🎯 할 일**: 알림 서버를 켜고, 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 1 ~ 3 과 서버 터미널을 읽습니다.

**`ticket_notice.py`** — 담당자에게 알림을 전파합니다. 직접 쓰는 곳은 1 ~ 6번입니다. 3교시의 `ticket_merge.py` 와 1과목에서 복사한 `notifier.py` 가 같은 폴더에 있어야 합니다.

```python
from notifier import notify                                            # 1과목 notifier.py 의 알림 함수를 불러온다 (성공하면 True, 실패하면 False)

MAX_TRIES = 3                                                          # 알림을 보내 보는 최대 횟수


def pick_recipients(grade, rules):                                     # 등급과 규칙을 받는 함수
    """등급에 맞는 수신자 이름 리스트를 리턴한다.
    위험한 알림일수록 더 많은 사람에게 알려야 할 때 쓴다.
    """
    table = rules["recipients"]                                        # 등급마다 정한 수신자 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table[grade] 를 리턴한다 (이 등급의 수신자 리스트)


def should_send(ticket, now, gap):                                     # 티켓 · 지금 시각(분) · 알림 간격(분)을 받는 함수
    """이 티켓의 알림을 지금 보내도 되면 True, 너무 일러서 건너뛰어야 하면 False 를 리턴한다.
    같은 티켓의 알림이 연달아 가서 사람이 알림을 무시하게 되는 일을 막을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. ticket 의 "notified_count" 가 0 이면 (if, ==) 처음 보내는 것이다
    # 3.   True 를 리턴한다
    elapsed = now - ticket["last_notified"]                            # 마지막으로 보낸 뒤 몇 분 지났는지 — 미리 채운 줄
    # 4. elapsed 가 gap 이상인지(>=)의 결과를 리턴한다


def send_with_retry(message, url, max_tries):                          # 메시지 · 알림 주소 · 최대 횟수를 받는 함수
    """알림을 최대 max_tries 번 보내 본다. 성공한 시도 번호를, 모두 실패하면 0 을 리턴한다.
    알림 서버가 잠깐 응답하지 않을 때 바로 포기하지 않고 다시 보내 보려고 쓴다.
    """
    for attempt in range(1, max_tries + 1):                            # 시도 번호를 1 부터 최대 횟수까지 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. notify(message, url) 의 결과가 참이면 (if)
            # 6. attempt 를 리턴한다
    return 0                                                           # 모두 실패했으면 0 을 리턴한다 — 미리 채운 줄


def send_ticket_notice(ticket, now, rules):                            # 티켓 · 지금 시각(분) · 규칙을 받는 함수
    """티켓 알림을 보낼지 정하고, 보내야 하면 수신자를 붙여 보낸다. 「전송」 · 「건너뜀」 · 「실패」 중 하나를 리턴한다.
    티켓이 만들어지거나 합쳐질 때마다 부른다.
    """
    if not should_send(ticket, now, rules["send_gap_minutes"]):        # 너무 일러서 보내면 안 되면
        return "건너뜀"                                                # 보내지 않고 「건너뜀」을 리턴한다
    recipients = pick_recipients(ticket["grade"], rules)               # 이 등급의 수신자 리스트를 구한다
    names = ""                                                         # 수신자 이름을 이어 붙일 빈 문자열
    for name in recipients:                                            # 수신자를 하나씩 읽는다
        if names != "":                                                # 이미 이름이 있으면
            names = names + ", "                                       # 쉼표를 붙이고
        names = names + name                                           # 이름을 이어 붙인다
    message = ticket["title"] + " · " + ticket["id"] + " · 알림 " + str(ticket["count"]) + "건 · 기한 " + str(ticket["sla_due"]) + "분 · 수신: " + names  # 알림 내용을 만든다
    attempt = send_with_retry(message, rules["alert_url"], MAX_TRIES)  # 최대 3번까지 보내 본다
    if attempt == 0:                                                   # 모두 실패했으면
        return "실패"                                                  # 「실패」를 리턴한다
    ticket["notified_count"] = ticket["notified_count"] + 1            # 보낸 횟수를 1 늘린다
    ticket["last_notified"] = now                                      # 마지막으로 보낸 시각을 적는다
    return "전송"                                                      # 「전송」을 리턴한다
```

**`day04_4-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 7번 아래에는 `result = …` 를 씁니다. 8번 아래에는 `if … :` 를 씁니다. 9번 아래에는 한 단계 들여쓴 줄을 씁니다.

```python
from incident import load_json, save_json                                             # 월요일 파일의 JSON 읽기 · 저장 함수를 불러온다
from ticket_merge import handle_alert                                                 # 3교시에 만든 알림 처리 함수를 불러온다
from ticket_notice import send_ticket_notice, send_with_retry, MAX_TRIES              # 방금 만든 알림 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                 # 오늘 오전 알림 파일을 읽는다
rules = load_json("config/escalation_rules.json")                                     # 규칙 파일을 읽는다
tickets = []                                                                          # 만든 티켓을 저장할 빈 리스트
sent_count = 0                                                                        # 알림을 보낸 수 : 처음에는 0
skipped_count = 0                                                                     # 건너뛴 수 : 처음에는 0

print("--- 단계 1: 알림", len(alerts), "건 처리와 담당자 알리기")                     # 단계 1 시작을 알리는 줄과 개수
for alert in alerts:                                                                  # 알림을 하나씩 읽는다
    ticket, action = handle_alert(alert, tickets, rules)                              # 알림을 처리하고 티켓과 처리 방식을 받는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. send_ticket_notice(ticket, alert["minute"], rules) 의 결과를 result 에 저장한다
    print(alert["id"], "->", ticket["id"], action, "· 담당자 알리기:", result)        # 알림 한 건의 결과를 출력한다
    # 8. result 가 "전송" 이면 (if, ==)
        # 9. sent_count 에 sent_count + 1 을 저장한다 (1 늘린다)
    if result == "건너뜀":                                                            # 건너뛰었으면 — 미리 채운 줄
        skipped_count = skipped_count + 1                                             # 건너뛴 수를 1 늘린다 — 미리 채운 줄

print("--- 단계 2: 담당자에게 전송", sent_count, "건 · 건너뜀", skipped_count, "건")  # 단계 2 시작을 알리는 줄과 건수
for ticket in tickets:                                                                # 티켓을 하나씩 읽는다
    print(ticket["id"], "담당자에게 알린 횟수", ticket["notified_count"], "번 · 마지막으로 알린 시각", ticket["last_notified"], "분")  # 티켓별 전송 횟수를 출력한다

url_off = "http://127.0.0.1:5999/alert"                                               # 아무 서버도 없는 주소 — 알림 서버가 꺼진 상황
print("--- 단계 3: 꺼진 주소로 최대", MAX_TRIES, "번 보내 보기")                      # 단계 3 시작을 알리는 줄
attempt = send_with_retry("[테스트] 꺼진 알림 서버", url_off, MAX_TRIES)              # 꺼진 주소로 보내 본다
print("성공한 시도 번호:", attempt, "(0 은 모두 실패)")                               # 시도 결과를 출력한다

save_json(tickets, "tickets_day4.json")                                               # 티켓을 파일에 저장한다
saved = load_json("tickets_day4.json")                                                # 저장한 파일을 다시 읽는다
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")                             # 단계 4 시작을 알리는 줄과 장수
```

**순서**

1. **[터미널]** 알림 서버를 켭니다. 먼저 VS Code 터미널 창 오른쪽 위의 `+` 로 **새 터미널**을 하나 더 엽니다. 그 터미널에서 위치를 확인한 뒤 서버를 켭니다(맥북은 `python3`). <mark style="background:#bde3ff">`Running on http://127.0.0.1:5001` 이 보이면</mark> 됩니다. 이 터미널은 그대로 두고 쓰지 않습니다.
   ```bash
   pwd
   python alert_server.py
   ```
   - `pwd` 결과가 `soar_response` 로 끝나지 않으면 `cd soar_response` 를 먼저 입력합니다. 새 터미널이 다른 폴더에서 열릴 수 있습니다.
2. **[터미널]** 처음 쓰던 터미널로 돌아와 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch ticket_notice.py day04_4-1_run.py
   ls
   ```
3. **[VS Code]** `ticket_notice.py` 1 ~ 6번, `day04_4-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
4. **[터미널]** 처음 쓰던 터미널에서 <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day04_4-1_run.py
   ```
5. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 11줄, 단계 2 는 숫자가 제목 줄에 함께 나오고 그 아래 티켓 7줄, 단계 3 은 `[알림 실패] ConnectionError` 3줄과 결과 1줄(재시도를 확인하는 시험입니다), 단계 4 는 숫자가 제목 줄에 함께 나오고 그 아래 줄이 없습니다. <mark style="background:#bde3ff">알림 서버 터미널에는 `[알림 받음]` 줄이 9개 출력됩니다.</mark>
6. **[터미널]** 알림 서버 터미널을 `Ctrl + C` 로 끕니다.
7. **[보고서]** `day04_am_report.md` 의 `## 4교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 알림 서버 터미널에 출력된 `[알림 받음]` 줄 수와, 단계 2 의 전송 건수 · 건너뜀 건수를 적어 주세요.
   - (나) 🔍 `INC-205` 와 `INC-206` 은 전송을 생략했고 `INC-209` 와 `INC-210` 은 전송했습니다. 각각 전송을 생략한 사유와 전송한 사유를 적어 주세요. 근거는 각 알림이 수신된 시각과 해당 티켓의 마지막 전송 시각입니다. 그다음 전송 간격을 제한하지 않으면 담당자에게 어떤 일이 생기는지 적어 주세요.
   - (다) 🔍 단계 3 에서 꺼진 주소로 3번 전송을 시도했고 모두 실패했습니다. `[알림 실패] ConnectionError`(연결 오류: 서버에 연결하지 못했을 때 발생하는 오류 이름)가 3번 출력된 사유를 적어 주세요. 그다음 3번 모두 실패한 알림이 누락되지 않게 하려면, 실제 관제에서 무엇을 추가로 해야 하는지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 딕셔너리에서 값을 읽어 리턴 | `return table[grade]` |
| 같으면 | `if ticket["notified_count"] == 0:` |
| 이상인지의 결과 리턴 | `return elapsed >= gap` |
| 함수 결과가 참이면 | `if notify(message, url):` |
| 번호를 1 부터 하나씩 읽기 | `for attempt in range(1, max_tries + 1):` |
| 함수 결과를 변수에 저장 | `result = send_ticket_notice(ticket, alert["minute"], rules)` |
| 1 늘려 다시 저장 | `sent_count = sent_count + 1` |

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 알림으로 티켓을 생성하고 응답 기한(SLA)을 계산했으며, 조치 확인에 실패한 건을 수동 확인 대상으로 표시했다 | 오전 2-1 |
| 같은 사건의 알림을 티켓 한 장으로 병합(중복 제거)하고 허용된 순서로 상태를 전이했다 | 오전 3-1 |
| 등급별 수신자에게 알림을 전파하고, 전송 간격을 제한했으며, 실패하면 최대 3번 재시도했다 | 오전 4-1 |

오전에 구현한 티켓 생성 · 병합 · 알림 전파는 오후로 이어집니다. <mark>오후에는 응답 기한이 지나도 아무도 확인하지 않은 티켓을 상급자에게 올리는 에스컬레이션(escalation)을 구현합니다. 그리고 오전부터 만든 것을 가상 근무 시간 동안 한 번에 실행합니다.</mark>

---

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`ticketing.py` 의 1 ~ 6번입니다.

```python
    # 1. "[" + grade + "] " + entity + " — " + rule 을 이어 붙인 문자열를 리턴한다
    return "[" + grade + "] " + entity + " — " + rule  # 등급 · 대상 · 규칙을 이어 붙인 제목을 리턴한다
    # 2. next_steps.get(status, DEFAULT_NEXT_STEP) 의 결과를 리턴한다 (키가 없으면 기본 문장)
    return next_steps.get(status, DEFAULT_NEXT_STEP)   # 상태에 맞는 다음 할 일을 리턴한다 (없으면 기본 문장)
        # 3. text 안에 "확인 실패" 가 들어 있으면 (if, in)
        if "확인 실패" in text:                        # 문장 안에 확인 실패가 있으면
            # 4. True 를 리턴한다
            return True                                # 확인 실패가 있다고 True 를 리턴한다
    # 5. sla_table[alert["grade"]] 를 sla_minutes 에 저장한다 (이 알림 등급의 응답 기한)
    sla_minutes = sla_table[alert["grade"]]            # 이 알림 등급의 응답 기한(분)을 꺼낸다
    # 6. alert["minute"] + sla_minutes 를 sla_due 에 저장한다 (응답해야 하는 시각)
    sla_due = alert["minute"] + sla_minutes            # 알림이 온 시각 + 응답 기한 = 응답해야 하는 시각
```

`day04_2-1_run.py` 의 7 ~ 9번입니다.

```python
    # 7. make_ticket(alert, ticket_no, rules, NEXT_STEPS) 의 결과를 ticket 에 저장한다
    ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)  # 알림으로 티켓을 만든다
    # 8. tickets 리스트에 ticket 을 추가한다 (append)
    tickets.append(ticket)                                     # 티켓 리스트에 추가한다
        # 9. manual_count 에 manual_count + 1 을 저장한다 (1 늘린다)
        manual_count = manual_count + 1                        # 직접 확인이 필요한 티켓 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 직접 확인이 필요한 티켓은 <mark style="background:#bde3ff">**TCK-7**</mark> 한 장이고, 응답 기한 시각이 가장 이른 티켓은 <mark style="background:#bde3ff">**TCK-1**</mark>(15분)입니다.

```
--- 단계 1: 불러온 알림 11 건 · 응답 기한을 정한 등급 3 개
--- 단계 2: 알림마다 만든 티켓
TCK-1 [high] dami — 퇴사한 계정 · 만든 시각 0 분 · 기한 15 분
TCK-2 [low] 198.51.100.90 — 경로 스캔 · 만든 시각 3 분 · 기한 243 분
TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 만든 시각 8 분 · 기한 68 분
TCK-4 [mid] seoyeon — 대량 다운로드 · 만든 시각 12 분 · 기한 72 분
TCK-5 [high] dami — 퇴사한 계정 · 만든 시각 14 분 · 기한 29 분
TCK-6 [low] 198.51.100.90 — 경로 스캔 · 만든 시각 20 분 · 기한 260 분
TCK-7 [low] 203.0.113.250 — 경로 스캔 · 만든 시각 30 분 · 기한 270 분
TCK-8 [mid] hana — 업무 시간 밖 로그인 · 만든 시각 35 분 · 기한 95 분
TCK-9 [high] dami — 퇴사한 계정 · 만든 시각 40 분 · 기한 55 분
TCK-10 [high] dami — 퇴사한 계정 · 만든 시각 95 분 · 기한 110 분
TCK-11 [high] dami — 퇴사한 계정 · 만든 시각 160 분 · 기한 175 분
--- 단계 3: 티켓 본문 예 (TCK-1)
제목: [high] dami — 퇴사한 계정
조치 내역:
 - 계정 잠금: 잠기지 않음 → 잠김
 - 세션 종료: 세션 2개 → 세션 0개
다음 할 일: 조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다
응답 기한: 15 분 (만든 시각 0 분)
--- 단계 4: 직접 확인이 필요한 티켓 1 건
TCK-7 [low] 203.0.113.250 — 경로 스캔 → 조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다
```

- (나) `INC-207` 의 `done` 문장이 <mark style="background:#bde3ff">`IP 차단: 차단되지 않음 → 차단되지 않음 (확인 실패)`</mark> 입니다. `has_failed_action` 이 이 문장에서 「확인 실패」를 찾아 `True` 를 리턴합니다. 그래서 후속 조치(`next_step`)가 직접 확인을 지시하는 문장으로 교체됩니다.
  - 이 표시가 없으면 `조치됨` 용 문장(「조치 결과가 맞는지 확인하고…」)만 보입니다.
  - 그러면 담당자는 IP 가 차단됐다고 판단할 수 있습니다. 그 결과 <mark style="background:#ffc4d6">차단되지 않은 공격 IP 의 접속이 계속되는 것을 놓칠 수 있습니다</mark>.
- (다) 응답 기한 시각은 **알림 수신 시각 + 등급별 응답 기한**입니다. TCK-1 은 high 라서 <mark style="background:#bde3ff">0 + 15 = 15분이고, TCK-2 는 low 라서 3 + 240 = 243분</mark>입니다.
  - 모든 티켓의 응답 기한이 240분이면 긴급한 high 알림도 늦게 확인하게 됩니다. 모든 응답 기한이 15분이면 긴급하지 않은 low 알림까지 15분 안에 확인해야 합니다.
  - 그러면 심각도에 따라 처리 우선순위를 정하기 어렵습니다.

**왜**

- <mark>티켓에 「사건 개요 · 이미 수행한 조치 · 후속 조치 · 응답 기한」이 기재되어 있으면, 담당자가 알림 원문을 다시 찾지 않고 즉시 대응에 착수할 수 있습니다.</mark> 사후 검증에 실패한 건을 별도로 표시하면, 자동 대응이 완료하지 못한 조치를 사람이 직접 확인할 수 있습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**제목이 `None` 으로 나옵니다.**</mark> 단계 2 의 줄이 이 실수의 결과입니다.

```
--- 단계 2: 알림마다 만든 티켓
TCK-1 None · 만든 시각 0 분 · 기한 15 분
TCK-2 None · 만든 시각 3 분 · 기한 243 분
```

- 2번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**다음 할 일이 `None` 으로 나옵니다.**</mark> 단계 3 의 `다음 할 일:` 줄이 이 실수의 결과입니다.

```
--- 단계 3: 티켓 본문 예 (TCK-1)
제목: [high] dami — 퇴사한 계정
조치 내역:
 - 계정 잠금: 잠기지 않음 → 잠김
 - 세션 종료: 세션 2개 → 세션 0개
다음 할 일: None
응답 기한: 15 분 (만든 시각 0 분)
```

- 3번의 `if` 를 빠뜨리고 4번만 쓰면 <mark style="background:#ffc4d6">**조치 내역이 있는 티켓이 모두 직접 확인 대상이 됩니다.**</mark> 단계 4 가 1건이 아니라 8건으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 4: 직접 확인이 필요한 티켓 8 건
```

- 4번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError`(들여쓰기 오류)로 시작하는 오류입니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 5번을 비워 두면 `sla_minutes` 가 만들어지지 않아 오류가 납니다. <mark style="background:#ffc4d6">**6번에서 쓰기 전에 5번에서 만들어야 합니다.**</mark> 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'sla_minutes' is not defined
```

- 6번을 비워 두면 `sla_due` 가 만들어지지 않아 티켓을 만드는 줄에서 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'sla_due' is not defined
```

- 7번을 비워 두면 `ticket` 이 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'ticket' is not defined
```

- 8번을 비워 두면 티켓이 리스트에 모이지 않습니다. 단계 2 의 줄은 나오지만 번호가 모두 `TCK-1` 이고, 단계 3 에서 오류가 납니다.

```
IndexError: list index out of range
```

- 9번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError` 로 시작하는 오류입니다.

```
IndentationError: expected an indented block
```

**관제에서는**

- 티켓은 알림 내용과 처리 상황을 담당자가 확인하도록 남기는 기록입니다. 그래서 제목 작성 규칙과 응답 기한(SLA)을 팀이 미리 정의합니다. <mark>사후 검증에 실패한 건은 「조치 완료」와 구분해 별도로 표시하는 것이 기본입니다.</mark> <mark style="background:#ffdcb0">오늘의 15분 · 60분 · 240분은 예시이고</mark>, 실제 값은 팀과 고객사 계약마다 다릅니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — `ticket_merge.py` 의 1 ~ 9번입니다.

```python
        # 1. ticket 의 "entity" 가 alert 의 "entity" 와 같고(and) ticket 의 "rule" 도 alert 의 "rule" 과 같으면 (if, ==)
        if ticket["entity"] == alert["entity"] and ticket["rule"] == alert["rule"]:  # 같은 대상 · 같은 규칙이면
                # 2. gap 이 window 이하이면 (if, <=)
                if gap <= window:                                                    # 합치는 시간 안이면
                    # 3. ticket 을 리턴한다
                    return ticket                                                    # 그 티켓을 리턴한다
    # 4. ticket 의 "count" 에 ticket["count"] + 1 을 저장한다 (1 늘린다)
    ticket["count"] = ticket["count"] + 1                                            # 합쳐진 알림 수를 1 늘린다
    # 5. ticket 의 "incidents" 리스트에 alert 의 "id" 를 추가한다 (append)
    ticket["incidents"].append(alert["id"])                                          # 합쳐진 알림 번호를 추가한다
    # 6. ticket 의 "updated_at" 에 alert 의 "minute" 을 저장한다
    ticket["updated_at"] = alert["minute"]                                           # 갱신 시각을 이 알림이 온 시각으로 바꾼다
    # 7. find_open_ticket(tickets, alert, window) 의 결과를 existing 에 저장한다
    existing = find_open_ticket(tickets, alert, window)                              # 합칠 티켓을 찾는다
    # 8. existing 이 None 이면 (if, is)
    if existing is None:                                                             # 합칠 티켓이 없으면
    # 9. merge_alert(existing, alert) 를 호출한다 (합칠 티켓이 있을 때만 여기까지 온다)
    merge_alert(existing, alert)                                                     # 찾은 티켓에 새 알림을 합친다
```

위 줄만 보면 들여쓰기가 헷갈리니, 두 함수의 완성된 모양을 함께 봅니다. 미리 채운 줄도 보입니다. 1번의 `if` 아래에 미리 채운 두 줄이 있고, 8번의 `if` 아래에는 미리 채운 네 줄이 있습니다. 9번은 그 `if` 가 끝난 뒤 한 단계 왼쪽에서 다시 시작합니다.

**전체 모양 — `find_open_ticket`**

```python
def find_open_ticket(tickets, alert, window):                                        # 티켓 리스트 · 알림 · 병합 시간(분)을 받는 함수
    """같은 대상 · 같은 규칙이고, 해결되지 않았고, window 분 안에 갱신된 티켓을 찾아 리턴한다. 없으면 None 을 리턴한다.
    같은 사건의 알림이 티켓 여러 장이 되는 것을 막을 때 쓴다.
    """
    for ticket in tickets:                                                           # 티켓을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        if ticket["entity"] == alert["entity"] and ticket["rule"] == alert["rule"]:  # 같은 대상 · 같은 규칙이면
            if ticket["status"] != "해결":                                           # 해결되지 않은 티켓이면 — 미리 채운 줄
                gap = alert["minute"] - ticket["updated_at"]                         # 마지막 갱신 뒤 몇 분 지났는지 — 미리 채운 줄
                if gap <= window:                                                    # 합치는 시간 안이면
                    return ticket                                                    # 그 티켓을 리턴한다
    return None                                                                      # 맞는 티켓이 없으면 None 을 리턴한다 — 미리 채운 줄
```

**전체 모양 — `handle_alert`**

```python
def handle_alert(alert, tickets, rules):                           # 알림 · 티켓 리스트 · 규칙을 받는 함수
    """알림 한 건을 처리한다. 합칠 티켓이 있으면 합치고, 없으면 새 티켓을 만든다. 처리한 티켓과 「새 티켓」 또는 「병합」을 함께 리턴한다.
    알림이 올 때마다 부른다.
    """
    window = rules["merge_window_minutes"]                         # 같은 사건으로 보는 시간(분) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    existing = find_open_ticket(tickets, alert, window)            # 합칠 티켓을 찾는다
    if existing is None:                                           # 합칠 티켓이 없으면
        ticket_no = len(tickets) + 1                               # 새 티켓 번호 — 미리 채운 줄
        ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)  # 새 티켓을 만들고 — 미리 채운 줄
        tickets.append(ticket)                                     # 티켓 리스트에 추가한다 — 미리 채운 줄
        return ticket, "새 티켓"                                   # 티켓과 「새 티켓」을 함께 리턴하고 끝낸다 — 미리 채운 줄
    merge_alert(existing, alert)                                   # 찾은 티켓에 새 알림을 합친다
    return existing, "병합"                                        # 티켓과 「병합」을 함께 리턴한다 — 미리 채운 줄
```

**결과**

- (가) 출력은 다음과 같습니다. 티켓은 <mark style="background:#bde3ff">**7장**</mark>이고, TCK-1 에 병합된 알림은 <mark style="background:#bde3ff">**INC-201 · INC-205 · INC-209 · INC-210**</mark> 입니다.

```
--- 단계 1: 알림 11 건 처리 (합치는 시간 60 분)
INC-201 -> TCK-1 새 티켓 · 합쳐진 알림 1 건
INC-202 -> TCK-2 새 티켓 · 합쳐진 알림 1 건
INC-203 -> TCK-3 새 티켓 · 합쳐진 알림 1 건
INC-204 -> TCK-4 새 티켓 · 합쳐진 알림 1 건
INC-205 -> TCK-1 병합 · 합쳐진 알림 2 건
INC-206 -> TCK-2 병합 · 합쳐진 알림 2 건
INC-207 -> TCK-5 새 티켓 · 합쳐진 알림 1 건
INC-208 -> TCK-6 새 티켓 · 합쳐진 알림 1 건
INC-209 -> TCK-1 병합 · 합쳐진 알림 3 건
INC-210 -> TCK-1 병합 · 합쳐진 알림 4 건
INC-211 -> TCK-7 새 티켓 · 합쳐진 알림 1 건
--- 단계 2: 알림 11 건 → 티켓 7 장
TCK-1 [high] dami — 퇴사한 계정 · 알림 ['INC-201', 'INC-205', 'INC-209', 'INC-210'] · 상태 열림
TCK-2 [low] 198.51.100.90 — 경로 스캔 · 알림 ['INC-202', 'INC-206'] · 상태 열림
TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 알림 ['INC-203'] · 상태 열림
TCK-4 [mid] seoyeon — 대량 다운로드 · 알림 ['INC-204'] · 상태 열림
TCK-5 [low] 203.0.113.250 — 경로 스캔 · 알림 ['INC-207'] · 상태 열림
TCK-6 [mid] hana — 업무 시간 밖 로그인 · 알림 ['INC-208'] · 상태 열림
TCK-7 [high] dami — 퇴사한 계정 · 알림 ['INC-211'] · 상태 열림
--- 단계 3: TCK-1 상태 바꾸기
TCK-1 → 확인 중 · 바꾼 사람 kim.sec
TCK-1 → 해결 · 바꾼 사람 kim.sec
TCK-1 → 열림 · 거절됨 · 해결에서는 갈 수 없음
댓글 기록:
 - kim.sec · 50분 · 열림 → 확인 중
 - kim.sec · 65분 · 확인 중 → 해결
```

- (나) TCK-1 의 마지막 갱신 시각은 `INC-209` 가 병합된 40분입니다.
  - `INC-210` 은 95분에 수신됐으니 95 − 40 = 55분이라 60분 이하여서 <mark style="background:#bde3ff">병합됐습니다.</mark>
  - 병합되면서 마지막 갱신 시각이 95분이 되고, `INC-211` 은 160분에 수신되어 160 − 95 = 65분이 되어 <mark style="background:#bde3ff">새 티켓(TCK-7)</mark> 이 됐습니다.
  - 티켓 생성 시각(0분)부터 계산하면 `INC-209`(40분)는 병합되지만 `INC-210`(95분)은 60분을 넘어 새 티켓이 됩니다. 그러면 티켓이 8장이 되고 TCK-1 의 알림은 3건뿐입니다.
- (다) `해결 → 열림` 전이를 허용하면 기록이 서로 어긋납니다. 댓글(상태 전이 이력)에는 누가 언제 「해결」했다고 기록되어 있는데, <mark style="background:#ffc4d6">현재 상태는 「열림」이 됩니다</mark>. 또한 해결한 사건이 재발한 것인지, 새 사건인지 구별할 수 없습니다.
  - `해결` 확인이 없으면 해결 후에 수신된 같은 알림이 해결된 티켓에 병합됩니다.
  - 상태가 `해결` 그대로여서 아무도 새 알림이 수신된 것을 확인하지 못합니다.

**왜**

- <mark>같은 사건의 알림을 티켓 한 장으로 병합(중복 제거)하면 담당자가 새로 발생한 사건을 더 쉽게 식별해 처리할 수 있습니다.</mark> 다만 <mark>마지막 갱신 후 경과 시간과 해결 여부를 함께 확인해야 합니다</mark>. 그래야 오래전 알림이 병합되거나 이미 해결된 티켓에 잘못 병합되는 일이 없습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**대상과 규칙을 비교하지 않아 서로 다른 사건이 한 장으로 합쳐집니다.**</mark> 단계 1 에서 `INC-202` 가 `dami` 의 TCK-1 에 합쳐지는 것이 이 실수의 결과입니다.

```
--- 단계 1: 알림 11 건 처리 (합치는 시간 60 분)
INC-201 -> TCK-1 새 티켓 · 합쳐진 알림 1 건
INC-202 -> TCK-1 병합 · 합쳐진 알림 2 건
INC-203 -> TCK-1 병합 · 합쳐진 알림 3 건
INC-204 -> TCK-1 병합 · 합쳐진 알림 4 건
INC-205 -> TCK-1 병합 · 합쳐진 알림 5 건
INC-206 -> TCK-1 병합 · 합쳐진 알림 6 건
```

- 2 · 3번을 비워 두면 합칠 티켓을 찾지 못해 <mark style="background:#ffc4d6">**티켓이 알림 수만큼 만들어집니다.**</mark> 단계 2 의 제목 줄이 이 실수의 결과입니다.

```
--- 단계 2: 알림 11 건 → 티켓 11 장
```

- 2번에서 `<=` 대신 `>=` 를 쓰면 <mark style="background:#ffc4d6">**60분 안의 알림은 합치지 않고 60분이 지난 알림만 합칩니다.**</mark> 티켓 수가 7장이 아니게 됩니다.

```
--- 단계 2: 알림 11 건 → 티켓 9 장
```

- 4번을 비워 두면 합쳐도 <mark style="background:#ffc4d6">**합쳐진 알림 수가 늘지 않습니다.**</mark> 단계 1 에서 `병합` 인데 1건으로 나오는 것이 이 실수의 결과입니다.

```
INC-205 -> TCK-1 병합 · 합쳐진 알림 1 건
INC-206 -> TCK-2 병합 · 합쳐진 알림 1 건
```

- 5번을 비워 두면 <mark style="background:#ffc4d6">**합쳐진 알림 번호가 티켓에 남지 않습니다.**</mark> 단계 2 의 TCK-1 줄에 `INC-201` 한 건만 나오는 것이 이 실수의 결과입니다.

```
TCK-1 [high] dami — 퇴사한 계정 · 알림 ['INC-201'] · 상태 열림
```

- 6번을 비워 두면 갱신 시각이 바뀌지 않아 <mark style="background:#ffc4d6">**60분 기준이 처음 만든 시각부터 재어집니다.**</mark> 티켓이 7장이 아니라 8장이 됩니다.

```
--- 단계 2: 알림 11 건 → 티켓 8 장
TCK-1 [high] dami — 퇴사한 계정 · 알림 ['INC-201', 'INC-205', 'INC-209'] · 상태 열림
TCK-2 [low] 198.51.100.90 — 경로 스캔 · 알림 ['INC-202', 'INC-206'] · 상태 열림
TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 알림 ['INC-203'] · 상태 열림
TCK-4 [mid] seoyeon — 대량 다운로드 · 알림 ['INC-204'] · 상태 열림
TCK-5 [low] 203.0.113.250 — 경로 스캔 · 알림 ['INC-207'] · 상태 열림
TCK-6 [mid] hana — 업무 시간 밖 로그인 · 알림 ['INC-208'] · 상태 열림
TCK-7 [high] dami — 퇴사한 계정 · 알림 ['INC-210'] · 상태 열림
TCK-8 [high] dami — 퇴사한 계정 · 알림 ['INC-211'] · 상태 열림
```

- 7번을 비워 두면 `existing` 이 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'existing' is not defined
```

- 8번을 비워 두면 그 아래 미리 채운 줄들이 `if` 없이 들여쓰기만 남아 실행하기 전에 멈춥니다. `IndentationError` 로 시작하는 오류입니다.

```
IndentationError: unexpected indent
```

- 9번을 비워 두면 찾기만 하고 합치지 않아 <mark style="background:#ffc4d6">**「병합」이라고 나오는데 알림 수가 늘지 않습니다.**</mark> 단계 1 의 `병합` 줄이 이 실수의 결과입니다.

```
INC-205 -> TCK-1 병합 · 합쳐진 알림 1 건
INC-206 -> TCK-2 병합 · 합쳐진 알림 1 건
```

**관제에서는**

- 티켓 도구는 같은 사건의 알림을 병합하는 기능(중복 제거, deduplication: 디듀플리케이션)을 갖고 있는 경우가 많습니다. <mark>병합 기준은 도구마다 다르고, 대상 · 규칙(또는 별칭) 같은 식별 값을 쓰는 경우가 많습니다. 해결된 티켓에 병합할지도 도구와 팀마다 정합니다.</mark> 오늘의 60분은 예시입니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.** 알림 서버를 켠 터미널은 그대로 두고, 처음 쓰던 터미널에서 실행합니다.

```bash
pwd
python day04_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`ticket_notice.py` 의 1 ~ 6번입니다.

```python
    # 1. table[grade] 를 리턴한다 (이 등급의 수신자 리스트)
    return table[grade]                # 이 등급의 수신자 리스트를 리턴한다
    # 2. ticket 의 "notified_count" 가 0 이면 (if, ==) 처음 보내는 것이다
    if ticket["notified_count"] == 0:  # 처음 보내는 것이면
    # 3.   True 를 리턴한다
        return True                    # 바로 보내도 된다고 True 를 리턴한다
    # 4. elapsed 가 gap 이상인지(>=)의 결과를 리턴한다
    return elapsed >= gap              # 알림 간격 이상 지났는지의 결과를 리턴한다
        # 5. notify(message, url) 의 결과가 참이면 (if)
        if notify(message, url):       # 알림을 보냈으면
            # 6. attempt 를 리턴한다
            return attempt             # 성공한 시도 번호를 리턴한다
```

`day04_4-1_run.py` 의 7 ~ 9번입니다.

```python
    # 7. send_ticket_notice(ticket, alert["minute"], rules) 의 결과를 result 에 저장한다
    result = send_ticket_notice(ticket, alert["minute"], rules)  # 티켓 알림을 보내고 결과를 받는다
    # 8. result 가 "전송" 이면 (if, ==)
    if result == "전송":                                         # 알림을 보냈으면
        # 9. sent_count 에 sent_count + 1 을 저장한다 (1 늘린다)
        sent_count = sent_count + 1                              # 보낸 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 2 의 전송은 <mark style="background:#bde3ff">**9건**</mark>, 건너뜀은 <mark style="background:#bde3ff">**2건**</mark>입니다.

```
--- 단계 1: 알림 11 건 처리와 담당자 알리기
INC-201 -> TCK-1 새 티켓 · 담당자 알리기: 전송
INC-202 -> TCK-2 새 티켓 · 담당자 알리기: 전송
INC-203 -> TCK-3 새 티켓 · 담당자 알리기: 전송
INC-204 -> TCK-4 새 티켓 · 담당자 알리기: 전송
INC-205 -> TCK-1 병합 · 담당자 알리기: 건너뜀
INC-206 -> TCK-2 병합 · 담당자 알리기: 건너뜀
INC-207 -> TCK-5 새 티켓 · 담당자 알리기: 전송
INC-208 -> TCK-6 새 티켓 · 담당자 알리기: 전송
INC-209 -> TCK-1 병합 · 담당자 알리기: 전송
INC-210 -> TCK-1 병합 · 담당자 알리기: 전송
INC-211 -> TCK-7 새 티켓 · 담당자 알리기: 전송
--- 단계 2: 담당자에게 전송 9 건 · 건너뜀 2 건
TCK-1 담당자에게 알린 횟수 3 번 · 마지막으로 알린 시각 95 분
TCK-2 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 3 분
TCK-3 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 8 분
TCK-4 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 12 분
TCK-5 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 30 분
TCK-6 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 35 분
TCK-7 담당자에게 알린 횟수 1 번 · 마지막으로 알린 시각 160 분
--- 단계 3: 꺼진 주소로 최대 3 번 보내 보기
[알림 실패] ConnectionError
[알림 실패] ConnectionError
[알림 실패] ConnectionError
성공한 시도 번호: 0 (0 은 모두 실패)
--- 단계 4: 파일에 저장된 티켓 7 장
```

알림 서버 터미널에는 `[알림 받음]` 줄이 <mark style="background:#bde3ff">**9개**</mark> 찍힙니다.

```
[알림 받음] [high] dami — 퇴사한 계정 · TCK-1 · 알림 1건 · 기한 15분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [low] 198.51.100.90 — 경로 스캔 · TCK-2 · 알림 1건 · 기한 243분 · 수신: kim.sec
[알림 받음] [mid] gaeun — 규칙은 허용인데 서버가 거절 · TCK-3 · 알림 1건 · 기한 68분 · 수신: kim.sec, lee.soc
[알림 받음] [mid] seoyeon — 대량 다운로드 · TCK-4 · 알림 1건 · 기한 72분 · 수신: kim.sec, lee.soc
[알림 받음] [low] 203.0.113.250 — 경로 스캔 · TCK-5 · 알림 1건 · 기한 270분 · 수신: kim.sec
[알림 받음] [mid] hana — 업무 시간 밖 로그인 · TCK-6 · 알림 1건 · 기한 95분 · 수신: kim.sec, lee.soc
[알림 받음] [high] dami — 퇴사한 계정 · TCK-1 · 알림 3건 · 기한 15분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [high] dami — 퇴사한 계정 · TCK-1 · 알림 4건 · 기한 15분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [high] dami — 퇴사한 계정 · TCK-7 · 알림 1건 · 기한 175분 · 수신: kim.sec, lee.soc, team.lead
```

- (나) 전송을 생략할지 전송할지는 <mark style="background:#ffdcb0">마지막 전송 시각과 최소 간격(30분)</mark>으로 결정됩니다.
  - `INC-205`(14분): TCK-1 은 0분에 전송했고 14분이 지나 30분보다 짧아서 <mark style="background:#bde3ff">전송을 생략합니다.</mark>
  - `INC-206`(20분): TCK-2 는 3분에 전송했고 17분이 지나 30분보다 짧아 전송을 생략합니다.
  - `INC-209`(40분): TCK-1 은 0분에 전송했고 40분이 지나 30분 이상이라 <mark style="background:#bde3ff">전송합니다.</mark>
  - `INC-210`(95분): TCK-1 은 40분에 마지막으로 전송했고 55분이 지나 30분 이상이므로 전송합니다.
  - 전송을 생략하지 않으면 `dami` 의 같은 알림 4건이 모두 담당자에게 전달되어, 알림 피로로 담당자가 알림을 무시하게 됩니다.
- (다) 꺼진 주소(5999번 포트)에는 알림 서버가 없습니다. 그래서 전송할 때마다 연결 오류(`ConnectionError`)가 발생합니다. `notify` 는 `[알림 실패]` 를 출력한 뒤 `False` 를 리턴합니다. `send_with_retry` 가 최대 3번 시도했으므로 이 줄이 3번 출력됩니다. 3번 모두 실패했으므로 `send_with_retry` 는 0 을 리턴했습니다.
  - <mark style="background:#ffc4d6">이 코드는 3번 모두 실패한 알림을 저장하지 않습니다</mark>. 실제 관제에서는 전송에 실패한 알림의 목록을 별도로 보관합니다.
  - 전화나 메일 같은 대체 채널(fallback channel, 폴백 채널: 기본 수단이 실패했을 때 쓰는 다른 전달 수단)로도 통지해야 합니다. 또한 다음 근무자에게 인수인계(handover)해야 합니다.
  - 이 수업 코드에는 없는 운영 절차입니다.

**왜**

- <mark>알림은 전송하는 것만큼 담당자가 실제로 확인하게 하는 것이 중요합니다.</mark> 수신자를 등급에 맞추고 전송 간격을 두면 알림이 무시되지 않습니다. 알림 서버가 일시적으로 멈춘 것이라면 재시도하는 동안 성공할 수 있습니다. <mark style="background:#ffc4d6">이 코드는 시도 사이에 기다리지 않습니다</mark>. 실제 제품은 재시도 사이에 몇 초의 대기 시간(백오프, backoff)을 둔 뒤 다시 전송합니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 수신자 리스트가 `None` 이 되어 이름을 이어 붙이는 줄에서 오류가 납니다.

```
TypeError: 'NoneType' object is not iterable
```

- 2 · 3번을 비워 두면 <mark style="background:#ffc4d6">**처음 보내는 알림도 간격 계산에서 너무 이르다고 나와 건너뜁니다.**</mark> 단계 1 의 첫 줄부터 `건너뜀` 으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 1: 알림 11 건 처리와 담당자 알리기
INC-201 -> TCK-1 새 티켓 · 담당자 알리기: 건너뜀
INC-202 -> TCK-2 새 티켓 · 담당자 알리기: 건너뜀
INC-203 -> TCK-3 새 티켓 · 담당자 알리기: 건너뜀
```

- 4번을 비워 두면 `should_send` 가 아무것도 리턴하지 않아 <mark style="background:#ffc4d6">**처음이 아닌 알림은 모두 건너뜁니다.**</mark> 전송이 9건이 아니라 7건으로 나옵니다.

```
--- 단계 2: 담당자에게 전송 7 건 · 건너뜀 4 건
```

- 5번의 `if` 를 빠뜨리고 6번만 쓰면 <mark style="background:#ffc4d6">**알림 서버로 보내지도 않고 성공으로 처리됩니다.**</mark> 단계 1 은 모두 `전송` 으로 나오지만 알림 서버 터미널에는 `[알림 받음]` 이 하나도 찍히지 않습니다.

```
--- 단계 1: 알림 11 건 처리와 담당자 알리기
INC-201 -> TCK-1 새 티켓 · 담당자 알리기: 전송
INC-202 -> TCK-2 새 티켓 · 담당자 알리기: 전송
```

- 6번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError` 로 시작하는 오류입니다.

```
IndentationError: expected an indented block
```

- 7번을 비워 두면 `result` 가 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'result' is not defined
```

- 8 · 9번을 비워 두면 알림은 가지만 <mark style="background:#ffc4d6">**센 값이 늘지 않아 전송이 0건으로 나옵니다.**</mark> 단계 2 의 제목 줄이 이 실수의 결과입니다.

```
--- 단계 2: 담당자에게 전송 0 건 · 건너뜀 2 건
```

- 알림 서버를 켜지 않고 실행하면 코드는 정상이어도 <mark style="background:#ffc4d6">**모든 알림이 3번씩 실패합니다.**</mark> 단계 1 의 시작이 이렇게 나오면 서버 터미널이 꺼져 있는 것입니다(알림 11건이 모두 `실패` 가 되어 `[알림 실패]` 가 33번 나옵니다).

```
--- 단계 1: 알림 11 건 처리와 담당자 알리기
[알림 실패] ConnectionError
[알림 실패] ConnectionError
[알림 실패] ConnectionError
INC-201 -> TCK-1 새 티켓 · 담당자 알리기: 실패
```

**관제에서는**

- 알림 전파는 「수신자 · 전송 간격 · 실패 시 대응」을 먼저 정합니다. <mark>같은 사건은 병합해 한 번만 통지하고, 긴급한 알림만 상급자에게 에스컬레이션하는 것</mark>이 알림 피로를 줄이는 기본입니다. 이 수업에서는 알림 서버를 사용합니다. 실제 관제에서는 그 자리에 메신저나 호출 도구(pager, 페이저: 호출 메시지를 받는 기기나 앱) 같은 도구를 사용하며, 달라지는 것은 주로 전송 방법입니다.
