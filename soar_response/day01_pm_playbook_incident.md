# 11/9(월) 오후 · 5과목 자동 대응(SOAR) ① — 쏘아가 하는 일 직접 겪기 · 플레이북으로 알림 5건을 한 번에 처리하기 — 실습

오전에 4과목을 마쳤습니다. 4과목에서는 로그를 읽어 **위험한 대상을 찾아 점수와 등급을 매겼습니다.** 오늘 오후부터 시작하는 5과목은 그 **알림이 난 뒤에 하는 일**을 다룹니다. 계정을 잠그고, **티켓**(ticket, 티켓: 처리할 일 한 건을 적어 두고 누가 맡았는지와 처리됐는지를 추적하는 기록)을 만들고, 담당자에게 알리는 일을 정해 둔 절차대로 프로그램이 실행하게 만드는 과목입니다.

오늘은 <mark>**모의 시스템**(실제 서버와 계정 대신 파일로 흉내 낸 시스템)에서 대응이 실제로 일어나는 것</mark>을 봅니다. 실제 서버와 계정은 건드리지 않습니다.

- **5교시**: SOAR 가 무엇인지 읽고, **플레이북**(playbook, 플레이북: 「이런 알림이 오면 이렇게 대응한다」를 미리 적어 둔 대응 절차서) 한 건을 직접 씁니다. 그리고 알림 두 건을 **수동 처리**(수동: 프로그램 없이 사람이 직접 하는 처리입니다. 여기서는 VS Code 로 `system_state.json` 을 열어 값을 직접 타이핑해 넣고 저장하는 처리)해 보면서 얼마나 번거로운지 겪습니다.
- **6교시**: 같은 일을 프로그램(`playbook_runner.py`)이 하게 만듭니다. <mark>한 번 실행하면 알림 5건이 처리되고, 사람의 승인이 필요한 건은 멈추고, 무엇을 했는지 기록이 남습니다.</mark>

오늘은 오후 5 · 6교시이고, <mark>깃허브에 올리는 일은 6교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **파이썬 · VS Code · 터미널 · git** 입니다. 판다스와 Gemini API 는 쓰지 않으므로 호출 한도(1분에 15번)는 신경 쓰지 않아도 됩니다.
- 오늘 새로 배우는 문법은 없습니다. 이번 주에 쓴 문법(딕셔너리 · 리스트 · `in` · `not in` · `if` · `for` · `append` · `json`)을 다시 씁니다.
- 새로 나오는 용어가 많은 날입니다. <mark>처음 나올 때 한 번씩 풀어 쓰고, 문제를 풀 때는 5.2 와 6.1 의 표를 보면서 풉니다.</mark>
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 출력이나 샘플 데이터의 값을 근거로 이유까지 서술합니다</mark>.

📎 **오늘 불러 쓰는 이전 파일**: 없습니다. 오늘 쓰는 데이터(`incident_samples.json`)는 오전 4과목의 점수 파일과 같은 내용을 오늘 실습용 예시 데이터로 아래 시작하기에 적어 두었고, 그것을 붙여 넣어 만듭니다. 그래서 오전 파일이 없어도 그대로 따라 할 수 있습니다. 6교시는 5교시에서 만드는 `config/playbook_registry.json` 을 읽습니다(없으면 `complete_files.md` 의 1절이나 문제 5-1 의 「정답 5-1」 완성본으로 만듭니다).

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 지금 위치를 확인합니다. <mark>`pwd` 결과가 `…/security-agent-toolkit` 으로 끝나고, `ls` 결과에 `anomaly_detection` 폴더가 보이면</mark> 됩니다. 결과가 다르면 `security-agent-toolkit` 폴더에서 터미널을 새로 엽니다.
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
3. **[터미널]** 5과목 폴더를 만들고 그 안으로 들어갑니다. 5과목의 모든 파일은 <mark>`soar_response` 폴더 안</mark>에 둡니다. 폴더 이름은 강의계획서가 정한 이름 그대로입니다.
   ```bash
   mkdir soar_response
   cd soar_response
   mkdir config
   ls
   ```
   - 명령 풀이: `mkdir 폴더이름` 새 폴더 만들기 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 이름 보기
   - <mark>`config` 폴더가 보이면</mark> 됩니다. `config` 에는 JSON 설정 파일만 둡니다.
4. **오늘 받은 파일 두 개**(`day01_pm_playbook_incident.md`, `day01_pm_report.md`)를 <mark>`다운로드` 폴더에서 `soar_response` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 그리고 **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-09(월))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[터미널]** 오늘 쓸 파일 두 개를 만들고 **[VS Code]** 에서 열어 아래 내용을 그대로 붙여 넣습니다.
   ```bash
   touch incident_samples.json system_state.json
   ls
   ```
   - 명령 풀이: `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 이름 보기

**`incident_samples.json`** — 오늘 처리할 알림 5건의 목록입니다.

- **무엇인가**:
  - 오전 4과목에서 저장한 대상별 점수 기록 5건에 인시던트 번호(`id`)와 처음 상태(`status`)를 붙인 것입니다.
  - **인시던트**(incident, 인시던트): 알림 가운데 사람이 확인하고 대응해야 하는 일 한 건입니다. 예를 들어 「퇴사한 `dami` 의 계정으로 서버에 요청이 왔다」는 알림에 `INC-001` 이라는 번호를 붙이면 인시던트 한 건이 되고, 대응이 끝날 때까지 이 번호로 추적합니다.
  - `entity` 는 점수를 매긴 대상(사용자 또는 IP), `grade` 는 등급, `reasons` 는 탐지된 규칙 이름입니다. <mark>처음 상태는 모두 `탐지됨` 입니다.</mark>
- **어디에 쓰나**:
  - 5교시: 어떤 알림을 처리할지 볼 때 읽습니다.
  - 6교시: 실행기(`playbook_runner.py`)가 이 파일을 읽어 알림을 하나씩 처리합니다.

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

**`system_state.json`** — 모의 시스템의 상태를 적는 파일입니다.

- **무엇인가**:
  - 대응을 하면 바뀌는 것 네 가지를 적습니다. 잠긴 계정(`locked_users`) · 차단한 IP(`blocked_ips`) · 티켓(`tickets`) · 담당자 알림(`notifications`)입니다.
  - 처음에는 모두 비어 있습니다.
- **어디에 쓰나**:
  - 5교시: 알림 두 건을 수동 처리하면서 VS Code 로 이 파일을 열어 값을 직접 입력하고 저장합니다.
  - 6교시: 실행기가 대응 결과를 이 파일에 새로 저장합니다. 실행하면 직접 입력한 내용은 덮어씁니다.

```
{
  "locked_users": [],
  "blocked_ips": [],
  "tickets": [],
  "notifications": []
}
```

6. **[터미널]** 파일이 정상인지 확인합니다. <mark>`5` 가 나와야</mark> 합니다. 다르면 붙여 넣은 내용이나 파일 위치(`soar_response` 폴더 안인지)를 다시 확인합니다(맥북은 `python3`).
   ```bash
   python -c "import json; print(len(json.load(open('incident_samples.json', encoding='utf-8'))))"
   ```

### 🆘 오류가 나면

- 먼저 `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `FileNotFoundError` 가 나오면 <mark>파일이 `soar_response` 폴더 바로 아래(또는 `config` 폴더 안)에 있는지</mark> `ls` 로 봅니다. `config/playbook_registry.json` 은 `config` 폴더 안에 있어야 합니다.
- `json.decoder.JSONDecodeError` 가 나오면 <mark>JSON 파일의 쉼표나 대괄호 · 중괄호가 빠졌거나 남은 것</mark>입니다. 오류에 적힌 줄 번호의 앞뒤 줄을 봅니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · SOAR 와 플레이북 4요소 이해하고, 알림 두 건을 수동 처리해 보기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「오전에 만든 점수 파일에는 알림이 5건 있습니다. 예를 들어 퇴사한 `dami` 의 계정으로 서버에 요청이 온 알림은 high 등급이고, IP `198.51.100.90` 의 경로 스캔(서버의 여러 주소에 차례로 요청을 보내 약점을 찾는 일) 알림은 low 등급입니다. 지금은 제가 알림을 하나씩 열어서 계정을 잠그고(그 계정으로 로그인하지 못하게 막고) 티켓을 만드는데, 사람마다 순서가 달라서 어떤 날은 티켓을 만들지 않고 넘어갑니다.
>
> 알림 종류마다 「이런 알림이 오면 이렇게 대응한다」를 문서로 먼저 정해 주세요. 그리고 지금처럼 파일을 직접 열어 고치는 방식이 얼마나 번거롭고 틀리기 쉬운지, 알림 두 건으로 직접 해 보고, 몇 군데를 고쳤는지와 어느 알림에서 실행을 멈춰야 했는지를 알려 주세요.」
> - **왜 중요한가**: <mark>같은 알림도 사람마다 다르게 처리하면 날마다 결과가 달라지고, 알림이 늘어날수록 빠뜨리는 일이 생깁니다.</mark> 절차를 먼저 정해 두어야 프로그램이 대신 실행할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

