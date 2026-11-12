# 11/11(수) 오전 · 5과목 자동 대응(SOAR) ④ — 봉쇄(containment) 조치 구현: 계정 잠금 · IP 차단 · 세션 종료, 사후 검증 · 감사 기록 · 롤백 대비 — 실습

어제까지는 판단 단계(맥락 보강 · 처리 경로 분기 · 안전장치 · 승인 · 재시도)를 만들었습니다. 오늘은 판단한 대응 조치를 모의 시스템(실제 서버 대신 연습용으로 만든 시뮬레이션 환경)에서 **실행하고, 사후 검증하고, 감사 기록으로 남기고, 롤백할 수 있게** 구현합니다. 사후 검증(post-action verification)은 조치 후 실제 상태를 다시 확인하는 일이고, 감사 기록(audit log)은 조치를 순서대로 남긴 기록이며, 롤백(rollback)은 조치 이전 상태로 복원하는 일입니다. 침해 사고 대응에서 이 구현 단계는 봉쇄(containment, 컨테인먼트: 피해가 더 확산되기 전에 사고를 차단하는 단계)에 해당합니다. NIST SP 800-61 Rev. 2 는 봉쇄를 「봉쇄 · 제거 · 복구」(Containment, Eradication, and Recovery) 단계 안에 둡니다. 오늘은 현업에서 자주 생기는 결함 세 가지를 하나씩 해소합니다.

- **2교시**: 계정 잠금(account lockout, 어카운트 락아웃: 계정의 로그인을 비활성화하는 조치)을 실행하고 <mark>잠금 상태를 사후 검증</mark>하며, 조치 전 · 후 상태를 감사 기록으로 남깁니다(`containment_store.py` · `account_actions.py`).
- **3교시**: IP 를 차단(block)하되 <mark>허용 목록(allowlist: 차단 대상에서 제외하기로 미리 정한 IP 의 목록)에 있는 IP 와 여러 계정이 공유하는 IP 는 자동 차단에서 제외하고</mark>, 차단에는 유효 기간(TTL, Time To Live, 티티엘)을 두어 기간이 지나면 자동 해제합니다(`ip_actions.py`).
- **4교시**: 계정을 잠가도 <mark>이미 발급된 세션(session, 세션: 로그인한 뒤 서버가 유지하는 접속 상태)이 활성 상태(active, 액티브: 아직 유효한 상태)로 남는 문제</mark>를 세션 종료(session termination)로 해소하고, 잠긴 계정에 활성 세션이 잔존하는지 점검합니다(`session_actions.py` · `containment.py`).

깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 새 문법은 2교시의 `리스트.remove()` 하나입니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기는 미리 채운 줄에 맞춥니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. 주석은 지우지 않습니다.

📎 **이전 파일**: 월요일에 만든 `incident.py` 의 `load_json` · `save_json` 만 씁니다. 없으면 `complete_files.md` 의 1절에서 복사합니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark>`ls` 결과에 `config` 와 `incident.py` 가 보이면</mark> 됩니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day03_am_containment.md`, `day03_am_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 설정 · 데이터 파일 세 개를 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch config/vip_accounts.json config/allowlist_ips.json ip_users.json
   ls config
   ```

**`config/vip_accounts.json`** — 자동 조치 대상에서 제외하는 **VIP 계정**(고중요도 계정: 자동 조치로 잠기면 업무 영향이 큰 계정) 리스트입니다. `gaeun` 은 계정 관리자이므로 포함했습니다. 2 · 4교시가 읽습니다.

```
["gaeun"]
```

**`config/allowlist_ips.json`** — **허용 목록**(allowlist, 얼라우리스트: 정상 접속이 발생하는 출처라서 차단 대상에서 제외하기로 미리 정한 IP 의 목록)입니다. 협력사 사무실 `203.0.113.80` 과 자사 취약점(vulnerability, 벌너러빌리티: 공격에 이용될 수 있는 보안상의 약점) 점검 서버 `192.0.2.10` 이 들어 있습니다. 점검 서버(취약점 스캐너)는 취약점을 찾기 위해 경로 스캔(path scan, 패스 스캔: 서버의 여러 주소에 차례로 요청을 보내 확인하는 일) 같은 요청을 보내므로 탐지 알림이 발생합니다. 그러나 자사가 의도적으로 수행하는 점검이므로 차단하면 안 됩니다. 3교시가 읽습니다.

```
["203.0.113.80", "192.0.2.10"]
```

**`ip_users.json`** — IP 별로 해당 IP 를 사용하는 계정의 리스트입니다. 여러 사용자가 공유하는 IP(공유 IP, shared IP, 셰어드 아이피: 사무실 공용 회선처럼 한 주소를 여러 사람이 공유 IP)를 차단하면 정상 사용자까지 접속하지 못하는 부수적 피해(collateral damage, 콜래터럴 대미지: 의도하지 않은 대상까지 영향을 받는 일)가 생깁니다. 그래서 3교시에서 IP 별 사용 계정 수를 계산합니다.

```
{"203.0.113.80": ["seoyeon", "jiwoo"], "192.0.2.41": ["junho", "hana"]}
```

5. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`). <mark>`1 2 2` 가 나와야</mark> 합니다(VIP 계정 1개 · 허용 목록 IP 2개 · `ip_users.json` 에 적은 IP 2개를 센 값).
   ```bash
   python -c "import json; print(len(json.load(open('config/vip_accounts.json', encoding='utf-8'))), len(json.load(open('config/allowlist_ips.json', encoding='utf-8'))), len(json.load(open('ip_users.json', encoding='utf-8'))))"
   ```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'incident'` 는 <mark>월요일에 만든 `incident.py` 가 이 폴더에 없다는 뜻</mark>입니다. `complete_files.md` 에서 복사합니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 실행할 때마다 처음 상태에서 시작해 같은 결과가 나옵니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 계정 잠금을 실행하고 사후 검증하며, 조치 전 · 후 상태를 감사 기록으로 남기기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 오늘 오전에 계정 잠금 요청이 세 건 들어옵니다. **계정 잠금**(account lockout, 어카운트 락아웃)은 해당 계정의 로그인을 비활성화하는 조치입니다. `INC-001` 은 퇴사한 `dami`, `INC-003` 은 계정 관리자 `gaeun`, `INC-006` 은 이미 잠겨 있던 `junho` 입니다. 월요일에 만든 `run_action` 에 이 세 계정을 그대로 넘기면, 세 건 모두 계정 이름을 잠긴 계정 리스트에 추가하고 「잠금 완료」라는 결과만 기록합니다.
> - **문제**:
>   - 사후 검증(post-action verification: 조치 후 실제 상태를 다시 확인하는 일, 2.1 에서 설명)이 없습니다. 잠금이 실제로 적용됐는지 확인하지 않으므로 실제 서버에서 잠금 명령이 실패해도 「잠금 완료」로 기록됩니다.
>   - 조치 전 상태(before)를 기록하지 않습니다. `junho` 는 원래 잠겨 있었는데, 나중에 알림이 오탐(false positive, 폴스 포지티브: 정상 활동을 공격으로 잘못 판정한 것)으로 판명되어 자동 대응이 잠근 계정을 일괄 해제(롤백, rollback: 조치 이전 상태로 복원하는 일)하면, 조치 전 상태가 기록에 없으므로 원래 잠겨 있던 `junho` 까지 해제됩니다.
>   - 화요일에는 계정 관리자 알림을 승인 경로로 분기했습니다. 그러나 이 경로를 거치지 않고 잠금 함수를 직접 호출하면 `gaeun` 계정도 잠겨, 직원들의 계정 관리 업무가 중단됩니다.
> - **부탁**: 계정을 잠근 후 실제로 잠겼는지 사후 검증하고, 조치 전 · 후 상태를 감사 기록으로 남겨 주세요. 계정 관리자(VIP) 계정은 이 함수에서도 잠그지 않아야 하며, 오탐으로 판명되면 해제할 수 있어야 합니다.
> - **바뀌는 점**: 사후 검증으로 확인된 상태만 「잠김」으로 기록되고, 원래 잠겨 있던 계정(`junho`)과 이번에 잠근 계정(`dami`)이 조치 전 상태(before)로 구분됩니다. 오늘 샘플에서는 세 건 중 `dami` 한 건만 새로 잠기고 `gaeun` 은 잠기지 않습니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 2.1 대응 조치는 「실행 · 사후 검증 · 감사 기록」 세 단계를 모두 마쳐야 완료된다

계정 잠금 같은 **대응 조치**는 ① 실행(execution), ② 사후 검증, ③ 감사 기록의 세 단계를 모두 마쳐야 완료된 것으로 봅니다. ②의 **사후 검증**(post-action verification, 포스트 액션 베리피케이션: 조치 후 시스템의 실제 상태가 의도한 대로 바뀌었는지 다시 확인하는 일)은 이후 문서에서 「조치 후 확인」이라고도 부릅니다. 사후 검증은 명령이 오류 없이 종료됐지만 실제로는 적용되지 않은 경우를 탐지합니다. 예를 들어 `dami` 를 잠근 후 잠긴 계정 리스트에 `dami` 가 실제로 있는지 다시 조회합니다. ③의 **감사 기록**(audit log, 오딧 로그: 어떤 조치를 어떤 대상에 했는지 순서대로 남긴 기록) 한 건에는 다음 여섯 가지를 남깁니다.

| 키 | 뜻 | 예 |
|---|---|---|
| `action` | 수행한 조치의 종류 | `"계정 잠금"` |
| `target` | 조치 대상(계정 이름 또는 IP) | `"dami"` |
| `incident` | 인시던트(incident: 처리해야 하는 보안 사건 한 건) 번호 | `"INC-001"` |
| `before` | 조치 전 상태 | `"잠기지 않음"` |
| `after` | 사후 검증으로 **확인한** 조치 후 상태 | `"잠김"` |
| `reason` | 조치 사유 | `"퇴사한 계정의 서버 요청"` |

- `before` 는 롤백할 때 복원할 원래 상태를 알려 주므로 남깁니다.
- 조치 전에 이미 잠겨 있던 계정은 `잠김 → 잠김`(상태 변경 없음)으로 기록해야, 나중에 오탐으로 판명되어 롤백할 때 `junho` 처럼 원래 잠겨 있던 계정은 해제 대상에서 제외할 수 있습니다. 이미 잠긴 계정에 잠금을 다시 요청해도 시스템 상태가 바뀌지 않는 성질을 멱등성(idempotency, 아이뎀포턴시: 같은 조치를 여러 번 실행해도 결과가 한 번 실행한 것과 같은 성질)이라고 합니다.
- 모의 시스템의 상태 `state` 는 잠긴 계정(`locked_users`) · 차단한 IP · 열린 세션을 저장하는 딕셔너리입니다. 이 상태는 실행할 때마다 초기값에서 다시 시작하므로 결과를 재현할 수 있습니다. 조치 기록은 파일에 추가한 순서대로 남으므로, 사건의 경과를 사후에 재구성하는 감사 추적(audit trail, 오딧 트레일: 어떤 일이 어떤 순서로 있었는지 재구성할 수 있게 남긴 시간순 기록)에 사용할 수 있습니다.

**🐍 문법 상자 — `리스트.remove(값)` 은 리스트에서 그 값을 제거한다**

```python
locked = ["junho", "dami"]
locked.remove("dami")
print(locked)
```

| 코드 | 뜻 |
|---|---|
| `locked.remove("dami")` | 리스트에서 `dami` 를 제거한다. 리스트에 없으면 `ValueError`(밸류 에러: 값이 맞지 않아 나는 오류)가 난다 |
| 위 코드의 출력 | `['junho']` |

함수는 두 파일에 나뉘어 있고 실행 파일이 하나 더 있습니다. 직접 쓰는 곳은 **아홉 군데**입니다.

```
containment_store.py  make_record       : 위 표의 여섯 키를 가진 조치 기록 한 건을 만든다 (1번)
                      append_log        : 기록을 기록 파일에 한 건 더한다 (2번)
