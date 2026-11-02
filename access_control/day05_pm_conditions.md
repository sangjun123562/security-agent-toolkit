# 10/30(금) 오후 · 3과목 접근통제 ⑤ — 조건기반 정책 · 판정 서버 · 서버 로그 — 실습

오전에는 점검에서 찾은 권한을 계획 → 승인 → 실행 순서로 회수했습니다. 오후에는 회수하고도 남은 권한을 **요청이 올 때마다 조건을 확인해서** 판정하고, 그 판정을 **서버**로 만들어 다른 프로그램이 주소로 요청해 판정을 받을 수 있게 합니다.

- **5교시**: 기본 판정이 허용이어도 업무 시간과 접속 위치 조건에 어긋나면 거부하는 **조건기반 정책**을 만든다.
- **6교시**: 판정을 `.py` **서버**로 만들어 다른 프로그램이 주소로 요청해 판정을 받을 수 있게 하고, 요청마다 로그를 한 줄씩 남긴다.
  - 요청을 보내 응답과 서버 로그를 대조하고, 마지막 10분에 오늘 만든 것을 깃허브에 올립니다.

교시마다 문제는 하나입니다. 오후 수업은 오전의 회수 결과를 쓰지 않고, 10/22(목)에 만든 판정 함수 `evaluate_access` 만 씁니다.

**📎 오늘 불러 쓰는 이전 파일** — 오늘 코드가 `import` 로 가져다 쓰는 앞 수업 파일입니다. 없으면 오른쪽 열의 방법으로 먼저 준비합니다.

| 파일 | 만든 날 | 오늘 가져다 쓰는 것 | 쓰는 교시 | 없으면 |
|---|---|---|---|---|
| `policy.py` | 10/22(목) | `evaluate_access` (이 함수가 `rbac.py` · `exception_policy.py` 와 `config` 의 json 3개를 다시 가져다 씁니다) | 5교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |
| `config_loader.py` | 10/22(목) | `load_json` | 5교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |

- 오전 회수 결과와 10/23(금) 파일, 10/29(목) 파일은 오후에 쓰지 않습니다. 앞 날에 결석했어도 위 `day02_recovery` 폴더만 있으면 됩니다.
- 오늘 만드는 파일도 뒤 교시가 가져다 씁니다. 5교시 `conditional.py` 는 6교시에서 씁니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 이전 파일, 설치한 도구(flask · requests)를 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python -c "from datetime import datetime; from rbac import USERS; from policy import evaluate_access; from config_loader import load_json; import flask, requests; print('이전 파일 · flask · requests 정상', len(USERS), evaluate_access('seoyeon', 'SALES', 'QUERY', datetime(2026, 10, 30, 10, 0)))"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다. 맥북에서 결과 줄 앞에 `NotOpenSSLWarning` 경고가 붙으면 무시합니다.
   - `rbac.py` · `policy.py` · `exception_policy.py` · `config_loader.py` 가 보이고, `config` 안에 `users.json` · `roles.json` · `exceptions.json` 이 보여야 합니다.
   - 마지막 줄에 `이전 파일 · flask · requests 정상 6 (True, '역할 권한')` 이 나와야 합니다.
     - 6은 사용자 6명이고, 괄호는 10/22(목)의 판정 함수가 seoyeon 의 조회 요청을 허용한다는 결과입니다.
     - 다르게 나오거나 오류가 나면 10/22(목) 파일이 완성본이 아닌 것이니 아래 `day02_recovery` 방법으로 파일을 다시 넣고 확인 명령을 다시 칩니다.
   - `No module named 'flask'` 나 `No module named 'requests'` 가 나오면 `pip install flask requests` 를 치고(맥북은 `pip3`) 확인 명령을 다시 칩니다. 그래도 안 되면 6교시 아래의 「AI 에게 이렇게 물어봅니다」를 봅니다.
   - 파일이 없거나 결과가 다르면 수업 자료로 받은 `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) 안의 파일을 `access_control` 폴더에 넣고(`config` 안의 파일은 `config` 폴더에 넣습니다) 마지막 줄을 다시 칩니다.
3. **오늘 받은 파일 두 개를 `access_control` 폴더에 둡니다.** 이미 그 폴더에 있으면 건너뜁니다. 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day05_pm_conditions.md` (이 파일) — 오후 실습 안내. 읽기만 합니다.
   - `day05_pm_report.md` — **오후 보고서.** 5 · 6교시 답과 마무리 칸을 여기에 적습니다.
4. **[VS Code]** `access_control` 폴더에 있는 `day05_pm_conditions.md` 를 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day05_pm_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-30(금))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이며, 이유까지 적어야 합니다.
     - 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다.
     - 🔍 가 없는 질문도 못 적으면 같은 말을 씁니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 문자열(string)은 따옴표로 감싼 글입니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일이 `config/…` 를 지금 위치 기준으로 찾기 때문입니다. `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **어제까지의 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 업무 시간과 접속 위치 조건으로 판정하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「정산을 조회할 권한이 있는 직원이 새벽에 집 밖의 공용 와이파이에서 접속해도 지금은 그대로 허용됩니다. 권한이 있어도 업무 시간이 아니거나 회사 밖에서 접속하면 막고 싶습니다. 특히 데이터를 바꾸는 권한과 계정을 관리하는 권한은 더 엄격하게요.
>
> 권한마다 허용하는 시간대와 접속 위치(사내망 · VPN · 외부)를 파일에 적어 둘 테니, 판정할 때 함께 확인해 주세요.」
> - **왜 중요한가**: 권한이 있어도 평소와 다른 시간이나 장소에서 온 요청은 위험할 수 있습니다. 판정할 때 시간과 접속 위치를 함께 확인하면 그런 요청을 가려낼 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 지금까지의 판정(`evaluate_access`)은 **누가 어떤 권한을 갖고 있나**만 봤습니다. 권한이 있으면 새벽이든 외부든 허용합니다.
2. 이번에는 **언제, 어디서 요청했나**도 함께 봅니다. 기본 판정이 허용이어도 그 권한에 걸린 조건(업무 시간, 접속 위치)에 어긋나면 거부합니다. 이것을 **조건기반 정책**이라고 부릅니다.
3. 조건은 코드 안이 아니라 `config/conditions.json` 파일에 적습니다.

### 📖 5.1 조건 파일과 판정 순서

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`config/conditions.json` 의 한 조건은 아래 세 키로 이루어집니다.

| 키 | 뜻 | 값의 예 |
|---|---|---|
| `permission` | 조건이 걸린 권한 | `"SALES:CHANGE"` |
| `hours` | 허용 시간대 `[시작 시, 끝 시]`. 끝 시각은 **포함하지 않음** | `[9, 18]` (9시부터 18시 **전까지**) |
| `networks` | 허용하는 접속 위치 | `["office", "vpn"]` |

- 접속 위치는 세 가지입니다.
  - `office`(사내망) · `vpn`(VPN으로 회사에 연결한 상태) · `external`(그 밖의 외부)
- 오늘 조건은 세 권한에만 걸려 있습니다.
  - `SALES:CHANGE`: 9시부터 18시 전까지, 사내망 · VPN
  - `SETTLE:QUERY`: 8시부터 20시 전까지, 사내망 · VPN
  - `ACCOUNT:CHANGE`: 9시부터 18시 전까지, 사내망만
  - 조건이 없는 권한(예: `SALES:QUERY`)은 기본 판정 그대로입니다.
- 판정 순서는 **기본 판정 → 조건**입니다.
  - 퇴사한 사용자처럼 사람 자체가 거부 대상이면 조건을 볼 필요 없이 그 이유로 거부합니다.
- 요청에는 접속 위치(`network`)가 추가되었습니다. 시각(`now`)에서 시(`now.hour`)를 꺼내는 것은 1과목에서 배웠습니다.
- `start, end = rule["hours"]` 는 리스트의 두 값을 두 이름으로 한꺼번에 받습니다.
  - 함수가 리턴한 두 값을 `ok, reason = …` 로 받던 것과 같은 모양입니다.
  - 실행 파일의 `number += 1` 은 `number = number + 1` 과 같은 뜻입니다.
- **직접 쓰는 곳은 세 함수**입니다. 판단이 필요한 함수마다 2 ~ 4줄만 쓰고, 나머지는 미리 채웠습니다.
  - `is_work_time`(1 ~ 3번): 요청 시각이 허용 시간대 안인지 알려 줍니다.
  - `is_allowed_network`(4 · 5번): 접속 위치가 허용 리스트에 있는지 알려 줍니다.
  - `evaluate_conditional`(6 ~ 9번): 두 확인이 거짓이면 이유와 함께 거부합니다.
- **미리 채운 것**: `load_rules` 와 `evaluate_conditional` 의 기본 판정 · 조건 찾기 반복 · 마지막 `return` 입니다.

**🐍 문법 상자 — 범위 비교**

**① `a <= x < b` 는 x 가 a 이상이고 b 미만인지 한 번에 묻습니다**

```python
hour = 10                                                            # 요청 시각의 시
print(9 <= hour < 18)                                                # 9시 이상이고 18시 미만인가
```

실행 결과:

```
True
```

```python
hour = 18                                                            # 요청 시각의 시
print(9 <= hour < 18)                                                # 9시 이상이고 18시 미만인가
```

실행 결과:

```
False
```

- `9 <= hour < 18` 은 `9 <= hour and hour < 18` 과 같은 뜻입니다. 끝 값(18)은 포함하지 않아서 18시 정각은 `False` 입니다.
- 이 비교의 결과(`True` 또는 `False`)를 그대로 `return` 하면 「업무 시간 안인가」를 알려 주는 함수가 됩니다.

```
+-------------------------------------------------------------------+
| evaluate_conditional(user, resource, action, network, now, rules) |
+-------------------------------------------------------------------+
   |
   v