1. **SOAR**(Security Orchestration, Automation and Response, 쏘아: 여러 보안 도구를 서로 연결해, 정해 둔 대응 절차대로 자동으로 실행하는 것)는 알림이 난 뒤에 사람이 하던 일을 맡습니다.
2. 오늘 질문은 하나입니다. <mark>**알림이 오면 무엇을 어떤 순서로 하고, 어떤 일은 사람의 허락을 받아야 하는가?**</mark> 이 답을 적은 문서가 플레이북입니다.

### 📖 먼저 보기 — 4과목과 5과목은 무엇이 다른가

- **한 줄**: 5과목은 보안관제(SOC, Security Operations Center, 에스오씨: 보안 사고를 지켜보고 대응하는 센터의 업무)에서 <mark>탐지 이후 단계인 분류 · 조치 · 보고를 자동화</mark>하는 과목입니다.

```
로그 ─(4과목: 탐지 · 점수)─▶ 알림 · 점수 · 등급 ─(5과목: 분류 · 승인 · 조치 · 보고)─▶ 시스템 상태 변화 + 감사 기록
```

| 관점 | 4과목 이상탐지 | 5과목 자동 대응 |
|---|---|---|
| 입력 → 출력 | 로그 → 알림 · 점수 · 등급 | 알림 → 상태 변화 · 티켓 · 차단 · 감사 기록 |
| 틀렸을 때 생기는 문제 | 오탐(정상인데 위협으로 잘못 찾은 것)은 분석 시간을 낭비하고, 미탐(진짜 위협을 못 찾은 것)은 위협을 놓친다 | **조치 오류는 정상 계정 · IP 를 막아 서비스를 중단시킨다** |
| 사람의 역할 | 알림을 읽고 판단한다 | 승인하고, 자동 처리 밖의 건을 맡는다 |

- **같은 사건으로 보면** `dami` (퇴사한 사람의 계정으로 서버에 요청이 온 일)는 이렇게 이어집니다.
  - 4과목: `퇴사한 계정` 규칙에 해당해 60점 · `high` 알림이 만들어집니다.
  - 5과목: 그 알림이 인시던트가 되고, 플레이북 PB-001 이 계정 잠금과 티켓 생성을 실행합니다. 액션을 실행할 때마다 감사 기록(6교시에서 설명)이 한 줄 남아, 모두 두 줄이 됩니다.

### 📖 5.1 대응 흐름 네 단계와 실제 제품

대응은 네 단계로 나눠 생각합니다. 5과목 전체가 이 흐름을 따라갑니다.

| 단계 | 하는 일 | 이 과목에서 |
|---|---|---|
| 탐지 | 이상한 일을 찾아 알림을 낸다 | 4과목에서 만든 점수 파일 (오늘의 입력) |
| 분류 | 알림이 진짜인지, 얼마나 급한지 정하고 상태를 기록한다 | 오늘 6교시 (`분류됨` 상태) |
| 조치 | 계정 잠금 · IP 차단 같은 대응을 실행한다 | 오늘은 모의 시스템에서 하고, 실제 서버에서 하는 조치는 강의계획서의 2일 차에 한다 |
| 보고 | 무엇을 했는지 기록하고, 필요하면 담당자에게 알린다 (오늘 PB-001 은 감사 기록만 남기고 담당자 알림은 보내지 않는다) | 오늘 6교시에서 감사 기록을 남기고, 3 · 4일 차에 티켓 · 알림 · 리포트를 만든다 |

보안관제 현장에서 쓰는 SOAR 제품에도 플레이북이 있습니다. 

| 제품 | 플레이북은 | 자세한 설명 |
|---|---|---|
| Splunk SOAR(스플렁크 쏘아) | 보안 업무를 자동으로 처리하는 파이썬 프로그램이다. 코드를 쓰지 않고 화면에서 단계를 이어 붙이는 편집기로도 만들 수 있다. 새 데이터가 들어오면 켜져 있는 플레이북이 실행된다 | https://docs.splunk.com/Documentation/SOARonprem/latest/Playbook/CreatePlaybooks |
| Cortex XSOAR(코텍스 엑스쏘아) | 보안 처리 과정을 자동으로 실행하는 기능이다. 작업 중에는 분석가가 정보를 확인하거나 상급자에게 넘기는 수동 작업이 있다. 또 조건에 따라 다음 작업이 정해지는 조건 작업이 있다 | https://cortex-docs.paloaltonetworks.com/r/Cortex-XSOAR/8/Cortex-XSOAR-Cloud-Documentation/What-is-a-playbook |
| Microsoft Sentinel(마이크로소프트 센티널) | 마이크로소프트의 자동화 서비스인 Azure Logic Apps 로 만든 처리 순서이다. 알림이나 인시던트가 자동화 규칙을 작동시키면 자동으로 실행되고, 사람이 직접 실행할 수도 있다 | https://learn.microsoft.com/en-us/azure/sentinel/automate-responses-with-playbooks |

- 세 제품 모두 <mark>알림이 오면 실행되는 대응 절차</mark>를 플레이북이라고 부릅니다. 오늘 만드는 플레이북은 이 제품들의 플레이북을 아주 단순하게 줄인 모양입니다.
- Cortex XSOAR 에 **사람이 확인하는 작업**이 따로 있는 것에서 보듯이, 모든 대응을 자동으로 하지는 않습니다. 오늘 4요소 가운데 「승인」이 사람이 확인하는 부분에 해당합니다.

### 📖 5.2 플레이북 4요소와 실제로 쓰는 값

플레이북은 네 가지를 정하면 완성됩니다. 질문 네 개에 답하는 것과 같습니다.

| 요소 | 쉬운 질문 | 오늘 JSON 파일의 키 |
|---|---|---|
| **트리거**(trigger, 트리거: 대응을 시작하게 하는 일) | 어떤 규칙이 탐지되면 시작하나? | `trigger_rule` |
| **조건**(condition, 컨디션: 트리거에 맞는 것 중 대응할 것만 고르는 기준) | 그중 어떤 것만 하나? | `min_grade` (이 등급 이상) |
| **액션**(action, 액션: 실제로 하는 대응 한 가지) | 무엇을 하나? | `actions` (리스트) |
| **승인**(approval, 어프루벌: 실행하기 전에 사람의 허락을 받는 것) | 사람의 허락이 필요한가? | `approval` |

예시 하나를 문장으로 읽습니다. 플레이북 PB-001 은 <mark>「규칙 `퇴사한 계정`이 탐지되고(트리거), 등급이 high 이상이면(조건), 계정을 잠그고 티켓을 만든다(액션). 사람의 허락 없이 자동으로 한다(승인)」</mark>입니다.

액션으로 쓸 수 있는 대응은 다음과 같습니다. 오늘은 모의 시스템에서 실행합니다. <mark>「대상」 열을 보고 알림의 대상에 맞는 액션을 고릅니다.</mark>

| 액션 | 하는 일 | 대상 | 모의 시스템에서 일어나는 일 |
|---|---|---|---|
| 계정 잠금 | 사용자 계정으로 로그인하거나 요청하지 못하게 한다 | 사용자 | `locked_users` 에 이름이 들어간다 |
| IP 차단 | 그 IP 에서 오는 접속을 막는다 | IP | `blocked_ips` 에 IP 가 들어간다 |
| 담당자 알림 | 담당자에게 알림을 보낸다 | 사용자 · IP 모두 | `notifications` 에 알림이 들어간다 |
| 티켓 생성 | 티켓을 만들어 담당자와 진행 상황을 추적한다 | 사용자 · IP 모두 | `tickets` 에 티켓이 들어간다 |

승인은 두 값 중 하나로 씁니다.

| 값 | 뜻 | 이런 때 씁니다 |
|---|---|---|
| `자동` | 사람의 허락 없이 실행한다 | 잘못 실행해도 영향이 작고 쉽게 되돌릴 수 있을 때 |
| `담당자 승인 필요` | 담당자가 허락해야 실행한다 | 잘못 실행하면 정상 사용자의 업무가 막힐 수 있을 때 |