account_actions.py    check_policy      : VIP 계정이면 자동 조치를 막는 이유를 리턴한다 (3 · 4번)
                      verify_locked     : 실제로 잠긴 계정 리스트에 있는지 확인한다 (5번)
                      lock_account      : 잠그고, 확인하고, 기록을 만든다 (6번이 잠그는 줄)
                      unlock_account    : 해제하고, 확인하고, 기록을 만든다 (7번이 해제하는 줄)
실행 파일             day03_2-1_run.py  : 잠금 요청마다 잠그고 (8번) 기록을 남긴다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 2-1 · 계정 잠금을 실행하고 사후 검증하며, 조치 전 · 후 상태를 감사 기록으로 남기기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>잠금 호출만 있고 사후 검증도 조치 전 상태 기록도 없어서, 「잠갔다」는 기록이 실제 상태를 입증하지 못합니다</mark>.
- **만드는 것**: 조치 기록 생성과 기록 파일 추가(`containment_store.py`), VIP 정책 검사 · 잠금 사후 검증 · 잠금 · 해제(`account_actions.py`), 잠금 요청 처리(`day03_2-1_run.py`).
- **실행하면**: <mark>단계 1: 조치 전 잠긴 계정, 단계 2: 잠금 요청 3건의 조치 전 → 후, 단계 3: 해제, 단계 4: 파일에 저장해 둔 잠긴 계정과 조치 기록 수를 다시 읽은 결과가 나옵니다.</mark>

**🎯 할 일**: 파일 세 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 ~ 4 를 읽습니다.

**`containment_store.py`** — 모의 시스템의 상태와 조치 기록 파일을 관리합니다. 3 · 4교시에서도 이 파일의 함수를 불러와 사용합니다. 직접 쓰는 곳은 1 · 2번입니다. `INITIAL_STATE` 의 `junho` 는 실습 전부터 잠겨 있는 계정입니다.

```python
import copy                                                           # 처음 상태를 복사해 쓰기 위해 copy 를 불러온다
from incident import load_json, save_json                             # 월요일 파일의 파일 읽기 · 쓰기 함수를 불러온다

STATE_PATH = "containment_state.json"                                 # 모의 시스템 상태를 저장할 파일 이름
LOG_PATH = "containment_log.json"                                     # 조치 기록을 저장할 파일 이름
INITIAL_STATE = {                                                     # 실습을 시작할 때의 모의 시스템 상태
    "locked_users": ["junho"],                                        # 이미 잠겨 있는 계정 : junho 는 실습 전부터 잠겨 있다
    "blocked_ips": [],                                                # 차단한 IP 리스트 : 처음에는 비어 있다
    "block_expiry": {},                                               # IP 별 차단이 끝나는 시각(분) : 처음에는 비어 있다
    "clock": 0,                                                       # 모의 시스템의 시계(분) : 0 에서 시작한다
    "sessions": {"dami": ["S-101", "S-102"], "seoyeon": ["S-201"], "gaeun": ["S-301"], "jiwoo": ["S-401"], "junho": ["S-501"], "hana": ["S-601"]},  # 계정별로 열려 있는 로그인 세션
}


def new_state():                                                      # 인자가 없는 함수
    """처음 상태를 복사해 새 모의 시스템 상태를 리턴한다.
    실행할 때마다 같은 상태에서 시작해 결과를 비교할 때 쓴다.
    """
    return copy.deepcopy(INITIAL_STATE)                               # 처음 상태의 복사본을 리턴한다


def save_state(state):                                                # 모의 시스템 상태를 받는 함수
    """상태를 파일에 저장한다.
    다음 프로그램이 이어서 읽을 수 있게 할 때 쓴다.
    """
    save_json(state, STATE_PATH)                                      # 상태를 JSON 파일로 저장한다


def load_state():                                                     # 인자가 없는 함수
    """저장해 둔 상태 파일을 읽어 리턴한다.
    저장이 제대로 됐는지 확인하거나 이어서 일할 때 쓴다.
    """
    return load_json(STATE_PATH)                                      # 상태 파일을 읽어 리턴한다


def reset_log():                                                      # 인자가 없는 함수
    """조치 기록 파일을 빈 리스트로 비운다.
    실행할 때마다 기록을 처음부터 추가할 때 쓴다.
    """
    save_json([], LOG_PATH)                                           # 빈 리스트를 기록 파일로 저장한다


def make_record(action, target, incident_id, before, after, reason):  # 조치 이름 · 대상 · 인시던트 번호 · 조치 전 · 조치 후 · 이유를 받는 함수
    """조치 한 건(무엇을 · 누구에게 · 조치 전 · 조치 후 · 이유)의 기록을 딕셔너리로 만들어 리턴한다.
    조치 전과 후 상태를 함께 남겨 두고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 키 "action"(action), "target"(target), "incident"(incident_id), "before"(before), "after"(after), "reason"(reason) 를 가진 딕셔너리를 record 에 저장한다
    return record                                                     # 기록 한 건을 리턴한다


def append_log(record):                                               # 기록 한 건을 받는 함수
    """기록 파일을 읽어 기록 한 건을 더하고 다시 저장한다. 파일이 아직 없으면 빈 리스트로 시작한다.
    조치할 때마다 기록을 한 건씩 추가해 둘 때 쓴다.
    """
    try:                                                              # 파일 읽기를 시도한다 — 미리 채운 줄
        log = load_json(LOG_PATH)                                     # 기록 파일을 읽는다 — 미리 채운 줄
    except FileNotFoundError:                                         # 파일이 없으면 — 미리 채운 줄
        log = []                                                      # 빈 리스트로 시작한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. log 에 record 를 추가한다 (append)
    save_json(log, LOG_PATH)                                          # 기록 파일로 다시 저장한다
```

**`account_actions.py`** — 계정 잠금과 해제를 구현합니다. 4교시에서도 이 파일의 함수를 불러와 사용합니다. 직접 쓰는 곳은 3 ~ 7번입니다.