+--------------------------------------------------+
| evaluate_access 로 기본 판정을 한다 (ok, reason) |
+--------------------------------------------------+
   |
   v
+-----------------+
| ok 가 거짓인가? |
+-----------------+
   |
   +--> 그렇다 --> False, reason 을 리턴한다   (사람 자체가 거부 대상이면 조건을 볼 필요가 없다)
   |
   v  아니다
+-----------------------------------+
| permission = 「자원:행위」 문자열 |
+-----------------------------------+
   |
   v
+---------------------------------------------------------+
| 조건(rule)을 하나씩 꺼내 permission 이 같은 것을 찾는다 |
+---------------------------------------------------------+
   |
   v
+----------------------------------------------------------+
| is_work_time(rule, now) 가 참인가? (start <= hour < end) |
+----------------------------------------------------------+
   |
   +--> 아니다 --> False, 「업무 시간 밖」을 리턴한다
   |
   v  그렇다
+----------------------------------------------------------------------------+
| is_allowed_network(rule, network) 가 참인가? (network in allowed_networks) |
+----------------------------------------------------------------------------+
   |
   +--> 아니다 --> False, 「허용되지 않은 접속 위치」를 리턴한다
   |
   v  그렇다  (다음 조건으로, 같은 권한의 조건이 더 없으면 반복이 끝난다)
+-----------------------------------------------------+
| True, reason 을 리턴한다  (기본 판정의 이유로 허용) |
+-----------------------------------------------------+
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 기본 판정 뒤에 업무 시간과 접속 위치 조건을 확인하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 권한이 있는 사용자는 새벽이든 외부든 모두 허용됩니다. 탈취된 계정이 한밤중에 외부에서 들어와도 판정 함수로는 막을 수 없습니다.
- **그래서 만드는 것**: `evaluate_conditional` 입니다.
  - 먼저 10/22(목)의 `evaluate_access` 로 기본 판정을 하고, 허용이면 그 권한의 조건(업무 시간, 접속 위치)에 어긋나는지 확인합니다.
  - 어긋나면 이유와 함께 거부합니다.
- **실행하면**: 단계 1은 요청 여덟 건의 판정, 단계 2는 조건 파일에 적힌 조건을 출력합니다.
- **현업에서는**: 접근 제어 도구도 신원만 보지 않고 접속 시간, 위치, 기기 같은 조건을 함께 확인합니다.

**🎯 할 일**

1. `config/conditions.json` · `conditional.py` · `day05_5-1_run.py` 세 파일을 만들고, `is_work_time` · `is_allowed_network` · `evaluate_conditional` 에서 직접 쓰는 곳 세 군데를 씁니다.
2. 실행해서 <mark>요청 여덟 건의 판정</mark>(단계 1: 판정)과 <mark>조건 파일에 적힌 조건</mark>(단계 2: 확인)을 읽습니다.

**`config/conditions.json`** — 그대로 붙여 넣습니다. 권한별 조건입니다. `access_control` 안의 `config` 폴더에 만듭니다.

```json
[
  {"permission": "SALES:CHANGE", "hours": [9, 18], "networks": ["office", "vpn"]},
  {"permission": "SETTLE:QUERY", "hours": [8, 20], "networks": ["office", "vpn"]},
  {"permission": "ACCOUNT:CHANGE", "hours": [9, 18], "networks": ["office"]}
]
```

**`conditional.py`**

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 기본 판정 함수를 불러온다


def load_rules(path):                                            # 조건 파일 경로를 받는 함수
    """조건 파일을 읽어 조건 딕셔너리의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽는다(못 읽으면 두 번째 값인 빈 리스트를 리턴한다)


def is_work_time(rule, now):                                     # 조건 한 건과 요청 시각(datetime)을 받는 함수
    """요청 시각의 시가 조건의 허용 시간대 안이면 True, 밖이면 False 를 리턴한다. 끝 시각은 포함하지 않는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. rule["hours"] 를 start, end 두 이름으로 받는다
    # 2. now.hour 를 hour 에 담는다
    # 3. start <= hour < end 의 결과(True 또는 False)를 리턴한다


