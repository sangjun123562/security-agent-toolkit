# 10/29(목) 오전 · 3과목 접근통제 ④ — 접근 점검 · 필요 없어진 권한 찾기 — 실습

지난 10/23(금)까지는 권한을 **주는** 흐름(요청 → 승인 → 예외 권한 부여 → 기한 점검 → 기록 저장)을 만들었습니다. 오늘 오전에는 반대로 이미 **부여돼 있는 권한** 가운데 필요 없어진 것을 찾는 **접근 점검**을 만듭니다.

- **2교시**: 지금 누가 어떤 권한을 어떤 방법(역할 · 예외)으로 갖고 있는지 **현황 목록**을 만든다.
- **3교시**: 현황 목록에서 **규칙**으로 필요 없어진 권한(퇴사한 사람, 만료된 예외)을 찾는다.
- **4교시**: 규칙으로는 못 찾는 권한을 찾는다.

오늘은 오전 2 · 3 · 4교시, 오후 5 · 6교시이고, 깃허브에 올리는 일은 6교시 마지막에 한 번에 합니다. 교시마다 문제는 하나이고, 그 안에서 단계를 나눠 질문에 답합니다. 오늘은 **찾기까지만** 하고, 찾은 권한을 실제로 회수하는 일은 내일(10/30(금)) 합니다.

> 📦 **앞 수업에 결석했거나 파일이 없다면**: 수업 자료의 `day02_recovery` 폴더는 10/21(수) ~ 10/22(목)에 만든 파일의 완성본입니다. 이 폴더로 오늘 수업을 따라올 수 있습니다.
> - 들어 있는 것: `rbac.py` · `exception_policy.py` · `config_loader.py` · `policy.py` 와 `config` 폴더(`users.json` · `roles.json` · `exceptions.json`).
> - 오늘은 10/23(금)에 만든 파일을 쓰지 않으므로, 10/23(금)에 결석했어도 따로 준비할 것이 없습니다.
> - 넣는 방법은 아래 「시작하기」 2번에 있습니다.

**📎 오늘 불러 쓰는 이전 파일** — 오늘 코드가 `import` 로 가져다 쓰는 앞 수업 파일입니다. 없으면 오른쪽 열의 방법으로 먼저 준비합니다.

| 파일 | 만든 날 | 오늘 가져다 쓰는 것 | 쓰는 교시 | 없으면 |
|---|---|---|---|---|
| `rbac.py` | 10/21(수) | `USERS` · `ROLES` (`config/users.json` · `config/roles.json`) | 2교시 (3 · 4교시는 `review_list.py` 를 거쳐 씀) | `day02_recovery` 폴더 |
| `exception_policy.py` | 10/22(목) | `EXCEPTIONS` · `TIME_FORMAT` (`config/exceptions.json`) | 2 · 3 · 4교시 | `day02_recovery` 폴더 |
| `config_loader.py` | 10/22(목) | `load_json` | 4교시 | `day02_recovery` 폴더 |

- 오늘 만드는 파일도 뒤 교시가 가져다 씁니다. 2교시 `review_list.py` 는 3 · 4교시에서, 3교시 `review_rules.py` 는 4교시에서 씁니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 이전 파일을 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python -c "from rbac import USERS, ROLES; from exception_policy import EXCEPTIONS, TIME_FORMAT; from config_loader import load_json; print('이전 파일 정상', len(USERS), len(ROLES), len(EXCEPTIONS))"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다.
   - `rbac.py` · `exception_policy.py` · `config_loader.py` 가 보이고, `config` 안에 `users.json` · `roles.json` · `exceptions.json` 이 보여야 합니다.
   - 마지막 줄에 `이전 파일 정상 6 5 5` 가 나와야 합니다. 뒤의 숫자는 차례로 사용자 6명, 역할 5개, 예외 5건입니다. 숫자가 다르면 오늘 출력도 달라집니다.
   - 아니면 수업 자료로 받은 `day02_recovery` 폴더 안의 파일을 `access_control` 폴더에 넣고(`config` 안의 파일은 `config` 폴더에 넣습니다) 마지막 줄을 다시 칩니다.
3. **오늘 받은 파일 두 개를 `access_control` 폴더로 옮깁니다.** 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day04_am_access_review.md` (이 파일) — 오전 실습 안내. 읽기만 합니다.
   - `day04_am_report.md` — **오전 보고서.** 2 · 3 · 4교시 답을 여기에 적습니다.
4. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day04_am_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-29(목))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이며, 이유까지 설명합니다. 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일이 `config/…` 를 지금 위치 기준으로 찾기 때문입니다. `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **이전 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 지금 부여돼 있는 권한 현황 만들기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「지난주에 감사팀이 물었습니다. "지금 우리 회사에서 누가 어떤 권한을 갖고 있나요?" 저는 사용자 파일, 역할 파일, 예외 파일을 하나씩 열어 맞춰 보느라 반나절이 걸렸고, 그래도 빠뜨린 것이 없는지 자신이 없었습니다.
>
> 판정 함수는 요청이 올 때 허용인지 거부인지는 잘 가려 줍니다. 하지만 권한이 지금 어떻게 부여돼 있는지를 한곳에서 보여 주지는 않습니다. 먼저 누가 어떤 권한을 어떤 방법(역할 · 예외)으로 갖고 있는지 한곳에서 볼 수 있는 목록을 만들어 주세요.」
> - **왜 중요한가**: 지금은 누가 어떤 권한을 갖고 있는지 파일 세 개를 열어 직접 맞춰 봐야 해서, 빠뜨린 권한이 있어도 알 수 없습니다. 목록 하나로 모으면 ① 감사팀이 물을 때 바로 보여 줄 수 있고 ② 필요 없는 권한을 찾아 정리할 수 있습니다. 3교시와 4교시의 점검도 이 목록에서 시작합니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 앞 수업(10/21(수) ~ 10/23(금)) 흐름 복습

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 날짜 | 만든 것 | 기억할 것 |
|---|---|---|
| 10/21(수) | 역할 · 권한 파일, 판정 함수 `check_permission` | 허용 목록에 없으면 모두 거부 |
| 10/22(목) | 역할 부여 · 회수, 기간이 정해진 예외, 최종 판정 `evaluate_access` | 예외는 만료 시각이 지나면 거부, 퇴사한 사용자는 모두 거부 |
| 10/23(금) | 요청서 접수 → 승인 · 반려 → 예외 권한 부여, 처리 기한(SLA) 점검, 이력 저장 | 요청서 상태는 `reviewing` → `approved` → `granted` |

### 📖 왜 접근 점검이 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 권한은 **부여할 때는 절차를 거치지만, 회수할 때는 아무도 확인하지 않는** 일이 많습니다. 퇴사 · 부서 이동 · 프로젝트 종료가 지나도 권한이 그대로 남습니다.
2. 실제 업무에 필요한 것보다 많은 권한을 가진 상태를 **과다권한**(over-privilege · 오버 프리빌리지)이라고 합니다. 계정이 탈취되면 과다권한만큼 피해가 커집니다. 정기적으로 부여된 권한을 살펴보고 필요 없는 것을 가려내는 일을 **접근 점검**(access review · 액세스 리뷰)이라고 합니다.
3. 오늘 오전의 점검은 두 갈래입니다. 3교시는 파일에 적힌 사실로 걸러 냅니다(퇴사 · 만료). 4교시는 규칙으로 못 거르는 권한을 찾습니다.

### 📖 2.1 현황 목록의 한 건

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 현황 목록의 **한 건은 사용자 한 명의 권한 하나**이고, 딕셔너리로 적습니다. 같은 사용자가 권한을 세 개 가졌으면 세 건입니다. 코드에서는 이 한 건을 `entry`(엔트리)라고 부릅니다.
- **키**(key)는 딕셔너리에서 값을 찾는 이름입니다. 한 건의 키는 아래와 같습니다.

| 키 | 뜻 | 값의 예 |
|---|---|---|
| `user` | 권한을 가진 사용자 | `"seoyeon"` |
| `permission` | 권한 (`자원:행위`) | `"SALES:QUERY"` |
| `source` | 어떻게 받았나 | `"역할 sales"` · `"예외 1번"` |
| `employed` | 재직 여부 | `True` · `False` |
| `expires` | 예외의 만료 시각 (**예외로 받은 권한에만 있음**) | `"2026-10-22 18:00"` |

- `batch-night` 은 사람이 아니라 밤에 자동으로 도는 집계 프로그램이 쓰는 계정입니다(`employed` 는 `True` 로 둡니다).
- 권한을 받는 방법은 두 가지입니다. **역할**로 받으면 그 역할의 권한 목록이 모두 들어오고(10/21(수) `roles.json`), **예외**로 받으면 기간이 정해진 권한 한 건이 들어옵니다(10/22(목) `exceptions.json`).