- 같은 액션이라도 <mark>누구에게 실행하는지에 따라 승인 값이 달라집니다.</mark> 퇴사한 사람의 계정을 잠그면 막히는 업무가 없지만, 정상 사용자가 쓰는 IP 를 차단하면 그 사람의 업무도 막힙니다.

플레이북은 `config/playbook_registry.json` 한 파일에 모아 적습니다. 한 건의 키는 다음과 같습니다.

| 키 | 뜻 | PB-001 의 값 |
|---|---|---|
| `id` | 플레이북 번호 | `"PB-001"` |
| `name` | 플레이북 이름 | `"퇴사한 계정의 서버 요청"` |
| `trigger_rule` | 트리거: 탐지된 규칙 이름 | `"퇴사한 계정"` |
| `min_grade` | 조건: 이 등급 이상(`low` · `mid` · `high`) | `"high"` |
| `actions` | 액션: 대응 이름의 리스트 | `["계정 잠금", "티켓 생성"]` |
| `approval` | 승인 | `"자동"` |
| `reason` | 이유: 왜 이렇게 정했는지 한두 문장 | `"퇴사한 사람의 계정으로 서버에 요청이 오면 …"` |

### 📖 5.3 플레이북은 이 과목에서 어떻게 쓰이나

- **플레이북은 5과목 내내 계속 쓰는 파일입니다.**
  - 5과목에서는 플레이북에 적힌 액션을 하나씩 실제로 동작하게 만듭니다.
  - 아래는 강의계획서 기준입니다. 날짜는 예정이고, 바뀔 수 있습니다.

| 일차(예정) | 만드는 것 | 플레이북과의 관계 |
|---|---|---|
| 1일 차 (11/9 오후 ~ 11/10) | 플레이북 등록 파일 · 인시던트 상태 · 실행기 | 플레이북을 쓰고, 읽고, 실행하는 파일과 프로그램 (오늘은 그중 첫 부분) |
| 2일 차 (11/11) | 계정 잠금 · 접근 차단 (`containment.py`) | `actions` 의 `계정 잠금` · `IP 차단` 을 모의가 아닌 실제 동작으로 바꾼다. VIP 계정(특별히 관리하는 중요 계정)은 따로 예외 처리한다 |
| 3일 차 (11/12) | 티켓 생성 · 알림 · 윗사람에게 넘기기(에스컬레이션) (`ticketing.py` · `escalation.py`) | `티켓 생성` · `담당자 알림` 을 실제 동작으로 바꾼다. 정해진 시간 안에 처리되지 않으면 윗사람에게 넘긴다 |
| 4일 차 (11/13) | 처음 대응을 정리한 리포트 · 승인 판단 (`report.py` · `approval_gate.py`) | `approval` 을 위험도에 따라 코드가 판단하게 하고, 플레이북 실행 결과로 리포트를 쓴다 |
| 5일 차 (11/16 오전) | 전체 통합 (`soar_engine.py`) | 4과목 탐지 결과부터 플레이북 실행까지 한 번에 이어서 실행한다 |

- **JSON 한 건이 플레이북의 전부일까요? 아닙니다.**
  - 플레이북은 「알림이 오면 이렇게 대응한다」는 **절차**이고, JSON 한 건은 그 절차를 프로그램이 읽을 수 있게 적은 **저장 형태**입니다.
  - 절차는 알림이 올 때마다 아래 흐름으로 반복해서 실행됩니다. 모든 단계가 플레이북 파일의 값을 읽습니다.

```
알림 도착 → 인시던트 생성(탐지됨) → 맞는 플레이북 찾기 → 승인 확인 → 액션을 순서대로 실행 → 감사 기록 → 상태 변경(조치됨)
```

- **프로그램은 플레이북의 어느 키를 언제 읽나요?**

| 키 | 읽는 때 | 하는 일 |
|---|---|---|
| `trigger_rule` · `min_grade` | 맞는 플레이북을 찾을 때 | 인시던트에서 탐지된 규칙이 `trigger_rule` 과 같은지, 등급이 `min_grade` 이상인지 비교한다 |
| `approval` | 실행하기 직전 | `자동` 이 아니면 멈추고 승인 대기로 기록한다 |
| `actions` | 실행할 때 | 적힌 순서대로 액션을 하나씩 실행한다 |
| `id` | 기록을 남길 때 | 어느 플레이북이 한 일인지 감사 기록에 적는다 |
| `name` · `reason` | 프로그램은 읽지 않는다 | 사람이 검토하거나 감사할 때 읽는다 |

- **현업에서도 같은 방식으로 씁니다.**
  - 플레이북은 한 번 만들고 끝나지 않습니다. 운영하면서 오탐이 반복되면 조건을 고치고, 안전하다고 확인된 액션은 승인을 `자동` 으로 바꿉니다.
  - 그래서 플레이북을 코드 안에 쓰지 않고 별도 파일에 적어 두는 것이 중요합니다. 코드를 바꾸지 않고 플레이북만 고쳐 대응을 바꿀 수 있기 때문입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 경로 스캔 플레이북을 쓰고, 알림 두 건을 수동 처리하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>오전 점수 파일에는 퇴사한 계정(dami)과 경로 스캔(IP `198.51.100.90`)이 있지만, 그 알림이 오면 무엇을 할지 정해 둔 문서가 없습니다. 처리는 모두 사람이 파일을 직접 열어 고쳐서 합니다</mark>.
- **그래서 하는 것**: 플레이북 PB-003 을 직접 쓰고, 알림 두 건(INC-001 · INC-005)을 VS Code 에서 `system_state.json` 을 열어 수동 처리합니다. 승인이 필요한 건은 담당자가 허락했다고 가정합니다.
- **끝나면**: <mark>등록 파일을 읽으면 `PB-001` · `PB-002` · `PB-003` 이 나오고, `system_state.json` 에 잠긴 계정 · 차단한 IP · 티켓이 들어 있습니다.</mark>

**🎯 할 일**

1. 등록 파일을 만들고 예시 두 건을 붙여 넣은 뒤, PB-003 한 건을 추가합니다.
2. 확인 명령으로 등록 파일을 확인합니다.
3. `system_state.json` 을 열어 INC-001 과 INC-005 를 수동 처리하고 확인 명령을 칩니다.

**`config/playbook_registry.json`** — 플레이북 목록 파일입니다.

- **무엇인가**:
  - 플레이북 4요소(트리거 · 조건 · 액션 · 승인)와 이유를 한 건씩 모아 적은 파일입니다.
  - 사람이 읽는 대응 절차서이면서, 프로그램이 읽는 설정 파일입니다.
- **어디에 쓰나**:
  - 6교시: 프로그램이 이 파일을 읽어 알림에 맞는 플레이북을 찾고, 적힌 `actions` 와 `approval` 대로 실행합니다.
- **지금은**: 앞 두 건을 먼저 붙여 넣습니다.

```
[
  {
    "id": "PB-001",
    "name": "퇴사한 계정의 서버 요청",
    "trigger_rule": "퇴사한 계정",
    "min_grade": "high",
    "actions": [
      "계정 잠금",
      "티켓 생성"
    ],
    "approval": "자동",
    "reason": "퇴사한 사람의 계정으로 서버에 요청이 오면 그 계정이 아직 사용할 수 있는 상태라는 뜻입니다. 퇴사한 사람이 쓰는 계정이 없으므로 잠가도 막히는 업무가 없습니다."
  },
  {
    "id": "PB-002",
    "name": "대량 다운로드",
    "trigger_rule": "대량 다운로드",
    "min_grade": "mid",
    "actions": [
      "담당자 알림",
      "티켓 생성"
    ],
    "approval": "담당자 승인 필요",
    "reason": "파일을 많이 내려받은 것은 업무 때문일 수도 있습니다. 사람이 확인하기 전에는 정상인지 알 수 없으므로 담당자가 허락한 뒤에 실행합니다."
  }
]
```

PB-003 은 위 파일의 맨 아래 `]` 앞에 한 건을 더합니다. <mark>PB-002 의 닫는 중괄호 `}` 뒤에 쉼표를 붙이고, 새 건 뒤에는 쉼표를 붙이지 않습니다.</mark> `actions` · `approval` · `reason` 은 내가 정해 씁니다.

