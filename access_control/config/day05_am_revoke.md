# 10/30(금) 오전 · 3과목 접근통제 ⑤ — 권한 회수 계획 · 승인 · 실행 · 이력 — 실습

어제 10/29(목)에는 부여돼 있는 권한을 점검해서 **회수 대상 8건**을 찾았습니다. 오늘 오전에는 그 8건을 실제로 **회수**(권한을 없애는 일)합니다. 단, 바로 지우지 않고 계획 → 승인 → 실행 순서로 합니다.

- **2교시**: 회수 대상마다 어떤 방법으로 회수할지, 몇 건의 권한이 사라지는지 **회수 계획**을 세운다(아직 지우지 않는다).
- **3교시**: 쓰기 권한 같은 **민감한 권한**은 보안 책임자의 승인이 필요합니다. 승인이 필요한 계획을 가려 **승인 상태**를 적는다.
- **4교시**: 승인 대기가 아닌 계획만 **실행**하고, 회수 전후의 판정을 비교하고, **회수 이력**을 파일로 남긴다.

오늘은 오전 2 · 3 · 4교시, 오후 5 · 6교시이고, 깃허브에 올리는 일은 6교시 마지막에 합니다. 교시마다 문제는 하나입니다. 오늘 회수는 파일 자체를 고치지 않고, 프로그램이 파일에서 읽어 둔 **메모리 안의 데이터**(`USERS` · `ROLES` · `EXCEPTIONS`)를 바꿉니다. 프로그램을 끄면 처음 상태로 돌아가고, 파일로 저장하는 것은 회수 이력뿐입니다.

**📎 오늘 불러 쓰는 이전 파일** — 오늘 코드가 `import` 로 가져다 쓰는 앞 수업 파일입니다. 없으면 오른쪽 열의 방법으로 먼저 준비합니다.

| 파일 | 만든 날 | 오늘 가져다 쓰는 것 | 쓰는 교시 | 없으면 |
|---|---|---|---|---|
| `rbac.py` | 10/21(수) | `USERS` · `ROLES` (`config/users.json` · `config/roles.json`) | 2 · 3 · 4교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |
| `exception_policy.py` | 10/22(목) | `EXCEPTIONS` · `TIME_FORMAT` (`config/exceptions.json`) | 4교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |
| `policy.py` | 10/22(목) | `evaluate_access` | 4교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |
| `config_loader.py` | 10/22(목) | `load_json` | 3 · 4교시 | `day02_recovery` 폴더(10/21(수) · 10/22(목) 파일의 완성본) |
| `review_list.py` · `review_rules.py` · `review_unused.py` · `config/access_log.json` | 10/29(목) 오전 | `build_access_list` · `find_stale` · `find_unused` | 2 · 4교시 | 10/29(목) 오전 문서 맨 아래 「앞 교시 파일 완성본」 |
| `overprivilege.py` · `report_exclude.py` · `config/exclude_list.json` | 10/29(목) 오후 | `generate_report` · `split_by_exclude` | 2 · 4교시 | 10/29(목) 오후 문서 맨 아래 「앞 교시 파일 완성본」 |

- 오늘 만드는 파일도 뒤 교시가 가져다 씁니다. 2교시 `revoke_plan.py` 는 3 · 4교시에서, 3교시 `revoke_approve.py` 는 4교시에서 씁니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 어제까지의 파일을 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python -c "from rbac import USERS, ROLES; from policy import evaluate_access; from config_loader import load_json; from exception_policy import EXCEPTIONS, TIME_FORMAT; from review_list import build_access_list; from review_rules import find_stale; from review_unused import load_last_used; from overprivilege import generate_report; from report_exclude import load_exclude_map; print('이전 파일 정상', len(build_access_list()), len(load_last_used()), len(load_exclude_map('config/exclude_list.json')))"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다.
   - 10/29(목)에 만든 `review_list.py` · `review_rules.py` · `review_unused.py` · `overprivilege.py` · `report_exclude.py` 가 보이고, `config` 안에 `access_log.json` · `exclude_list.json` 이 보여야 합니다.
   - 마지막 줄에 `이전 파일 정상 14 7 3` 이 나와야 합니다. 뒤의 숫자는 현황 14건, 사용 이력 7건, 회수 제외 리스트 3건입니다. 숫자가 다르면 오늘 출력도 달라집니다.
   - 아니면 10/29(목) 오전 문서(`day04_am_access_review.md`)와 오후 문서(`day04_pm_overprivilege.md`) 맨 아래 「앞 교시 파일 완성본」으로 없는 파일을 만듭니다.
     - 10/21(수) · 10/22(목) 파일이 없으면 수업 자료로 받은 `day02_recovery` 폴더 안의 파일을 `access_control` 폴더에 넣고(`config` 안의 파일은 `config` 폴더에 넣습니다) 마지막 줄을 다시 칩니다.
3. **오늘 받은 파일 두 개를 `access_control` 폴더로 옮깁니다.** 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day05_am_revoke.md` (이 파일) — 오전 실습 안내. 읽기만 합니다.
   - `day05_am_report.md` — **오전 보고서.** 2 · 3 · 4교시 답을 여기에 적습니다.
4. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day05_am_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-30(금))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이며, 이유까지 적어야 합니다.
     - 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다.
     - 🔍 가 없는 질문도 못 적으면 같은 말을 씁니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 문자열(string)은 따옴표로 감싼 글입니다. `""` 는 문자가 하나도 없는 빈 문자열입니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일이 `config/…` 를 지금 위치 기준으로 찾기 때문입니다. `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **어제까지의 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 회수 대상의 회수 계획 세우기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「어제 점검 결과에서 회수할 권한이 8건 나왔습니다. 그런데 바로 지워도 되는지 걱정됩니다. 예외로 받은 권한은 그 예외만 지우면 되지만, 역할로 받은 권한은 같은 역할을 가진 다른 사람에게도 영향이 갈 수 있기 때문입니다.
>
> 지우기 전에 8건을 어떤 방법으로 회수할지, 그 회수로 몇 건의 권한이 사라지는지를 먼저 리스트로 보여 주세요.」
> - **왜 중요한가**: 권한을 잘못 지우면 일하던 사람이 갑자기 접근하지 못합니다. 지우기 전에 방법과 영향을 먼저 확인하면 실수를 줄일 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 앞 수업 흐름 복습

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 날짜 | 한 일 | 오늘 이어지는 것 |
|---|---|---|
| 10/29(목) | 현황 리스트 → 규칙(퇴사 · 만료)과 사용 이력(권한을 마지막으로 쓴 시각의 기록. 90일)으로 후보 찾기 → 후보 10건에서 회수 제외 2건을 뺌 | 회수 대상 8건(`load_to_revoke` 가 리턴하는 리스트, 코드에서는 `findings`). 회수 제외 리스트의 3건 중 dami 의 권한은 「퇴사한 계정」이라 제외하지 않아, 실제 제외는 gaeun 의 `ACCOUNT:CHANGE` · seoyeon 의 `SALES:CHANGE` 2건입니다. |
| 10/22(목) | 역할 부여 · 퇴사 처리(`revoke_access`), 예외 만료, 최종 판정 `evaluate_access` | 오늘 4교시의 회수 확인에 다시 씀 |

### 📖 왜 회수 계획이 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 점검에서 찾은 8건은 「회수해야 할 권한」입니다. 하지만 권한을 받은 방식에 따라 회수 방법이 다르고, 방법에 따라 영향받는 사람이 다릅니다.
2. 권한을 받은 방식에 따라 지우는 대상이 다릅니다.
   - **예외로 받은 권한**은 그 예외 한 건만 지우면 됩니다.
   - **역할로 받은 권한**은 사용자의 역할을 해제하거나, 역할 자체에서 그 권한을 빼야 합니다.
     - 역할에서 권한을 빼면 그 역할을 가진 **모든 사용자**가 권한을 잃습니다.
3. 그래서 지우기 전에 방법과 영향을 정리한 **회수 계획**을 먼저 만듭니다. 계획은 실제로는 아무것도 지우지 않는 미리보기(dry-run · 드라이 런)입니다.

### 📖 2.1 회수 방법과 영향 범위

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- **회수 방법**은 권한을 없애려고 **어느 데이터를 고칠지**입니다.
  - 권한은 두 길로 받습니다. 예외(`EXCEPTIONS`)로 받거나, 사용자의 역할(`USERS` 의 `role` 이 가리키는 `ROLES`)로 받습니다.
  - 그래서 방법은 **예외 삭제 · 역할 해제 · 역할에서 권한 빼기** 세 가지입니다.
- **영향**(impact · 임팩트)은 이 회수로 사용자들이 잃는 권한을 하나씩 센 수입니다(예: dami 가 권한 2개를 잃으면 2).
- **오늘 쓰는 데이터의 모양**
  - `USERS`: `{"seoyeon": {"role": "sales", "employed": True}, "junho": {"role": "finance", "employed": True}, "dami": {"role": "sales", "employed": False}, …}`
  - `ROLES`: `{"sales": ["SALES:QUERY", "SALES:CHANGE"], "finance": ["SALES:QUERY", "SETTLE:QUERY"], …}` (역할 이름 → 권한 리스트)
  - `EXCEPTIONS`: 예외 한 건은 `{"id": 3, "user": "dami", "permission": "SALES:QUERY", …}` 모양입니다.
  - `findings`: 회수 대상 8건의 리스트이고, `finding` 은 그 한 건입니다.
    - `finding` 한 건에는 `user` · `permission` · `source`(권한을 받은 경로: 「예외 3번」 또는 「역할 sales」) · `reasons`(어제 점검에서 나온 이유의 리스트)가 들어 있습니다.
    - 회수 대상은 (사용자, 권한, 받은 경로)마다 한 건이라, 같은 방법의 계획이 여러 건 나올 수 있습니다(dami 의 역할 해제 2건).

**방법 ① 예외 삭제 — 예외로 받은 권한**

- **상황**: dami 가 예외 3번으로 `SALES:QUERY` 를 받았습니다.
- **하는 일**: `EXCEPTIONS` 리스트에서 번호가 3인 예외를 지웁니다.
- **사라지는 것**: 예외로 받은 그 권한 1개라서 **영향 1**입니다. dami 는 같은 권한을 `sales` 역할로도 받지만, 그쪽은 방법 ②에서 따로 회수합니다.
- **지울 대상**(`target`): 예외 번호 3
- **왜 이 방법인가**: 예외 한 건에만 들어 있는 권한이라 그 예외만 지우면 됩니다.

**방법 ② 역할 해제 — 퇴사한 사용자가 역할로 받은 권한**

- **상황**: dami 는 퇴사했고, 역할 `sales` 로 `SALES:QUERY` · `SALES:CHANGE` 를 받았습니다.
- **하는 일**: `USERS` 에서 dami 의 `role` 을 빈 문자열(`""`)로 바꿉니다. dami 는 어떤 역할의 권한도 받지 않게 됩니다.
- **사라지는 것**: dami 가 `sales` 로 받던 권한 2개가 모두 사라져서 **영향 2**입니다.
- **지울 대상**(`target`): 사용자 이름 dami
- **왜 이 방법인가**: 퇴사한 사람은 어떤 권한도 필요 없어서 역할째로 끊습니다. `sales` 역할에서 권한을 빼면 재직 중인 seoyeon 도 그 권한을 잃으므로, 역할이 아니라 dami 의 `role` 만 비웁니다.

**방법 ③ 역할에서 권한 빼기 — 재직 중인 사용자가 역할로 받은 권한**

- **상황**: 재직 중인 junho 가 역할 `finance` 로 `SALES:QUERY` 를 받았습니다.
- **하는 일**: `ROLES` 의 `finance` 권한 리스트에서 `SALES:QUERY` 를 뺍니다.
- **사라지는 것**: `finance` 역할을 가진 사용자 모두가 그 권한을 잃습니다. 오늘은 junho 1명이라 **영향 1**입니다.
- **지울 대상**(`target`): 역할 이름 finance
- **왜 이 방법인가**: junho 의 `role` 을 비우면 `finance` 의 다른 권한(`SETTLE:QUERY`)까지 모두 사라지므로, 그 권한만 뺍니다.

- **참고**: 10/22(목)의 `revoke_access` 는 `employed` 만 `False` 로 바꾸고 `role` 은 그대로 두었습니다. 오늘의 역할 해제는 `role` 을 비웁니다.

**어떤 방법을 고르나**