```
+---------------------+
| build_access_list() |
+---------------------+
   |
   v
+-----------------------------------------+
| access_list = []  (현황을 담을 빈 목록) |
+-----------------------------------------+
   |
   v
+--------------------------------------+
| 사용자를 한 명씩 꺼낸다 (user, info) |
+--------------------------------------+
   |
   v
+--------------------------------------------------------------------------------------------------------------------+
| role_entries(user, info) 로 그 사용자가 역할로 받은 권한 목록을 얻어 access_list 뒤에 이어 붙인다 (미리 채운 함수) |
+--------------------------------------------------------------------------------------------------------------------+
   |
   v  사용자를 모두 꺼낸 뒤
+----------------------+
| 예외를 하나씩 꺼낸다 |
+----------------------+
   |
   v
+--------------------------------------------------------------------------------------------------+
| 권한 한 건을 만들어 access_list 에 추가한다  (source: 「예외 N번」, 만료 시각 expires 도 적는다) |
+--------------------------------------------------------------------------------------------------+
   |
   v  예외를 모두 꺼낸 뒤
access_list 를 리턴한다  (역할로 받은 권한 + 예외로 받은 권한)
```

**🐍 문법 상자 — 목록 이어 붙이기**

`+` 로 목록 두 개를 이으면, 두 목록의 값이 차례로 들어 있는 새 목록이 됩니다.

```python
a = ["QUERY", "CHANGE"]                                          # 목록 a
b = ["SETTLE"]                                                   # 목록 b
print(a + b)                                                     # 두 목록을 이은 새 목록을 출력한다
a = a + b                                                        # 이은 목록을 a 에 다시 담는다
print(a)                                                         # a 가 길어진 것을 출력한다
```

실행 결과:

```
['QUERY', 'CHANGE', 'SETTLE']
['QUERY', 'CHANGE', 'SETTLE']
```

- `access_list = access_list + role_entries(user, info)` 는 `access_list` 뒤에 그 사용자의 권한 목록을 이어 붙인 목록을 `access_list` 에 다시 담는 것입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 역할과 예외를 합쳐 지금 부여돼 있는 권한 현황 만들기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 누가 어떤 권한을 갖고 있는지 알려면 사용자 파일, 역할 파일, 예외 파일을 따로따로 열어 맞춰 봐야 합니다. 퇴사자나 만료된 예외가 섞여 있어도 한눈에 보이지 않습니다.
- **그래서 만드는 것**: `build_access_list` 입니다. 사용자마다 역할로 받은 권한 목록(미리 채운 `role_entries`)을 모으고, 예외로 받은 권한도 한 건씩 만들어 하나의 목록으로 리턴합니다. 건마다 어떻게 받았는지(`source`)와 재직 여부(`employed`)를 적습니다.
- **실행하면**: 단계 1은 현황 목록을 한 줄씩 출력하고, 단계 2는 사용자별 권한 개수를 출력합니다.
- **현업에서는**: 접근 점검 도구도 먼저 「누가 어떤 권한을 어떤 방법(역할 · 예외)으로 갖고 있나」 현황 목록부터 뽑습니다.

**🎯 할 일**

1. `review_list.py` 와 `day04_2-1_run.py` 두 파일을 만들고, `build_access_list` 본문을 직접 씁니다.
2. 실행해서 <mark>부여돼 있는 권한 현황</mark>(단계 1: 현황)과 <mark>사용자별 권한 개수</mark>(단계 2: 점검)를 읽습니다.

**`review_list.py`**

```python
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def role_entries(user, info):                                    # 사용자 이름과 그 사용자의 정보 딕셔너리를 받는 함수
    """사용자 한 명이 역할로 받은 권한을 현황의 권한 한 건씩 만들어 목록으로 리턴한다."""
    role = info["role"]                                          # 그 사용자의 역할을 꺼낸다
    entries = []                                                 # 역할로 받은 권한을 담을 빈 목록
    for permission in ROLES.get(role, []):                       # 역할의 권한을 하나씩 꺼낸다(역할 파일에 없는 역할이면 빈 목록)
        entry = {"user": user, "permission": permission, "source": f"역할 {role}", "employed": info["employed"]}  # 현황의 권한 한 건을 만든다
        entries.append(entry)                                    # 목록에 추가한다
    return entries                                               # 역할로 받은 권한 목록을 리턴한다


def build_access_list():                                         # 지금 부여돼 있는 권한을 모두 모아 목록으로 만드는 함수
    """부여돼 있는 권한을 모아 리턴한다. 목록의 한 건 = 사용자 한 명의 권한 하나(역할로 받았거나 예외로 받은 것)."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 현황을 담을 빈 목록 access_list 를 만든다
    # 2. USERS 에서 user, info 를 하나씩 꺼낸다 (.items())
    # 3.   access_list 와 role_entries(user, info) 를 + 로 이은 목록을 access_list 에 다시 담는다
    # 4. EXCEPTIONS 에서 exception 을 하나씩 꺼낸다
    # 5.   exception["user"] 를 user 에 담는다
    # 6.   딕셔너리 entry 를 만든다: "user" 는 user, "permission" 은 exception["permission"], "source" 는 f"예외 {exception['id']}번", "employed" 는 USERS[user]["employed"]
    # 7.   entry["expires"] 를 exception["expires"] 로 정한다 (예외에만 있는 키)
    # 8.   access_list 에 entry 를 추가한다
    # 9. access_list 를 리턴한다
```

- 본문은 모두 함수 안이라 앞에 공백 4개를 넣고(Tab 키 한 번), `for` 안쪽은 공백 4개 더(8개) 넣습니다. 마지막 `return` 은 `for` 밖이므로 공백 4개입니다. `role_entries` 는 미리 채워 두었으니 그대로 둡니다.
- 6번의 딕셔너리는 한 줄에 쓰거나, `{ }` 안에서 `,` 뒤에 줄을 바꿔 써도 됩니다.
- 채우기 전에 실행하면 `TypeError: object of type 'NoneType' has no len()` 오류가 납니다. 함수가 아무것도 리턴하지 않아 `len(access_list)` 를 셀 수 없기 때문입니다.

**`day04_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 단계 1은 현황을 한 줄씩 출력하고, 단계 2는 사용자별 권한 개수를 셉니다.

```python
from review_list import build_access_list                        # 방금 만든 현황 함수를 불러온다

access_list = build_access_list()                                # 지금 부여돼 있는 권한 현황을 만든다

print("--- 단계 1: 현황 - 부여돼 있는 권한", len(access_list), "건")   # 단계 1 시작을 알리는 줄
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    print(entry["user"], entry["permission"], "<-", entry["source"], "| 재직", entry["employed"])   # 사용자 · 권한 <- 출처 | 재직 여부를 출력한다

print("--- 단계 2: 점검 - 사용자별 권한 개수")                     # 단계 2 시작을 알리는 줄
counts = {}                                                      # 사용자 → 권한 개수를 담을 빈 딕셔너리
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    counts[entry["user"]] = counts.get(entry["user"], 0) + 1     # 그 사용자의 개수를 1 늘린다
print(counts)                                                    # 사용자별 개수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `review_list.py` · `day04_2-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch review_list.py` → `touch day04_2-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim review_list.py` → `vim day04_2-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `review_list.py` 의 `build_access_list` 본문을 직접 씁니다. 2.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 이어서 실행합니다.
   ```bash
   pwd
   python day04_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day04_2-1_run.py` 실행할 파일
   - 맥북은 `python3 day04_2-1_run.py` 로 칩니다.
