# 10/29(목) 오후 · 3과목 접근통제 ④ — 과다권한 종합 리포트 · 회수 제외 — 실습

오전에는 부여돼 있는 권한의 **현황 목록**을 만들고, 거기서 필요 없어진 권한을 **규칙**(퇴사 · 만료)과 **사용 이력**(90일 넘게 안 씀)으로 찾았습니다. 오후에는 그 결과들을 한 장의 **과다권한 리포트**로 합치고, 회수하지 않을 권한을 가려냅니다.

- **5교시**: 규칙으로 찾은 것과 사용 이력으로 찾은 것을 합쳐 **리포트**를 만든다(후보마다 이유 목록).
- **6교시**: 후보 가운데 평소에 안 써도 되는 권한을 **회수 제외 목록**으로 가려내 「회수 대상」과 「회수 제외」로 나눈다. 마지막 10분에 오늘 만든 것을 깃허브에 올립니다.

오늘 오후도 **찾기와 기록까지만** 하고, 실제로 회수하는 일은 내일(10/30(금)) 합니다. 교시마다 문제는 하나입니다.

> 📦 **앞 수업에 결석했거나 파일이 없다면**: 오전 문서(`day04_am_access_review.md`) 맨 위의 안내처럼 수업 자료의 `day02_recovery` 폴더(10/21(수) ~ 10/22(목) 파일의 완성본)로 먼저 준비하고, 오전 파일은 오전 문서 맨 아래 「앞 교시 파일 완성본」으로 만듭니다. 넣는 방법은 아래 「시작하기」 2번에 있습니다.

**📎 오늘 불러 쓰는 이전 파일** — 오늘 코드가 `import` 로 가져다 쓰는 앞 수업 파일입니다. 없으면 오른쪽 열의 방법으로 먼저 준비합니다.

| 파일 | 만든 날 | 오늘 가져다 쓰는 것 | 쓰는 교시 | 없으면 |
|---|---|---|---|---|
| `review_list.py` | 10/29(목) 오전 2교시 | `build_access_list` | 5 · 6교시 | 오전 문서 맨 아래 「앞 교시 파일 완성본」 |
| `review_rules.py` | 10/29(목) 오전 3교시 | `find_stale` | 5 · 6교시 | 오전 문서 맨 아래 「앞 교시 파일 완성본」 |
| `review_unused.py` · `config/access_log.json` | 10/29(목) 오전 4교시 | `load_last_used` · `find_unused` (사용 이력) | 5 · 6교시 | 오전 문서 맨 아래 「앞 교시 파일 완성본」 |
| `config_loader.py` | 10/22(목) | `load_json` | 6교시 | `day02_recovery` 폴더 |

- 오전 파일(`review_list.py` 등)이 10/21(수) ~ 10/22(목)의 `rbac.py` · `exception_policy.py` · `config_loader.py` 를 다시 가져다 쓰므로, 그 파일들도 있어야 합니다. 없으면 `day02_recovery` 폴더를 씁니다.
- 오늘 만드는 파일도 뒤 교시가 가져다 씁니다. 5교시 `overprivilege.py` 는 6교시에서 씁니다.

## 시작하기

1. **[VS Code]** 왼쪽 목록의 `access_control` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 위치와 오전 파일을 확인합니다. 결과가 `…/security-agent-toolkit/access_control` 로 끝나야 합니다.
   ```bash
   pwd
   ls
   ls config
   python -c "from review_list import build_access_list; from review_rules import find_stale; from review_unused import load_last_used, find_unused; print('오전 파일 정상', len(build_access_list()), len(load_last_used()))"
   ```
   - 맥북은 맨 앞의 `python` 을 `python3` 로 바꿔 칩니다. 따옴표 안의 글은 같습니다.
   - `review_list.py` · `review_rules.py` · `review_unused.py` 가 보이고, `config` 안에 `access_log.json` 이 보여야 합니다.
   - 마지막 줄에 `오전 파일 정상 14 7` 이 나와야 합니다. 뒤의 숫자는 현황 14건, 사용 이력 7건입니다.
   - 아니면 오전 문서(`day04_am_access_review.md`) 맨 아래 「앞 교시 파일 완성본」으로 `review_list.py` · `review_rules.py` · `review_unused.py` 와 `config/access_log.json` 을 만듭니다. 10/21(수) · 10/22(목) 파일이 없으면 수업 자료로 받은 `day02_recovery` 폴더에서 넣습니다.
3. **오늘 받은 파일 두 개를 `access_control` 폴더로 옮깁니다.** 수업 자료에서 내려받은 파일은 보통 `다운로드` 폴더에 있습니다. 파일 탐색기(맥북은 Finder)에서 `다운로드` 폴더를 열고, 두 파일을 VS Code 왼쪽 목록의 `access_control` 폴더 위로 끌어다 놓습니다. 끌어다 놓기가 안 되면 파일을 VS Code 로 열고 메뉴 **File › Save As…** 로 `access_control` 폴더에 저장합니다.
   - `day04_pm_overprivilege.md` (이 파일) — 오후 실습 안내. 읽기만 합니다.
   - `day04_pm_report.md` — **오후 보고서.** 5 · 6교시 답과 마무리 칸을 여기에 적습니다.
4. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다. 이 문서가 미리보기로 열립니다.
5. **[VS Code]** `day04_pm_report.md` 를 오른쪽 클릭 › **Open to the Side** (보고서가 화면 오른쪽 칸에 열립니다). 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다. 코드나 출력을 붙여 넣는 질문은 `답:` 아래의 빈 코드 상자 안에 붙여 넣습니다. 보고서 맨 위 제목 `(이름 · 2026-10-29(목))` 에서 `이름` 두 글자만 내 이름으로 바꿉니다.
6. 문제는 **할 일 → 순서**대로 합니다.
   - 순서 앞의 `[창 이름]` 이 지금 쓸 창이고, `[창 이름]` 이 없는 단계는 안내를 읽고 생각하는 단계입니다.
   - 「🔍」가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이며, 이유까지 설명합니다. 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다.
   - 막히면 문서 맨 아래 「정답」을 봅니다.
   - 코드를 채우는 문제는 **줄 수가 정해져 있지 않습니다.** 주석이 말하는 일(로직)을 하면 몇 줄로 쓰든 맞습니다.

> 실행은 **터미널**에서 합니다(VS Code 의 ▶ 단추를 쓰지 않습니다). `python` 이 없다는 오류가 나오면 `python3` 으로 칩니다(맥북은 `python3`). **오전까지 만든 파일은 고치지 않습니다.** 오늘 만드는 파일은 모두 새 파일입니다. 앞 교시 파일이 없으면 문서 맨 아래 「앞 교시 파일 완성본」(5 · 6교시 파일)과 오전 문서의 완성본으로 먼저 만듭니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 점검 결과를 한 장의 리포트로 합치기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「월요일 보안 회의에서 팀장님이 "점검 결과는 한 장만 보면 되게 해 주세요"라고 하셨습니다. 지금은 규칙으로 걸린 목록과 90일 넘게 안 쓴 목록이 따로 나옵니다. 같은 권한이 두 목록에 모두 나올 수도 있어서, 합치면 후보가 몇 건인지 저도 바로 말하지 못합니다.
>
> 후보 권한마다 어떤 이유로 걸렸는지를 권한 한 건에 모은, 한 장짜리 리포트를 만들어 주세요.」
> - **왜 중요한가**: 목록이 둘로 나뉘어 있으면 같은 권한이 양쪽에 있어도 알아보기 어려워서, 후보가 몇 건인지 말할 수 없습니다. 이유까지 권한 한 건에 모은 리포트 한 장이 있으면, 그 한 장만 보고 어떤 권한을 회수할지 정할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 규칙으로 찾은 결과와 90일 넘게 안 쓴 권한을 찾은 결과가 따로 나오면, 담당자가 같은 권한이 두 곳에 나오는지 직접 맞춰 봐야 합니다. 두 결과를 합쳐 모은 것이 **후보**이고, 후보는 업무에 필요한 것보다 많이 가진 권한, 곧 **과다권한**(over-privilege · 오버 프리빌리지)일 수 있는 권한입니다.
2. 후보 하나에 걸린 **이유**를 붙여 한곳에 모읍니다.
3. 오늘 리포트는 **리포트 한 장 = 딕셔너리 하나**입니다. 여기서 「리포트」는 프로그램이 만드는 점검 결과이고, 「보고서」는 내가 답을 적는 `day04_pm_report.md` 입니다.
4. 오전 4교시에서는 규칙에 걸린 권한을 빼고 안 쓴 권한을 찾았지만, 오늘은 **전체 현황**에 두 점검을 따로 돌립니다. 그래서 권한 한 건이 두 이유에 모두 걸릴 수 있고, 안 쓴 권한도 오전보다 더 많이 나옵니다. 코드가 틀려서가 아니라 규칙에 걸린 권한도 함께 검사하기 때문입니다.