def is_allowed_network(rule, network):                           # 조건 한 건과 접속 위치를 받는 함수
    """접속 위치가 조건의 허용 접속 위치에 들어 있으면 True, 아니면 False 를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. rule["networks"] 를 allowed_networks 에 담는다
    # 5. network 가 allowed_networks 안에 있는지(in)의 결과(True 또는 False)를 리턴한다


def evaluate_conditional(user, resource, action, network, now, rules):   # 사용자 · 자원 · 행위 · 접속 위치 · 요청 시각(datetime) · 조건 리스트를 받는 함수
    """(허용 여부, 이유)를 리턴한다. 기본 판정이 허용이어도 그 권한의 조건(업무 시간 · 접속 위치)에 어긋나면 거부한다."""
    ok, reason = evaluate_access(user, resource, action, now)    # 먼저 10/22(목)의 기본 판정을 한다 (미리 채움)
    if not ok:                                                   # 기본 판정이 거부이면
        return False, reason                                     # 그 이유로 바로 거부한다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    for rule in rules:                                           # 조건을 하나씩 꺼낸다
        if rule["permission"] == permission:                     # 이 권한에 걸린 조건이면
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 6. is_work_time(rule, now) 가 거짓이면 (if not …)
            # 7.   False, "업무 시간 밖" 을 리턴한다
            # 8. is_allowed_network(rule, network) 가 거짓이면 (if not …)
            # 9.   False, "허용되지 않은 접속 위치" 를 리턴한다
    return True, reason                                          # 어긋나는 조건이 없으면 기본 판정의 이유로 허용한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다.
  - `is_work_time` · `is_allowed_network`: 함수 안이라 앞에 공백 4개입니다(1 ~ 5번).
  - `evaluate_conditional`: 미리 채운 `if rule["permission"] == permission:` 의 안쪽이라 앞에 공백 12개이고, `if` 안쪽 `return`(7번 · 9번)은 4개 더(16개)입니다.
  - 나머지 줄은 미리 채워 두었으니 그대로 둡니다.
- 3번의 `start <= hour < end` 는 start 이상이고 end 미만인지의 참 · 거짓입니다. 이 결과를 그대로 `return` 하므로 `if` 가 필요 없습니다.
- 6번 · 8번의 `not` 은 함수가 리턴한 참과 거짓을 뒤집습니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다(파이썬 버전에 따라 뒤에 `after 'if' statement on line …` 가 붙습니다). `evaluate_conditional` 의 `if` 아래에 실행할 줄이 아직 없기 때문입니다. `is_work_time` · `is_allowed_network` 는 채우기 전에 아무것도 리턴하지 않습니다.

**`day05_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 요청 여덟 건을 시각까지 정해 판정하고, 조건 파일의 조건을 출력합니다.

```python
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from conditional import load_rules, evaluate_conditional         # 방금 만든 조건 판정 함수를 불러온다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 문자열의 형식
RULES = load_rules("config/conditions.json")                     # 조건 파일을 읽는다

CASES = [                                                        # 시험할 요청 여덟 건. (사용자, 자원, 행위, 접속 위치, 시각)
    ("seoyeon", "SALES", "QUERY", "office", "2026-10-30 10:00"),     # 1. 조건이 없는 조회 권한
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 09:00"),    # 2. 시작 시각 정각, 사내망
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 18:00"),    # 3. 끝 시각 정각
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 10:00"),  # 4. 업무 시간 안, 외부 접속
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 22:00"),  # 5. 시간도 위치도 어긋남
    ("junho", "SETTLE", "QUERY", "vpn", "2026-10-30 19:30"),         # 6. 정산 조회는 20시까지
    ("gaeun", "ACCOUNT", "CHANGE", "vpn", "2026-10-30 10:00"),       # 7. 계정 변경은 사내망만
    ("dami", "SALES", "QUERY", "office", "2026-10-30 10:00"),        # 8. 퇴사한 사용자
]

print("--- 단계 1: 판정 - 요청", len(CASES), "건")                  # 단계 1 시작을 알리는 줄
number = 0                                                       # 요청 번호를 0 으로 시작한다
for user, resource, action, network, time_text in CASES:         # 요청을 하나씩 꺼낸다
    number += 1                                                  # 요청 번호를 1 늘린다
    now = datetime.strptime(time_text, TIME_FORMAT)              # 시각 문자열을 시각으로 바꾼다
    ok, reason = evaluate_conditional(user, resource, action, network, now, RULES)   # 조건까지 판정한다
    if ok:                                                       # 허용이면
        result = "허용"                                           # 허용이라고 적는다
    else:                                                        # 거부이면
        result = "거부"                                           # 거부라고 적는다
    permission = f"{resource}:{action}"                          # 권한 문자열을 만든다
    time_text = now.strftime("%H:%M")                            # 시각을 「시:분」 문자열로 바꾼다
    verdict = f"{result}({reason})"                              # 결과와 이유를 합친다
    print(number, user, permission, network, time_text, "->", verdict)  # 번호 · 요청과 결과를 출력한다

print("--- 단계 2: 확인 - 조건 파일에 적힌 조건")                      # 단계 2 시작을 알리는 줄
for rule in RULES:                                               # 조건을 하나씩 꺼낸다
    hours = rule["hours"]                                        # 허용 시간대 [시작 시, 끝 시]
    hours_text = f"{hours[0]}시부터 {hours[1]}시 전까지"                # 시간대를 문자열로 만든다
    networks_text = ", ".join(rule["networks"])                  # 허용 접속 위치를 쉼표로 이어 붙인다
    print(rule["permission"], "|", hours_text, "|", networks_text)  # 권한 | 시간대 | 허용 접속 위치를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `config/conditions.json` · `conditional.py` · `day05_5-1_run.py` 를 만들어 위 코드를 붙여 넣습니다. 만드는 법은 둘 중 하나를 고릅니다.
   - VS Code: `access_control` 폴더를 선택하고 **새 파일**(New File) 아이콘을 눌러 이름을 입력합니다(`config/…` 이름은 이 폴더를 선택한 채 입력하면 `config` 폴더 안에 만들어집니다).
   - 터미널: `pwd` 로 `access_control` 인지 확인하고 `touch 이름` 으로 만든 뒤 VS Code 에서 열어 붙여 넣습니다(`vim 이름` → `i` → 붙여넣기 → `Esc` → `:wq` 도 됩니다).
2. **[터미널]** `ls config` 로 `conditions.json` 이 `users.json` 과 같은 `config` 폴더에 있는지 보고, `python -m json.tool config/conditions.json`(맥북은 `python3`)로 내용이 정상인지 확인합니다.
   - 깨진 채 두면 `[경고] 설정 파일 깨짐: config/conditions.json` 이 찍히고, 조건을 읽지 못해 조건 없이 허용됩니다.
3. **[VS Code]** `conditional.py` 의 `is_work_time` · `is_allowed_network` · `evaluate_conditional` 에서 직접 쓰는 곳 세 군데를 씁니다. 5.1 의 표와 그림, 문법 상자를 보고 씁니다.
4. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_5-1_run.py
   ```
5. 출력은 두 단계입니다. 단계 1은 `요청 8 건` 줄과 판정 여덟 줄, 단계 2는 조건 세 줄입니다.
6. **[보고서]** `day05_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 허용된 요청과 거부된 요청이 각각 몇 건인지, 조건 때문에 거부된 요청이 몇 건이고 몇 번인지 적어 주세요.
   - (나) 🔍 5번 요청(seoyeon, 외부, 22시)은 업무 시간도 접속 위치도 어긋나는데 거부 이유는 「업무 시간 밖」 하나만 나옵니다. 거부 이유를 하나만 알려 주는 것과 어긋난 조건을 모두 알려 주는 것 중, 요청한 사람이 정상 사용자인 경우와 계정을 가로챈 사람인 경우 각각 어느 쪽이 나은지, 판정 결과를 점검하는 관제 담당자에게는 어느 쪽이 나은지 이유와 함께 적어 주세요.
   - (다) 🔍 seoyeon 의 계정을 다른 사람이 새벽 2시에 외부에서 쓰려 한다고 해 봅시다. 계정에 `SALES:CHANGE` 역할 권한이 있는데도 이 요청을 거부해야 하는 이유와, 로그인할 때 한 번만 확인하고 그 뒤 요청은 확인하지 않았다면 어떻게 되었을지 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 기본 판정 먼저 | `ok, reason = evaluate_access(user, resource, action, now)` (미리 채움) |
| 기본 판정이 거부이면 | `if not ok:` → `return False, reason` (미리 채움) |
| 요청 시각의 시 | `hour = now.hour` (`is_work_time` 안) |
| 시간대 안인지 | `return start <= hour < end` (끝 시각은 포함하지 않음) |
| 접속 위치가 허용 리스트에 있는지 | `allowed_networks = rule["networks"]` → `return network in allowed_networks` (`is_allowed_network` 안) |
| 조건에 어긋나면 거부 | `if not is_work_time(rule, now):` · `if not is_allowed_network(rule, network):` → `return False, …` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 판정 서버 만들고 요청 로그 남기기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「지금은 판정 함수를 파이썬 파일 안에서만 쓸 수 있습니다. 사내의 다른 프로그램이 「이 사용자가 지금 이 권한을 쓸 수 있나」를 물으려면 주소로 물을 수 있어야 합니다.
>
> 판정을 주소로 요청해 받을 수 있는 서버로 만들어 주세요. 허용이면 200, 거부면 403, 요청에 빠진 값이 있으면 400으로 답하고(처리 결과를 알리는 숫자를 상태 코드라고 합니다), 요청마다 로그를 한 줄씩 남겨 주세요.」
> - **왜 중요한가**: 판정을 한곳에 두고 여러 프로그램이 같은 주소로 물으면 규칙이 한 군데에만 있어서 서로 어긋나지 않습니다. 로그가 있으면 누가 언제 무엇을 요청했는지 나중에 볼 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 판정 함수를 `import` 해서 쓰면 그 파일을 가진 프로그램만 쓸 수 있습니다. **서버**로 만들면 주소만 알면 어떤 프로그램이든 같은 규칙으로 물을 수 있습니다.
2. 서버는 켜 두고 요청을 기다리는 프로그램입니다.
   - 서버를 켠 터미널(터미널 1)은 계속 실행 중이라 다른 일을 못 하므로, 요청은 다른 터미널(터미널 2)에서 보냅니다.
   - VS Code 터미널 창 오른쪽의 터미널 리스트에서 이름을 누르면 그 터미널 화면으로 바뀝니다.
3. 1과목에서는 노트북 셀 안에서 서버를 만들었습니다. 오늘은 **파일**(`access_server.py`)로 만들어 터미널에서 켭니다.

### 📖 6.1 서버와 요청의 구조

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

```
+---------------------------------------------------------+
| 요청을 보내는 쪽 (터미널 2에서 실행하는 send_checks.py) |
+---------------------------------------------------------+
   |
   |  요청: /check?user=…&resource=…&action=…&network=…&time=…
   v
+--------------------------------------------+
| 서버 쪽 (터미널 1에서 켠 access_server.py) |
+--------------------------------------------+
   |
   |  응답: 상태 코드(200 · 403 · 400)와 {"allowed": …, "reason": …}
   v
요청을 보내는 쪽이 응답을 받는다
```

**주소**(URL · 유알엘)는 서버의 위치를 적은 문자열입니다. 서버 주소(`http://127.0.0.1:5001`) 뒤에 서버 안의 위치인 경로 `/check` 를 붙이고, `?` 뒤에 값 다섯 개를 `이름=값` 으로 이어 붙인 전체를 **요청 주소**라고 부릅니다.

| 주소의 이름 | 뜻 | 값의 예 |
|---|---|---|
| `user` | 사용자 | `seoyeon` |
| `resource` · `action` | 자원 · 행위 | `SALES` · `CHANGE` |
| `network` | 접속 위치 | `office` |
| `time` | 요청 시각. 실습에서는 같은 결과가 나오도록 직접 넣습니다. 5교시 실행 파일의 `2026-10-30 10:00` 과 달리 주소에서는 공백 대신 `T` 를 씁니다 | `2026-10-30T10:00` |

응답의 **상태 코드**는 요청이 어떻게 처리됐는지를 숫자로 알려 줍니다. 앞자리 `2` 는 성공, `4` 는 **요청을 보낸 쪽에서 고치거나 받아들여야 하는 경우**입니다(1과목에서 배웠습니다).

| 상태 코드 | 뜻 | 이 서버에서 |
|---|---|---|
| 200 | 성공 | 판정이 **허용** |
| 403 | **누구인지는 알겠는데 안 된다.** 요청은 올바르게 도착했지만 **인가**(이 일을 해도 되나)에서 막힘 | 판정이 **거부**(퇴사한 계정 · 권한 없음 · 업무 시간 밖 · 허용되지 않은 접속 위치) |
| 400 | 보낸 쪽 잘못: 요청이 잘못됨 | 요청에 값이 빠졌거나 시각 형식이 틀림(둘 다 「입력이 잘못됨」으로 답함) |

- 403 은 1과목의 `401` 과 다릅니다.
  - `401` 은 「당신이 누구인지 모르겠다」(인증에서 막힘)입니다.
  - 이 서버는 비밀번호나 토큰으로 사용자를 확인하는 단계(인증)가 없고 요청에 적힌 사용자 이름을 그대로 믿으므로 `401` 은 쓰지 않습니다.
- **직접 쓰는 곳은 세 함수**입니다. 판단이 필요한 함수마다 1 ~ 4줄만 쓰고, 나머지는 미리 채웠습니다.
  - `parse_time`(1 · 2번): 시각 문자열을 시각으로 바꾸고, 모양이 틀리면 `None` 을 리턴합니다.
  - `write_log`(3번): 로그 파일을 여는 모드를 정합니다(덧붙이기 `"a"`).
  - `check`(4 ~ 7번): 5교시의 `evaluate_conditional` 로 판정하고 200 · 403 으로 답합니다.
- **미리 채운 것**
  - `parse_time` 의 `if text is None:` 과 `try` · `except` 틀, `write_log` 의 파일 열기와 쓰기 줄
  - `check` 안의 주소에서 값 다섯 개를 꺼내는 다섯 줄, 값이 빠졌을 때 400 으로 답하는 두 줄, 요청 로그를 남기는 `log_entry` 와 `write_log` 줄
  - 서버를 켜는 맨 아래 두 줄
- **로그**(log)는 요청마다 한 줄씩 남기는 기록 파일(`server_log.jsonl`)입니다.
  - `.jsonl` 은 한 줄에 JSON 한 건씩 적은 파일입니다(JSON Lines · 제이슨 라인즈).
  - 400 으로 답한 요청은 판정을 하지 않아 로그에 남기지 않으므로, 로그 줄 수가 보낸 요청 수보다 적을 수 있습니다.
- `write_log` 는 로그 파일을 `"a"`(덧붙이기) 모드로 엽니다.
  - `"a"` 는 기존 내용 뒤에 쓰고, `"w"`(쓰기)는 열 때마다 내용을 지웁니다. 로그는 쌓아 두어야 해서 `"a"` 를 씁니다.
  - 남기는 `time` 은 시각으로 바꾼 `now` 가 아니라 주소에 적혀 온 글자 그대로입니다.
- **포트**(port)는 서버가 요청을 기다리는 번호입니다.
  - 서버는 `5001` 번 포트로 켜고, 주소는 `http://127.0.0.1:5001` 입니다(`127.0.0.1` 은 내 PC 자신입니다).
- 이 실습에서는 `network` 와 `time` 을 요청하는 쪽이 주소에 적어 보냅니다.
  - 요청하는 쪽이 적은 값은 거짓으로 적을 수 있습니다. 실제 서비스에서는 서버가 접속 위치와 시각을 직접 알아내야 합니다.
- **요청을 보내는 쪽** `send_checks.py` 가 하는 일
  - 요청 아홉 건을 `requests.get(주소, params=딕셔너리)` 로 서버에 보냅니다(1과목과 같은 방식). 딕셔너리의 키와 값이 주소의 `?user=…&resource=…` 가 됩니다.
  - 응답에서 `response.status_code`(상태 코드)와 `response.json()`(내용)을 꺼냅니다.
  - 서버가 남긴 로그 파일을 한 줄씩 읽어 `json.loads(line)` 으로 딕셔너리로 바꿉니다(로그는 한 줄에 JSON 한 건).
  - 9번 요청은 일부러 `network` 를 빠뜨려 400 이 나오고 로그에는 남지 않습니다.
  - 시작할 때 이전 로그 파일을 지웁니다(이번 요청 로그만 보려는 시험용이고, 실제 서비스에서는 로그를 보관합니다).

**🐍 문법 상자 — 주소에서 값 꺼내기**

**`request.args.get("이름")` 은 주소의 `?이름=값` 에서 값을 꺼냅니다**

| 주소 | 코드 | 값 |
|---|---|---|
| `/check?user=seoyeon&network=office` | `request.args.get("user")` | `"seoyeon"` |
| `/check?user=seoyeon&network=office` | `request.args.get("network")` | `"office"` |
| `/check?user=seoyeon&network=office` | `request.args.get("time")` | `None` (주소에 없음) |

- 주소에 없는 이름은 오류가 아니라 `None` 이 나옵니다. 딕셔너리의 `.get` 과 같습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 판정 서버를 만들고 요청마다 로그 남기기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 판정 함수는 파이썬 파일 안에서만 부를 수 있습니다. 다른 프로그램은 쓸 수 없고, 누가 언제 물었는지 로그도 없습니다.
- **그래서 만드는 것**: `access_server.py` 의 `check` 함수입니다.
  - 주소에서 꺼낸 다섯 값에 빠진 것이 있으면 400, 없으면 5교시의 `evaluate_conditional` 로 판정하고, 요청 로그를 한 줄 남기고, 허용이면 200 · 거부면 403 으로 답합니다.
- **실행하면**: 서버가 켜지고 터미널 1이 요청을 기다립니다. 터미널 2에서 `send_checks.py` 를 실행하면 요청 아홉 건을 보내고, 응답과 서버가 남긴 로그를 세 단계로 출력합니다.
- **현업에서는**: 접근 제어 서비스도 판정을 주소로 받을 수 있게 하고, 요청마다 로그를 남깁니다.

**🎯 할 일**

1. `access_server.py` 와 `send_checks.py` 두 파일을 만들고, `parse_time` · `write_log` · `check` 에서 직접 쓰는 곳 네 군데를 씁니다. 5교시의 `conditional.py` 와 `config/conditions.json` 이 필요합니다.
2. 터미널 1에서 서버를 켜고, 터미널 2에서 `send_checks.py` 를 실행해 <mark>응답</mark>(단계 1: 응답), <mark>서버 로그</mark>(단계 2: 로그), <mark>대조 결과</mark>(단계 3: 대조)를 읽습니다.

**`access_server.py`**

```python
import json                                                      # JSON 문자열을 만드는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from flask import Flask, request                                 # 서버를 만드는 Flask 와 요청 정보를 담은 request 를 불러온다
from conditional import load_rules, evaluate_conditional         # 5교시에 만든 조건 판정 함수를 불러온다

app = Flask(__name__)                                            # 서버 프로그램을 만든다
app.json.ensure_ascii = False                                    # 응답의 한글이 \uXXXX 로 깨지지 않게 한다
RULES = load_rules("config/conditions.json")                     # 조건 파일을 서버를 켤 때 한 번 읽는다
LOG_PATH = "server_log.jsonl"                                    # 요청 로그를 남길 파일 이름
TIME_FORMAT = "%Y-%m-%dT%H:%M"                                   # 주소로 받는 시각 문자열의 형식(예: 2026-10-30T10:00)


def parse_time(text):                                            # 시각 문자열을 받는 함수
    """2026-10-30T10:00 모양 문자열을 시각으로 바꿔 리턴한다. 문자열이 없거나 모양이 틀리면 None 을 리턴한다."""
    if text is None:                                             # 시각 문자열이 아예 없으면
        return None                                              # 없다고 알린다
    try:                                                         # 아래를 시도한다 (미리 채움)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. datetime.strptime(text, TIME_FORMAT) 의 결과(시각)를 리턴한다
    except ValueError:                                           # 모양이 틀렸으면 (미리 채움)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. None 을 리턴한다 (없다고 알린다)


def write_log(entry):                                            # 로그에 쓸 딕셔너리를 받는 함수
    """딕셔너리 한 건을 JSON 한 줄로 만들어 로그 파일 끝에 덧붙인다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. 파일을 여는 모드 "a"(덧붙이기: 기존 내용 뒤에 쓴다)를 mode 에 담는다
    with open(LOG_PATH, mode, encoding="utf-8") as f:            # 파일을 mode(덧붙이기 모드)로 연다
        text = json.dumps(entry, ensure_ascii=False)             # 딕셔너리를 JSON 문자열로 만든다(한글은 그대로)
        f.write(text + "\n")                                     # 한 줄로 파일 끝에 쓴다