4. 출력은 두 단계입니다. 단계 1은 `부여돼 있는 권한 N 건` 한 줄과 현황 목록이고, 단계 2는 사용자별 권한 개수 딕셔너리 한 줄입니다.
5. **[보고서]** `day04_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 부여돼 있는 권한이 모두 몇 건인지, 그중 예외로 받은 권한이 몇 건인지, 현황에 권한이 하나도 없는 사용자가 있다면 누구이고 그 이유는 무엇인지 적어 주세요.
     - 현황에 권한이 하나도 없는 사용자는 `config/users.json` 의 사용자와 출력의 사용자를 비교해 찾고, 이유는 그 사용자의 역할이 `config/roles.json` 에 있는지 열어 확인합니다.
   - (나) 🔍 현황 목록에는 판정 함수(`check_permission` · `evaluate_access`)가 이미 거부하는 권한도 들어 있습니다. 어떤 권한이 그런지 예를 하나 들고, 거부되는 권한을 목록에서 빼지 않고 남겨 두는 것이 점검에 왜 필요한지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 현황의 권한 한 건 | 딕셔너리. 키는 `user` · `permission` · `source` · `employed` (예외 권한은 `expires` 도) |
| 사용자와 정보를 같이 꺼내기 | `for user, info in USERS.items():` |
| 사용자가 역할로 받은 권한 목록 | `role_entries(user, info)` (미리 채움) |
| 목록 이어 붙이기 | `access_list = access_list + 목록` |
| 예외로 받은 권한에만 추가하는 키 | `entry["expires"] = exception["expires"]` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 규칙으로 필요 없어진 권한 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「현황 목록을 뽑아 보니 퇴사로 표시된 사용자의 권한도 보이고, 예외 파일을 열어 보면 이미 기간이 끝난 예외도 있습니다. 지금은 열네 건이라 제가 건마다 사용자 파일을 열어 퇴사 여부를, 예외 파일을 열어 만료 시각을 확인하고 있는데, 10분이 넘게 걸리고 한 건을 놓칠 수도 있습니다. 감사팀은 이 확인을 매주 하라고 합니다.
>
> 퇴사나 기간 만료처럼 파일에 적힌 사실만 보면 되는 것은 코드가 걸러 내 주세요. 걸러 낸 권한마다 왜 걸렸는지도 적어 주면, 저는 이유만 보고 정리할지 정할 수 있습니다.」
> - **왜 중요한가**: 퇴사 여부와 만료 시각을 사람이 건마다 확인하면 10분이 넘게 걸리고 한 건을 놓칠 수 있는데, 이 확인은 매주 해야 합니다. 코드가 열네 건을 같은 기준으로 한 번에 검사하고 걸린 이유까지 붙여 주면, 담당자는 이유만 보고 정리할지 정하면 됩니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 퇴사한 사람의 권한이나 기간이 끝난 예외는 사람이 판단할 것이 없습니다. 사실만 보고 바로 걸러 낼 수 있는 **규칙**입니다.
2. 규칙으로 걸러 낼 수 있는 것은 코드에 맡기고, 사람은 규칙으로 안 걸리는 것(다음 교시)에 시간을 씁니다.

### 📖 3.1 오늘의 두 규칙

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- **stale**(스테일)은 「오래돼서 쓸모없어진」이라는 뜻입니다. 여기서는 퇴사한 사람의 권한이나 기간이 끝난 예외처럼, 시간이 지나 필요 없어진 권한을 말합니다. 그래서 `find_stale` 은 그런 권한을 찾는 함수이고, 변수 `stale` 은 그렇게 찾은 권한의 목록입니다.

| 규칙 | 걸리는 조건 | 쓰는 키 | `reason` |
|---|---|---|---|
| 퇴사 | `employed` 가 `False` | `employed` | `"퇴사한 계정"` |
| 예외 만료 | 만료 시각이 지금과 같거나 이미 지남 | `expires` | `"만료된 예외"` |

- 권한 한 건이 두 규칙에 모두 걸릴 수도 있습니다(퇴사한 사람의 만료된 예외). 그때는 이유를 하나만 적도록 `if` 다음에 `elif` 를 씁니다. 오늘 데이터에는 이런 권한이 없습니다.
- 10/22(목)에도 예외의 만료와 퇴사자를 목록으로 뽑아 봤습니다. 오늘은 역할로 받은 권한까지 포함한 **현황 전체**를 한 함수로 점검합니다.
- 만료 시각의 비교는 10/22(목)과 같습니다. 만료 시각이 지금과 같거나 이미 지났으면 만료입니다(`<= now`).

```
+---------------------------------------------------------------------------------------+
| find_stale(access_list, now)  (현황과 지금 시각을 받아, 규칙에 걸린 권한을 골라 리턴) |
+---------------------------------------------------------------------------------------+
   |
   v
+--------------------------------------------+
| stale = []  (규칙에 걸린 권한을 담을 목록) |
+--------------------------------------------+
   |
   v
+-----------------------------------------------------------------+
| 현황의 권한을 한 건씩 꺼낸다  (아래 판단을 권한마다 되풀이한다) |
+-----------------------------------------------------------------+
   |
   v
+-------------------------+
| employed 가 False 인가? |
+-------------------------+
   |
   +--> 그렇다 --> reason = "퇴사한 계정"
   |
   v  아니다
+------------------------------------------------------------------+
| 예외 권한이고(expires 가 있고) 만료 시각이 now 와 같거나 지났나? |
+------------------------------------------------------------------+
   |
   +--> 그렇다 --> reason = "만료된 예외"
   |
   v  아니다
+--------------------------------------------------------+
| reason 이 비어 있다 = 규칙에 안 걸림 --> 다음 권한으로 |
+--------------------------------------------------------+
   |
   v  reason 이 적혔으면
+--------------------------------------------------+
| 권한을 복사해 reason 키를 적고 stale 에 추가한다 |
+--------------------------------------------------+
   |
   v  모든 권한을 꺼낸 뒤
stale 을 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 현황에서 퇴사한 계정과 만료된 예외 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 현황 목록에 열네 건이 있고, 관제 담당이 건마다 퇴사 여부를 보고 예외 파일을 열어 만료 시각을 눈으로 확인합니다. 시간이 걸리고 놓칠 수 있습니다.
- **그래서 만드는 것**: `find_stale` 입니다. 현황 목록과 지금 시각을 받아, 규칙에 걸린 권한을 복사해 `reason` 키를 추가하고 목록으로 리턴합니다. 원래 현황 권한은 바꾸지 않습니다.
- **실행하면**: 단계 1은 규칙에 걸린 권한을 이유와 함께 출력하고, 단계 2는 이유별 건수를 출력합니다. 지금 시각은 `2026-10-29 10:00` 으로 고정합니다.
- **현업에서는**: 계정 관리 도구도 퇴사 처리가 안 된 계정과 기한이 지난 임시 권한을 정기 점검 목록으로 뽑아 담당자에게 보냅니다.

**🎯 할 일**

1. `review_rules.py` 와 `day04_3-1_run.py` 두 파일을 만들고, `find_stale` 본문을 직접 씁니다.
2. 실행해서 <mark>규칙에 걸린 권한</mark>(단계 1: 판정)과 <mark>이유별 건수</mark>(단계 2: 점검)를 읽습니다.