- 아래 「`plan_revocation` 의 흐름」 그림의 두 갈림길로 정합니다.
  - 예외로 받았나? 그렇다 → ① 예외 삭제
  - 아니고, 퇴사한 사용자인가? 그렇다 → ② 역할 해제
  - 그 밖(재직 중인 사용자의 역할 권한) → ③ 역할에서 권한 빼기

**한 장 정리**

| 받은 방식 | 쓰는 방법 | 지울 대상(`target`) | 사라지는 권한 수(`impact`) |
|---|---|---|---|
| 예외로 받음(`source` 가 「예외 N번」) | 예외 삭제 | 예외 번호 N | 1건 |
| 역할로 받음 + 퇴사한 사용자(`employed` 가 `False`) | 역할 해제 | 그 사용자의 이름 | 그 역할에 든 권한 수(dami 의 `sales` 는 2건) |
| 역할로 받음 + 재직 중인 사용자 | 역할에서 권한 빼기 | 역할 이름 | 그 역할을 가진 사용자 수(사용자마다 그 권한 1건) |

- **계획**(`plan`) 한 건: 회수 대상 한 건에 `method`(회수 방법) · `target`(지울 대상) · `impact`(영향) 키를 추가한 딕셔너리입니다.

**`plan_revocation` 의 흐름**

```
+-----------------------------------------+
| plan_revocation(findings, users, roles) |
+-----------------------------------------+
   |
   v
+-------------------------------------+
| plans = []  (계획을 담을 빈 리스트) |
+-------------------------------------+
   |
   v
+---------------------------------------------------------------------+
| role_counts = 역할별 사용자 수 딕셔너리  (반복 전에 한 번만 만든다) |
+---------------------------------------------------------------------+
   |
   v
+---------------------------------------------------------+
| 회수 대상을 하나씩 꺼내 그 사용자의 정보(info)를 꺼낸다 |
+---------------------------------------------------------+
   |
   v
+----------------------------+
| source 에 「예외」가 있나? |
+----------------------------+
   |
   +--> 있다 --> method = 「예외 삭제」 --> 아래 「build_plan」으로
   |
   v  없다
+----------------------------------------------+
| info["employed"] 가 거짓(퇴사한 사용자)인가? |
+----------------------------------------------+
   |
   +--> 그렇다 --> method = 「역할 해제」 --> 아래 「build_plan」으로
   |
   v  아니다   method = 「역할에서 권한 빼기」
+-----------------------------------------------------------------------------------------------------------------------+
| build_plan(finding, method, …) 으로 지울 대상(target)과 영향(impact)을 정한 계획 한 건을 만든다 (영향 계산은 직접 씀) |
+-----------------------------------------------------------------------------------------------------------------------+
   |
   v
+----------------------------------------------------+
| 계획을 plans 에 추가하고 다음 회수 대상으로 (반복) |
+----------------------------------------------------+
   |
   v  모든 회수 대상을 꺼낸 뒤
plans 를 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 회수 대상 8건의 회수 방법과 영향 범위 정하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 어제 찾은 회수 대상 8건이 리스트로만 있습니다. 각각 어떤 방법으로 지워야 하는지, 지우면 누가 영향을 받는지는 담당자가 파일을 열어 따져야 합니다.
- **그래서 만드는 것**: `plan_revocation` 입니다.
  - 회수 대상을 하나씩 보고 회수 방법을 정합니다.
  - 예외로 받은 것은 「예외 삭제」, 퇴사한 사용자의 역할 권한은 「역할 해제」, 재직 중인 사용자의 역할 권한은 「역할에서 권한 빼기」입니다.
  - 지울 대상과 영향(사라지는 권한 건수)은 `build_plan` 이 계획에 적습니다.
- **실행하면**: 단계 1은 8건의 회수 방법과 영향을 출력하고, 단계 2는 방법별 건수, 단계 3은 `finance` · `sales` 역할의 사용자 수와 이름을 출력합니다.
- **현업에서는**: 권한 회수 도구도 실제로 지우기 전에 「무엇을 어떻게 지울지」 계획을 먼저 보여 줍니다.

**🎯 할 일**

1. `revoke_input.py` · `revoke_plan.py` · `day05_2-1_run.py` 세 파일을 만들고, `exception_id` · `count_users_by_role` · `build_plan` · `plan_revocation` 에서 직접 쓰는 곳 다섯 군데를 씁니다.
2. 실행해서 <mark>회수 방법과 영향</mark>(단계 1: 계획), <mark>방법별 건수</mark>(단계 2: 집계), <mark>역할별 사용자 수와 이름</mark>(단계 3: 확인)를 읽습니다.

**`revoke_input.py`** — 그대로 붙여 넣습니다. 어제 점검 결과(회수 대상 8건)를 다시 만드는 도우미입니다. 학생이 쓰는 줄은 없습니다.

```python
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from review_list import build_access_list                        # 10/29(목) 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 10/29(목) 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 10/29(목) 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report                        # 10/29(목) 5교시에 만든 리포트 함수를 불러온다
from report_exclude import load_exclude_map, split_by_exclude    # 10/29(목) 6교시에 만든 회수 제외 함수를 불러온다

REVIEW_TIME = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")   # 어제 점검한 시각(고정). 같은 결과를 얻으려고 어제 시각을 쓴다
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 문자열의 형식


def load_to_revoke():                                            # 어제 점검 결과를 다시 만드는 함수
    """어제(10/29(목)) 5 · 6교시와 같은 방법으로 점검해서 「회수 대상」 리스트(8건)를 리턴한다."""
    access_list = build_access_list()                            # 현황을 만든다
    stale = find_stale(access_list, REVIEW_TIME)                 # 규칙에 걸린 권한을 찾는다
    last_used_map = load_last_used()                             # 마지막 사용 시각 딕셔너리를 읽는다
    unused = find_unused(access_list, last_used_map, REVIEW_TIME, 90)  # 90일 넘게 안 쓴 권한을 찾는다
    generated_at = REVIEW_TIME.strftime(TIME_FORMAT)             # 리포트를 만든 시각을 문자열로 바꾼다
    report = generate_report(access_list, stale, unused, 90, generated_at)  # 후보 리포트를 만든다
    exclude_map = load_exclude_map("config/exclude_list.json")   # 회수 제외 리스트를 읽는다
    to_revoke, excluded = split_by_exclude(report["findings"], exclude_map)   # 후보를 회수 대상과 회수 제외로 나눈다
    return to_revoke                                             # 회수 대상 리스트만 리턴한다
```

**`revoke_plan.py`**

```python
def exception_id(source):                                        # "예외 3번" 모양 문자열을 받는 함수
    """"예외 3번" 모양 문자열에서 예외 번호(3)를 꺼내 숫자로 리턴한다."""
    number_text = source.replace("예외 ", "")                      # "예외 3번" 에서 "예외 " 를 지워 "3번" 으로 만든다 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. number_text 에서 "번" 을 지운 문자열을 number_text 에 다시 담는다 (.replace("번", ""))
    # 2. number_text 를 숫자로 바꿔 리턴한다 (int)


def count_users_by_role(users):                                  # 사용자 딕셔너리를 받는 함수
    """역할마다 사용자가 몇 명인지 센 딕셔너리를 리턴한다(재직 여부와 상관없이 센다). 예: {"finance": 1, "sales": 2}"""
    counts = {}                                                  # 역할 → 사용자 수를 담을 빈 딕셔너리
    for info in users.values():                                  # 사용자 정보를 하나씩 꺼낸다(.values() 는 딕셔너리의 값만 꺼낸다)
        role = info["role"]                                      # 그 사용자의 역할
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. counts.get(role, 0) 을 old_count 에 담는다 (처음이면 0)
        # 4. counts[role] 를 old_count + 1 로 정한다
    return counts                                                # 역할별 사용자 수를 리턴한다


def make_plan(finding, method, target, impact):                  # 회수 대상 · 방법 · 대상 · 영향 범위를 받는 함수
    """회수 대상을 복사해 method · target · impact 키를 추가한 계획 한 건을 리턴한다. impact 는 이 회수로 사라지는 (사용자, 권한)의 수다."""
    plan = finding.copy()                                        # 원래 권한은 바꾸지 않고 복사한다
    plan["method"] = method                                      # 회수 방법을 적는다
    plan["target"] = target                                      # 실제로 지울 대상(예외 번호 · 사용자 · 역할)을 적는다
    plan["impact"] = impact                                      # 사라지는 (사용자, 권한)의 수를 적는다
    return plan                                                  # 계획 한 건을 리턴한다


def build_plan(finding, method, users, roles, role_counts):      # 회수 대상 한 건 · 회수 방법 · 사용자 · 역할 · 역할별 사용자 수를 받는 함수
    """회수 방법에 맞게 지울 대상(target)과 영향(impact)을 정해 계획 한 건을 리턴한다."""
    info = users[finding["user"]]                                # 그 사용자의 정보를 꺼낸다
    if method == "예외 삭제":                                    # 방법이 예외 삭제이면
        target = exception_id(finding["source"])                 # 지울 대상은 예외 번호
        return make_plan(finding, method, target, 1)             # 영향은 권한 1건
    if method == "역할 해제":                                    # 방법이 역할 해제이면
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. roles[info["role"]] 를 role_permissions 에 담는다 (그 사용자의 역할에 든 권한 리스트)
        # 6. len(role_permissions) 를 impact 에 담는다 (영향은 그 역할에 든 권한 수)
        return make_plan(finding, method, finding["user"], impact)  # 지울 대상은 그 사용자의 이름 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. role_counts[info["role"]] 를 impact 에 담는다 (역할에서 권한 빼기: 영향은 그 역할을 가진 사용자 수)
    return make_plan(finding, method, info["role"], impact)      # 지울 대상은 역할 이름 (미리 채움)


def plan_revocation(findings, users, roles):                     # 회수 대상 리스트 · 사용자 딕셔너리 · 역할 딕셔너리를 받는 함수
    """회수 대상마다 회수 방법을 정해 계획 리스트를 리턴한다. 실제로는 아무것도 지우지 않는다."""
    role_counts = count_users_by_role(users)                     # 역할마다 사용자가 몇 명인지 센다(반복 전에 한 번만)
    plans = []                                                   # 계획을 담을 빈 리스트
    for finding in findings:                                     # 회수 대상을 하나씩 꺼낸다
        info = users[finding["user"]]                            # 그 사용자의 정보를 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 8. finding["source"] 안에 "예외" 가 있으면 (in)
        # 9.   method 를 "예외 삭제" 로 정한다
        # 10. 그렇지 않고 info["employed"] 가 거짓이면 (elif not)
        # 11.  method 를 "역할 해제" 로 정한다
        # 12. 그렇지 않으면 (else)
        # 13.  method 를 "역할에서 권한 빼기" 로 정한다
        plan = build_plan(finding, method, users, roles, role_counts)  # 계획 한 건을 만든다
        plans.append(plan)                                       # 방법에 맞는 계획을 만들어 계획 리스트에 추가한다
    return plans                                                 # 계획 리스트를 리턴한다
```

- **직접 쓰는 곳은 네 함수의 다섯 군데**입니다. 판단이 필요한 함수마다 1 ~ 6줄만 쓰고, 나머지는 미리 채웠습니다.
  - `exception_id`(1 · 2번): 「번」을 지우고 숫자로 바꿉니다.
  - `count_users_by_role`(3 · 4번): 역할마다 사용자 수를 1 늘려 적습니다.
  - `build_plan`(5 · 6번, 7번): 역할 해제와 역할에서 권한 빼기의 영향을 정합니다.
  - `plan_revocation`(8 ~ 13번): 회수 대상마다 **어떤 방법으로 회수할지**(`method`)를 정합니다.
- 들여쓰기는 미리 채운 줄에 맞춥니다.
  - `exception_id` · `count_users_by_role`: 함수 안이라 `for` 밖은 4개, `for` 안쪽은 8개입니다.
  - `build_plan`: `if method == "역할 해제":` 안쪽(5 · 6번)은 8개이고, 7번은 `if` 밖이라 4개입니다.
  - `plan_revocation`: 미리 채운 `for` 안쪽이라 `if` · `elif` · `else` 는 8개, 그 안쪽 `method = …` 는 4개 더(12개)입니다.
- **미리 채운 함수**
  - `make_plan`: 회수 대상을 복사해 세 키를 추가한 계획을 만듭니다(판단이 없는 복사라 미리 채움).
  - `count_users_by_role` 의 `for info in users.values():` 에서 `.values()` 는 딕셔너리의 값만 하나씩 꺼냅니다.
- **`load_to_revoke`**(`revoke_input.py` 에 들어 있고 그대로 붙여 넣습니다): 어제 점검을 같은 방법으로 다시 해서 회수 대상 8건을 만듭니다.
  - 어제와 같은 결과를 얻으려고 점검 시각은 `2026-10-29 14:00` 으로 고정했습니다.
- 오늘 데이터에서 영향이 2건 이상인 계획은 dami 의 역할 해제 두 건(영향 2)이고, 3교시에서 승인 대상이 됩니다.
- 10번의 `elif not info["employed"]` 는 「재직 여부(`employed`)가 `False` 이면」입니다.
  - 주석 목록의 10번이 `elif` 입니다.
  - `not` 은 참과 거짓을 뒤집습니다.
- 채우기 전에 실행하면 `NameError: name 'method' is not defined` 오류가 납니다.
  - 회수 방법(`method`)을 아직 정하지 않았는데 `build_plan` 에 전달하려 하기 때문입니다. 위의 `exception_id` · `count_users_by_role` · `build_plan` 은 채우기 전에도 오류가 나지 않습니다.

**`day05_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 어제 점검 결과를 만들고 `plan_revocation` 으로 계획을 세워 세 단계로 출력합니다.