### 📖 5.1 리포트의 모양

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 리포트의 키 | 뜻 | 값의 예 |
|---|---|---|
| `generated_at` | 리포트를 만든 시각 | `"2026-10-29 14:00"` |
| `total` | 점검한 권한 수 (현황의 권한 수) | `14` |
| `finding_count` | 후보 수 | `10` |
| `findings` | 후보 목록. 후보 한 건 = 현황의 권한 한 건 + `reasons` 키 | `[{…}, {…}]` |

- 「90일 넘게 안 씀(이력 없음 포함)」은 사용 이력이 아예 없는 권한도 이 이유에 넣는다는 뜻입니다.
- `reasons` 는 이유 글자의 **목록**입니다. 규칙에 걸렸으면 그 이유(`"퇴사한 계정"` 등)가, 오래 안 썼으면 `"90일 넘게 안 씀(이력 없음 포함)"` 이 들어갑니다. 이유가 하나도 없는 권한은 후보가 아니므로 `findings` 에 넣지 않습니다.
- 「90일 넘게」는 오전과 같은 기준입니다. 마지막으로 쓴 뒤 지난 일 수가 91일 이상이거나 사용 이력이 없으면 해당합니다.
- `stale`(스테일)은 「오래돼서 쓸모없어진」이라는 뜻으로, 퇴사 · 만료로 필요 없어진 권한을 말합니다. 변수 `stale` 은 오전 3교시 `find_stale` 이 리턴한 「규칙에 걸린 권한」 목록이고(여기서 「걸렸다」는 퇴사 · 만료 규칙에 해당한다는 뜻), `unused` 는 오전 4교시 `find_unused` 가 리턴한 「90일 넘게 안 쓴 권한」 목록입니다.
- 오늘 새로 하는 것은 두 점검 결과를 권한 한 건마다 하나의 `reasons` 목록으로 합치는 것입니다. 복사해서 키를 추가하는 `entry.copy()` 는 오전 3교시, 글자로 이어 붙인 키로 찾는 방법은 오전 4교시와 같습니다.

**식별 키**

- 현황의 **권한 한 건**(`entry`)은 사용자 한 명의 권한 하나입니다. `stale` 과 `unused` 의 권한은 현황의 권한을 **복사해서 `reason` 이나 `last_used` 키를 추가한 것**이라, 현황의 원래 권한과 `==` 로 비교하면 서로 다르다고 나옵니다. `user` · `permission` · `source` 세 값을 하나씩 비교해도 되지만, 세 값을 `:` 로 이어 붙여 글자 하나로 만들면 딕셔너리의 키로 쓸 수 있어서 `key in stale_reason` 한 번으로 찾을 수 있습니다. 이 글자를 **식별 키**(identification key · 아이덴티피케이션 키)라고 부릅니다. 현황의 권한 한 건을 다른 권한과 구별하는 글자입니다. 오전 4교시 실행 파일에서도 같은 방법으로 규칙에 걸린 권한을 뺐습니다.
- 현황에서 dami 의 `SALES:QUERY` 는 역할로도, 예외로도 부여돼 있어서 서로 다른 두 건이고, 식별 키도 서로 달라야 합니다.

| 현황의 권한 한 건 (`entry`) | 식별 키 (`entry_key(entry)` 가 리턴하는 글자) |
|---|---|
| `user` dami · `permission` SALES:QUERY · `source` 역할 sales | `"dami:SALES:QUERY:역할 sales"` |
| `user` dami · `permission` SALES:QUERY · `source` 예외 3번 | `"dami:SALES:QUERY:예외 3번"` |

- 오늘 데이터에서는 이 두 건의 점검 결과가 같아서(둘 다 「퇴사한 계정」) `source` 가 없어도 출력은 같습니다. 하지만 한쪽 권한만 만료되는 날처럼 두 건의 결과가 다르면, `source` 가 없을 때 한쪽 이유가 다른 쪽 권한에도 붙어 후보가 잘못 나옵니다.

**미리 채워 둔 함수와 리포트의 이름들**

- `reason`(글자 하나, 규칙 결과에 있는 이유)과 `reasons`(목록, 오늘 후보에 적는 이유들)는 한 글자 차이입니다. 후보에는 `reasons` 를 씁니다.
- `findings`(파인딩스)는 「찾아낸 것들」, 곧 후보 목록입니다.
- `entry_key` 는 식별 키를 만드는 함수입니다.
- `make_stale_reason`(메이크 스테일 리즌)은 규칙에 걸린 권한의 「식별 키 → 걸린 이유」 딕셔너리를 리턴합니다. 예: `{"dami:SALES:QUERY:역할 sales": "퇴사한 계정", "dami:SALES:CHANGE:역할 sales": "퇴사한 계정", …}`
- `make_unused_keys`(메이크 언유즈드 키즈)는 90일 넘게 안 쓴 권한의 식별 키 목록을 리턴합니다. 예: `["seoyeon:SALES:CHANGE:역할 sales", "junho:SALES:QUERY:역할 finance", …]`
- 이 두 함수는 `generate_report` 의 처음 두 줄에서 이미 불러 두었습니다.
- 직접 쓰는 것은 `generate_report` 의 나머지(후보를 모으는 반복문)입니다.
- 실행 파일은 이유 목록을 한 줄로 출력할 때 `", ".join(목록)` 을 씁니다. 목록의 글자들을 쉼표로 이어 붙여 하나의 글자로 만드는 것입니다.