```
  {
    "id": "PB-003",
    "name": "경로 스캔",
    "trigger_rule": "경로 스캔",
    "min_grade": "low",
    "actions": [ 내가 정한 액션 이름들 ],
    "approval": "내가 정한 승인 값",
    "reason": "내가 정한 이유 한두 문장"
  }
```

**수동 처리하는 방법** — 프로그램을 쓰지 않습니다. VS Code 에서 `system_state.json` 을 열어 아래 표대로 값을 직접 타이핑해 넣고 저장합니다.

```
고치기 전:  "locked_users": [],
고친 뒤:    "locked_users": ["dami"],
```

- 위는 INC-001 을 처리할 때 `locked_users` 줄을 고치는 예입니다. 잠긴 계정 리스트에 `"dami"` 를 적어 넣는 것이 「계정을 잠갔다」는 뜻입니다(모의 시스템이므로 실제 계정은 바뀌지 않습니다).
- 두 건을 처리해야 하는 곳은 다음과 같습니다.

| 인시던트 | 맞는 플레이북 | 고칠 곳 |
|---|---|---|
| INC-001 (dami) | PB-001 (자동) | `locked_users` 에 `"dami"` 를 넣고, `tickets` 에 `{"id": "TCK-1", "incident": "INC-001", "target": "dami"}` 를 넣는다 |
| INC-005 (198.51.100.90) | PB-003 (내가 쓴 것) | 내가 정한 액션대로 고친다. 티켓 번호는 `TCK-2` 로 한다 |

- 리스트에 넣을 때는 `["dami"]` 처럼 대괄호 안에 쓰고, 두 개 이상이면 쉼표로 나눕니다.
- 고친 곳이 모두 몇 군데인지 <mark>세어 둡니다.</mark> 보고서 (나)에서 씁니다.

**순서**

1. **[터미널]** 등록 파일을 만듭니다. <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 먼저 봅니다.
   ```bash
   pwd
   touch config/playbook_registry.json
   ls config
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름` 빈 파일 만들기 · `ls 폴더이름` 폴더 안의 파일 이름 보기
2. **[VS Code]** `config/playbook_registry.json` 에 앞 두 건을 붙여 넣고, PB-003 한 건을 추가합니다. 쉼표 위치를 확인합니다.
3. **[터미널]** 등록 파일을 확인합니다(맥북은 `python3`). <mark>`['PB-001', 'PB-002', 'PB-003']` 이 나오면</mark> 됩니다. 오류가 나면 위 「🆘」 의 JSON 안내를 따릅니다.
   ```bash
   python -c "import json; print([p['id'] for p in json.load(open('config/playbook_registry.json', encoding='utf-8'))])"
   ```
   - 명령 풀이: JSON 파일을 읽어 플레이북 번호만 모아 출력합니다. 쉼표나 괄호가 틀리면 여기서 오류가 납니다.
4. **[VS Code]** `system_state.json` 을 열어 위 표대로 INC-001 과 INC-005 를 처리합니다. 저장합니다.
5. **[터미널]** 수동 처리한 결과를 확인합니다. 아래 명령은 잠긴 계정 · 차단한 IP · 티켓 수를 한 줄로 보여 줍니다.
   ```bash
   python -c "import json; s = json.load(open('system_state.json', encoding='utf-8')); print(s['locked_users'], s['blocked_ips'], len(s['tickets']))"
   ```
   - 명령 풀이: 상태 파일을 읽어 잠긴 계정 리스트, 차단한 IP 리스트, 티켓 개수를 출력합니다.
   - 나오는 것: 내가 정한 액션에 따라 다릅니다. 예를 들어 IP 차단과 티켓 생성을 골랐다면 <mark>`['dami'] ['198.51.100.90'] 2`</mark> 가 나옵니다.
6. **[보고서]** `day01_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 내가 쓴 PB-003 의 액션과 승인을 적고, 5번 확인 명령의 출력을 붙여 넣어 주세요.
   - (나) 🔍 알림 두 건을 수동 처리하면서 `system_state.json` 을 직접 고친 곳이 모두 몇 군데였는지 적고, 알림이 100건이면 어떤 문제가 생길지 적어 주세요.
   - (다) 🔍 PB-003 의 승인 값을 그렇게 정한 이유를 적어 주세요. 대상이 사용자 계정이 아니라 IP 라는 점과 잘못 차단했을 때의 영향을 근거로 쓰세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 플레이북 4요소 | 트리거(언제) · 조건(어떤 것만) · 액션(무엇을) · 승인(허락이 필요한가) |
| 등록 파일의 키 | `id` · `name` · `trigger_rule` · `min_grade` · `actions` · `approval` · `reason` |
| 승인 값 | `자동` · `담당자 승인 필요` |
| 액션을 고르는 기준 | 알림의 대상이 사용자이면 계정 잠금, IP 이면 IP 차단, 사용자와 IP 모두에는 티켓 생성 · 담당자 알림 |
| JSON 쉼표 | 플레이북과 플레이북 사이에는 있고, 마지막 플레이북 뒤에는 없다 |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 플레이북으로 알림 5건을 한 번에 처리하고 감사 기록 남기기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「5교시처럼 파일을 직접 열어 고치면 알림 두 건만 처리해도 여러 곳을 고쳐야 하고, 하나라도 빠뜨리면 아무도 모릅니다. 알림 5건을 한 번 실행으로 처리해 주세요.
>
> 단, 담당자가 허락하기 전에 실행하면 안 되는 대응이 있습니다. 예를 들어 IP `198.51.100.90` 을 차단하면 그 IP 를 함께 쓰는 정상 사용자도 접속하지 못할 수 있습니다. 허락이 필요한 알림은 실행하지 않고 멈춰 주세요. 그리고 나중에 「누가 무엇을 언제 했는지」 물으면 답할 수 있게, 한 일과 하지 않은 일을 모두 기록해 주세요.」
> - **왜 중요한가**: <mark>자동으로 실행하는 만큼 잘못 실행했을 때의 피해도 큽니다. 그래서 허락이 필요한 건은 멈추게 하고, 한 일은 모두 기록으로 남겨야 합니다.</mark> 기록이 없으면 「안 한 일」도 증명할 수 없습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 6.1 오늘 쓰는 파일과 모의 시스템

오늘 쓰는 파일은 다음과 같습니다. <mark>`incident.py` 는 완성본을 그대로 붙여 넣고, `playbook_runner.py` 의 핵심 6곳만 직접 씁니다.</mark>

| 파일 | 하는 일 | 누가 불러 쓰나 | 오늘 |
|---|---|---|---|
| `incident.py` | 인시던트 상태 바꾸기 · 맞는 플레이북 찾기 · 액션 하나 실행하기 · 감사 기록 한 건 만들기 (도구 모음) | `playbook_runner.py` 와 실행 파일 | 완성본을 붙여 넣는다 |
| `playbook_runner.py` | 플레이북 하나를 실행한다(승인 확인 → 액션 차례로 실행 → 기록). 인시던트를 하나씩 처리하고 결과를 출력한다 | 실행 파일 | **핵심 6곳을 직접 쓴다** |
| `day01_6-1_run.py` | 파일을 읽고, 실행하고, 상태 · 승인 대기 · 기록을 출력하고 저장한다 (시작 파일) | 내가 터미널에서 직접 실행한다 | 그대로 붙여 넣는다 |
| `action_log.json` | 실행하면 생기는 감사 기록 파일 | 사고 뒤에 사람이 읽는다 | 실행하면 자동으로 생긴다 |

- **모의 시스템**은 `state` 딕셔너리입니다. 키 네 개(`locked_users` · `blocked_ips` · `tickets` · `notifications`)가 5교시의 `system_state.json` 과 같습니다. 액션을 실행하면 이 딕셔너리에 값이 들어갑니다.
- `incident.py` 의 `run_action` 은 대상과 맞지 않는 액션(IP 에 계정 잠금, 사용자에게 IP 차단)을 <mark>실행하지 않고, 「건너뜀」과 그 이유를 결과로 리턴합니다.</mark> 잘못 고른 액션이 모의 시스템에 반영되지 않게 막는 확인입니다.

**상태와 상태 전이** — 인시던트는 대응이 끝날 때까지 여러 단계를 거칩니다. 지금 단계를 **상태**(status, 스테이터스)라고 하고, 한 상태에서 다른 상태로 옮기는 것을 **상태 전이**(state transition, 스테이트 트랜지션: 상태가 바뀌는 일)라고 합니다.

```
탐지됨  →  분류됨  →  조치됨  →  보고됨  →  종료
            └──────────────────────────────→  종료  (오탐으로 판단했을 때)