**`review_rules.py`**

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def find_stale(access_list, now):                                # 현황 목록과 지금 시각(datetime)을 받는 함수
    """규칙에 걸려 필요 없어진 권한을 리턴한다. 걸린 권한마다 "reason" 키에 이유를 적는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 걸린 권한을 담을 빈 목록 stale 을 만든다
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    # 3.   entry.get("expires") 를 expires 에 담는다 (역할로 받은 권한에는 이 키가 없어 None 이 된다)
    # 4.   빈 글자 ""를 reason 에 담는다
    # 5.   entry["employed"] 가 False 이면(재직이 아니면) reason 을 "퇴사한 계정" 으로 정한다
    # 6.   아니고(elif), expires 가 None 이 아니면서 datetime.strptime(expires, TIME_FORMAT) 이 now 와 같거나 now 보다 이전이면(<= now) reason 을 "만료된 예외" 로 정한다
    # 7.   reason 이 빈 글자가 아니면
    # 8.     entry.copy() 를 stale_entry 에 담는다
    # 9.     stale_entry["reason"] 을 reason 으로 정한다
    # 10.    stale 에 stale_entry 를 추가한다
    # 11. stale 을 리턴한다
```

- `find_stale` 의 본문은 함수 안이라 앞에 공백 4개를 넣고(Tab 키 한 번), `for` 안쪽은 공백 4개 더(8개), `if` 안쪽은 또 4개 더(12개) 넣습니다. 마지막 `return` 은 `for` 밖이므로 공백 4개입니다.
- `expires` 가 `None` 인지는 `== None` 이 아니라 `is None`(아니면 `is not None`)으로 묻습니다. `expires is not None` 은 「`expires` 가 `None` 이 아니다」, 곧 만료 시각이 적혀 있다(예외로 받은 권한)는 뜻입니다.
- 6번의 조건은 길지만 한 줄로 씁니다. 순서는 「`expires` 가 `None` 이 아니다 → 그러면 시각으로 바꿔 비교」입니다. `and` 는 앞이 거짓이면 뒤를 보지 않으므로, `None` 일 때 `strptime` 이 실행되지 않아 오류가 나지 않습니다.
- 채우기 전에 실행하면 `TypeError: object of type 'NoneType' has no len()` 오류가 납니다. `find_stale` 이 아무것도 리턴하지 않기 때문입니다.

**`day04_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 2교시의 `build_access_list` 로 현황을 만든 뒤 `find_stale` 로 규칙에 걸린 권한을 찾아 출력합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 방금 만든 규칙 점검 함수를 불러온다

NOW = datetime.strptime("2026-10-29 10:00", "%Y-%m-%d %H:%M")    # 오늘 실습의 지금 시각(고정)

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다

print("--- 단계 1: 판정 - 규칙에 걸린 권한", len(stale), "건 (전체", len(access_list), "건 중)")   # 단계 1 시작을 알리는 줄
for entry in stale:                                              # 걸린 권한을 한 건씩 꺼낸다
    print(entry["user"], entry["permission"], "<-", entry["source"], "|", entry["reason"])   # 사용자 · 권한 <- 출처 | 이유를 출력한다

print("--- 단계 2: 점검 - 이유별 건수")                           # 단계 2 시작을 알리는 줄
counts = {}                                                      # 이유 → 건수를 담을 빈 딕셔너리
for entry in stale:                                              # 걸린 권한을 한 건씩 꺼낸다
    counts[entry["reason"]] = counts.get(entry["reason"], 0) + 1   # 그 이유의 건수를 1 늘린다
print(counts)                                                    # 이유별 건수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `review_rules.py` · `day04_3-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch review_rules.py` → `touch day04_3-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim review_rules.py` → `vim day04_3-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `review_rules.py` 의 `find_stale` 본문을 직접 씁니다. 3.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 이어서 실행합니다.
   ```bash
   pwd
   python day04_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day04_3-1_run.py` 실행할 파일
   - 맥북은 `python3 day04_3-1_run.py` 로 칩니다.
4. 출력은 두 단계입니다. 단계 1은 `규칙에 걸린 권한 N 건` 한 줄과 걸린 권한, 단계 2는 이유별 건수 딕셔너리 한 줄입니다.
5. **[보고서]** `day04_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 규칙에 걸린 권한이 이유별로 몇 건인지 적어 주세요.
   - (나) 🔍 퇴사한 계정과 만료된 예외는 파일에 적힌 사실로 걸러 냈습니다. 이 규칙으로는 걸러 낼 수 없지만 필요 없을 수 있는 권한의 예를 하나 들고, 그것을 찾으려면 어떤 정보가 더 필요한지 적어 주세요.
   - (다) 🔍 규칙에 걸린 7건을 내일 회수한다면 어떤 것부터 회수할까요? 출력의 이유(퇴사한 계정 · 만료된 예외)를 보고 기준을 하나 정해, 그 기준으로 이유를 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 없을 수도 있는 키 꺼내기 | `expires = entry.get("expires")` |
| 퇴사 규칙 | `if not entry["employed"]: reason = "퇴사한 계정"` |
| 예외 만료 규칙 | `elif expires is not None and datetime.strptime(expires, TIME_FORMAT) <= now:` |
| 걸린 권한에 이유 적기 | `stale_entry = entry.copy()` → `stale_entry["reason"] = reason` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 사용 이력으로 90일 넘게 안 쓴 권한 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「규칙으로 걸러 낸 뒤에도 재직 중인 사람의 권한이 남습니다. 그중에는 받아 놓고 실제로는 쓰지 않는 권한이 있을 수 있습니다. 사용 기록을 모아 둔 사용 이력 파일이 있으니, 그것으로 90일 넘게 쓰지 않은 권한을 후보로 뽑아 주세요.
>
> 이번에는 뽑기만 하고 회수하지는 않습니다. 어떤 권한을 회수할지는 후보를 본 뒤에 정하겠습니다.」
> - **왜 중요한가**: 계정을 다른 사람이 가로채면, 그 계정이 가진 권한만큼 가로챈 사람이 할 수 있는 일이 생깁니다. 쓰지도 않는 권한이 많을수록 그 일만 늘어납니다. 사용 이력의 「마지막으로 쓴 시각」을 보면 90일 넘게 안 쓴 권한을 찾아 줄일 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 규칙(퇴사 · 만료)에 안 걸려도 필요 없는 권한이 있습니다. 부여 때는 필요했지만 일이 끝나서 이제 안 쓰는 권한입니다.
2. 이런 권한은 **마지막으로 쓴 시각**을 보면 알 수 있습니다. 권한은 있는데 오래 쓴 이력이 없으면 과다권한의 후보입니다.
3. 오늘은 **찾기만** 하고 회수하지 않습니다. 회수는 내일 합니다.

### 📖 4.1 사용 이력과 비교하는 방법

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 사용 이력 파일 `config/access_log.json` 의 한 건은 「누가 어떤 권한을 마지막으로 언제 썼나」입니다. 사용자와 권한마다 한 건만 있습니다.
- `load_last_used` 는 사용 이력 파일을 딕셔너리 하나로 바꿉니다. 이 딕셔너리의 키는 `user` 와 `permission` 을 `:` 로 이어 붙인 글자(예: `"seoyeon:SALES:QUERY"`)이고, 값은 마지막으로 쓴 시각 글자입니다. 현황의 권한 한 건에서도 같은 방법으로 키 글자를 만들어 마지막 사용 시각을 찾습니다.
- 이름이 비슷한 두 가지를 구별합니다. `last_used_map` 은 사용 이력 딕셔너리(「사용자:권한」 글자 → 마지막으로 쓴 시각 글자)이고, `"last_used"` 는 후보에 추가하는 키(값은 마지막으로 쓴 시각 글자, 이력이 없으면 `None`)입니다.

- 실행 파일은 `find_unused` 를 부르기 전에 3교시 규칙에 이미 걸린 권한(퇴사한 dami 포함)을 현황에서 뺍니다. 권한 한 건마다 `user:permission:source` 를 이어 붙인 글자(**식별 키**)를 만들어 비교하는 방법인데, 오후 5교시에서 자세히 설명하므로 오늘은 붙여 넣기만 합니다.

| 현황의 권한 한 건의 상태 | 판정 |
|---|---|
| 사용 이력이 없음 | 안 쓴 후보 (`last_used` 는 `None`) |
| 마지막 사용이 90일보다 오래됨 (91일째부터) | 안 쓴 후보 |
| 마지막 사용이 90일 이내 (90일째 포함) | 쓴 것 → 후보 아님 |

```
+----------------------------------------------------------+
| find_unused(access_list, last_used_map, now, limit_days) |
+----------------------------------------------------------+
   |
   v
+--------------------------------------------+
| unused = []  (오래 안 쓴 권한을 담을 목록) |
+--------------------------------------------+
   |
   v
+----------------------------------------------------------------------------------------+
| 현황의 권한을 한 건씩 꺼내 「사용자:권한」 글자로 마지막 사용 시각(used_text)을 찾는다 |
+----------------------------------------------------------------------------------------+
   |
   v
+------------------------------------------+
| used_text 가 None 인가? (사용 이력 없음) |
+------------------------------------------+
   |
   +--> 그렇다 --> 마지막 사용 시각이 None 인 복사본을 unused 에 추가한다   (다음 권한으로)
   |
   v  아니다
+-----------------------------------------------------+
| 마지막 사용 이후 지난 일 수가 limit_days 보다 큰가? |
+-----------------------------------------------------+
   |
   +--> 그렇다 --> 마지막 사용 시각을 적은 복사본을 unused 에 추가한다   (다음 권한으로)
   |
   +--> 아니다 --> 최근에 쓴 것이므로 그대로 둔다   (다음 권한으로)
   |
   v  모든 권한을 꺼낸 뒤
unused 를 리턴한다
```

**🐍 문법 상자 — 안 쓴 일 수 구하기**

**① `.days` 는 시각 차이에서 「일」만 숫자로 알려 줍니다**

```python
from datetime import datetime                                       # 시각을 다루는 모듈에서 datetime 을 불러온다
used_at = datetime.strptime("2026-07-31 10:00", "%Y-%m-%d %H:%M")   # 마지막으로 쓴 시각
now = datetime.strptime("2026-10-29 10:00", "%Y-%m-%d %H:%M")       # 지금 시각
gap = now - used_at                                                 # 시각에서 시각을 빼면 안 쓴 시간이 나온다
print(gap)                                                          # 「90 days, 0:00:00」 처럼 일과 시:분:초로 나온다
print(gap.days)                                                     # .days 는 그중 「일」 부분만 숫자로 준다
print(gap.days <= 90)                                               # 90일째는 90 이하이므로 참이다
```

실행 결과:

```
90 days, 0:00:00
90
True
```

- 시각에서 시각을 빼면 `90 days, 0:00:00` 처럼 일과 시:분:초가 함께 나옵니다. 일 수만 비교할 때는 `.days` 를 씁니다.
- 이 계산은 아래 `review_unused.py` 의 `days_since` 함수에 미리 채워 두었습니다. 직접 쓰지 않고, 읽고 이해만 합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 사용 이력으로 90일 넘게 안 쓴 권한 후보 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 규칙에 안 걸린 재직자의 권한 일곱 건은 겉으로는 문제가 없어 보여서, 쓰는 권한인지 안 쓰는 권한인지 알 수 없습니다.
- **그래서 만드는 것**: `find_unused` 입니다. 현황 · 마지막 사용 시각 딕셔너리 · 지금 시각 · 기준 일 수를 받아, 마지막 사용이 기준 일 수보다 오래됐거나 사용 이력이 없는 권한을 복사해 `last_used` 키를 추가하고 목록으로 리턴합니다.
- **실행하면**: 단계 1은 규칙에 안 걸린 권한 일곱 건이 며칠째 안 쓰였는지 출력하고, 단계 2는 90일 넘게 안 쓴 후보를 출력합니다. 규칙에 이미 걸린 권한은 실행 파일이 미리 뺍니다.
- **현업에서는**: 접근 관리 도구도 「마지막 사용일」 기준(예: 90일)으로 안 쓰는 권한을 모아 담당자에게 확인을 요청합니다.

**🎯 할 일**

1. `config/access_log.json` · `review_unused.py` · `day04_4-1_run.py` 세 파일을 만들고, `find_unused` 본문을 직접 씁니다.
2. 실행해서 <mark>안 쓴 일 수</mark>(단계 1: 현황)와 <mark>90일 넘게 안 쓴 후보</mark>(단계 2: 판정)를 읽습니다.

**`config/access_log.json`** — 그대로 붙여 넣습니다. 사용 이력입니다. `access_control` 안의 `config` 폴더에 만듭니다.

```json
[
  {"user": "seoyeon", "permission": "SALES:QUERY", "last_used": "2026-10-27 09:10"},
  {"user": "seoyeon", "permission": "SALES:CHANGE", "last_used": "2026-06-30 14:00"},
  {"user": "junho", "permission": "SALES:QUERY", "last_used": "2026-07-30 09:00"},
  {"user": "junho", "permission": "SETTLE:QUERY", "last_used": "2026-07-31 10:00"},
  {"user": "gaeun", "permission": "ACCOUNT:QUERY", "last_used": "2026-10-20 08:00"},
  {"user": "batch-night", "permission": "SETTLE:QUERY", "last_used": "2026-10-29 02:00"},
  {"user": "dami", "permission": "SALES:QUERY", "last_used": "2026-10-10 13:00"}
]
```

**`review_unused.py`**

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def load_last_used():                                            # 사용 이력 파일을 읽어 「마지막 사용 시각」 딕셔너리를 만드는 함수
    """「사용자:권한」 글자를 키로, 마지막으로 쓴 시각 글자를 값으로 하는 딕셔너리를 리턴한다."""
    last_used_map = {}                                           # 빈 딕셔너리로 시작한다
    for log in load_json("config/access_log.json", []):          # 사용 이력을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        key = f"{log['user']}:{log['permission']}"               # 「사용자:권한」 글자를 키로 만든다
        last_used_map[key] = log["last_used"]                    # 그 키의 값에 마지막 사용 시각 글자를 담는다
    return last_used_map                                         # 딕셔너리를 리턴한다


def make_unused(entry, used_text):                               # 현황의 권한 한 건과 마지막 사용 시각 글자를 받는 함수
    """권한 한 건을 복사해 "last_used" 키(마지막 사용 시각, 이력이 없으면 None)를 적어 리턴한다. 원래 권한은 바꾸지 않는다."""
    unused_entry = entry.copy()                                  # 원래 권한은 바꾸지 않고 복사한다
    unused_entry["last_used"] = used_text                        # 복사본에 마지막 사용 시각(없으면 None)을 적는다
    return unused_entry                                          # 복사본을 리턴한다


def days_since(used_text, now):                                  # 마지막 사용 시각 글자와 지금 시각을 받는 함수
    """마지막 사용 시각 글자를 시각으로 바꿔, 지금까지 안 쓴 일 수를 리턴한다."""
    used_at = datetime.strptime(used_text, TIME_FORMAT)          # 글자를 시각으로 바꾼다
    return (now - used_at).days                                  # 지금 - 마지막 사용 시각의 일 수를 리턴한다


def find_unused(access_list, last_used_map, now, limit_days):    # 현황 · 마지막 사용 시각 딕셔너리 · 지금 시각 · 기준 일 수를 받는 함수
    """마지막 사용이 limit_days 일보다 오래됐거나 사용 이력이 없는 권한을 리턴한다. 후보마다 "last_used" 키에 마지막 사용 시각(없으면 None)을 적는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 후보를 담을 빈 목록 unused 를 만든다
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    # 3.   f"{entry['user']}:{entry['permission']}" 를 key 에 담는다
    # 4.   last_used_map.get(key) 를 used_text 에 담는다 (이력이 없으면 None)
    # 5.   used_text 가 None 이면 (is None, 사용 이력이 없음)
    # 6.     make_unused(entry, None) 을 unused 에 추가한다
    # 7.   아니고(elif), days_since(used_text, now) 가 limit_days 보다 크면 (>)
    # 8.     make_unused(entry, used_text) 를 unused 에 추가한다
    # 9. unused 를 리턴한다
