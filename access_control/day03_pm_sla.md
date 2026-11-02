# 10/23(금) 오후 · 3과목 접근통제 ④ — 요청 처리 기한(SLA) 점검 · 요청 이력 저장 — 실습

오전에는 요청을 요청서로 접수하고(`req_create.py`), 승인 · 반려하고(`req_review.py`), 정책으로 확인해 예외 권한을 부여하는(`req_grant.py`) 흐름을 만들었습니다. 오후에는 그 흐름이 **정해진 시간 안에** 처리되는지 점검하고, 요청서를 **파일로 저장**해 이력(처리 기록)으로 남깁니다.

- **5교시**: 접수한 지 정해진 시간(SLA, 처리 기한)이 지났는데도 처리되지 않은 요청서를 찾는다.
- **6교시**: 요청서 전체를 `requests.json` 으로 저장하고, 상태별 건수를 센다. 마지막 10분에 오늘 만든 것을 깃허브에 올린다.

오늘 오후는 5 · 6교시이고 7교시는 없습니다. 교시마다 문제는 하나이고, 그 안에서 단계를 나눠 질문에 답합니다. 깃허브에 올리는 일은 6교시 마지막에 합니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 오전 파일을 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   python -c "from rbac import check_permission; from exception_policy import EXCEPTIONS; from config_loader import load_json; from req_grant import grant_request; print('오전 파일 정상')"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다.
   - `req_create.py` · `req_review.py` · `req_grant.py` · `config_loader.py` 가 보이고, 마지막 줄에 `오전 파일 정상` 이 나와야 합니다.
   - 아니면 오전 문서(`day03_am_request.md`) 맨 아래 「앞 교시 파일 완성본」으로 `req_create.py` · `req_review.py` · `req_grant.py` 를 먼저 만듭니다. `rbac.py` · `exception_policy.py` · `config_loader.py` 가 없으면 수업 자료로 받은 `day02_recovery` 폴더에서 `access_control` 폴더로 넣습니다. 마지막 줄을 다시 칩니다.
3. **[VS Code]** **오후에 받은 파일 두 개를 `access_control` 폴더로 옮깁니다.** 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day03_pm_sla.md` (이 파일) — 오후 실습 안내. 읽기만 합니다.
   - `day03_pm_report.md` — **오후 보고서.** 5 · 6교시와 마무리 답을 여기에 적습니다.
4. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day03_pm_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-23(금))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이유까지 설명해야 하는 핵심 질문입니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 **터미널**에서 합니다(VS Code 의 ▶ 단추를 쓰지 않습니다). `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **오전까지 만든 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 접수 후 4시간이 지나도 처리되지 않은 요청 찾기(SLA 점검)</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당(요청이 정해진 시간 안에 처리되는지 지켜보는 사람)이 보낸 메시지: 「요청서를 접수해 놓고 승인자가 처리를 미루는 일이 있습니다. 그러면 권한이 필요한 직원은 일을 못 하고 메신저로 계속 재촉합니다. 목록을 눈으로 훑어서는 오래된 요청을 놓치기 쉽습니다. 접수한 지 4시간이 지났는데도 아직 검토 중인 요청서를 찾아서 알려 주세요.」
> - 이 교시에서 하는 일: 접수한 지 정해진 시간(SLA, 오늘은 4시간)이 지났는데도 아직 검토 중인 요청서를 찾는 함수 `check_sla_breach` 를 직접 씁니다. 요청서 여섯 장 가운데 어느 것이 몇 시간 지났는지 읽습니다.
> - 끝나면 쓰는 것: 보고서 (가)~(다) 답

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 요청은 접수한 뒤에 승인자가 봐 주어야 진행됩니다. 오래 방치되면 요청자의 업무가 막히고, 그사이에 요청자가 퇴사하거나 역할이 바뀌면 승인할 때의 판단도 달라집니다.
2. **SLA**(service level agreement · 서비스 레벨 어그리먼트)는 「이 일은 이 시간 안에 처리한다」는 처리 기한의 약속입니다. 오늘은 검토 중인 요청서를 접수 후 4시간 안에 처리하는 것으로 정합니다.
3. 기한을 초과한 요청서를 코드로 찾아 두면, 사람이 목록을 눈으로 훑지 않아도 매일 아침 알림을 보낼 수 있습니다.

### 📖 5.1 기한이 지났는지 가리는 방법

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- **어떤 요청서를 보나**: 아직 처리 중인 요청서, 즉 상태가 `reviewing`(검토 중)인 것만 봅니다. 이미 승인되거나 반려된 요청서는 처리가 끝났으므로 기한을 따지지 않습니다.
- **얼마나 지났나**: `지금 시각 − 접수 시각` 으로 구합니다. 이 값을 시간(hour) 단위 숫자로 바꿔서 SLA 시간(`SLA_HOURS`, 오늘은 4)과 비교합니다.
- **SLA 시간은 어디에 두나**: 코드에 4를 직접 쓰지 않고 `config/sla.json` 파일에 적어 두고 읽습니다. 그러면 기한을 4시간에서 2시간으로 바꿀 때 코드는 그대로 두고 파일만 고치면 됩니다.
- **파일은 어떻게 읽나**: 10/22(목)에 만든 `load_json` 으로 읽습니다. 파일이 없거나 깨졌을 때는 기본값 4를 씁니다.
- **기한이 지난 요청은 어떻게 하나**: 현업에서는 승인자의 윗사람이나 대리 승인자(승인자가 자리에 없을 때 대신 승인하는 사람)에게 넘깁니다. 이것을 **에스컬레이션**(escalation · 에스컬레이션)이라고 합니다. 오늘은 넘기는 일은 만들지 않고, 기한이 지난 요청을 찾는 데까지만 합니다.
- **`now` 이름**: 함수가 받는 `now` 는 **지금 시각**(datetime)입니다. 10/22(목)의 `evaluate_access` 의 `now` 와 같은 뜻입니다.