@app.route("/check")                                             # 주소 /check 로 오는 요청을 아래 함수가 받는다
def check():                                                     # 요청 한 건을 처리하는 함수
    """주소의 user · resource · action · network · time 으로 판정하고, 허용이면 200, 거부이면 403, 값이 빠졌으면 400 으로 답한다."""
    user = request.args.get("user")                              # 요청 주소에서 user 값을 꺼낸다(주소에 없으면 None)
    resource = request.args.get("resource")                      # 요청 주소에서 resource 값을 꺼낸다
    action = request.args.get("action")                          # 요청 주소에서 action 값을 꺼낸다
    network = request.args.get("network")                        # 요청 주소에서 network 값을 꺼낸다
    time_text = request.args.get("time")                         # 요청 주소에서 time 값을 꺼낸다(없으면 None)
    now = parse_time(time_text)                                  # 시각으로 바꾼다(없거나 모양이 틀리면 None)
    if None in (user, resource, action, network, now):           # 빠졌거나 모양이 틀린 값이 하나라도 있으면 (미리 채움)
        return {"allowed": False, "reason": "입력이 잘못됨"}, 400   # 요청이 잘못됐다는 상태 코드 400 으로 답한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. evaluate_conditional(user, resource, action, network, now, RULES) 의 결과를 allowed, reason 으로 받는다
    log_entry = {
        "time": request.args.get("time"),                        # 시각
        "user": user,                                            # 사용자
        "permission": f"{resource}:{action}",                    # 권한
        "network": network,                                      # 접속 위치
        "allowed": allowed,                                      # 허용 여부
        "reason": reason,                                        # 이유
    }
    write_log(log_entry)                                         # 요청 로그를 한 줄 덧붙인다 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. allowed 가 참이면
    # 6.   {"allowed": True, "reason": reason} 과 상태 코드 200 을 함께 리턴한다
    # 7. {"allowed": False, "reason": reason} 과 상태 코드 403 을 함께 리턴한다 (if 밖, 함수 안쪽 줄에 맞춘다)

if __name__ == "__main__":                                       # 이 파일을 직접 실행했을 때만
    app.run(port=5001)                                           # 5001번 포트로 서버를 켠다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다.
  - `parse_time`: 미리 채운 `try` · `except` 안쪽이라 8개입니다(1 · 2번).
  - `write_log`: 함수 안이라 4개입니다(3번).
  - `check`: 함수 안이라 4개이고, 5번 `if allowed:` 도 4개입니다. `if` 안쪽 `return`(6번)은 4개 더(8개)이고, 7번 `return` 은 `if` 밖이라 4개입니다.
  - 400 으로 답하는 `if None in …` 과 `log_entry` · `write_log` 줄은 미리 채워 두었으니 그대로 둡니다.