```
+-----------------------------------------------------------------+
| generate_report(access_list, stale, unused, days, generated_at) |
+-----------------------------------------------------------------+
   |
   v
+----------------------------------------------------------------------------------------------------+
| stale_reason = make_stale_reason(stale), unused_keys = make_unused_keys(unused)  (미리 채운 두 줄) |
+----------------------------------------------------------------------------------------------------+
   |
   v
+-----------------------------------+
| findings = []  (후보를 담을 목록) |
+-----------------------------------+
   |
   v
+----------------------------------------------------------------------------+
| 현황의 권한을 한 건씩 꺼내 식별 키(key)를 만들고, reasons = [] 로 시작한다 |
+----------------------------------------------------------------------------+
   |
   v
+------------------------------+
| key 가 stale_reason 에 있나? |
+------------------------------+
   |
   +--> 있다 --> reasons 에 걸린 이유를 추가한다
   |
   v  (이어서)
+-----------------------------+
| key 가 unused_keys 에 있나? |
+-----------------------------+
   |
   +--> 있다 --> reasons 에 「N일 넘게 안 씀」을 추가한다
   |
   v  (이어서)
+----------------------------------------------+
| reasons 가 하나라도 있나? (len(reasons) > 0) |
+----------------------------------------------+
   |
   +--> 없다 --> 후보가 아니므로 다음 권한으로
   |
   v  있다
+------------------------------------------------------+
| 권한을 복사해 reasons 키를 적고 findings 에 추가한다 |
+------------------------------------------------------+
   |
   v  모든 권한을 꺼낸 뒤
리포트 딕셔너리(generated_at · total · finding_count · findings)를 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 규칙 결과와 안 쓴 결과를 합쳐 과다권한 후보 리포트 만들기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 규칙에 걸린 권한과 90일 넘게 안 쓴 권한이 따로 출력됩니다. 같은 권한이 두 점검에 모두 걸릴 수도 있어서, 담당자가 둘을 합쳐 「후보가 모두 몇 건이고 왜 걸렸나」를 직접 정리해야 합니다.
- **그래서 만드는 것**: `generate_report` 입니다. 현황의 권한을 하나씩 보면서, 규칙에 걸렸거나 안 쓴 권한이면 이유를 `reasons` 목록에 담아 후보로 모으고, 리포트 딕셔너리로 리턴합니다.
- **실행하면**: 단계 1은 리포트 요약 한 줄과 후보를 이유와 함께 한 줄씩 출력하고, 단계 2는 후보가 아닌 권한을 출력합니다. 실행 파일은 현황 전체에 규칙 점검과 안 쓴 권한 점검을 따로 돌립니다. 지금 시각은 `2026-10-29 14:00` 으로 고정합니다.
- **현업에서는**: 접근 점검 도구도 여러 점검 결과를 한 장의 리포트로 합쳐 담당자에게 보냅니다.

**🎯 할 일**

1. `overprivilege.py` 와 `day04_5-1_run.py` 두 파일을 만들고, `generate_report` 본문을 직접 씁니다.
2. 실행해서 <mark>리포트 요약과 후보</mark>(단계 1: 요약)와 <mark>후보가 아닌 권한</mark>(단계 2: 확인)을 읽습니다.

**`overprivilege.py`**

```python
def entry_key(entry):                                            # 현황의 권한 한 건의 식별 키를 만드는 함수
    """현황의 권한 한 건(또는 그 복사본)의 식별 키(user:permission:source 를 이어 붙인 글자)를 리턴한다."""
    return entry["user"] + ":" + entry["permission"] + ":" + entry["source"]   # 세 값을 : 로 이어 붙인다


def make_stale_reason(stale):                                    # 규칙에 걸린 권한 목록을 받는 함수
    """규칙에 걸린 권한의 식별 키를 키로, 걸린 이유를 값으로 하는 딕셔너리를 리턴한다."""
    stale_reason = {}                                            # 식별 키 → 걸린 이유를 담을 빈 딕셔너리
    for item in stale:                                           # 규칙에 걸린 권한을 하나씩 꺼낸다
        stale_reason[entry_key(item)] = item["reason"]           # 식별 키로 걸린 이유를 찾을 수 있게 담는다
    return stale_reason                                          # 딕셔너리를 리턴한다


def make_unused_keys(unused):                                    # 안 쓴 권한 목록을 받는 함수
    """안 쓴 권한의 식별 키를 담은 목록을 리턴한다."""
    unused_keys = []                                             # 안 쓴 권한의 식별 키를 담을 빈 목록
    for item in unused:                                          # 안 쓴 권한을 하나씩 꺼낸다
        unused_keys.append(entry_key(item))                      # 식별 키를 목록에 추가한다
    return unused_keys                                           # 목록을 리턴한다


def generate_report(access_list, stale, unused, days, generated_at):   # 현황 · 규칙 결과 · 안 쓴 결과 · 기준 일 수 · 만든 시각 글자를 받는 함수
    """과다권한 후보 리포트(딕셔너리)를 리턴한다. 후보마다 "reasons" 키에 이유 목록을 적는다."""
    stale_reason = make_stale_reason(stale)                      # 규칙에 걸린 권한의 식별 키 → 걸린 이유 딕셔너리를 만든다(미리 채움)
    unused_keys = make_unused_keys(unused)                       # 안 쓴 권한의 식별 키 목록을 만든다(미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 후보를 담을 빈 목록 findings 를 만든다
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    # 3.   entry_key(entry) 가 리턴하는 식별 키를 key 에 담는다
    # 4.   빈 목록 reasons 를 만든다
    # 5.   key 가 stale_reason 에 있으면 (in)
    # 6.     reasons 에 stale_reason[key] 를 추가한다
    # 7.   key 가 unused_keys 에 있으면 (in)
    # 8.     reasons 에 f"{days}일 넘게 안 씀(이력 없음 포함)" 을 추가한다
    # 9.   reasons 의 개수가 0 보다 크면 (len(reasons) > 0)
    # 10.    entry.copy() 를 finding 에 담는다
    # 11.    finding["reasons"] 를 reasons 로 정한다
    # 12.    findings 에 finding 을 추가한다
    # 13. 딕셔너리를 리턴한다: "generated_at" 은 generated_at, "total" 은 len(access_list), "finding_count" 는 len(findings), "findings" 는 findings

```

- `generate_report` 의 본문은 함수 안이라 앞에 공백 4개를 넣고(Tab 키 한 번), `for` 안쪽은 공백 4개 더(8개), `if` 안쪽은 또 4개 더(12개) 넣습니다.
- 5 · 6번은 규칙에 걸린 경우, 7 · 8번은 안 쓴 경우입니다. 둘 다 「이유가 있으면 `reasons` 에 추가한다」입니다. 마지막 13번 `return` 은 `for` 밖이므로 공백 4개입니다.
- `generate_report` 의 처음 두 줄(`stale_reason = …` · `unused_keys = …`)은 미리 채워 두었으니 그대로 둡니다.
- 채우기 전에 실행하면 `TypeError: 'NoneType' object is not subscriptable` 오류가 납니다. 함수가 아무것도 리턴하지 않아 `report["total"]` 을 꺼낼 수 없기 때문입니다.

**`day04_5-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 오전 함수로 현황과 규칙 결과, 안 쓴 결과를 만든 뒤 `generate_report` 로 리포트를 만들어 출력합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report, entry_key             # 방금 만든 리포트 함수와 식별 키 함수를 불러온다

NOW = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 글자의 형식

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다
unused = find_unused(access_list, load_last_used(), NOW, 90)     # 같은 현황에서 90일 넘게 안 쓴 권한을 찾는다(규칙에 걸린 권한도 빼지 않고 전부 넣는다)

report = generate_report(access_list, stale, unused, 90, NOW.strftime(TIME_FORMAT))   # 과다권한 후보 리포트를 만든다

print("--- 단계 1: 요약 - 점검", report["total"], "건 중 후보", report["finding_count"], "건 (", report["generated_at"], ")")   # 단계 1 시작을 알리는 줄
for finding in report["findings"]:                               # 후보를 한 건씩 꺼낸다
    print(finding["user"], finding["permission"], "<-", finding["source"], "|", ", ".join(finding["reasons"]))   # 사용자 · 권한 <- 출처 | 이유들을 출력한다

print("--- 단계 2: 확인 - 후보가 아닌 권한")                       # 단계 2 시작을 알리는 줄
finding_keys = []                                                # 후보의 식별 키를 담을 빈 목록
for finding in report["findings"]:                               # 후보를 하나씩 꺼내
    finding_keys.append(entry_key(finding))                      # 그 식별 키를 목록에 추가한다
names = []                                                       # 후보가 아닌 권한(「사용자 권한」 글자)을 담을 빈 목록
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    if entry_key(entry) not in finding_keys:                     # 식별 키가 후보 목록에 없으면
        names.append(entry["user"] + " " + entry["permission"])  # 사용자와 권한을 목록에 추가한다
print(names)                                                     # 후보가 아닌 권한을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `overprivilege.py` · `day04_5-1_run.py` 입니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널에서 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch overprivilege.py` → `touch day04_5-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim overprivilege.py` → `vim day04_5-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[VS Code]** `overprivilege.py` 의 `generate_report` 본문을 직접 씁니다. 5.1 의 표와 그림을 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 이어서 실행합니다.
   ```bash
   pwd
   python day04_5-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day04_5-1_run.py` 실행할 파일
   - 맥북은 `python3 day04_5-1_run.py` 로 칩니다.