```python
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 방금 만든 회수 계획 함수를 불러온다

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 회수 계획을 세운다(실제로는 지우지 않는다)

print("--- 단계 1: 계획 - 회수 대상", len(to_revoke), "건의 회수 방법")   # 단계 1 시작을 알리는 줄
for plan in plans:                                               # 계획을 하나씩 꺼낸다
    print(plan["user"], plan["permission"], "<-", plan["source"], "|", plan["method"], "| 영향", plan["impact"], "건")   # 사용자 · 권한 <- 출처 | 방법 | 영향을 출력한다

print("--- 단계 2: 집계 - 방법별 건수")                           # 단계 2 시작을 알리는 줄
counts = {}                                                      # 방법 → 건수를 담을 빈 딕셔너리
for plan in plans:                                               # 계획을 하나씩 꺼낸다
    count_key = plan["method"]                                   # 세는 기준이 되는 키
    old_count = counts.get(count_key, 0)                         # 그 키의 지금까지 센 수(처음이면 0)
    counts[count_key] = old_count + 1                            # 1 늘려서 다시 적는다
print(counts)                                                    # 방법별 건수를 출력한다

print("--- 단계 3: 확인 - 역할별 사용자 수와 이름")                    # 단계 3 시작을 알리는 줄
names_by_role = {"finance": [], "sales": []}                     # 역할 → 그 역할을 가진 사용자 이름 리스트
for name, info in USERS.items():                                 # 사용자를 하나씩 꺼낸다
    if info["role"] in names_by_role:                            # finance 나 sales 역할이면
        names_by_role[info["role"]].append(name)                 # 그 역할의 이름 리스트에 이름을 추가한다
for role in names_by_role:                                       # 두 역할을 하나씩 꺼낸다
    names = names_by_role[role]                                  # 그 역할의 이름 리스트
    print(role, len(names), "명", names)                         # 역할 · 사용자 수 · 이름을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `revoke_input.py` · `revoke_plan.py` · `day05_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다. 만드는 법은 둘 중 하나를 고릅니다.
   - VS Code: `access_control` 폴더를 선택하고 **새 파일**(New File) 아이콘을 눌러 이름을 입력합니다.
   - 터미널: `pwd` 로 `access_control` 인지 확인하고 `touch 이름` 으로 만든 뒤 VS Code 에서 열어 붙여 넣습니다(`vim 이름` → `i` → 붙여넣기 → `Esc` → `:wq` 도 됩니다).
2. **[VS Code]** `revoke_plan.py` 에서 직접 쓰는 곳 다섯 군데(`exception_id` · `count_users_by_role` · `build_plan` · `plan_revocation`)를 씁니다. 2.1 의 카드와 표, 흐름 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_2-1_run.py
   ```
4. 출력은 세 단계입니다. 단계 1은 `회수 대상 8 건의 회수 방법` 줄과 계획 여덟 줄, 단계 2는 방법별 건수 딕셔너리 한 줄, 단계 3은 역할 두 줄(사용자 수와 이름)입니다.
5. **[보고서]** `day05_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 회수 방법별 건수와 `finance` · `sales` 역할의 사용자 수를 적어 주세요.
   - (나) 🔍 dami 의 역할 `sales` 권한 `SALES:QUERY` 를 「`sales` 역할에서 `SALES:QUERY` 권한 빼기」로 회수했다면 누가 영향을 받았을까요? 코드가 퇴사한 dami 를 「역할 해제」로 정한 이유도 적어 주세요.
   - (다) 🔍 회수 대상 8건 가운데 dami 의 권한이 3건입니다. 실제로 지우기 전에 회수 계획을 리스트로 먼저 만들어 보는 이유와, dami 3건을 처리하려고 데이터를 실제로 바꾸는 작업의 종류가 몇 가지인지(`users` 의 dami 정보를 바꾸는 일, 예외 리스트 `EXCEPTIONS` 에서 지우는 일 중 몇 가지가 필요한지) 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 예외로 받은 권한인지 | `if "예외" in finding["source"]:` |
| 퇴사한 사용자인지 | `elif not info["employed"]:` |
| 회수 방법 정하기 | `method = "예외 삭제"` · `method = "역할 해제"` · `method = "역할에서 권한 빼기"` |
| 계획 한 건 만들기 | `build_plan(finding, method, users, roles, role_counts)` (지울 대상과 영향을 정함. 역할 두 경우의 영향은 직접 씀) |
| 예외 번호 꺼내기 | `number_text = number_text.replace("번", "")` → `return int(number_text)` |
| 역할별 사용자 수 세기 | `old_count = counts.get(role, 0)` → `counts[role] = old_count + 1` |
| 역할 해제의 영향 | `role_permissions = roles[info["role"]]` → `impact = len(role_permissions)` |
| 역할에서 권한 빼기의 영향 | `impact = role_counts[info["role"]]` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 승인이 필요한 회수 계획 가려내기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「회수할 8건 가운데에는 데이터를 바꾸는 쓰기 권한(`CHANGE`)도 있습니다. 쓰기 권한은 잘못 없애면 영향이 크니 보안 책임자의 승인을 받고 회수하고 싶습니다. 조회 같은 일반 권한 한 건은 바로 회수해도 됩니다.
>
> 다만 퇴사한 사람의 역할을 비우면 그 사람이 역할로 받던 권한이 모두 없어집니다. 이렇게 권한이 2개 이상 사라지는 회수는 조회 권한이어도 승인을 받아 주세요. 8건 가운데 어느 것이 승인 대상인지 가려서, 계획마다 승인 상태를 적어 주세요. 보안 책임자가 승인한 것과 아직 기다리는 것도 구분해 주세요.」
> - **왜 중요한가**: 중요한 권한을 한 사람이 혼자 정하면 실수나 부정이 생길 수 있습니다. 승인 상태가 적혀 있으면 어느 회수가 승인을 받았고 어느 회수가 아직 기다리는지 바로 알 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 2교시의 계획은 8건 모두 같은 방식으로 다룹니다. 하지만 권한마다 중요도가 다릅니다. 데이터를 바꾸는 권한(`CHANGE`)은 잘못 없애면 그 권한으로 일하던 사람의 업무가 멈추고 실제 서비스에서는 되돌리기도 어렵습니다.
2. 그래서 승인이 필요한 경우를 둘로 정합니다. ① **민감한 권한**(sensitive · 센서티브, 잘못 없애면 피해가 큰 권한)이다 ② 한 번의 회수로 권한이 2개 이상 사라지는 경우(영향 2건 이상)다. 예를 들어 퇴사한 dami 의 역할을 비우면 dami 가 그 역할로 받던 권한 2개가 모두 없어진다. 이 경우에는 보안 책임자의 승인을 받고, 그 밖의 일반 권한 한 건은 바로 회수합니다.
3. 이 교시에서는 계획마다 승인이 필요한지, 필요하다면 승인됐는지를 **승인 상태**로 적습니다. 실제로 지우는 일은 4교시에서 합니다.

### 📖 3.1 승인이 필요한 경우와 승인 상태

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- 승인이 필요한 계획은 둘 중 하나입니다.
  - ① `config/sensitive.json` 에 적힌 민감한 권한: junho 의 `SALES:CHANGE`(예외 2번), dami 의 `SALES:CHANGE`(역할 해제) 두 건입니다.
  - ② 영향(`impact`)이 2건 이상: dami 의 역할 해제 두 건(영향 2건)입니다.
  - 겹치는 것을 한 번만 세면 승인이 필요한 계획은 모두 3건입니다.
- 민감한 권한 리스트는 「자원:행위」 문자열의 리스트입니다.
  - 쓰기 권한인 `SALES:CHANGE` · `ACCOUNT:CHANGE` · `SETTLE:CHANGE` 세 개를 적었습니다.
  - `QUERY` 는 조회, `CHANGE` 는 변경(쓰기)입니다.
- 예외 1 · 2 · 4 · 5번은 만료 시각이 이미 지났습니다(어제 점검 결과에 「만료된 예외」로 나왔습니다).
  - 접근은 이미 막혀 있지만 예외 기록이 남아 있어서 회수 대상입니다.
  - 3번은 아직 유효하지만 dami 가 퇴사해서 쓸 수 없습니다.
- 승인 요청서는 따로 만들지 않고, 계획 한 건마다 `approval` 키에 **승인 상태**를 적습니다. 값은 아래 세 가지 중 하나입니다.

| `approval` 값 | 뜻 |
|---|---|
| `승인 불필요` | 승인 없이 바로 회수할 수 있는 계획 |
| `승인됨` | 승인이 필요한데 보안 책임자가 승인함 |
| `승인 대기` | 승인이 필요한데 아직 결정이 없음 |

- 보안 책임자가 승인할지는 사람이 정하고, 그 결정은 `decisions` 딕셔너리로 주어집니다.
  - 예: `{"dami:SALES:QUERY": "승인"}` 처럼 키는 「사용자:권한」 문자열입니다. 여기에 없는 계획은 아직 결정하지 않은 것입니다.
  - dami 의 `SALES:QUERY` 계획은 둘(역할 해제, 예외 3번 삭제)이지만 결정 키 `dami:SALES:QUERY` 는 같습니다.
  - 이 키는 승인이 필요한 계획에서만 찾는데, 오늘은 역할 해제 쪽만 승인이 필요합니다.
- **직접 쓰는 곳은 세 함수**입니다. 판단이 필요한 함수마다 1 ~ 6줄만 쓰고, 나머지는 미리 채웠습니다.
  - `plan_key`(1번): 계획에서 「사용자:권한」 문자열을 만듭니다(승인 결정을 찾는 키).
  - `needs_approval`(2 ~ 4번): 민감한 권한이거나 영향이 2건 이상이면 `True` 를 리턴합니다.
  - `mark_approvals`(5 ~ 10번): 계획마다 승인 상태(`approval`)를 정합니다.
- **미리 채운 함수**
  - `load_sensitive`: 민감한 권한 파일을 읽습니다(판단이 없는 읽기라 미리 채움).