- 6번 · 7번의 `return` 은 `return 딕셔너리, 상태코드` 로 두 값을 함께 리턴합니다.
  - 상태 코드가 응답의 숫자가 됩니다.
  - 1과목에서 `return {…}, 200` 으로 쓴 방식과 같습니다.
- 미리 채운 `None in (…)` 는 괄호 안 값 중 `None` 이 하나라도 있으면 참입니다.
  - 예: `None in ("seoyeon", None)` 는 `True`, `None in ("seoyeon", "office")` 는 `False` 입니다.
- 채우기 전에 서버를 켜면 `IndentationError: expected an indented block` 오류가 납니다.
  - `parse_time` 의 `try` 아래에 실행할 줄이 아직 없기 때문입니다.

**`send_checks.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 서버에 요청 아홉 건을 보내 응답을 출력하고, 서버가 남긴 로그를 읽어 출력하고, 둘을 대조합니다.

```python
import json                                                      # JSON 문자열을 읽는 모듈을 불러온다
import os                                                        # 파일이 있는지 보고 지우는 데 쓴다
import requests                                                  # 서버에 요청을 보내는 모듈을 불러온다

BASE_URL = "http://127.0.0.1:5001"                               # 서버 주소
LOG_PATH = "server_log.jsonl"                                    # 서버가 남기는 로그 파일 이름
CASES = [                                                        # 서버에 보낼 요청 아홉 건. 주소의 ?user=… 로 들어가는 값이다
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "office", "time": "2026-10-30T09:00"},     # 1. 시작 시각 정각, 사내망
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "office", "time": "2026-10-30T18:00"},     # 2. 끝 시각 정각
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "external", "time": "2026-10-30T10:00"},   # 3. 외부 접속
    {"user": "seoyeon", "resource": "SALES", "action": "QUERY", "network": "external", "time": "2026-10-30T23:00"},    # 4. 조건이 없는 조회
    {"user": "junho", "resource": "SETTLE", "action": "QUERY", "network": "vpn", "time": "2026-10-30T19:30"},          # 5. 정산 조회는 20시까지
    {"user": "junho", "resource": "SETTLE", "action": "QUERY", "network": "external", "time": "2026-10-30T10:00"},     # 6. 외부 접속
    {"user": "gaeun", "resource": "ACCOUNT", "action": "CHANGE", "network": "vpn", "time": "2026-10-30T10:00"},        # 7. 계정 변경은 사내망만
    {"user": "dami", "resource": "SALES", "action": "QUERY", "network": "office", "time": "2026-10-30T10:00"},         # 8. 퇴사한 사용자
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "time": "2026-10-30T10:00"},                          # 9. 접속 위치(network)를 빠뜨린 요청
]

if os.path.exists(LOG_PATH):                                     # 이전에 남은 로그 파일이 있으면
    os.remove(LOG_PATH)                                          # 지운다(이번 요청 로그만 보려고. 실제 서비스에서는 로그를 지우지 않고 보관한다)

print("--- 단계 1: 응답 - 요청", len(CASES), "건")               # 단계 1 시작을 알리는 줄
results = []                                                     # 서버의 응답을 담을 빈 리스트
case_count = len(CASES)                                          # 개수를 먼저 구한다
for i in range(case_count):                                      # 번호 i 로 요청을 하나씩 꺼낸다
    case = CASES[i]                                              # i 번째 요청
    response = requests.get(BASE_URL + "/check", params=case)    # 서버의 /check 에 요청을 보낸다(params 의 값이 주소의 ?user=… 가 된다)
    body = response.json()                                       # 응답의 JSON 문자열을 딕셔너리로 바꾼다
    result = {
        "status": response.status_code,                          # 응답 상태 코드
        "allowed": body["allowed"],                              # 허용 여부
        "reason": body["reason"],                                # 이유
    }
    results.append(result)                                       # 상태 코드 · 허용 여부 · 이유를 응답 리스트에 추가한다
    permission = case["resource"] + ":" + case["action"]         # 자원과 행위를 : 로 이어 붙여 권한 문자열을 만든다
    print(i + 1, case["user"], permission, "->", response.status_code, body["reason"])  # 번호 · 사용자 · 권한 -> 상태 코드 · 이유를 출력한다

entries = []                                                     # 로그에서 읽은 기록을 담을 빈 리스트
with open(LOG_PATH, encoding="utf-8") as f:                      # 로그 파일을 읽기 모드로 연다
    for line in f:                                               # 파일에서 한 줄씩 꺼낸다
        entry = json.loads(line)                                 # JSON 한 줄을 딕셔너리로 바꾼다
        entries.append(entry)                                    # 그 줄의 JSON 문자열을 딕셔너리로 바꿔 추가한다
print("--- 단계 2: 로그 - 서버가 남긴", len(entries), "줄")      # 단계 2 시작을 알리는 줄
for entry in entries:                                            # 로그의 기록을 하나씩 꺼낸다
    print(entry["user"], entry["permission"], entry["network"], entry["time"], "->", entry["allowed"], entry["reason"])  # 사용자 · 권한 · 접속 위치 · 시각 -> 결과를 출력한다

answered = 0                                                     # 판정까지 간 응답 수를 0 으로 시작한다
for result in results:                                           # 응답을 하나씩 꺼낸다
    if result["status"] != 400:                                  # 입력 부족(400)이 아니면 서버가 판정까지 한 것이다
        answered = answered + 1                                  # 판정까지 간 응답 수를 1 늘린다
print("--- 단계 3: 대조 - 판정까지 간 응답과 로그")              # 단계 3 시작을 알리는 줄
print("판정까지 간 응답", answered, "건 / 로그에 남은 줄", len(entries), "줄")  # 두 수가 같은지 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `access_server.py` · `send_checks.py` 를 만들어 위 코드를 붙여 넣습니다. 만드는 법은 둘 중 하나를 고릅니다.
   - VS Code: `access_control` 폴더를 선택하고 **새 파일**(New File) 아이콘을 눌러 이름을 입력합니다.
   - 터미널: `pwd` 로 `access_control` 인지 확인하고 `touch 이름` 으로 만든 뒤 VS Code 에서 열어 붙여 넣습니다(`vim 이름` → `i` → 붙여넣기 → `Esc` → `:wq` 도 됩니다).
2. **[VS Code]** `access_server.py` 의 `parse_time` · `write_log` · `check` 에서 직접 쓰는 곳 네 군데를 씁니다. 6.1 의 표와 그림을 보고 씁니다.
3. **[터미널 1]** 서버를 켭니다(맥북은 `python3`).
   ```bash
   pwd
   python access_server.py
   ```
   - `Running on http://127.0.0.1:5001` 이 나오고 입력을 받지 않으면 정상입니다. 이 터미널은 켠 채로 두고 다른 명령을 치지 않습니다.
   - `Address already in use` 가 나오면 이미 켜진 서버가 있는 것이니, 그 터미널에서 `Ctrl + C` 로 끄고 다시 켭니다.
   - 코드나 `config/conditions.json` 을 고쳤으면 `Ctrl + C` 로 끄고 다시 켭니다(서버는 켤 때 한 번만 읽습니다).
   - 켤 때 `[경고] 설정 파일 …` 줄이 나오면 5교시의 `config/conditions.json` 을 확인합니다.
4. **[터미널 2]** VS Code 터미널 창 오른쪽 위의 `+` 단추로 새 터미널을 엽니다(서버를 켠 터미널은 그대로 둡니다).
   ```bash
   cd access_control
   pwd
   python send_checks.py
   ```
   - 새 터미널이 이미 `access_control` 에서 열렸다면 `cd access_control` 은 건너뜁니다(맥북은 `python3`, 결과 줄 앞의 `NotOpenSSLWarning` 은 무시합니다).
   - `Connection refused` 가 나오면 터미널 1에서 서버가 켜져 있는지 확인합니다.
   - `No module named 'requests'` 가 나오면 `pip install requests`(맥북은 `pip3`)를 치고 다시 실행합니다.
5. 출력은 세 단계입니다. 단계 1은 `요청 9 건` 제목 줄과 응답 아홉 줄, 단계 2는 `서버가 남긴 8 줄` 제목 줄과 로그 여덟 줄, 단계 3은 대조 두 줄입니다.
6. **[터미널 1]** 서버를 켠 터미널(오른쪽 터미널 리스트에서 선택)에는 요청마다 `"GET /check?… HTTP/1.1" 200 -` 줄이 찍혔습니다. 끝의 숫자가 상태 코드입니다.
   - 확인한 뒤 그 터미널에서 `Ctrl + C` 로 서버를 끕니다(Windows 에서 안 꺼지면 한 번 더 누릅니다).