```

- 위 그림에 화살표가 없는 이동은 거절합니다. 예를 들어 `탐지됨` 에서 `조치됨` 으로 바로 가는 것은 거절합니다. 분류하지 않은 인시던트에 조치하는 것을 막기 위해서입니다.
- 오늘 `playbook_runner.py` 는 실행을 시작할 때 `분류됨` 으로, 모든 액션이 끝나면 `조치됨` 으로 옮깁니다. 승인 대기로 멈춘 건은 `분류됨` 에 남습니다.

**맞는 플레이북 찾기** — `incident.py` 의 `match_playbooks` 가 아래 두 가지가 <mark>모두 맞는</mark> 플레이북을 찾습니다.

| 확인 | 맞는 때 |
|---|---|
| 트리거 | 플레이북의 `trigger_rule` 이 인시던트의 `reasons` 리스트 안에 있다 |
| 조건 | 인시던트의 등급이 플레이북의 `min_grade` 이상이다 (`low` 1 · `mid` 2 · `high` 3 으로 바꿔 비교) |

- 이 부분은 완성본으로 제공합니다. 오늘 직접 쓰는 것은 「찾은 플레이북을 어떻게 실행하는가」입니다.
- 한 인시던트에 규칙이 여러 개이면 그중 하나만 트리거와 맞아도 됩니다. 예를 들어 INC-002 는 `평소와 다른 IP` 에 맞는 플레이북은 없지만 `대량 다운로드` 로 PB-002 와 맞습니다.

**감사 기록**(audit log, 오딧 로그: 누가 무엇을 언제 했는지 남기는 기록) — 액션을 실행할 때마다, 그리고 승인 대기로 멈출 때도 한 건씩 남깁니다.

| 키 | 뜻 | 예 |
|---|---|---|
| `time` | 기록한 시각 | `"14:52:07"` |
| `incident` | 인시던트 번호 | `"INC-001"` |
| `playbook` | 실행한 플레이북 번호 | `"PB-001"` |
| `action` | 한 액션 (승인 대기로 멈추면 `"전체"`) | `"계정 잠금"` |
| `result` | 결과 문장 | `"계정 dami 잠금 완료"` |

- 현업에서는 이 기록으로 「그 계정을 누가 언제 왜 잠갔는지」를 설명합니다. <mark>실행하지 않은 건(승인 대기)도 남겨야</mark> 「왜 아직 조치하지 않았는지」를 설명할 수 있습니다.

**`run_playbook` 이 하는 일의 순서**를 그림으로 읽습니다. 직접 쓰는 6곳이 이 순서입니다.

```
상태를 분류됨으로 옮긴다 (미리 채움)
   ↓
승인이 「자동」이 아닌가?  ── 예 → 「승인 대기」를 기록하고 멈춘다 (1 · 2 · 3번)
   ↓ 아니요
액션을 하나씩 실행하고(4번) 기록한다(5번)
   ↓
상태를 조치됨으로 옮긴다 (6번)
```

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `change_status` | 인시던트 · 바꿀 상태 | 바꿨으면 `True`, 거절했으면 `False` (제공) |
| `match_playbooks` | 인시던트 · 플레이북 리스트 | 맞는 플레이북 리스트 (제공) |
| `run_action` | 액션 · 인시던트 · 모의 시스템 | 결과 문장 (제공) |
| `make_log_entry` | 인시던트 · 플레이북 · 액션 · 결과 | 감사 기록 한 건 (제공) |
| `run_playbook` | 인시던트 · 플레이북 · 모의 시스템 · 기록 리스트 | 실행했으면 `True`, 승인 대기면 `False` (**직접 쓴다**) |
| `process_incidents` | 인시던트 리스트 · 플레이북 리스트 · 모의 시스템 · 기록 리스트 | 승인 대기 건의 리스트 (미리 채움) |

- **직접 쓰는 곳은 여섯 군데**(번호 1 ~ 6)이고, 함수 한 개(`run_playbook`) 안에 있습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 플레이북 실행기로 알림 5건 처리하고 감사 기록 읽기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 5건이 모두 `탐지됨` 상태이고, 5교시처럼 수동 처리하면 번거롭습니다. 또 승인이 필요한 건을 구별하기 어렵습니다</mark>.
- **그래서 만드는 것**: `playbook_runner.py` 의 `run_playbook` 입니다.
  - 승인이 필요한 플레이북은 실행하지 않고 승인 대기로 기록합니다.
  - 자동으로 해도 되는 플레이북은 액션을 차례로 실행하고 한 건씩 기록합니다.
- **실행하면**: <mark>단계 1: 불러온 인시던트와 플레이북 수, 단계 2: 실행 전 모의 시스템 상태, 단계 3: 인시던트마다 실행 결과, 단계 4: 실행 후 상태, 단계 5: 승인 대기 건, 단계 6: 감사 기록이 나옵니다.</mark>

**🎯 할 일**

1. `incident.py` · `playbook_runner.py` · `day01_6-1_run.py` 세 파일을 만듭니다. `incident.py` 와 실행 파일은 그대로 붙여 넣고, `playbook_runner.py` 의 `run_playbook` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>인시던트마다 실행 결과</mark>(단계 3), <mark>실행 전후 상태</mark>(단계 2 · 4), <mark>승인 대기</mark>(단계 5), <mark>감사 기록</mark>(단계 6)를 읽습니다.

**`incident.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

- **무엇인가**: 플레이북을 실행할 때 쓰는 **도구 모음**입니다. 상태 바꾸기, 맞는 플레이북 찾기, 액션 하나 실행하기, 기록 한 건 만들기 함수가 들어 있습니다.
- **어디에 쓰나**: `playbook_runner.py` 와 실행 파일이 이 파일의 함수를 불러다 씁니다. 오늘은 읽기만 하고 고치지 않습니다.

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

**`playbook_runner.py`**

- **무엇인가**: 플레이북 하나를 실행하는 **프로그램의 핵심**입니다. 승인을 확인하고, 액션을 차례로 실행하고, 기록을 남깁니다. 여기서 직접 6곳을 씁니다.
- **어디에 쓰나**: 실행 파일이 인시던트 5건을 이 파일의 함수에 넘겨 처리합니다.

