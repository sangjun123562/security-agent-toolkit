# 10/23(금) 오전 · 3과목 접근통제 ③ — 권한 요청서 · 승인과 반려 · 정책 확인 후 부여 — 실습

어제(10/22(목))에는 역할 부여와 회수, 기간이 정해진 예외, 최종 판정 함수 `evaluate_access`(`policy.py`)를 만들었습니다. 오늘 오전에는 직원이 권한을 달라고 하는 **요청**을 기록으로 남기고, 승인하고, 정책으로 한 번 더 확인해서 어제의 예외 권한을 부여하는 흐름을 만듭니다.

- **2교시**: 요청을 요청서 한 장(딕셔너리)으로 적어 목록에 모으고, 접수할 수 없는 요청을 걸러 낸다.
- **3교시**: 보안 담당이 요청서를 승인하거나 반려하고, 이미 처리한 요청서는 다시 처리하지 못하게 막는다.
- **4교시**: 승인된 요청서를 정책으로 한 번 더 확인하고, 통과한 것만 예외 권한을 부여한다.

오늘 수업은 오전 2 · 3 · 4교시와 오후 5 · 6교시이고 7교시는 없습니다. 교시마다 문제는 하나이고, 그 안에서 단계를 나눠 질문에 답합니다. 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 어제 파일을 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python -c "from datetime import datetime; from policy import evaluate_access; from exception_policy import EXCEPTIONS; print('어제 파일 정상', len(EXCEPTIONS)); print(evaluate_access('dami', 'SALES', 'QUERY', datetime(2026, 10, 23, 10, 0)))"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다.
   - `rbac.py` · `exception_policy.py` · `policy.py` 가 보이고, `config` 안에 `users.json` · `roles.json` · `exceptions.json` 이 보여야 합니다.
   - 마지막 두 줄에 `어제 파일 정상 5` 와 `(False, '퇴사한 계정')` 이 나와야 합니다. 뒤의 숫자 5 는 어제 만든 예외 개수입니다. 숫자가 다르면 4교시에 나오는 예외 번호도 달라집니다. 두 번째 줄은 퇴사한 사용자 dami 가 거부되는지 보는 것이고, 다르게 나오면 어제 `policy.py` 를 확인합니다.
   - 아니면 수업 자료로 받은 `day02_recovery` 폴더 안의 파일을 `access_control` 폴더에 넣고(`config` 안의 파일은 `config` 폴더에 넣습니다) 마지막 줄을 다시 칩니다.
3. **오늘 받은 파일 두 개를 `access_control` 폴더로 옮깁니다.** 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day03_am_request.md` (이 파일) — 오전 실습 안내. 읽기만 합니다.
   - `day03_am_report.md` — **오전 보고서.** 2 · 3 · 4교시 답을 여기에 적습니다.
4. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day03_am_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-23(금))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이유까지 설명해야 하는 핵심 질문입니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일이 `config/…` 를 지금 위치 기준으로 찾기 때문입니다. `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **어제까지 만든 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 권한 요청서 만들기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 담당이 보낸 메시지: 「어제 18시에 끝난 정산 예외가 오늘도 필요해서, seoyeon 이 저에게 메신저로 다시 부탁했습니다. 이렇게 메신저나 말로 받으면 나중에 확인할 기록이 남지 않습니다. 요청을 요청서 한 장으로 적어 목록에 모아 주세요. 정보가 빠졌거나 잘못된 요청은 받지 않게 해 주세요.」
> - 이 교시에서 하는 일: 요청 하나를 요청서(딕셔너리)로 만들어 목록에 더하는 함수 `create_request` 를 직접 씁니다. 실행해서 접수된 요청과 접수되지 않은 요청을 읽습니다.
> - 끝나면 쓰는 것: 보고서 (가)~(나) 답

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 메신저나 말로 받은 요청은 기록이 남지 않습니다. 승인 기준도 사람마다 다르고, 받아 놓고 회수를 잊습니다.
2. 요청을 **요청서**(request form · 리퀘스트 폼)라는 정해진 모양의 기록으로 받으면, 필요한 정보가 빠진 요청은 접수 단계에서 걸러 낼 수 있습니다.
3. 오늘 오전의 전체 흐름은 이렇습니다. 2교시에서 요청서를 **접수**하고, 3교시에서 **승인 · 반려**하고, 4교시에서 정책으로 한 번 더 확인한 뒤 어제의 **예외 권한을 부여**합니다. 부여된 예외는 어제 만든 `evaluate_access` 가 그대로 허용으로 판정합니다.

### 📖 2.1 요청서와 상태

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- **요청서**: 요청 한 건을 적은 딕셔너리. 접수할 때 칸 아홉 개를 씁니다(아래 표는 `resource` · `action` 을 한 행에 묶어 여덟 행입니다). 3교시에 `approver` 칸이, 4교시에 `exception_id` 칸이 더 생깁니다.
- **이력**: 무슨 일이 어떤 순서로 있었는지 남겨 둔 기록. 요청서에 처리 결과를 남기면 나중에 되짚어 볼 수 있습니다.
- **상태**(status · 스테이터스): 그 요청서가 지금 어디까지 처리됐는지를 적는 칸. 정해 둔 글자 중 하나만 씁니다.

| 칸 | 뜻 | 예 |
|---|---|---|
| `id` | 요청 번호 | `1` |
| `user` | 요청한 사람 | `"seoyeon"` |
| `resource` · `action` | 달라는 권한의 자원과 행위 | `"SETTLE"` · `"QUERY"` |
| `permission` | 위 둘을 `자원:행위` 로 합친 글자 | `"SETTLE:QUERY"` |
| `until` | 요청자가 바라는 만료 시각 | `"2026-10-27 18:00"` |
| `reason` | 요청 이유 | `"정산 대조 지원"` |
| `requested_at` | 접수한 시각 | `"2026-10-23 08:30"` |
| `status` | 처리 상태 | `"reviewing"` |

| 상태 글자 | 뜻 | 쓰이는 교시 |
|---|---|---|
| `reviewing` | 검토 중. 접수 직후의 상태 | 2교시 |
| `approved` · `rejected` | 승인됨 · 반려됨(검토한 사람이 거절해서 돌려보냄) | 3교시 |
| `granted` | 예외 권한이 부여됨 | 4교시 |

```
+---------------------------------------+
| 요청서 접수 (create_request)  [2교시] |
+---------------------------------------+
   |
   v
+-----------------------------+
| status: reviewing (검토 중) |
+-----------------------------+
   |
   +--> 반려 --> status: rejected (반려됨)  [3교시]
   |
   v  승인
+------------------------------------+
| status: approved (승인됨)  [3교시] |
+------------------------------------+
   |
   v  정책 확인을 통과하면
+--------------------------------------------------+
| status: granted (부여됨)  [4교시, grant_request] |
+--------------------------------------------------+
```

### 📖 2.2 접수할 수 없는 요청

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 접수 단계에서는 세 가지만 걸러 냅니다. 사용자 파일에 없는 이름, 이유가 비어 있는 요청, 그리고 희망 만료 시각(`until`)이 접수 시각보다 늦지 않은(이미 지난) 요청입니다.
- 퇴사한 사람이나 이미 권한이 있는 사람의 요청은 접수 단계에서 걸러 내지 않습니다. 그것은 4교시의 부여 단계에서 정책 코드가 확인합니다.
- 함수가 받는 접수 시각 `received_at` 은 요청서의 `requested_at` 칸에 그대로 들어갑니다.
- `until` 이 비었는지, 너무 먼 미래인지는 접수 단계에서 확인하지 않습니다. 

```
+--------------------------------------------------------------------+
| create_request(user, resource, action, until, reason, received_at) |
+--------------------------------------------------------------------+
   |
   v
+------------------------+
| user 가 USERS 에 있나? |
+------------------------+
   |
   +--> 없음 --> (False, "등록되지 않은 사용자")
   |
   v  있음
+------------------------+
| reason 이 빈 글자인가? |
+------------------------+
   |
   +--> 빈 글자 --> (False, "이유가 없음")
   |
   v  아님
+-----------------------------------+
| until 이 received_at 보다 늦은가? |
+-----------------------------------+
   |
   +--> 늦지 않음 --> (False, "만료 시각이 이미 지났음")
   |
   v  늦음
+---------------------------------------------+
| 요청서 딕셔너리를 만들어 REQUESTS 에 더한다 |
+---------------------------------------------+
   |
   v
(True, 요청서)  --  status 는 "reviewing"
```