7. **[보고서]** `day05_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 터미널 2의 출력 전체를 붙여 넣고, 응답의 상태 코드별 건수(200 · 403 · 400)와 서버가 남긴 로그 줄 수를 적어 주세요.
   - (나) 🔍 거부는 403, 값이 빠진 요청은 400 으로 상태 코드를 다르게 답했습니다. 요청을 보내는 쪽이 이 둘을 구별해야 하는 이유와, 구별하지 않으면 생길 수 있는 일을 적어 주세요.
   - (다) 🔍 서버 로그를 요청마다 새로 쓰면(`"w"` 모드) 한 달 뒤에 지난주의 거부 기록을 찾으려 할 때 어떻게 되나요? 로그에는 끝에 덧붙이는 방식이 알맞은 이유를 적어 주세요.

### 🆘 서버가 안 켜지거나 오류가 나면 — AI 에게 이렇게 물어봅니다

- 먼저 확인합니다.
  - 터미널 맨 앞에 가상환경 이름(예: `(.venv)`)이 보이면 가상환경이 켜진 것입니다.
  - 서버를 켠 터미널(터미널 1)과 요청을 보내는 터미널(터미널 2)을 헷갈리지 않았는지 봅니다.
- AI 에게 물을 때는 아래 세 가지를 함께 적습니다.
  - 내 운영체제(Windows 인지 맥북인지)와 터미널 종류(Git Bash 등)
  - 내가 친 명령 한 줄
  - 화면에 나온 오류 전체(`.env` 의 내용이나 API 키가 화면에 있으면 지우고 붙여 넣습니다)

**① `No module named 'flask'` 또는 `No module named 'requests'`** — 가상환경이 안 켜졌거나 도구가 설치되지 않은 경우입니다.

```text
Windows 의 VS Code 터미널(Git Bash)에서 `python access_server.py` 를 쳤더니 아래 오류가 나옵니다.
파이썬 가상환경이 켜져 있는지 확인하는 방법과, 이 가상환경에 flask 와 requests 를 설치하는 명령을 알려 주세요.
오류: (여기에 붙여 넣기)
```

- 답으로 받은 설치 명령이 `python -m pip install flask requests` 처럼 `python -m pip` 로 시작하면, 지금 쓰는 파이썬에 설치됩니다.

**② 터미널 2 에서 `No module named 'requests'`** — 새로 연 터미널에는 가상환경이 안 켜져 있을 수 있습니다.

```text
VS Code 에서 터미널을 새로 열고 `python send_checks.py` 를 쳤더니 `No module named 'requests'` 가 나옵니다.
처음 열었던 터미널에서는 같은 도구가 잘 됩니다. 새 터미널에서 가상환경을 켜는 방법을 알려 주세요.
```

**③ `Address already in use`** — 이미 켜진 서버가 5001번 포트를 쓰고 있습니다.

- 서버를 켰던 터미널을 찾으면 그 터미널에서 `Ctrl + C` 로 끄는 것이 가장 쉽습니다.
- 못 찾겠으면 AI 에게 이렇게 묻습니다.

```text
`python access_server.py` 를 켰더니 `Address already in use` 가 나옵니다.
Windows(Git Bash)에서 5001번 포트를 쓰는 프로그램을 찾아서 끄는 방법을 한 단계씩 알려 주세요. 파일을 지우는 명령은 빼 주세요.
```

- 주의할 것
  - AI 가 알려 준 명령은 치기 전에 무슨 뜻인지 한 줄씩 읽습니다.
  - `rm` · `del` · `kill` 처럼 지우거나 강제로 끄는 명령은 무슨 뜻인지 AI 에게 되물은 뒤에 칩니다.
  - 그래도 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: 오류 화면의 내용」이라고 쓰고 다음 단계로 넘어갑니다.

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 주소에서 값 꺼내기 | `user = request.args.get("user")` (미리 채움) |
| 값이 하나라도 빠졌는지 | `if None in (user, resource, action, network, now):` (미리 채움) |
| 상태 코드와 함께 답하기 | `return {"allowed": True, "reason": reason}, 200` |
| 요청 로그 한 줄 남기기 | `write_log(log_entry)` (이 줄은 미리 채움) |
| 로그 파일 여는 모드 | `mode = "a"` (`write_log` 안. 덧붙이기) |
| 시각 문자열 바꾸기 | `try:` → `return datetime.strptime(text, TIME_FORMAT)` · `except ValueError:` → `return None` (`parse_time` 안) |
| 서버 켜기 · 끄기 | `python access_server.py` · `Ctrl + C` |
| 요청 보내기 | `python send_checks.py` (다른 터미널) |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다. 6교시 마지막 10분에 합니다. 서버를 끈 뒤에는 터미널 1 이나 터미널 2 중 아무 터미널을 써도 됩니다. 어느 쪽이든 `pwd` 로 위치를 먼저 확인하고, 결과가 `access_control` 로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: 팀장이 「오늘 오전에 만든 회수 코드(`revoke.py` 등)와 오후에 만든 판정 서버를 저장소에 남겨 달라」고 합니다.
- **그래서 하는 것**: 올라갈 파일을 `git status` 로 먼저 확인하고(비밀 키 파일 `.env` 가 섞이면 안 됩니다), `git add` → `git commit` → `git push` 로 올립니다.
- **끝나면**: 깃허브 저장소의 `access_control` 폴더에서 오늘 만든 파일이 모두 보입니다.

**순서**

1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 결과가 `…/security-agent-toolkit` 으로 끝나야 합니다.
   ```bash
   cd ..
   pwd
   ```
   - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `pwd` 지금 위치 확인
   - 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.
     - 새로 연 뒤 `pwd` 를 한 번 더 쳐서 확인합니다.
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. 빨간 목록에 `.env` 나 `.venv` 가 보이면 올리지 않고 멈춥니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 올릴 파일의 상태를 봄
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 도 같은 방법으로 합니다.
   - 어제(10/29(목))까지 올렸다면 오늘 만든 파일이 `access_control/revoke.py` 처럼 한 줄씩 보입니다.
     - 올리지 않았다면 `access_control/` 한 줄로 보일 수 있습니다.
     - 어느 쪽이든 `Untracked files:` 아래에 보이는 줄을 센 그대로 적습니다.
   - `access_control/revocation_log.json` 은 오전 4교시에, `access_control/server_log.jsonl` 은 6교시에 서버가 만든 기록 파일입니다.
     - 이것도 올라갑니다.
   - `Untracked files:` 는 「아직 깃이 모르는 새 파일」 목록입니다.
   - `access_control/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - 줄 수는 그 뒤에 다시 셉니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `Untracked files:` 아래에 줄이 몇 개 보였는지, 그중에 `.env` 나 `.venv` 가 있었는지 적어 주세요.
   - 앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다. 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add access control day 5 revocation, conditional policy and check server"
   git push
   ```
   - 명령 풀이: `git add .` 바뀐 파일을 올릴 목록에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림
   - `git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다. `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `access_control` 폴더를 열고, VS Code 왼쪽 목록의 `access_control` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. `__pycache__` 폴더는 없어도 됩니다.
   - 빠진 이름이 있으면 VS Code 왼쪽 목록의 `access_control` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `access_control` 안으로 옮기고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

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
| 기본 판정 뒤에 업무 시간과 접속 위치 조건을 확인했다 | 오후 5-1 |
| 판정 서버를 만들고, 요청을 보내 응답과 서버 로그를 대조했다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

다음 수업은 11/2(월) 오전입니다. 오늘 서버가 남긴 `server_log.jsonl` 을 읽어 **점검 체크리스트와 주간 보고서**를 만들고 3과목을 마무리합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_5-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `is_work_time` 안

```python
    start, end = rule["hours"]                                   # 허용 시작 시와 끝 시를 꺼낸다
    hour = now.hour                                              # 요청 시각의 시를 꺼낸다
    return start <= hour < end                                   # 시작 시 이상이고 끝 시 미만인지(True 또는 False)를 리턴한다
```

② `is_allowed_network` 안

```python
    allowed_networks = rule["networks"]                          # 허용된 접속 위치 리스트를 꺼낸다
    return network in allowed_networks                           # 그 리스트에 들어 있는지(True 또는 False)를 리턴한다
```

③ `evaluate_conditional` 안(미리 채운 `if rule["permission"] == permission:` 아래)

```python
            if not is_work_time(rule, now):                      # 업무 시간 안이 아니면
                return False, "업무 시간 밖"                       # 거부한다
            if not is_allowed_network(rule, network):            # 허용된 접속 위치가 아니면
                return False, "허용되지 않은 접속 위치"            # 거부한다