4. 출력은 두 단계입니다. 단계 1은 요약 한 줄과 후보 한 줄씩, 단계 2는 후보가 아닌 권한 목록 한 줄입니다.
5. **[보고서]** `day04_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 후보가 모두 몇 건인지, 이유가 둘인 후보가 몇 건인지, 후보가 아닌 권한은 무엇인지 적어 주세요.
   - (나) 🔍 출력에서 이유가 둘인 후보를 하나 고르고, 이유가 둘이라는 것이 담당자가 처리 순서를 정할 때 어떤 도움이 되는지 적어 주세요. 이유를 글자(문자열) 하나가 아니라 목록(`reasons`)으로 담으면 어떤 점이 좋은지도 적어 주세요.
   - (다) 🔍 프로그램이 만든 리포트에는 후보만 담고, 후보가 아닌 권한은 전체 건수(`total`)로만 남겼습니다. 후보가 아닌 권한까지 모두 담는 방법과 비교해 담당자 입장에서 어느 쪽이 나은지 이유와 함께 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 권한의 식별 키 만들기 | `entry_key(entry)` (미리 채움) |
| 이유 목록 만들기 | `reasons = []` → 걸릴 때마다 `reasons.append(이유)` |
| 규칙에 걸렸는지 (딕셔너리의 키로 찾기) | `if key in stale_reason:` |
| 90일 넘게 안 썼는지 (목록에서 찾기) | `if key in unused_keys:` |
| 이유가 하나라도 있는지 | `if len(reasons) > 0:` |
| 후보 만들기 | `finding = entry.copy()` → `finding["reasons"] = reasons` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 회수하지 않을 권한을 가려내기</mark>

> 📨 **오늘 들어온 일**
>
> A사 관제 담당이 보낸 메시지:
> 「점검 결과 후보 10건 가운데 평소에 안 쓰는 것이 정상인 권한이 두 개 있습니다.
> - 가은의 `ACCOUNT:CHANGE`(계정 설정을 바꾸는 권한): 계정에 사고가 났을 때만 씁니다.
> - 서연의 `SALES:CHANGE`(영업 자료를 바꾸는 권한): 6월 말과 12월 말, 반년에 한 번 결산 때만 씁니다.
>
> 내일 권한을 회수할 때 이 두 권한까지 없어지면 필요한 날 일을 못 합니다. 회수하지 않을 권한은 파일에 적어 둘 테니, 후보를 「회수 대상」과 「회수 제외」로 나눠 주세요.」
> - **왜 중요한가**: 후보를 전부 회수하면, 가은은 계정에 사고가 난 날 서연은 결산하는 날 필요한 권한이 없어 일을 못 합니다. 그래서 회수하기 전에 「회수 제외」를 먼저 가려냅니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 5교시 리포트의 후보 10건은 「바로 회수할 권한」이 아니라 「확인이 필요한 권한」입니다.
2. 후보 중에는 평소에 안 써도 되는 권한이 있습니다. 담당자가 이런 권한을 **회수 제외 목록**(exclude list · 익스클루드 리스트, 줄여서 제외 목록)에 적어 두면, 프로그램이 후보를 「회수 대상」과 「회수 제외」로 나눕니다.
3. 단, 퇴사한 사람의 권한은 제외 목록에 있어도 제외하지 않습니다. 이미 회사에 없는 사람의 계정에 권한이 열려 있으면 다른 사람이 몰래 쓸 수 있어 위험하기 때문입니다.
4. 제외 목록은 사람이 적기 때문에 잘못 적을 수 있습니다. 목록에 있다는 이유만으로 무조건 믿으면, 퇴사한 사람의 권한처럼 제외하면 안 되는 것까지 남게 됩니다.

### 📖 6.1 회수 제외 목록의 모양

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`config/exclude_list.json` 의 한 건은 아래 세 키로 이루어집니다. 제외하는 기간을 적는 키는 없습니다.

| 키 | 뜻 | 값의 예 |
|---|---|---|
| `user` | 사용자 | `"gaeun"` |
| `permission` | 권한 | `"ACCOUNT:CHANGE"` |
| `reason` | 제외하는 이유 | `"계정에 사고가 났을 때만 쓰는 권한이라 평소에는 쓰지 않음"` |

- 오늘 목록에는 권한이 세 건 있습니다. 가은(`gaeun`) `ACCOUNT:CHANGE`, 서연(`seoyeon`) `SALES:CHANGE`, 다미(`dami`) `SALES:QUERY` 입니다. 메시지에는 두 개만 나왔고, 세 번째 다미 권한은 문제 (나)에서 다룹니다.
- 제외 목록과 후보는 「사용자:권한」 글자(예: `"gaeun:ACCOUNT:CHANGE"`)가 같은지 비교합니다. 5교시의 식별 키와 달리 `source`(역할인지 예외인지)는 붙이지 않습니다. 제외 목록은 어떻게 받은 권한이든 그 사람의 그 권한을 기준으로 적기 때문입니다.
- 미리 채워 둔 함수가 셋 있습니다. `exclude_key` 는 「사용자:권한」 글자를 만들고, `make_excluded` 는 후보를 복사해 `exclude_reason` 키(제외 이유)를 적은 복사본을 리턴하고, `load_exclude_map` 은 파일을 읽어 `{"gaeun:ACCOUNT:CHANGE": "계정에 사고가 …", …}` 모양의 딕셔너리(`exclude_map`, 제외 이유를 찾는 딕셔너리)를 리턴합니다. 직접 쓰는 것은 `split_by_exclude` 입니다.
- `reason`(제외 목록 파일에 적힌 제외 이유 글자)과 `reasons`(5교시 후보에 붙은 이유 목록)는 한 글자 차이이니 헷갈리지 마세요.
- `to_revoke`(투 리보크)는 회수 대상 목록, `excluded`(익스클루디드)는 제외된 후보 목록입니다. 두 목록은 `return to_revoke, excluded` 로 한꺼번에 리턴하고, 받는 쪽은 `to_revoke, excluded = …` 로 두 이름에 나눠 받습니다(리턴한 두 값이 차례로 두 이름에 들어갑니다).

```
+-----------------------------------------+
| split_by_exclude(findings, exclude_map) |
+-----------------------------------------+
   |
   v
+----------------------------------------------------------------+
| to_revoke = [] / excluded = []  (두 목록을 비워 두고 시작한다) |
+----------------------------------------------------------------+
   |
   v
+-------------------------------------------------------+
| 후보를 하나씩 꺼내 key(「사용자:권한」 글자)를 만든다 |
+-------------------------------------------------------+
   |
   v
+------------------------------------------------------------------------+
| key 가 exclude_map 에 있고, 후보의 이유 목록에 「퇴사한 계정」이 없나? |
+------------------------------------------------------------------------+
   |
   +--> 그렇다 --> 복사본에 exclude_reason 키를 적어 excluded 에 추가한다
   |
   +--> 아니다 --> 그대로 to_revoke 에 추가한다
   |
   v  모든 후보를 꺼낸 뒤
(to_revoke, excluded) 를 리턴한다
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 후보를 「회수 대상」과 「회수 제외」로 나누기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 5교시 리포트의 후보 10건이 한 목록에 섞여 있습니다. 회수하지 않을 권한을 담당자가 눈으로 골라야 합니다.
- **그래서 만드는 것**: `split_by_exclude` 입니다. 제외 목록에 있는 후보는 `exclude_reason` 키를 붙여 「회수 제외」로, 나머지는 「회수 대상」으로 나눕니다. 후보에 붙은 이유(`reasons`)에 「퇴사한 계정」이 있으면 제외 목록에 있어도 제외하지 않습니다.
- **실행하면**: 단계 1은 분류 건수, 단계 2는 회수 제외한 후보와 이유, 단계 3은 제외 목록에 있지만 회수 대상으로 남은 후보를 출력합니다.
- **현업에서는**: 자동 점검 도구도 회수 제외 목록을 두고, 비상용 권한이나 사람이 아닌 프로그램용 계정의 권한을 회수 대상에서 뺍니다.