```python
from incident import change_status, match_playbooks, run_action, make_log_entry  # 제공받은 함수를 불러온다


def run_playbook(incident, playbook, state, action_log):                         # 인시던트 · 플레이북 · 시스템 상태 · 감사 기록 리스트를 받는 함수
    """플레이북의 액션을 차례로 실행하고 감사 기록을 남긴다. 승인이 필요하면 실행하지 않고 승인 대기로 기록한다.
    실행했으면 True, 승인 대기로 멈췄으면 False 를 리턴한다.
    """
    change_status(incident, "분류됨")                                            # 대응을 시작하기 전에 분류됨 상태로 옮긴다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. playbook 의 "approval" 값이 "자동" 이 아니면 (if, !=)
    # 2.   make_log_entry(incident, playbook, "전체", "승인 대기") 의 결과를 action_log 에 추가한다 (append)
    # 3.   False 를 리턴한다 (실행하지 않았다)
    for action in playbook["actions"]:                                           # 액션을 하나씩 꺼낸다
        # 4. run_action(action, incident, state) 의 결과를 result 에 담는다
        # 5. make_log_entry(incident, playbook, action, result) 의 결과를 action_log 에 추가한다 (append)
    # 6. change_status(incident, "조치됨") 를 호출한다 (실행이 끝났으니 조치됨으로 옮긴다)
    return True                                                                  # 모두 실행했으니 True 를 리턴한다


def process_incidents(incidents, registry, state, action_log):                   # 인시던트 리스트 · 플레이북 리스트 · 시스템 상태 · 감사 기록을 받는 함수
    """인시던트마다 맞는 플레이북을 찾아 실행하고 결과를 한 줄씩 출력한다.
    승인 대기로 멈춘 건의 리스트를 리턴한다.
    """
    pending = []                                                                 # 승인 대기로 멈춘 건을 담을 빈 리스트
    for incident in incidents:                                                   # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                          # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                       # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                               # 맞는 플레이북을 하나씩 꺼낸다
            done = run_playbook(incident, playbook, state, action_log)           # 플레이북을 실행한다
            if done:                                                             # 실행했으면
                result_text = playbook["id"] + " 실행 완료"                      # 실행 완료라고 적는다
            else:                                                                # 승인 대기로 멈췄으면
                result_text = playbook["id"] + " 승인 대기"                      # 승인 대기라고 적는다
                waiting = {"incident": incident["id"], "entity": incident["entity"], "playbook": playbook["id"], "approval": playbook["approval"]}  # 대기 건 한 건
                pending.append(waiting)                                          # 승인 대기 리스트에 추가한다
        status_text = "(상태: " + incident["status"] + ")"                       # 지금 상태를 괄호 글자로 만든다
        print(incident["id"], incident["entity"], incident["grade"], "->", result_text, status_text)  # 번호 · 대상 · 등급 · 결과 · 상태를 출력한다
    return pending                                                               # 승인 대기 리스트를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 · 6번은 함수 안이라 앞에 공백 4개입니다. 2 · 3번은 `if` 안이라 공백 8개입니다. 4 · 5번은 `for` 안이라 공백 8개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 3번의 `return False` 는 「더 실행하지 않고 여기서 끝낸다」는 뜻입니다. 2번에서 기록을 남긴 뒤 바로 끝내야 `for` 문의 액션이 실행되지 않습니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 으로 시작하는 오류가 납니다(문구는 파이썬 버전마다 조금 다릅니다). `for` 안쪽의 4 · 5번이 비어 있기 때문입니다.

**`day01_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(리스트)` 는 리스트의 개수입니다.

- **무엇인가**: 알림 5건 처리를 한 번에 실행하는 **시작 파일**입니다. 파일을 읽고, 실행기에 넘겨 처리하고, 결과를 출력하고 저장합니다.
- **어디에 쓰나**: 터미널에서 `python day01_6-1_run.py` 로 실행합니다. 실행하면 `system_state.json` 과 `action_log.json` 이 새로 저장됩니다.

```python
from incident import load_json, save_json, INCIDENTS_PATH, REGISTRY_PATH, STATE_PATH, LOG_PATH  # 제공받은 함수를 불러온다
from playbook_runner import process_incidents                                           # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                                                   # 인시던트 파일을 리스트로 읽는다
registry = load_json(REGISTRY_PATH)                                                     # 플레이북 등록 파일을 리스트로 읽는다
incident_count = len(incidents)                                                         # 인시던트가 몇 건인지 센다
playbook_count = len(registry)                                                          # 등록된 플레이북이 몇 개인지 센다
print("--- 단계 1: 불러온 인시던트", incident_count, "건 · 등록된 플레이북", playbook_count, "개")  # 단계 1 시작을 알리는 줄

state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}     # 모의 시스템의 처음 상태 : 아무것도 없다
action_log = []                                                                         # 감사 기록을 담을 빈 리스트
print("--- 단계 2: 실행 전 모의 시스템 상태")                                           # 단계 2 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                               # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 3: 인시던트마다 플레이북 실행")                                         # 단계 3 시작을 알리는 줄
pending = process_incidents(incidents, registry, state, action_log)                     # 플레이북을 실행한다

print("--- 단계 4: 실행 후 모의 시스템 상태")                                           # 단계 4 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                               # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

pending_count = len(pending)                                                            # 승인 대기가 몇 건인지 센다
print("--- 단계 5: 승인 대기", pending_count, "건")                                     # 단계 5 시작을 알리는 줄과 건수
for waiting in pending:                                                                 # 승인 대기 건을 하나씩 꺼낸다
    print(waiting["incident"], waiting["entity"], waiting["playbook"], "·", waiting["approval"])  # 번호 · 대상 · 플레이북 · 승인 값을 출력한다

save_json(state, STATE_PATH)                                                            # 모의 시스템 상태를 파일에 저장한다
save_json(action_log, LOG_PATH)                                                         # 감사 기록을 파일에 저장한다
log_count = len(action_log)                                                             # 감사 기록이 몇 건인지 센다
print("--- 단계 6: 감사 기록", log_count, "건을", LOG_PATH, "에 저장")                  # 단계 6 시작을 알리는 줄과 건수
for entry in action_log:                                                                # 감사 기록을 하나씩 꺼낸다
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])  # 번호 · 플레이북 · 액션 · 결과를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 세 개를 `soar_response` 폴더에 만들어 위 코드를 붙여 넣습니다. 터미널에서는 `touch` 로 만든 뒤 VS Code 에서 엽니다. <mark>`config/playbook_registry.json` 에 PB-001 ~ PB-003 이 있어야</mark> 합니다.
   ```bash
   pwd
   touch incident.py playbook_runner.py day01_6-1_run.py
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
2. **[VS Code]** `playbook_runner.py` 에서 <mark>직접 쓰는 곳 여섯 군데를 씁니다</mark>. 위 6.1 의 그림과 표를 참고해 씁니다. 막히면 아래 「6교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day01_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day01_6-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **여섯 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 줄 수는 단계마다 다릅니다. 단계 1은 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다. 단계 2와 4는 각각 3줄입니다. 단계 3은 인시던트마다 1줄이라 5줄입니다. 단계 5는 승인 대기 건수만큼, 단계 6은 감사 기록 건수만큼 줄이 나옵니다. <mark>승인 대기와 기록 수는 5교시에서 내가 정한 PB-003 의 승인 값에 따라 달라집니다.</mark>
5. **[VS Code]** 새로 생긴 `action_log.json` 과 `system_state.json` 을 열어 봅니다.
   - `action_log.json`: 감사 기록입니다. 누가 무엇을 언제 했는지 남은 파일이고, 사고가 난 뒤 대응이 적절했는지 다시 확인할 때 읽습니다. 시각(`time`)이 있는지 확인합니다.
   - `system_state.json`: 실행 후 모의 시스템의 상태입니다. 잠긴 계정과 티켓이 들어 있는지 확인합니다.
6. **[보고서]** `day01_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 실행 후 잠긴 계정 · 차단한 IP · 티켓의 개수와 승인 대기 건수를 적어 주세요.
   - (나) 🔍 5교시에서 INC-005 를 수동 처리할 때와 달리, 실행기는 INC-005 를 어떻게 처리했는지 적어 주세요. 근거는 단계 3 · 4 · 5 의 출력으로 쓰고, 그렇게 처리한 이유도 적어 주세요.
   - (다) 🔍 감사 기록(단계 6)에서 INC-002 의 한 줄을 읽고, 그 인시던트에 실제로 무엇이 일어났고 무엇이 일어나지 않았는지 적어 주세요. 이런 기록이 현업에서 필요한 이유도 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 값이 다르면 | `if playbook["approval"] != "자동":` |
| 리스트에 추가 | `action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))` |
| 여기서 끝내기 | `return False` |
| 액션 실행하고 결과 받기 | `result = run_action(action, incident, state)` |
| 상태 옮기기 | `change_status(incident, "조치됨")` |

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다.</mark> 6교시 마지막 약 10분에 합니다. 5과목 폴더를 처음 올리는 날이므로 올라가는 파일 목록을 꼭 확인합니다. 어느 터미널을 써도 됩니다. `pwd` 로 위치를 먼저 확인하고, 그 결과가 `soar_response` 로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「5과목 첫날에 만든 플레이북과 실행 코드, 감사 기록을 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소에 `soar_response` 폴더가 생기고 `config` 폴더와 `incident.py` · `playbook_runner.py` · `action_log.json` 이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `soar_response` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day01_pm_report.md` 의 5 · 6교시 칸에서 비어 있는 칸이 없는지도 봅니다. 질문마다 `답:` 뒤와 코드 상자를 채웠는지 확인합니다(마무리 (가)는 3번에서 채웁니다).

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
   - 나오는 것: `config` · `incident.py` · `playbook_runner.py` · `incident_samples.json` · `system_state.json` · `action_log.json` · `day01_6-1_run.py` 가 보이면 됩니다.

1. **[터미널]** `security-agent-toolkit` 폴더로 옮깁니다. 0번의 `pwd` 결과가 `soar_response` 로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.

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

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark>빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 말고,</mark> 아래 안내대로 `.gitignore`(깃에 올리지 않을 파일 이름을 적어 두는 파일)를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다. <mark>`soar_response/` 가 새 폴더로 보이면</mark> 됩니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `soar_response/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.

3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 올릴 목록에 추가하고(`add`), 기록으로 저장하고(`commit`), 깃허브로 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 추가합니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 올릴 목록에 추가합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add SOAR playbook runner with approval and audit log"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark>`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다.
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
| 플레이북을 쓰고, 알림 두 건을 수동 처리해 보며 번거로움을 겪었다 | 오후 5-1 |
| 플레이북 실행기로 알림 5건을 처리하고, 승인이 필요한 건은 멈추고, 감사 기록을 읽었다 | 오후 6-1 |
| 5과목 첫날 파일과 보고서를 깃허브에 올렸다 | 마무리 |