```
+---------------------------------------------+
| mark_approvals(plans, sensitive, decisions) |
+---------------------------------------------+
   |
   v
+---------------------------------------+
| results = []  (결과를 담을 빈 리스트) |
+---------------------------------------+
   |
   v
+------------------------------------------+
| 계획을 하나씩 꺼내 복사본(item)을 만든다 |
+------------------------------------------+
   |
   v
+--------------------------------------------------------------------------+
| 승인이 필요한가? (needs_approval: 민감한 권한이거나 영향이 2건 이상인가) |
+--------------------------------------------------------------------------+
   |
   +--> 아니다 --> item["approval"] = "승인 불필요" --> 아래 「results 에 추가한다」로
   |
   v  그렇다
+-----------------------------------------------+
| 보안 책임자의 결정(decisions)이 「승인」인가? |
+-----------------------------------------------+
   |
   +--> 그렇다 --> item["approval"] = "승인됨" --> 아래 「results 에 추가한다」로
   |
   +--> 아니다 --> item["approval"] = "승인 대기" --> 아래 「results 에 추가한다」로
   |
   v
+--------------------------------------------------+
| item 을 results 에 추가하고 다음 계획으로 (반복) |
+--------------------------------------------------+
   |
   v  모든 계획을 꺼낸 뒤
results 를 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 승인이 필요한 회수 계획 가려내고 승인 상태 적기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 2교시의 계획 8건이 모두 같은 리스트에 섞여 있습니다. 쓰기 권한처럼 승인이 필요한 것과 바로 회수해도 되는 것을 담당자가 눈으로 가려야 합니다.
- **그래서 만드는 것**: `mark_approvals` 입니다.
  - 승인이 필요 없는 계획은 「승인 불필요」, 승인이 필요하고 보안 책임자가 승인하기로 한 계획은 「승인됨」, 승인이 필요한데 아직 결정이 없는 계획은 「승인 대기」로 `approval` 키에 적습니다.
- **실행하면**: 단계 1은 계획 8건의 승인 상태를 출력하고, 단계 2는 승인 상태별 건수를 출력합니다.
- **현업에서는**: 접근 관리 도구도 중요한 권한의 변경은 승인자를 거치고, 승인 여부를 기록으로 남깁니다.

**🎯 할 일**

1. `config/sensitive.json` · `revoke_approve.py` · `day05_3-1_run.py` 세 파일을 만들고, `plan_key` · `needs_approval` · `mark_approvals` 에서 직접 쓰는 곳 세 군데를 씁니다.
2. 실행해서 <mark>승인 상태</mark>(단계 1: 승인 상태)와 <mark>승인 상태별 건수</mark>(단계 2: 집계)를 읽습니다.

**`config/sensitive.json`** — 그대로 붙여 넣습니다. 민감한 권한 리스트입니다. `access_control` 안의 `config` 폴더에 만듭니다.

```json
["SALES:CHANGE", "ACCOUNT:CHANGE", "SETTLE:CHANGE"]
```

**`revoke_approve.py`**

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def load_sensitive(path):                                        # 민감한 권한 파일 경로를 받는 함수
    """민감한 권한 파일을 읽어 「자원:행위」 문자열의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽어 그대로 리턴한다


def plan_key(plan):                                              # 계획 한 건을 받는 함수
    """「사용자:권한」 문자열(예: "dami:SALES:CHANGE")을 리턴한다. 승인 결정을 찾는 키로 쓴다."""
    user = plan["user"]                                          # 계획의 사용자
    permission = plan["permission"]                              # 계획의 권한
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. f"{user}:{permission}" 을 리턴한다 (사용자와 권한을 : 로 이어 붙인 문자열)


def needs_approval(plan, sensitive):                             # 계획 한 건과 민감한 권한 리스트를 받는 함수
    """민감한 권한이거나 영향이 2건 이상이면 True, 아니면 False 를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. plan["permission"] 이 sensitive 안에 있는지(in)를 is_sensitive 에 담는다
    # 3. plan["impact"] 가 2 이상인지(>=)를 is_big_impact 에 담는다
    # 4. is_sensitive 이거나 is_big_impact 이면 True 가 되도록 리턴한다 (or)


def mark_approvals(plans, sensitive, decisions):                 # 계획 리스트 · 민감한 권한 리스트 · 승인 결정 딕셔너리를 받는 함수
    """계획마다 "approval" 키(승인 상태)를 적은 복사본 리스트를 리턴한다. 승인 상태는 「승인 불필요」 · 「승인됨」 · 「승인 대기」 중 하나다."""
    results = []                                                 # 결과를 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        item = plan.copy()                                       # 원래 계획은 바꾸지 않고 복사한다
        key = plan_key(plan)                                     # 승인 결정을 찾는 「사용자:권한」 문자열을 만든다
        decision = decisions.get(key)                            # 보안 책임자의 결정을 꺼낸다(결정이 없으면 None)
        needs = needs_approval(plan, sensitive)                  # 승인이 필요한 계획인지 알아본다(True 또는 False)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. needs 가 거짓이면 (not)
        # 6.   item["approval"] 을 "승인 불필요" 로 정한다
        # 7. 그렇지 않고 decision 이 "승인" 이면 (elif)
        # 8.   item["approval"] 을 "승인됨" 으로 정한다
        # 9. 그렇지 않으면 (else)
        # 10.  item["approval"] 을 "승인 대기" 로 정한다
        results.append(item)                                     # 승인 상태를 적은 복사본을 결과 리스트에 추가한다
    return results                                               # 결과 리스트를 리턴한다

```

- 직접 쓰는 곳은 세 함수이고, 모두 함수 안이라 앞에 공백 4개를 기본으로 넣습니다(Tab 키 한 번).
  - `plan_key` · `needs_approval` 안: 1 ~ 4번은 모두 4개입니다.
  - `mark_approvals` 안: 미리 채운 `for` 안쪽이라 `if` · `elif` · `else` 는 8개이고, 그 안쪽 `item["approval"] = …` 는 4개 더(12개)입니다. 위의 `key` · `decision` · `needs` 는 미리 채운 줄입니다.
  - 나머지 줄은 미리 채워 두었으니 그대로 둡니다.
- 5번의 `not needs` 는 「승인이 필요하지 않으면」입니다(`needs` 는 승인이 필요한지의 참 · 거짓). `not` 은 참과 거짓을 뒤집습니다.
- 채우기 전에 실행하면 `KeyError: 'approval'` 오류가 납니다. 승인 상태(`approval`)를 아직 적지 않았기 때문입니다.

**`day05_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 2교시의 계획을 만든 뒤 `mark_approvals` 로 승인 상태를 정하고 두 단계로 출력합니다.

```python
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 2교시에 만든 회수 계획 함수를 불러온다
from revoke_approve import load_sensitive, mark_approvals        # 방금 만든 승인 함수를 불러온다

DECISIONS = {"dami:SALES:QUERY": "승인", "dami:SALES:CHANGE": "승인"}  # 보안 책임자의 결정. 여기 없는 계획은 아직 결정하지 않은 것이다

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 2교시와 같은 방법으로 회수 계획을 세운다
sensitive = load_sensitive("config/sensitive.json")              # 민감한 권한 리스트를 읽는다
results = mark_approvals(plans, sensitive, DECISIONS)            # 계획마다 승인 상태를 적는다

print("--- 단계 1: 승인 상태 - 계획 8건")                        # 단계 1 시작을 알리는 줄
for item in results:                                             # 결과를 하나씩 꺼낸다
    print(item["user"], item["permission"], "<-", item["source"], "|", item["method"], "| 영향", item["impact"], "건 |", item["approval"])  # 사용자 · 권한 <- 출처 | 방법 | 영향 | 승인 상태를 출력한다

print("--- 단계 2: 집계 - 승인 상태별 건수")                     # 단계 2 시작을 알리는 줄
counts = {}                                                      # 승인 상태 → 건수를 담을 빈 딕셔너리
for item in results:                                             # 결과를 하나씩 꺼낸다
    count_key = item["approval"]                                 # 세는 기준이 되는 키
    old_count = counts.get(count_key, 0)                         # 그 키의 지금까지 센 수(처음이면 0)
    counts[count_key] = old_count + 1                            # 1 늘려서 다시 적는다
print(counts)                                                    # 승인 상태별 건수를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `config/sensitive.json` · `revoke_approve.py` · `day05_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다. 만드는 법은 둘 중 하나를 고릅니다.
   - VS Code: `access_control` 폴더를 선택하고 **새 파일**(New File) 아이콘을 눌러 이름을 입력합니다(`config/…` 이름은 이 폴더를 선택한 채 입력하면 `config` 폴더 안에 만들어집니다).
   - 터미널: `pwd` 로 `access_control` 인지 확인하고 `touch 이름` 으로 만든 뒤 VS Code 에서 열어 붙여 넣습니다(`vim 이름` → `i` → 붙여넣기 → `Esc` → `:wq` 도 됩니다).
2. **[터미널]** `ls config` 로 `sensitive.json` 이 `users.json` 과 같은 `config` 폴더에 있는지 보고, `python -m json.tool config/sensitive.json`(맥북은 `python3`)로 내용이 정상인지 확인합니다.
   - 깨진 채 두면 민감한 권한 리스트를 읽지 못해 junho 의 `SALES:CHANGE` 가 「승인 불필요」로 나오고, 승인이 필요한 계획이 3건에서 2건으로 줄어듭니다.
3. **[VS Code]** `revoke_approve.py` 에서 `plan_key` · `needs_approval` · `mark_approvals` 에서 직접 쓰는 곳 세 군데를 씁니다. 3.1 의 표와 그림을 보고 씁니다.
4. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_3-1_run.py
   ```
5. 출력은 두 단계입니다. 단계 1은 `계획 8건` 제목 줄과 계획 여덟 줄(줄마다 승인 상태), 단계 2는 승인 상태별 건수 딕셔너리 한 줄입니다.
6. **[보고서]** `day05_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 「승인 불필요」 · 「승인됨」 · 「승인 대기」가 각각 몇 건인지, 승인 대기인 계획이 무엇인지 적어 주세요.
   - (나) 🔍 권한을 없애는 일인데 왜 쓰기 권한 같은 민감한 권한은 승인을 받게 할까요? 조회 같은 일반 권한 한 건은 바로 회수해도 되는 이유도 적어 주세요.
   - (다) 🔍 junho 의 `SALES:CHANGE`(예외 2번) 계획은 승인 대기입니다. 4교시에서 이 계획은 어떻게 처리될지 예상해서 적고, 승인이 오래 나지 않으면 어떤 문제가 생길지도 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 결정을 찾는 키 | `return f"{user}:{permission}"` (`plan_key` 안) |
| 승인이 필요한지 | `is_sensitive = plan["permission"] in sensitive` · `is_big_impact = plan["impact"] >= 2` → `return is_sensitive or is_big_impact` (`needs_approval` 안) |
| 승인이 필요 없을 때 | `if not needs:` → `item["approval"] = "승인 불필요"` |
| 결정이 「승인」인지 | `elif decision == "승인":` → `item["approval"] = "승인됨"` |
| 그 밖(결정 없음) | `else:` → `item["approval"] = "승인 대기"` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 회수 실행하고 이력 남기기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「승인이 필요 없거나 승인된 것만 실제로 회수하고, 회수한 내용을 이력 파일로 남겨 주세요. 아직 승인되지 않은 것은 실행하지 말고 「대기」로 남겨 주세요.
>
> 회수한 뒤에는 같은 사용자 · 권한으로 접근을 다시 판정해서 정말 막혔는지 확인해 주세요. 회수했다고 적어 놓고 여전히 접근이 허용되면 안 됩니다.」
> - **왜 중요한가**: 회수했다는 기록만으로는 부족합니다. 다시 판정해 보아야 정말 막혔는지 알 수 있고, 이력이 있어야 나중에 누가 언제 왜 없앴는지 설명할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 승인 상태까지 정해진 계획을 이제 실행합니다. 승인 상태가 「승인 불필요」 또는 「승인됨」인 계획만 실행하고, 「승인 대기」인 계획은 실행하지 않습니다.
2. 실행한 뒤에는 **같은 사용자 · 권한을 다시 판정**합니다. 10/22(목)의 `evaluate_access` 가 회수 전과 후에 같은 요청을 어떻게 판정하는지 비교하면 회수가 정말 효과가 있었는지 알 수 있습니다.
3. 실행한 내용은 **회수 이력**(`revocation_log.json`)으로 남깁니다. 어제의 「사용 이력」(권한을 마지막으로 쓴 시각의 기록)과 다른 것입니다. 회수 이력은 오늘 무엇을 회수했는지의 기록입니다.

### 📖 4.1 실행 방법과 이력

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 방법 | 실제로 하는 일 |
|---|---|
| 예외 삭제 | 예외 리스트(`EXCEPTIONS`)에서 번호가 `target` 인 예외 한 건을 지움 |
| 역할 해제 | `users[target]["role"]` 을 빈 문자열(`""`)로 바꿈. 어떤 역할의 권한도 받지 않게 됨 |
| 역할에서 권한 빼기 | `roles[target]` 권한 리스트에서 그 권한을 지움 |

- 이력 한 건은 여섯 키로 이루어집니다: `time`(회수 시각) · `user` · `permission` · `method` · `approval`(승인 상태) · `result`(「실행」 또는 「대기」).
  - `result` 의 「대기」는 `approval` 이 「승인 대기」라서 실행하지 않았다는 뜻입니다.
- **직접 쓰는 곳은 세 함수**입니다. 판단이 필요한 함수마다 3 ~ 5줄만 쓰고, 나머지는 미리 채웠습니다.
  - `remove_exception`(1 ~ 3번): 번호가 같은 예외를 찾아 지웁니다(`리스트.remove(값)` 은 리스트에서 그 값을 지웁니다).
  - `apply_plan`(4 ~ 8번): 회수 방법별로 실제로 지우는 일(세 곳)입니다.
  - `execute_revocation`(9 ~ 13번): 계획마다 「대기」인지 「실행」인지 정합니다.