**🐍 문법 상자 — 요청서(딕셔너리)를 만들 때 쓰는 모양**

**① 칸이 많은 딕셔너리는 괄호 `{ }` 안에서 줄을 바꿔 쓸 수 있습니다. 한 문장입니다**

```python
request = {"id": 1, "user": "seoyeon",
           "status": "reviewing"}                                  # 괄호 안에서는 줄을 바꿔 써도 한 문장이다
print(request["status"])                                           # 위와 같은 값이 나온다
```

실행 결과:

```
reviewing
```

**② 글자가 비어 있는지 `== ""` 로 묻기**

```python
reason = ""                                                        # 비어 있는 글자
print(reason == "")                                                # 비어 있는지 묻는다
reason = "정산 확인"                                                 # 글자가 있는 이유
print(reason == "")                                                # 비어 있지 않으면 거짓이다
```

실행 결과:

```
True
False
```

**③ 같은 형식의 시각 글자는 `<=` · `>` 로 비교해도 시각 순서와 같습니다**

```python
print("2026-10-27 18:00" > "2026-10-23 09:15")                    # 같은 형식의 글자는 앞에서부터 비교한다. 늦은 시각이 더 크다
print("2026-10-22 18:00" <= "2026-10-23 09:15")                   # 어제 시각은 오늘 접수 시각보다 작으므로 참이다
```

실행 결과:

```
True
True
```

- 어제는 시각 글자를 `strptime` 으로 시각으로 바꿔 비교했습니다. 오늘의 `until` 과 `received_at` 은 `"2026-10-23 09:15"` 처럼 자릿수까지 같은 형식이라, 글자 그대로 비교해도 같은 결과가 나옵니다.
- `==` 는 「같은가」를 묻는 비교이고, `=` 는 값을 담는 대입입니다. `if` 의 조건에는 `==` 를 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 요청서를 만들어 목록에 모으고, 접수할 수 없는 요청 걸러 내기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 직원이 메신저로 「정산 조회 권한을 주세요」라고 부탁하면, 보안 담당이 그 메시지를 찾아서 처리합니다. 메시지가 여기저기 흩어져 있어서 누가 · 언제 · 무엇을 부탁했는지 한곳에서 볼 수 없습니다.
- **그래서 만드는 것**: 요청 하나를 **요청서**(딕셔너리) 한 장으로 적어 목록 `REQUESTS` 에 모으는 함수 `create_request` 입니다. 정보가 잘못된 요청은 목록에 넣지 않고 이유를 알려 줍니다.
- **실행하면**: 오늘 아침에 들어온 요청 일곱 건이 하나씩 접수가 시도됩니다. 줄마다 「접수됨, 요청 번호 …」 또는 「접수 안 됨: 이유」가 나오고, 끝에 접수된 요청서 목록이 나옵니다.
- **현업에서는**: 권한 신청 도구도 요청자 · 시각 · 이유가 없는 신청은 받지 않고, 받은 신청마다 번호를 붙여 기록으로 남깁니다.

**🎯 할 일**

1. `req_create.py` 와 `day03_2-1_run.py` 두 파일을 만들고, `create_request` 본문(함수 안에 들여써서 채우는 줄들)을 직접 씁니다.
2. 실행해서 <mark>접수된 요청 네 건과 접수되지 않은 세 건</mark>(단계 1: 접수)과 <mark>요청서 목록</mark>(단계 2: 점검)을 읽습니다.

**`req_create.py`**

```python
from rbac import USERS                                           # 10/21(수)에 만든 사용자 딕셔너리를 불러온다

REQUESTS = []                                                    # 접수한 요청서를 모아 두는 목록(프로그램이 끝나면 사라진다)


def create_request(user, resource, action, until, reason, received_at):  # 요청자 · 자원 · 행위 · 희망 만료 시각 · 이유 · 접수 시각을 받는 함수
    """요청서를 만들어 REQUESTS 에 넣고 (True, 요청서)를 리턴한다. 접수할 수 없으면 (False, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. user 가 USERS 에 없으면 False, "등록되지 않은 사용자" 를 리턴한다
    # 2. reason 이 빈 글자("")이면 False, "이유가 없음" 을 리턴한다
    # 3. until 이 received_at 과 같거나 앞서면(until <= received_at) False, "만료 시각이 이미 지났음" 을 리턴한다
    # 4. 딕셔너리 request 를 만든다. 칸 아홉 개의 이름은 2.1 의 표와 같고, 값은 이렇게 정한다:
    #    "id" 는 REQUESTS 의 개수 + 1, "permission" 은 f"{resource}:{action}", "requested_at" 은 received_at,
    #    "status" 는 "reviewing", 나머지 다섯 칸(user · resource · action · until · reason)은 같은 이름의 값을 그대로 넣는다
    # 5. REQUESTS 목록 끝에 request 를 더한다
    # 6. True, request 를 리턴한다
```

- 본문은 모두 함수 안이라 4칸으로 쓰고, `if` 아래 `return` 은 4칸 더(8칸) 들어갑니다. 1 · 2 · 3번 주석 밑에는 각각 `if` 줄과 그 안쪽 `return` 줄을 씁니다. 4번의 딕셔너리는 `{ }` 안이라 `,` 뒤에서 줄을 바꿔도 되고, 이어지는 줄의 들여쓰기 칸 수는 몇 칸이든 됩니다.
- `status` 의 값은 따옴표를 붙인 글자 `"reviewing"` 입니다. 2.1 의 표와 철자가 같아야 3교시가 읽습니다.
- 채우기 전에 실행하면 `TypeError: cannot unpack non-iterable NoneType object` 오류가 납니다. 함수가 아무것도 리턴하지 않아 `ok, result` 로 나눠 받지 못하기 때문입니다. 본문을 채운 뒤에 실행합니다.

**`day03_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 단계 1은 요청 일곱 건을 `create_request` 로 접수하고, 단계 2는 접수된 요청서 목록을 출력합니다.

```python
from req_create import REQUESTS, create_request                  # 방금 만든 요청서 함수와 목록을 불러온다

INBOX = [                                                        # 오늘 아침에 들어온 요청 일곱 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),           # 어제 끝난 예외가 아직 필요함
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),              # 계정 관리자의 영업 실적 조회
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),           # 접수 단계에서는 걸러지지 않는 요청
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),                  # 접수 단계에서는 걸러지지 않는 요청
    ("hana", "SALES", "QUERY", "2026-10-27 18:00", "신규 업무 지원", "2026-10-23 09:05"),               # 접수되는지 실행해서 확인
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "", "2026-10-23 09:10"),                        # 접수되는지 실행해서 확인
    ("gaeun", "ACCOUNT", "QUERY", "2026-10-22 18:00", "어제 적은 요청서 재사용", "2026-10-23 09:15"),   # 접수되는지 실행해서 확인
]

print("--- 단계 1: 접수 - 요청 일곱 건을 하나씩 넣는다")             # 단계 1 시작을 알리는 줄
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼낸다
    ok, result = create_request(user, resource, action, until, reason, received_at)   # 접수를 시도하고 결과를 받는다
    if ok:                                                       # 접수됐으면
        print(user, resource, action, "-> 접수됨, 요청 번호", result["id"])   # 요청 번호를 출력한다
    else:                                                        # 접수되지 않았으면
        print(user, resource, action, "-> 접수 안 됨:", result)    # 이유를 출력한다

print("--- 단계 2: 점검 - 요청서 목록")                            # 단계 2 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], request["permission"], request["status"])   # 번호 · 요청자 · 권한 · 상태를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `req_create.py` · `day03_2-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch req_create.py` → `touch day03_2-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim req_create.py` → `vim day03_2-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `req_create.py` 의 `create_request` 본문을 직접 씁니다. 2.2 의 그림과 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 를 쳐서 마지막 폴더가 `access_control` 인지 확인한 뒤 실행합니다.
   ```bash
   python day03_2-1_run.py
   ```
   - 명령 풀이: `python` 파이썬으로 파일을 실행 · `day03_2-1_run.py` 실행할 파일
   - 맥북은 `python3 day03_2-1_run.py` 로 칩니다.