오늘은 모의 시스템에서 실행했습니다. <mark>다음 수업부터 모의 시스템 대신 실제로 동작하는 대응(계정 잠금 · 접근 차단 등)을 연결하고, 승인과 기록 기능을 더 추가합니다.</mark> 오늘 정한 승인 값과 감사 기록의 모양은 그때도 그대로 쓰입니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
touch config/playbook_registry.json
ls config
python -c "import json; print([p['id'] for p in json.load(open('config/playbook_registry.json', encoding='utf-8'))])"
python -c "import json; s = json.load(open('system_state.json', encoding='utf-8')); print(s['locked_users'], s['blocked_ips'], len(s['tickets']))"
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름` 빈 파일 만들기 · `ls 폴더이름` 폴더 안의 파일 이름 보기

**채운 파일** (한 예)

`config/playbook_registry.json` 의 PB-003 한 건과 전체 파일은 다음과 같습니다.

```
[
  {
    "id": "PB-001",
    "name": "퇴사한 계정의 서버 요청",
    "trigger_rule": "퇴사한 계정",
    "min_grade": "high",
    "actions": [
      "계정 잠금",
      "티켓 생성"
    ],
    "approval": "자동",
    "reason": "퇴사한 사람의 계정으로 서버에 요청이 오면 그 계정이 아직 사용할 수 있는 상태라는 뜻입니다. 퇴사한 사람이 쓰는 계정이 없으므로 잠가도 막히는 업무가 없습니다."
  },
  {
    "id": "PB-002",
    "name": "대량 다운로드",
    "trigger_rule": "대량 다운로드",
    "min_grade": "mid",
    "actions": [
      "담당자 알림",
      "티켓 생성"
    ],
    "approval": "담당자 승인 필요",
    "reason": "파일을 많이 내려받은 것은 업무 때문일 수도 있습니다. 사람이 확인하기 전에는 정상인지 알 수 없으므로 담당자가 허락한 뒤에 실행합니다."
  },
  {
    "id": "PB-003",
    "name": "경로 스캔",
    "trigger_rule": "경로 스캔",
    "min_grade": "low",
    "actions": [
      "IP 차단",
      "티켓 생성"
    ],
    "approval": "담당자 승인 필요",
    "reason": "경로 스캔의 대상은 사용자가 아니라 IP 입니다. 같은 IP 를 여러 사람이 쓰고 있으면 차단했을 때 정상 사용자의 업무도 막히므로, 담당자가 확인한 뒤에 차단합니다."
  }
]
```

수동 처리한 뒤의 `system_state.json` 은 다음과 같습니다(PB-003 을 `IP 차단` · `티켓 생성` 으로 쓴 경우).

```
{
  "locked_users": ["dami"],
  "blocked_ips": ["198.51.100.90"],
  "tickets": [
    {"id": "TCK-1", "incident": "INC-001", "target": "dami"},
    {"id": "TCK-2", "incident": "INC-005", "target": "198.51.100.90"}
  ],
  "notifications": []
}
```

위 파일은 한 예입니다. <mark>액션과 승인은 다르게 골라도 이유가 맞으면 맞습니다.</mark>

**결과**

- (가) PB-003 의 액션은 <mark style="background:#bde3ff">**IP 차단 · 티켓 생성**</mark>, 승인은 <mark style="background:#bde3ff">**담당자 승인 필요**</mark>입니다. 두 확인 명령의 출력은 다음과 같습니다.

```
['PB-001', 'PB-002', 'PB-003']
['dami'] ['198.51.100.90'] 2
```

- (나) 위 예에서 고친 곳은 <mark style="background:#bde3ff">**모두 4군데**</mark>입니다.
  - `locked_users` 에 `"dami"` 1군데, `blocked_ips` 에 IP 1군데, `tickets` 에 티켓 2군데입니다.
  - 알림 두 건에 이 정도이니, 알림이 100건이면 수백 군데를 고쳐야 합니다.
  - 같은 모양의 줄을 반복해 쓰다 보면 쉼표나 대괄호를 빠뜨려 파일을 읽을 때 오류가 나기 쉽습니다. 또 어떤 알림을 처리했는지 빠뜨려도 아무도 알지 못합니다.
  - 티켓 번호(`TCK-1` · `TCK-2`)를 사람이 직접 세어야 하는 것도 틀리기 쉬운 부분입니다.
- (다) 승인을 <mark style="background:#bde3ff">`담당자 승인 필요`</mark> 로 정한 이유는 대상이 IP 이기 때문입니다.
  - 사용자 계정은 한 사람의 것이지만, IP 하나는 여러 사람이 함께 쓸 수 있습니다. 그 IP 를 차단하면 경로 스캔과 상관없는 사람도 접속하지 못합니다.
  - 오늘 샘플에서 `198.51.100.90` 은 점수 30점으로 등급이 `low` 입니다. 급하게 막지 않아도 되는 등급이라, 담당자가 확인할 시간을 두는 쪽이 안전합니다.
  - 한 예로 `자동` 을 고르려면 「차단을 바로 풀 수 있다」는 전제가 있어야 합니다. 그 경우에도 `reason` 에 전제를 적어 둡니다.

**왜**

- <mark>플레이북은 「무엇을 할지」뿐 아니라 「누구의 허락을 받고 할지」까지 정해야 완성됩니다.</mark> 수동 처리를 해 보면 같은 일을 반복하는 데 시간이 들고 틀리기 쉽습니다. 그래서 6교시에 프로그램이 대신하게 만듭니다.

**자주 틀리는 곳**

- 등록 파일의 마지막 플레이북 뒤에 쉼표를 남기면 확인 명령에서 `JSONDecodeError` 가 납니다. <mark>**마지막 플레이북 뒤에는 쉼표를 붙이지 않습니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`Expecting value`</mark> 로 시작하면 이 실수이고, 줄 번호는 사람마다 다릅니다).

```
json.decoder.JSONDecodeError: Expecting value: line 38 column 1 (char 875)
```

- PB-002 의 `}` 뒤에 쉼표를 빼고 PB-003 을 붙이면 같은 명령에서 다른 오류가 납니다. <mark>**플레이북과 플레이북 사이에는 쉼표가 있어야 합니다.**</mark>

```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 14 column 3 (char 298)
```

- `actions` 를 `"IP 차단", "티켓 생성"` 처럼 대괄호 없이 쓰면 JSON 문법에 맞지 않아 오류가 납니다. <mark>**`actions` 의 값은 `[ ]` 로 감싼 리스트입니다.**</mark>
- 알림의 대상이 IP 인데 액션에 `계정 잠금` 을 고르면 대상과 맞지 않는 액션입니다. 이 알림은 IP 가 대상이므로 5.2 의 표에서 「대상」이 IP 인 액션을 골라야 합니다. 6교시 실행기는 이런 액션을 실행하지 않고 「건너뜀」으로 기록합니다.

**관제에서는**

- 플레이북은 새 담당자가 와도 같은 순서로 대응하게 하는 문서이고, 승인 값은 자동화를 안전하게 쓰는 기준입니다. <mark>처음에는 사람의 승인을 넣어 두고, 같은 알림을 여러 번 처리해도 잘못된 대응이 없었다고 확인되면 `자동` 으로 바꾸는 방식이 흔합니다.</mark>

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day01_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 `run_playbook` 한 함수입니다.

```python
    if playbook["approval"] != "자동":                                              # 승인 값이 자동이 아니면
        action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))  # 승인 대기로 기록하고
        return False                                                                # 실행하지 않고 끝낸다
    for action in playbook["actions"]:                                              # 액션을 하나씩 꺼낸다
        result = run_action(action, incident, state)                                # 액션을 실행하고 결과 문장을 받는다
        action_log.append(make_log_entry(incident, playbook, action, result))       # 결과를 감사 기록에 추가한다
    change_status(incident, "조치됨")                                               # 실행이 끝났으니 조치됨으로 옮긴다