- **미리 채운 함수**
  - `save_log`: 이력을 JSON 파일로 저장합니다(판단이 없는 저장이라 미리 채움, 10/23(금)의 `save_requests` 와 같은 방법입니다).
- 회수한 뒤에 다시 판정하면 결과가 달라질 수 있습니다.
  - `execute_revocation` 이 바꾼 `USERS` · `ROLES` · `EXCEPTIONS` 를 `evaluate_access` 도 같은 것으로 읽기 때문입니다.
  - `evaluate_access(사용자, 자원, 행위, 시각)` 는 `(허용 여부, 이유)` 두 값을 리턴합니다(10/22(목)).
- `apply_plan` 은 승인 상태를 보지 않습니다. 승인 상태를 보고 실행할지 정하는 것은 `execute_revocation` 이 하는 일입니다.
- `day05_4-1_run.py` 는 회수 전과 후에 계획마다 `evaluate_access` 로 같은 사용자 · 권한을 판정해 「허용(이유)」 또는 「거부(이유)」 문자열로 비교합니다.

```
+----------------------------------------------------------+
| execute_revocation(plans, users, roles, exceptions, now) |
+----------------------------------------------------------+
   |
   v
+-----------------------------------+
| log = []  (이력을 담을 빈 리스트) |
+-----------------------------------+
   |
   v
+----------------------+
| 계획을 하나씩 꺼낸다 |
+----------------------+
   |
   v
+--------------------------------+
| approval 이 「승인 대기」인가? |
+--------------------------------+
   |
   +--> 그렇다 --> result = "대기"   (아무것도 지우지 않음) --> 아래 「이력 한 건」으로
   |
   v  아니다
+----------------------------------------------------------------+
| apply_plan 으로 실제로 회수한다 (방법별로 지우는 일은 직접 씀) |
+----------------------------------------------------------------+
   |
   v
+-----------------+
| result = "실행" |
+-----------------+
   |
   v
+----------------------------------------------------------+
| 이력 한 건을 만들어 log 에 추가하고 다음 계획으로 (반복) |
+----------------------------------------------------------+
   |
   v  모든 계획을 꺼낸 뒤
log 를 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 회수를 실행하고 전후 판정과 이력 남기기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 회수 계획과 승인 상태만 있고 실제로는 아무것도 지워지지 않았습니다. 지운 뒤에 정말 막혔는지 확인하는 방법도, 지운 기록도 없습니다.
- **그래서 만드는 것**: `execute_revocation` 입니다.
  - 승인 상태가 「승인 대기」인 계획은 실행하지 않고 「대기」로 남기고, 나머지는 `apply_plan` 으로 실행해 「실행」으로 남기고, 이력 리스트를 리턴합니다.
- **실행하면**: 단계 1은 계획별 실행 결과, 단계 2는 회수 전후의 판정 비교, 단계 3은 `revocation_log.json` 저장과 다시 읽은 건수를 출력합니다.
- **현업에서는**: 회수 도구도 실행한 뒤 다시 판정해 막혔는지 확인하고, 이력을 지우지 않고 보관합니다.

**🎯 할 일**

1. `revoke.py` 와 `day05_4-1_run.py` 두 파일을 만들고, `remove_exception` · `apply_plan` · `execute_revocation` 에서 직접 쓰는 곳 다섯 군데를 씁니다.
2. 실행해서 <mark>회수 결과</mark>(단계 1: 실행), <mark>회수 전후의 판정</mark>(단계 2: 확인), <mark>저장한 이력</mark>(단계 3: 저장)을 읽고, 새로 생긴 `revocation_log.json` 파일도 열어 봅니다.

**`revoke.py`**

```python
import json                                                      # JSON 파일을 쓰는 모듈을 불러온다


def remove_exception(exceptions, target_id):                     # 예외 리스트와 지울 예외 번호를 받는 함수
    """예외 리스트에서 번호가 target_id 인 예외 한 건을 지운다. 지웠으면 True, 못 찾았으면 False 를 리턴한다."""
    for exc in exceptions:                                       # 예외를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. exc["id"] 가 target_id 와 같으면 (==)
        # 2.   exceptions 에서 exc 를 지운다 (.remove)
        # 3.   True 를 리턴한다 (지웠다고 알리고 함수를 끝낸다)
    return False                                                 # 끝까지 못 찾았으면 False 를 리턴한다


def apply_plan(plan, users, roles, exceptions):                  # 계획 한 건 · 사용자 · 역할 · 예외 리스트를 받는 함수
    """계획 한 건의 회수 방법대로 프로그램 안의 데이터를 실제로 바꾼다. 승인 상태는 보지 않는다(승인 확인은 호출하는 쪽이 한다)."""
    if plan["method"] == "예외 삭제":                            # 방법이 예외 삭제이면
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. remove_exception(exceptions, plan["target"]) 을 호출한다 (예외 리스트에서 그 번호의 예외를 지운다)
    elif plan["method"] == "역할 해제":                          # 방법이 역할 해제이면
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. users[plan["target"]] 를 user_info 에 담는다 (그 사용자의 정보 딕셔너리)
        # 6. user_info["role"] 을 빈 문자열 "" 로 바꾼다 (어떤 역할의 권한도 받지 않게 된다)
    else:                                                        # 방법이 역할에서 권한 빼기이면
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. roles[plan["target"]] 를 role_permissions 에 담는다 (그 역할의 권한 리스트)
        # 8. role_permissions 에서 plan["permission"] 을 지운다 (.remove)


