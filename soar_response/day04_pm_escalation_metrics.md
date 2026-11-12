# 11/12(목) 오후 · 5과목 자동 대응(SOAR) ⑦ — 에스컬레이션(escalation) 구현: 응답 기한(SLA) 초과 티켓의 상급자 통보 · 근무 3시간 시뮬레이션과 운영 지표(MTTA · MTTR · 응답 기한 위반 수) 산출

오전에는 세 가지를 했습니다. 알림으로 티켓(ticket, 티켓: 처리할 일 한 건을 적어 두는 기록)을 생성했습니다. 같은 사건의 알림은 티켓 한 장으로 병합(merge)했습니다. 그리고 담당자에게 통지(notification)했습니다. 오후에는 두 가지를 구현합니다. 하나는 **에스컬레이션**(escalation, 에스컬레이션: 처리되지 않는 일을 더 높은 책임자에게 넘기는 절차)입니다. <mark>담당자가 응답 기한 안에 응답하지 않으면 상급자에게 통보하는 기능</mark>입니다. 다른 하나는 **운영 지표**(operational metrics, 오퍼레이셔널 메트릭스: 팀의 대응 속도를 숫자로 나타낸 값)입니다. 근무가 끝날 때 팀의 대응 속도를 보고하기 위해 이 값을 산출합니다. 두 기능은 보안 관제(SOC, Security Operations Center, 소크: 보안 사건을 감시하고 대응하는 조직)가 근무 중 운영하는 절차입니다.

- **5교시**: **응답 기한**(SLA, Service Level Agreement, 에스엘에이: 티켓이 생성된 뒤 담당자가 확인해야 하는 제한 시간. 원래는 「서비스 수준 협약」의 줄임말)이 지났는데도 확인(acknowledge)되지 않은 티켓을 상급자에게 에스컬레이션합니다(`escalation.py`). 예를 들어 <mark style="background:#ffdcb0">`TCK-1` 은 응답 기한이 15분이므로 15분 안에 확인되어야 합니다</mark>. 20분이 되도록 아무도 확인하지 않았다면 5분을 초과한 것입니다.
- **6교시**: 오전부터 구현한 기능을 근무 3시간 시뮬레이션(simulation, 시뮬레이션: 실제 근무 대신 연습용 알림 · 동작 기록으로 근무 시간을 재현하는 방식)으로 연속 실행합니다. 그 결과로 <mark>MTTA(평균 확인 시간) · MTTR(평균 해결 시간) · 응답 기한 위반(SLA breach) 수를 산출합니다</mark>. 마지막으로 다음 근무자에게 인계(handoff)할 미해결 티켓 목록을 작성합니다(`shift_metrics.py`).

깃허브에 올리는 일은 6교시 마지막에 합니다. 새 문법은 6교시의 `sum()` 과 `%` 둘이고, 나눗셈 `/` 는 문법 상자에서 풀이합니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기는 미리 채운 줄에 맞춥니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. <mark style="background:#ffc4d6">주석은 지우지 않습니다</mark>.

📎 **이전 파일**: 오전에 만든 `ticketing.py` · `ticket_merge.py` · `ticket_notice.py` 와 데이터 `alerts_thu.json` · `config/escalation_rules.json`, <mark style="background:#e0d4ff">월요일의 `incident.py`</mark>, <mark style="background:#e0d4ff">1과목의 `notifier.py` · `alert_server.py`</mark> 를 씁니다. 5교시는 오전 4교시가 저장한 `tickets_day4.json` 도 읽습니다. 6교시는 5교시에서 만든 `escalation.py` 도 씁니다. 없는 파일은 `complete_files.md` 에서 복사합니다(오전 파일은 6절, `escalation.py` 는 7절). `incident.py` · `notifier.py` · `alert_server.py` 는 오전 안내 시작하기의 「🛟 이전 파일이 없을 때」 코드 상자로 만듭니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark style="background:#bde3ff">`ls` 결과에 `ticketing.py` · `ticket_merge.py` · `ticket_notice.py` · `tickets_day4.json` 이 보이면</mark> 됩니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다. `cd` 가 안 되면 `ls` 로 `soar_response` 폴더가 보이는지 확인합니다.
   - `tickets_day4.json` 이 없으면 먼저 아래 6번(알림 서버 켜기)을 합니다. 그다음 이 터미널에서 오전 4교시 실행 파일(`day04_4-1_run.py`)을 한 번 실행하면 `tickets_day4.json` 이 생깁니다. 오전 4교시 안내 문서의 `day04_4-1_run.py` 코드로 파일을 만들어 실행합니다(`ticketing.py` 같은 오전 코드 파일은 `complete_files.md` 6절에서 복사합니다). 이 경우 서버 터미널에 오전 4교시의 `[알림 받음]` 9줄이 먼저 나오므로, 5교시의 4줄은 그 아래부터 셉니다.