```

- `find_unused` 의 본문은 함수 안이라 앞에 공백 4개를 넣고(Tab 키 한 번), `for` 안쪽은 공백 4개 더(8개), `if` · `elif` 안쪽은 또 4개 더(12개) 넣습니다. 마지막 `return` 은 `for` 밖이므로 공백 4개입니다. `load_last_used` · `make_unused` · `days_since` 는 미리 채워 두었으니 그대로 둡니다.
- `used_text is None` 은 「값이 `None` 인가」를 묻는 것입니다. `.get(key)` 는 키가 없으면 `None` 을 주므로 `None` 이면 사용 이력이 없다는 뜻입니다. 그 경우에는 일 수를 계산할 수 없으니, `days_since` 는 사용 이력이 있을 때(`elif`)만 부릅니다. `elif` 는 3교시의 `find_stale` 에서 쓴 것과 같습니다.
- 채우기 전에 실행하면 `TypeError: object of type 'NoneType' has no len()` 오류가 납니다. `find_unused` 가 아무것도 리턴하지 않기 때문입니다.

**`day04_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 현황을 만들고, 3교시의 `find_stale` 에 걸린 권한을 뺀 뒤, 남은 권한이 며칠째 안 쓰였는지 출력하고 `find_unused` 로 후보를 찾습니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 방금 만든 미사용 점검 함수를 불러온다

NOW = datetime.strptime("2026-10-29 10:00", "%Y-%m-%d %H:%M")    # 오늘 실습의 지금 시각(고정)
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 글자의 형식

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 이미 걸린 권한을 찾는다
stale_keys = []                                                  # 이미 걸린 권한의 식별 키(「사용자:권한:출처」 글자)를 담을 빈 목록
for entry in stale:                                              # 이미 걸린 권한을 한 건씩 꺼낸다
    stale_keys.append(entry["user"] + ":" + entry["permission"] + ":" + entry["source"])   # 그 권한의 식별 키를 목록에 추가한다
not_stale = []                                                   # 규칙에 안 걸린 권한을 담을 빈 목록
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    if entry["user"] + ":" + entry["permission"] + ":" + entry["source"] not in stale_keys:   # 식별 키가 걸린 목록에 없으면
        not_stale.append(entry)                                     # 규칙에 안 걸린 목록에 추가한다

last_used_map = load_last_used()                                     # 마지막 사용 시각 딕셔너리를 읽는다
print("--- 단계 1: 현황 - 규칙에 안 걸린 권한", len(not_stale), "건의 안 쓴 일 수")   # 단계 1 시작을 알리는 줄
for entry in not_stale:                                             # 규칙에 안 걸린 권한을 한 건씩 꺼낸다
    used_text = last_used_map.get(entry["user"] + ":" + entry["permission"])   # 마지막 사용 시각 글자를 꺼낸다
    if used_text is None:                                        # 사용 이력이 없으면
        print(entry["user"], entry["permission"], "-> 사용 이력 없음")   # 이력이 없다고 출력한다
    else:                                                        # 기록이 있으면
        idle_days = (NOW - datetime.strptime(used_text, TIME_FORMAT)).days   # 안 쓴 일 수를 구해서
        print(entry["user"], entry["permission"], "->", idle_days, "일째 안 씀")   # 출력한다

unused = find_unused(not_stale, last_used_map, NOW, 90)                 # 90일보다 오래 안 쓴 권한을 찾는다
print("--- 단계 2: 판정 - 90일 넘게 안 쓴 후보", len(unused), "건")   # 단계 2 시작을 알리는 줄
for entry in unused:                                             # 후보를 한 건씩 꺼낸다
    print(entry["user"], entry["permission"], "<-", entry["source"])   # 사용자 · 권한 <- 출처를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `config/access_log.json` · `review_unused.py` · `day04_4-1_run.py` 입니다. `access_control` 폴더를 선택한 채로 `config/access_log.json` 을 입력하면 `config` 폴더 안에 만들어집니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널의 위치가 `access_control` 인지 `pwd` 로 먼저 확인합니다. 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch config/access_log.json` → `touch review_unused.py` → `touch day04_4-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim config/access_log.json` → `vim review_unused.py` → `vim day04_4-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[터미널]** 파일을 만든 뒤 `ls config` 를 쳐서 `access_log.json` 이 `users.json` 과 같은 `config` 폴더 안에 있는지 확인합니다.
   - `config` 안에 또 `config` 가 생겼다면 위치가 틀린 것이니 옮깁니다.
   - 붙여 넣은 내용이 맞는지 `python -m json.tool config/access_log.json` 으로 확인합니다(맥북은 `python3 -m json.tool …`). 여러 줄로 정리되어 출력되면 정상이고, 오류가 나면 붙여 넣을 때 글자가 빠진 것입니다. 깨진 채 두면 사용 이력을 못 읽어 모든 권한이 「이력 없음」으로 나옵니다.
3. **[VS Code]** `review_unused.py` 의 `find_unused` 본문을 직접 씁니다. 4.1 의 표와 그림, 문법 상자를 보고 씁니다.
4. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 이어서 실행합니다.
   ```bash
   pwd
   python day04_4-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day04_4-1_run.py` 실행할 파일
   - 맥북은 `python3 day04_4-1_run.py` 로 칩니다.