```
+---------------------------------+
| check_sla_breach(requests, now) |
+---------------------------------+
   |
   v
+---------------------------------------------------+
| breached = []  (기한을 초과한 요청서를 담을 목록) |
+---------------------------------------------------+
   |
   v
+-------------------------------------------------------------+
| 요청서를 하나씩 꺼낸다  (아래 판단을 요청서마다 되풀이한다) |
+-------------------------------------------------------------+
   |
   v
+-----------------------------+
| status 가 "reviewing" 인가? |
+-----------------------------+
   |
   +--> 아님 --> 다음 요청서로  (처리가 끝난 요청은 기한을 따지지 않는다)
   |
   v  맞음
+-----------------------------------------------------------------+
| 접수 시각을 시각으로 바꾸고, 지금까지 걸린 시간(hours)을 구한다 |
+-----------------------------------------------------------------+
   |
   v
+-------------------------------+
| hours 가 SLA_HOURS 보다 큰가? |
+-------------------------------+
   |
   +--> 아님 --> 다음 요청서로  (정확히 같으면 아직 초과가 아니다)
   |
   v  큼
+-----------------------------------------------------------------------+
| 요청서를 복사해 wait_hours 를 적고, breached 에 더한 뒤 다음 요청서로 |
+-----------------------------------------------------------------------+
   |
   v  모든 요청서를 꺼낸 뒤
breached 를 리턴한다
```

**🐍 문법 상자 — 걸린 시간을 시간 단위 숫자로 바꾸기**

- 시각 글자를 시각으로 바꾸는 `datetime.strptime(글자, 형식)` 은 10/22(목)에 쓴 것과 같습니다. 형식 글자 `"%Y-%m-%d %H:%M"` 은 `exception_policy.py` 의 `TIME_FORMAT` 에 이미 적혀 있어서 오늘은 그것을 불러다 씁니다. 아래 상자에서는 그 모양을 그대로 볼 수 있습니다.

**① 시각에서 시각을 빼면 「걸린 시간」이 나옵니다**

```python
from datetime import datetime                                       # 시각을 다루는 모듈에서 datetime 을 불러온다
requested = datetime.strptime("2026-10-23 09:15", "%Y-%m-%d %H:%M")   # 접수 시각
now = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")         # 지금 시각
gap = now - requested                                               # 시각에서 시각을 빼면 「걸린 시간」이 나온다
print(gap)                                                          # 시:분:초 모양이라 숫자처럼 비교할 수 없다
```

실행 결과:

```
4:45:00
```

- 걸린 시간은 `4:45:00` 처럼 「시:분:초」 모양입니다. 숫자가 아니라서 `SLA_HOURS`(4)와 `>` 로 비교할 수 없습니다.

**② `.total_seconds()` 로 걸린 시간을 초 단위 숫자로 바꿉니다**

```python
from datetime import datetime                                       # 시각을 다루는 모듈에서 datetime 을 불러온다
requested = datetime.strptime("2026-10-23 09:15", "%Y-%m-%d %H:%M")   # 접수 시각
now = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")         # 지금 시각
gap = now - requested                                               # 시각에서 시각을 빼면 「걸린 시간」이 나온다
print(gap.total_seconds())                                          # 걸린 시간을 전부 초로 센 숫자다(4시간 45분 = 17100초)
```

실행 결과:

```
17100.0
```

- `.total_seconds()` 는 걸린 시간을 전부 초로 세어 숫자로 줍니다. 4시간 45분은 4 × 3600 + 45 × 60 = 17100초입니다.
- 실제 코드에서는 `gap` 없이 한 줄로 `(now - requested).total_seconds()` 처럼 씁니다. 뺄셈을 괄호로 묶은 뒤에 `.total_seconds()` 를 붙이는 것입니다. 괄호 없이 `now - requested.total_seconds()` 로 쓰면 `requested` 에 먼저 `.total_seconds()` 가 붙어 오류가 납니다.

**③ 3600 으로 나눠 시간 단위 숫자로 만듭니다**

```python
from datetime import datetime                                       # 시각을 다루는 모듈에서 datetime 을 불러온다
requested = datetime.strptime("2026-10-23 09:15", "%Y-%m-%d %H:%M")   # 접수 시각
now = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")         # 지금 시각
gap = now - requested                                               # 시각에서 시각을 빼면 「걸린 시간」이 나온다
print(gap.total_seconds() / 3600)                                   # 1시간은 3600초라서, 나누면 시간 단위 숫자가 된다
```

실행 결과:

```
4.75
```

- 1시간은 3600초이므로 초 숫자를 3600 으로 나누면 시간 단위 숫자(4.75)가 됩니다. 이제 `SLA_HOURS` 와 비교할 수 있습니다.
- 3600 으로 나누는 것을 빼먹으면 숫자가 초 단위(17100.0)라서 항상 4보다 커집니다.
- 걸린 시간이 SLA 시간보다 「큰」 것만 초과로 셉니다. 정확히 4시간이면 초과가 아닙니다(`4.0 > 4` 는 거짓).

**④ `.copy()` 로 복사하면 원래 요청서는 그대로 두고, `round(숫자, 1)` 은 소수 첫째 자리로 반올림합니다**

```python
request = {"id": 1, "status": "reviewing"}                          # 요청서 한 장
overdue = request.copy()                                            # .copy() 는 딕셔너리를 복사한 새 딕셔너리를 만든다
overdue["wait_hours"] = round(4.26, 1)                              # 복사본에만 키를 더한다. round(숫자, 1) 은 소수 첫째 자리까지 반올림한다
print(request)                                                      # 원래 요청서는 그대로다
print(overdue)                                                      # 복사본에만 wait_hours 키가 생겼다
```

실행 결과:

```
{'id': 1, 'status': 'reviewing'}
{'id': 1, 'status': 'reviewing', 'wait_hours': 4.3}
```


> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 검토 중인 요청서 가운데 처리 기한을 초과한 것 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 요청서를 접수해 놓고 승인자가 오래 확인하지 않으면 요청자의 일이 막힙니다. 지금은 사람이 목록을 눈으로 훑어서 오래된 요청을 찾기 때문에 놓치기 쉽습니다.
- **그래서 만드는 것**: `check_sla_breach` 입니다. 요청서 목록과 지금 시각을 받아, **검토 중이고 접수한 지 SLA 시간(4시간)을 초과한** 요청서만 골라 목록으로 리턴합니다. SLA 시간은 코드에 쓰지 않고 `config/sla.json` 에서 읽습니다.
- **오늘 데이터**: 요청서 여섯 장이고, 지금 시각은 14:00 으로 고정합니다. 그중 한 장은 이미 승인되어 있습니다.
- **실행하면**: 단계 1은 요청서 현황(번호 · 요청자 · 상태 · 접수 시각), 단계 2는 SLA 를 초과한 요청서와 접수한 뒤 지난 시간이 나옵니다.
- **현업에서는**: 신청 처리 도구도 접수 후 정해진 시간이 지난 신청에 알림을 보내거나 윗사람에게 넘깁니다(에스컬레이션).