**🎯 할 일**

1. `config/exclude_list.json` · `report_exclude.py` · `day04_6-1_run.py` 세 파일을 만들고, `split_by_exclude` 본문을 직접 씁니다.
2. 실행해서 <mark>분류 건수</mark>(단계 1: 분류), <mark>회수 제외한 후보</mark>(단계 2: 제외), <mark>회수 대상으로 남은 후보</mark>(단계 3: 확인)를 읽습니다.

**`config/exclude_list.json`** — 그대로 붙여 넣습니다. 회수 제외 목록입니다. `access_control` 안의 `config` 폴더에 만듭니다.

```json
[
  {"user": "gaeun", "permission": "ACCOUNT:CHANGE", "reason": "계정에 사고가 났을 때만 쓰는 권한이라 평소에는 쓰지 않음"},
  {"user": "seoyeon", "permission": "SALES:CHANGE", "reason": "6월 말 · 12월 말 결산 때만 쓰는 권한"},
  {"user": "dami", "permission": "SALES:QUERY", "reason": "일을 넘겨받을 사람이 정해질 때까지 필요"}
]
```

**`report_exclude.py`**

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def exclude_key(entry):                                          # 사용자와 권한이 든 딕셔너리(후보 또는 제외 목록의 한 건)를 받는 함수
    """「사용자:권한」 글자를 리턴한다. 제외 목록과 후보를 비교하는 키로 쓴다."""
    return f"{entry['user']}:{entry['permission']}"              # 사용자와 권한을 : 로 이어 붙인다


def make_excluded(finding, reason):                              # 후보 한 건과 제외 이유 글자를 받는 함수
    """후보를 복사해 "exclude_reason" 키(제외 이유)를 적어 리턴한다. 원래 후보는 바꾸지 않는다."""
    item = finding.copy()                                        # 원래 후보는 바꾸지 않고 복사한다
    item["exclude_reason"] = reason                              # 복사본에 제외 이유를 적는다
    return item                                                  # 복사본을 리턴한다


def load_exclude_map(path):                                      # 회수 제외 목록 파일 경로를 받는 함수
    """회수 제외 목록 파일을 읽어 「사용자:권한」 글자를 키로, 제외 이유를 값으로 하는 딕셔너리를 리턴한다."""
    exclude_map = {}                                             # 빈 딕셔너리로 시작한다
    for item in load_json(path, []):                             # 제외 목록의 권한을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        exclude_map[exclude_key(item)] = item["reason"]          # 그 권한의 「사용자:권한」 글자를 키로, 제외 이유를 값으로 담는다
    return exclude_map                                           # 딕셔너리를 리턴한다