```python
from containment_store import make_record                                             # 기록 한 건을 만드는 함수를 불러온다


def check_policy(user, vip_accounts):                                                 # 계정 이름과 VIP 계정 리스트를 받는 함수
    """자동으로 조치하면 안 되는 계정(VIP)이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    경로에서 이미 `승인 필요` 로 보냈어도 조치 함수가 마지막으로 한 번 더 막고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. user 가 vip_accounts 안에 있으면 (if, in)
    # 4.   "VIP 계정이라 자동 조치 대상이 아님" 을 리턴한다
    return ""                                                                         # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def verify_locked(user, state):                                                       # 계정 이름과 모의 시스템 상태를 받는 함수
    """계정이 잠긴 계정 리스트에 들어 있으면 True, 없으면 False 를 리턴한다.
    잠그라고 호출한 것과 실제로 잠긴 것이 같은지 조치 뒤에 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. user 가 state["locked_users"] 안에 있는지(in)의 결과를 리턴한다


def lock_account(user, state, vip_accounts, incident_id, reason):                     # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """VIP 인지 먼저 확인하고 계정을 잠근 뒤, 실제로 잠겼는지 다시 확인해 조치 기록 한 건을 리턴한다.
    VIP 이거나 이미 잠겨 있으면 잠그지 않고 그 이유를 기록에 남긴다.
    """
    blocked = check_policy(user, vip_accounts)                                        # 자동 조치를 막을 이유를 구한다 — 미리 채운 줄
    if blocked != "":                                                                 # 막을 이유가 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "변경 없음", "변경 없음", blocked)  # 바꾸지 않고 이유를 기록한다 — 미리 채운 줄
    if user in state["locked_users"]:                                                 # 이미 잠겨 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "잠김", "잠김", "이미 잠겨 있어 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. state["locked_users"] 에 user 를 추가한다 (append)
    after = "잠김"                                                                    # 조치 뒤 상태 : 일단 잠겼다고 적고 — 미리 채운 줄
    if not verify_locked(user, state):                                                # 실제로 확인해 잠기지 않았으면 — 미리 채운 줄
        after = "잠기지 않음 (확인 실패)"                                             # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 잠금", user, incident_id, "잠기지 않음", after, reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unlock_account(user, state, incident_id, reason):                                 # 계정 · 상태 · 인시던트 번호 · 이유를 받는 함수
    """잠긴 계정을 해제하고 실제로 해제됐는지 확인해 조치 기록 한 건을 리턴한다.
    오탐으로 확인된 계정을 되돌릴 때 쓴다.
    """
    if user not in state["locked_users"]:                                             # 잠겨 있지 않으면 — 미리 채운 줄
        return make_record("계정 해제", user, incident_id, "잠기지 않음", "잠기지 않음", "잠겨 있지 않아 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. state["locked_users"] 에서 user 를 제거한다 (remove)
    after = "잠기지 않음"                                                             # 조치 뒤 상태 : 일단 해제됐다고 적고 — 미리 채운 줄
    if verify_locked(user, state):                                                    # 실제로 확인해 아직 잠겨 있으면 — 미리 채운 줄
        after = "잠김 (확인 실패)"                                                    # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 해제", user, incident_id, "잠김", after, reason)         # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄
```

**`day03_2-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json                                                          # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log  # 방금 만든 상태 · 기록 함수를 불러온다
from account_actions import lock_account, unlock_account                                # 방금 만든 계정 조치 함수를 불러온다

vip_accounts = load_json("config/vip_accounts.json")                                    # VIP 계정 리스트를 읽는다
requests = [("INC-001", "dami", "퇴사한 계정의 서버 요청"), ("INC-003", "gaeun", "여러 로그 연결"), ("INC-006", "junho", "퇴사 처리 확인")]  # 잠금 요청 3건 : (인시던트 번호, 계정, 이유)
state = new_state()                                                                     # 처음 상태에서 시작한다
reset_log()                                                                             # 기록 파일을 비운다

print("--- 단계 1: 조치 전에 잠겨 있는 계정")                                           # 단계 1 시작을 알리는 줄
print(state["locked_users"])                                                            # 잠긴 계정을 출력한다

print("--- 단계 2: 잠금 요청 3건")                                                      # 단계 2 시작을 알리는 줄
for incident_id, user, reason in requests:                                              # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 record 에 저장한다
    # 9. append_log(record) 를 호출한다 (조치 기록을 파일에 남긴다)
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 3: 오탐으로 확인되어 dami 해제")                                        # 단계 3 시작을 알리는 줄
record = unlock_account("dami", state, "INC-001", "오탐으로 확인되어 해제")             # 해제한다
append_log(record)                                                                      # 해제 기록도 남긴다
print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

save_state(state)                                                                       # 상태를 파일에 저장한다
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                         # 단계 4 시작을 알리는 줄
saved_state = load_state()                                                              # 저장한 상태 파일을 읽는다
saved_log = load_json("containment_log.json")                                           # 저장한 기록 파일을 읽는다
print("잠긴 계정:", saved_state["locked_users"])                                        # 파일에 저장된 잠긴 계정을 출력한다
print("조치 기록:", len(saved_log), "건")                                               # 파일에 저장된 기록 수를 출력한다
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch containment_store.py account_actions.py day03_2-1_run.py
   ls
   ```
2. **[VS Code]** `containment_store.py` 1 · 2번, `account_actions.py` 3 ~ 7번, `day03_2-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day03_2-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 1줄, 단계 2 는 3줄, 단계 3 은 1줄, 단계 4 는 2줄입니다. 실행하면 `containment_state.json` 과 `containment_log.json` 이 생깁니다.
5. **[보고서]** `day03_am_report.md` 의 `## 2교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 단계 4 의 잠긴 계정과 조치 기록 수를 적어 주세요.
   - (나) 🔍 INC-003 의 `gaeun` 은 잠기지 않았습니다. 단계 2 의 줄을 근거로 이유를 적어 주세요. 그리고 어제 3교시의 경로가 VIP 계정을 이미 `승인 필요` 경로로 분기했는데도 조치 함수가 정책을 한 번 더 검사하는 이유도 적어 주세요.
   - (다) 🔍 INC-006 의 `junho` 는 `잠김 → 잠김` 으로 기록됐고, 단계 3 에서 해제한 `dami` 는 `잠김 → 잠기지 않음` 입니다. `before` 를 남기면 롤백할 때 어떤 판단이 가능해지는지 적어 주세요. 그리고 잠금 뒤 사후 검증(`verify_locked`)이 없으면 어떤 문제가 생기는지도 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 딕셔너리를 만들어 변수에 저장하기 | `record = {"action": action, ..., "reason": reason}` |
| 리스트에 추가 | `log.append(record)` |
| 리스트 안에 있으면 | `if user in vip_accounts:` |
| 리스트 안에 있는지 확인한 결과 리턴 | `return user in state["locked_users"]` |
| 리스트에서 제거 | `state["locked_users"].remove(user)` |
| 함수 결과를 변수에 저장하기 | `record = lock_account(user, state, vip_accounts, incident_id, reason)` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 허용 목록 IP 와 공유 IP 는 자동 차단에서 제외하고, 차단에 유효 기간(TTL)을 두어 자동 해제하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 오늘 아침 경로 스캔(path scan, 패스 스캔: 서버의 여러 주소에 차례로 요청을 보내 취약점을 찾는 시도) 탐지 알림이 세 건 들어왔습니다. 하나는 외부 IP `198.51.100.90`, 하나는 자사 취약점 점검 서버(취약점 스캐너) `192.0.2.10`, 하나는 `junho` 와 `hana` 가 공유하는 사무실 IP `192.0.2.41` 입니다. IP 차단(IP block)은 해당 IP 에서 들어오는 접속을 모두 거부하는 조치입니다.
> - **문제**:
>   - 세 건을 모두 자동 차단하면 점검 서버가 차단되어 점검이 중단되고, 공유 IP 를 차단하면 `junho` 와 `hana` 두 사람이 접속하지 못합니다(부수적 피해).
>   - 한 번 차단하면 사람이 해제하기 전까지 유지되어, 오래된 차단이 누적되면 어떤 차단이 아직 필요한지 판단할 수 없게 됩니다.
> - **부탁**: 허용 목록(allowlist)에 있는 IP 는 차단하지 말고, 여러 계정이 공유하는 IP 는 담당자 승인을 거치게 해 주세요. 차단한 IP 는 정해진 유효 기간(TTL, 2시간)이 지나면 자동 해제해 주세요.
> - **바뀌는 점**: 세 건 중 외부 공격 IP 한 건만 차단되고, 그 차단도 2시간 뒤 자동으로 해제됩니다(오늘은 차단 함수를 직접 호출하는 실습이라, 월요일 플레이북의 승인 값 확인은 거치지 않습니다). 점검 서버와 정상 사용자는 차단되지 않습니다. 상황과 IP 는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 3.1 차단 전에 영향 범위를 확인하고, 차단에는 만료 시각을 정한다

차단 전에 적용하는 정책 검사(policy check) 규칙은 두 가지입니다. 영향 범위(blast radius, 블라스트 레이디어스: 한 조치가 잘못됐을 때 영향을 받는 대상의 범위)에는 정상 사용자와 필요한 서버가 포함되므로, 두 규칙은 그 범위를 먼저 확인하는 장치입니다.

| 검사 | 조건 | 결과 |
|---|---|---|
| 허용 목록 | `allowlist_ips.json` 에 있다 | 차단하지 않고 이유를 기록한다 |
| 공유 IP | 여러 사용자가 공유하는 IP 다 (그 IP 를 쓰는 계정이 `SHARED_IP_LIMIT`(2) 개 이상) | 차단하지 않고 담당자 승인이 필요하다고 기록한다 |

- 둘 다 해당하지 않으면 차단하고 **만료 시각**(expiry time, 익스파이어리 타임: 차단이 만료 시각)을 함께 기록합니다.
- 만료 시각은 모의 시스템의 현재 시각(`clock`, 분)에 차단 유효 기간(`ttl`, 티티엘: Time To Live, 설정한 조치가 유효한 기간)을 더한 값입니다. 예를 들어 현재 0분이고 `ttl` 이 120분이면 만료 시각은 120분입니다. 오늘은 `ttl` 이 120분입니다.
- 차단은 일정 기간 뒤 자동 해제되는 임시 조치로 두고, 영구 차단은 사람이 사유를 확인한 뒤 결정합니다. NIST SP 800-61 Rev. 2 는 봉쇄 전략을 선택하는 기준으로 서비스 가용성(service availability)과 조치의 지속 기간(duration of the solution: 예를 들어 4시간 뒤 제거하는 긴급 임시 조치, 2주 뒤 제거하는 임시 조치, 영구 조치)을 듭니다.