def save_log(log, path):                                         # 이력 리스트와 저장할 파일 경로를 받는 함수
    """이력 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다. 한글이 그대로 보이게 쓴다."""
    with open(path, "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
        json.dump(log, f, ensure_ascii=False, indent=2)          # 이력을 파일에 JSON 으로 쓴다
    return len(log)                                              # 저장한 건수를 리턴한다


def execute_revocation(plans, users, roles, exceptions, now):    # 계획 · 사용자 · 역할 · 예외 리스트 · 지금 시각 문자열을 받는 함수
    """승인 불필요이거나 승인됨인 계획만 실제로 실행하고, 이력 리스트를 리턴한다. 승인 대기인 계획은 실행하지 않고 이력에 「대기」로 남긴다."""
    log = []                                                     # 이력을 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 9. plan["approval"] 이 "승인 대기" 이면 (==)
        # 10.  result 를 "대기" 로 정한다
        # 11. 그렇지 않으면 (else)
        # 12.  apply_plan(plan, users, roles, exceptions) 를 호출한다
        # 13.  result 를 "실행" 으로 정한다
        entry = {
            "time": now,                                         # 시각
            "user": plan["user"],                                # 사용자
            "permission": plan["permission"],                    # 권한
            "method": plan["method"],                            # 회수 방법
            "approval": plan["approval"],                        # 승인 상태
            "result": result,                                    # 결과(실행 또는 대기)
        }
        log.append(entry)                                        # 이력 한 건을 만들어 이력 리스트에 추가한다
    return log                                                   # 이력 리스트를 리턴한다

```

- 직접 쓰는 곳은 세 함수이고, 모두 함수 안이라 앞에 공백 4개를 기본으로 넣습니다(Tab 키 한 번).
  - `remove_exception` 안: 미리 채운 `for` 안쪽이라 1번 `if` 는 8개이고, 그 안쪽(2 · 3번)은 4개 더(12개)입니다.
  - `apply_plan` 안: 미리 채운 `if` · `elif` · `else` 가 4개이고, 그 안쪽 줄(4 ~ 8번)은 4개 더(8개)입니다.
  - `execute_revocation` 안: 미리 채운 `for` 안쪽이라 `if` · `else` 는 8개이고, 그 안쪽은 4개 더(12개)입니다.
  - 나머지 줄은 미리 채워 두었으니 그대로 둡니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다(파이썬 버전에 따라 뒤에 `after 'if' statement on line …` 가 붙습니다). `remove_exception` 의 `for` 아래에 실행할 줄이 아직 없기 때문입니다.

**`day05_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 3교시까지의 계획과 승인 상태를 만든 뒤 회수 전 판정을 모으고, `execute_revocation` 으로 회수하고, 회수 후 판정을 모아 비교하고, 이력을 저장합니다.

```python
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from exception_policy import EXCEPTIONS, TIME_FORMAT             # 10/22(목)에 만든 예외 리스트와 시각 형식을 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 최종 판정 함수를 불러온다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 2교시에 만든 회수 계획 함수를 불러온다
from revoke_approve import load_sensitive, mark_approvals        # 3교시에 만든 승인 함수를 불러온다
from revoke import execute_revocation, save_log                  # 방금 만든 회수 실행 함수와 이력 저장 함수를 불러온다

NOW_TEXT = "2026-10-30 10:00"                                    # 오늘 오전 실습의 지금 시각 문자열(고정)
NOW = datetime.strptime(NOW_TEXT, TIME_FORMAT)                   # 같은 시각을 시각으로 바꾼다. 판정 함수가 쓴다
DECISIONS = {"dami:SALES:QUERY": "승인", "dami:SALES:CHANGE": "승인"}  # 보안 책임자의 결정(3교시와 같다)

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 회수 계획을 세운다
sensitive = load_sensitive("config/sensitive.json")              # 민감한 권한 리스트를 읽는다
plans = mark_approvals(plans, sensitive, DECISIONS)              # 계획마다 승인 상태를 적는다

def judge(plan):                                                 # 계획 한 건을 받는 함수
    """계획의 사용자 · 권한을 지금 판정해 「허용(이유)」 또는 「거부(이유)」 문자열을 리턴한다."""
    resource, action = plan["permission"].split(":")             # "SALES:QUERY" 를 자원과 행위로 나눈다
    ok, reason = evaluate_access(plan["user"], resource, action, NOW)  # 최종 판정을 한다
    if ok:                                                       # 허용이면
        return "허용(" + reason + ")"                            # 허용과 이유를 하나의 문자열로 합친다
    return "거부(" + reason + ")"                                # 거부와 이유를 하나의 문자열로 합친다


def judge_all(plans):                                            # 계획 리스트를 받는 함수
    """계획마다 judge 로 판정한 문자열을 같은 순서의 리스트로 리턴한다."""
    results = []                                                 # 판정을 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        verdict = judge(plan)                                    # 계획 한 건을 판정한다
        results.append(verdict)                                  # 판정해서 추가한다
    return results                                               # 판정 리스트를 리턴한다


before = judge_all(plans)                                        # 회수하기 전의 판정을 모두 구해 둔다
log = execute_revocation(plans, USERS, ROLES, EXCEPTIONS, NOW_TEXT)  # 회수를 실행한다
after = judge_all(plans)                                         # 회수한 뒤의 판정을 모두 구한다

print("--- 단계 1: 실행 - 회수 결과")                            # 단계 1 시작을 알리는 줄
done = 0                                                         # 실행한 건수를 0 으로 시작한다
for entry in log:                                                # 이력을 하나씩 꺼낸다
    print(entry["user"], entry["permission"], "|", entry["method"], "|", entry["result"])  # 사용자 · 권한 | 방법 | 결과를 출력한다
    if entry["result"] == "실행":                                # 실행한 건이면
        done = done + 1                                          # 건수를 1 늘린다
print("실행", done, "건, 대기", len(log) - done, "건")           # 실행과 대기 건수를 출력한다

print("--- 단계 2: 확인 - 회수 전후의 판정")                     # 단계 2 시작을 알리는 줄
plan_count = len(plans)                                          # 개수를 먼저 구한다
for i in range(plan_count):                                      # 번호 i 로 회수 전 리스트와 회수 후 리스트를 짝지어 꺼낸다
    mark = "그대로"                                              # 표시를 그대로로 시작한다
    if before[i] != after[i]:                                    # 회수 전후의 판정이 다르면
        mark = "바뀜"                                            # 바뀜으로 고친다
    print(plans[i]["user"], plans[i]["permission"], "|", before[i], "->", after[i], "|", mark)  # 전후 판정과 표시를 출력한다

print("--- 단계 3: 저장 - 회수 이력")                            # 단계 3 시작을 알리는 줄
count = save_log(log, "revocation_log.json")                     # 이력을 파일로 저장한다
saved = load_json("revocation_log.json", [])                     # 저장한 파일을 다시 읽어
print("저장", count, "건, 다시 읽은 건수", len(saved), "건, 첫 이력:", saved[0]["user"], saved[0]["permission"], saved[0]["result"])  # 건수와 첫 이력을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `revoke.py` · `day05_4-1_run.py` 를 만들어 위 코드를 붙여 넣습니다. 만드는 법은 둘 중 하나를 고릅니다.
   - VS Code: `access_control` 폴더를 선택하고 **새 파일**(New File) 아이콘을 눌러 이름을 입력합니다.
   - 터미널: `pwd` 로 `access_control` 인지 확인하고 `touch 이름` 으로 만든 뒤 VS Code 에서 열어 붙여 넣습니다(`vim 이름` → `i` → 붙여넣기 → `Esc` → `:wq` 도 됩니다).
2. **[VS Code]** `revoke.py` 에서 `remove_exception` · `apply_plan` · `execute_revocation` 의 직접 쓰는 곳 다섯 군데를 씁니다. 4.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_4-1_run.py
   ```
4. 출력은 세 단계입니다. 단계 1은 계획 여덟 줄과 `실행 N 건, 대기 N 건`, 단계 2는 판정 비교 여덟 줄, 단계 3은 저장 한 줄입니다.
5. **[VS Code]** 왼쪽 목록에 새로 생긴 `revocation_log.json` 을 열어 한글이 그대로 저장됐는지 봅니다.
6. **[보고서]** `day05_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 출력 전체를 붙여 넣고, 이력의 결과가 「실행」인 건수와 「대기」인 건수, 회수 전후 판정이 바뀐 권한, 저장한 이력 건수를 적어 주세요.
   - (나) 🔍 회수를 실행한 7건 가운데 회수 전후 판정이 바뀐 것은 일부입니다. 바뀌지 않은 권한이 그대로인 이유와, 그래도 회수하고 이력을 남기는 이유를 적어 주세요.
   - (다) 🔍 회수 이력에는 시각 · 사용자 · 권한 · 방법 · 승인 상태 · 결과가 들어 있습니다. 반년 뒤 감사(점검 기록을 검토받는 일)에서 「이 권한이 왜 없어졌나요?」라고 물으면 이 이력만으로 답할 수 있을까요? 이력에 없는 정보가 있다면 무엇인지, 어떤 키를 추가하면 되는지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 아직 승인을 기다리는 계획인지 | `if plan["approval"] == "승인 대기":` |
| 실제로 회수하기 | `apply_plan(plan, users, roles, exceptions)` (방법별로 지우는 일은 `apply_plan` 안에서 직접 씀) |
| 번호가 같은 예외 찾기 | `if exc["id"] == target_id:` → `exceptions.remove(exc)` → `return True` (`remove_exception` 안) |
| 예외 삭제 | `remove_exception(exceptions, plan["target"])` |
| 역할 해제 | `user_info = users[plan["target"]]` → `user_info["role"] = ""` |
| 역할에서 권한 빼기 | `role_permissions = roles[plan["target"]]` → `role_permissions.remove(plan["permission"])` |
| 이력 한 건 | `{"time": now, "user": …, "result": result}` 딕셔너리를 `log.append(…)` |

---

## 오전 마무리 — 보고서 2 · 3 · 4교시 칸 확인

`day05_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지 봅니다. `access_control` 폴더에 오늘 만든 파일이 있는지 확인합니다.

```bash
ls
ls config
```

- `revoke_input.py` · `revoke_plan.py` · `revoke_approve.py` · `revoke.py` · `day05_2-1_run.py` · `day05_3-1_run.py` · `day05_4-1_run.py` · `revocation_log.json` 이 보여야 합니다.
  - `config` 안에는 `sensitive.json` 이 새로 보여야 합니다.

오후에는 회수한 뒤에도 조건을 따져 접근을 판단하는 **조건기반 정책**과 판정 함수를 서버로 여는 수업을 합니다. 올리기(git)는 오후 6교시 마지막에 한 번에 합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_2-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 네 함수의 다섯 군데입니다.

① `exception_id` 안(미리 채운 첫 줄 아래)

```python
    number_text = number_text.replace("번", "")                   # "번" 을 지워 "3" 으로 만든다
    return int(number_text)                                      # 문자열 "3" 을 숫자 3 으로 바꿔 리턴한다
```

② `count_users_by_role` 안(미리 채운 `role` 줄 아래)

```python
        old_count = counts.get(role, 0)                          # 그 역할의 지금까지 센 수(처음이면 0)
        counts[role] = old_count + 1                             # 1 늘려서 다시 적는다
```

③ `build_plan` 안(`if method == "역할 해제":` 아래)

```python
        role_permissions = roles[info["role"]]                   # 그 사용자의 역할에 든 권한 리스트
        impact = len(role_permissions)                           # 영향은 그 역할에 든 권한 수
```

④ `build_plan` 안(마지막 `return` 위)

```python
    impact = role_counts[info["role"]]                           # 역할에서 권한 빼기: 영향은 그 역할을 가진 사용자 수(각자 그 권한 1건을 잃는다)
```

⑤ `plan_revocation` 안(미리 채운 `info` 줄 아래)

```python
        if "예외" in finding["source"]:                          # 예외로 받은 권한이면
            method = "예외 삭제"                                 # 그 예외를 지운다
        elif not info["employed"]:                               # 퇴사한 사용자의 역할 권한이면
            method = "역할 해제"                                 # 그 사용자의 역할을 해제한다
        else:                                                    # 재직 중인 사용자의 역할 권한이면
            method = "역할에서 권한 빼기"                        # 역할에서 그 권한을 뺀다
```

**결과**

- (가) 출력은 다음과 같고, 방법별 건수는 예외 삭제 **5건** · 역할 해제 **2건** · 역할에서 권한 빼기 **1건**입니다.
  - 역할별 사용자 수는 `finance` **1명**(junho) · `sales` **2명**(seoyeon · dami)입니다.

```
--- 단계 1: 계획 - 회수 대상 8 건의 회수 방법
junho SALES:QUERY <- 역할 finance | 역할에서 권한 빼기 | 영향 1 건
dami SALES:QUERY <- 역할 sales | 역할 해제 | 영향 2 건
dami SALES:CHANGE <- 역할 sales | 역할 해제 | 영향 2 건
seoyeon SETTLE:QUERY <- 예외 1번 | 예외 삭제 | 영향 1 건
junho SALES:CHANGE <- 예외 2번 | 예외 삭제 | 영향 1 건
dami SALES:QUERY <- 예외 3번 | 예외 삭제 | 영향 1 건
batch-night SALES:QUERY <- 예외 4번 | 예외 삭제 | 영향 1 건
gaeun SETTLE:QUERY <- 예외 5번 | 예외 삭제 | 영향 1 건
--- 단계 2: 집계 - 방법별 건수
{'역할에서 권한 빼기': 1, '역할 해제': 2, '예외 삭제': 5}
--- 단계 3: 확인 - 역할별 사용자 수와 이름
finance 1 명 ['junho']
sales 2 명 ['seoyeon', 'dami']
```

- (나) `sales` 역할에서 `SALES:QUERY` 를 뺐다면 `sales` 역할을 가진 **seoyeon 과 dami 두 사람**이 모두 그 권한을 잃습니다(단계 3의 `sales` 2명, 퇴사한 dami 도 센 수입니다). dami 는 퇴사했으니 문제가 없어도 seoyeon 은 지금도 일하는 사람이라 영업 조회 업무가 멈춥니다.
  - 그래서 퇴사한 dami 는 역할 자체는 그대로 두고 dami 의 `role` 만 해제하는 「역할 해제」로 정합니다.
  - dami 1명이 영향을 받고, 사라지는 권한은 2건(영향 2건)입니다.
- (다) 계획을 먼저 리스트로 만들어 보면 ① 지우기 전에 방법이 맞는지, 영향받는 사람이 누구인지 사람이 확인할 수 있고 ② 계획 단계에서는 잘못된 방법을 고칠 수 있고 ③ 계획 리스트가 승인과 이력의 근거가 됩니다.
  - 실제 서비스에서는 한 번 지우면 되돌리기 어렵다는 점도 계획을 먼저 확인하는 이유입니다.
  - dami 3건을 처리하는 작업의 종류는 **두 가지**입니다.
  - 계획은 3건이지만 역할 해제 2건은 같은 변경이라 종류로는 하나입니다.
  - dami 의 `role` 을 비우는 역할 해제 한 번이 역할로 받은 두 건(`SALES:QUERY` · `SALES:CHANGE`)을 함께 처리하고, 예외 3번 삭제가 한 번입니다.
  - 코드는 계획 3건을 차례로 실행하므로 역할 해제를 두 번 하지만, 같은 값을 다시 쓰는 것이라 결과는 같습니다.

**왜**

- 회수는 되돌리기 어려운 변경이라 지우기 전에 방법과 영향을 먼저 표로 확인합니다.
  - 같은 8건이라도 방법에 따라 영향받는 사람이 1명일 수도, 여러 명일 수도 있습니다.
  - 퇴사자는 역할 정의가 아니라 그 사람의 `role` 만 해제하므로 같은 역할의 재직자에게 영향이 없습니다.

**자주 틀리는 곳**

- `elif not info["employed"]` 검사를 `"예외"` 검사보다 먼저 쓰면, 퇴사한 dami 의 예외 3번이 「예외 삭제」가 아니라 「역할 해제」로 계획됩니다.
  - 오류는 나지 않고 숫자만 달라집니다.
  - 실행하면 다음처럼 됩니다(예외 3번 권한이 「역할 해제」로 나오고 방법별 건수가 예외 삭제 4건 · 역할 해제 3건이면 이 실수입니다).

```
--- 단계 1: 계획 - 회수 대상 8 건의 회수 방법
junho SALES:QUERY <- 역할 finance | 역할에서 권한 빼기 | 영향 1 건
dami SALES:QUERY <- 역할 sales | 역할 해제 | 영향 2 건
dami SALES:CHANGE <- 역할 sales | 역할 해제 | 영향 2 건
seoyeon SETTLE:QUERY <- 예외 1번 | 예외 삭제 | 영향 1 건
junho SALES:CHANGE <- 예외 2번 | 예외 삭제 | 영향 1 건
dami SALES:QUERY <- 예외 3번 | 역할 해제 | 영향 2 건
batch-night SALES:QUERY <- 예외 4번 | 예외 삭제 | 영향 1 건
gaeun SETTLE:QUERY <- 예외 5번 | 예외 삭제 | 영향 1 건
--- 단계 2: 집계 - 방법별 건수
{'역할에서 권한 빼기': 1, '역할 해제': 3, '예외 삭제': 4}
--- 단계 3: 확인 - 역할별 사용자 수와 이름
finance 1 명 ['junho']
sales 2 명 ['seoyeon', 'dami']
```

**관제에서는**

- 회수 도구는 실제로 지우기 전에 계획(드라이 런)을 만들어 담당자에게 보여 주고, 한 번에 권한이 여러 개 사라지는 변경은 따로 확인합니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_3-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `plan_key` 안(미리 채운 `permission` 줄 아래)

```python
    return f"{user}:{permission}"                                # 사용자와 권한을 : 로 이어 붙인다
```

② `needs_approval` 안

```python
    is_sensitive = plan["permission"] in sensitive               # 권한이 민감한 권한 리스트에 있는지(True 또는 False)
    is_big_impact = plan["impact"] >= 2                          # 영향이 2건 이상인지(True 또는 False)
    return is_sensitive or is_big_impact                         # 둘 중 하나라도 참이면 True 를 리턴한다
```

③ `mark_approvals` 안(미리 채운 `needs` 줄 아래)

```python
        if not needs:                                            # 승인이 필요하지 않으면
            item["approval"] = "승인 불필요"                     # 바로 회수할 수 있다
        elif decision == "승인":                                  # 승인이 필요한데 보안 책임자가 승인했으면
            item["approval"] = "승인됨"                          # 회수할 수 있다
        else:                                                    # 승인이 필요한데 아직 결정이 없으면
            item["approval"] = "승인 대기"                       # 결정이 날 때까지 기다린다
```

**결과**

- (가) 출력은 다음과 같고, 승인 불필요 **5건** · 승인됨 **2건** · 승인 대기 **1건**입니다.
  - 승인이 필요한 계획은 3건(dami 의 역할 해제 두 건과 junho 의 `SALES:CHANGE` 예외 2번)이고, 그중 dami 의 두 건은 보안 책임자가 승인하기로 결정해서 「승인됨」, junho 의 예외 2번은 결정이 없어서 「승인 대기」입니다.

```
--- 단계 1: 승인 상태 - 계획 8건
junho SALES:QUERY <- 역할 finance | 역할에서 권한 빼기 | 영향 1 건 | 승인 불필요
dami SALES:QUERY <- 역할 sales | 역할 해제 | 영향 2 건 | 승인됨
dami SALES:CHANGE <- 역할 sales | 역할 해제 | 영향 2 건 | 승인됨
seoyeon SETTLE:QUERY <- 예외 1번 | 예외 삭제 | 영향 1 건 | 승인 불필요
junho SALES:CHANGE <- 예외 2번 | 예외 삭제 | 영향 1 건 | 승인 대기
dami SALES:QUERY <- 예외 3번 | 예외 삭제 | 영향 1 건 | 승인 불필요
batch-night SALES:QUERY <- 예외 4번 | 예외 삭제 | 영향 1 건 | 승인 불필요
gaeun SETTLE:QUERY <- 예외 5번 | 예외 삭제 | 영향 1 건 | 승인 불필요
--- 단계 2: 집계 - 승인 상태별 건수
{'승인 불필요': 5, '승인됨': 2, '승인 대기': 1}
```

- (나) 민감한 권한(쓰기 권한)과, 한 번의 회수로 권한이 여러 개 사라지는 회수는 잘못되면 그 권한으로 일하던 사람의 업무가 멈추고 피해가 큽니다.
  - 한 사람이 혼자 정하면 실수나 잘못된 사용이 생길 수 있어서, 다른 사람(보안 책임자)이 이유를 확인하고 승인하게 합니다.
  - 반면 조회 같은 일반 권한 한 건은 영향이 작고, 필요하면 다시 요청해서 받을 수 있어 되돌리기 쉽습니다.
  - 예를 들어 junho 의 `SALES:QUERY` 는 재직자의 권한이지만 마지막 사용이 90일보다 오래됐다고 어제 점검에서 나왔고 영향이 1건이라 승인 없이 회수합니다.
- (다) 4교시에서 junho 의 `SALES:CHANGE`(예외 2번) 계획은 실행하지 않고 「대기」로 남습니다.
  - 승인이 오래 나지 않으면 이 예외가 정리되지 않은 채 남아 점검에 계속 나오고 담당자가 같은 계획을 거듭 확인해야 합니다.
  - 그 예외는 이미 만료되어 접근은 막혀 있지만, 만료 시각이 고쳐지는 등의 일이 생기면 다시 쓰일 수 있어 오래 두면 위험합니다.

**왜**

- 쓰기 같은 중요한 권한과, 한 번의 회수로 권한이 여러 개 사라지는 회수는 한 사람이 혼자 정하지 않고 승인을 받습니다.
  - 승인 상태를 계획마다 적어 두면 4교시가 「승인 대기」인 계획만 빼고 실행할 수 있습니다.
  - 같은 사용자의 역할 해제 두 건(dami)은 같은 변경(`role` 비우기)이므로 함께 결정해야 합니다.
  - 코드는 이를 막지 않으므로, 한쪽만 승인하면 승인받지 않은 권한까지 함께 없어집니다.

**자주 틀리는 곳**

- 보안 책임자의 결정을 확인하는 `elif decision == "승인":` 줄을 빼먹으면, 승인하기로 한 dami 의 두 건도 「승인 대기」로 나옵니다.
  - 오류는 나지 않고 상태만 달라집니다.
  - 실행하면 다음처럼 됩니다(「승인됨」이 하나도 없고 「승인 대기」가 3건이면 이 실수입니다).

```
--- 단계 1: 승인 상태 - 계획 8건
junho SALES:QUERY <- 역할 finance | 역할에서 권한 빼기 | 영향 1 건 | 승인 불필요
dami SALES:QUERY <- 역할 sales | 역할 해제 | 영향 2 건 | 승인 대기
dami SALES:CHANGE <- 역할 sales | 역할 해제 | 영향 2 건 | 승인 대기
seoyeon SETTLE:QUERY <- 예외 1번 | 예외 삭제 | 영향 1 건 | 승인 불필요
junho SALES:CHANGE <- 예외 2번 | 예외 삭제 | 영향 1 건 | 승인 대기
dami SALES:QUERY <- 예외 3번 | 예외 삭제 | 영향 1 건 | 승인 불필요
batch-night SALES:QUERY <- 예외 4번 | 예외 삭제 | 영향 1 건 | 승인 불필요
gaeun SETTLE:QUERY <- 예외 5번 | 예외 삭제 | 영향 1 건 | 승인 불필요
--- 단계 2: 집계 - 승인 상태별 건수
{'승인 불필요': 5, '승인 대기': 3}
```

**관제에서는**

- 승인 대기 중인 계획에는 처리 기한을 정해 두고, 넘으면 담당자에게 알립니다.
  - 승인한 사람과 요청한 사람은 달라야 합니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_4-1_run.py
```

**채운 코드** (한 예) — 직접 쓰는 곳은 `remove_exception` 의 한 곳, `apply_plan` 의 세 곳, `execute_revocation` 의 한 곳입니다.

① `remove_exception` 안(미리 채운 `for` 아래)

```python
        if exc["id"] == target_id:                               # 번호가 같으면
            exceptions.remove(exc)                               # 리스트에서 그 예외를 지운다
            return True                                          # 지웠다고 알리고 함수를 끝낸다
```

② `apply_plan` 안(미리 채운 `if` 아래)

```python
        remove_exception(exceptions, plan["target"])             # 예외 리스트에서 그 번호의 예외를 지운다
```

③ `apply_plan` 안(미리 채운 `elif` 아래)

```python
        user_info = users[plan["target"]]                        # 그 사용자의 정보 딕셔너리를 꺼낸다
        user_info["role"] = ""                                   # 역할을 빈 문자열로 바꾼다(어떤 역할의 권한도 받지 않게 된다)
```

④ `apply_plan` 안(미리 채운 `else` 아래)

```python
        role_permissions = roles[plan["target"]]                 # 그 역할의 권한 리스트를 꺼낸다
        role_permissions.remove(plan["permission"])              # 그 리스트에서 그 권한을 지운다
```

⑤ `execute_revocation` 안(미리 채운 `for` 아래)

```python
        if plan["approval"] == "승인 대기":                      # 승인을 기다리는 계획이면
            result = "대기"                                      # 실행하지 않고 대기로 남긴다
        else:                                                    # 승인 불필요이거나 승인됨이면
            apply_plan(plan, users, roles, exceptions)           # 실제로 회수한다
            result = "실행"                                      # 실행했다고 남긴다
```

**결과**

- (가) 출력은 다음과 같고, **실행 7건 · 대기 1건**입니다.
  - 대기는 아직 승인되지 않은 junho 의 `SALES:CHANGE`(예외 2번)입니다.
  - 판정이 바뀐 것은 **junho 의 `SALES:QUERY` 1건**(허용 → 거부)이고, 저장한 이력은 **8건**입니다.

```
--- 단계 1: 실행 - 회수 결과
junho SALES:QUERY | 역할에서 권한 빼기 | 실행
dami SALES:QUERY | 역할 해제 | 실행
dami SALES:CHANGE | 역할 해제 | 실행
seoyeon SETTLE:QUERY | 예외 삭제 | 실행
junho SALES:CHANGE | 예외 삭제 | 대기
dami SALES:QUERY | 예외 삭제 | 실행
batch-night SALES:QUERY | 예외 삭제 | 실행
gaeun SETTLE:QUERY | 예외 삭제 | 실행
실행 7 건, 대기 1 건
--- 단계 2: 확인 - 회수 전후의 판정
junho SALES:QUERY | 허용(역할 권한) -> 거부(권한 없음) | 바뀜
dami SALES:QUERY | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
dami SALES:CHANGE | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
seoyeon SETTLE:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
junho SALES:CHANGE | 거부(권한 없음) -> 거부(권한 없음) | 그대로
dami SALES:QUERY | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
batch-night SALES:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
gaeun SETTLE:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
--- 단계 3: 저장 - 회수 이력
저장 8 건, 다시 읽은 건수 8 건, 첫 이력: junho SALES:QUERY 실행
```

- (나) 실행한 7건 가운데 나머지 6건은 회수 전에도 이미 거부였습니다. 퇴사한 계정(dami 세 건)은 사용자 파일의 재직 표시 때문에, 예외 세 건(seoyeon 1번 · batch-night 4번 · gaeun 5번)은 만료 시각이 지난 예외라 출력에서도 거부(권한 없음)로 나옵니다. 그래도 회수하고 이력을 남기는 이유는 ① 데이터에 남아 있으면 퇴사자의 재직 표시가 잘못 바뀌거나 예외 만료 시각이 고쳐질 때 다시 허용될 수 있고 ② 점검에 같은 권한이 계속 나와 담당자가 거듭 확인해야 하고 ③ 정리하지 않은 권한이 남아 있으면 감사에서 문제가 되기 때문입니다. 실제로 위험을 줄인 것은 허용되던 junho 의 `SALES:QUERY` 한 건입니다.
- (다) 이 이력만으로는 부족합니다.
  - 「이 권한이 왜 없어졌나요?」에 답하려면 ① 회수 이유(퇴사 · 만료 · 90일 미사용 중 무엇 때문인지. 어제 점검 결과의 `reasons` 키에 적혀 있습니다) ② 승인한 사람의 이름 ③ 승인한 시각이 있어야 합니다.
  - 지금 이력에는 승인 상태(`승인됨`)만 있고 누가 승인했는지와 회수 이유가 없습니다.
  - `revoke_reason`(회수 이유) · `approver`(승인한 사람) · `approved_at`(승인한 시각) 키를 추가하면 됩니다.
  - 다만 승인한 사람을 남기려면 보안 책임자의 결정(`decisions`)에 사람 이름도 함께 적어 두어야 합니다.
  - 지금 결정에는 「승인」이라는 문자열만 있습니다.

**왜**

- 회수는 실행한 뒤에 다시 판정해 보아야 효과를 압니다.
  - 실행한 7건 중 6건은 회수 전에도 이미 막혀 있어서 판정이 바뀌지 않았고, 이력은 「막혀 있던 권한까지 정리했다」는 증거입니다.
  - 이력이 있어야 나중에 누가 언제 무엇을 왜 없앴는지 설명할 수 있습니다.

**자주 틀리는 곳**

- `if plan["approval"] == "승인 대기":` 검사를 빼고 모든 계획을 실행하면, 아직 승인되지 않은 junho 의 예외 2번까지 지워집니다.
  - 오류는 나지 않고 건수만 달라집니다.
  - 실행하면 다음처럼 됩니다(`실행 8 건, 대기 0 건` 이 나오면 이 실수입니다).

```
--- 단계 1: 실행 - 회수 결과
junho SALES:QUERY | 역할에서 권한 빼기 | 실행
dami SALES:QUERY | 역할 해제 | 실행
dami SALES:CHANGE | 역할 해제 | 실행
seoyeon SETTLE:QUERY | 예외 삭제 | 실행
junho SALES:CHANGE | 예외 삭제 | 실행
dami SALES:QUERY | 예외 삭제 | 실행
batch-night SALES:QUERY | 예외 삭제 | 실행
gaeun SETTLE:QUERY | 예외 삭제 | 실행
실행 8 건, 대기 0 건
--- 단계 2: 확인 - 회수 전후의 판정
junho SALES:QUERY | 허용(역할 권한) -> 거부(권한 없음) | 바뀜
dami SALES:QUERY | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
dami SALES:CHANGE | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
seoyeon SETTLE:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
junho SALES:CHANGE | 거부(권한 없음) -> 거부(권한 없음) | 그대로
dami SALES:QUERY | 거부(퇴사한 계정) -> 거부(퇴사한 계정) | 그대로
batch-night SALES:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
gaeun SETTLE:QUERY | 거부(권한 없음) -> 거부(권한 없음) | 그대로
--- 단계 3: 저장 - 회수 이력
저장 8 건, 다시 읽은 건수 8 건, 첫 이력: junho SALES:QUERY 실행
```

**관제에서는**

- 회수 이력은 지우지 않고 보관하고, 승인 대기가 길어지는 계획은 담당자에게 알립니다.
  - 회수한 뒤 다시 판정해서 막혔는지 확인하는 점검을 정기적으로 돌립니다.

---

### 앞 교시 파일 완성본

앞 교시 파일이 없거나 잘 안 될 때 이 코드로 만듭니다. 어제(10/29(목)) 파일이 필요하면 10/29(목) 오전 · 오후 문서 맨 아래의 「앞 교시 파일 완성본」을 씁니다.

**`revoke_input.py`** (2교시 도우미)

```python
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from review_list import build_access_list                        # 10/29(목) 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 10/29(목) 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 10/29(목) 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report                        # 10/29(목) 5교시에 만든 리포트 함수를 불러온다
from report_exclude import load_exclude_map, split_by_exclude    # 10/29(목) 6교시에 만든 회수 제외 함수를 불러온다

REVIEW_TIME = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")   # 어제 점검한 시각(고정). 같은 결과를 얻으려고 어제 시각을 쓴다
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 문자열의 형식


def load_to_revoke():                                            # 어제 점검 결과를 다시 만드는 함수
    """어제(10/29(목)) 5 · 6교시와 같은 방법으로 점검해서 「회수 대상」 리스트(8건)를 리턴한다."""
    access_list = build_access_list()                            # 현황을 만든다
    stale = find_stale(access_list, REVIEW_TIME)                 # 규칙에 걸린 권한을 찾는다
    last_used_map = load_last_used()                             # 마지막 사용 시각 딕셔너리를 읽는다
    unused = find_unused(access_list, last_used_map, REVIEW_TIME, 90)  # 90일 넘게 안 쓴 권한을 찾는다
    generated_at = REVIEW_TIME.strftime(TIME_FORMAT)             # 리포트를 만든 시각을 문자열로 바꾼다
    report = generate_report(access_list, stale, unused, 90, generated_at)  # 후보 리포트를 만든다
    exclude_map = load_exclude_map("config/exclude_list.json")   # 회수 제외 리스트를 읽는다
    to_revoke, excluded = split_by_exclude(report["findings"], exclude_map)   # 후보를 회수 대상과 회수 제외로 나눈다
    return to_revoke                                             # 회수 대상 리스트만 리턴한다
```

**`revoke_plan.py`** (2교시 완성본)

```python
def exception_id(source):                                        # "예외 3번" 모양 문자열을 받는 함수
    """"예외 3번" 모양 문자열에서 예외 번호(3)를 꺼내 숫자로 리턴한다."""
    number_text = source.replace("예외 ", "")                      # "예외 3번" 에서 "예외 " 를 지워 "3번" 으로 만든다
    number_text = number_text.replace("번", "")                   # "번" 을 지워 "3" 으로 만든다
    return int(number_text)                                      # 문자열 "3" 을 숫자 3 으로 바꿔 리턴한다


def count_users_by_role(users):                                  # 사용자 딕셔너리를 받는 함수
    """역할마다 사용자가 몇 명인지 센 딕셔너리를 리턴한다(재직 여부와 상관없이 센다). 예: {"finance": 1, "sales": 2}"""
    counts = {}                                                  # 역할 → 사용자 수를 담을 빈 딕셔너리
    for info in users.values():                                  # 사용자 정보를 하나씩 꺼낸다(.values() 는 딕셔너리의 값만 꺼낸다)
        role = info["role"]                                      # 그 사용자의 역할
        old_count = counts.get(role, 0)                          # 그 키의 지금까지 센 수(처음이면 0)
        counts[role] = old_count + 1                             # 1 늘려서 다시 적는다
    return counts                                                # 역할별 사용자 수를 리턴한다


def make_plan(finding, method, target, impact):                  # 회수 대상 · 방법 · 대상 · 영향 범위를 받는 함수
    """회수 대상을 복사해 method · target · impact 키를 추가한 계획 한 건을 리턴한다. impact 는 이 회수로 사라지는 (사용자, 권한)의 수다."""
    plan = finding.copy()                                        # 원래 권한은 바꾸지 않고 복사한다
    plan["method"] = method                                      # 회수 방법을 적는다
    plan["target"] = target                                      # 실제로 지울 대상(예외 번호 · 사용자 · 역할)을 적는다
    plan["impact"] = impact                                      # 사라지는 (사용자, 권한)의 수를 적는다
    return plan                                                  # 계획 한 건을 리턴한다


def build_plan(finding, method, users, roles, role_counts):      # 회수 대상 한 건 · 회수 방법 · 사용자 · 역할 · 역할별 사용자 수를 받는 함수
    """회수 방법에 맞게 지울 대상(target)과 영향(impact)을 정해 계획 한 건을 리턴한다."""
    info = users[finding["user"]]                                # 그 사용자의 정보를 꺼낸다
    if method == "예외 삭제":                                    # 방법이 예외 삭제이면
        target = exception_id(finding["source"])                 # 지울 대상은 예외 번호
        return make_plan(finding, method, target, 1)             # 영향은 권한 1건
    if method == "역할 해제":                                    # 방법이 역할 해제이면
        role_permissions = roles[info["role"]]                   # 그 사용자의 역할에 든 권한 리스트
        impact = len(role_permissions)                           # 영향은 그 역할에 든 권한 수
        return make_plan(finding, method, finding["user"], impact)  # 지울 대상은 그 사용자의 이름
    impact = role_counts[info["role"]]                           # 역할에서 권한 빼기: 영향은 그 역할을 가진 사용자 수(각자 그 권한 1건을 잃는다)
    return make_plan(finding, method, info["role"], impact)      # 지울 대상은 역할 이름


def plan_revocation(findings, users, roles):                     # 회수 대상 리스트 · 사용자 딕셔너리 · 역할 딕셔너리를 받는 함수
    """회수 대상마다 회수 방법을 정해 계획 리스트를 리턴한다. 실제로는 아무것도 지우지 않는다."""
    role_counts = count_users_by_role(users)                     # 역할마다 사용자가 몇 명인지 센다(반복 전에 한 번만)
    plans = []                                                   # 계획을 담을 빈 리스트
    for finding in findings:                                     # 회수 대상을 하나씩 꺼낸다
        info = users[finding["user"]]                            # 그 사용자의 정보를 꺼낸다
        if "예외" in finding["source"]:                          # 예외로 받은 권한이면
            method = "예외 삭제"                                 # 그 예외를 지운다
        elif not info["employed"]:                               # 퇴사한 사용자의 역할 권한이면
            method = "역할 해제"                                 # 그 사용자의 역할을 해제한다
        else:                                                    # 재직 중인 사용자의 역할 권한이면
            method = "역할에서 권한 빼기"                        # 역할에서 그 권한을 뺀다
        plan = build_plan(finding, method, users, roles, role_counts)  # 계획 한 건을 만든다
        plans.append(plan)                                       # 방법에 맞는 계획을 만들어 계획 리스트에 추가한다
    return plans                                                 # 계획 리스트를 리턴한다
```

**`revoke_approve.py`** (3교시 완성본)

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def load_sensitive(path):                                        # 민감한 권한 파일 경로를 받는 함수
    """민감한 권한 파일을 읽어 「자원:행위」 문자열의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽어 그대로 리턴한다


def plan_key(plan):                                              # 계획 한 건을 받는 함수
    """「사용자:권한」 문자열(예: "dami:SALES:CHANGE")을 리턴한다. 승인 결정을 찾는 키로 쓴다."""
    user = plan["user"]                                          # 계획의 사용자
    permission = plan["permission"]                              # 계획의 권한
    return f"{user}:{permission}"                                # 사용자와 권한을 : 로 이어 붙인다


def needs_approval(plan, sensitive):                             # 계획 한 건과 민감한 권한 리스트를 받는 함수
    """민감한 권한이거나 영향이 2건 이상이면 True, 아니면 False 를 리턴한다."""
    is_sensitive = plan["permission"] in sensitive               # 권한이 민감한 권한 리스트에 있는지(True 또는 False)
    is_big_impact = plan["impact"] >= 2                          # 영향이 2건 이상인지(True 또는 False)
    return is_sensitive or is_big_impact                         # 둘 중 하나라도 참이면 True 를 리턴한다


def mark_approvals(plans, sensitive, decisions):                 # 계획 리스트 · 민감한 권한 리스트 · 승인 결정 딕셔너리를 받는 함수
    """계획마다 "approval" 키(승인 상태)를 적은 복사본 리스트를 리턴한다. 승인 상태는 「승인 불필요」 · 「승인됨」 · 「승인 대기」 중 하나다."""
    results = []                                                 # 결과를 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        item = plan.copy()                                       # 원래 계획은 바꾸지 않고 복사한다
        key = plan_key(plan)                                     # 승인 결정을 찾는 「사용자:권한」 문자열을 만든다
        decision = decisions.get(key)                            # 보안 책임자의 결정을 꺼낸다(결정이 없으면 None)
        needs = needs_approval(plan, sensitive)                  # 승인이 필요한 계획인지 알아본다(True 또는 False)
        if not needs:                                            # 승인이 필요하지 않은 계획이면
            item["approval"] = "승인 불필요"                     # 승인 불필요라고 적는다
        elif decision == "승인":                                  # 승인이 필요하고, 보안 책임자가 승인하기로 결정한 계획이면
            item["approval"] = "승인됨"                          # 승인됨이라고 적는다
        else:                                                    # 승인이 필요한데 아직 결정이 없으면
            item["approval"] = "승인 대기"                       # 승인 대기라고 적는다
        results.append(item)                                     # 결과 리스트에 추가한다
    return results                                               # 결과 리스트를 리턴한다
```

**`config/sensitive.json`** (3교시 완성본)

```json
["SALES:CHANGE", "ACCOUNT:CHANGE", "SETTLE:CHANGE"]
```

**`revoke.py`** (4교시 완성본)

```python
import json                                                      # JSON 파일을 쓰는 모듈을 불러온다


def remove_exception(exceptions, target_id):                     # 예외 리스트와 지울 예외 번호를 받는 함수
    """예외 리스트에서 번호가 target_id 인 예외 한 건을 지운다. 지웠으면 True, 못 찾았으면 False 를 리턴한다."""
    for exc in exceptions:                                       # 예외를 하나씩 꺼낸다
        if exc["id"] == target_id:                               # 번호가 같으면
            exceptions.remove(exc)                               # 리스트에서 그 예외를 지운다
            return True                                          # 지웠다고 알리고 함수를 끝낸다
    return False                                                 # 끝까지 못 찾았으면 False 를 리턴한다


def apply_plan(plan, users, roles, exceptions):                  # 계획 한 건 · 사용자 · 역할 · 예외 리스트를 받는 함수
    """계획 한 건의 회수 방법대로 프로그램 안의 데이터를 실제로 바꾼다. 승인 상태는 보지 않는다(승인 확인은 호출하는 쪽이 한다)."""
    if plan["method"] == "예외 삭제":                            # 방법이 예외 삭제이면
        remove_exception(exceptions, plan["target"])             # 예외 리스트에서 그 번호의 예외를 지운다
    elif plan["method"] == "역할 해제":                          # 방법이 역할 해제이면
        user_info = users[plan["target"]]                        # 그 사용자의 정보 딕셔너리를 꺼낸다
        user_info["role"] = ""                                   # 역할을 빈 문자열로 바꾼다(어떤 역할의 권한도 받지 않게 된다)
    else:                                                        # 방법이 역할에서 권한 빼기이면
        role_permissions = roles[plan["target"]]                 # 그 역할의 권한 리스트를 꺼낸다
        role_permissions.remove(plan["permission"])              # 그 리스트에서 그 권한을 지운다


def save_log(log, path):                                         # 이력 리스트와 저장할 파일 경로를 받는 함수
    """이력 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다. 한글이 그대로 보이게 쓴다."""
    with open(path, "w", encoding="utf-8") as f:                 # 파일을 쓰기 모드("w")로 연다
        json.dump(log, f, ensure_ascii=False, indent=2)          # 이력을 파일에 JSON 으로 쓴다
    return len(log)                                              # 저장한 건수를 리턴한다


def execute_revocation(plans, users, roles, exceptions, now):    # 계획 · 사용자 · 역할 · 예외 리스트 · 지금 시각 문자열을 받는 함수
    """승인 불필요이거나 승인됨인 계획만 실제로 실행하고, 이력 리스트를 리턴한다. 승인 대기인 계획은 실행하지 않고 이력에 「대기」로 남긴다."""
    log = []                                                     # 이력을 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        if plan["approval"] == "승인 대기":                      # 아직 승인을 기다리는 계획이면
            result = "대기"                                      # 실행하지 않고 대기로 남긴다
        else:                                                    # 승인 불필요이거나 승인된 계획이면
            apply_plan(plan, users, roles, exceptions)           # 실제로 회수한다
            result = "실행"                                      # 실행했다고 적는다
        entry = {
            "time": now,                                         # 시각
            "user": plan["user"],                                # 사용자
            "permission": plan["permission"],                    # 권한
            "method": plan["method"],                            # 회수 방법
            "approval": plan["approval"],                        # 승인 상태
            "result": result,                                    # 결과(실행 또는 대기)
        }
        log.append(entry)                                        # 이력 한 건을 이력 리스트에 추가한다
    return log                                                   # 이력 리스트를 리턴한다
```