5. 출력은 두 단계입니다. 단계 1은 규칙에 안 걸린 권한 일곱 건의 안 쓴 일 수(일곱 줄), 단계 2는 90일 넘게 안 쓴 후보입니다.
6. **[보고서]** `day04_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 90일 넘게 안 쓴 후보가 몇 건인지와 후보마다 며칠째 안 쓰였는지 적어 주세요.
     - 며칠째인지는 단계 1 출력에서 후보와 같은 사용자 · 권한의 줄을 찾아 적습니다. 사용 이력이 없는 후보는 단계 1 에 「사용 이력 없음」으로 나옵니다.
   - (나) 🔍 junho 의 `SETTLE:QUERY` 는 마지막 사용이 90일 전이라 후보에서 빠졌고, 같은 junho 의 `SALES:QUERY` 는 91일 전이라 후보에 들어갔습니다. 하루 차이로 나누는 기준은 합리적일까요? 경계 부근에서 담당자가 추가로 확인할 것도 적어 주세요.
   - (다) 🔍 사용 이력이 없는 권한을 바로 지우면 위험한 경우가 있습니다. 어떤 경우인지 예를 들고, 지우기 전에 무엇을 확인해야 하는지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 마지막 사용 시각을 찾는 키 글자 | `key = f"{entry['user']}:{entry['permission']}"` |
| 마지막 사용 시각 찾기 | `used_text = last_used_map.get(key)` (이력이 없으면 `None`) |
| 사용 이력이 없는지 | `if used_text is None:` |
| 사용 이력이 있고 기준을 넘었는지 | `elif days_since(used_text, now) > limit_days:` (`days_since` 는 미리 채움) |
| 후보에 추가하기 | `unused.append(make_unused(entry, used_text))` (`make_unused` 는 미리 채움) |

---

## 오전 마무리 — 보고서 2 · 3 · 4교시 칸 확인

`day04_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지 봅니다. `access_control` 폴더에 오늘 만든 파일이 있는지 확인합니다.

```bash
ls
ls config
```

- `review_list.py` · `review_rules.py` · `review_unused.py` · `day04_2-1_run.py` · `day04_3-1_run.py` · `day04_4-1_run.py` 가 보여야 합니다. `config` 안에는 `access_log.json` 이 새로 보여야 합니다.

오후에는 오늘 오전에 찾은 결과를 합쳐 **과다권한 종합 리포트**를 만들고 회수하지 않을 권한을 가려냅니다. 올리기(git)는 오후 6교시 마지막에 한 번에 합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
python day04_2-1_run.py
```

**채운 코드** (한 예)

```python
    access_list = []                                             # 현황을 담을 빈 목록
    for user, info in USERS.items():                             # 사용자를 한 명씩 꺼낸다
        access_list = access_list + role_entries(user, info)     # 그 사용자가 역할로 받은 권한 목록을 현황 뒤에 이어 붙인다
    for exception in EXCEPTIONS:                                 # 예외를 하나씩 꺼낸다
        user = exception["user"]                                 # 예외를 받은 사용자 이름을 꺼낸다
        entry = {"user": user, "permission": exception["permission"], "source": f"예외 {exception['id']}번", "employed": USERS[user]["employed"]}  # 현황의 권한 한 건을 만든다
        entry["expires"] = exception["expires"]                  # 예외에만 있는 만료 시각 키를 추가한다
        access_list.append(entry)                                # 현황에 추가한다
    return access_list                                           # 현황을 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 부여돼 있는 권한은 모두 **14건**입니다. 역할로 받은 권한이 9건, 예외로 받은 권한이 5건입니다. 사용자별 개수는 seoyeon · junho · gaeun · dami 가 3건씩, batch-night 가 2건이고, 사용자 파일에 있는 tester 는 권한이 하나도 없습니다. tester 의 역할 `intern` 이 역할 파일에 없어서 받은 권한이 없기 때문입니다.

```
--- 단계 1: 현황 - 부여돼 있는 권한 14 건
seoyeon SALES:QUERY <- 역할 sales | 재직 True
seoyeon SALES:CHANGE <- 역할 sales | 재직 True
junho SALES:QUERY <- 역할 finance | 재직 True
junho SETTLE:QUERY <- 역할 finance | 재직 True
gaeun ACCOUNT:QUERY <- 역할 account_admin | 재직 True
gaeun ACCOUNT:CHANGE <- 역할 account_admin | 재직 True
dami SALES:QUERY <- 역할 sales | 재직 False
dami SALES:CHANGE <- 역할 sales | 재직 False
batch-night SETTLE:QUERY <- 역할 batch | 재직 True
seoyeon SETTLE:QUERY <- 예외 1번 | 재직 True
junho SALES:CHANGE <- 예외 2번 | 재직 True
dami SALES:QUERY <- 예외 3번 | 재직 False
batch-night SALES:QUERY <- 예외 4번 | 재직 True
gaeun SETTLE:QUERY <- 예외 5번 | 재직 True
--- 단계 2: 점검 - 사용자별 권한 개수
{'seoyeon': 3, 'junho': 3, 'gaeun': 3, 'dami': 3, 'batch-night': 2}
```

- (나) 판정 함수(`check_permission` · `evaluate_access`)가 이미 거부하는 권한이 목록에 들어 있습니다. 예를 들어 퇴사한 dami 의 권한들(역할 2건 + 예외 3번)은 「퇴사한 계정」으로 거부되고, 만료 시각이 지난 예외(1 · 2 · 4 · 5번)는 판정에 쓰이지 않습니다. 그래도 목록에서 빼지 않는 이유는, 점검의 목적이 「지금 거부되는가」가 아니라 「부여 기록에 남아 있는 필요 없는 권한을 찾아 정리하는가」이기 때문입니다. 거부되는 권한을 빼 버리면 3교시에서 퇴사자나 만료된 예외를 찾을 수 없습니다. 또 판정 함수는 접근을 막을 뿐 기록을 지우지 않으므로, 기록이 남아 있는 한 재직 표시가 실수로 바뀌면 다시 접근할 수 있게 됩니다. 목록에 남겨야 정리 대상을 알 수 있습니다.

**왜** — 점검은 「누가 어떤 권한을 어떤 방법(역할 · 예외)으로 갖고 있나」를 먼저 한곳에 모아야 시작됩니다. 역할 파일 · 예외 파일 · 사용자 파일을 따로 보면 같은 사람의 권한이 나뉘어 있어 놓치기 쉽습니다. 출처(`source`)를 권한마다 적어 두면 나중에 「어느 방법으로 받은 권한을 거둘지」 정할 수 있습니다.

**자주 틀리는 곳** — `access_list = access_list + role_entries(user, info)` 에서 앞의 `access_list =` 를 빼먹는 경우가 많습니다. 이은 목록이 어디에도 담기지 않아 역할로 받은 권한이 모두 사라집니다. 오류는 나지 않고 예외로 받은 5건만 나옵니다. 실행하면 다음처럼 됩니다(`부여돼 있는 권한 5 건`이면 이 실수입니다).

```
--- 단계 1: 현황 - 부여돼 있는 권한 5 건
seoyeon SETTLE:QUERY <- 예외 1번 | 재직 True
junho SALES:CHANGE <- 예외 2번 | 재직 True
dami SALES:QUERY <- 예외 3번 | 재직 False
batch-night SALES:QUERY <- 예외 4번 | 재직 True
gaeun SETTLE:QUERY <- 예외 5번 | 재직 True
--- 단계 2: 점검 - 사용자별 권한 개수
{'seoyeon': 1, 'junho': 1, 'dami': 1, 'batch-night': 1, 'gaeun': 1}
```

예외 권한에 `entry["expires"]` 를 추가하는 줄을 빼먹으면 3교시에서 예외 만료를 판단할 수 없습니다. 이 오류는 2교시 출력에는 보이지 않고 3교시에서 나타납니다.

**관제에서는** — 현황표는 점검을 시작할 때 가장 먼저 뽑는 표입니다. 점검 때마다 같은 형식으로 뽑아 두면 지난 점검과 비교해 새로 생긴 권한 · 사라진 권한을 찾을 수 있습니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
python day04_3-1_run.py
```

**채운 코드** (한 예)

```python
    stale = []                                                   # 걸린 권한을 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        expires = entry.get("expires")                           # 만료 시각을 꺼낸다(역할로 받은 권한에는 이 키가 없어 None)
        reason = ""                                              # 이유를 빈 글자로 시작한다
        if not entry["employed"]:                                # 퇴사한 사용자의 권한이면
            reason = "퇴사한 계정"                                 # 이유를 적는다
        elif expires is not None and datetime.strptime(expires, TIME_FORMAT) <= now:   # 아니고, 예외인데 만료 시각이 지났으면
            reason = "만료된 예외"                                 # 이유를 적는다
        if reason != "":                                         # 이유가 적혔으면(규칙에 걸렸으면)
            stale_entry = entry.copy()                           # 권한을 복사해서
            stale_entry["reason"] = reason                       # 복사본에 이유를 적고
            stale.append(stale_entry)                            # 걸린 목록에 추가한다
    return stale                                                 # 걸린 목록을 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 규칙에 걸린 권한은 **7건**입니다. 퇴사한 계정이 3건(dami 의 역할 권한 2건과 예외 3번), 만료된 예외가 4건(1 · 2 · 4 · 5번)입니다. dami 의 예외 3번은 만료 시각(10/31(토))이 아직 안 지났지만 퇴사한 계정이라 퇴사로 걸렸습니다.