**🎯 할 일**

1. `req_sla.py` · `config/sla.json` · `day03_5-1_run.py` 세 파일을 만들고, `check_sla_breach` 본문을 직접 씁니다.
2. 실행해서 <mark>요청서 현황</mark>(단계 1: 현황)과 <mark>기한을 초과한 요청</mark>(단계 2: 판정)을 읽습니다.

**`config/sla.json`** — 그대로 붙여 넣습니다. 처리 기한(시간)을 적은 설정 파일이고, `access_control` 안의 `config` 폴더(10/21(수)부터 `users.json` 이 있던 곳)에 만듭니다.

```json
{"hours": 4}
```

**`req_sla.py`**

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다

SLA_HOURS = load_json("config/sla.json", {"hours": 4})["hours"]  # 처리 기한(시간). 파일이 없거나 깨졌으면 기본값 4


def check_sla_breach(requests, now):                             # 요청서 목록과 지금 시각(datetime)을 받는 함수
    """검토 중(reviewing)인 요청서 가운데 접수한 지 SLA_HOURS 시간을 초과한 것의 목록을 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 기한을 초과한 요청서를 담을 빈 목록 breached 를 만든다
    # 2. requests 에서 request 를 하나씩 꺼낸다
    # 3.   request["status"] 가 "reviewing" 이면(검토 중인 것만 본다)
    # 4.     request["requested_at"] 을 TIME_FORMAT 으로 시각으로 바꿔 requested 에 담는다
    # 5.     (now - requested) 를 .total_seconds() 로 초 단위 숫자로 바꾸고 3600 으로 나눠 hours 에 담는다
    # 6.     hours 가 SLA_HOURS 보다 크면(같으면 아직 아니다)
    # 7.       request.copy() 로 요청서를 복사해 overdue 에 담는다
    # 8.       overdue["wait_hours"] 를 round(hours, 1) 로 정한다 (지난 시간을 소수 첫째 자리까지 반올림)
    # 9.       breached 에 overdue 를 더한다
    # 10. 반복이 끝나면 breached 를 리턴한다
```

- **영어 이름의 뜻**: `breach`(브리치)는 약속이나 기준을 「어기다」라는 뜻이고, `breached` 는 「어긴」입니다. 그래서 `check_sla_breach` 는 「SLA 를 어겼는지(기한을 초과했는지) 확인」, `breached` 는 「기한을 어긴 요청서를 담는 목록」입니다.
- 코드는 각 주석 바로 아래 줄에 씁니다. 주석 안에서 들여쓴 모양은 코드의 깊이를 보여 줍니다. 칸 수는 아래와 같습니다.
- 칸 수: `breached = []` 와 `for` 는 4칸, `for` 아래의 `if request["status"] …` 는 8칸, 그 `if` 안의 두 줄(`requested` · `hours`)과 `if hours > …` 는 12칸, 그 `if` 안의 세 줄(`overdue` · `wait_hours` · `breached.append`)은 16칸, 마지막 `return` 은 4칸입니다.
- `SLA_HOURS` 와 `TIME_FORMAT` 은 파일 위쪽에 이미 있습니다. 새로 만들지 않고 그대로 씁니다.
- 채우기 전에 실행하면 단계 1은 정상으로 나오고, 단계 2에서 `TypeError: 'NoneType' object is not iterable` 오류가 납니다. 함수가 아무것도 리턴하지 않아 `for` 가 돌 목록이 없기 때문입니다.

**`day03_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 요청 여섯 건을 접수하고 4번을 승인한 뒤, 단계 1은 요청서 현황을 출력하고 단계 2는 `check_sla_breach` 로 기한을 초과한 요청서를 출력합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request                           # 오전 3교시에 만든 승인 함수를 불러온다
from req_sla import SLA_HOURS, check_sla_breach                  # 방금 만든 기한 점검 함수와 SLA 시간을 불러온다

NOW = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)

INBOX = [                                                        # 오늘 들어온 요청 여섯 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),    # 오전 일찍 접수한 요청
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 10:30"),       # 오전에 접수한 요청
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 12:00"),    # 낮에 접수한 요청
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),           # 나중에 승인해서 처리가 끝나게 될 요청
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "계정 권한 점검", "2026-10-23 07:50"),   # 이른 아침에 접수한 요청
    ("tester", "SALES", "QUERY", "2026-10-27 18:00", "시험 계정 확인", "2026-10-23 10:00"),      # 오전 10시 정각에 접수한 요청
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다
approve_request(REQUESTS[3], "security_manager")                 # 4번(junho)은 이미 승인해 처리가 끝난 요청으로 만든다

print("--- 단계 1: 현황 - SLA 시간", SLA_HOURS, "시간, 지금 14:00")   # 단계 1 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], request["status"], request["requested_at"])   # 번호 · 요청자 · 상태 · 접수 시각을 출력한다

print("--- 단계 2: 판정 - SLA 를 초과한 요청")                       # 단계 2 시작을 알리는 줄
for request in check_sla_breach(REQUESTS, NOW):                  # 기한을 초과한 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], "접수", request["requested_at"], "->", request["wait_hours"], "시간 지남")   # 번호 · 요청자 · 접수 시각 · 지난 시간을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `req_sla.py` · `config/sla.json` · `day03_5-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch req_sla.py` → `touch config/sla.json` → `touch day03_5-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim req_sla.py` → `vim config/sla.json` → `vim day03_5-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[터미널]** 파일을 만든 뒤 `ls config` 를 쳐서 `sla.json` 이 `users.json` 과 같은 `config` 폴더 안에 있는지 확인합니다.
   - `config` 안에 또 `config` 가 생겼다면 위치가 틀린 것이니 옮깁니다.
   - `sla.json` 을 비워 두면 실행할 때 `[경고] 설정 파일 깨짐: config/sla.json` 이 나옵니다. 그래도 기본값 4로 돌아가 실행은 되니, 이 경고가 보이면 붙여 넣은 내용을 확인합니다.
3. **[VS Code]** `req_sla.py` 의 `check_sla_breach` 본문을 직접 씁니다. 5.1 의 그림과 문법 상자를 보고 씁니다.
4. **[터미널]** 위치가 `…/access_control` 인지 확인하고 실행합니다.
   ```bash
   pwd
   python day03_5-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day03_5-1_run.py` 실행할 파일
   - 맥북은 `python3 day03_5-1_run.py` 로 칩니다.
5. 출력은 두 단계입니다. 단계 1은 요청서 현황(여섯 줄)이고, 단계 2는 기한을 초과한 요청서와 지난 시간입니다.
6. **[보고서]** `day03_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 접수한 뒤 4시간을 초과한 요청이 몇 번인지, 접수한 뒤 몇 시간이 지났는지 적어 주세요.
   - (나) 🔍 승인자(`security_manager`)가 4시간을 초과하도록 처리하지 않은 요청을 찾았다면, 관제 담당은 누구에게 어떤 조치를 하면 좋을까요? 알림만 보낼 때와 윗사람에게 넘길 때(에스컬레이션)는 어떤 기준(예: 얼마나 더 지났을 때)으로 나누면 좋을까요?
   - (다) 🔍 상태(`reviewing` 인지)는 확인하지 않고 접수 시각만 보고 기한을 따진다면, 목록에 어떤 문제가 생기나요? 그 목록을 받은 사람은 무엇이 곤란할까요?

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 처리 기한 읽기 | `load_json("config/sla.json", {"hours": 4})["hours"]` |
| 검토 중인 것만 보기 | `if request["status"] == "reviewing":` |
| 접수 시각을 시각으로 | `datetime.strptime(request["requested_at"], TIME_FORMAT)` |
| 걸린 시간(시간 단위) | `(now - requested).total_seconds() / 3600` |
| 기한을 초과했는지 | `hours > SLA_HOURS` (정확히 같으면 아직 아님) |
| 복사해서 지난 시간 적기 | `overdue = request.copy()` → `overdue["wait_hours"] = round(hours, 1)` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 요청 이력 저장과 상태별 건수</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지: 「지금까지 만든 요청서는 프로그램을 끄면 사라집니다. 접수 · 승인 · 반려 · 부여를 한 번 돌리고 나면 요청서 전체를 파일로 남겨 주세요. 그리고 상태별로 몇 건인지 숫자로 보고 싶은데, 손으로 세면 시간이 걸리고 틀리기 쉽습니다.」
> - 이 교시에서 하는 일: 요청서 목록을 `requests.json` 으로 저장하는 함수 `save_requests` 와 상태별 건수를 세는 함수 `count_by_status` 를 직접 씁니다. 오전 · 오후에 만든 함수를 모두 이어서 한 번 돌려 봅니다. 마지막 10분에 오늘 만든 것을 깃허브에 올립니다.
> - 끝나면 쓰는 것: 보고서 (가)~(다) 답

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 요청서는 프로그램이 켜져 있는 동안에만 남아 있고, 프로그램이 끝나면 사라집니다. 파일로 저장해야 다음 날에도 요청서를 볼 수 있습니다. 여기서 **이력**은 요청이 어떻게 처리됐는지 남은 기록입니다.
2. 상태별 건수는 매일 아침 한눈에 보는 숫자입니다.

### 📖 6.1 JSON 파일로 저장하기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 어제까지는 JSON 파일을 **읽기**만 했습니다. 오늘은 파일에 **쓰기**를 합니다.

| 파일 열기 | 뜻 |
|---|---|
| `open(path, encoding="utf-8")` | 읽기 모드. 파일이 있어야 하고, 내용을 읽기만 한다 |
| `open(path, "w", encoding="utf-8")` | 쓰기 모드. 파일이 없으면 만들고, **있으면 내용을 지우고 새로 쓴다** |

- `json.dump(데이터, 파일, ensure_ascii=False, indent=2)` 는 데이터를 JSON 글자로 바꿔 파일에 씁니다. `ensure_ascii=False` 는 한글을 그대로 쓰라는 뜻이고, `indent=2` 는 사람이 읽기 쉽게 줄을 나누고 2칸씩 들여 쓰라는 뜻입니다.

```
+-------------------------------------+
| INBOX 여섯 건 접수 (create_request) |
+-------------------------------------+
   |
   v
+-------------------------------------------------------+
| 승인 · 반려 · 부여 (approve / reject / grant_request) |
+-------------------------------------------------------+
   |
   v
+-------------------------------------------------------------------+
| 점검: 상태별 건수 (count_by_status) + SLA 초과 (check_sla_breach) |
+-------------------------------------------------------------------+
   |
   v
+-------------------------------------+
| 저장: requests.json (save_requests) |
+-------------------------------------+
   |
   v
다시 읽어서 건수와 첫 요청서의 상태를 확인한다 (load_json)
```

**🐍 문법 상자 — 파일에 JSON 쓰기**

아래 코드는 읽기만 합니다. 따라 치지 않습니다.

**① `"w"` 로 열고 `json.dump` 로 쓰기**

```python
import json                                                         # JSON 을 다루는 모듈을 불러온다
data = [{"id": 1, "reason": "정산 확인"}]                             # 저장할 목록
with open("demo.json", "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
    json.dump(data, f, ensure_ascii=False, indent=2)                # 목록을 파일에 JSON 으로 쓴다
print(open("demo.json", encoding="utf-8").read())                   # 쓴 파일을 다시 열어 내용을 출력한다
```

실행 결과:

```
[
  {
    "id": 1,
    "reason": "정산 확인"
  }
]
```

**② `ensure_ascii=False` 를 빼면 한글이 `\uXXXX` 글자로 바뀌어 사람이 읽을 수 없습니다**

```python
import json                                                         # JSON 을 다루는 모듈을 불러온다
data = [{"id": 1, "reason": "정산 확인"}]                             # 저장할 목록
with open("demo.json", "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
    json.dump(data, f, indent=2)                                    # ensure_ascii=False 를 빼고 쓴다
print(open("demo.json", encoding="utf-8").read())                   # 쓴 파일을 다시 열어 내용을 출력한다
```

실행 결과:

```
[
  {
    "id": 1,
    "reason": "\uc815\uc0b0 \ud655\uc778"
  }
]
```

- `as f` 는 열린 파일을 `f` 라는 이름으로 부르겠다는 뜻이고, 파일은 `with` 아래에 들여쓴 줄 안에서만 열려 있습니다.
- `open(…).read()` 는 파일을 열어 내용 전체를 글자로 읽습니다. 위 코드는 방금 쓴 파일을 확인하려고 한 번 더 읽어 출력한 것입니다.
- 세는 모양 `counts[키] = counts.get(키, 0) + 1` 은 10/21(수)에 쓴 것과 같습니다. `counts.get(키, 0)` 은 그 키가 있으면 값을, 없으면 0 을 꺼냅니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 요청서 전체를 파일로 저장하고 상태별 건수 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 접수 · 승인 · 부여 · 기한 점검 결과가 프로그램이 켜져 있는 동안에만 남아 있어서, 프로그램을 끄면 모두 사라집니다. 관제 담당은 상태별로 몇 건인지도 숫자로 보고 싶어 하는데, 손으로 세면 틀리기 쉽습니다.
- **그래서 만드는 것**: `save_requests`(요청서 전체를 `requests.json` 파일에 저장하고 저장한 건수를 리턴)와 `count_by_status`(상태별 건수를 딕셔너리로 리턴)입니다.
- **실행하면**: 세 단계가 나옵니다. 단계 1은 요청 여섯 건의 처리 결과, 단계 2는 상태별 건수와 SLA 초과 요청 번호, 단계 3은 저장 결과입니다. 끝나면 `requests.json` 을 열어 한글이 그대로 저장됐는지 봅니다.
- **현업에서는**: 신청 도구도 신청 기록을 지우지 않고 보관하고, 상태별 건수를 날마다 세어 보냅니다.

**🎯 할 일**

1. `request_flow.py` 와 `day03_6-1_run.py` 두 파일을 만들고, `save_requests` 와 `count_by_status` 본문을 직접 씁니다.
2. 실행해서 <mark>처리 결과</mark>(단계 1: 처리), <mark>상태별 건수와 SLA 초과</mark>(단계 2: 점검), <mark>저장 결과</mark>(단계 3: 저장)를 읽습니다. `requests.json` 파일도 열어 봅니다.

**`request_flow.py`**

```python
import json                                                      # JSON 파일을 쓰는 모듈을 불러온다


def save_requests(requests, path):                               # 요청서 목록과 저장할 파일 경로를 받는 함수
    """요청서 목록을 JSON 파일로 저장한다. 한글이 그대로 보이게 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. path 를 쓰기 모드("w")로, encoding="utf-8" 로 열어 f 로 받는다
    # 2.   json.dump 로 requests 를 f 에 쓴다. ensure_ascii=False 와 indent=2 를 함께 쓴다
    # 3. 저장한 요청서 건수 len(requests) 를 리턴한다 (with 블록 밖, 함수 안쪽 줄에 맞춘다)