```

**결과**

- (가) 출력은 다음과 같고, 허용은 **3건**(1 · 2 · 6번), 거부는 **5건**입니다.
  - 조건 때문에 거부된 요청은 **4건**(3 · 4 · 5 · 7번)이고, 8번은 기본 판정에서 퇴사한 계정으로 거부됐습니다.

```
--- 단계 1: 판정 - 요청 8 건
1 seoyeon SALES:QUERY office 10:00 -> 허용(역할 권한)
2 seoyeon SALES:CHANGE office 09:00 -> 허용(역할 권한)
3 seoyeon SALES:CHANGE office 18:00 -> 거부(업무 시간 밖)
4 seoyeon SALES:CHANGE external 10:00 -> 거부(허용되지 않은 접속 위치)
5 seoyeon SALES:CHANGE external 22:00 -> 거부(업무 시간 밖)
6 junho SETTLE:QUERY vpn 19:30 -> 허용(역할 권한)
7 gaeun ACCOUNT:CHANGE vpn 10:00 -> 거부(허용되지 않은 접속 위치)
8 dami SALES:QUERY office 10:00 -> 거부(퇴사한 계정)
--- 단계 2: 확인 - 조건 파일에 적힌 조건
SALES:CHANGE | 9시부터 18시 전까지 | office, vpn
SETTLE:QUERY | 8시부터 20시 전까지 | office, vpn
ACCOUNT:CHANGE | 9시부터 18시 전까지 | office
```

- (나) 정상 사용자에게는 어긋난 조건을 모두 알려 주는 쪽이 낫습니다.
  - 한 번에 무엇을 고쳐야 하는지 알 수 있기 때문입니다.
  - 계정을 가로챈 사람에게는 이유를 하나만 알려 주는 쪽이 낫습니다.
  - 어떤 조건이 걸려 있는지 덜 알려 주기 때문입니다.
  - 두 경우가 서로 반대라서, 실제 서비스에서는 요청한 사람에게 보내는 응답에는 이유를 줄이고 서버 로그에는 어긋난 조건을 모두 남기는 방법을 많이 씁니다.
  - 관제 담당자에게는 어긋난 조건을 **모두** 아는 쪽이 낫습니다.
  - 어긋난 조건이 여러 개인 요청이 몇 건인지 세면 평소와 다른 접속이 얼마나 되는지 볼 수 있기 때문입니다.
  - 오늘 만든 코드는 첫 번째 이유만 리턴하므로, 모두 알리려면 코드를 바꿔야 합니다.
- (다) 권한이 있어도 계정을 다른 사람이 가로챘다면 그 요청은 정상 사용자가 보낸 것이 아닙니다.
  - 로그인할 때 한 번만 확인하면 가로챈 계정이 새벽 2시에 외부에서 들어와도 막지 못하고, 쓰기 권한이 있는 데이터까지 바꿀 수 있습니다.
  - 요청마다 시간과 접속 위치를 확인하면(서버가 그 값을 직접 알아낼 수 있을 때) 평소와 다른 접속을 바로 막을 수 있습니다.

**왜**

- 권한이 있다는 것만으로 모든 요청을 믿지 않고, 요청마다 조건을 함께 봅니다.
  - 기본 판정이 거부이면 조건을 볼 필요가 없어서 먼저 확인하고 바로 끝냅니다.
  - 조건은 파일에 두어서 업무 시간이 바뀌어도 코드를 고치지 않습니다.

**자주 틀리는 곳**

- `is_work_time` 의 끝 시각 비교를 `hour < end` 대신 `hour <= end` 로 쓰면 18시 정각 요청도 허용됩니다.
  - 오류는 나지 않고 결과만 달라집니다.
  - 실행하면 다음처럼 됩니다(3번 줄 18:00 요청이 허용으로 나오면 이 실수입니다).

```
--- 단계 1: 판정 - 요청 8 건
1 seoyeon SALES:QUERY office 10:00 -> 허용(역할 권한)
2 seoyeon SALES:CHANGE office 09:00 -> 허용(역할 권한)
3 seoyeon SALES:CHANGE office 18:00 -> 허용(역할 권한)
…
```

**관제에서는**

- 접근 제어 서비스는 사용자를 확인한 뒤에도 접속 시간, 위치, 기기 상태를 요청마다 다시 확인하고, 평소와 다른 요청은 한 번 더 확인하거나 막습니다.
  - 오늘 단순화한 부분은 두 가지입니다.
  - 첫째, 실습에서는 접속 위치(`network`)와 시각(`time`)을 요청하는 쪽이 적어 보내지만, 실제 서비스는 서버에 접속해 온 쪽의 주소(IP)와 서버 시계로 직접 알아냅니다.
  - 둘째, 조건 파일을 읽지 못하면 오늘 코드는 조건 없이 모두 허용하는데, 실제 서비스는 읽지 못하면 서버를 켜지 않거나 모두 거부하는 쪽으로 만듭니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

터미널 1:

```bash
pwd
python access_server.py
```

터미널 2:

```bash
cd access_control
pwd
python send_checks.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수의 다섯 군데입니다.

① `parse_time` 안(미리 채운 `try` 아래)

```python
        return datetime.strptime(text, TIME_FORMAT)              # 문자열을 시각으로 바꿔 리턴한다
```

② `parse_time` 안(미리 채운 `except` 아래)

```python
        return None                                              # 모양이 틀렸으면 없다고 알린다
```

③ `write_log` 안(`with` 위)

```python
    mode = "a"                                                   # 파일을 여는 모드: 덧붙이기("a")
```

④ `check` 안(미리 채운 400 처리 아래)

```python
    allowed, reason = evaluate_conditional(user, resource, action, network, now, RULES)   # 조건까지 판정한다
```

⑤ `check` 안(미리 채운 `write_log` 줄 아래)

```python
    if allowed:                                                  # 허용이면
        return {"allowed": True, "reason": reason}, 200          # 상태 코드 200 으로 답한다
    return {"allowed": False, "reason": reason}, 403             # 거부이면 상태 코드 403 으로 답한다
```

**결과**

- (가) 출력은 다음과 같고, 상태 코드는 200 이 **3건**(1 · 4 · 5번), 403 이 **5건**(2 · 3 · 6 · 7 · 8번), 400 이 **1건**(9번)입니다.
  - 서버가 남긴 로그는 **8줄**입니다(400 요청은 기록하지 않습니다).

```
--- 단계 1: 응답 - 요청 9 건
1 seoyeon SALES:CHANGE -> 200 역할 권한
2 seoyeon SALES:CHANGE -> 403 업무 시간 밖
3 seoyeon SALES:CHANGE -> 403 허용되지 않은 접속 위치
4 seoyeon SALES:QUERY -> 200 역할 권한
5 junho SETTLE:QUERY -> 200 역할 권한
6 junho SETTLE:QUERY -> 403 허용되지 않은 접속 위치
7 gaeun ACCOUNT:CHANGE -> 403 허용되지 않은 접속 위치
8 dami SALES:QUERY -> 403 퇴사한 계정
9 seoyeon SALES:CHANGE -> 400 입력이 잘못됨
--- 단계 2: 로그 - 서버가 남긴 8 줄
seoyeon SALES:CHANGE office 2026-10-30T09:00 -> True 역할 권한
seoyeon SALES:CHANGE office 2026-10-30T18:00 -> False 업무 시간 밖
seoyeon SALES:CHANGE external 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
seoyeon SALES:QUERY external 2026-10-30T23:00 -> True 역할 권한
junho SETTLE:QUERY vpn 2026-10-30T19:30 -> True 역할 권한
junho SETTLE:QUERY external 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
gaeun ACCOUNT:CHANGE vpn 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
dami SALES:QUERY office 2026-10-30T10:00 -> False 퇴사한 계정
--- 단계 3: 대조 - 판정까지 간 응답과 로그
판정까지 간 응답 8 건 / 로그에 남은 줄 8 줄
```

- (나) 403 은 요청이 제대로 도착했고 서버가 판정(인가)까지 마친 뒤 거부했다는 뜻이라, 같은 요청을 다시 보내도 결과가 같습니다.
  - 400 은 요청 자체가 잘못됐다는 뜻이라, 값을 고쳐 다시 보내면 결과가 달라질 수 있습니다.
  - 요청을 보내는 쪽이 둘을 구별하면 400 이면 자기 프로그램의 오류로 보고 고치고, 403 이면 접근 거부로 처리할 수 있습니다.
  - 구별하지 않으면 거부를 입력 오류로 오해해 같은 요청을 계속 다시 보내거나, 입력 오류를 거부로 오해해 방치하게 됩니다.
- (다) `"w"` 로 열면 요청이 올 때마다 파일이 새로 써져서 앞의 기록이 지워지고 마지막 한 건만 남습니다.
  - 한 달 뒤에 지난주 거부 기록을 찾으면 그 기록은 이미 없습니다.
  - 로그는 시간이 지나도 앞의 기록이 남아 있어야 하므로 끝에 덧붙이는 `"a"` 방식이 알맞습니다.
  - 한 줄에 한 건씩 쓰면 파일이 아무리 커져도 한 줄씩 읽어 처리할 수 있습니다.

**왜**

- 판정을 서버로 만들어 주소로 요청하게 하면 여러 프로그램이 같은 규칙으로 물을 수 있습니다.
  - 상태 코드로 허용(200) · 거부(403) · 잘못된 요청(400)을 숫자로 구별해 알려 주고, 요청마다 한 줄씩 로그를 남겨 나중에 볼 수 있게 합니다.
  - 응답과 서버 로그를 세어 맞춰 보면 판정까지 간 요청이 빠짐없이 로그에 남았는지 알 수 있습니다.
  - 입력 오류(400)가 로그에 없다는 점도 이 대조로 알 수 있습니다.

**자주 틀리는 곳**

- 거부 응답의 상태 코드를 `403` 대신 `200` 으로 쓰면 화면에 보이는 내용은 같아서 알아채기 어렵습니다.
  - 하지만 상태 코드만 보는 프로그램은 거부를 허용으로 오해합니다.
  - 실행하면 다음처럼 됩니다(거부 요청인데 `->` 뒤 숫자가 `200` 이면 이 실수입니다).

```
--- 단계 1: 응답 - 요청 9 건
1 seoyeon SALES:CHANGE -> 200 역할 권한
2 seoyeon SALES:CHANGE -> 200 업무 시간 밖
3 seoyeon SALES:CHANGE -> 200 허용되지 않은 접속 위치
4 seoyeon SALES:QUERY -> 200 역할 권한
5 junho SETTLE:QUERY -> 200 역할 권한
6 junho SETTLE:QUERY -> 200 허용되지 않은 접속 위치
7 gaeun ACCOUNT:CHANGE -> 200 허용되지 않은 접속 위치
8 dami SALES:QUERY -> 200 퇴사한 계정
9 seoyeon SALES:CHANGE -> 400 입력이 잘못됨
--- 단계 2: 로그 - 서버가 남긴 8 줄
seoyeon SALES:CHANGE office 2026-10-30T09:00 -> True 역할 권한
seoyeon SALES:CHANGE office 2026-10-30T18:00 -> False 업무 시간 밖
seoyeon SALES:CHANGE external 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
seoyeon SALES:QUERY external 2026-10-30T23:00 -> True 역할 권한
junho SETTLE:QUERY vpn 2026-10-30T19:30 -> True 역할 권한
junho SETTLE:QUERY external 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
gaeun ACCOUNT:CHANGE vpn 2026-10-30T10:00 -> False 허용되지 않은 접속 위치
dami SALES:QUERY office 2026-10-30T10:00 -> False 퇴사한 계정
--- 단계 3: 대조 - 판정까지 간 응답과 로그
판정까지 간 응답 8 건 / 로그에 남은 줄 8 줄
```