```

위 코드는 한 예입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같습니다(PB-003 이 `담당자 승인 필요` 인 경우). 실행 후 잠긴 계정은 <mark style="background:#bde3ff">**`dami` 1개**</mark>, 차단한 IP는 <mark style="background:#bde3ff">**0개**</mark>, 티켓은 <mark style="background:#bde3ff">**1건**</mark>, 승인 대기는 <mark style="background:#bde3ff">**2건**</mark>(INC-002 · INC-005)입니다.

```
--- 단계 1: 불러온 인시던트 5 건 · 등록된 플레이북 3 개
--- 단계 2: 실행 전 모의 시스템 상태
잠긴 계정: []
차단한 IP: []
티켓: 0 건 · 담당자 알림: 0 건
--- 단계 3: 인시던트마다 플레이북 실행
INC-001 dami high -> PB-001 실행 완료 (상태: 조치됨)
INC-002 seoyeon mid -> PB-002 승인 대기 (상태: 분류됨)
INC-003 gaeun mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-004 jiwoo mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-005 198.51.100.90 low -> PB-003 승인 대기 (상태: 분류됨)
--- 단계 4: 실행 후 모의 시스템 상태
잠긴 계정: ['dami']
차단한 IP: []
티켓: 1 건 · 담당자 알림: 0 건
--- 단계 5: 승인 대기 2 건
INC-002 seoyeon PB-002 · 담당자 승인 필요
INC-005 198.51.100.90 PB-003 · 담당자 승인 필요
--- 단계 6: 감사 기록 4 건을 action_log.json 에 저장
INC-001 PB-001 계정 잠금 : 계정 dami 잠금 완료
INC-001 PB-001 티켓 생성 : 티켓 TCK-1 생성
INC-002 PB-002 전체 : 승인 대기
INC-005 PB-003 전체 : 승인 대기
```

- (나) 5교시에서는 INC-005 를 처리한다고 가정하고 `198.51.100.90` 을 차단했지만, <mark style="background:#bde3ff">실행기는 INC-005 를 처리하지 않고 승인 대기로 멈췄습니다.</mark>
  - 근거: 단계 3 에 `INC-005 … -> PB-003 승인 대기 (상태: 분류됨)`, 단계 4 에 `차단한 IP: []`, 단계 5 에 `INC-005 … PB-003 · 담당자 승인 필요` 가 나옵니다.
  - 이유: `run_playbook` 이 플레이북의 `approval` 이 `자동` 이 아니면 액션을 실행하지 않기 때문입니다. 수동 처리할 때는 이 확인을 사람이 기억해야 했지만, 실행기는 매번 확인합니다.
  - PB-003 의 승인 값을 `자동` 으로 쓴 경우에는 단계 4 의 `차단한 IP` 에 `198.51.100.90` 이 들어갑니다. 또 INC-005 가 `실행 완료 (상태: 조치됨)` 로 나옵니다. 승인 값 하나가 실제 결과를 바꿉니다.
- (다) INC-002 의 기록 한 줄은 `INC-002 PB-002 전체 : 승인 대기` 입니다.
  - 일어난 일: 플레이북 PB-002 가 인시던트 INC-002 에 맞아서 시작됐고, 승인이 필요해 승인 대기로 기록됐습니다.
  - 일어나지 않은 일: 담당자 알림도 티켓 생성도 실행하지 않았습니다. 이 인시던트의 상태는 `분류됨` 입니다.
  - 필요한 이유: 사고가 난 뒤 「그때 왜 조치하지 않았나」를 물으면 이 기록으로 「승인을 기다리고 있었다」고 설명할 수 있습니다. 기록이 없으면 실행하지 않은 일은 아무 흔적도 남지 않습니다.

PB-003 을 `자동` 으로 쓴 경우의 단계 3 ~ 6 은 다음과 같습니다.

```
--- 단계 3: 인시던트마다 플레이북 실행
INC-001 dami high -> PB-001 실행 완료 (상태: 조치됨)
INC-002 seoyeon mid -> PB-002 승인 대기 (상태: 분류됨)
INC-003 gaeun mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-004 jiwoo mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-005 198.51.100.90 low -> PB-003 실행 완료 (상태: 조치됨)
--- 단계 4: 실행 후 모의 시스템 상태
잠긴 계정: ['dami']
차단한 IP: ['198.51.100.90']
티켓: 2 건 · 담당자 알림: 0 건
--- 단계 5: 승인 대기 1 건
INC-002 seoyeon PB-002 · 담당자 승인 필요
--- 단계 6: 감사 기록 5 건을 action_log.json 에 저장
INC-001 PB-001 계정 잠금 : 계정 dami 잠금 완료
INC-001 PB-001 티켓 생성 : 티켓 TCK-1 생성
INC-002 PB-002 전체 : 승인 대기
INC-005 PB-003 IP 차단 : IP 198.51.100.90 차단 완료
INC-005 PB-003 티켓 생성 : 티켓 TCK-2 생성
```

PB-003 의 액션에 `계정 잠금` 을 골랐고 승인을 `자동` 으로 쓴 경우의 단계 3 과 단계 6 은 다음과 같습니다. 대상이 IP 라서 실행하지 않고 건너뜁니다.

```
--- 단계 3: 인시던트마다 플레이북 실행
INC-001 dami high -> PB-001 실행 완료 (상태: 조치됨)
INC-002 seoyeon mid -> PB-002 승인 대기 (상태: 분류됨)
INC-003 gaeun mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-004 jiwoo mid -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-005 198.51.100.90 low -> PB-003 실행 완료 (상태: 조치됨)
…
--- 단계 6: 감사 기록 5 건을 action_log.json 에 저장
INC-001 PB-001 계정 잠금 : 계정 dami 잠금 완료
INC-001 PB-001 티켓 생성 : 티켓 TCK-1 생성
INC-002 PB-002 전체 : 승인 대기
INC-005 PB-003 계정 잠금 : 건너뜀: 대상이 IP 라서 계정 잠금을 할 수 없습니다
INC-005 PB-003 티켓 생성 : 티켓 TCK-2 생성
```

**왜**

- <mark>승인 값을 코드가 매번 확인해 멈추게 하면, 사람이 기억하지 않아도 허락 없이 실행되는 일이 막힙니다.</mark> 그리고 실행한 일과 멈춘 일을 모두 기록하면 나중에 설명할 수 있습니다.

**자주 틀리는 곳**

- 1 ~ 3번을 빠뜨리면 오류는 나지 않지만 <mark>**승인이 필요한 플레이북도 바로 실행됩니다.**</mark> 단계 4 에 차단한 IP 가 들어 있고 단계 5 의 승인 대기가 0건으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 4: 실행 후 모의 시스템 상태
잠긴 계정: ['dami']
차단한 IP: ['198.51.100.90']
티켓: 3 건 · 담당자 알림: 1 건
--- 단계 5: 승인 대기 0 건
```

- 1번을 `!=` 대신 `==` 로 쓰면 반대로 동작합니다. <mark>**자동이어야 하는 PB-001 이 승인 대기로 멈추고, 승인이 필요한 플레이북이 실행됩니다.**</mark> 단계 5 에 `INC-001 dami PB-001 · 자동` 이 나오는 것이 이 실수의 결과입니다.

```
--- 단계 5: 승인 대기 1 건
INC-001 dami PB-001 · 자동
```

- 4번을 빠뜨리고 5번에서 `result` 를 쓰면 오류가 납니다. <mark>**`result` 는 4번에서 만들어야 쓸 수 있습니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`name 'result' is not defined`</mark>).

```
NameError: name 'result' is not defined
```

- 6번을 빠뜨리면 오류는 나지 않지만 <mark>**실행을 마친 인시던트의 상태가 `조치됨` 이 아니라 `분류됨` 으로 남습니다.**</mark> 단계 3 의 INC-001 줄 끝이 이 실수의 결과입니다.

```
INC-001 dami high -> PB-001 실행 완료 (상태: 분류됨)
```

**관제에서는**

- 자동 대응을 켤 때 가장 먼저 확인하는 것은 「허락이 필요한 일이 멈추는가」와 「한 일이 모두 기록되는가」입니다. <mark>승인 대기 목록은 담당자가 아침에 가장 먼저 보는 목록</mark>이고, 감사 기록은 사고가 난 뒤 대응을 다시 확인할 때 쓰는 자료입니다.

---

### 정답 마무리

- (가) 한 예: <mark>`git status` 에서 `.env` 와 `.venv` 가 보이지 않았습니다.</mark> `__pycache__` 가 보여서 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 다시 확인했습니다.
- 깃허브에 `soar_response` 폴더가 생기고 `config` 폴더와 `incident.py` · `playbook_runner.py` · `action_log.json` 이 보이면 됩니다.