def count_by_status(requests):                                   # 요청서 목록을 받는 함수
    """상태(status)별 요청서 건수를 딕셔너리로 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 빈 딕셔너리 counts 를 만든다
    # 2. requests 에서 request 를 하나씩 꺼낸다
    # 3.   request["status"] 를 status 에 담는다
    # 4.   counts[status] 를 지금 값(없으면 0)에 1 을 더한 값으로 바꾼다
    # 5. 반복이 끝나면 counts 를 리턴한다
```

- 본문은 모두 함수 안이라 4칸으로 쓰고, `with` 와 `for` 안쪽은 4칸 더(8칸) 들어갑니다. 각 주석 바로 아래 줄에 씁니다. `save_requests` 의 `return len(requests)` 는 `with` 와 같은 4칸입니다.
- 채우기 전에 처음 실행하면(`requests.json` 이 아직 없을 때) 단계 2의 첫 줄이 `None` 으로 나옵니다. `count_by_status` 가 아무것도 리턴하지 않기 때문입니다. 이어서 단계 3에서 `저장 함수가 리턴한 건수: None` 과 `[경고] 설정 파일 없음: requests.json` 이 나온 뒤 `IndexError` 가 납니다. `save_requests` 가 파일을 만들지 않았기 때문입니다.

**`day03_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 요청 여섯 건을 접수하고 처리한 뒤, 단계 1은 승인 · 반려 · 부여 결과를 출력하고 단계 2는 상태별 건수와 SLA 초과 요청을 출력하고 단계 3은 `requests.json` 으로 저장해 다시 읽어 확인합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request, reject_request           # 오전 3교시에 만든 승인 · 반려 함수를 불러온다
from req_grant import grant_request                              # 오전 4교시에 만든 부여 함수를 불러온다
from req_sla import check_sla_breach                             # 5교시에 만든 기한 점검 함수를 불러온다
from request_flow import save_requests, count_by_status          # 방금 만든 저장 · 집계 함수를 불러온다

NOW = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)

INBOX = [                                                        # 오늘 들어온 요청 여섯 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 10:30"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 12:00"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "계정 권한 점검", "2026-10-23 07:50"),
    ("tester", "SALES", "QUERY", "2026-10-27 18:00", "시험 계정 확인", "2026-10-23 10:00"),
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다

print("--- 단계 1: 처리 - 승인 · 반려 · 부여")                      # 단계 1 시작을 알리는 줄
approve_request(REQUESTS[0], "security_manager")                 # 1번 승인
reject_request(REQUESTS[1], "security_manager")                  # 2번 반려
approve_request(REQUESTS[2], "security_manager")                 # 3번 승인
approve_request(REQUESTS[3], "security_manager")                 # 4번 승인
for request in REQUESTS:                                         # 요청서를 하나씩 꺼내
    ok, result = grant_request(request)                          # 부여를 시도한다(승인된 것만 의미가 있다)
    print(request["id"], request["user"], request["status"], "->", result)   # 번호 · 요청자 · 상태 -> 결과 를 출력한다

print("--- 단계 2: 점검 - 상태별 건수와 SLA")                      # 단계 2 시작을 알리는 줄
print(count_by_status(REQUESTS))                                 # 상태별 건수를 출력한다
for request in check_sla_breach(REQUESTS, NOW):                  # 기한을 초과한 요청서를 하나씩 꺼낸다
    print("SLA 초과 요청 번호:", request["id"])                    # 요청 번호를 출력한다

print("--- 단계 3: 저장 - requests.json")                        # 단계 3 시작을 알리는 줄
count = save_requests(REQUESTS, "requests.json")                 # 요청서 목록 전체를 파일로 저장하고 저장한 건수를 받는다
print("저장 함수가 리턴한 건수:", count)                            # 리턴한 건수를 출력한다
saved = load_json("requests.json", [])                           # 저장한 파일을 다시 읽어
print("저장한 요청서", len(saved), "건, 첫 요청서의 상태:", saved[0]["status"])   # 건수와 첫 요청서의 상태를 출력한다
```

**순서**

0. **[터미널]** 5교시 파일이 정상인지 먼저 확인합니다. 마지막 줄에 `5교시 파일 정상` 이 나와야 합니다(맥북은 `python3 -c "…"`). 아니면 문서 맨 아래 「앞 교시 파일 완성본」으로 `req_sla.py` 와 `config/sla.json` 을 먼저 만듭니다.
   ```bash
   python -c "from req_sla import check_sla_breach; print('5교시 파일 정상')"
   ```
1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `request_flow.py` · `day03_6-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch request_flow.py` → `touch day03_6-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim request_flow.py` → `vim day03_6-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `request_flow.py` 의 두 함수 본문을 직접 씁니다. 6.1 의 표와 문법 상자를 보고 씁니다.
3. **[터미널]** 위치가 `…/access_control` 인지 확인하고 실행합니다.
   ```bash
   pwd
   python day03_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day03_6-1_run.py` 실행할 파일
   - 맥북은 `python3 day03_6-1_run.py` 로 칩니다.
4. 출력은 세 단계입니다. 단계 1은 요청 여섯 건의 처리 결과(여섯 줄), 단계 2는 상태별 건수와 SLA 초과 요청 번호, 단계 3은 저장 함수가 리턴한 건수와 저장 결과입니다.
   - 5교시에서는 SLA 초과가 1번과 5번이었지만 여기서는 5번만 나옵니다. 이 실행에서는 1번이 승인 · 부여까지 끝나 더 이상 `reviewing` 이 아니기 때문입니다.
5. **[VS Code]** 왼쪽 목록에 새로 생긴 `requests.json` 을 열어 요청서가 한글 그대로 저장됐는지 봅니다.
6. **[보고서]** `day03_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, `requests.json` 에 저장된 요청서가 몇 건인지와 상태별 건수를 적어 주세요.
   - (나) 🔍 반려된 요청서(`rejected`)나 승인은 됐지만 부여하지 않은 요청서(`approved`)도 지우지 않고 `requests.json` 에 남기는 이유는 무엇인가요?
   - (다) 🔍 상태별 건수가 `granted` 1 · `rejected` 1 · `approved` 2 · `reviewing` 2 로 나왔습니다. 이 숫자를 매일 아침 보면 처리 흐름의 어디가 막혀 있는지 어떻게 알 수 있나요?

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 파일에 쓰기 | `with open(path, "w", encoding="utf-8") as f:` |
| 목록을 JSON 으로 | `json.dump(requests, f, ensure_ascii=False, indent=2)` |
| 상태별 건수 | `counts[status] = counts.get(status, 0) + 1` |
| 저장한 건수 알리기 | `return len(requests)` |
| 저장했는지 확인 | `load_json("requests.json", [])` 로 다시 읽는다 |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다. 6교시 마지막 10분에 합니다.

- **지금은**: 팀장이 「오늘 만든 요청 처리 코드를 저장소에 남겨 달라」고 합니다.
- **그래서 하는 것**: 올라갈 파일을 `git status` 로 먼저 확인하고(비밀 키 파일 `.env` 가 섞이면 안 됩니다), `git add` → `git commit` → `git push` 로 올립니다.
- **끝나면**: 깃허브 저장소의 `access_control` 폴더에서 오늘 만든 파일이 모두 보입니다.

**순서**

1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 결과가 `…/security-agent-toolkit` 으로 끝나야 합니다.
   ```bash
   cd ..
   pwd
   ```
   - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 위치 확인
   - 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다. 새로 연 뒤 `pwd` 를 한 번 더 쳐서 확인합니다.
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. 빨간 목록에 `.env` 나 `.venv` 가 보이면 올리지 않고 멈춥니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 올릴 파일의 상태를 봄
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다. `.venv` 도 같은 방법으로 합니다.
   - 어제 `access_control` 을 이미 올렸다면 오늘 새로 만든 파일이 `access_control/req_create.py` 처럼 한 줄씩 보입니다. 어제 올리지 않았다면 `access_control/` 한 줄로 보일 수 있습니다. 어느 쪽이든 `Untracked files:` 아래에 보이는 줄을 센 그대로 적습니다.
   - `access_control/requests.json` 은 6교시에 프로그램이 만든 이력 파일입니다. 이것도 올라갑니다.
   - `access_control/__pycache__/` 가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다. 줄 수는 그 뒤에 다시 셉니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `Untracked files:` 아래에 줄이 몇 개 보였는지, 그중에 `.env` 나 `.venv` 가 있었는지 적어 주세요.
   - 앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다. 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add access control day 3 request, approval, grant, SLA and history"
   git push
   ```
   - 명령 풀이: `git add .` 바뀐 파일을 올릴 목록에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림
   - `git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다. `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `access_control` 폴더를 열고, 터미널에서 `ls access_control` 로 본 파일들이 깃허브에도 보이는지 확인합니다. `__pycache__` 폴더는 없어도 됩니다.
   - 빠진 이름이 있으면 터미널에서 `ls access_control` 로 내 PC 에 있는지 봅니다. 없으면 다른 폴더에 만든 것이니 `access_control` 안으로 옮기고 1 ~ 4번을 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 파일이 모두 있는지 확인 |

---

## 오늘 마무리

| 확인 | 문제 |
|---|---|
| 요청을 요청서로 접수하고 접수 못 할 요청을 걸러 냈다 | 오전 2-1 |
| 승인 · 반려가 검토 중인 요청서에만 되게 했다 | 오전 3-1 |
| 승인된 요청서를 정책으로 확인하고 예외 권한을 부여했다 | 오전 4-1 |
| 처리 기한을 초과한 요청서를 시간 계산으로 찾았다 | 5-1 |
| 요청서 전체를 `requests.json` 으로 저장하고 상태별 건수를 셌다 | 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

주말과 현직자 수업(10/26(월)~10/28(수))이 지나고 10/29(목)에는 부여된 권한 가운데 쓰이지 않는 것 · 넘치는 것을 찾는 과다권한 탐지를 합니다. 오늘 만든 `requests.json` 이 그때 「누가 어떤 권한을 요청해 받았나」를 보는 자료입니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_5-1_run.py
```

**채운 코드** (한 예)

```python
    breached = []                                                # 기한을 초과한 요청서를 담을 빈 목록
    for request in requests:                                     # 요청서를 하나씩 꺼낸다
        if request["status"] == "reviewing":                     # 검토 중인 것만 본다(처리가 끝난 것은 기한을 따지지 않는다)
            requested = datetime.strptime(request["requested_at"], TIME_FORMAT)   # 접수 시각 글자를 시각으로 바꾼다
            hours = (now - requested).total_seconds() / 3600     # 지금까지 걸린 시간을 시간(hour) 단위 숫자로 구한다
            if hours > SLA_HOURS:                                # 걸린 시간이 SLA 시간보다 크면
                overdue = request.copy()                         # 요청서를 복사한다(원래 요청서는 바꾸지 않는다)
                overdue["wait_hours"] = round(hours, 1)          # 지난 시간을 소수 첫째 자리까지 반올림해 복사본에 적는다
                breached.append(overdue)                         # 기한을 초과한 목록에 복사본을 더한다
    return breached                                              # 기한을 초과한 요청서 목록을 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, SLA 를 초과한 요청은 **1번**(접수 08:30, 5.5시간 지남)과 **5번**(접수 07:50, 6.2시간 지남)입니다. 6번은 10:00 에 접수해 정확히 4시간이라 초과하지 않았습니다.

```
--- 단계 1: 현황 - SLA 시간 4 시간, 지금 14:00
1 seoyeon reviewing 2026-10-23 08:30
2 gaeun reviewing 2026-10-23 10:30
3 dami reviewing 2026-10-23 12:00
4 junho approved 2026-10-23 09:00
5 seoyeon reviewing 2026-10-23 07:50
6 tester reviewing 2026-10-23 10:00
--- 단계 2: 판정 - SLA 를 초과한 요청
1 seoyeon 접수 2026-10-23 08:30 -> 5.5 시간 지남
5 seoyeon 접수 2026-10-23 07:50 -> 6.2 시간 지남
```

- (나) 한 예: 기한을 초과한 요청서를 찾으면 ① 먼저 요청서를 맡은 승인자(`security_manager`)에게 알림을 보내 오늘 안에 처리하게 합니다. ② 알림 뒤에도 일정 시간(예: 2시간) 더 지나면 승인자의 윗사람이나 대리 승인자에게 넘깁니다(에스컬레이션). 처음 기한을 초과했을 때는 알림만 하고, 더 지나도 처리가 없을 때 넘기는 식으로 단계를 나눕니다. 요청자에게는 「검토가 늦어지고 있다」는 상태를 알려 메신저로 재촉해 오는 일을 줄입니다.
- (다) 4번(junho)은 접수한 지 5시간이 지났지만 이미 승인되어 처리가 끝난 요청입니다. 상태를 확인하지 않고 접수 시각만으로 세면 ① 초과 목록에 이미 처리된 요청(4번)이 섞입니다. ② 그 목록을 받은 담당자는 이미 끝난 일을 다시 확인하느라 시간을 쓰고, 정말 늦어진 요청을 찾기 어려워집니다. 기한은 아직 처리되지 않은 요청에만 의미가 있으므로 `reviewing` 인지 먼저 봅니다.

**왜** — 기한을 따지려면 「아직 처리되지 않았는가」와 「접수한 지 얼마나 됐는가」를 둘 다 봐야 합니다. 시각에서 시각을 빼면 걸린 시간이 나오고, 그 시간을 SLA 와 비교하는 것이 전부입니다. SLA 시간을 파일로 빼 두면 4시간을 2시간으로 줄일 때 코드를 고치지 않아도 됩니다.

**자주 틀리는 곳** — `.total_seconds()` 에서 `/ 3600` 을 빼먹는 경우가 가장 많습니다. 걸린 시간이 초 단위(예: 19800.0)라서 SLA 4 보다 항상 커지고, 검토 중인 요청서가 모두 기한 초과로 나옵니다. 실행하면 다음처럼 됩니다(정확히 4시간인 6번까지 나오는 것이 신호입니다).

```
--- 단계 2: 판정 - SLA 를 초과한 요청
1 seoyeon 접수 2026-10-23 08:30 -> 19800.0 시간 지남
2 gaeun 접수 2026-10-23 10:30 -> 12600.0 시간 지남
3 dami 접수 2026-10-23 12:00 -> 7200.0 시간 지남
5 seoyeon 접수 2026-10-23 07:50 -> 22200.0 시간 지남
6 tester 접수 2026-10-23 10:00 -> 14400.0 시간 지남
```

`hours > SLA_HOURS` 를 `>=` 로 쓰면 정확히 4시간인 6번도 초과로 나옵니다. `datetime.strptime` 에 형식 글자 대신 다른 값을 넣으면 `ValueError` 가 납니다.

**관제에서는** — 기한을 초과한 요청 건수는 승인이 밀리는 곳을 보는 숫자입니다. 같은 승인자에게 계속 쌓이면 승인자를 늘리거나 대리 승인자를 정합니다. 오래 방치된 요청이 갑자기 승인되는 경우는 요청 당시와 상황이 달라졌는지 다시 확인합니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_6-1_run.py
```

**채운 코드** (한 예)

```python
    with open(path, "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
        json.dump(requests, f, ensure_ascii=False, indent=2)     # 목록을 파일에 JSON 으로 쓴다
    return len(requests)                                         # 저장한 요청서 건수를 리턴한다
```

```python
    counts = {}                                                  # 상태 → 건수를 담을 빈 딕셔너리
    for request in requests:                                     # 요청서를 하나씩 꺼낸다
        status = request["status"]                               # 그 요청서의 상태를 꺼낸다
        counts[status] = counts.get(status, 0) + 1               # 그 상태의 건수를 1 늘린다
    return counts                                                # 상태별 건수를 리턴한다
```

**결과**

- (가) 출력은 다음과 같고(단계 3 첫 줄 `저장 함수가 리턴한 건수` 는 `save_requests` 의 마지막 줄 `return len(requests)` 가 만든 값입니다), `requests.json` 에 저장된 요청서는 **6건**이며 상태별 건수는 `granted` 1건 · `rejected` 1건 · `approved` 2건 · `reviewing` 2건입니다.

```
--- 단계 1: 처리 - 승인 · 반려 · 부여
1 seoyeon granted -> 부여
2 gaeun rejected -> 승인되지 않음
3 dami approved -> 부여하지 않음(퇴사한 계정)
4 junho approved -> 부여하지 않음(허용)
5 seoyeon reviewing -> 승인되지 않음
6 tester reviewing -> 승인되지 않음
--- 단계 2: 점검 - 상태별 건수와 SLA
{'granted': 1, 'rejected': 1, 'approved': 2, 'reviewing': 2}
SLA 초과 요청 번호: 5
--- 단계 3: 저장 - requests.json
저장 함수가 리턴한 건수: 6
저장한 요청서 6 건, 첫 요청서의 상태: granted
```

- (나) 반려되거나 부여되지 않은 요청서도 「그런 요청이 있었고 이렇게 처리됐다」는 사실이기 때문입니다. 지우면 나중에 같은 사람이 같은 요청을 반복하는지, 승인자가 어떤 요청을 반려했는지, 퇴사한 사람의 요청이 승인까지 갔는지를 알 수 없습니다. 감사에서는 처리된 것뿐 아니라 거절된 것도 증빙이 됩니다.
- (다) 숫자가 말하는 막힌 곳은 두 군데입니다. ① `reviewing` 2건은 승인자가 아직 처리하지 않은 요청입니다(그중 5번은 4시간을 초과했습니다). ② `approved` 2건은 승인은 됐지만 정책 확인에서 부여되지 않은 요청입니다(퇴사한 계정 · 이미 허용된 권한). 막힌 곳이 다르므로 ①은 승인자에게 처리를 재촉하고, ②는 요청자에게 부여되지 않은 이유를 알려 요청을 정리합니다. 막힌 곳과 조치가 이어져 있으면 맞습니다.

**왜** — 프로그램 안의 요청서는 프로그램이 끝나면 사라지므로, 이력은 파일로 남겨야 합니다. `"w"` 로 열면 파일 내용이 새로 쓰여서 항상 가장 최근의 전체 목록이 저장됩니다. 상태별 건수는 처리가 어디에서 막히는지 보여 주는 가장 간단한 숫자입니다.

**자주 틀리는 곳** — `json.dump` 에서 `ensure_ascii=False` 를 빼먹는 경우가 가장 많습니다. 파일은 만들어지지만 한글이 `\uXXXX` 글자로 저장되어 사람이 읽을 수 없습니다. 실행한 뒤 `requests.json` 의 앞부분이 다음처럼 보이면 그 실수입니다.

```
[
  {
    "id": 1,
    "user": "seoyeon",
    "resource": "SETTLE",
    "action": "QUERY",
    "permission": "SETTLE:QUERY",
    "until": "2026-10-27 18:00",
    "reason": "\uc815\uc0b0 \ub300\uc870 \uc9c0\uc6d0",
    "requested_at": "2026-10-23 08:30",
```

파일을 `"w"` 대신 읽기 모드(`"r"`)로 열면 `io.UnsupportedOperation: not writable` 오류가 납니다. `with` 줄 아래를 들여쓰지 않으면 `IndentationError: expected an indented block` 오류가 납니다.

**관제에서는** — 요청 이력 파일은 과다권한 점검의 입력이 됩니다. 「누가 어떤 권한을 받았고 아직 쓰이는가」를 이력과 접속 기록을 맞춰 봅니다. 실무에서는 이력을 날짜별 파일로 나눠 남기고(오늘은 가장 최근 목록 하나만 저장합니다), 파일 자체도 접근 권한을 제한합니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
cd ..
pwd
git status
git add .
git commit -m "Add access control day 3 request, approval, grant, SLA and history"
git push
```

**결과**

- (가) 한 예: 「줄이 열여섯 개였고(`.py` 열 개 + `config/sla.json` 한 개 + `requests.json` 한 개 + `.md` 네 개), `.env` · `.venv` 는 없었다」. 이 16줄은 `__pycache__` 가 보이지 않을 때의 숫자이고, 줄 수와 이름은 학생마다 다를 수 있습니다. `.env` 나 `.venv` 가 보였다면 `.gitignore` 에 한 줄을 적고 `git status` 를 다시 쳤다고 적습니다.

**왜** — 올리기 전에 올라갈 파일을 확인해야 비밀 키가 섞이지 않습니다. 요청 처리 코드와 이력 파일이 함께 올라가야 다음에 누가 보아도 같은 흐름을 따라갈 수 있습니다.

**자주 틀리는 곳** — `.env` 가 보이는데 그대로 `git add .` 를 하는 실수가 가장 위험합니다. `cd ..` 를 두 번 쳐서 `security-agent-toolkit` 바깥으로 나가는 경우도 있습니다. `pwd` 로 확인합니다.

**관제에서는** — 접근통제 코드와 요청 이력은 같은 커밋에 함께 올려, 어느 요청이 어느 코드로 처리됐는지 이력으로 남깁니다.

---

### 앞 교시 파일 완성본

5교시 파일을 못 만들고 6교시로 넘어가야 할 때 그대로 만들어 씁니다. 정답 본문을 머리말과 합친 전체 파일입니다.

**`config/sla.json`**

```json
{"hours": 4}
```

**`req_sla.py`** (5교시 완성본)

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다

SLA_HOURS = load_json("config/sla.json", {"hours": 4})["hours"]  # 처리 기한(시간). 파일이 없거나 깨졌으면 기본값 4


def check_sla_breach(requests, now):                             # 요청서 목록과 지금 시각(datetime)을 받는 함수
    """검토 중(reviewing)인 요청서 가운데 접수한 지 SLA_HOURS 시간을 초과한 것의 목록을 리턴한다."""
    breached = []                                                # 기한을 초과한 요청서를 담을 빈 목록
    for request in requests:                                     # 요청서를 하나씩 꺼낸다
        if request["status"] == "reviewing":                     # 검토 중인 것만 본다(처리가 끝난 것은 기한을 따지지 않는다)
            requested = datetime.strptime(request["requested_at"], TIME_FORMAT)   # 접수 시각 글자를 시각으로 바꾼다
            hours = (now - requested).total_seconds() / 3600     # 지금까지 걸린 시간을 시간(hour) 단위 숫자로 구한다
            if hours > SLA_HOURS:                                # 걸린 시간이 SLA 시간보다 크면
                overdue = request.copy()                         # 요청서를 복사한다(원래 요청서는 바꾸지 않는다)
                overdue["wait_hours"] = round(hours, 1)          # 지난 시간을 소수 첫째 자리까지 반올림해 복사본에 적는다
                breached.append(overdue)                         # 기한을 초과한 목록에 복사본을 더한다
    return breached                                              # 기한을 초과한 요청서 목록을 리턴한다
```