```
--- 단계 1: 판정 - 규칙에 걸린 권한 7 건 (전체 14 건 중)
dami SALES:QUERY <- 역할 sales | 퇴사한 계정
dami SALES:CHANGE <- 역할 sales | 퇴사한 계정
seoyeon SETTLE:QUERY <- 예외 1번 | 만료된 예외
junho SALES:CHANGE <- 예외 2번 | 만료된 예외
dami SALES:QUERY <- 예외 3번 | 퇴사한 계정
batch-night SALES:QUERY <- 예외 4번 | 만료된 예외
gaeun SETTLE:QUERY <- 예외 5번 | 만료된 예외
--- 단계 2: 점검 - 이유별 건수
{'퇴사한 계정': 3, '만료된 예외': 4}
```

- (나) 예를 들어 **재직 중이고 기한도 안 지났지만 실제로는 쓰지 않는 권한**입니다. 맡은 일이 바뀌었거나 프로젝트가 끝났는데 역할이 그대로인 사람의 권한이 그렇습니다. 이런 권한은 파일에 적힌 사실(퇴사 여부 · 만료 시각)만으로는 알 수 없고, 실제로 그 권한을 썼는지 보여 주는 정보(권한을 마지막으로 쓴 시각)가 있어야 찾을 수 있습니다. 부서 이동 기록을 비교하는 방법도 가능합니다.
- (다) 한 예: 먼저 회수할 것은 **퇴사한 계정 3건**(dami 의 역할로 받은 두 건과 예외 3번)입니다. 기준은 「그 권한을 쓸 사람이 이미 없는가」입니다. 퇴사한 사람의 권한은 업무에 쓰일 일이 없어 회수해도 업무가 멈추지 않습니다. 또 이 세 건은 이유가 퇴사 하나뿐이라, 사용자 파일의 재직 표시(`employed`)가 입력 실수나 인사 변경으로 `True` 로 바뀌면 다시 접근할 수 있게 되어 위험합니다. 반면 만료된 예외 4건은 기간이 이미 끝났고, 누가 `expires` 를 일부러 고치지 않는 한 다시 쓰일 일이 거의 없어 급하지 않습니다. 기준 하나를 정하고 그 기준으로 이유를 대면 맞습니다. 다른 기준(예: 쓰기 권한이 있는 것부터, 예외 전체를 먼저)도 이유가 맞으면 인정합니다.

**왜** — 사실만 보고 판단할 수 있는 점검은 코드가 사람보다 빠르고 빠짐이 없습니다. 이유(`reason`)를 함께 적어 두면 관제 담당이 걸린 이유를 바로 알고 처리할 수 있습니다. 권한 한 건이 두 규칙에 모두 걸릴 때 `elif` 로 하나만 적게 하지 않으면 같은 권한이 두 번 나오거나 이유가 뒤섞입니다.

**자주 틀리는 곳** — `entry.get("expires")` 대신 `entry["expires"]` 로 꺼내는 경우가 가장 많습니다. 역할로 받은 권한에는 `expires` 키가 없어 첫 줄에서 바로 멈춥니다. 실행하면 다음처럼 됩니다.

```
Traceback (most recent call last):
  File "…/파일이름.py", line 8, in <module>
    stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다
  File "…/파일이름.py", line 9, in find_stale
    expires = entry["expires"]                           # 만료 시각을 꺼낸다
KeyError: 'expires'
```

`if` 두 개를 따로 쓰면(`elif` 대신) 퇴사한 사람의 만료된 예외가 만료 이유로 덮어써질 수 있습니다. 걸린 권한을 복사하지 않고 `entry["reason"] = reason` 으로 원래 현황 권한을 바꾸면 다음 교시에 현황 목록을 다시 쓸 때 `reason` 키가 섞여 들어갑니다.

**관제에서는** — 규칙으로 걸리는 권한은 매주 자동으로 목록을 뽑아 담당자에게 보내고, 처리하지 않은 채 몇 주째 남아 있는 권한은 따로 표시합니다. 같은 계정이 반복해서 걸리면 퇴사 처리 절차(인사 시스템과 권한 시스템의 연동)에 빠진 곳이 있다는 뜻으로 봅니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
python day04_4-1_run.py
```

**채운 코드** (한 예)

```python
    unused = []                                                  # 후보를 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        key = f"{entry['user']}:{entry['permission']}"           # 그 권한의 「사용자:권한」 글자를 만든다
        used_text = last_used_map.get(key)                       # 마지막 사용 시각 글자를 꺼낸다(이력이 없으면 None)
        if used_text is None:                                    # 사용 이력이 없으면
            unused.append(make_unused(entry, None))              # 마지막 사용 시각을 None 으로 적은 복사본을 후보에 추가한다
        elif days_since(used_text, now) > limit_days:            # 사용 이력이 있고 기준 일 수보다 오래 안 썼으면
            unused.append(make_unused(entry, used_text))         # 마지막 사용 시각을 적은 복사본을 후보에 추가한다
    return unused                                                # 후보 목록을 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 90일 넘게 안 쓴 후보는 **3건**입니다. seoyeon 의 `SALES:CHANGE`(120일째 안 씀), junho 의 `SALES:QUERY`(91일째 안 씀), gaeun 의 `ACCOUNT:CHANGE`(사용 이력 없음)입니다.

```
--- 단계 1: 현황 - 규칙에 안 걸린 권한 7 건의 안 쓴 일 수
seoyeon SALES:QUERY -> 2 일째 안 씀
seoyeon SALES:CHANGE -> 120 일째 안 씀
junho SALES:QUERY -> 91 일째 안 씀
junho SETTLE:QUERY -> 90 일째 안 씀
gaeun ACCOUNT:QUERY -> 9 일째 안 씀
gaeun ACCOUNT:CHANGE -> 사용 이력 없음
batch-night SETTLE:QUERY -> 0 일째 안 씀
--- 단계 2: 판정 - 90일 넘게 안 쓴 후보 3 건
seoyeon SALES:CHANGE <- 역할 sales
junho SALES:QUERY <- 역할 finance
gaeun ACCOUNT:CHANGE <- 역할 account_admin
```

- (나) 하루 차이로 나누는 것은 단순하지만, 그 하루 차이가 실제 필요 여부를 뜻하지는 않습니다. 90일은 「대부분의 정기 업무(분기 정산 등)는 그 안에 한 번은 쓴다」는 약속일 뿐이고, 같은 junho 의 `SETTLE:QUERY`(90일째)와 `SALES:QUERY`(91일째)는 사실상 같은 상태입니다. 기준이 필요한 이유는 점검 결과를 사람마다 다르게 해석하지 않고 같은 잣대로 반복해서 뽑기 위해서입니다. 경계 부근(예: 85~95일)의 권한은 후보가 되기 직전이거나 막 후보가 된 것이므로, 담당자가 다음을 추가로 확인합니다. ① 그 권한이 분기 · 반기 · 연 단위 업무에 쓰이는가 ② 사용 이력이 누락된 로그는 없는가 ③ 최근 업무 변경이 있었는가.
- (다) 사용 이력이 없다고 바로 지우면 안 되는 경우는 **평소엔 안 쓰지만 꼭 필요한 순간이 있는 권한**입니다. 예: 장애나 보안 사고 때만 쓰는 비상 권한, 분기 · 연말 결산 때만 쓰는 권한, 아직 한 번도 안 썼지만 곧 시작할 업무를 위해 미리 받은 권한입니다. gaeun 의 `ACCOUNT:CHANGE`(계정 변경)도 계정 관리 담당이 평소엔 조회만 하다가 사고 때 변경해야 한다면 필요한 권한입니다. 그래서 「후보」로만 뽑고, 담당자가 사용 목적을 확인한 뒤에 회수를 결정합니다.

**왜** — 규칙으로 못 찾는 필요 없는 권한은 사용 이력과 비교해야 찾을 수 있습니다. 기준 일 수(`limit_days`)를 함수의 인자로 받으면 90일을 60일이나 180일로 바꿀 때 함수를 고치지 않아도 됩니다. 사용 이력이 없는 권한도 후보에 넣는 것은, 이력에 한 번도 나오지 않았다면 쓰이지 않았을 가능성이 크기 때문입니다.

**자주 틀리는 곳** — 비교를 `days_since(used_text, now) > limit_days` 대신 `>=` 로 쓰는 경계 실수가 가장 흔합니다. 90일째 쓴 junho 의 `SETTLE:QUERY` 가 후보에 잘못 들어갑니다. 실행하면 다음처럼 됩니다(후보가 4건이 되면 이 실수입니다. 줄 번호는 내 파일과 다를 수 있습니다).