def split_by_exclude(findings, exclude_map):                     # 후보 목록과 제외 이유 딕셔너리를 받는 함수
    """후보를 (회수 대상 후보 목록, 회수 제외 후보 목록) 두 목록으로 나눠 리턴한다. 제외 목록에 있어도 후보의 이유(reasons)에 「퇴사한 계정」이 있으면 제외하지 않는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 빈 목록 to_revoke 와 빈 목록 excluded 를 만든다
    # 2. findings 에서 finding 을 하나씩 꺼낸다
    # 3.   exclude_key(finding) 을 key 에 담는다
    # 4.   key 가 exclude_map 에 있고(in), "퇴사한 계정" 이 finding["reasons"] 에 없으면 (not in) — 두 조건을 and 로 이어 한 줄에 쓴다
    # 5.     make_excluded(finding, exclude_map[key]) 를 excluded 에 추가한다
    # 6.   그렇지 않으면 (else)
    # 7.     to_revoke 에 finding 을 추가한다
    # 8. 두 목록 to_revoke, excluded 를 리턴한다
```

- 본문은 모두 함수 안이라 앞에 공백 4개를 넣고(Tab 키 한 번), `for` 안쪽은 공백 4개 더(8개), `if` · `else` 안쪽은 또 4개 더(12개) 넣습니다. `else:` 는 `if` 와 같은 8개이고, 마지막 8번 `return` 은 `for` 밖이므로 4개입니다. `exclude_key` 와 `make_excluded` 는 미리 채워 두었으니 그대로 둡니다.
- 채우기 전에 실행하면 `TypeError: cannot unpack non-iterable NoneType object` 오류가 납니다. 함수가 아무것도 리턴하지 않기 때문입니다.

**`day04_6-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 5교시와 같은 방법으로 리포트를 만든 뒤, 회수 제외 목록을 읽어 후보를 나누고 세 단계로 출력합니다.

```python
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report                        # 오후 5교시에 만든 리포트 함수를 불러온다
from report_exclude import load_exclude_map, split_by_exclude   # 방금 만든 회수 제외 함수를 불러온다

NOW = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 글자의 형식

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다
unused = find_unused(access_list, load_last_used(), NOW, 90)     # 같은 현황에서 90일 넘게 안 쓴 권한을 찾는다(규칙에 걸린 권한도 빼지 않고 전부 넣는다)
report = generate_report(access_list, stale, unused, 90, NOW.strftime(TIME_FORMAT))   # 5교시와 같은 방법으로 리포트를 만든다

exclude_map = load_exclude_map("config/exclude_list.json")   # 회수 제외 목록을 읽는다
to_revoke, excluded = split_by_exclude(report["findings"], exclude_map)   # 후보를 회수 대상과 회수 제외로 나눈다

print("--- 단계 1: 분류 - 후보", report["finding_count"], "건 중 회수 대상", len(to_revoke), "건, 회수 제외", len(excluded), "건")   # 단계 1 시작을 알리는 줄
print("--- 단계 2: 제외 - 회수 제외한 후보와 제외 이유")              # 단계 2 시작을 알리는 줄
for item in excluded:                                            # 회수 제외한 후보를 하나씩 꺼낸다
    print(item["user"], item["permission"], "<-", item["source"], "|", item["exclude_reason"])   # 사용자 · 권한 <- 출처 | 제외 이유를 출력한다

print("--- 단계 3: 확인 - 제외 목록에 있지만 회수 대상으로 남은 후보")        # 단계 3 시작을 알리는 줄
for item in to_revoke:                                           # 회수 대상을 하나씩 꺼낸다
    if item["user"] + ":" + item["permission"] in exclude_map:   # 제외 목록에 있는 권한이면
        print(item["user"], item["permission"], "<-", item["source"], "|", ", ".join(item["reasons"]))   # 사용자 · 권한 <- 출처 | 이유들을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일을 만들고 각각 붙여 넣습니다. 파일마다 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**: 파일마다 아래 네 가지를 반복합니다.
     1. VS Code 왼쪽 목록에서 `access_control` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 파일 이름을 입력하고 Enter 를 누릅니다. 이름은 차례로 `config/exclude_list.json` · `report_exclude.py` · `day04_6-1_run.py` 입니다. `access_control` 폴더를 선택한 채로 `config/exclude_list.json` 을 입력하면 `config` 폴더 안에 만들어집니다.
     4. 열린 파일에 위 코드 상자의 내용을 복사해 붙여 넣고 저장합니다.
   - **방법 2 · touch 로 만들기**: 터미널의 위치가 `access_control` 인지 `pwd` 로 먼저 확인합니다. 파일마다 한 줄씩 치고, 각각 VS Code 에서 열어 붙여넣기: `touch config/exclude_list.json` → `touch report_exclude.py` → `touch day04_6-1_run.py`
   - **방법 3 · vim 으로 만들기**: 파일마다 한 번씩 합니다: `vim config/exclude_list.json` → `vim report_exclude.py` → `vim day04_6-1_run.py` (각각 `i` → 붙여넣기 → `Esc` → `:wq` Enter. 줄 앞 공백이 줄마다 밀려 있으면 `Esc` → `:q!` 로 나와서 방법 1 이나 방법 2 로 다시 만듭니다)
2. **[터미널]** 파일을 만든 뒤 `ls config` 를 쳐서 `exclude_list.json` 이 `access_log.json` 과 같은 `config` 폴더 안에 있는지 확인합니다.
   - `config` 안에 또 `config` 가 생겼다면 위치가 틀린 것이니 옮깁니다.
   - 붙여 넣은 내용이 맞는지 `python -m json.tool config/exclude_list.json` 으로 확인합니다(맥북은 `python3 -m json.tool …`). 여러 줄로 정리되어 출력되면 정상이고, 오류가 나면 붙여 넣을 때 글자가 빠진 것입니다. 깨진 채 두면 제외 목록을 읽지 못해 아무것도 제외되지 않습니다.
3. **[VS Code]** `report_exclude.py` 의 `split_by_exclude` 본문을 직접 씁니다. 6.1 의 표와 그림을 보고 씁니다.
4. **[터미널]** `pwd` 의 결과가 `access_control` 로 끝나는지 확인하고 이어서 실행합니다.
   ```bash
   pwd
   python day04_6-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 위치 확인 · `python` 파이썬으로 파일을 실행 · `day04_6-1_run.py` 실행할 파일
   - 맥북은 `python3 day04_6-1_run.py` 로 칩니다.
5. 출력은 세 단계입니다. 단계 1은 분류 건수 한 줄, 단계 2는 회수 제외한 후보와 이유, 단계 3은 제외 목록에 있지만 회수 대상으로 남은 후보입니다.
6. **[보고서]** `day04_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 회수 대상과 회수 제외가 각각 몇 건인지, 회수 제외된 후보와 제외한 이유를 적어 주세요.
   - (나) 🔍 단계 3 출력을 보면 다미의 `SALES:QUERY` 는 제외 목록에 있는데 회수 대상으로 남았습니다. 왜 제외하지 않게 만들었을까요? 제외했다면 어떤 위험이 있을지도 적어 주세요.
   - (다) 🔍 제외 목록에는 제외하는 기간을 적는 키가 없습니다. 한 번 적은 권한을 아무도 다시 확인하지 않으면 어떤 문제가 생길까요? 목록에 권한을 추가할 때 누가 확인하면 좋을까요?

### 6교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 「사용자:권한」 글자 만들기 | `key = exclude_key(finding)` (`exclude_key` 는 미리 채움) |
| 제외 목록에 있는지 | `if key in exclude_map` |
| 이유에 퇴사가 없는지 | `"퇴사한 계정" not in finding["reasons"]` |
| 두 조건을 한 줄에 | `if key in exclude_map and "퇴사한 계정" not in finding["reasons"]:` |
| 제외된 후보 만들기 | `excluded.append(make_excluded(finding, exclude_map[key]))` (`make_excluded` 는 미리 채움) |
| 둘로 나눠 리턴 | `return to_revoke, excluded` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다. 6교시 마지막 10분에 합니다.

**📍 이런 상황이 있습니다**

- **지금은**: 팀장이 「오늘 만든 접근 점검 코드와 리포트를 저장소에 남겨 달라」고 합니다.
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
   - 10/23(금)에 올린 뒤 만든 오늘 파일이 `access_control/review_list.py` 처럼 한 줄씩 보입니다. 지난번에 올리지 않았다면 `access_control/` 한 줄로 보일 수 있습니다. 어느 쪽이든 `Untracked files:` 아래에 보이는 줄을 센 그대로 적습니다.
   - `access_control/config/exclude_list.json` 은 6교시에 만든 회수 제외 목록입니다. 이것도 올라갑니다.
   - `Untracked files:` 는 「아직 깃이 모르는 새 파일」 목록입니다.
   - `access_control/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다. 줄 수는 그 뒤에 다시 셉니다.
3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `Untracked files:` 아래에 줄이 몇 개 보였는지, 그중에 `.env` 나 `.venv` 가 있었는지 적어 주세요.
   - 앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다. 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   ```bash
   git add .
   git commit -m "Add access control day 4 access review and overprivilege report"
   git push
   ```
   - 명령 풀이: `git add .` 바뀐 파일을 올릴 목록에 담음 · `git commit -m "…"` 따옴표 안의 설명을 붙여 기록으로 저장 · `git push` 깃허브로 올림
   - `git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다. `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `access_control` 폴더를 열고, VS Code 왼쪽 목록의 `access_control` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. `__pycache__` 폴더는 없어도 됩니다.
   - 빠진 이름이 있으면 VS Code 왼쪽 목록의 `access_control` 폴더에 내 PC 에도 있는지 봅니다. 없으면 다른 폴더에 만든 것이니 `access_control` 안으로 옮기고 1 ~ 4번을 다시 합니다.

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
| 현황과 규칙 · 안 쓴 결과를 합쳐 이유가 붙은 후보 리포트를 만들었다 | 오후 5-1 |
| 후보를 「회수 대상」과 「회수 제외」로 나눴다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

내일(10/30(금))은 오늘 찾은 후보를 실제로 **회수**하는 일을 하고, 회수한 이력을 남깁니다. 오후에는 판정 함수를 서버로 여는 수업이 이어집니다. 오늘 만든 후보 리포트와 회수 제외 목록으로 내일 회수할 대상을 정합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_5-1_run.py
```

**채운 코드** (한 예)

```python
    findings = []                                                # 후보를 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        key = entry_key(entry)                                   # 그 권한의 식별 키를 만든다
        reasons = []                                             # 이유를 담을 빈 목록
        if key in stale_reason:                                  # 규칙에 걸린 권한이면
            reasons.append(stale_reason[key])                    # 걸린 이유를 추가한다
        if key in unused_keys:                                   # 안 쓴 권한이면
            reasons.append(f"{days}일 넘게 안 씀(이력 없음 포함)")   # 안 쓴 이유를 추가한다
        if len(reasons) > 0:                                     # 이유가 하나라도 있으면
            finding = entry.copy()                               # 권한을 복사해서
            finding["reasons"] = reasons                         # 복사본에 이유 목록을 적고
            findings.append(finding)                             # 후보에 추가한다
    return {"generated_at": generated_at, "total": len(access_list), "finding_count": len(findings), "findings": findings}   # 리포트를 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 후보는 **10건**입니다. 규칙에 걸린 7건과 90일 넘게 안 쓴 8건 가운데 5건이 두 점검에 모두 걸려서(7 + 8 − 5 = 10) 이유가 둘인 후보가 **5건**입니다. 후보가 아닌 권한은 4개(`seoyeon SALES:QUERY` · `junho SETTLE:QUERY` · `gaeun ACCOUNT:QUERY` · `batch-night SETTLE:QUERY`)입니다.

```
--- 단계 1: 요약 - 점검 14 건 중 후보 10 건 ( 2026-10-29 14:00 )
seoyeon SALES:CHANGE <- 역할 sales | 90일 넘게 안 씀(이력 없음 포함)
junho SALES:QUERY <- 역할 finance | 90일 넘게 안 씀(이력 없음 포함)
gaeun ACCOUNT:CHANGE <- 역할 account_admin | 90일 넘게 안 씀(이력 없음 포함)
dami SALES:QUERY <- 역할 sales | 퇴사한 계정
dami SALES:CHANGE <- 역할 sales | 퇴사한 계정, 90일 넘게 안 씀(이력 없음 포함)
seoyeon SETTLE:QUERY <- 예외 1번 | 만료된 예외, 90일 넘게 안 씀(이력 없음 포함)
junho SALES:CHANGE <- 예외 2번 | 만료된 예외, 90일 넘게 안 씀(이력 없음 포함)
dami SALES:QUERY <- 예외 3번 | 퇴사한 계정
batch-night SALES:QUERY <- 예외 4번 | 만료된 예외, 90일 넘게 안 씀(이력 없음 포함)
gaeun SETTLE:QUERY <- 예외 5번 | 만료된 예외, 90일 넘게 안 씀(이력 없음 포함)
--- 단계 2: 확인 - 후보가 아닌 권한
['seoyeon SALES:QUERY', 'junho SETTLE:QUERY', 'gaeun ACCOUNT:QUERY', 'batch-night SETTLE:QUERY']
```

- (나) 출력에서 이유가 둘인 후보는 예를 들어 `seoyeon SETTLE:QUERY <- 예외 1번 | 만료된 예외, 90일 넘게 안 씀(이력 없음 포함)` 입니다. 기간이 끝난 예외인데 사용 이력도 없다는 뜻입니다. 회수해도 되는 근거가 둘이라, 이유가 하나뿐인 후보보다 회수해도 되는지 판단하기 쉽습니다. 이유를 목록으로 담으면 담당자가 ① 이유가 여럿인 권한을 확신 있게 먼저 처리하고 ② 이유가 하나뿐인 권한은 그 이유가 퇴사처럼 충분히 강한지, 더 확인이 필요한지 가려서 처리하고 ③ 나중에 이유별로 집계할 수 있습니다. 이유를 글자(문자열) 하나로 담으면 둘 중 하나가 덮어써져 사라지고, 이유가 둘인 권한도 하나뿐인 권한과 구별되지 않습니다.
- (다) 후보만 담으면 파일이 짧아 읽기 쉽고, 담당자가 바로 처리할 대상만 보입니다. 후보가 아닌 권한까지 담으면 파일이 길어지지만 「점검했는데 문제없었다」는 근거가 남아 감사(점검 기록을 검토받는 일) 때 도움이 되고 점검이 빠뜨린 권한이 있는지도 확인할 수 있습니다. 실무에서는 두 방법을 섞습니다. 후보를 본문에 담고, 점검한 전체 건수(`total`)와 점검 기준(예: 90일)을 함께 남겨 「몇 건을 어떤 기준으로 봤는지」를 증명합니다. 어느 쪽이든 이유를 들면 맞습니다.

**왜** — 점검 결과가 여러 곳에서 나올수록 담당자가 맞춰 보는 일이 늘고 빠뜨리기 쉽습니다. 이유를 목록으로 권한 한 건에 모으면 한 장만 보고 처리 순서를 정할 수 있습니다. 식별 키에 `source` 까지 넣은 이유는, dami 의 `SALES:QUERY` 처럼 같은 사용자의 같은 권한이 역할과 예외 두 건으로 나올 때 둘을 구별하기 위해서입니다.

**자주 틀리는 곳** — `if len(reasons) > 0:` 검사를 빼먹으면 이유가 하나도 없는 권한까지 후보에 들어갑니다. 실행하면 다음처럼 후보가 14건이 됩니다(점검한 14건이 전부 후보로 나오면 이 실수입니다).

```
--- 단계 1: 요약 - 점검 14 건 중 후보 14 건 ( 2026-10-29 14:00 )
seoyeon SALES:QUERY <- 역할 sales | 
seoyeon SALES:CHANGE <- 역할 sales | 90일 넘게 안 씀(이력 없음 포함)
junho SALES:QUERY <- 역할 finance | 90일 넘게 안 씀(이력 없음 포함)
…
```

`finding = entry.copy()` 대신 `finding = entry` 로 쓰면 원래 현황 권한에도 `reasons` 키가 붙어 버립니다. 그러면 다른 곳에서 같은 현황을 쓸 때 이유 키가 섞여 나옵니다.

**관제에서는** — 리포트 한 장에서 이유가 둘 이상인 후보를 먼저 보고, 이유가 하나인 후보는 이유별로 묶어 처리합니다. 후보 목록과 점검 기준(일 수 · 기준 시각)을 항상 함께 남깁니다.

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day04_6-1_run.py
```

**채운 코드** (한 예)

```python
    to_revoke = []                                               # 회수 대상을 담을 빈 목록
    excluded = []                                                # 회수 제외를 담을 빈 목록
    for finding in findings:                                     # 후보를 하나씩 꺼낸다
        key = exclude_key(finding)                               # 「사용자:권한」 글자를 만든다
        if key in exclude_map and "퇴사한 계정" not in finding["reasons"]:  # 제외 목록에 있고 퇴사한 계정이 아니면
            excluded.append(make_excluded(finding, exclude_map[key]))  # 제외 이유를 적은 복사본을 회수 제외에 추가한다
        else:                                                    # 그렇지 않으면
            to_revoke.append(finding)                            # 회수 대상에 추가한다
    return to_revoke, excluded                                   # 두 목록을 함께 리턴한다
```

**결과**

- (가) 출력은 다음과 같고, 후보 10건 중 회수 대상은 **8건**, 회수 제외는 **2건**입니다. 회수 제외는 서연의 `SALES:CHANGE`(6월 말 · 12월 말 결산 때만 씀)와 가은의 `ACCOUNT:CHANGE`(계정에 사고가 났을 때만 씀)입니다.

```
--- 단계 1: 분류 - 후보 10 건 중 회수 대상 8 건, 회수 제외 2 건
--- 단계 2: 제외 - 회수 제외한 후보와 제외 이유
seoyeon SALES:CHANGE <- 역할 sales | 6월 말 · 12월 말 결산 때만 쓰는 권한
gaeun ACCOUNT:CHANGE <- 역할 account_admin | 계정에 사고가 났을 때만 쓰는 권한이라 평소에는 쓰지 않음
--- 단계 3: 확인 - 제외 목록에 있지만 회수 대상으로 남은 후보
dami SALES:QUERY <- 역할 sales | 퇴사한 계정
dami SALES:QUERY <- 예외 3번 | 퇴사한 계정
```

- (나) 다미는 퇴사한 계정이기 때문입니다. 퇴사한 사람의 권한을 「일을 넘겨받을 사람이 정해질 때까지 필요」라는 이유로 남겨 두면, 이미 회사에 없는 사람의 계정에 권한이 계속 부여된 채로 남습니다. 그 계정을 다른 사람이 몰래 쓸 수 있습니다. 그래서 퇴사한 계정은 제외 목록에 있어도 제외하지 않고 회수 대상에 둡니다. 일을 넘겨받는 사람이 필요하면 그 사람에게 권한을 따로 부여해야 합니다.
- (다) 제외 목록에는 제외하는 기간을 적는 곳이 없어서, 한 번 적은 권한을 아무도 다시 확인하지 않으면 필요 없어진 뒤에도 권한이 계속 남습니다. 목록이 길어지면 어떤 권한이 아직 필요한지 아무도 모르게 됩니다. 목록에 권한을 추가할 때는 적은 담당자와 다른 사람(예: 팀장이나 보안 책임자)이 이유를 보고 확인하고, 권한마다 다시 확인할 날짜를 정해 두는 방법이 좋습니다. 이유가 맞으면 다른 방법도 인정합니다.

**왜** — 점검 결과는 판단을 돕는 자료이고 최종 결정이 아닙니다. 사람이 정한 회수 제외 목록을 코드가 반영해야 필요한 권한이 없어지지 않습니다. 다만 목록에 잘못 적혀도 퇴사한 사람의 권한만큼은 열려 있으면 위험하므로, 퇴사한 계정은 코드가 막습니다.

**자주 틀리는 곳** — `and "퇴사한 계정" not in finding["reasons"]` 조건을 빼먹으면 퇴사한 다미까지 회수 제외가 됩니다. 오류는 나지 않고 숫자만 달라집니다. 실행하면 다음처럼 됩니다(회수 제외가 2건이어야 하는데 4건이 되고 단계 3이 비면 이 실수입니다).

```
--- 단계 1: 분류 - 후보 10 건 중 회수 대상 6 건, 회수 제외 4 건
```

**관제에서는** — 회수 제외 목록을 바꿀 때마다 바꾼 사람 · 승인한 사람 · 날짜를 남기고, 점검 리포트에 제외한 건수를 함께 적습니다. 권한을 적은 날짜를 따로 기록해 두고, 가장 오래된 권한도 같이 봅니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
cd ..
pwd
git status
git add .
git commit -m "Add access control day 4 access review and overprivilege report"
git push
```

**결과**

- (가) 한 예: 「줄이 열여섯 개였고(`.py` 열 개 + `config/access_log.json` · `config/exclude_list.json` 두 개 + `.md` 네 개), `.env` · `.venv` 는 없었다」. 이 숫자는 10/23(금) 파일을 이미 올렸고 `__pycache__` 가 보이지 않을 때의 숫자이며, 줄 수와 이름은 학생마다 다를 수 있습니다. `.env` 나 `.venv` 가 보였다면 `.gitignore` 에 한 줄을 적고 `git status` 를 다시 쳤다고 적습니다.

**왜** — 올리기 전에 올라갈 파일을 확인해야 비밀 키가 섞이지 않습니다. 코드와 오늘 만든 회수 제외 목록이 함께 올라가야 내일 회수 수업이 같은 기준에서 시작합니다.

**자주 틀리는 곳** — `.env` 가 보이는데 그대로 `git add .` 를 하는 실수가 가장 위험합니다. `cd ..` 를 두 번 쳐서 `security-agent-toolkit` 바깥으로 나가는 경우도 있습니다. `pwd` 로 확인합니다.

**관제에서는** — 점검 코드와 회수 제외 목록은 같은 커밋에 함께 올려, 어느 코드와 어느 목록으로 점검했는지 이력으로 남깁니다.

---

### 앞 교시 파일 완성본

앞 교시 파일을 못 만들고 다음 교시로 넘어가야 할 때 그대로 만들어 씁니다. 오전 파일(`review_list.py` · `review_rules.py` · `review_unused.py` · `config/access_log.json`)은 오전 문서 맨 아래에 있습니다. 정답 본문을 함수 머리말과 합친 전체 파일입니다.

**`overprivilege.py`** (5교시 완성본)

```python
def entry_key(entry):                                            # 현황의 권한 한 건의 식별 키를 만드는 함수
    """현황의 권한 한 건(또는 그 복사본)의 식별 키(user:permission:source 를 이어 붙인 글자)를 리턴한다."""
    return entry["user"] + ":" + entry["permission"] + ":" + entry["source"]   # 세 값을 : 로 이어 붙인다


def make_stale_reason(stale):                                    # 규칙에 걸린 권한 목록을 받는 함수
    """규칙에 걸린 권한의 식별 키를 키로, 걸린 이유를 값으로 하는 딕셔너리를 리턴한다."""
    stale_reason = {}                                            # 식별 키 → 걸린 이유를 담을 빈 딕셔너리
    for item in stale:                                           # 규칙에 걸린 권한을 하나씩 꺼낸다
        stale_reason[entry_key(item)] = item["reason"]           # 식별 키로 걸린 이유를 찾을 수 있게 담는다
    return stale_reason                                          # 딕셔너리를 리턴한다


def make_unused_keys(unused):                                    # 안 쓴 권한 목록을 받는 함수
    """안 쓴 권한의 식별 키를 담은 목록을 리턴한다."""
    unused_keys = []                                             # 안 쓴 권한의 식별 키를 담을 빈 목록
    for item in unused:                                          # 안 쓴 권한을 하나씩 꺼낸다
        unused_keys.append(entry_key(item))                      # 식별 키를 목록에 추가한다
    return unused_keys                                           # 목록을 리턴한다


def generate_report(access_list, stale, unused, days, generated_at):   # 현황 · 규칙 결과 · 안 쓴 결과 · 기준 일 수 · 만든 시각 글자를 받는 함수
    """과다권한 후보 리포트(딕셔너리)를 리턴한다. 후보마다 "reasons" 키에 이유 목록을 적는다."""
    stale_reason = make_stale_reason(stale)                      # 규칙에 걸린 권한의 식별 키 → 걸린 이유 딕셔너리를 만든다(미리 채움)
    unused_keys = make_unused_keys(unused)                       # 안 쓴 권한의 식별 키 목록을 만든다(미리 채움)
    findings = []                                                # 후보를 담을 빈 목록
    for entry in access_list:                                    # 현황의 권한을 한 건씩 꺼낸다
        key = entry_key(entry)                                   # 그 권한의 식별 키를 만든다
        reasons = []                                             # 이유를 담을 빈 목록
        if key in stale_reason:                                  # 규칙에 걸린 권한이면
            reasons.append(stale_reason[key])                    # 걸린 이유를 추가한다
        if key in unused_keys:                                   # 안 쓴 권한이면
            reasons.append(f"{days}일 넘게 안 씀(이력 없음 포함)")   # 안 쓴 이유를 추가한다
        if len(reasons) > 0:                                     # 이유가 하나라도 있으면
            finding = entry.copy()                               # 권한을 복사해서
            finding["reasons"] = reasons                         # 복사본에 이유 목록을 적고
            findings.append(finding)                             # 후보에 추가한다
    return {"generated_at": generated_at, "total": len(access_list), "finding_count": len(findings), "findings": findings}   # 리포트를 리턴한다
```

**`report_exclude.py`** (6교시 완성본)

```python
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def exclude_key(entry):                                          # 사용자와 권한이 든 딕셔너리(후보 또는 제외 목록의 한 건)를 받는 함수
    """「사용자:권한」 글자를 리턴한다. 제외 목록과 후보를 비교하는 키로 쓴다."""
    return f"{entry['user']}:{entry['permission']}"              # 사용자와 권한을 : 로 이어 붙인다


def make_excluded(finding, reason):                              # 후보 한 건과 제외 이유 글자를 받는 함수
    """후보를 복사해 "exclude_reason" 키(제외 이유)를 적어 리턴한다. 원래 후보는 바꾸지 않는다."""
    item = finding.copy()                                        # 원래 후보는 바꾸지 않고 복사한다
    item["exclude_reason"] = reason                              # 복사본에 제외 이유를 적는다
    return item                                                  # 복사본을 리턴한다


def load_exclude_map(path):                                      # 회수 제외 목록 파일 경로를 받는 함수
    """회수 제외 목록 파일을 읽어 「사용자:권한」 글자를 키로, 제외 이유를 값으로 하는 딕셔너리를 리턴한다."""
    exclude_map = {}                                             # 빈 딕셔너리로 시작한다
    for item in load_json(path, []):                             # 제외 목록의 권한을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        exclude_map[exclude_key(item)] = item["reason"]          # 그 권한의 「사용자:권한」 글자를 키로, 제외 이유를 값으로 담는다
    return exclude_map                                           # 딕셔너리를 리턴한다


def split_by_exclude(findings, exclude_map):                     # 후보 목록과 제외 이유 딕셔너리를 받는 함수
    """후보를 (회수 대상 후보 목록, 회수 제외 후보 목록) 두 목록으로 나눠 리턴한다. 제외 목록에 있어도 후보의 이유(reasons)에 「퇴사한 계정」이 있으면 제외하지 않는다."""
    to_revoke = []                                               # 회수 대상을 담을 빈 목록
    excluded = []                                                # 회수 제외를 담을 빈 목록
    for finding in findings:                                     # 후보를 하나씩 꺼낸다
        key = exclude_key(finding)                               # 「사용자:권한」 글자를 만든다
        if key in exclude_map and "퇴사한 계정" not in finding["reasons"]:  # 제외 목록에 있고 퇴사한 계정이 아니면
            excluded.append(make_excluded(finding, exclude_map[key]))  # 제외 이유를 적은 복사본을 회수 제외에 추가한다
        else:                                                    # 그렇지 않으면
            to_revoke.append(finding)                            # 회수 대상에 추가한다
    return to_revoke, excluded                                   # 두 목록을 함께 리턴한다
```

**`config/exclude_list.json`** (6교시 완성본)

```json
[
  {"user": "gaeun", "permission": "ACCOUNT:CHANGE", "reason": "계정에 사고가 났을 때만 쓰는 권한이라 평소에는 쓰지 않음"},
  {"user": "seoyeon", "permission": "SALES:CHANGE", "reason": "6월 말 · 12월 말 결산 때만 쓰는 권한"},
  {"user": "dami", "permission": "SALES:QUERY", "reason": "일을 넘겨받을 사람이 정해질 때까지 필요"}
]
```