4. 출력은 두 단계입니다. 단계 1은 요청 일곱 건의 접수 결과(일곱 줄)이고, 단계 2는 접수된 요청서 목록(네 줄)입니다.
5. **[보고서]** `day03_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 접수되지 않은 세 건이 각각 `create_request` 의 어느 `if` 조건 때문에 접수되지 않았는지 적어 주세요.
   - (나) 🔍 요청서의 `until`(희망 만료 시각)은 요청자가 직접 적습니다. 요청자가 적은 기간을 그대로 믿고 승인해도 될까요? 승인하기 전에 확인할 것을 두 가지 이상 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 요청서 한 장 | 딕셔너리. 칸은 `id` · `user` · `resource` · `action` · `permission` · `until` · `reason` · `requested_at` · `status` |
| 다음 요청 번호 | `len(REQUESTS) + 1` |
| 접수 못 하는 요청 | 사용자 파일에 없음 · 이유가 `""` · `until <= received_at` → `(False, 이유)` |
| 접수한 요청의 상태 | `"reviewing"` |
| 목록에 더하기 | `REQUESTS.append(request)` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 승인과 반려</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 담당이 보낸 메시지: 「접수된 요청서를 제가 하나씩 보고 승인하거나 반려합니다. 그런데 같은 요청서를 실수로 두 번 승인하거나, 이미 반려한 요청서를 나중에 승인하는 일이 생기면 안 됩니다. 검토 중인 요청서만 처리되게 하고, 누가 처리했는지도 요청서에 남겨 주세요. 요청한 본인이 자기 요청을 처리하는 일도 막아 주세요.」
> - 이 교시에서 하는 일: 요청서를 승인하는 함수 `approve_request` 를 직접 쓰고, 반려하는 함수 `reject_request` 는 남은 부분을 채웁니다. 본인 요청과 두 번째 처리를 시도해 막히는 것을 확인합니다.
> - 끝나면 쓰는 것: 보고서 (가)~(다) 답

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 요청서는 **정해진 순서로만** 상태를 바꿉니다.
2. 누가 승인하거나 반려했는지 적어 두어야, 나중에 문제가 생겼을 때 책임을 찾고 감사에 답할 수 있습니다.

### 📖 3.1 상태가 바뀌는 순서

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 지금 상태 | 할 수 있는 처리 | 처리 뒤 상태 | 다시 처리하면 |
|---|---|---|---|
| `reviewing` | 승인 | `approved` | — |
| `reviewing` | 반려 | `rejected` | — |
| `approved` · `rejected` | (없음) | 그대로 | `(False, "검토 중이 아님")` |

- 이 규칙을 코드로 쓰는 방법은 간단합니다. **바꾸기 전에 지금 상태를 먼저 확인**하고, 맞지 않으면 아무것도 바꾸지 않고 `False` 와 이유를 리턴합니다.
- `approved` 가 된 요청서를 `granted` 로 바꾸는 일은 4교시에 합니다.

```
+--------------------------------------------------------------------------+
| approve_request(request, approver)  /  reject_request(request, approver) |
+--------------------------------------------------------------------------+
   |
   v
+----------------------------------------+
| request["status"] 가 "reviewing" 인가? |
+----------------------------------------+
   |
   +--> 아님 --> (False, "검토 중이 아님")   [상태를 바꾸지 않는다]
   |
   v  맞음
+----------------------------------------------------+
| 요청한 사람(request["user"])이 approver 와 같은가? |
+----------------------------------------------------+
   |
   +--> 같음 --> (False, "본인 요청은 처리할 수 없음")   [상태를 바꾸지 않는다]
   |
   v  다름
+---------------------------------------------------------------------+
| status 를 "approved" (또는 "rejected") 로 바꾸고 approver 를 적는다 |
+---------------------------------------------------------------------+
   |
   v
(True, "승인")  또는  (True, "반려")
```

### 📖 3.2 승인자를 정하는 규칙

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 오늘은 승인자를 `security_manager` 한 사람으로 둡니다. 사람 이름이 아니라 보안 담당자가 쓰는 계정 이름입니다.
- 현업에서는 요청한 권한에 따라 승인자가 달라집니다.
- 오늘은 요청한 본인 여부를 확인하는 검사를 승인 · 반려 두 함수에 넣습니다.

**🐍 문법 상자 — 상태 확인과 칸 바꾸기**

**① 있는 칸은 값을 바꾸고, 없던 칸은 이렇게 쓰면 새로 생깁니다**

```python
request = {"id": 1, "status": "reviewing"}                          # approver 칸이 아직 없는 요청서
request["status"] = "approved"                                     # 있는 칸의 값을 바꾼다
request["approver"] = "security_manager"                                     # 없던 칸은 이렇게 쓰면 새로 생긴다
print(request)                                                     # 요청서 전체를 출력한다
```

실행 결과:

```
{'id': 1, 'status': 'approved', 'approver': 'security_manager'}
```

**② 딕셔너리의 칸이 있는지 확실하지 않을 때는 `.get("칸 이름")` 으로 꺼냅니다**

```python
request = {"id": 1, "status": "reviewing"}                          # 요청서 한 장. approver 칸은 아직 없다
print(request["status"])                                           # [ ] 로 있는 칸을 꺼낸다
print(request.get("status"))                                       # .get 으로 있는 칸을 꺼내도 같은 값이 나온다
print(request.get("approver"))                                     # 없는 칸을 .get 으로 꺼내면 오류 없이 None(값 없음)이 나온다
print(request["approver"])                                         # 없는 칸을 [ ] 로 꺼내면 KeyError 오류가 나고 프로그램이 멈춘다
```

실행 결과:

```
reviewing
reviewing
None
Traceback (most recent call last):
  File "…/파일이름.py", line 5, in <module>
    print(request["approver"])                                         # 없는 칸을 [ ] 로 꺼내면 KeyError 오류가 나고 프로그램이 멈춘다