```
--- 단계 1: 현황 - 규칙에 안 걸린 권한 7 건의 안 쓴 일 수
seoyeon SALES:QUERY -> 2 일째 안 씀
seoyeon SALES:CHANGE -> 120 일째 안 씀
junho SALES:QUERY -> 91 일째 안 씀
junho SETTLE:QUERY -> 90 일째 안 씀
gaeun ACCOUNT:QUERY -> 9 일째 안 씀
gaeun ACCOUNT:CHANGE -> 사용 이력 없음
batch-night SETTLE:QUERY -> 0 일째 안 씀
--- 단계 2: 판정 - 90일 넘게 안 쓴 후보 4 건
seoyeon SALES:CHANGE <- 역할 sales
junho SALES:QUERY <- 역할 finance
junho SETTLE:QUERY <- 역할 finance
gaeun ACCOUNT:CHANGE <- 역할 account_admin
```

`elif` 대신 `if` 로 쓰면, 사용 이력이 없는 gaeun 의 `ACCOUNT:CHANGE` 도 `days_since` 에 들어가 `TypeError: strptime() argument 1 must be str, not None` 으로 멈춥니다. 이력이 없으면 일 수를 계산할 수 없으므로 이력이 있을 때(`elif`)만 계산해야 합니다.

**관제에서는** — 미사용 후보는 곧바로 회수하지 않고, 권한 소유자와 그 상급자에게 「계속 필요한가」를 확인하는 요청을 보냅니다. 응답이 없으면 한 단계 낮은 권한으로 줄였다가 문제가 없으면 회수합니다. 확인 요청과 응답은 점검 이력으로 남깁니다.

---

### 앞 교시 파일 완성본

앞 교시 파일을 못 만들고 다음 교시로 넘어가야 할 때 그대로 만들어 씁니다. 정답 본문을 함수 머리말과 합친 전체 파일입니다.

**`review_list.py`** (2교시 완성본)

```python
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def role_entries(user, info):                                    # 사용자 이름과 그 사용자의 정보 딕셔너리를 받는 함수
    """사용자 한 명이 역할로 받은 권한을 현황의 권한 한 건씩 만들어 목록으로 리턴한다."""
    role = info["role"]                                          # 그 사용자의 역할을 꺼낸다
    entries = []                                                 # 역할로 받은 권한을 담을 빈 목록
    for permission in ROLES.get(role, []):                       # 역할의 권한을 하나씩 꺼낸다(역할 파일에 없는 역할이면 빈 목록)
        entry = {"user": user, "permission": permission, "source": f"역할 {role}", "employed": info["employed"]}  # 현황의 권한 한 건을 만든다
        entries.append(entry)                                    # 목록에 추가한다
    return entries                                               # 역할로 받은 권한 목록을 리턴한다


def build_access_list():                                         # 지금 부여돼 있는 권한을 모두 모아 목록으로 만드는 함수
    """부여돼 있는 권한을 모아 리턴한다. 목록의 한 건 = 사용자 한 명의 권한 하나(역할로 받았거나 예외로 받은 것)."""
    access_list = []                                             # 현황을 담을 빈 목록
    for user, info in USERS.items():                             # 사용자를 한 명씩 꺼낸다
        access_list = access_list + role_entries(user, info)     # 그 사용자가 역할로 받은 권한 목록을 현황 뒤에 이어 붙인다
    for exception in EXCEPTIONS:                                 # 예외를 하나씩 꺼낸다
        user = exception["user"]                                 # 예외를 받은 사용자 이름을 꺼낸다
        entry = {"user": user, "permission": exception["permission"], "source": f"예외 {exception['id']}번", "employed": USERS[user]["employed"]}  # 현황의 권한 한 건을 만든다
        entry["expires"] = exception["expires"]                  # 예외에만 있는 만료 시각 키를 추가한다
        access_list.append(entry)                                # 현황에 추가한다
    return access_list                                           # 현황을 리턴한다
```

**`review_rules.py`** (3교시 완성본)

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def find_stale(access_list, now):                                # 현황 목록과 지금 시각(datetime)을 받는 함수
    """규칙에 걸려 필요 없어진 권한을 리턴한다. 걸린 권한마다 "reason" 키에 이유를 적는다."""
    stale = []                                                   # 걸린 권한을 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        expires = entry.get("expires")                           # 만료 시각을 꺼낸다(역할로 받은 권한에는 이 키가 없어 None)
        reason = ""                                              # 이유를 빈 글자로 시작한다
        if not entry["employed"]:                                # 퇴사한 사용자의 권한이면
            reason = "퇴사한 계정"                                 # 이유를 적는다
        elif expires is not None and datetime.strptime(expires, TIME_FORMAT) <= now:   # 아니고, 예외인데 만료 시각이 지났으면
            reason = "만료된 예외"                                 # 이유를 적는다
        if reason != "":                                         # 이유가 적혔으면(규칙에 걸렸으면)
            stale_entry = entry.copy()                           # 권한을 복사해서
            stale_entry["reason"] = reason                       # 복사본에 이유를 적고
            stale.append(stale_entry)                            # 걸린 목록에 추가한다
    return stale                                                 # 걸린 목록을 리턴한다
```

**`review_unused.py`** (4교시 완성본)

```python
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def load_last_used():                                            # 사용 이력 파일을 읽어 「마지막 사용 시각」 딕셔너리를 만드는 함수
    """「사용자:권한」 글자를 키로, 마지막으로 쓴 시각 글자를 값으로 하는 딕셔너리를 리턴한다."""
    last_used_map = {}                                           # 빈 딕셔너리로 시작한다
    for log in load_json("config/access_log.json", []):          # 사용 이력을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        key = f"{log['user']}:{log['permission']}"               # 「사용자:권한」 글자를 키로 만든다
        last_used_map[key] = log["last_used"]                    # 그 키의 값에 마지막 사용 시각 글자를 담는다
    return last_used_map                                         # 딕셔너리를 리턴한다


def make_unused(entry, used_text):                               # 현황의 권한 한 건과 마지막 사용 시각 글자를 받는 함수
    """권한 한 건을 복사해 "last_used" 키(마지막 사용 시각, 이력이 없으면 None)를 적어 리턴한다. 원래 권한은 바꾸지 않는다."""
    unused_entry = entry.copy()                                  # 원래 권한은 바꾸지 않고 복사한다
    unused_entry["last_used"] = used_text                        # 복사본에 마지막 사용 시각(없으면 None)을 적는다
    return unused_entry                                          # 복사본을 리턴한다


def days_since(used_text, now):                                  # 마지막 사용 시각 글자와 지금 시각을 받는 함수
    """마지막 사용 시각 글자를 시각으로 바꿔, 지금까지 안 쓴 일 수를 리턴한다."""
    used_at = datetime.strptime(used_text, TIME_FORMAT)          # 글자를 시각으로 바꾼다
    return (now - used_at).days                                  # 지금 - 마지막 사용 시각의 일 수를 리턴한다


def find_unused(access_list, last_used_map, now, limit_days):    # 현황 · 마지막 사용 시각 딕셔너리 · 지금 시각 · 기준 일 수를 받는 함수
    """마지막 사용이 limit_days 일보다 오래됐거나 사용 이력이 없는 권한을 리턴한다. 후보마다 "last_used" 키에 마지막 사용 시각(없으면 None)을 적는다."""
    unused = []                                                  # 후보를 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        key = f"{entry['user']}:{entry['permission']}"           # 그 권한의 「사용자:권한」 글자를 만든다
        used_text = last_used_map.get(key)                       # 마지막 사용 시각 글자를 꺼낸다(이력이 없으면 None)
        if used_text is None:                                    # 사용 이력이 없으면
            unused.append(make_unused(entry, None))              # 마지막 사용 시각을 None 으로 적은 복사본을 후보에 추가한다
        elif days_since(used_text, now) > limit_days:            # 사용 이력이 있고 기준 일 수보다 오래 안 썼으면
            unused.append(make_unused(entry, used_text))         # 마지막 사용 시각을 적은 복사본을 후보에 추가한다
    return unused                                                # 후보 목록을 리턴한다
```

**`config/access_log.json`** (4교시 사용 이력)

```json
[
  {"user": "seoyeon", "permission": "SALES:QUERY", "last_used": "2026-10-27 09:10"},
  {"user": "seoyeon", "permission": "SALES:CHANGE", "last_used": "2026-06-30 14:00"},
  {"user": "junho", "permission": "SALES:QUERY", "last_used": "2026-07-30 09:00"},
  {"user": "junho", "permission": "SETTLE:QUERY", "last_used": "2026-07-31 10:00"},
  {"user": "gaeun", "permission": "ACCOUNT:QUERY", "last_used": "2026-10-20 08:00"},
  {"user": "batch-night", "permission": "SETTLE:QUERY", "last_used": "2026-10-29 02:00"},
  {"user": "dami", "permission": "SALES:QUERY", "last_used": "2026-10-10 13:00"}
]
```