함수는 한 파일에 있고, 직접 쓰는 곳은 **아홉 군데**입니다.

```
ip_actions.py     is_in_allowlist    : 허용 목록에 있는지 확인한다 (1번)
                  count_users_on_ip  : 그 IP 를 쓰는 계정 수를 센다 (2번)
                  check_ip_policy    : 허용 목록 IP · 함께 쓰는 IP 이면 차단을 막는 이유를 리턴한다 (미리 채움)
                  block_ip           : 차단하고 (3번) 끝나는 시각을 적는다 (4번)
                  expire_blocks      : 끝나는 시각이 지난 차단을 찾아 (5번) 풀고 기록한다 (6번)
실행 파일         day03_3-1_run.py   : 막을 이유를 구하고 (7번), 이유가 없으면 (8번) 차단한다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 3-1 · 허용 목록 IP 와 공유 IP 를 판별해 차단하고, 유효 기간이 지나면 자동 해제하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>경로 스캔 알림 세 건을 모두 차단하면 점검 서버와 정상 사용자가 차단되고, 차단이 해제되지 않고 계속 유지됩니다</mark>.
- **만드는 것**: 허용 목록 조회 · 사용 계정 수 집계 · 차단 · 만료된 차단 해제(`ip_actions.py`), 정책 검사와 차단 호출(`day03_3-1_run.py`).
- **실행하면**: <mark>단계 1: 요청 3건의 처리 결과, 단계 2: 차단 뒤 상태, 단계 3: 120분 뒤 자동 해제, 단계 4: 저장한 파일에서 읽은 값이 나옵니다.</mark>

**🎯 할 일**: 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 1 ~ 3 을 읽습니다.

**`ip_actions.py`** — IP 차단과 만료된 차단의 자동 해제를 구현합니다. 오후에도 이 파일의 함수를 불러와 사용합니다. 직접 쓰는 곳은 1 ~ 6번입니다.

```python
from containment_store import make_record                                              # 기록 한 건을 만드는 함수를 불러온다

SHARED_IP_LIMIT = 2                                                                    # 한 IP 를 쓰는 계정이 이 수 이상이면 공유 IP 로 본다
DEFAULT_TTL = 120                                                                      # 차단을 유지하는 시간(분)


def is_in_allowlist(ip, allowlist_ips):                                                # IP 와 허용 목록을 받는 함수
    """IP 가 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실처럼 차단하면 안 되는 IP 를 찾아낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. ip 가 allowlist_ips 안에 있는지(in)의 결과를 리턴한다


def count_users_on_ip(ip, ip_users):                                                   # IP 와 IP 별 사용 계정 딕셔너리를 받는 함수
    """그 IP 를 쓰는 계정이 몇 개인지 리턴한다. ip_users.json 에 없는 IP 는 0 을 리턴한다.
    차단하면 정상 사용자가 몇 명 영향을 받는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. ip_users.get(ip, []) 의 개수(len)를 리턴한다 (목록에 없으면 빈 리스트로 본다)