3. 오늘 받은 파일 두 개(`day04_pm_escalation_metrics.md`, `day04_pm_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 담당자 동작 파일을 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch status_events.json
   ls
   ```

**`status_events.json`** — 6교시 근무 시뮬레이션 3시간 동안 담당자가 티켓 상태를 변경한 기록입니다.

- **구성**: 담당자 동작 한 건은 `minute`(변경 시각, 분), `ticket`(티켓 번호), `status`(변경 후 상태), `who`(변경한 담당자)로 이루어집니다.
- **용도**: 6교시 실행 파일이 이 기록에 따라 티켓 상태를 변경합니다. 5교시에서는 사용하지 않습니다.

```
[
  {"minute": 10, "ticket": "TCK-1", "status": "확인 중", "who": "kim.sec"},
  {"minute": 45, "ticket": "TCK-1", "status": "해결", "who": "kim.sec"},
  {"minute": 80, "ticket": "TCK-3", "status": "확인 중", "who": "lee.soc"},
  {"minute": 90, "ticket": "TCK-6", "status": "확인 중", "who": "kim.sec"},
  {"minute": 105, "ticket": "TCK-7", "status": "확인 중", "who": "kim.sec"},
  {"minute": 120, "ticket": "TCK-3", "status": "해결", "who": "lee.soc"},
  {"minute": 130, "ticket": "TCK-6", "status": "해결", "who": "kim.sec"},
  {"minute": 140, "ticket": "TCK-4", "status": "확인 중", "who": "lee.soc"}
]
```

5. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`). <mark style="background:#bde3ff">`7 8` 이 나와야</mark> 합니다.
   ```bash
   python -c "import json; print(len(json.load(open('tickets_day4.json', encoding='utf-8'))), len(json.load(open('status_events.json', encoding='utf-8'))))"
   ```
6. **[터미널]** 알림 서버를 시작합니다. VS Code 터미널 창 오른쪽 위의 `+` 로 **새 터미널**을 하나 더 열고 서버를 실행합니다(맥북은 `python3`). <mark style="background:#bde3ff">`Running on http://127.0.0.1:5001` 이 보이면</mark> 됩니다. 이 터미널은 오후 내내 그대로 둡니다.
   ```bash
   pwd
   python alert_server.py
   ```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError` 는 <mark style="background:#ffc4d6">오전 파일이나 `incident.py` · `notifier.py` 가 이 폴더에 없다는 뜻</mark>입니다. `complete_files.md` 에서 복사합니다.
- 출력에 `[알림 실패] ConnectionError`(연결 오류)가 나오면 <mark style="background:#ffc4d6">알림 서버가 실행 중이 아니라는 뜻</mark>입니다. 6번을 다시 실행합니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 5교시 실행 파일은 `tickets_day4.json` 을 읽기만 하고 다시 저장하지 않아서, 몇 번을 실행해도 같은 결과가 나옵니다.

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 응답 기한(SLA)이 초과된 미확인 티켓을 상급자에게 에스컬레이션하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 오전에 만든 `TCK-1`(퇴사한 `dami` 계정, 등급 high)은 <mark style="background:#ffdcb0">응답 기한(SLA)이 15분입니다</mark>. 즉, 티켓이 생성된 뒤 15분 안에 담당자가 확인해야 합니다. 확인(acknowledge, 애크날리지)은 알림을 받았고 처리를 맡았다고 표시하는 일입니다. 티켓 상태 `열림`(open, 오픈)은 아직 아무도 확인하지 않은 상태입니다. 그런데 20분이 되도록 어떤 담당자도 `TCK-1` 을 확인하지 않아 `열림` 그대로인 경우를 가정합니다. 이때 응답 기한을 5분 초과한 것입니다.
> - **문제**: 두 가지입니다. 먼저 용어를 정리합니다. 에스컬레이션(escalation)은 처리되지 않는 일을 상급자에게 추가로 통보하는 일입니다.
>   - 첫째, <mark style="background:#ffc4d6">티켓이 `열림` 상태로 응답 기한을 초과해도 통보 체계가 없으면 위험도가 높은 사건이 처리되지 않은 채 남습니다</mark>. `TCK-1` 은 high 등급의 퇴사자 계정 사건인데도 방치될 수 있습니다.
>   - 둘째, 담당자가 이미 확인 중인 티켓까지 반복해서 에스컬레이션하면 상급자에게 알림이 지나치게 많아집니다. 그러면 상급자가 알림 피로(alert fatigue: 알림이 지나치게 많아 중요한 알림에도 반응이 둔해지는 현상)를 겪고 알림을 무시하게 됩니다.
> - **부탁**: 다음 세 가지를 만들어 주세요.
>   - <mark>응답 기한이 지났는데 아직 `열림` 상태인 티켓만</mark> 상급자에게 에스컬레이션해 주세요.
>   - <mark style="background:#ffdcb0">응답 기한을 초과한 시간이 길수록 더 높은 직급의 상급자에게 통보해 주세요</mark>. 기한을 넘기면 바로 팀장(`team.lead`)에게, 30분 이상 넘기면 관제 센터장(`soc.head`)에게 통보합니다. 예를 들어 5분 초과는 팀장 대상입니다.
>   - 같은 에스컬레이션 단계는 한 번만 실행해 주세요.
> - **바뀌는 점**: 방치된 티켓은 초과 시간에 따라 단계적으로 상급자에게 에스컬레이션되고, 확인 중인 티켓은 대상에서 제외됩니다. 오늘 샘플은 20 · 60 · 110분에 세 번 점검합니다. 점검은 정해진 시각마다 티켓 상태를 조회하는 일입니다.
>   - 20분: `TCK-1` 이 5분 초과라서 `team.lead` 에게 통보합니다. 그 뒤 25분에 `kim.sec` 이 `TCK-1` 을 확인해 상태가 `확인 중` 이 됩니다.
>   - 60분: `TCK-1` 은 `확인 중` 이므로 대상에서 제외됩니다. 통보는 없습니다.
>   - 110분: `TCK-3`(42분 초과)과 `TCK-4`(38분 초과)는 `soc.head` 에게, `TCK-6`(15분 초과)은 `team.lead` 에게 통보합니다.
>   - 세 번의 점검에서 에스컬레이션이 실행된 횟수를 모두 합하면 4번입니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 5.1 에스컬레이션은 「발동 시점 · 대상 티켓 · 통보 대상」을 정의한 규칙이다

**에스컬레이션**(escalation, 에스컬레이션: 처리되지 않는 일을 더 높은 책임자에게 넘기는 절차)은 미리 정한 규칙에 따라 실행합니다. 규칙은 아래 세 가지, 즉 <mark>언제 시작하는지(발동 시점), 어느 티켓이 대상인지(대상 티켓), 누구에게 통보하는지(통보 대상)</mark>를 정합니다. 오늘은 담당자보다 높은 직급(팀장 · 관제 센터장)에게 넘깁니다. 이 방식은 **계층적 에스컬레이션**(hierarchical escalation, 하이어라키컬 에스컬레이션: 지휘 체계를 따라 더 높은 권한자에게 넘기는 방식)에 해당합니다. 전문성이 더 높은 기술 팀에 넘기는 방식은 기능적 에스컬레이션(functional escalation)이라고 따로 부릅니다.

| 정의할 것 | 오늘 정한 방법 | 규칙 파일의 키 |
|---|---|---|
| 발동 시점(trigger, 트리거: 에스컬레이션을 시작하는 조건) | <mark style="background:#ffdcb0">지금 시각이 응답 기한 시각(`sla_due`, due 는 마감이라는 뜻)을 지났을 때</mark> | 티켓의 `sla_due`(규칙 파일의 `sla_minutes` 로 계산) |
| 대상 티켓 | <mark style="background:#ffdcb0">상태가 `열림` 인 티켓만 해당한다</mark>. `확인 중`(담당자가 확인함)이나 `해결`(처리 완료)은 대상에서 제외한다 | |
| 통보 대상 | <mark style="background:#ffdcb0">응답 기한 초과 시간이 0분 이상 30분 미만이면 1단계로 `team.lead`(팀장)에게, 30분 이상이면 2단계로 `soc.head`(관제 센터장)에게 통보한다</mark>. 예를 들어 `TCK-1` 은 5분 초과라 1단계, `TCK-3` 은 42분 초과라 2단계다 | `escalation_steps` |

- 담당자가 티켓을 확인하면 상태가 `열림` 에서 `확인 중` 으로 변경됩니다. 출력과 코드에서는 에스컬레이션 단계를 「올림 단계」라고 표시합니다.
- 이미 실행한 에스컬레이션 단계는 반복하지 않습니다. 티켓의 `escalation_level` 에 실행한 단계를 기록합니다. 그리고 기록된 단계보다 더 높은 단계에 해당할 때만 에스컬레이션합니다. 예를 들어 `escalation_level` 이 1 인 티켓은 1단계에 해당하는 동안 다시 통보하지 않고, 초과 시간이 30분 이상이 되어 2단계에 해당할 때 통보합니다. <mark style="background:#ffc4d6">점검할 때마다 같은 티켓을 반복해서 통보하면 상급자가 알림 피로를 겪어 알림을 무시하게 됩니다</mark>.
- 등급 low 는 응답 기한이 240분입니다. 그래서 오늘 점검 시각(20 · 60 · 110분)은 모두 응답 기한 시각보다 이릅니다. 예를 들어 `TCK-2` 의 응답 기한 시각은 243분입니다. 따라서 등급 low 티켓은 에스컬레이션 대상이 아닙니다.
- 점검 시각은 20분, 60분, 110분입니다(근무 시작 시점을 0분으로 하는 상대 시각). 이처럼 정해진 주기로 상태를 반복 조회하는 방식을 폴링(polling, 폴링: 일정한 간격으로 상태를 반복해서 확인하는 방식)이라고 합니다. 실제 운영에서는 몇 분마다 자동으로 점검합니다.
- 상급자에게 통보하는 기능은 오전 4교시의 `send_with_retry`(알림 전송에 실패하면 최대 3회까지 재시도(retry)하는 함수)를 재사용합니다. 오전 4교시 `ticket_notice.py` 를 가져와 사용(import)합니다.

아래 함수 네 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
escalation.py   overdue_minutes   : 응답 기한을 넘긴 시간(분)을 구한다 (1번)
                needs_escalation  : 열림 상태이고 기한이 지났으면 True 를 리턴한다 (2 ~ 4번)
                pick_level        : 넘긴 시간에 해당하는 가장 높은 올림 단계를 고른다 (5 · 6번)
                escalate_ticket   : 그 단계의 상급자에게 알리고 올린 단계를 적는다 (미리 채움)
실행 파일       day04_5-1_run.py  : 점검 시각마다 올릴 티켓을 찾고 (7번), 올리고 (8번), 올린 횟수를 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 5-1 · 응답 기한이 초과된 열림 상태 티켓을 초과 시간에 맞는 단계로 에스컬레이션하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>티켓이 확인되지 않은 채 응답 기한을 초과해도 상급자에게 에스컬레이션되지 않습니다</mark>.
- **만드는 것**: 두 파일을 만듭니다. `escalation.py` 는 응답 기한 초과 시간을 산출하고, 에스컬레이션 대상 티켓을 판별하고, 에스컬레이션 단계를 선택합니다. `day04_5-1_run.py` 는 점검 시각마다 대상 티켓을 에스컬레이션하고 실행 횟수를 집계합니다. 상급자에게 통보하는 함수는 미리 채워져 있습니다.
- **실행하면**: <mark>출력은 세 단계입니다. 단계 1 은 불러온 티켓 수와 올림 단계 수입니다. 단계 2 는 점검 시각마다 올린 티켓입니다. 단계 3 은 올린 결과 요약입니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 알림 서버를 실행한 상태에서 프로그램을 실행합니다. 그리고 단계 2 · 3 의 출력과 서버 터미널의 수신 로그를 해석합니다.

**`escalation.py`** — 응답 기한이 지난 티켓을 상급자에게 올립니다. 6교시에서도 이 파일을 가져와 사용(import)합니다. 직접 쓰는 곳은 1 ~ 6번입니다. 5번 아래에는 `if` 한 줄을, 6번 아래에는 한 단계 더 들여쓴 줄을 씁니다.

```python
from ticket_notice import send_with_retry, MAX_TRIES                                       # 4교시에 만든 재시도 함수를 불러온다


def overdue_minutes(ticket, now):                                                          # 티켓과 지금 시각(분)을 받는 함수
    """응답 기한을 넘긴 시간(분)을 리턴한다. 기한이 아직 안 됐으면 음수가 나온다.
    얼마나 늦었는지 알아야 어느 상급자에게 올릴지 정할 수 있어서 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. now 에서 ticket["sla_due"] 를 뺀 값을 리턴한다


def needs_escalation(ticket, now):                                                         # 티켓과 지금 시각(분)을 받는 함수
    """아직 열림 상태이고 응답 기한이 지났으면 True, 아니면 False 를 리턴한다. 담당자가 이미 확인 중이거나 해결한 티켓은 올리지 않는다.
    아무도 열어 보지 않은 티켓만 골라낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. ticket 의 "status" 가 "열림" 이 아니면 (if, !=)
    # 3.   False 를 리턴한다
    # 4. overdue_minutes(ticket, now) 가 0 이상인지(>=)의 결과를 리턴한다


def pick_level(overdue, steps):                                                            # 넘긴 시간과 올림 단계 리스트를 받는 함수
    """넘긴 시간에 해당하는 가장 높은 올림 단계 번호(1부터)를 리턴한다. 해당하는 단계가 없으면 0 을 리턴한다.
    오래 방치된 티켓일수록 더 높은 상급자에게 올릴 때 쓴다.
    """
    level = 0                                                                              # 처음에는 올릴 단계가 없다 — 미리 채운 줄
    for index in range(len(steps)):                                                        # 단계 번호를 0 부터 하나씩 읽는다 — 미리 채운 줄
        step = steps[index]                                                                # 그 번호의 올림 단계 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. overdue 가 step 의 "overdue_minutes" 이상이면 (if, >=)
            # 6. level 에 index + 1 을 저장한다
    return level                                                                           # 가장 높은 단계 번호를 리턴한다 — 미리 채운 줄


def escalate_ticket(ticket, now, rules):                                                   # 티켓 · 지금 시각(분) · 규칙을 받는 함수
    """티켓을 상급자에게 올린다. 이미 올린 단계이거나 올릴 때가 아니면 「그대로」, 올렸으면 「올림」, 알림이 모두 실패했으면 「실패」를 리턴한다.
    응답 기한이 지나도 아무도 확인하지 않은 티켓을 놓치지 않을 때 쓴다.
    """
    overdue = overdue_minutes(ticket, now)                                                 # 기한을 얼마나 넘겼는지
    steps = rules["escalation_steps"]                                                      # 규칙 파일의 올림 단계 리스트
    level = pick_level(overdue, steps)                                                     # 지금 해당하는 올림 단계
    if level <= ticket["escalation_level"]:                                                # 이미 올린 단계이거나 아직 올릴 때가 아니면
        return "그대로"                                                                    # 아무것도 하지 않는다
    step = steps[level - 1]                                                                # 그 단계의 규칙(받는 사람)
    message = "[올림 " + str(level) + "단계] " + ticket["id"] + " " + ticket["title"] + " · 기한을 " + str(overdue) + "분 넘김 · 받는 사람: " + step["notify"]  # 알림 내용을 만든다
    attempt = send_with_retry(message, rules["alert_url"], MAX_TRIES)                      # 최대 3번까지 보내 본다
    if attempt == 0:                                                                       # 모두 실패했으면
        return "실패"                                                                      # 올리지 못했다고 「실패」를 리턴한다
    ticket["escalation_level"] = level                                                     # 올린 단계를 적는다
    comment = str(now) + "분 · " + str(level) + "단계로 " + step["notify"] + " 에게 올림"  # 댓글 내용을 만든다
    ticket["comments"].append(comment)                                                     # 댓글 리스트에 추가한다
    return "올림"                                                                          # 「올림」을 리턴한다
```

**`day04_5-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 7번 아래에는 `if` 한 줄을, 8번 아래에는 한 단계 더 들여쓴 줄을, 9번 아래에는 또 한 단계 들여쓴 줄을 씁니다. 그 사이의 미리 채운 줄은 그대로 둡니다.

```python
from incident import load_json                                                       # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticket_merge import change_ticket_status                                        # 3교시에 만든 상태 바꾸기 함수를 불러온다
from escalation import overdue_minutes, needs_escalation, escalate_ticket            # 방금 만든 함수를 불러온다

tickets = load_json("tickets_day4.json")                                             # 오전 4교시가 저장한 티켓을 읽는다
rules = load_json("config/escalation_rules.json")                                    # 규칙 파일을 읽는다
steps_count = len(rules["escalation_steps"])                                         # 올림 단계가 몇 개인지 센다
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 올림 단계", steps_count, "개")  # 단계 1 시작을 알리는 줄
escalated_count = 0                                                                  # 상급자에게 올린 횟수 : 처음에는 0

print("--- 단계 2: 점검 시각마다 상급자에게 올릴 티켓 찾기")                         # 단계 2 시작을 알리는 줄
for now in [20, 60, 110]:                                                            # 점검할 시각(분)을 하나씩 읽는다
    print("[" + str(now) + "분] 점검")                                               # 점검 시각을 출력한다
    for ticket in tickets:                                                           # 티켓을 하나씩 읽는다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. needs_escalation(ticket, now) 가 참이면 (if)
            # 8. escalate_ticket(ticket, now, rules) 의 결과를 result 에 저장한다
            overdue = overdue_minutes(ticket, now)                                   # 기한을 얼마나 넘겼는지 구한다 — 미리 채운 줄
            print(ticket["id"], ticket["title"], "→", result, "· 기한을", overdue, "분 넘김 · 올림 단계", ticket["escalation_level"])  # 결과를 출력한다 — 미리 채운 줄
            if result == "올림":                                                     # 올렸으면 — 미리 채운 줄
                # 9. escalated_count 에 escalated_count + 1 을 저장한다 (1 늘린다)
    if now == 20:                                                                    # 20분 점검이 끝나면 — 미리 채운 줄
        change_ticket_status(tickets[0], "확인 중", 25, "kim.sec")                   # 25분에 kim.sec 이 TCK-1 을 확인하기 시작한다 — 미리 채운 줄
        print("[25분] TCK-1 → 확인 중 · kim.sec")                                    # 담당자의 동작을 출력한다 — 미리 채운 줄

print("--- 단계 3: 올린 결과 요약 (올린 횟수", escalated_count, "번)")               # 단계 3 시작을 알리는 줄과 횟수
for ticket in tickets:                                                               # 티켓을 하나씩 읽는다
    if ticket["escalation_level"] > 0:                                               # 상급자에게 올린 티켓이면
        print(ticket["id"], "올림 단계", ticket["escalation_level"], "· 상태", ticket["status"])  # 올림 단계와 지금 상태를 출력한다
```

**순서**

1. **[터미널]** 처음 쓰던 터미널에서 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch escalation.py day04_5-1_run.py
   ls
   ```
2. **[VS Code]** `escalation.py` 1 ~ 6번, `day04_5-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「5교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`). 알림 서버 터미널은 켜 둡니다.
   ```bash
   python day04_5-1_run.py
   ```
4. 출력은 세 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 제목 줄 하나만 나옵니다(숫자가 제목 줄 안에 함께 나옵니다). 단계 2 는 제목 아래 8줄입니다. 단계 3 은 제목 아래 4줄입니다(올린 횟수는 제목 줄 안에 있습니다). <mark>알림 서버 터미널에는 `[알림 받음]` 줄이 4개 찍힙니다.</mark>
5. **[보고서]** `day04_pm_report.md` 의 `## 5교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣어 주세요. 그리고 알림 서버 터미널에 출력된 `[알림 받음]` 줄 수와 단계 3 의 올린 횟수(에스컬레이션 실행 횟수)를 적어 주세요.
   - (나) 🔍 `TCK-1` 은 20분 점검에서 1단계로 에스컬레이션되었지만, 60분 점검에서는 에스컬레이션되지 않았습니다. 그 이유를 설명해 주세요. 이때 25분에 변경된 상태와 `needs_escalation` 의 조건을 근거로 쓰고, 이 조건이 없을 때 발생하는 문제도 함께 설명해 주세요.
   - (다) 🔍 110분 점검에서 `TCK-3` 은 2단계로, `TCK-6` 은 1단계로 에스컬레이션되었습니다. 두 티켓의 응답 기한과 초과 시간을 근거로 단계가 달라진 이유를 설명해 주세요. 또한 등급 low 인 `TCK-2` 가 에스컬레이션되지 않은 이유도 설명해 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 빼서 리턴 | `return now - ticket["sla_due"]` |
| 같지 않으면 | `if ticket["status"] != "열림":` |
| 이상인지의 결과 리턴 | `return overdue_minutes(ticket, now) >= 0` |
| 이상이면 | `if overdue >= step["overdue_minutes"]:` |
| 번호에 1 더해 저장 | `level = index + 1` |
| 함수 결과가 참이면 | `if needs_escalation(ticket, now):` |
| 함수 결과를 변수에 저장 | `result = escalate_ticket(ticket, now, rules)` |
| 1 늘려 다시 저장 | `escalated_count = escalated_count + 1` |

---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 근무 3시간 시뮬레이션을 연속 실행하고 MTTA(평균 확인 시간) · MTTR(평균 해결 시간) · 응답 기한 위반 수 산출하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 근무 교대(shift handoff, 시프트 핸드오프: 근무 시간이 끝나 다음 근무자에게 업무를 넘기는 일) 직전에 팀장이 요청합니다. 요청 내용은 「오늘 오전 3시간 동안 팀의 대응 속도를 지표로 보고해 주세요」입니다. 이 3시간 동안 알림이 11건 수신되었고, 담당자가 티켓 상태를 변경한 동작 기록(이력)은 8건입니다. 예를 들어 `TCK-1` 은 0분에 생성되어, 10분에 `확인 중` 으로, 45분에 `해결` 로 바뀌었습니다.
> - **문제**: 티켓마다 상태와 시각이 따로 기록되어 있습니다. 그래서 <mark style="background:#ffc4d6">대응 속도를 나타내는 집계 값(여러 기록을 합쳐 낸 숫자)이 없습니다</mark>. 응답 기한 위반 티켓(확인 시각이 응답 기한 시각보다 늦은 티켓. 아직 확인하지 않은 티켓은 현재 시각을 확인 시각으로 봅니다)도 사람이 하나씩 세어야 합니다. 인계할 미해결 티켓도 하나씩 확인해서 골라야 합니다. 그러면 보고가 늦어지고 세다가 틀릴 수 있습니다.
> - **부탁**: 근무 3시간 시뮬레이션(연습용 알림 · 동작 기록으로 근무 시간을 재현하는 방식)을 처음부터 끝까지 연속 실행한 뒤, 다음 세 가지를 산출해 주세요. 해결되지 않은 티켓은 다음 근무자에게 인계할 목록으로 출력해 주세요.
>   - MTTA(평균 확인 시간): 티켓이 생성된 때부터 담당자가 처음 확인하기까지 걸린 시간의 평균
>   - MTTR(평균 해결 시간): 티켓이 생성된 때부터 해결되기까지 걸린 시간의 평균
>   - 응답 기한 위반 티켓 수
> - **바뀌는 점**: 지표 세 개와 인계 목록(handoff list, 핸드오프 리스트: 다음 근무자에게 넘길 미해결 티켓 목록)으로 보고합니다. 오늘 샘플에서는 확인한 티켓 5장으로 구한 MTTA 가 55.0분이고, 해결한 티켓 3장으로 구한 MTTR 이 84.0분이며, 응답 기한 위반은 2장입니다. 인계 목록은 미해결 티켓 4장(`TCK-2` · `TCK-4` · `TCK-5` · `TCK-7`)입니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 6.1 관제 팀은 MTTA · MTTR · 응답 기한 위반 수로 「얼마나 빨리 확인하고 해결했는가」를 정량화해 보고한다

| 지표 | 정의 | 산출 방법 |
|---|---|---|
| **MTTA**(Mean Time To Acknowledge, 평균 확인 시간) | 티켓이 생성된 시점부터 담당자가 처음 확인(acknowledge)하기까지 걸린 시간의 평균 | <mark style="background:#ffdcb0">(확인 시각 − 생성 시각)의 평균</mark> |
| **MTTR**(Mean Time To Resolve, 평균 해결 시간) | 티켓이 생성된 시점부터 해결(resolve)되기까지 걸린 시간의 평균 | <mark style="background:#ffdcb0">(해결 시각 − 생성 시각)의 평균</mark> |
| 응답 기한 위반(SLA breach, 에스엘에이 브리치: 약속한 응답 기한을 지키지 못한 것) | 응답 기한 시각보다 늦게 확인된 티켓 | <mark style="background:#ffdcb0">확인 시각 > `sla_due`</mark> |

- 예를 들어 `TCK-1` 은 0분에 생성되어 10분에 확인되었으므로 확인 시간이 10 − 0 = 10분입니다. `TCK-3` 은 8분에 생성되어 80분에 확인되었으므로 80 − 8 = 72분입니다. MTTA 는 이런 확인 시간을 모두 더해 확인한 티켓 수로 나눈 값입니다.
- MTTR 도 같은 방식으로 구합니다. 오늘 샘플에서 해결한 티켓 3장의 해결 시간은 `TCK-1` 45분, `TCK-3` 112분, `TCK-6` 95분입니다. 합계 252분을 3으로 나누면 MTTR 은 84.0분입니다.
- <mark style="background:#ffdcb0">미확인 티켓과 미해결 티켓은 해당 시간 값이 아직 없으므로 평균 계산에서 제외합니다</mark>.
- MTTR 의 R 은 이 문서에서는 해결(Resolve)을 뜻합니다. 그러나 도구와 조직에 따라 <mark style="background:#ffc4d6">복구(Recovery) · 수리(Repair) 같은 다른 뜻으로도 정의합니다</mark>. 그래서 보고할 때는 측정 구간, 즉 어느 시점부터 어느 시점까지 잰 값인지를 함께 적습니다.
- 응답 기한 위반은 아직 확인되지 않은 티켓도 집계합니다. 확인되지 않았는데 이미 기한 시각이 지났다면 위반이기 때문입니다. 판정 방법은 다음과 같습니다. <mark style="background:#ffdcb0">미확인 티켓은 「지금 시각에 확인된 것」으로 간주합니다</mark>. 그리고 지금 시각이 기한 시각을 초과했는지 비교합니다.
- 예를 들어 `TCK-2` 는 근무 종료 시각 180분까지 확인되지 않았지만, 응답 기한 시각이 243분이어서 아직 기한 안이므로 위반이 아닙니다.
- 평균은 표본 크기(sample size, 샘플 사이즈: 평균을 계산한 티켓 수)와 함께 보고합니다. 티켓 5장으로 낸 평균보다 50장으로 낸 평균의 신뢰도가 높기 때문입니다. 오늘 MTTA 는 티켓 5장으로, MTTR 은 티켓 3장으로 계산한 평균입니다.
- 근무 시뮬레이션에서도 오전 3교시의 병합 규칙을 그대로 적용합니다. 이 규칙에서는 <mark style="background:#ffdcb0">해결된 티켓에 새 알림을 병합하지 않습니다</mark>. `TCK-1` 은 45분에 해결되었으므로, 95분에 같은 `dami` 알림(`INC-210`)이 수신되면 새 티켓 `TCK-7` 이 생성됩니다.

**🐍 문법 상자 — `sum()` 은 리스트의 합계를, `%`(나머지 연산자, modulo operator) 는 나눗셈의 나머지를 구한다**

```python
times = [10, 70, 40]
print(sum(times))
print(sum(times) / len(times))
print(25 % 10)
print(30 % 10 == 0)
```

| 코드 | 결과 | 뜻 |
|---|---|---|
| `sum(times)` | `120` | 리스트의 숫자를 모두 더한다 |
| `sum(times) / len(times)` | `40.0` | 합계를 개수로 나눈 평균이다. `/` 의 결과는 소수점이 있는 숫자다 |
| `25 % 10` | `5` | 25 를 10 으로 나눈 나머지다 |
| `30 % 10 == 0` | `True` | 나머지가 0 이면 나누어떨어진다. <mark style="background:#ffdcb0">수업에서는 `now % 10 == 0` 으로 10분마다 점검한다</mark> |

아래 함수 네 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
shift_metrics.py   average                 : 숫자 리스트의 평균을 구한다. 비어 있으면 0 (1 ~ 3번)
                   collect_response_times  : 확인한 티켓마다 (확인한 시각 − 만든 시각)을 모은다 (4 · 5번)
                   collect_resolve_times   : 해결한 티켓마다 (해결한 시각 − 만든 시각)을 모은다 (미리 채움)
                   count_sla_breaches      : 응답 기한을 넘겨 확인한 티켓 수를 센다 (6 · 7번)
실행 파일          day04_6-1_run.py        : 가상 근무 3시간을 실행하고 (미리 채움), 확인까지 걸린 시간 리스트를 만들어 (8번) 평균을 구한다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 6-1 · 근무 3시간 시뮬레이션을 실행하고 MTTA · MTTR · 응답 기한 위반 수 산출하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>티켓 생성 · 병합 · 통지 · 에스컬레이션이 개별 기능으로만 있고, 근무 3시간을 연속 실행해 지표로 보고하는 코드가 없습니다</mark>.
- **만드는 것**: 두 파일을 만듭니다. `shift_metrics.py` 는 평균을 계산하고, 확인 시간을 수집하고, 응답 기한 위반 티켓을 집계합니다. `day04_6-1_run.py` 는 확인까지 걸린 시간 리스트를 만들고 그 평균인 MTTA 를 구합니다. 근무 3시간을 시뮬레이션하는 부분은 미리 채워져 있습니다.
- **실행하면**: <mark>출력은 네 단계입니다. 단계 1 은 0분부터 180분까지 발생한 이벤트(알림 처리 · 담당자 동작 · 에스컬레이션)입니다. 단계 2 는 근무 지표(MTTA · MTTR · 응답 기한 위반 수)입니다. 단계 3 은 다음 근무자에게 인계할 미해결 티켓입니다. 단계 4 는 파일에 저장한 티켓 수입니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 알림 서버를 실행한 상태에서 프로그램을 실행합니다. 그리고 단계 1 ~ 3 의 출력을 해석합니다.

**`shift_metrics.py`** — 근무 지표를 계산합니다. 직접 쓰는 곳은 1 ~ 7번입니다. 4번 아래에는 `if` 한 줄을, 5번 아래에는 한 단계 더 들여쓴 줄을 씁니다. 6번과 7번도 같은 모양입니다.

```python
def average(numbers):                                                   # 숫자 리스트를 받는 함수
    """숫자 리스트의 평균을 리턴한다. 리스트가 비어 있으면 0 을 리턴한다.
    평균 확인 시간과 평균 해결 시간을 계산할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. numbers 의 개수(len)가 0 이면 (if, ==)
    # 2.   0 을 리턴한다 (비어 있으면 나눌 수 없다)
    # 3. sum(numbers) / len(numbers) 를 리턴한다 (합계를 개수로 나눈다)


def collect_response_times(tickets):                                    # 티켓 리스트를 받는 함수
    """담당자가 처음 확인한 티켓마다 (확인한 시각 − 만든 시각)을 모아 리스트로 리턴한다. 아직 확인하지 않은 티켓은 뺀다.
    평균 확인 시간(MTTA)을 구할 재료를 만들 때 쓴다.
    """
    times = []                                                          # 걸린 시간(분)을 저장할 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. ticket 의 "acked_at" 이 -1 이 아니면 (if, !=)
            # 5. times 리스트에 ticket["acked_at"] - ticket["created_at"] 을 추가한다 (append)
    return times                                                        # 걸린 시간 리스트를 리턴한다 — 미리 채운 줄


def collect_resolve_times(tickets):                                     # 티켓 리스트를 받는 함수
    """해결한 티켓마다 (해결한 시각 − 만든 시각)을 모아 리스트로 리턴한다. 아직 해결하지 않은 티켓은 뺀다.
    평균 해결 시간(MTTR)을 구할 재료를 만들 때 쓴다.
    """
    times = []                                                          # 걸린 시간(분)을 저장할 빈 리스트
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다
        if ticket["resolved_at"] != -1:                                 # 해결한 티켓이면
            times.append(ticket["resolved_at"] - ticket["created_at"])  # 걸린 시간을 추가한다
    return times                                                        # 걸린 시간 리스트를 리턴한다


def count_sla_breaches(tickets, now):                                   # 티켓 리스트와 지금 시각(분)을 받는 함수
    """응답 기한을 넘긴 티켓 수를 리턴한다. 아직 확인하지 않은 티켓은 지금 시각에 확인한 것으로 본다.
    응답 기한(SLA)을 얼마나 지켰는지 보고할 때 쓴다.
    """
    late = 0                                                            # 기한을 넘긴 티켓 수 : 처음에는 0 — 미리 채운 줄
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다 — 미리 채운 줄
        checked_time = ticket["acked_at"]                               # 확인한 시각 — 미리 채운 줄
        if checked_time == -1:                                          # 아직 확인하지 않았으면 — 미리 채운 줄
            checked_time = now                                          # 지금 시각에 확인한 것으로 본다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. checked_time 이 ticket 의 "sla_due" 보다 크면 (if, >)
            # 7. late 에 late + 1 을 저장한다 (1 늘린다)
    return late                                                         # 기한을 넘긴 티켓 수를 리턴한다 — 미리 채운 줄
```

**`day04_6-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 오전의 `ticket_merge.py` · `ticket_notice.py` 와 5교시의 `escalation.py` 가 같은 폴더에 있어야 합니다.

```python
from incident import load_json, save_json                                             # 월요일 파일의 JSON 읽기 · 저장 함수를 불러온다
from ticket_merge import handle_alert, change_ticket_status                           # 3교시에 만든 함수를 불러온다
from ticket_notice import send_ticket_notice                                          # 4교시에 만든 알리기 함수를 불러온다
from escalation import needs_escalation, escalate_ticket                              # 5교시에 만든 올리기 함수를 불러온다
from shift_metrics import average, collect_response_times, collect_resolve_times, count_sla_breaches  # 방금 만든 계산 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                 # 오늘 오전 알림 파일을 읽는다
events = load_json("status_events.json")                                              # 담당자의 동작 기록을 읽는다
rules = load_json("config/escalation_rules.json")                                     # 규칙 파일을 읽는다
tickets = []                                                                          # 만든 티켓을 저장할 빈 리스트

print("--- 단계 1: 가상 근무 0분부터 180분까지 (알림", len(alerts), "건 · 담당자 동작", len(events), "건)")  # 단계 1 시작을 알리는 줄
for now in range(0, 181):                                                             # 지금 시각을 0 분부터 180 분까지 1분씩 꺼낸다
    for alert in alerts:                                                              # 알림을 하나씩 읽는다
        if alert["minute"] == now:                                                    # 이 시각에 온 알림이면
            ticket, action = handle_alert(alert, tickets, rules)                      # 알림을 처리하고 티켓과 처리 방식을 받는다
            result = send_ticket_notice(ticket, now, rules)                           # 담당자에게 알린다
            print("[" + str(now) + "분]", alert["id"], "→", ticket["id"], action, "· 알리기", result)  # 알림 처리 결과를 출력한다
    for event in events:                                                              # 담당자의 동작을 하나씩 읽는다
        if event["minute"] == now:                                                    # 이 시각에 한 동작이면
            for ticket in tickets:                                                    # 티켓을 하나씩 읽는다
                if ticket["id"] == event["ticket"]:                                   # 동작 대상 티켓이면
                    change_ticket_status(ticket, event["status"], now, event["who"])  # 상태를 바꾼다
                    print("[" + str(now) + "분]", ticket["id"], "→", event["status"], "·", event["who"])  # 담당자의 동작을 출력한다
    if now % 10 == 0:                                                                 # 10분마다 (10 으로 나눈 나머지가 0 이면)
        for ticket in tickets:                                                        # 티켓을 하나씩 읽는다
            if needs_escalation(ticket, now):                                         # 상급자에게 올릴 티켓이면
                result = escalate_ticket(ticket, now, rules)                          # 상급자에게 올린다
                if result != "그대로":                                                # 새로 올렸거나 실패했으면
                    print("[" + str(now) + "분]", ticket["id"], "상급자에게", result, "· 올림 단계", ticket["escalation_level"])  # 올린 결과를 출력한다

print("--- 단계 2: 근무 지표")                                                        # 단계 2 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. collect_response_times(tickets) 의 결과를 ack_times 에 저장한다
# 9. average(ack_times) 의 결과를 mtta 에 저장한다
resolve_times = collect_resolve_times(tickets)                                        # 해결한 티켓의 걸린 시간 리스트 — 미리 채운 줄
mttr = average(resolve_times)                                                         # 평균 해결 시간(MTTR) — 미리 채운 줄
late_count = count_sla_breaches(tickets, 180)                                         # 응답 기한을 넘긴 티켓 수 — 미리 채운 줄
print("티켓", len(tickets), "장 · 확인한 티켓", len(ack_times), "장 · 해결한 티켓", len(resolve_times), "장")  # 티켓 수를 출력한다
print("평균 확인 시간(MTTA):", mtta, "분")                                            # 평균 확인 시간을 출력한다
print("평균 해결 시간(MTTR):", mttr, "분")                                            # 평균 해결 시간을 출력한다
print("응답 기한을 넘긴 티켓:", late_count, "장")                                     # 응답 기한을 넘긴 티켓 수를 출력한다

print("--- 단계 3: 다음 근무자에게 넘길 티켓 (해결되지 않은 티켓)")                   # 단계 3 시작을 알리는 줄
for ticket in tickets:                                                                # 티켓을 하나씩 읽는다
    if ticket["status"] != "해결":                                                    # 해결되지 않은 티켓이면
        print(ticket["id"], ticket["title"], "· 상태", ticket["status"], "·", ticket["next_step"])  # 티켓과 다음 할 일을 출력한다

save_json(tickets, "shift_tickets.json")                                              # 근무가 끝난 티켓을 파일에 저장한다
saved = load_json("shift_tickets.json")                                               # 저장한 파일을 다시 읽는다
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")                             # 단계 4 시작을 알리는 줄과 장수
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch shift_metrics.py day04_6-1_run.py
   ls
   ```
2. **[VS Code]** `shift_metrics.py` 1 ~ 7번, `day04_6-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「6교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`). 알림 서버 터미널은 켜 둡니다.
   ```bash
   python day04_6-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 22줄(알림 11줄 · 담당자 동작 8줄 · 상급자에게 올림 3줄), 단계 2 는 4줄, 단계 3 은 4줄(해결되지 않은 티켓 4장)입니다. 단계 4 는 제목 줄 하나뿐이고 저장한 티켓 수가 그 줄 안에 있습니다. <mark style="background:#bde3ff">6교시를 실행하면 알림 서버 터미널에 새로 출력되는 `[알림 받음]` 줄이 12개입니다.</mark> 5교시의 4줄 아래에 이어서 나오므로 터미널 전체로는 16줄입니다.
5. **[보고서]** `day04_pm_report.md` 의 `## 6교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣어 주세요. 그리고 그 출력에서 MTTA(평균 확인 시간) · MTTR(평균 해결 시간) · 응답 기한을 넘긴 티켓 수(응답 기한 위반 수)를 찾아 적어 주세요.
   - (나) 🔍 확인된 티켓 `TCK-1` · `TCK-3` · `TCK-4` · `TCK-6` · `TCK-7` 의 확인 시간(확인 시각 − 생성 시각)을 각각 계산하고, 그 평균인 MTTA(평균 확인 시간)를 직접 계산해 적어 주세요. 또한 미확인 티켓인 `TCK-2` · `TCK-5` 를 평균에서 제외하는 이유도 설명해 주세요.
   - (다) 🔍 응답 기한을 위반한 티켓 2장이 어느 티켓인지 적어 주세요. 이때 각 티켓의 `sla_due` 와 확인 시각을 근거로 씁니다. 그리고 단계 1 의 70분 · 80분 · 110분에 출력된 줄(상급자에게 올림 · 확인 중)이 이 두 티켓과 어떤 관계인지 설명해 주세요.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 개수가 0 이면 | `if len(numbers) == 0:` |
| 합계를 개수로 나누기 | `return sum(numbers) / len(numbers)` |
| 값이 -1 이 아니면 | `if ticket["acked_at"] != -1:` |
| 리스트에 추가 | `times.append(ticket["acked_at"] - ticket["created_at"])` |
| 보다 늦으면 | `if checked_time > ticket["sla_due"]:` |
| 1 늘려 다시 저장 | `late = late + 1` |
| 함수 결과를 변수에 저장 | `mtta = average(ack_times)` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아닙니다. 오늘 구현한 코드를 원격 저장소(remote repository, 리모트 리포지토리: 깃허브에 있는 저장소)에 반영하는 마무리입니다.</mark> 6교시 마지막 약 10분에 진행합니다. 알림 서버를 켜지 않은, 처음 쓰던 터미널에서 진행합니다. 먼저 `pwd` 로 위치를 확인하고, 결과가 `soar_response` 로 끝나면 아래 1번의 `cd ..` 를 실행합니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「오늘 구현한 티켓 생성 · 병합 · 통지 · 에스컬레이션 · 지표 산출 코드를 저장소에 보관해 달라」고 요청합니다</mark>.
- **진행 내용**: 먼저 `git status` 로 반영할 파일을 점검합니다. `.env` 같은 비밀 키(API 키) 파일이 포함되면 누구나 볼 수 있게 공개되어 보안 사고가 되므로 반드시 제외합니다. 점검한 뒤 `git add` → `git commit` → `git push` 순서로 반영합니다.
- **끝나면**: 깃허브 저장소의 `soar_response` 폴더에 `ticketing.py` · `ticket_merge.py` · `ticket_notice.py` · `escalation.py` · `shift_metrics.py` 가 보입니다.

**순서**

0. **[터미널]** 오늘 구현한 파일이 있는지 `soar_response` 폴더에서 점검합니다. 두 명령을 하나씩 실행합니다. 이 단계에서 보고서도 점검합니다. `day04_am_report.md` 와 `day04_pm_report.md` 의 모든 질문에서 `답:` 뒤와 코드 상자가 모두 작성되었는지 확인합니다(마무리 (가)는 3번에서 작성합니다).

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
   - 나오는 것: `ticketing.py` · `ticket_merge.py` · `ticket_notice.py` · `escalation.py` · `shift_metrics.py` · `config` 가 보이면 됩니다.

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

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark style="background:#ffc4d6">빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 않습니다.</mark> `.env` 는 API 키가 들어 있어 공개되면 안 되는 파일이고, `.venv` 는 크기가 커서 올릴 필요가 없는 가상환경 폴더입니다. 이때 아래 안내대로 `.gitignore`(깃이 올리지 않을 파일 이름을 적어 두는 파일)를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다. `soar_response/` 아래의 새 파일들이 보이면 됩니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `soar_response/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.

3. **[보고서]** `day04_pm_report.md` 의 `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 작성합니다. <mark>반영하기 전에 작성해야</mark> 깃허브에 빈 답이 없는 상태로 올라갑니다.
   - (가) `git status` 를 실행했을 때 `.env` 나 `.venv` 가 목록에 표시되었는지, 표시되었다면 어떤 조치를 했는지 적어 주세요.
   - <mark>앞 교시에서 답하지 못한 보고서 질문이 있으면 `모름 — 막힌 곳: …` 으로 적고 push 합니다.</mark> push 한 뒤에 이어서 작성하여 다시 push 해도 됩니다.
4. **[터미널]** 바뀐 파일을 올릴 목록에 추가하고(`add`), 설명을 붙여 저장하고(`commit`), 깃허브로 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 올릴 목록에 추가합니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 이번에 올릴 목록에 추가합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add ticketing, escalation and shift metrics"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark style="background:#ffc4d6">`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull --no-rebase`(깃허브의 새 기록을 내 PC 로 받아 와 합치는 명령)를 입력한 뒤 `git push` 를 다시 합니다.
   - 편집기 화면이 뜨면 `Esc` → `:wq`(저장하고 나가기) → `Enter` 를 합니다.
   - `git pull` 만 입력했을 때 `fatal: Need to specify how to reconcile divergent branches` 가 나오면, 내 기록과 깃허브 기록이 갈라졌다는 뜻이므로 `git pull --no-rebase` 를 입력합니다.

5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `soar_response` 폴더를 열고, VS Code 왼쪽 목록의 `soar_response` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
   - 깃허브에 안 보이는 파일이 있으면, 먼저 VS Code 왼쪽 목록의 `soar_response` 폴더 안에 그 파일이 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `soar_response` 안으로 옮기고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.
6. **[터미널]** 알림 서버 터미널을 `Ctrl + C` 로 끕니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `soar_response` 폴더와 파일이 있는지 확인 |

---

## 오늘 오후 마무리

| 달성 기준 | 문제 |
|---|---|
| 응답 기한이 초과된 열림 상태 티켓을 초과 시간에 맞는 단계로 에스컬레이션했다 | 오후 5-1 |
| 근무 3시간 시뮬레이션을 실행하고 MTTA · MTTR · 응답 기한 위반 수를 산출했다 | 오후 6-1 |
| 오늘 구현한 파일과 보고서를 깃허브에 반영했다 | 마무리 |

**강의계획서 평가 기준 확인**

| 기준 | 확인할 곳 |
|---|---|
| 티켓 생성 시 플레이북(playbook, 플레이북: 사건 종류별로 정해 둔 대응 순서) · 조치 내역이 자동으로 반영된다 | 오전 2교시 단계 3 (TCK-1 의 조치 내역), 티켓의 `playbook` · `done` |
| 에스컬레이션이 응답 기한(SLA) 기준에 따라 해당 단계의 상급자에게 통보된다 | 오후 5교시 단계 2 · 3 (기한을 넘긴 시간과 올림 단계), 6교시 단계 1 의 70분 · 80분 · 110분 줄 |
| 1과목 알림 함수가 재사용되었다 | 오전 4교시 `ticket_notice.py` 의 `notify` (1과목 `notifier.py`), 알림 서버 터미널의 `[알림 받음]` |

오늘은 알림 서버(연습용 시스템)로 검증했습니다. <mark>실제 제품에서는 `notify` 가 알림 서버가 아니라 메신저 · 호출기(pager, 페이저: 담당자를 호출하는 알림 장치) · 티켓 관리 도구로 통지를 전송하는 경우가 많습니다.</mark> 응답 기한 계산, 에스컬레이션 단계, MTTA · MTTR 계산 방식은 그대로 적용됩니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

아래 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.** 알림 서버 터미널은 켜 둔 채, 처음 쓰던 터미널에서 실행합니다.

```bash
pwd
python day04_5-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`escalation.py` 의 1 ~ 6번입니다.

```python
    # 1. now 에서 ticket["sla_due"] 를 뺀 값을 리턴한다
    return now - ticket["sla_due"]              # 지금 시각에서 응답 기한 시각을 뺀 값을 리턴한다
    # 2. ticket 의 "status" 가 "열림" 이 아니면 (if, !=)
    if ticket["status"] != "열림":              # 이미 확인 중이거나 해결한 티켓이면
    # 3.   False 를 리턴한다
        return False                            # 올리지 않는다고 False 를 리턴한다
    # 4. overdue_minutes(ticket, now) 가 0 이상인지(>=)의 결과를 리턴한다
    return overdue_minutes(ticket, now) >= 0    # 기한이 지났는지의 결과를 리턴한다
        # 5. overdue 가 step 의 "overdue_minutes" 이상이면 (if, >=)
        if overdue >= step["overdue_minutes"]:  # 넘긴 시간이 이 단계의 기준 이상이면
            # 6. level 에 index + 1 을 저장한다
            level = index + 1                   # 이 단계 번호를 담는다 (뒤의 더 높은 단계가 덮어쓴다)
```

`day04_5-1_run.py` 의 7 ~ 9번입니다.

```python
        # 7. needs_escalation(ticket, now) 가 참이면 (if)
        if needs_escalation(ticket, now):                 # 상급자에게 올릴 티켓이면
            # 8. escalate_ticket(ticket, now, rules) 의 결과를 result 에 저장한다
            result = escalate_ticket(ticket, now, rules)  # 상급자에게 올리고 결과를 받는다
                # 9. escalated_count 에 escalated_count + 1 을 저장한다 (1 늘린다)
                escalated_count = escalated_count + 1     # 올린 횟수를 1 늘린다
```

위 줄만 보면 들여쓰기가 헷갈리니 완성된 모양을 함께 봅니다. 7번의 `if` 아래에는 8번 줄과 미리 채운 세 줄이 들어갑니다. 9번은 미리 채운 `if result == "올림":` 아래에 들어갑니다.

**전체 모양 — 점검 반복 부분**

```python
for now in [20, 60, 110]:                                           # 점검할 시각(분)을 하나씩 읽는다
    print("[" + str(now) + "분] 점검")                              # 점검 시각을 출력한다
    for ticket in tickets:                                          # 티켓을 하나씩 읽는다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        if needs_escalation(ticket, now):                           # 상급자에게 올릴 티켓이면
            result = escalate_ticket(ticket, now, rules)            # 상급자에게 올리고 결과를 받는다
            overdue = overdue_minutes(ticket, now)                  # 기한을 얼마나 넘겼는지 구한다 — 미리 채운 줄
            print(ticket["id"], ticket["title"], "→", result, "· 기한을", overdue, "분 넘김 · 올림 단계", ticket["escalation_level"])  # 결과를 출력한다 — 미리 채운 줄
            if result == "올림":                                    # 올렸으면 — 미리 채운 줄
                escalated_count = escalated_count + 1               # 올린 횟수를 1 늘린다
    if now == 20:                                                   # 20분 점검이 끝나면 — 미리 채운 줄
        change_ticket_status(tickets[0], "확인 중", 25, "kim.sec")  # 25분에 kim.sec 이 TCK-1 을 확인하기 시작한다 — 미리 채운 줄
        print("[25분] TCK-1 → 확인 중 · kim.sec")                   # 담당자의 동작을 출력한다 — 미리 채운 줄
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 3 의 올린 횟수(에스컬레이션 실행 횟수)는 <mark style="background:#bde3ff">**4번**</mark>입니다.

```
--- 단계 1: 불러온 티켓 7 장 · 올림 단계 2 개
--- 단계 2: 점검 시각마다 상급자에게 올릴 티켓 찾기
[20분] 점검
TCK-1 [high] dami — 퇴사한 계정 → 올림 · 기한을 5 분 넘김 · 올림 단계 1
[25분] TCK-1 → 확인 중 · kim.sec
[60분] 점검
[110분] 점검
TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 → 올림 · 기한을 42 분 넘김 · 올림 단계 2
TCK-4 [mid] seoyeon — 대량 다운로드 → 올림 · 기한을 38 분 넘김 · 올림 단계 2
TCK-6 [mid] hana — 업무 시간 밖 로그인 → 올림 · 기한을 15 분 넘김 · 올림 단계 1
--- 단계 3: 올린 결과 요약 (올린 횟수 4 번)
TCK-1 올림 단계 1 · 상태 확인 중
TCK-3 올림 단계 2 · 상태 열림
TCK-4 올림 단계 2 · 상태 열림
TCK-6 올림 단계 1 · 상태 열림
```

알림 서버 터미널에는 `[알림 받음]` 줄이 <mark style="background:#bde3ff">**4개**</mark> 찍힙니다.

```
[알림 받음] [올림 1단계] TCK-1 [high] dami — 퇴사한 계정 · 기한을 5분 넘김 · 받는 사람: team.lead
[알림 받음] [올림 2단계] TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 기한을 42분 넘김 · 받는 사람: soc.head
[알림 받음] [올림 2단계] TCK-4 [mid] seoyeon — 대량 다운로드 · 기한을 38분 넘김 · 받는 사람: soc.head
[알림 받음] [올림 1단계] TCK-6 [mid] hana — 업무 시간 밖 로그인 · 기한을 15분 넘김 · 받는 사람: team.lead
```

- (나) `TCK-1` 은 응답 기한(15분)이 지난 20분 점검에서 5분을 초과했으므로 1단계로 에스컬레이션되었습니다. 그 뒤 25분에 `kim.sec` 이 상태를 `확인 중` 으로 변경했습니다.
  - 60분 점검에서 `TCK-1` 의 상태는 `확인 중` 입니다. `needs_escalation` 은 상태가 `열림` 이 아니면 `False` 를 리턴하므로 <mark style="background:#bde3ff">에스컬레이션하지 않았습니다.</mark>
  - 이 조건이 없으면 담당자가 이미 확인 중인 티켓도 점검할 때마다 상급자에게 통보됩니다. 그러면 불필요한 알림이 늘어나고, 상급자가 알림 피로를 겪어 알림을 무시하게 됩니다.
- (다) 110분 점검에서 `TCK-3` 은 응답 기한 시각이 68분이므로 110 − 68 = 42분을 초과하여 <mark style="background:#bde3ff">2단계</mark>로 에스컬레이션되었습니다. `TCK-6` 은 응답 기한 시각이 95분이므로 110 − 95 = 15분을 초과하여 <mark style="background:#bde3ff">1단계</mark>로 에스컬레이션되었습니다.
  - <mark style="background:#ffdcb0">응답 기한 초과 시간이 30분 이상이면 2단계(`soc.head`, 관제 센터장), 0분 이상 30분 미만이면 1단계(`team.lead`, 팀장)</mark>입니다. <mark style="background:#bde3ff">42분은 30분 이상이므로 2단계이고, 15분은 30분 미만이므로 1단계입니다</mark>.
  - `TCK-2` 는 등급 low 이므로 응답 기한 시각이 243분입니다. 110분은 그보다 이르므로 초과 시간이 110 − 243 = −133분으로 음수입니다. 응답 기한이 아직 지나지 않았으므로 에스컬레이션 대상이 아닙니다.

**왜**

- <mark>에스컬레이션은 「확인되지 않은 티켓이 방치되어 응답 기한을 위반하는 일」을 막는 절차입니다.</mark> `열림` 상태인 티켓만 에스컬레이션하고 같은 단계는 한 번만 실행해야 불필요한 알림이 늘어나지 않습니다. 그래야 알림 피로 없이 상급자가 실제로 필요한 알림에 반응할 수 있습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1번을 비워 두면 `None`(값이 없다는 뜻의 파이썬 값)이 리턴되어 기한을 비교하는 줄에서 오류가 납니다.

```
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

- 2 · 3번을 비워 두면 <mark style="background:#ffc4d6">**확인 중인 티켓도 반복해서 에스컬레이션됩니다.**</mark> 아래 출력이 그 결과입니다. 60분 점검에서 `TCK-1` 이 2단계로 에스컬레이션되고, 110분 점검에서도 `TCK-1` 의 출력 줄이 나옵니다.

```
[60분] 점검
TCK-1 [high] dami — 퇴사한 계정 → 올림 · 기한을 45 분 넘김 · 올림 단계 2
[110분] 점검
TCK-1 [high] dami — 퇴사한 계정 → 그대로 · 기한을 95 분 넘김 · 올림 단계 2
```

- 3번만 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError`(들여쓰기가 맞지 않다는 오류)로 시작하는 오류입니다(문구는 파이썬 버전마다 조금 다릅니다).

```
IndentationError: expected an indented block
```

- 4번을 비워 두면 `needs_escalation` 이 값을 리턴하지 않아(`None`) <mark style="background:#ffc4d6">**에스컬레이션이 한 건도 실행되지 않습니다.**</mark> 단계 3 의 올린 횟수가 0번으로 출력되는 것이 이 실수의 결과입니다.

```
--- 단계 3: 올린 결과 요약 (올린 횟수 0 번)
```

- 5번을 비워 두면 6번의 줄이 `if` 없이 들여쓰기만 남아 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 6번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다.

```
IndentationError: expected an indented block
```

- 7번을 비워 두면 <mark style="background:#ffc4d6">**기한 이전의 티켓도 모두 처리 대상이 됩니다.**</mark> 응답 기한에 도달하지 않은 티켓의 줄이 음수의 초과 시간과 함께 출력되는 것이 이 실수의 결과입니다.

```
[20분] 점검
TCK-1 [high] dami — 퇴사한 계정 → 올림 · 기한을 5 분 넘김 · 올림 단계 1
TCK-2 [low] 198.51.100.90 — 경로 스캔 → 그대로 · 기한을 -223 분 넘김 · 올림 단계 0
```

- 8번을 비워 두면 `result` 가 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'result' is not defined
```

- 9번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다.

```
IndentationError: expected an indented block
```

- 알림 서버를 켜지 않고 실행하면 코드는 정상이어도 <mark style="background:#ffc4d6">**상급자에게 통보하지 못합니다.**</mark> 단계 2 의 시작이 이렇게 출력되면 알림 서버가 실행 중이 아닌 것입니다.

```
--- 단계 2: 점검 시각마다 상급자에게 올릴 티켓 찾기
[20분] 점검
[알림 실패] ConnectionError
[알림 실패] ConnectionError
[알림 실패] ConnectionError
```

**관제에서는**

- 에스컬레이션 규칙(escalation policy, 에스컬레이션 폴리시: 어느 시점에 누구에게 통보할지 정한 규칙)은 「응답 기한 초과 시간이 몇 분이면 누구에게 통보하는가」를 표로 정의해 둡니다. 이 표가 있으면 사람이 판단하지 않아도 상위 단계에 자동으로 통보하도록 설정할 수 있습니다. <mark>이미 담당자가 확인 중인 티켓은 에스컬레이션하지 않는 것</mark>이 기본 설계입니다. 이렇게 하면 불필요한 알림이 늘어나 상급자가 알림을 무시하게 되는 일(알림 피로)을 줄일 수 있습니다. <mark style="background:#ffdcb0">오늘의 0분 · 30분 기준은 예시입니다</mark>.

---

### 정답 6-1

💻 **터미널에 입력합니다.** 알림 서버 터미널은 켜 둔 채, 처음 쓰던 터미널에서 실행합니다.

```bash
pwd
python day04_6-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`shift_metrics.py` 의 1 ~ 7번입니다.

```python
    # 1. numbers 의 개수(len)가 0 이면 (if, ==)
    if len(numbers) == 0:                                            # 숫자가 하나도 없으면
    # 2.   0 을 리턴한다 (비어 있으면 나눌 수 없다)
        return 0                                                     # 0 을 리턴한다
    # 3. sum(numbers) / len(numbers) 를 리턴한다 (합계를 개수로 나눈다)
    return sum(numbers) / len(numbers)                               # 합계를 개수로 나눈 평균을 리턴한다
        # 4. ticket 의 "acked_at" 이 -1 이 아니면 (if, !=)
        if ticket["acked_at"] != -1:                                 # 담당자가 확인한 티켓이면
            # 5. times 리스트에 ticket["acked_at"] - ticket["created_at"] 을 추가한다 (append)
            times.append(ticket["acked_at"] - ticket["created_at"])  # 확인까지 걸린 시간을 추가한다
        # 6. checked_time 이 ticket 의 "sla_due" 보다 크면 (if, >)
        if checked_time > ticket["sla_due"]:                         # 확인한 시각이 응답 기한 시각보다 늦으면
            # 7. late 에 late + 1 을 저장한다 (1 늘린다)
            late = late + 1                                          # 기한을 넘긴 티켓 수를 1 늘린다
```

`day04_6-1_run.py` 의 8 · 9번입니다.

```python
# 8. collect_response_times(tickets) 의 결과를 ack_times 에 저장한다
ack_times = collect_response_times(tickets)  # 확인까지 걸린 시간 리스트를 만든다
# 9. average(ack_times) 의 결과를 mtta 에 저장한다
mtta = average(ack_times)                    # 평균 확인 시간(MTTA)을 구한다
```

**결과**

- (가) 출력은 다음과 같습니다. MTTA(평균 확인 시간)는 <mark style="background:#bde3ff">**55.0분**</mark>, MTTR(평균 해결 시간)은 <mark style="background:#bde3ff">**84.0분**</mark>, 응답 기한을 넘긴 티켓(응답 기한 위반)은 <mark style="background:#bde3ff">**2장**</mark>입니다.

```
--- 단계 1: 가상 근무 0분부터 180분까지 (알림 11 건 · 담당자 동작 8 건)
[0분] INC-201 → TCK-1 새 티켓 · 알리기 전송
[3분] INC-202 → TCK-2 새 티켓 · 알리기 전송
[8분] INC-203 → TCK-3 새 티켓 · 알리기 전송
[10분] TCK-1 → 확인 중 · kim.sec
[12분] INC-204 → TCK-4 새 티켓 · 알리기 전송
[14분] INC-205 → TCK-1 병합 · 알리기 건너뜀
[20분] INC-206 → TCK-2 병합 · 알리기 건너뜀
[30분] INC-207 → TCK-5 새 티켓 · 알리기 전송
[35분] INC-208 → TCK-6 새 티켓 · 알리기 전송
[40분] INC-209 → TCK-1 병합 · 알리기 전송
[45분] TCK-1 → 해결 · kim.sec
[70분] TCK-3 상급자에게 올림 · 올림 단계 1
[80분] TCK-3 → 확인 중 · lee.soc
[80분] TCK-4 상급자에게 올림 · 올림 단계 1
[90분] TCK-6 → 확인 중 · kim.sec
[95분] INC-210 → TCK-7 새 티켓 · 알리기 전송
[105분] TCK-7 → 확인 중 · kim.sec
[110분] TCK-4 상급자에게 올림 · 올림 단계 2
[120분] TCK-3 → 해결 · lee.soc
[130분] TCK-6 → 해결 · kim.sec
[140분] TCK-4 → 확인 중 · lee.soc
[160분] INC-211 → TCK-7 병합 · 알리기 전송
--- 단계 2: 근무 지표
티켓 7 장 · 확인한 티켓 5 장 · 해결한 티켓 3 장
평균 확인 시간(MTTA): 55.0 분
평균 해결 시간(MTTR): 84.0 분
응답 기한을 넘긴 티켓: 2 장
--- 단계 3: 다음 근무자에게 넘길 티켓 (해결되지 않은 티켓)
TCK-2 [low] 198.51.100.90 — 경로 스캔 · 상태 열림 · 조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다
TCK-4 [mid] seoyeon — 대량 다운로드 · 상태 확인 중 · 승인할지 거절할지 정하고 정한 사람의 이름을 남긴다
TCK-5 [low] 203.0.113.250 — 경로 스캔 · 상태 열림 · 조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다
TCK-7 [high] dami — 퇴사한 계정 · 상태 확인 중 · 조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다
--- 단계 4: 파일에 저장된 티켓 7 장
```

알림 서버 터미널에는 `[알림 받음]` 줄이 <mark style="background:#bde3ff">**12개**</mark> 찍힙니다(담당자에게 알린 9개와 상급자에게 올린 3개).

```
[알림 받음] [high] dami — 퇴사한 계정 · TCK-1 · 알림 1건 · 기한 15분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [low] 198.51.100.90 — 경로 스캔 · TCK-2 · 알림 1건 · 기한 243분 · 수신: kim.sec
[알림 받음] [mid] gaeun — 규칙은 허용인데 서버가 거절 · TCK-3 · 알림 1건 · 기한 68분 · 수신: kim.sec, lee.soc
[알림 받음] [mid] seoyeon — 대량 다운로드 · TCK-4 · 알림 1건 · 기한 72분 · 수신: kim.sec, lee.soc
[알림 받음] [low] 203.0.113.250 — 경로 스캔 · TCK-5 · 알림 1건 · 기한 270분 · 수신: kim.sec
[알림 받음] [mid] hana — 업무 시간 밖 로그인 · TCK-6 · 알림 1건 · 기한 95분 · 수신: kim.sec, lee.soc
[알림 받음] [high] dami — 퇴사한 계정 · TCK-1 · 알림 3건 · 기한 15분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [올림 1단계] TCK-3 [mid] gaeun — 규칙은 허용인데 서버가 거절 · 기한을 2분 넘김 · 받는 사람: team.lead
[알림 받음] [올림 1단계] TCK-4 [mid] seoyeon — 대량 다운로드 · 기한을 8분 넘김 · 받는 사람: team.lead
[알림 받음] [high] dami — 퇴사한 계정 · TCK-7 · 알림 1건 · 기한 110분 · 수신: kim.sec, lee.soc, team.lead
[알림 받음] [올림 2단계] TCK-4 [mid] seoyeon — 대량 다운로드 · 기한을 38분 넘김 · 받는 사람: soc.head
[알림 받음] [high] dami — 퇴사한 계정 · TCK-7 · 알림 2건 · 기한 110분 · 수신: kim.sec, lee.soc, team.lead
```

- (나) 확인한 티켓 5장의 확인 시간은 다음과 같습니다.
  - `TCK-1` 10 − 0 = 10분, `TCK-3` 80 − 8 = 72분, `TCK-4` 140 − 12 = 128분, `TCK-6` 90 − 35 = 55분, `TCK-7` 105 − 95 = 10분입니다.
  - 합계 275분을 5로 나누면 <mark style="background:#bde3ff">55.0분</mark>입니다.
  - `TCK-2` 와 `TCK-5` 는 아직 확인되지 않아 확인 시간 값이 없습니다(결측값, missing value: 아직 측정되지 않은 값). 이 값을 0분으로 넣으면 MTTA 가 실제보다 낮아져 대응이 빠른 것처럼 왜곡됩니다.
- (다) 응답 기한을 위반한 티켓은 <mark style="background:#bde3ff">`TCK-3`</mark>(응답 기한 시각 68분, 80분에 확인)과 <mark style="background:#bde3ff">`TCK-4`</mark>(응답 기한 시각 72분, 140분에 확인)입니다. 각각 12분, 68분 늦게 확인되었습니다.
  - `TCK-3` 은 70분 점검에서 1단계로 에스컬레이션되었고, 80분에 `lee.soc` 이 확인했습니다.
  - `TCK-4` 는 80분에 1단계, 110분에 2단계로 에스컬레이션되었고, 140분에야 확인되었습니다.
  - 오늘 샘플에서는 에스컬레이션된 티켓(`TCK-3` · `TCK-4`)과 응답 기한 위반 티켓이 같습니다. 그러나 두 집합은 항상 같지는 않습니다. 에스컬레이션 대상은 응답 기한을 초과한 뒤 점검 시각까지 `열림` 으로 남은 티켓이고, 응답 기한 위반은 확인 시각이 기한 시각보다 늦은 티켓이기 때문입니다. 예를 들어 기한을 넘긴 뒤 다음 점검 전에 확인된 티켓은 에스컬레이션되지 않지만 위반으로는 집계됩니다.

**왜**

- <mark>MTTA · MTTR · 응답 기한 위반 수는 「팀이 얼마나 빨리 대응했는가」를 정량적으로 보여 줍니다.</mark> 지표가 있으면 두 가지를 근거를 가지고 판단할 수 있습니다. 하나는 어느 시간대에 인력이 부족한지이고, 다른 하나는 정한 응답 기한이 너무 짧거나 길지 않은지입니다.
- 비어 있는 리스트로 평균을 구하면 0 으로 나누는 오류(`ZeroDivisionError`)가 발생합니다. 확인된 티켓이 하나도 없는 날이 있을 수 있으므로 `average` 가 먼저 개수를 검사합니다. 이처럼 예외 상황을 미리 대비하는 작성 방식을 방어적 프로그래밍(defensive programming)이라고 합니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 지우고 실행한 것입니다.

- 1 · 2번을 비워 두면 오늘 샘플에서는 오류가 나지 않습니다. 하지만 숫자가 하나도 없는 리스트로 평균을 구하는 날에는 `ZeroDivisionError`(0 으로 나누었다는 오류)가 납니다.
- 3번을 비워 두면 평균이 `None` 으로 나옵니다.

```
평균 확인 시간(MTTA): None 분
평균 해결 시간(MTTR): None 분
```

- 4번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**미확인 티켓까지 평균에 포함됩니다.**</mark> 그 결과 확인한 티켓이 5장이 아니라 7장으로 계산되고 평균도 달라집니다.

```
티켓 7 장 · 확인한 티켓 7 장 · 해결한 티켓 3 장
평균 확인 시간(MTTA): 34.285714285714285 분
```

- 5번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. `IndentationError` 로 시작하는 오류입니다.

```
IndentationError: expected an indented block
```

- 6 · 7번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**응답 기한 위반이 0장으로 집계됩니다.**</mark>

```
응답 기한을 넘긴 티켓: 0 장
```

- 7번만 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다.

```
IndentationError: expected an indented block
```

- 8번을 비워 두면 `ack_times` 가 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'ack_times' is not defined
```

- 9번을 비워 두면 `mtta` 가 만들어지지 않아 오류가 납니다. 파이썬 버전에 따라 뒤에 `Did you mean: …` 이 더 붙을 수 있습니다.

```
NameError: name 'mtta' is not defined
```

**관제에서는**

- 근무 교대 인계(shift handoff) 보고에는 보통 두 가지를 포함합니다. 하나는 MTTA · MTTR · 응답 기한 위반 수이고, 다른 하나는 <mark>다음 근무자에게 인계할 미해결 티켓 목록</mark>(티켓마다 현재 상태와 다음 조치)입니다. 평균은 표본 크기(티켓 수)와 함께 보고합니다. 오늘의 숫자는 근무 3시간 시뮬레이션의 예시입니다.