KeyError: 'approver'
```

- `[ ]` 는 칸이 없으면 오류(`KeyError`)가 나고 프로그램이 멈춥니다. `.get( )` 은 칸이 없어도 멈추지 않고 `None`(값이 없다는 뜻의 값)을 꺼냅니다.
- 이 문제의 단계 2에서는 네 장 모두 처리되어 `approver` 칸이 있으므로 `None` 이 나오지 않습니다. 그래도 아직 처리하지 않은 요청서가 섞여 있을 때 멈추지 않도록 `.get` 을 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 승인 · 반려 함수 만들고, 두 번째 처리가 막히는지 확인하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 접수된 요청서 네 장이 `reviewing`(검토 중) 상태로 쌓여 있고, 보안 담당 `security_manager` 가 하나씩 보고 승인하거나 반려합니다. 사람이 하다 보면 같은 요청서를 두 번 처리하거나, 요청한 본인이 자기 요청을 처리하는 일이 생길 수 있습니다.
- **그래서 만드는 것**: 승인 함수 `approve_request` 와 반려 함수 `reject_request` 입니다. 두 함수는 ① 검토 중인 요청서만 처리하고 ② 요청한 본인이 처리하려 하면 막고 ③ 처리하면 상태를 바꿔 누가 처리했는지 요청서에 적습니다.
- **실행하면**: 본인 승인을 시험하는 한 줄과 처리 시도 여섯 줄이 나옵니다. 줄마다 성공 여부(`True` / `False`)와 이유가 붙고, 끝에 요청서 목록의 상태와 처리한 사람이 나옵니다.
- **현업에서는**: 승인 도구도 처리가 끝난 신청은 다시 처리하지 못하게 막고, 처리한 사람과 시각을 기록으로 남깁니다.

**🎯 할 일**

1. `req_review.py` 와 `day03_3-1_run.py` 두 파일을 만들고, `approve_request` 본문을 직접 쓰고 `reject_request` 는 남은 부분을 채웁니다.
2. 실행해서 <mark>본인 승인 시험과 처리 여섯 건의 결과</mark>(단계 1: 처리)와 <mark>요청서 목록</mark>(단계 2: 점검)을 읽습니다.

**`req_review.py`**

```python
def approve_request(request, approver):                          # 요청서와 승인자 이름을 받는 함수
    """검토 중(reviewing)인 요청서만 승인한다. (성공 여부, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["status"] 가 "reviewing" 이 아니면 False, "검토 중이 아님" 을 리턴한다
    # 2. request["user"] 가 approver 와 같으면(요청한 사람이 스스로 처리하려는 것) False, "본인 요청은 처리할 수 없음" 을 리턴한다
    # 3. request["status"] 를 "approved" 로 바꾼다
    # 4. request["approver"] 를 approver 로 정한다
    # 5. True, "승인" 을 리턴한다


def reject_request(request, approver):                           # 요청서와 반려하는 사람 이름을 받는 함수
    """검토 중(reviewing)인 요청서만 반려한다. (성공 여부, 이유)를 리턴한다."""
    if request["status"] != "reviewing":                         # 검토 중이 아니면(이미 처리됐으면)
        return False, "검토 중이 아님"                             # 바꾸지 않고 이유를 알린다
    if request["user"] == approver:                              # 요청한 사람이 스스로 처리하려고 하면
        return False, "본인 요청은 처리할 수 없음"                  # 바꾸지 않고 이유를 알린다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["status"] 를 "rejected" 로 바꾼다
    # 2. request["approver"] 를 approver 로 정한다
    # 3. True, "반려" 를 리턴한다
```

- `approve_request` 의 본문은 함수 안이라 4칸으로 쓰고, `if` 아래 `return` 은 4칸 더(8칸) 들어갑니다. 1 · 2번 주석 밑에는 각각 `if` 줄과 그 안쪽 `return` 줄을 씁니다.
- `reject_request` 는 `approve_request` 와 모양이 같고, 바뀌는 글자(`"rejected"` · `"반려"`)만 다릅니다. 그래서 앞의 두 검사(`if` 두 개)는 미리 채워 두었고, 1 ~ 3번 주석 아래만 씁니다.
- 채우기 전에 실행하면 `TypeError: cannot unpack non-iterable NoneType object` 오류가 납니다. `approve_request` 가 아무것도 리턴하지 않기 때문입니다.

**`day03_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 2교시의 `create_request` 로 요청서 네 장을 접수한 뒤, 단계 1은 본인 승인 시험 한 건과 처리 여섯 건을 넣고 단계 2는 요청서 목록을 출력합니다.

```python
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request, reject_request           # 방금 만든 승인 · 반려 함수를 불러온다

INBOX = [                                                        # 접수에 성공하는 요청 네 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다(결과는 쓰지 않는다)

DECISIONS = [                                                    # 보안 담당(security_manager)이 내리는 처리 여섯 건. (요청 번호, 처리)
    (1, "승인"),                                                 # seoyeon 의 정산 조회
    (2, "반려"),                                                 # gaeun 의 영업 실적 조회
    (3, "승인"),                                                 # dami 의 영업 실적 조회
    (4, "승인"),                                                 # junho 의 정산 조회
    (1, "승인"),                                                 # 이미 승인한 1번을 다시 승인해 본다
    (2, "승인"),                                                 # 이미 반려한 2번을 승인해 본다
]

print("--- 단계 1: 처리 - 본인 요청 시험 한 건, 승인 · 반려 여섯 건을 처리한다")   # 단계 1 시작을 알리는 줄
ok, result = approve_request(REQUESTS[0], "seoyeon")             # 요청자 seoyeon 이 자기 요청 1번을 스스로 승인해 본다
print(1, "본인 승인 ->", ok, result)                              # 요청 번호 · 처리 -> 성공 여부 · 이유 를 출력한다
for number, decision in DECISIONS:                               # 처리를 하나씩 꺼낸다
    request = REQUESTS[number - 1]                               # 요청 번호로 요청서를 찾는다(번호는 1부터, 목록 자리는 0부터)
    if decision == "승인":                                       # 승인이면
        ok, result = approve_request(request, "security_manager")  # 승인 함수를 부른다
    else:                                                        # 반려면
        ok, result = reject_request(request, "security_manager")  # 반려 함수를 부른다
    print(number, decision, "->", ok, result)                    # 요청 번호 · 처리 -> 성공 여부 · 이유 를 출력한다

print("--- 단계 2: 점검 - 요청서 목록")                            # 단계 2 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], request["status"], request.get("approver"))   # 번호 · 요청자 · 상태 · 처리한 사람을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `req_review.py` · `day03_3-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch req_review.py` → `touch day03_3-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim req_review.py` → `vim day03_3-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `req_review.py` 의 두 함수 본문을 직접 씁니다. 3.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 를 쳐서 마지막 폴더가 `access_control` 인지 확인한 뒤 실행합니다.
   ```bash
   python day03_3-1_run.py
   ```
   - 명령 풀이: `python` 파이썬으로 파일을 실행 · `day03_3-1_run.py` 실행할 파일
   - 맥북은 `python3 day03_3-1_run.py` 로 칩니다.
4. 출력은 두 단계입니다. 단계 1은 본인 승인 시험 한 줄과 처리 여섯 건의 결과(여섯 줄)이고, 단계 2는 요청서 목록(네 줄)입니다. 본인 승인 시험은 `False`, 처리 여섯 건은 앞의 네 건이 `True`, 뒤의 두 건이 `False` 로 나와야 합니다.
5. **[보고서]** `day03_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 막힌 세 줄이 각각 왜 막혔는지 적어 주세요.
   - (나) 🔍 이미 승인한 요청서를 다시 승인하지 못하게 막는 이유는 무엇인가요? 막지 않으면 어떤 일이 생길 수 있나요?
   - (다) 🔍 `approve_request` 에서 `request["user"] == approver` 검사를 뺀다면 어떤 위험이 생길까요? 요청자가 친구에게 대신 승인해 달라고 부탁하면 이 검사로는 막을 수 없습니다. 이런 경우를 막으려면 무엇이 더 필요할까요?

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 승인 · 반려는 검토 중일 때만 | `if request["status"] != "reviewing": return False, "검토 중이 아님"` |
| 본인 요청 막기 | `if request["user"] == approver: return False, "본인 요청은 처리할 수 없음"` |
| 상태 바꾸기 | `request["status"] = "approved"` (또는 `"rejected"`) |
| 처리한 사람 남기기 | `request["approver"] = approver` |
| 칸이 없을 수 있을 때 꺼내기 | `request.get("approver")` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 정책 확인 후 예외 권한 부여</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 담당이 보낸 메시지: 「승인한 요청서를 제가 직접 예외 파일에 옮겨 적으면 실수가 납니다. 예외 번호를 겹치게 적거나, 만료 시각을 잘못 옮기거나, 하나를 빠뜨립니다. 승인된 요청서를 코드가 정책으로 한 번 더 확인하고, 통과한 것만 예외 권한을 부여하게 해 주세요. 어느 예외를 부여했는지도 요청서에 남겨 주세요.」
> - 이 교시에서 하는 일: 승인된 요청서를 10/21(수)에 만든 `check_permission` 으로 한 번 더 확인하고, 통과하면 예외를 만들어 `EXCEPTIONS` 에 더하는 함수 `grant_request` 를 직접 씁니다. 부여 전과 후에 어제의 `evaluate_access` 로 판정해 비교합니다.
> - 끝나면 쓰는 것: 보고서 (가)~(다) 답

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 승인은 사람이 합니다. 그 뒤에 코드가 정책으로 한 번 더 확인하는 것을 **이중 검증**이라고 합니다.
2. 부여는 새 규칙을 만들지 않고, 어제 만든 **예외**(기간이 정해진 임시 권한)를 한 건 더하는 일입니다. 

### 📖 4.1 부여할지 판단하는 순서

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 요청자를 지금 정책으로 판정한 이유(`judge_reason`)에 따라 처리가 갈립니다.
- 이 이유는 10/21(수)에 만든 `check_permission` 이 리턴하는 글자입니다. `check_permission` 은 사용자 파일과 역할 파일만 보고 판정합니다(예외는 보지 않습니다).
- 단계 1은 10/22(목)의 `evaluate_access` 로 판정해 `역할 권한` 이라고 출력하고, 단계 2는 `check_permission` 의 이유를 써서 `부여하지 않음(허용)` 이라고 출력합니다. 두 출력이 다르게 보이는 것이 정상입니다.

| 판정 결과 | 뜻 | 부여 |
|---|---|---|
| 허용 (`ok` 가 `True`, 이유 「허용」) | 이미 그 권한이 있음 | 하지 않음 |
| 「권한 없음」 | 사람은 정상인데 권한만 없음 | **예외 권한 부여** |
| 「퇴사한 계정」 · 「등록되지 않은 사용자」 · 「역할이 없음」 | 사람 쪽에 문제가 있음 | 하지 않음 |

```
+------------------------+
| grant_request(request) |
+------------------------+
   |
   v
+----------------------------+
| status 가 "approved" 인가? |
+----------------------------+
   |
   +--> 아님 --> (False, "승인되지 않음")
   |
   v  맞음
+---------------------------------------------------+
| check_permission 으로 요청자를 지금 정책으로 판정 |
+---------------------------------------------------+
   |
   +--> 허용 --> (False, "부여하지 않음(허용)")   이미 가진 권한
   |
   +--> 그 밖의 이유(퇴사한 계정 · 등록되지 않은 사용자 · 역할이 없음) --> (False, "부여하지 않음(이유)")
   |
   v  권한 없음
+---------------------------------------------------+
| 요청서로 예외 한 건을 만들어 EXCEPTIONS 에 더한다 |
+---------------------------------------------------+
   |
   v
+-----------------------------------------------------------------------+
| 요청서에 예외 번호(exception_id)를 적고 status 를 "granted" 로 바꾼다 |
+-----------------------------------------------------------------------+
   |
   v
(True, "부여")
```

### 📖 4.2 요청서가 예외가 되는 방법

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 요청서 칸 | 예외 칸 |
|---|---|
| (없음. 새 번호) | `id` = `len(EXCEPTIONS) + 1` |
| `user` | `user` |
| `permission` | `permission` |
| `until` | `expires` |
| `reason` | `reason` |

- 예외를 만든 뒤에는 거꾸로, 예외의 `id` 를 요청서의 `exception_id` 칸에 적어 둡니다. 그러면 요청서만 보고도 어느 예외를 부여했는지 찾을 수 있습니다.
- `EXCEPTIONS` 는 어제 `exception_policy.py` 가 `exceptions.json` 을 읽어 만든 목록입니다. 오늘은 이 목록에 한 건을 더하기만 하고, `exceptions.json` 파일은 고치지 않습니다. 프로그램이 끝나면 더한 예외도 사라집니다.
- 어제 `find_exception` 이 같은 `EXCEPTIONS` 를 읽으므로, 더한 예외는 바로 판정에 쓰입니다.
- 어제 예외가 다섯 건이므로 새 예외의 번호는 5 + 1 = 6번입니다. 시작하기에서 본 숫자가 5가 아니면 6번이 아닌 다른 번호가 나옵니다.

**🐍 문법 상자 — 부여할지 가르는 조건과 번호 정하기**

**① `or` 로 두 조건 중 하나라도 맞는지 묻기**

```python
ok = False                                                         # 허용이 아닌 판정
reason = "퇴사한 계정"                                                # 판정 이유
print(ok or reason != "권한 없음")                                   # 둘 중 하나라도 참이면 참이다
reason = "권한 없음"                                                  # 이유를 바꾸면
print(ok or reason != "권한 없음")                                   # 둘 다 거짓이라 거짓이다
```

실행 결과:

```
True
False
```

**② 목록에 딕셔너리를 더하고, 번호는 지금 개수 + 1 로 정하기**

```python
exceptions = [{"id": 1}, {"id": 2}]                                # 예외 두 건이 든 목록
exceptions.append({"id": len(exceptions) + 1})                     # 번호는 지금 개수 + 1 로 정한다
print(exceptions)                                                  # 세 건이 되었다
```

실행 결과:

```
[{'id': 1}, {'id': 2}, {'id': 3}]
```


> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 승인된 요청서를 정책으로 확인하고 예외 권한 부여하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 승인한 요청서의 내용을 보안 담당이 예외 파일에 직접 옮겨 적습니다. 옮겨 적다 예외 번호를 겹치게 적거나, 만료 시각을 잘못 옮기거나, 하나를 빠뜨리기 쉽고 시간도 걸립니다.
- **그래서 만드는 것**: `grant_request` 입니다. 승인된 요청서를 받아서 10/21(수)에 만든 `check_permission` 으로 지금 정책을 한 번 더 확인하고, 통과한 것만 어제의 **예외**로 `EXCEPTIONS` 에 더합니다.
- **오늘 데이터**: 요청서 네 장입니다. 1번 seoyeon · 3번 dami · 4번 junho 는 승인됐고, 2번 gaeun 은 반려됐습니다.
- **실행하면**: 세 단계가 차례로 나옵니다. 단계 1은 부여하기 전의 판정, 단계 2는 부여를 시도한 결과, 단계 3은 부여한 뒤의 판정입니다. 부여 전과 후를 비교해 무엇이 달라졌는지 봅니다.
- **현업에서는**: 권한 부여 도구도 승인된 신청을 바로 부여하지 않고, 지금 정책으로 한 번 더 확인한 뒤에 부여합니다.

**🎯 할 일**

1. `req_grant.py` 와 `day03_4-1_run.py` 두 파일을 만들고, `grant_request` 본문을 직접 씁니다.
2. 실행해서 <mark>부여 전 판정</mark>(단계 1: 판정), <mark>부여 시도의 결과</mark>(단계 2: 부여), <mark>부여 후 판정</mark>(단계 3: 점검)을 읽습니다.

**`req_grant.py`**

```python
from rbac import check_permission                                # 10/21(수)에 만든 역할 판정 함수를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def grant_request(request):                                      # 요청서를 받는 함수
    """승인된 요청서를 정책으로 한 번 더 확인하고, 통과하면 예외 권한을 부여한다. (성공 여부, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["status"] 가 "approved" 가 아니면 False, "승인되지 않음" 을 리턴한다
    # 2. check_permission 에 request 의 "user" · "resource" · "action" 을 넣어 ok, judge_reason 으로 나눠 받는다
    # 3. ok 이거나 judge_reason 이 "권한 없음" 이 아니면 False, f"부여하지 않음({judge_reason})" 을 리턴한다
    # 4. 예외 딕셔너리 exception 을 만든다. 칸 다섯 개의 값은 이렇게 정한다:
    #    "id" 는 EXCEPTIONS 의 개수 + 1, "user" · "permission" · "reason" 은 request 의 같은 이름 칸,
    #    "expires" 는 request["until"] (이름이 다른 것에 주의)
    # 5. EXCEPTIONS 에 exception 을 더한다
    # 6. request["exception_id"] 를 exception["id"] 로 정한다 (어느 예외를 부여했는지 요청서에 적어 둔다)
    # 7. request["status"] 를 "granted" 로 바꾼다
    # 8. True, "부여" 를 리턴한다
```

- 본문은 모두 함수 안이라 4칸으로 쓰고, `if` 아래 `return` 은 4칸 더(8칸) 들어갑니다. 4번의 딕셔너리는 괄호 안이라 줄을 바꿔도 됩니다.
- 4번에서 딕셔너리를 변수 `exception` 에 담아 두면, 5번(`EXCEPTIONS.append(exception)`)과 6번(`exception["id"]`)에서 같은 값을 다시 쓸 수 있습니다.
- 3번의 `judge_reason` 은 `check_permission` 이 리턴하는 판정 이유 글자입니다(요청서의 `reason`, 즉 요청 이유와는 다릅니다). 「허용」이면 이미 가진 권한이라서 부여하지 않습니다.
- 채우기 전에 실행하면 `TypeError: cannot unpack non-iterable NoneType object` 오류가 납니다. 함수가 아무것도 리턴하지 않기 때문입니다.

**`day03_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 요청서 네 장을 접수하고 1 · 3 · 4번은 승인, 2번은 반려한 뒤, 단계 1 · 2 · 3을 차례로 실행합니다. 중간의 `show` 함수는 요청서마다 어제의 `evaluate_access` 로 판정해 출력하고, 단계 2 끝에서는 `exception_id` 칸이 있는 요청서(`"exception_id" in request`)의 예외 번호를 출력합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request, reject_request           # 오전 3교시에 만든 승인 · 반려 함수를 불러온다
from req_grant import grant_request                              # 방금 만든 부여 함수를 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 최종 판정 함수를 불러온다

NOW = datetime.strptime("2026-10-23 10:00", "%Y-%m-%d %H:%M")    # 오늘 실습의 지금 시각(고정)

INBOX = [                                                        # 접수에 성공하는 요청 네 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다
for number in [1, 3, 4]:                                         # 보안 담당이 1 · 3 · 4번을 승인하고
    approve_request(REQUESTS[number - 1], "security_manager")    # 승인 처리한다
reject_request(REQUESTS[1], "security_manager")                  # 2번은 반려한다


def show(title):                                                 # 제목을 받아 요청서마다 지금 판정을 출력하는 함수
    print("---", title)                                          # 제목 줄을 출력한다
    for request in REQUESTS:                                     # 요청서를 하나씩 꺼낸다
        ok, reason = evaluate_access(request["user"], request["resource"], request["action"], NOW)   # 22일의 최종 판정을 받는다
        print(request["id"], request["user"], request["permission"], "->", ok, reason)   # 요청 번호 · 요청자 · 권한 -> 판정 을 출력한다


show("단계 1: 판정 - 부여 전")                                     # 부여하기 전의 판정을 본다

print("--- 단계 2: 부여 - 요청서마다 부여를 시도한다")                # 단계 2 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    ok, result = grant_request(request)                          # 부여를 시도한다
    print(request["id"], request["user"], request["status"], "->", ok, result)   # 요청 번호 · 요청자 · 상태 -> 결과 를 출력한다

for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    if "exception_id" in request:                                # exception_id 칸이 적힌 요청서(부여된 것)만
        print("부여된 예외 번호:", request["exception_id"])         # 그 예외 번호를 출력한다

show("단계 3: 점검 - 부여 후")                                     # 부여한 뒤의 판정을 다시 본다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `req_grant.py` · `day03_4-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch req_grant.py` → `touch day03_4-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim req_grant.py` → `vim day03_4-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `req_grant.py` 의 `grant_request` 본문을 직접 씁니다. 4.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 를 쳐서 마지막 폴더가 `access_control` 인지 확인한 뒤 실행합니다.
   ```bash
   python day03_4-1_run.py
   ```
   - 명령 풀이: `python` 파이썬으로 파일을 실행 · `day03_4-1_run.py` 실행할 파일
   - 맥북은 `python3 day03_4-1_run.py` 로 칩니다.
4. 출력은 세 단계입니다. 단계 1은 부여 전 판정(네 줄), 단계 2는 부여 시도의 결과(네 줄)와 `부여된 예외 번호:` 한 줄, 단계 3은 부여 후 판정(네 줄)입니다. 부여 전과 후에 달라진 줄이 하나 있습니다.
5. **[보고서]** `day03_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 부여를 시도한 네 건이 각각 어떻게 됐는지 적어 주세요.
   - (나) 🔍 승인자가 승인한 3번 요청(`dami`)을 코드가 부여하지 않았습니다. 코드의 이 확인이 없었다면 어떤 일이 생겼을까요? 승인자가 이 문제를 미리 막기 어려운 이유도 적어 주세요.
   - (다) 🔍 부여한 예외의 만료 시각에는 요청서의 희망 만료 시각을 그대로 썼습니다. 그 시각이 지나면 이 예외는 어떻게 될까요? 만료된 예외를 정리하는 점검은 누가 얼마나 자주 하면 좋을까요?

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 승인된 것만 부여 | `if request["status"] != "approved": return False, "승인되지 않음"` |
| 정책으로 한 번 더 판정 | `ok, judge_reason = check_permission(user, resource, action)` |
| 부여하지 않는 경우 | `if ok or judge_reason != "권한 없음": return False, f"부여하지 않음({judge_reason})"` |
| 예외 권한 부여 | `exception = {"id": len(EXCEPTIONS) + 1, …}` → `EXCEPTIONS.append(exception)` |
| 어느 예외인지 적기 | `request["exception_id"] = exception["id"]` |
| 부여 끝 표시 | `request["status"] = "granted"` |

---

## 오전 마무리 — 보고서 2 · 3 · 4교시 칸 확인

`day03_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지 봅니다. `access_control` 폴더에 오늘 만든 파일이 있는지 확인합니다.

```bash
ls
ls config
```

- `req_create.py` · `req_review.py` · `req_grant.py` · `day03_2-1_run.py` · `day03_3-1_run.py` · `day03_4-1_run.py` 가 보여야 합니다. `config` 안은 어제와 같아야 합니다(오늘은 `config` 에 새 파일을 만들지 않았습니다).

오늘 오후에는 접수한 지 오래된 요청서를 시간으로 찾아내고(SLA · 처리 기한), 요청서 이력을 파일로 저장합니다. 올리기(git)는 오후 6교시 마지막에 한 번에 합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
python day03_2-1_run.py
```

**채운 코드** (한 예)

```python
    if user not in USERS:                                        # 사용자 파일에 없는 이름이면
        return False, "등록되지 않은 사용자"                       # 접수하지 않고 이유를 알린다
    if reason == "":                                             # 이유가 비어 있으면
        return False, "이유가 없음"                                # 접수하지 않고 이유를 알린다
    if until <= received_at:                                             # 희망 만료 시각이 접수 시각보다 늦지 않으면(같은 형식의 글자는 앞에서부터 비교해도 시각 순서와 같다)
        return False, "만료 시각이 이미 지났음"                     # 접수하지 않고 이유를 알린다
    request = {"id": len(REQUESTS) + 1, "user": user, "resource": resource, "action": action,
               "permission": f"{resource}:{action}", "until": until, "reason": reason,
               "requested_at": received_at, "status": "reviewing"}       # 요청서 한 장. 상태는 검토 중으로 시작한다
    REQUESTS.append(request)                                     # 요청서 목록 끝에 더한다
    return True, request                                         # 접수했다고 알리고 요청서를 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 접수되지 않은 세 건은 `hana`(`user not in USERS` 조건에 걸림, 사용자 파일에 없는 이름), `seoyeon` 의 `ACCOUNT:QUERY`(`reason == ""` 조건에 걸림, 이유가 비어 있음), `gaeun` 의 `ACCOUNT:QUERY`(`until <= received_at` 조건에 걸림, 희망 만료 시각 10/22(목) 18:00 이 접수 시각 10/23(금) 09:15 보다 앞)입니다. 줄 수가 달라도 주석이 말한 일을 하면 코드는 맞습니다.

```
--- 단계 1: 접수 - 요청 일곱 건을 하나씩 넣는다
seoyeon SETTLE QUERY -> 접수됨, 요청 번호 1
gaeun SALES QUERY -> 접수됨, 요청 번호 2
dami SALES QUERY -> 접수됨, 요청 번호 3
junho SETTLE QUERY -> 접수됨, 요청 번호 4
hana SALES QUERY -> 접수 안 됨: 등록되지 않은 사용자
seoyeon ACCOUNT QUERY -> 접수 안 됨: 이유가 없음
gaeun ACCOUNT QUERY -> 접수 안 됨: 만료 시각이 이미 지났음
--- 단계 2: 점검 - 요청서 목록
1 seoyeon SETTLE:QUERY reviewing
2 gaeun SALES:QUERY reviewing
3 dami SALES:QUERY reviewing
4 junho SETTLE:QUERY reviewing
```

- (나) 요청자가 적은 기간을 그대로 믿으면 안 됩니다. 요청자는 일이 끝난 뒤에도 불편하지 않게 길게 적기 쉽습니다. 승인자가 확인할 것: ① 이유에 적힌 일이 실제로 언제 끝나는지, 그 일에 필요한 가장 짧은 기간인지 ② 요청자가 이 권한을 받는 것이 업무에 맞는지(영업이 정산을 보려는 이유가 분명한지) ③ 만료 시각이 너무 먼 미래는 아닌지(접수 단계는 이미 지난 시각만 거르므로 최대 기간을 정해 둡니다). 필요하면 기간을 줄여서 승인합니다.

**왜** — 요청을 기록으로 받아야 「누가 언제 무엇을 왜 요청했나」를 나중에 증명할 수 있습니다. 필요한 정보가 빠진 요청은 접수 단계에서 걸러 내야 뒤의 승인 · 부여 단계가 단순해집니다. 상태를 `"reviewing"` 으로 시작해 두면 3교시가 「검토 중인 것만 처리」라는 규칙을 쓸 수 있습니다.

**자주 틀리는 곳** — `REQUESTS.append(request)` 를 빼먹는 경우가 가장 많습니다. 그러면 요청 번호가 모두 `1` 로 나오고 단계 2의 요청서 목록이 비어 나옵니다. 실행하면 다음처럼 됩니다(번호가 `1` 만 나오는 것이 신호입니다).

```
--- 단계 1: 접수 - 요청 일곱 건을 하나씩 넣는다
seoyeon SETTLE QUERY -> 접수됨, 요청 번호 1
gaeun SALES QUERY -> 접수됨, 요청 번호 1
dami SALES QUERY -> 접수됨, 요청 번호 1
junho SETTLE QUERY -> 접수됨, 요청 번호 1
hana SALES QUERY -> 접수 안 됨: 등록되지 않은 사용자
seoyeon ACCOUNT QUERY -> 접수 안 됨: 이유가 없음
gaeun ACCOUNT QUERY -> 접수 안 됨: 만료 시각이 이미 지났음
--- 단계 2: 점검 - 요청서 목록
```

`status` 철자를 `"reviewing"` 이 아니게 쓰면 3교시에서 모든 요청서가 「검토 중이 아님」으로 막힙니다. `if reason = ""` 처럼 `=` 한 개를 쓰면 `SyntaxError` 가 납니다.

**관제에서는** — 요청서 목록은 권한 관리의 첫 기록입니다. 이유 없이 접수하려던 요청 · 사용자 파일에 없는 이름의 요청 · 이미 지난 만료 시각의 요청은 건수를 세어 두고, 같은 사람이 같은 권한을 반복해서 요청하면 역할 설계가 업무와 맞지 않는다는 신호로 봅니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
python day03_3-1_run.py
```

**채운 코드** (한 예)

```python
    if request["status"] != "reviewing":                         # 검토 중이 아니면(이미 처리됐으면)
        return False, "검토 중이 아님"                             # 바꾸지 않고 이유를 알린다
    if request["user"] == approver:                              # 요청한 사람이 스스로 처리하려고 하면
        return False, "본인 요청은 처리할 수 없음"                  # 바꾸지 않고 이유를 알린다
    request["status"] = "approved"                               # 상태를 승인됨으로 바꾼다
    request["approver"] = approver                               # 누가 승인했는지 적어 둔다
    return True, "승인"                                          # 승인했다고 알린다
```

`reject_request` 는 미리 채워진 두 검사 아래 부분입니다.

```python
    request["status"] = "rejected"                               # 상태를 반려됨으로 바꾼다
    request["approver"] = approver                               # 누가 반려했는지 적어 둔다
    return True, "반려"                                          # 반려했다고 알린다
```

**결과**

- (가) 출력은 다음과 같고, 막힌 세 줄은 이렇습니다. 맨 위 `1 본인 승인` 은 요청자 seoyeon 이 자기 1번 요청을 승인하려 해서 `본인 요청은 처리할 수 없음` 입니다. 처리 여섯 건 중 `1 승인` 이 두 번째 나온 줄은 이미 승인된 1번이고, `2 승인` 은 이미 반려된 2번이라 둘 다 `검토 중이 아님` 입니다.

```
--- 단계 1: 처리 - 본인 요청 시험 한 건, 승인 · 반려 여섯 건을 처리한다
1 본인 승인 -> False 본인 요청은 처리할 수 없음
1 승인 -> True 승인
2 반려 -> True 반려
3 승인 -> True 승인
4 승인 -> True 승인
1 승인 -> False 검토 중이 아님
2 승인 -> False 검토 중이 아님
--- 단계 2: 점검 - 요청서 목록
1 seoyeon approved security_manager
2 gaeun rejected security_manager
3 dami approved security_manager
4 junho approved security_manager
```

- (나) 이미 승인한 요청서를 다시 승인하지 못하게 막는 이유는, 처리가 끝난 요청이 다시 처리되면 같은 요청이 두 번 부여되거나(예외가 중복으로 생김), 승인한 기록이 나중에 바뀌어 감사 기록을 믿을 수 없게 되기 때문입니다. 반려한 요청서를 나중에 승인으로 바꿀 수 있으면 「반려」라는 결정의 의미가 없어집니다. 번복이 필요하면 상태를 고치지 말고 새 요청서를 접수합니다.
- (다) ① 이 검사가 없으면 요청자가 자기 요청을 스스로 승인해, 아무도 확인하지 않은 요청이 통과합니다. ② 이 검사만으로는 요청자가 친구 계정이나 다른 사람에게 부탁해 대신 승인하게 하는 것을 막지 못합니다. 더 필요한 장치의 예: 계정 관리처럼 위험한 권한은 승인자를 두 명으로 하고(이중 승인), 승인자를 요청자와 다른 부서의 정해진 사람으로 두고, 승인 이력을 정기적으로 대조합니다. 근거가 있으면 맞습니다.

**왜** — 상태는 정해진 순서로만 바꿔야 요청서 하나의 처리 순서를 따라갈 수 있습니다. 「바꾸기 전에 지금 상태를 먼저 확인」하는 한 줄이 같은 요청의 중복 처리와 결정 번복을 함께 막습니다. 처리한 사람을 적어 두면 책임이 분명해집니다.

**자주 틀리는 곳** — 상태 확인을 `==` 로 써서(`if request["status"] == "reviewing": return False, …`) 거꾸로 동작하는 경우가 있습니다. 모든 처리가 「검토 중이 아님」으로 막히거나 이미 처리한 것만 통과합니다. `request["status"] = "approved"` 줄을 빼먹으면 `True` 는 나오는데 상태가 그대로라서 같은 요청서를 또 승인해도 통과합니다. 본인 요청 검사를 `==` 대신 `!=` 로 거꾸로 쓰면 security_manager 의 정상 처리가 모두 막힙니다. 실행하면 다음처럼 됩니다(`1 승인 -> True 승인` 줄이 두 번 나오면 상태를 안 바꾼 것입니다).

```
--- 단계 1: 처리 - 본인 요청 시험 한 건, 승인 · 반려 여섯 건을 처리한다
1 본인 승인 -> False 본인 요청은 처리할 수 없음
1 승인 -> True 승인
2 반려 -> True 반려
3 승인 -> True 승인
4 승인 -> True 승인
1 승인 -> True 승인
2 승인 -> False 검토 중이 아님
--- 단계 2: 점검 - 요청서 목록
1 seoyeon reviewing security_manager
2 gaeun rejected security_manager
3 dami reviewing security_manager
4 junho reviewing security_manager
```

**관제에서는** — 승인 · 반려 이력에 요청서 번호 · 처리한 사람 · 처리 시각을 남기고, 같은 요청서에 두 번째 처리 시도가 있었다면 실수인지 조작인지 확인합니다. 승인자와 요청자가 같은 요청서가 있는지 정기적으로 대조합니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
python day03_4-1_run.py
```

**채운 코드** (한 예)

```python
    if request["status"] != "approved":                          # 승인된 요청서가 아니면
        return False, "승인되지 않음"                              # 부여하지 않고 이유를 알린다
    ok, judge_reason = check_permission(request["user"], request["resource"], request["action"])   # 요청자를 지금 정책으로 판정한다
    if ok or judge_reason != "권한 없음":                                # 이미 허용이거나, 사람 자체가 거부 대상이면
        return False, f"부여하지 않음({judge_reason})"                    # 부여하지 않고 판정 이유를 알린다
    exception = {"id": len(EXCEPTIONS) + 1, "user": request["user"], "permission": request["permission"],
                 "expires": request["until"], "reason": request["reason"]}   # 요청서 내용으로 예외 한 건을 만든다
    EXCEPTIONS.append(exception)                                 # 예외 목록에 더한다
    request["exception_id"] = exception["id"]                    # 어느 예외를 부여했는지 요청서에 적어 둔다
    request["status"] = "granted"                                # 상태를 부여됨으로 바꾼다
    return True, "부여"                                          # 부여했다고 알린다
```

**결과**

- (가) 출력은 다음과 같고, 부여를 시도한 네 건의 결과는 이렇습니다(`부여된 예외 번호: 6` 줄은 1번 요청서에 적힌 예외 번호입니다). 1번 seoyeon 은 **부여됨**(예외 6번), 2번 gaeun 은 **부여 안 함**(반려된 요청서라 「승인되지 않음」), 3번 dami 는 **부여 안 함**(퇴사한 계정), 4번 junho 는 **부여 안 함**(이미 허용된 권한).

```
--- 단계 1: 판정 - 부여 전
1 seoyeon SETTLE:QUERY -> False 권한 없음
2 gaeun SALES:QUERY -> False 권한 없음
3 dami SALES:QUERY -> False 퇴사한 계정
4 junho SETTLE:QUERY -> True 역할 권한
--- 단계 2: 부여 - 요청서마다 부여를 시도한다
1 seoyeon granted -> True 부여
2 gaeun rejected -> False 승인되지 않음
3 dami approved -> False 부여하지 않음(퇴사한 계정)
4 junho approved -> False 부여하지 않음(허용)
부여된 예외 번호: 6
--- 단계 3: 점검 - 부여 후
1 seoyeon SETTLE:QUERY -> True 예외 6번
2 gaeun SALES:QUERY -> False 권한 없음
3 dami SALES:QUERY -> False 퇴사한 계정
4 junho SETTLE:QUERY -> True 역할 권한
```

- (나) 승인자는 사람이라서 요청자가 이미 퇴사했는지를 모르고 승인할 수 있습니다. 코드는 지금 사용자 파일과 역할 파일로 판정하므로 퇴사한 계정을 확실히 거릅니다. 승인자의 확인은 「이 요청이 업무에 맞는가」를 판단하고, 코드의 확인은 「이 사람이 지금 정책상 부여를 받을 수 있는 사람인가」를 판단합니다. 둘은 보는 것이 다르므로 함께 써야 합니다. 이 확인이 없으면 퇴사자에게 예외가 만들어져 목록에 남습니다.
- (다) 요청서의 `until`(2026-10-27 18:00)이 그대로 예외의 `expires` 가 되었습니다. 그 시각이 지나면 어제의 `find_exception` 이 `now < expires` 를 거짓으로 판정해 예외를 쓰지 않으므로 요청자는 다시 「권한 없음」으로 거부됩니다. 다만 만료된 예외가 `EXCEPTIONS` 에 계속 남으므로, 어제 만든 회수 점검(만료됨 · 퇴사자)을 매일 돌려 목록에서 정리 대상으로 뽑고 회수 이력을 남깁니다. 점검 담당과 주기(예: 보안 담당이 매일 아침)를 정해 두면 맞습니다.

**왜** — 승인과 부여 사이에 정책 확인을 두면, 사람의 승인이 정책 확인 없이 곧바로 부여로 이어지지 않습니다. 부여를 어제 만든 예외 권한으로 처리한 덕분에 새 판정 규칙을 만들 필요가 없고, 만료 시각도 그대로 적용됩니다. 「이미 허용이면 부여하지 않는다」는 규칙은 역할로 이미 가진 권한이 예외로 또 쌓이는 것을 막습니다.

**자주 틀리는 곳** — `check_permission` 의 결과를 확인하지 않고 바로 부여하면 퇴사자와 이미 권한이 있는 사람에게도 예외가 만들어집니다. 실행하면 다음처럼 3번과 4번도 `granted` 가 됩니다. 단계 3의 판정은 어제의 「사람 먼저 검사」가 막아 주지만, 쓸모없는 예외가 목록에 남고 이후 회수 점검에도 걸립니다.

```
--- 단계 1: 판정 - 부여 전
1 seoyeon SETTLE:QUERY -> False 권한 없음
2 gaeun SALES:QUERY -> False 권한 없음
3 dami SALES:QUERY -> False 퇴사한 계정
4 junho SETTLE:QUERY -> True 역할 권한
--- 단계 2: 부여 - 요청서마다 부여를 시도한다
1 seoyeon granted -> True 부여
2 gaeun rejected -> False 승인되지 않음
3 dami granted -> True 부여
4 junho granted -> True 부여
부여된 예외 번호: 6
부여된 예외 번호: 7
부여된 예외 번호: 8
--- 단계 3: 점검 - 부여 후
1 seoyeon SETTLE:QUERY -> True 예외 6번
2 gaeun SALES:QUERY -> False 권한 없음
3 dami SALES:QUERY -> False 퇴사한 계정
4 junho SETTLE:QUERY -> True 역할 권한
```

`ok or judge_reason != "권한 없음"` 을 `and` 로 쓰면 거의 모든 경우에 부여 쪽으로 넘어갑니다. `EXCEPTIONS` 에 더한 뒤 `request["status"]` 를 바꾸지 않으면 같은 요청서가 두 번 부여됩니다.

**관제에서는** — 오늘 요청서에 적은 `exception_id` 가 「이 예외는 어느 요청에서 나왔나」를 찾는 연결 정보입니다. 부여한 시각과 승인자까지 함께 남기면 감사에서 그대로 보여 줄 수 있습니다. 승인은 됐는데 부여가 막힌 요청서는 따로 모아 승인자에게 알립니다. 반복해서 부여되는 같은 권한은 예외를 계속 만들 것이 아니라 역할을 고쳐야 한다는 신호입니다.

---

### 앞 교시 파일 완성본

앞 교시 파일을 못 만들고 다음 교시로 넘어가야 할 때 그대로 만들어 씁니다. 정답 본문을 함수 머리말과 합친 전체 파일입니다.

**`req_create.py`** (2교시 완성본)

```python
from rbac import USERS                                           # 10/21(수)에 만든 사용자 딕셔너리를 불러온다

REQUESTS = []                                                    # 접수한 요청서를 모아 두는 목록(프로그램이 끝나면 사라진다)


def create_request(user, resource, action, until, reason, received_at):  # 요청자 · 자원 · 행위 · 희망 만료 시각 · 이유 · 접수 시각을 받는 함수
    """요청서를 만들어 REQUESTS 에 넣고 (True, 요청서)를 리턴한다. 접수할 수 없으면 (False, 이유)를 리턴한다."""
    if user not in USERS:                                        # 사용자 파일에 없는 이름이면
        return False, "등록되지 않은 사용자"                       # 접수하지 않고 이유를 알린다
    if reason == "":                                             # 이유가 비어 있으면
        return False, "이유가 없음"                                # 접수하지 않고 이유를 알린다
    if until <= received_at:                                             # 희망 만료 시각이 접수 시각보다 늦지 않으면(같은 형식의 글자는 앞에서부터 비교해도 시각 순서와 같다)
        return False, "만료 시각이 이미 지났음"                     # 접수하지 않고 이유를 알린다
    request = {"id": len(REQUESTS) + 1, "user": user, "resource": resource, "action": action,
               "permission": f"{resource}:{action}", "until": until, "reason": reason,
               "requested_at": received_at, "status": "reviewing"}       # 요청서 한 장. 상태는 검토 중으로 시작한다
    REQUESTS.append(request)                                     # 요청서 목록 끝에 더한다
    return True, request                                         # 접수했다고 알리고 요청서를 리턴한다
```

**`req_review.py`** (3교시 완성본)

```python
def approve_request(request, approver):                          # 요청서와 승인자 이름을 받는 함수
    """검토 중(reviewing)인 요청서만 승인한다. (성공 여부, 이유)를 리턴한다."""
    if request["status"] != "reviewing":                         # 검토 중이 아니면(이미 처리됐으면)
        return False, "검토 중이 아님"                             # 바꾸지 않고 이유를 알린다
    if request["user"] == approver:                              # 요청한 사람이 스스로 처리하려고 하면
        return False, "본인 요청은 처리할 수 없음"                  # 바꾸지 않고 이유를 알린다
    request["status"] = "approved"                               # 상태를 승인됨으로 바꾼다
    request["approver"] = approver                               # 누가 승인했는지 적어 둔다
    return True, "승인"                                          # 승인했다고 알린다


def reject_request(request, approver):                           # 요청서와 반려하는 사람 이름을 받는 함수
    """검토 중(reviewing)인 요청서만 반려한다. (성공 여부, 이유)를 리턴한다."""
    if request["status"] != "reviewing":                         # 검토 중이 아니면(이미 처리됐으면)
        return False, "검토 중이 아님"                             # 바꾸지 않고 이유를 알린다
    if request["user"] == approver:                              # 요청한 사람이 스스로 처리하려고 하면
        return False, "본인 요청은 처리할 수 없음"                  # 바꾸지 않고 이유를 알린다
    request["status"] = "rejected"                               # 상태를 반려됨으로 바꾼다
    request["approver"] = approver                               # 누가 반려했는지 적어 둔다
    return True, "반려"                                          # 반려했다고 알린다
```

**`req_grant.py`** (4교시 완성본)

```python
from rbac import check_permission                                # 10/21(수)에 만든 역할 판정 함수를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def grant_request(request):                                      # 요청서를 받는 함수
    """승인된 요청서를 정책으로 한 번 더 확인하고, 통과하면 예외 권한을 부여한다. (성공 여부, 이유)를 리턴한다."""
    if request["status"] != "approved":                          # 승인된 요청서가 아니면
        return False, "승인되지 않음"                              # 부여하지 않고 이유를 알린다
    ok, judge_reason = check_permission(request["user"], request["resource"], request["action"])   # 요청자를 지금 정책으로 판정한다
    if ok or judge_reason != "권한 없음":                                # 이미 허용이거나, 사람 자체가 거부 대상이면
        return False, f"부여하지 않음({judge_reason})"                    # 부여하지 않고 판정 이유를 알린다
    exception = {"id": len(EXCEPTIONS) + 1, "user": request["user"], "permission": request["permission"],
                 "expires": request["until"], "reason": request["reason"]}   # 요청서 내용으로 예외 한 건을 만든다
    EXCEPTIONS.append(exception)                                 # 예외 목록에 더한다
    request["exception_id"] = exception["id"]                    # 어느 예외를 부여했는지 요청서에 적어 둔다
    request["status"] = "granted"                                # 상태를 부여됨으로 바꾼다
    return True, "부여"                                          # 부여했다고 알린다
```