**관제에서는**

- 판정 서버는 요청 로그를 지우지 않고 보관하고, 거부(403)가 갑자기 늘면 담당자에게 알립니다.
  - 400 도 따로 기록해 두어야 많아졌는지 알 수 있습니다.
  - 서버가 요청을 받은 시각은 서버가 직접 적어야 하고(지금은 요청한 쪽이 보낸 `time` 을 그대로 씁니다), 입력 오류 요청도 따로 기록해서 공격 시도를 찾는 데 씁니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
cd ..
pwd
git status
```

`.env` 나 `.venv` 가 없는 것을 확인한 뒤에 아래를 칩니다.

```bash
git add .
git commit -m "Add access control day 5 revocation, conditional policy and check server"
git push
```

**결과**

- (가) 한 예: 「줄이 열아홉 개였고(`.py` 열한 개 + `.json` 세 개 + `server_log.jsonl` 한 개 + `.md` 네 개), `.env` · `.venv` 는 없었다」. 이 숫자는 어제(10/29(목))까지 올렸고 `__pycache__` 가 보이지 않을 때의 숫자이며, 줄 수와 이름은 학생마다 다를 수 있습니다.
  - `.env` 나 `.venv` 가 보였다면 `.gitignore` 에 한 줄을 적고 `git status` 를 다시 쳤다고 적습니다.

**왜**

- 올리기 전에 올라갈 파일을 확인해야 비밀 키가 섞이지 않습니다.
  - 코드와 오늘 서버가 남긴 `server_log.jsonl` 이 함께 올라가야 11/2(월) 수업이 같은 로그에서 시작합니다.

**자주 틀리는 곳**

- `.env` 가 보이는데 그대로 `git add .` 를 하는 실수가 가장 위험합니다.
  - `cd ..` 를 두 번 쳐서 `security-agent-toolkit` 바깥으로 나가는 경우도 있습니다.
  - `pwd` 로 확인합니다.

**관제에서는**

- 서버 코드와 그 서버가 남긴 로그는 같은 커밋에 함께 올려, 어느 코드로 어떤 요청을 처리했는지 이력으로 남깁니다.

---


### 앞 교시 파일 완성본

앞 교시 파일이 없거나 잘 안 될 때 이 코드로 만듭니다.

**`config/conditions.json`** (5교시 완성본)

```json
[
  {"permission": "SALES:CHANGE", "hours": [9, 18], "networks": ["office", "vpn"]},
  {"permission": "SETTLE:QUERY", "hours": [8, 20], "networks": ["office", "vpn"]},
  {"permission": "ACCOUNT:CHANGE", "hours": [9, 18], "networks": ["office"]}
]
```

**`conditional.py`** (5교시 완성본)

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 기본 판정 함수를 불러온다


def load_rules(path):                                            # 조건 파일 경로를 받는 함수
    """조건 파일을 읽어 조건 딕셔너리의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽는다(못 읽으면 두 번째 값인 빈 리스트를 리턴한다)


def is_work_time(rule, now):                                     # 조건 한 건과 요청 시각(datetime)을 받는 함수
    """요청 시각의 시가 조건의 허용 시간대 안이면 True, 밖이면 False 를 리턴한다. 끝 시각은 포함하지 않는다."""
    start, end = rule["hours"]                                   # 허용 시작 시와 끝 시를 꺼낸다
    hour = now.hour                                              # 요청 시각의 시를 꺼낸다
    return start <= hour < end                                   # 시작 시 이상이고 끝 시 미만인지(True 또는 False)를 리턴한다


def is_allowed_network(rule, network):                           # 조건 한 건과 접속 위치를 받는 함수
    """접속 위치가 조건의 허용 접속 위치에 들어 있으면 True, 아니면 False 를 리턴한다."""
    allowed_networks = rule["networks"]                          # 허용된 접속 위치 리스트를 꺼낸다
    return network in allowed_networks                           # 그 리스트에 들어 있는지(True 또는 False)를 리턴한다


def evaluate_conditional(user, resource, action, network, now, rules):   # 사용자 · 자원 · 행위 · 접속 위치 · 요청 시각(datetime) · 조건 리스트를 받는 함수
    """(허용 여부, 이유)를 리턴한다. 기본 판정이 허용이어도 그 권한의 조건(업무 시간 · 접속 위치)에 어긋나면 거부한다."""
    ok, reason = evaluate_access(user, resource, action, now)    # 먼저 10/22(목)의 기본 판정을 한다
    if not ok:                                                   # 기본 판정이 거부이면
        return False, reason                                     # 그 이유로 바로 거부한다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    for rule in rules:                                           # 조건을 하나씩 꺼낸다
        if rule["permission"] == permission:                     # 이 권한에 걸린 조건이면
            if not is_work_time(rule, now):                      # 업무 시간 안이 아니면
                return False, "업무 시간 밖"                       # 거부한다
            if not is_allowed_network(rule, network):            # 허용된 접속 위치가 아니면
                return False, "허용되지 않은 접속 위치"            # 거부한다
    return True, reason                                          # 어긋나는 조건이 없으면 기본 판정의 이유로 허용한다
```

**`access_server.py`** (6교시 완성본)

```python
import json                                                      # JSON 문자열을 만드는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from flask import Flask, request                                 # 서버를 만드는 Flask 와 요청 정보를 담은 request 를 불러온다
from conditional import load_rules, evaluate_conditional         # 5교시에 만든 조건 판정 함수를 불러온다

app = Flask(__name__)                                            # 서버 프로그램을 만든다
app.json.ensure_ascii = False                                    # 응답의 한글이 \uXXXX 로 깨지지 않게 한다
RULES = load_rules("config/conditions.json")                     # 조건 파일을 서버를 켤 때 한 번 읽는다
LOG_PATH = "server_log.jsonl"                                    # 요청 로그를 남길 파일 이름
TIME_FORMAT = "%Y-%m-%dT%H:%M"                                   # 주소로 받는 시각 문자열의 형식(예: 2026-10-30T10:00)


def parse_time(text):                                            # 시각 문자열을 받는 함수
    """2026-10-30T10:00 모양 문자열을 시각으로 바꿔 리턴한다. 문자열이 없거나 모양이 틀리면 None 을 리턴한다."""
    if text is None:                                             # 시각 문자열이 아예 없으면
        return None                                              # 없다고 알린다
    try:                                                         # 아래를 시도한다
        return datetime.strptime(text, TIME_FORMAT)              # 문자열을 시각으로 바꿔 리턴한다
    except ValueError:                                           # 모양이 틀렸으면
        return None                                              # 없다고 알린다


def write_log(entry):                                            # 로그에 쓸 딕셔너리를 받는 함수
    """딕셔너리 한 건을 JSON 한 줄로 만들어 로그 파일 끝에 덧붙인다."""
    mode = "a"                                                   # 파일을 여는 모드: 덧붙이기("a")
    with open(LOG_PATH, mode, encoding="utf-8") as f:            # 파일을 mode(덧붙이기 모드)로 연다
        text = json.dumps(entry, ensure_ascii=False)             # 딕셔너리를 JSON 문자열로 만든다(한글은 그대로)
        f.write(text + "\n")                                     # 한 줄로 파일 끝에 쓴다


@app.route("/check")                                             # 주소 /check 로 오는 요청을 아래 함수가 받는다
def check():                                                     # 요청 한 건을 처리하는 함수
    """주소의 user · resource · action · network · time 으로 판정하고, 허용이면 200, 거부이면 403, 값이 빠졌으면 400 으로 답한다."""
    user = request.args.get("user")                              # 요청 주소에서 user 값을 꺼낸다(주소에 없으면 None)
    resource = request.args.get("resource")                      # 요청 주소에서 resource 값을 꺼낸다
    action = request.args.get("action")                          # 요청 주소에서 action 값을 꺼낸다
    network = request.args.get("network")                        # 요청 주소에서 network 값을 꺼낸다
    time_text = request.args.get("time")                         # 요청 주소에서 time 값을 꺼낸다(없으면 None)
    now = parse_time(time_text)                                  # 시각으로 바꾼다(없거나 모양이 틀리면 None)
    if None in (user, resource, action, network, now):           # 빠졌거나 모양이 틀린 값이 하나라도 있으면
        return {"allowed": False, "reason": "입력이 잘못됨"}, 400   # 요청이 잘못됐다는 상태 코드 400 으로 답한다
    allowed, reason = evaluate_conditional(user, resource, action, network, now, RULES)   # 조건까지 판정한다
    log_entry = {
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

if __name__ == "__main__":                                       # 이 파일을 직접 실행했을 때만
    app.run(port=5001)                                           # 5001번 포트로 서버를 켠다
```