def check_ip_policy(ip, allowlist_ips, ip_users):                                      # IP · 허용 목록 · 사용 계정 딕셔너리를 받는 함수
    """자동으로 차단하면 안 되는 IP 이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    허용 목록 IP 이거나 여러 계정이 함께 쓰는 IP 를 차단하기 전에 가려낼 때 쓴다.
    """
    if is_in_allowlist(ip, allowlist_ips):                                             # 허용 목록 IP 이면 — 미리 채운 줄
        return "허용 목록 IP 라서 차단하지 않음"                                       # 이유를 리턴한다 — 미리 채운 줄
    if count_users_on_ip(ip, ip_users) >= SHARED_IP_LIMIT:                             # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        return "여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요"                        # 이유를 리턴한다 — 미리 채운 줄
    return ""                                                                          # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def block_ip(ip, state, incident_id, reason, ttl):                                     # IP · 상태 · 인시던트 번호 · 이유 · 유지 시간을 받는 함수
    """IP 를 차단하고 끝나는 시각을 적은 뒤, 실제로 차단됐는지 확인해 기록 한 건을 리턴한다.
    영구 차단 대신, 시간이 지나면 자동으로 풀리는 임시 차단을 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. state["blocked_ips"] 에 ip 를 추가한다 (append)
    # 4. state["block_expiry"][ip] 에 state["clock"] + ttl 을 저장한다 (끝나는 시각)
    after = "차단됨"                                                                   # 조치 뒤 상태 : 일단 차단됐다고 적고 — 미리 채운 줄
    if ip not in state["blocked_ips"]:                                                 # 실제로 확인해 차단되지 않았으면 — 미리 채운 줄
        after = "차단되지 않음 (확인 실패)"                                            # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("IP 차단", ip, incident_id, "차단되지 않음", after, reason + " (" + str(ttl) + "분 뒤 자동 해제)")  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unblock_ip(ip, state, incident_id, reason):                                        # IP · 상태 · 인시던트 번호 · 이유를 받는 함수
    """차단한 IP 를 풀고 끝나는 시각 기록도 지운 뒤 기록 한 건을 리턴한다.
    시간이 끝나서 풀거나 오탐으로 풀 때 쓴다.
    """
    state["blocked_ips"].remove(ip)                                                    # 차단 리스트에서 제거한다 — 미리 채운 줄
    state["block_expiry"].pop(ip)                                                      # 끝나는 시각 기록도 지운다 — 미리 채운 줄
    return make_record("IP 해제", ip, incident_id, "차단됨", "차단되지 않음", reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def expire_blocks(state, incident_id):                                                 # 상태와 인시던트 번호를 받는 함수
    """끝나는 시각이 지난 차단을 모두 풀고 해제 기록 리스트를 리턴한다.
    임시 차단이 사람 손 없이 풀리게 할 때 쓴다.
    """
    records = []                                                                       # 해제 기록을 저장할 빈 리스트
    for ip in list(state["blocked_ips"]):                                              # 차단 리스트의 복사본에서 IP 를 하나씩 꺼낸다 (원본을 바꾸며 돌면 안 되기 때문이다)
        end_time = state["block_expiry"][ip]                                           # 그 IP 의 차단이 끝나는 시각 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. end_time 이 state["clock"] 이하이면 (if, <=)
        # 6.   unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제") 의 결과를 records 에 추가한다 (append)
    return records                                                                     # 해제 기록 리스트를 리턴한다
```

**`day03_3-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 7번 아래에는 막을 이유를 저장하는 `refusal = …`(`refusal` 은 영어로 「거절」이고, 막을 이유가 있으면 그 문장이 저장됩니다)을, 8번 아래에는 `if … :` 를, 9번 아래에는 한 단계 들여쓴 `record = …` 를 씁니다. 그 사이의 미리 채운 줄은 그대로 둡니다. 2교시의 `containment_store.py` 가 같은 폴더에 있어야 합니다.

```python
from incident import load_json                                                           # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log, make_record  # 상태 · 기록 함수를 불러온다
from ip_actions import check_ip_policy, block_ip, expire_blocks, DEFAULT_TTL             # 방금 만든 IP 조치 함수를 불러온다

allowlist_ips = load_json("config/allowlist_ips.json")                                   # 허용 목록을 읽는다
ip_users = load_json("ip_users.json")                                                    # IP 별 사용 계정을 읽는다
requests = [("INC-005", "198.51.100.90", "경로 스캔"), ("INC-009", "192.0.2.10", "경로 스캔"), ("INC-008", "192.0.2.41", "경로 스캔")]  # 차단 요청 3건 : (인시던트 번호, IP, 이유)
state = new_state()                                                                      # 처음 상태에서 시작한다
reset_log()                                                                              # 기록 파일을 비운다

print("--- 단계 1: 차단 요청 3건")                                                       # 단계 1 시작을 알리는 줄
for incident_id, ip, reason in requests:                                                 # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. check_ip_policy(ip, allowlist_ips, ip_users) 의 결과를 refusal 에 저장한다
    record = make_record("IP 차단", ip, incident_id, "변경 없음", "변경 없음", refusal)  # 먼저 「바꾸지 않음」 기록을 만들어 두고 — 미리 채운 줄
    # 8. refusal 이 빈 글자("")이면 (if, ==)
    # 9.   block_ip(ip, state, incident_id, reason, DEFAULT_TTL) 의 결과를 record 에 저장한다 (실제로 차단한 기록으로 바꾼다)
    append_log(record)                                                                   # 조치 기록을 파일에 남긴다
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 2: 차단 뒤 차단한 IP 와 끝나는 시각")                                    # 단계 2 시작을 알리는 줄
print("차단한 IP:", state["blocked_ips"])                                                # 차단한 IP 를 출력한다
print("차단이 끝나는 시각(분):", state["block_expiry"])                                  # 끝나는 시각을 출력한다

print("--- 단계 3: 시계를 120분 뒤로 옮기고 시간이 끝난 차단 풀기")                      # 단계 3 시작을 알리는 줄
state["clock"] = state["clock"] + 120                                                    # 모의 시스템의 시계를 120분 뒤로 옮긴다
for record in expire_blocks(state, "INC-005"):                                           # 끝난 차단의 해제 기록을 하나씩 꺼낸다
    append_log(record)                                                                   # 해제 기록도 남긴다
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                # 해제 뒤 차단한 IP 를 출력한다

save_state(state)                                                                        # 상태를 파일에 저장한다
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                          # 단계 4 시작을 알리는 줄
print("차단한 IP:", load_state()["blocked_ips"])                                         # 저장된 차단 IP 를 출력한다
print("조치 기록:", len(load_json("containment_log.json")), "건")                        # 저장된 기록 수를 출력한다
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch ip_actions.py day03_3-1_run.py
   ls
   ```
2. **[VS Code]** `ip_actions.py` 1 ~ 6번, `day03_3-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day03_3-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 3줄, 단계 2 는 2줄, 단계 3 은 2줄, 단계 4 는 2줄입니다.
5. **[보고서]** `day03_am_report.md` 의 `## 3교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣어 주세요. 그리고 단계 1 에서 실제로 차단된 IP 와, 차단하지 않은 IP 와 그 이유를 적어 주세요.
   - (나) 🔍 INC-008 의 `192.0.2.41` 은 차단되지 않았습니다. `ip_users.json` 의 값을 근거로 차단하지 않은 이유를 적고, 그대로 차단했다면 영향을 받았을 사용자와 그 영향을 적어 주세요.
   - (다) 🔍 단계 2 의 차단이 만료 시각(120)과 단계 3 의 시계(120)를 근거로 `198.51.100.90` 이 자동 해제된 이유를 적어 주세요. 그리고 유효 기간이 있는 임시 차단이 영구 차단보다 나은 점도 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 리스트 안에 있는지 확인한 결과 리턴 | `return ip in allowlist_ips` |
| 키가 없어도 기본값을 주며 꺼내기 | `ip_users.get(ip, [])` |
| 리스트의 개수 | `len(ip_users.get(ip, []))` |
| 딕셔너리에 값 저장하기 | `state["block_expiry"][ip] = state["clock"] + ttl` |
| 이하이면 | `if end_time <= state["clock"]:` |
| 빈 문자열과 같으면 | `if refusal == "":` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 계정 잠금 뒤에도 남는 활성 세션을 종료하고, 빈틈(잔존 세션)이 없는지 점검하기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 퇴사자 `dami` 의 계정을 잠갔다고 기록했는데, 잠근 후에도 `dami` 의 서버 요청이 두 건 더 들어왔습니다. 잠금 실행 전에 이미 인증을 마친 **세션**(session, 세션: 로그인한 뒤 서버가 유지하는 접속 상태)이 두 개 남아 있었기 때문입니다.
> - **문제**: 계정을 잠그면 새 로그인(인증)만 차단되고, 이미 열려 있는 세션은 계속 유효합니다. 잠금만 하고 끝내면 퇴사자가 세션이 만료될 때까지 접속할 수 있는데, 이 상태를 점검하는 절차가 없습니다.
> - **부탁**: 계정을 잠근 후에는 열린 세션도 모두 종료해 주세요. 그리고 잠겼는데 활성 세션이 남은 계정이 있는지 점검하는 기능도 만들어 주세요.
> - **바뀌는 점**: 잠금과 세션 종료가 함께 실행되고, 조치가 누락된 계정은 점검에서 즉시 탐지됩니다. 오늘 샘플에서는 이미 잠겨 있는데 세션 하나가 열려 있는 `junho` 가 점검에서 발견됩니다. 상황은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 4.1 계정 잠금은 새 로그인을 차단하고, 세션 종료는 이미 열린 접속을 종료한다

**세션**(session, 세션: 로그인한 뒤 서버가 유지하는 접속 상태)이 유효하면 서버는 비밀번호를 다시 요구하지 않습니다. 따라서 계정을 잠가도 이미 발급된 세션은 계속 사용할 수 있습니다. 예를 들어 아침에 로그인해 둔 `dami` 의 세션 `S-101` 은 계정을 잠근 후에도 서버에 요청을 보낼 수 있습니다. 세션은 서버 쪽에서 무효화(invalidate, 인밸리데이트: 그 세션을 더는 인증에 쓸 수 없게 만드는 일)해야 종료되므로, 잠금 뒤에 세션 종료 조치가 따로 필요합니다. 조치 순서도 중요합니다.

| 순서 | 결과 |
|---|---|
| 잠금 → 세션 종료 (오늘 구현) | 새 로그인이 이미 차단되어 있어서, 세션을 종료하면 더는 접속할 수 없다 |
| 세션 종료 → 잠금 | 두 조치 사이에 재로그인(re-login)이 가능해 새 세션이 생길 수 있다 |
| 잠금만 | 활성 세션으로 계속 접속할 수 있다 |

- 이 표는 오늘 모의 시스템의 동작 규칙입니다. 실제 서비스는 시스템마다 동작이 다르므로, 계정을 잠글 때 세션이 어떻게 처리되는지 먼저 확인해야 합니다.
- 따라서 세션 종료는 **잠금이 사후 검증으로 확인된 뒤에만** 실행합니다. 잠금이 적용되지 않았거나 VIP 정책으로 차단된 계정의 세션은 종료하면 안 됩니다.
- 실습 시작 상태에서 `junho` 는 이미 잠겨 있지만 세션이 하나 열려 있습니다. 이처럼 계정은 잠겼는데 활성 세션이 잔존(residual, 레지듀얼: 조치 후에도 남아 있음)하는 상태를 이 문서에서는 **빈틈**이라 부르며(출력에도 「빈틈」으로 표시됩니다), 이를 탐지하는 점검이 `find_open_sessions` 입니다.

함수는 두 파일에 나뉘어 있고, 직접 쓰는 곳은 **아홉 군데**입니다.

```
session_actions.py  terminate_sessions  : 계정의 세션 리스트를 비운다 (1번)
                    find_open_sessions  : 잠긴 계정 중 열린 세션이 남은 계정을 모은다 (2 · 3번)
containment.py      contain_account     : 계정을 잠그고 (4번), 잠금이 확인되면 (5번) 세션을 종료한다 (6번)
실행 파일           day03_4-1_run.py    : 요청마다 contain_account 를 호출하고 (7번), 다시 점검하고 (8번), 상태를 저장한다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 4-1 · 계정 잠금 뒤 활성 세션까지 종료하고, 빈틈(잔존 세션)을 점검하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>계정만 잠그면 활성 세션이 잔존하고, 잔존 여부를 확인하는 점검도 없습니다</mark>.
- **만드는 것**: 세션 종료와 빈틈 점검(`session_actions.py`), 잠금 → 세션 종료를 순서대로 수행하는 통합 함수(`containment.py`), 호출 · 재점검 · 저장(`day03_4-1_run.py`).
- **실행하면**: <mark>단계 1: 실습 전부터 잠겨 있는데 세션이 열려 있던 계정, 단계 2: 잠금과 세션 종료 기록, 단계 3: 조치 후 재점검, 단계 4: 저장한 파일에서 읽은 값이 나옵니다.</mark>

**🎯 할 일**: 파일 세 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 1 ~ 3 을 읽습니다.

**`session_actions.py`** — 세션 종료와 점검입니다. 직접 쓰는 곳은 1 ~ 3번입니다.

```python
from containment_store import make_record                  # 기록 한 건을 만드는 함수를 불러온다


def terminate_sessions(user, state, incident_id, reason):  # 계정 · 상태 · 인시던트 번호 · 이유를 받는 함수
    """계정에 열려 있는 로그인 세션을 모두 종료하고, 조치 전과 후의 세션 수를 기록 한 건으로 리턴한다.
    계정을 잠가도 이미 로그인한 세션은 남기 때문에, 잠근 뒤에 이어서 쓴다.
    """
    before_count = len(state["sessions"].get(user, []))    # 조치 전 세션 수 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. state["sessions"][user] 에 빈 리스트를 저장한다 (세션을 모두 종료한다)
    after_count = len(state["sessions"].get(user, []))     # 조치 뒤 세션 수를 다시 구한다 — 미리 채운 줄
    return make_record("세션 종료", user, incident_id, "세션 " + str(before_count) + "개", "세션 " + str(after_count) + "개", reason)  # 조치 전 · 후 세션 수와 함께 기록한다 — 미리 채운 줄


def find_open_sessions(state):                             # 모의 시스템 상태를 받는 함수
    """잠겨 있는데도 열린 세션이 남아 있는 계정의 리스트를 리턴한다.
    잠금만 하고 세션을 끝내지 않아 생긴 빈틈을 점검할 때 쓴다.
    """
    gaps = []                                              # 빈틈이 있는 계정을 저장할 빈 리스트
    for user in state["locked_users"]:                     # 잠긴 계정을 하나씩 꺼낸다
        open_count = len(state["sessions"].get(user, []))  # 그 계정에 열린 세션 수 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. open_count 가 0 보다 크면 (if, >)
        # 3.   gaps 에 user 를 추가한다 (append)
    return gaps                                            # 빈틈이 있는 계정 리스트를 리턴한다
```

**`containment.py`** — 잠금과 세션 종료를 한 함수에서 순서대로 수행합니다. 오후에도 이 파일의 함수를 불러와 사용합니다. 직접 쓰는 곳은 4 ~ 6번입니다.

```python
from account_actions import lock_account                              # 2교시에 만든 계정 잠금 함수를 불러온다
from session_actions import terminate_sessions                        # 방금 만든 세션 종료 함수를 불러온다


def contain_account(user, state, vip_accounts, incident_id, reason):  # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """계정을 먼저 잠그고, 잠겼다고 확인되면 이어서 열린 세션을 종료한 뒤, 조치 기록 리스트를 리턴한다.
    잠금과 세션 종료를 따로 하다가 생기는 빈틈을 막고 싶을 때 쓴다.
    """
    records = []                                                      # 조치 기록을 저장할 빈 리스트
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 lock_record 에 저장한다
    records.append(lock_record)                                       # 잠금 기록을 리스트에 추가한다 — 미리 채운 줄
    # 5. lock_record 의 "after" 가 "잠김" 이면 (if, ==)
    # 6.   terminate_sessions(user, state, incident_id, reason) 의 결과를 records 에 추가한다 (append)
    return records                                                    # 조치 기록 리스트를 리턴한다
```

**`day03_4-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 2교시의 `containment_store.py` 와 `account_actions.py` 가 같은 폴더에 있어야 합니다.

```python
from incident import load_json                                                          # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log  # 상태 · 기록 함수를 불러온다
from session_actions import find_open_sessions                                          # 방금 만든 세션 점검 함수를 불러온다
from containment import contain_account                                                 # 방금 만든 통합 조치 함수를 불러온다

vip_accounts = load_json("config/vip_accounts.json")                                    # VIP 계정 리스트를 읽는다
requests = [("INC-001", "dami", "퇴사한 계정의 서버 요청"), ("INC-003", "gaeun", "여러 로그 연결"), ("INC-006", "junho", "퇴사 처리 확인")]  # 조치 요청 3건 : (인시던트 번호, 계정, 이유)
state = new_state()                                                                     # 처음 상태에서 시작한다
reset_log()                                                                             # 기록 파일을 비운다

print("--- 단계 1: 점검 — 잠겼는데 세션이 열려 있는 계정")                              # 단계 1 시작을 알리는 줄
print(find_open_sessions(state))                                                        # 실습 전부터 있는 빈틈을 출력한다

print("--- 단계 2: 잠금 → 세션 종료")                                                   # 단계 2 시작을 알리는 줄
for incident_id, user, reason in requests:                                              # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. contain_account(user, state, vip_accounts, incident_id, reason) 의 결과를 records 에 저장한다
    for record in records:                                                              # 조치 기록을 하나씩 꺼낸다
        append_log(record)                                                              # 조치 기록을 파일에 남긴다
        print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 3: 조치 뒤 다시 점검")                                                  # 단계 3 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. find_open_sessions(state) 의 결과를 gaps_after 에 저장한다
print("빈틈이 남은 계정:", gaps_after)                                                  # 점검 결과를 출력한다
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다

# 9. save_state(state) 를 호출한다 (상태를 파일에 저장한다)
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                         # 단계 4 시작을 알리는 줄
print("잠긴 계정:", load_state()["locked_users"])                                       # 저장된 잠긴 계정을 출력한다
print("조치 기록:", len(load_json("containment_log.json")), "건")                       # 저장된 기록 수를 출력한다
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch session_actions.py containment.py day03_4-1_run.py
   ls
   ```
2. **[VS Code]** `session_actions.py` 1 ~ 3번, `containment.py` 4 ~ 6번, `day03_4-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day03_4-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다. 단계 1 은 1줄, 단계 2 는 5줄, 단계 3 은 2줄, 단계 4 는 2줄입니다.
5. **[보고서]** `day03_am_report.md` 의 `## 4교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 단계 3 에서 빈틈이 남은 계정과 단계 4 의 잠긴 계정을 적어 주세요.
   - (나) 🔍 단계 1 에서 `junho` 가 점검에서 발견된 이유를 적어 주세요. 그리고 `dami` 가 단계 2 에서 받은 두 가지 조치와, 잠금만 했다면 유효하게 남았을 접속(세션)을 적어 주세요.
   - (다) 🔍 `gaeun` 은 잠금도 세션 종료도 받지 않았습니다. `containment.py` 5번의 `if` 조건과 단계 2 의 출력 줄을 근거로 그 이유를 적어 주세요. 그리고 잠금이 적용되지 않은 계정의 세션을 종료하면 안 되는 이유도 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 딕셔너리에 값 저장하기 | `state["sessions"][user] = []` |
| 보다 크면 | `if open_count > 0:` |
| 리스트에 추가 | `gaps.append(user)` |
| 함수 결과를 변수에 저장하기 | `lock_record = lock_account(...)` |
| 같으면 | `if lock_record["after"] == "잠김":` |
| 함수 호출만 하기 | `save_state(state)` |

---

## 오늘 오전 마무리

| 달성 기준 | 문제 |
|---|---|
| 계정 잠금을 실행하고 사후 검증했으며, 조치 전 · 후 상태를 감사 기록으로 남겼다 | 오전 2-1 |
| 허용 목록 IP 와 공유 IP 를 판별해 차단하고, 유효 기간이 지나면 자동 해제했다 | 오전 3-1 |
| 잠금 뒤 활성 세션을 종료하고, 빈틈(잔존 세션)이 남았는지 점검했다 | 오전 4-1 |

오후에는 두 가지를 합니다. ① 오늘 만든 조치를 기록만 근거로 **롤백**합니다(조치 전부터 잠겨 있던 계정은 변경하지 않습니다). ② 화요일에 만든 맥락 보강 · 경로 판단과 함께 알림 8건을 일괄 처리합니다. 마지막에는 처리 결과를 근무 보고로 요약합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 2-1

**채운 코드** (한 예)

`containment_store.py` 의 1 · 2번입니다.

```python
    # 1. 키 "action"(action), "target"(target), "incident"(incident_id), "before"(before), "after"(after), "reason"(reason) 를 가진 딕셔너리를 record 에 저장한다
    record = {"action": action, "target": target, "incident": incident_id, "before": before, "after": after, "reason": reason}  # 조치 한 건의 기록을 딕셔너리로 만든다
    # 2. log 에 record 를 추가한다 (append)
    log.append(record)  # 기록 한 건을 리스트에 추가한다
```

`account_actions.py` 의 3 ~ 7번입니다.

```python
    # 3. user 가 vip_accounts 안에 있으면 (if, in)
    if user in vip_accounts:                         # VIP 계정이면
    # 4.   "VIP 계정이라 자동 조치 대상이 아님" 을 리턴한다
        return "VIP 계정이라 자동 조치 대상이 아님"  # 막는 이유를 리턴한다
    # 5. user 가 state["locked_users"] 안에 있는지(in)의 결과를 리턴한다
    return user in state["locked_users"]             # 잠긴 계정 리스트 안에 있는지 확인한 결과를 리턴한다
    # 6. state["locked_users"] 에 user 를 추가한다 (append)
    state["locked_users"].append(user)               # 잠긴 계정 리스트에 추가한다
    # 7. state["locked_users"] 에서 user 를 제거한다 (remove)
    state["locked_users"].remove(user)               # 잠긴 계정 리스트에서 제거한다
```

`day03_2-1_run.py` 의 8 · 9번입니다.

```python
    # 8. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 record 에 저장한다
    record = lock_account(user, state, vip_accounts, incident_id, reason)  # 계정을 잠그고 기록을 받는다
    # 9. append_log(record) 를 호출한다 (조치 기록을 파일에 남긴다)
    append_log(record)                                                     # 조치 기록을 파일에 남긴다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 4 의 잠긴 계정은 <mark style="background:#bde3ff">**`['junho']`**</mark>, 조치 기록은 <mark style="background:#bde3ff">**4건**</mark>입니다.

```
--- 단계 1: 조치 전에 잠겨 있는 계정
['junho']
--- 단계 2: 잠금 요청 3건
INC-001 dami · 잠기지 않음 → 잠김 · 퇴사한 계정의 서버 요청
INC-003 gaeun · 변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
--- 단계 3: 오탐으로 확인되어 dami 해제
INC-001 dami · 잠김 → 잠기지 않음 · 오탐으로 확인되어 해제
--- 단계 4: 파일에 저장된 값 다시 읽기
잠긴 계정: ['junho']
조치 기록: 4 건
```

- (나) 단계 2 의 INC-003 줄이 <mark style="background:#bde3ff">`변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님`</mark> 입니다. `check_policy` 가 `gaeun` 이 `vip_accounts` 에 포함된 것을 확인하고 잠금을 차단했습니다.
  - 경로에서 이미 VIP 를 `승인 필요` 로 분기해도 조치 함수가 정책을 한 번 더 검사하는 이유: 경로 설정이 잘못될 수 있고, 경로를 거치지 않고 다른 코드가 이 함수를 직접 호출할 수도 있기 때문입니다.
  - 이처럼 통제를 한 지점에만 두지 않고 여러 지점에 중복해서 두는 설계를 심층 방어(defense in depth, 디펜스 인 뎁스: 한 통제가 실패해도 다른 통제가 보완하도록 여러 단계로 방어하는 전략)라고 합니다. 한 지점에서 누락돼도 다음 지점에서 차단해야 계정 관리자 계정이 잠기지 않습니다.
- (다) `before` 가 있으면 <mark style="background:#bde3ff">조치 전부터 잠겨 있던 계정(`junho`)과 이번 자동 대응이 잠근 계정(`dami`)을 구별</mark>할 수 있어서, 롤백할 때 자동 대응이 변경한 계정만 해제할 수 있습니다.
  - 사후 검증이 없으면 잠금 호출이 실패해도 「잠갔다」고 기록됩니다. 사후 검증이 있으면 `잠기지 않음 (확인 실패)` 로 남아 기록과 실제 상태가 일치합니다.

**왜**: <mark>조치는 실행만으로 완료되지 않습니다. 사후 검증으로 실제 상태 변경을 확인하고, 조치 전 · 후 상태를 기록해야 결과를 신뢰할 수 있고 롤백할 수 있습니다.</mark>

**자주 틀리는 곳**

- 1번을 비워 두면 기록 딕셔너리를 만들지 못해 오류가 납니다(`NameError`, 네임 에러: 정의하지 않은 이름을 썼다는 오류). 이름이 비슷한 변수가 있으면 파이썬 버전에 따라 뒤에 `Did you mean: …`(「혹시 이것을 말한 건가요?」라는 추천 문구)이 붙을 수 있습니다.

```
NameError: name 'record' is not defined
```

- 2번을 비워 두면 오류 없이 <mark>**기록이 하나도 파일에 남지 않습니다.**</mark> 단계 4 의 조치 기록이 0건으로 나옵니다.

```
--- 단계 4: 파일에 저장된 값 다시 읽기
잠긴 계정: ['junho']
조치 기록: 0 건
```

- 3 · 4번을 비워 두면 <mark>**VIP 인 `gaeun` 이 잠깁니다.**</mark> 단계 2 의 INC-003 줄이 `잠기지 않음 → 잠김` 으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 2: 잠금 요청 3건
INC-001 dami · 잠기지 않음 → 잠김 · 퇴사한 계정의 서버 요청
INC-003 gaeun · 잠기지 않음 → 잠김 · 여러 로그 연결
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
```

- 5번을 비워 두면 확인 함수가 아무것도 리턴하지 않습니다. 그러면 잠겼는지 확인할 때마다 「잠기지 않음」으로 판단되어, <mark>**이번에 잠그려던 `dami` 가 실제로 잠겼는데도 「확인 실패」로 기록됩니다.**</mark> 원인이 확인 함수의 리턴값에 있다는 점이 6번과 다릅니다.

```
--- 단계 2: 잠금 요청 3건
INC-001 dami · 잠기지 않음 → 잠기지 않음 (확인 실패) · 퇴사한 계정의 서버 요청
INC-003 gaeun · 변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
```

- 6번을 비워 두면 오류는 나지 않지만 <mark>**잠그는 줄이 없어 실제로 잠기지 않은 `dami` 의 잠금 실패가 사후 검증에서 드러납니다.**</mark> 5번과 달리 확인 함수는 정상이고, 계정을 잠그는 줄만 빠진 경우입니다. 두 경우 모두 사후 검증이 있어서 `잠기지 않음 (확인 실패)` 로 드러납니다.

```
--- 단계 2: 잠금 요청 3건
INC-001 dami · 잠기지 않음 → 잠기지 않음 (확인 실패) · 퇴사한 계정의 서버 요청
INC-003 gaeun · 변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
```

- 7번을 비워 두면 해제 호출이 끝나도 <mark>**계정이 그대로 잠겨 있습니다.**</mark> 사후 검증이 있어서 기록에 `잠김 → 잠김 (확인 실패)` 로 나타나고, 단계 4 의 잠긴 계정에도 `dami` 가 남습니다.

```
--- 단계 3: 오탐으로 확인되어 dami 해제
INC-001 dami · 잠김 → 잠김 (확인 실패) · 오탐으로 확인되어 해제
```

- 8 · 9번을 비워 두면 `record` 가 만들어지지 않아 오류가 납니다(`NameError`).

```
NameError: name 'record' is not defined
```

**관제에서는**: 사후 검증(조치 후 확인)은 「명령은 오류 없이 종료됐지만 실제로는 적용되지 않은」 결함을 탐지하는 방법 중 하나입니다. <mark>조치 전 상태를 기록해 두면 오탐을 복구(롤백)할 때 원래 상태로 정확히 복원할 수 있습니다.</mark>

---

### 정답 3-1

**채운 코드** (한 예)

`ip_actions.py` 의 1 ~ 6번입니다.

```python
    # 1. ip 가 allowlist_ips 안에 있는지(in)의 결과를 리턴한다
    return ip in allowlist_ips                                                                # 허용 목록 안에 있는지 확인한 결과를 리턴한다
    # 2. ip_users.get(ip, []) 의 개수(len)를 리턴한다 (목록에 없으면 빈 리스트로 본다)
    return len(ip_users.get(ip, []))                                                          # 그 IP 를 쓰는 계정 수를 리턴한다 (목록에 없으면 0)
    # 3. state["blocked_ips"] 에 ip 를 추가한다 (append)
    state["blocked_ips"].append(ip)                                                           # 차단한 IP 리스트에 추가한다
    # 4. state["block_expiry"][ip] 에 state["clock"] + ttl 을 저장한다 (끝나는 시각)
    state["block_expiry"][ip] = state["clock"] + ttl                                          # 차단이 끝나는 시각을 적는다
        # 5. end_time 이 state["clock"] 이하이면 (if, <=)
        if end_time <= state["clock"]:                                                        # 끝나는 시각이 지났으면
        # 6.   unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제") 의 결과를 records 에 추가한다 (append)
            records.append(unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제"))  # 차단을 풀고 해제 기록을 모은다
```

`day03_3-1_run.py` 의 7 ~ 9번입니다.

```python
    # 7. check_ip_policy(ip, allowlist_ips, ip_users) 의 결과를 refusal 에 저장한다
    refusal = check_ip_policy(ip, allowlist_ips, ip_users)              # 자동 차단을 막을 이유를 구한다
    # 8. refusal 이 빈 글자("")이면 (if, ==)
    if refusal == "":                                                   # 막을 이유가 없으면
    # 9.   block_ip(ip, state, incident_id, reason, DEFAULT_TTL) 의 결과를 record 에 저장한다 (실제로 차단한 기록으로 바꾼다)
        record = block_ip(ip, state, incident_id, reason, DEFAULT_TTL)  # 실제로 차단하고 기록을 받는다
```

**결과**

- (가) 출력은 다음과 같습니다. 실제로 차단된 IP 는 <mark style="background:#bde3ff">**`198.51.100.90`**</mark>, 차단하지 않은 IP 는 `192.0.2.10`(허용 목록 IP)과 `192.0.2.41`(공유 IP)입니다.

```
--- 단계 1: 차단 요청 3건
INC-005 198.51.100.90 · 차단되지 않음 → 차단됨 · 경로 스캔 (120분 뒤 자동 해제)
INC-009 192.0.2.10 · 변경 없음 → 변경 없음 · 허용 목록 IP 라서 차단하지 않음
INC-008 192.0.2.41 · 변경 없음 → 변경 없음 · 여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요
--- 단계 2: 차단 뒤 차단한 IP 와 끝나는 시각
차단한 IP: ['198.51.100.90']
차단이 끝나는 시각(분): {'198.51.100.90': 120}
--- 단계 3: 시계를 120분 뒤로 옮기고 시간이 끝난 차단 풀기
INC-005 198.51.100.90 · 차단됨 → 차단되지 않음 · 차단 시간이 끝나 자동 해제
차단한 IP: []
--- 단계 4: 파일에 저장된 값 다시 읽기
차단한 IP: []
조치 기록: 4 건
```

- (나) `ip_users.json` 에서 `192.0.2.41` 을 쓰는 계정은 <mark style="background:#bde3ff">`junho` 와 `hana` 두 명</mark>이라서 임계값(threshold, 쓰레숄드: 판정 기준이 되는 값) `SHARED_IP_LIMIT`(2) 명 이상에 해당합니다.
  - 그대로 차단했다면 두 사람이 모두 접속하지 못했을 것입니다.
  - 공격으로 의심된 접속이 한 사람의 것이었더라도 다른 사람의 업무가 함께 중단됩니다(부수적 피해).
  - 그래서 자동 차단하지 않고 담당자 승인을 받게 합니다.
- (다) 단계 2 의 만료 시각이 <mark style="background:#bde3ff">120</mark> 이고 단계 3 에서 시계를 120분 뒤로 옮겼습니다. 그러면 시계가 120이 되어 만료 시각 120과 같아집니다. 그래서 `end_time <= clock` 조건이 참이 되었고, 차단이 해제되었습니다.
  - 유효 기간이 있는 임시 차단은 사람의 해제 작업 없이 만료되므로 오래된 차단이 누적되지 않고, 필요하면 다시 차단하면 됩니다. 영구 차단은 사람이 사유를 확인한 뒤에 결정합니다.

**왜**: <mark>차단은 정상 사용자와 필요한 서버의 가용성(availability, 어베일러빌리티: 서비스를 필요할 때 쓸 수 있는 상태)까지 해칠 수 있으므로, 차단 전에 영향 범위를 확인하고 만료 시각을 함께 정해야 안전합니다.</mark>

**자주 틀리는 곳**

- 1번을 비워 두면 허용 목록 확인 함수가 아무것도 리턴하지 않아, 허용 목록에 없는 것으로 판단되어 <mark>**회사의 점검 서버 `192.0.2.10` 이 차단됩니다.**</mark> 단계 1 의 INC-009 줄이 `차단됨` 으로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 1: 차단 요청 3건
INC-005 198.51.100.90 · 차단되지 않음 → 차단됨 · 경로 스캔 (120분 뒤 자동 해제)
INC-009 192.0.2.10 · 차단되지 않음 → 차단됨 · 경로 스캔 (120분 뒤 자동 해제)
INC-008 192.0.2.41 · 변경 없음 → 변경 없음 · 여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요
```

- 2번을 비워 두면 사용 계정 수를 구하지 못해 비교에서 오류가 납니다.

```
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

- 3번을 비워 두면 오류는 나지 않지만 <mark>**차단 실패가 사후 검증에서 드러납니다.**</mark> `차단되지 않음 (확인 실패)` 로 기록됩니다.

```
INC-005 198.51.100.90 · 차단되지 않음 → 차단되지 않음 (확인 실패) · 경로 스캔 (120분 뒤 자동 해제)
```

- 4번을 비워 두면 만료 시각이 없어 시간이 끝난 차단을 푸는 단계에서 오류가 납니다(`KeyError`, 키 에러: 딕셔너리에 없는 키를 꺼냈다는 오류).

```
KeyError: '198.51.100.90'
```

- 5 · 6번을 비워 두면 <mark>**차단이 만료되지 않고 계속 유지됩니다.**</mark> 단계 3 에서 시계가 120분을 가리키는데도 차단한 IP 가 남아 있는 것이 이 실수의 결과입니다.

```
--- 단계 3: 시계를 120분 뒤로 옮기고 시간이 끝난 차단 풀기
차단한 IP: ['198.51.100.90']
```

- 7번을 비워 두면 `refusal` 이 만들어지지 않아 오류가 납니다(`NameError`).

```
NameError: name 'refusal' is not defined
```

- 8 · 9번을 비워 두면 <mark>**아무것도 차단되지 않고 첫 줄의 이유가 빈 문자열로 나옵니다.**</mark>

```
--- 단계 1: 차단 요청 3건
INC-005 198.51.100.90 · 변경 없음 → 변경 없음 · 
INC-009 192.0.2.10 · 변경 없음 → 변경 없음 · 허용 목록 IP 라서 차단하지 않음
INC-008 192.0.2.41 · 변경 없음 → 변경 없음 · 여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요
```

**관제에서는**: 차단 규칙에는 허용 목록(allowlist) 검사와 공유 IP 여부 검사를 함께 둡니다. 두 검사는 차단이 정상 업무에 미치는 영향 범위를 줄입니다. <mark>임시 차단에 만료 시각을 두면 자동 대응이 만든 차단이 계속 늘어나 아무도 관리하지 않게 되는 일을 방지합니다.</mark>

---

### 정답 4-1

**채운 코드** (한 예)

`session_actions.py` 의 1 ~ 3번입니다.

```python
    # 1. state["sessions"][user] 에 빈 리스트를 저장한다 (세션을 모두 종료한다)
    state["sessions"][user] = []  # 그 계정의 세션 리스트를 비운다
        # 2. open_count 가 0 보다 크면 (if, >)
        if open_count > 0:        # 열린 세션이 남아 있으면
        # 3.   gaps 에 user 를 추가한다 (append)
            gaps.append(user)     # 빈틈이 있는 계정으로 모은다
```

`containment.py` 의 4 ~ 6번입니다.

```python
    # 4. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 lock_record 에 저장한다
    lock_record = lock_account(user, state, vip_accounts, incident_id, reason)  # 계정을 먼저 잠그고 기록을 받는다
    # 5. lock_record 의 "after" 가 "잠김" 이면 (if, ==)
    if lock_record["after"] == "잠김":                                          # 잠금이 확인됐으면
    # 6.   terminate_sessions(user, state, incident_id, reason) 의 결과를 records 에 추가한다 (append)
        records.append(terminate_sessions(user, state, incident_id, reason))    # 이어서 세션을 종료하고 기록을 모은다
```

`day03_4-1_run.py` 의 7 ~ 9번입니다.

```python
    # 7. contain_account(user, state, vip_accounts, incident_id, reason) 의 결과를 records 에 저장한다
    records = contain_account(user, state, vip_accounts, incident_id, reason)  # 잠금 → 세션 종료를 하고 기록 리스트를 받는다
# 8. find_open_sessions(state) 의 결과를 gaps_after 에 저장한다
gaps_after = find_open_sessions(state)                                         # 조치 뒤 다시 점검한다
# 9. save_state(state) 를 호출한다 (상태를 파일에 저장한다)
save_state(state)                                                              # 상태를 파일에 저장한다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 3 에서 빈틈이 남은 계정은 <mark style="background:#bde3ff">**없음(`[]`)**</mark>, 단계 4 의 잠긴 계정은 <mark style="background:#bde3ff">**`['junho', 'dami']`**</mark> 입니다.

```
--- 단계 1: 점검 — 잠겼는데 세션이 열려 있는 계정
['junho']
--- 단계 2: 잠금 → 세션 종료
INC-001 dami · 잠기지 않음 → 잠김 · 퇴사한 계정의 서버 요청
INC-001 dami · 세션 2개 → 세션 0개 · 퇴사한 계정의 서버 요청
INC-003 gaeun · 변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
INC-006 junho · 세션 1개 → 세션 0개 · 퇴사 처리 확인
--- 단계 3: 조치 뒤 다시 점검
빈틈이 남은 계정: []
잠긴 계정: ['junho', 'dami']
--- 단계 4: 파일에 저장된 값 다시 읽기
잠긴 계정: ['junho', 'dami']
조치 기록: 5 건
```

- (나) `junho` 는 실습 전부터 <mark style="background:#bde3ff">잠겨 있지만 세션 `S-501` 이 열려 있어</mark> 점검에서 탐지됐습니다. `dami` 는 단계 2 에서 `계정 잠금` 과 `세션 종료`(세션 2개 → 0개) 두 가지를 받았습니다.
  - 잠금만 했다면 `dami` 의 세션 `S-101` · `S-102` 가 유효한 채 남아, 잠금 뒤에도 그 세션으로 서버에 요청할 수 있었을 것입니다.
- (다) `gaeun` 은 `lock_account` 의 기록이 <mark style="background:#bde3ff">`변경 없음 → 변경 없음`</mark> 이라 5번의 `lock_record["after"] == "잠김"` 이 거짓이 되어 세션 종료를 실행하지 않습니다.
  - 잠기지 않은 계정의 세션을 종료하면 정상 사용자의 접속만 중단됩니다. 계정은 잠기지 않았으므로 다시 로그인할 수 있어서, 접속을 차단하는 효과는 없습니다.
  - 특히 VIP 계정은 승인 전에 접속이 종료되면 업무가 중단됩니다.

**왜**: <mark>잠금은 새 로그인만 차단하므로, 이미 열린 세션을 종료하고 잔존 세션(빈틈)이 없는지 재점검해야 봉쇄 조치가 완료됩니다.</mark>

**자주 틀리는 곳**

- 1번을 비워 두면 오류는 나지 않지만 <mark>**세션이 그대로 남습니다.**</mark> 기록이 `세션 2개 → 세션 2개` 로 나오는 것이 이 실수의 결과입니다.

```
--- 단계 2: 잠금 → 세션 종료
INC-001 dami · 잠기지 않음 → 잠김 · 퇴사한 계정의 서버 요청
INC-001 dami · 세션 2개 → 세션 2개 · 퇴사한 계정의 서버 요청
INC-003 gaeun · 변경 없음 → 변경 없음 · VIP 계정이라 자동 조치 대상이 아님
INC-006 junho · 잠김 → 잠김 · 이미 잠겨 있어 변경 없음
INC-006 junho · 세션 1개 → 세션 1개 · 퇴사 처리 확인
```

- 2 · 3번을 비워 두면 점검이 항상 빈 리스트를 리턴해서 <mark>**`junho` 의 빈틈을 탐지하지 못합니다.**</mark>

```
--- 단계 1: 점검 — 잠겼는데 세션이 열려 있는 계정
[]
```

- 5 · 6번을 모두 비워 두면 <mark>**잠금만 하고 세션을 종료하지 않아 빈틈이 남습니다.**</mark> 단계 3 의 재점검에서 `dami` 와 `junho` 가 나오는 것이 이 실수의 결과입니다.

```
--- 단계 1: 점검 — 잠겼는데 세션이 열려 있는 계정
['junho']
…
--- 단계 3: 조치 뒤 다시 점검
빈틈이 남은 계정: ['junho', 'dami']
잠긴 계정: ['junho', 'dami']
```

- 4번을 비워 두면 `lock_record` 가 만들어지지 않아 오류가 납니다(`NameError`).

```
NameError: name 'lock_record' is not defined
```

- 7번을 비워 두면 `records` 가 만들어지지 않아 오류가 납니다(`NameError`).

```
NameError: name 'records' is not defined
```

- 9번을 비워 두면 상태가 저장되지 않아 단계 4 가 이전 실행에서 저장된 파일을 읽거나, 처음 실행이면 파일이 없다는 오류(`FileNotFoundError`)가 납니다.

**관제에서는**: 계정 잠금 뒤에는 열린 세션을 종료하는 것까지가 하나의 봉쇄 조치입니다. <mark>잠긴 계정에 활성 세션이 남았는지 정기적으로 점검하는 것</mark>은 자동 대응의 누락을 탐지하는 방법 중 하나입니다.
