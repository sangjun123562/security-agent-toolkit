# 11/10(화) 오전 · 5과목 자동 대응(SOAR) ② — 알림에 맥락 붙이기 · 조건에 따라 처리 경로 나누기 · 자동 대응에 안전장치 걸기 — 실습

깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 새 문법은 3교시의 **두 값을 한 번에 리턴하고 받기**(튜플 리턴과 언패킹)와 4교시의 **글자의 앞부분 확인하기**(`startswith`) 둘입니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기는 미리 채운 줄에 맞춥니다. 각 번호 주석 바로 아래에 한 줄을 씁니다. 주석은 지우지 않습니다.

📎 **이전 파일**: 어제 만든 `incident.py` · `playbook_runner.py` · `incident_samples.json` · `config/playbook_registry.json` 을 씁니다. 없는 파일은 `complete_files.md` 의 해당 절에서 복사합니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 어제 파일을 확인합니다. <mark>`ls` 결과에 `config` · `incident.py` · `incident_samples.json` · `playbook_runner.py` 가 보이면</mark> 됩니다.
   ```bash
   pwd
   cd soar_response
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day02_am_context_route_safety.md`, `day02_am_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 데이터 파일 세 개를 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch users_info.json source_ips.json trusted_ips.json
   ls
   ```

**`users_info.json`** — 계정 이름마다 재직 여부(`employed`)와 VIP 계정(VIP account, 브이아이피 계정: 막히면 업무에 큰 영향을 주는 중요한 계정) 여부(`vip`)를 적은 파일입니다. `true` 는 「그렇다」, `false` 는 「아니다」입니다. 실제 회사에서는 인사 · 계정 관리 시스템이 갖고 있는 정보이고, 오늘은 파일로 대신합니다. `dami` 는 퇴사(`employed` 가 `false`), `gaeun` 은 VIP(`vip` 가 `true`)입니다. 2 ~ 4교시가 읽습니다.

```
{
  "dami": {"employed": false, "vip": false},
  "seoyeon": {"employed": true, "vip": false},
  "gaeun": {"employed": true, "vip": true},
  "jiwoo": {"employed": true, "vip": false},
  "junho": {"employed": true, "vip": false},
  "hana": {"employed": true, "vip": false}
}
```

**`source_ips.json`** — 사용자 이름마다 로그인한 접속 IP 를 적은 파일입니다. 이 파일에 이름이 없는 사용자는 접속 IP 가 기록되어 있지 않은 사용자입니다. 2교시가 읽습니다.

```
{
  "seoyeon": "203.0.113.80",
  "jiwoo": "203.0.113.80",
  "gaeun": "198.51.100.77",
  "junho": "192.0.2.41"
}
```

**`trusted_ips.json`** — **신뢰 IP**(trusted IP, 트러스티드 아이피: 정상 접속이 오는 곳이라고 미리 확인해 둔 IP) 목록입니다. 협력사 사무실 IP 한 개가 들어 있고, `seoyeon` 과 `jiwoo` 가 이 IP 에서 접속합니다. 2교시가 읽습니다.

```
[
  "203.0.113.80"
]
```

5. **[터미널]** 두 가지를 확인합니다. 먼저 데이터 파일입니다. <mark>`6 4 1` 이 나와야</mark> 합니다.
   ```bash
   python -c "import json; print(len(json.load(open('users_info.json', encoding='utf-8'))), len(json.load(open('source_ips.json', encoding='utf-8'))), len(json.load(open('trusted_ips.json', encoding='utf-8'))))"
   ```
6. **[터미널]** 어제 만든 플레이북(playbook, 플레이북: 알림 종류별로 어떤 대응을 할지 미리 적어 둔 절차)의 값을 확인합니다. 오늘 출력이 문서와 같게 나오려면 이 값이 <mark>아래 출력과 같아야</mark> 합니다. 다르면 `config/playbook_registry.json` 을 열어 해당 값을 같게 고칩니다(어제 내 파일은 깃허브에 올라가 있습니다).
   ```bash
   python -c "import json; print([(p['id'], p['trigger_rule'], p['min_grade'], p['approval']) for p in json.load(open('config/playbook_registry.json', encoding='utf-8'))])"
   ```
   ```
   [('PB-001', '퇴사한 계정', 'high', '자동'), ('PB-002', '대량 다운로드', 'mid', '담당자 승인 필요'), ('PB-003', '경로 스캔', 'low', '담당자 승인 필요')]
   ```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'incident'` 는 <mark>어제 만든 `incident.py` 가 이 폴더에 없다는 뜻</mark>입니다. `complete_files.md` 에서 복사합니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 알림에 대상의 재직 · VIP · 접속 IP 맥락 붙이기 (보강)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 월요일에 만든 프로그램은 알림이 오면 대상 계정을 바로 잠갔습니다(그 계정으로 로그인하지 못하게 막았습니다). 오늘 샘플 알림 5건 가운데 세 건은 사정이 모두 다릅니다.
>   - `INC-001`(알림 한 건에 붙인 번호): 퇴사한 `dami` 의 계정입니다. 막아도 업무에 지장이 없습니다.
>   - `INC-003`: `gaeun` 은 직원들의 계정을 관리하는 사람입니다. 이 계정이 막히면 계정 관리 업무가 멈춥니다. 이 계정처럼 막히면 업무에 큰 영향을 주는 중요한 계정을 **VIP 계정**이라고 합니다.
>   - `INC-004`: `jiwoo` 는 협력사 사무실에서 평소처럼 접속했을 뿐입니다. 막을 이유가 없습니다.
> - **문제**: 프로그램은 알림에 적힌 이름과 등급만 봅니다. 퇴사했는지, 중요한 계정인지, 믿을 만한 곳에서 접속했는지 모른 채 세 건을 모두 같은 방식으로 막습니다.
> - **부탁**: 조치하기 전에 「이 사람이 누구이고 어디서 접속했나」를 알림마다 먼저 알아내서 붙여 주세요.
> - **바뀌는 점**: 알림마다 「바로 잠글지, 담당자에게 물을지」를 정할 때 이름이 아니라 알림에 붙은 정보(맥락)를 봅니다. 상황과 이름은 설명을 위한 예시입니다.
> - **용어**: **인시던트**(incident, 인시던트: 사람이 확인하고 대응해야 하는 사건 한 건)입니다. 이 문서에서는 알림 한 건을 인시던트 한 건으로 셉니다. `INC-001` 의 `INC` 는 incident 의 앞 세 글자입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 2.1 보강 — 조치하기 전에 알림에 정보를 붙인다

알림 한 건에 `context`(맥락)라는 딕셔너리를 붙입니다. 이 일을 **보강**(enrichment, 인리치먼트: 판단에 도움이 되는 정보를 알림에 더 붙이는 것)이라고 합니다. 알림이 가리키는 사용자 이름 또는 IP 를 알림 대상이라고 하고, 코드에서는 `entity` 라고 부릅니다. `context` 에는 알림 대상에 대한 정보 다섯 가지가 들어갑니다. 아래 표의 예는 VIP 계정인 `gaeun` 의 경우입니다.

| 키(이름표) | 알려 주는 것 | `gaeun` 의 값 | 정보를 못 찾으면 |
|---|---|---|---|
| `account_known` | 계정 정보 파일에 이 이름이 있는가 | `True`(있다) | `False`(IP 주소처럼 계정이 아닌 대상) |
| `employed` | 지금 재직 중인가 | `True`(재직) | `False` |
| `vip` | VIP 계정인가 | `True`(VIP 다) | `False` |
| `source_ip` | 로그인한 접속 IP | `198.51.100.77` | `None`(값이 없다) |
| `ip_trusted` | 그 IP 가 신뢰 IP 목록에 있는가 | `False`(목록에 없다) | `False` |

- **값을 읽는 파일**: `account_known` · `employed` · `vip` 는 `users_info.json`, `source_ip` 는 `source_ips.json`, `ip_trusted` 는 `source_ips.json` 에서 구한 접속 IP 가 `trusted_ips.json` 목록 안에 있으면 `True`, 없으면 `False` 입니다.
- **`True` · `False` · `None`**: `True` 는 「그렇다」, `False` 는 「아니다」, `None` 은 「값이 없다」입니다.
- **정보를 못 찾았을 때**: 일단 「모른다」 쪽 값(`False` 또는 `None`)으로 시작합니다. 모르는 대상을 재직 중인 정상 사용자로 보면 안 되기 때문입니다.
- **조심할 점**: 계정 정보에 없는 대상의 `employed` · `vip` 가 `False` 여도 「퇴사했다」나 「VIP 가 아니다」라는 뜻이 아니라, 「계정 정보에 없어서 모른다」는 뜻입니다.

함수 세 개가 각각 다른 일을 하고, 직접 쓰는 곳은 **아홉 군데**입니다.

```
enrichment.py   lookup_account   : 대상이 users_info 안에 있으면 재직 · VIP 를 담는다 (1 ~ 3번)
                lookup_source_ip : 대상이 source_ips 안에 있으면 접속 IP 와 신뢰 IP 여부를 담는다 (4 ~ 6번)
                enrich_incident  : 두 결과를 합쳐 incident["context"] 에 붙인다 (미리 채움)
실행 파일       day02_2-1_run.py : 알림마다 맥락을 붙이는 함수를 호출하고 (7번), VIP 이면 (8번) VIP 알림 수를 1 늘린다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 2-1 · 알림 5건에 재직 · VIP · 접속 IP 맥락을 붙이고 VIP 알림 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 5건에는 대상의 이름과 등급만 있어서 퇴사자 · VIP · 믿을 만한 IP 에서 온 접속을 구별할 수 없습니다</mark>.
- **만드는 것**: 계정 정보 찾기와 접속 IP 정보 찾기(`enrichment.py`), 맥락 붙이기 호출과 VIP 알림 수 세기(`day02_2-1_run.py`).
- **실행하면**: <mark>단계 1: 불러온 개수, 단계 2: 알림마다 붙인 정보, 단계 3: VIP 계정 알림 수가 나옵니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 · 3 을 읽습니다.

**`enrichment.py`** — 알림에 맥락을 붙입니다. 3교시 실행 파일도 `enrich_incident` 를 불러다 씁니다. 직접 쓰는 곳은 1 ~ 6번입니다.

```python
def lookup_account(entity, users_info):                              # 대상 이름과 계정 정보 딕셔너리를 받는 함수
    """계정 정보 파일에서 이 대상이 재직 중인지, VIP 계정인지 찾아 딕셔너리로 리턴한다.
    파일에 이름이 없는 대상(IP 등)은 처음 값(False)을 그대로 리턴한다.
    """
    account = {"employed": False, "vip": False}                      # 처음에는 모르는 상태로 시작한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. entity 가 users_info 안에 있으면 (if, in)
    # 2.   account 의 "employed" 에 users_info[entity]["employed"] 를 담는다
    # 3.   account 의 "vip" 에 users_info[entity]["vip"] 를 담는다
    return account                                                   # 계정 정보를 리턴한다


def lookup_source_ip(entity, source_ips, trusted_ips):               # 대상 이름 · 접속 IP 딕셔너리 · 신뢰 IP 리스트를 받는 함수
    """이 대상이 접속한 IP 와, 그 IP 가 신뢰 IP 목록에 있는지 찾아 딕셔너리로 리턴한다.
    접속 IP 를 모르는 대상은 처음 값(None 과 False)을 그대로 리턴한다.
    """
    ip_info = {"source_ip": None, "ip_trusted": False}               # 처음에는 모르는 상태로 시작한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. entity 가 source_ips 안에 있으면 (if, in)
    # 5.   ip_info 의 "source_ip" 에 source_ips[entity] 를 담는다
    # 6.   ip_info 의 "ip_trusted" 에 source_ips[entity] 가 trusted_ips 안에 있는지(in)의 결과를 담는다
    return ip_info                                                   # 접속 IP 정보를 리턴한다


def enrich_incident(incident, users_info, source_ips, trusted_ips):  # 인시던트 · 계정 정보 · 접속 IP 딕셔너리 · 신뢰 IP 리스트를 받는 함수
    """위 두 함수가 찾은 정보를 모아 알림에 context 라는 이름으로 붙이고, 붙인 알림을 리턴한다.
    붙이고 나면 알림만 봐도 퇴사 · VIP · 접속 IP 를 알 수 있어서, 조치하기 전에 확인할 때 쓴다.
    """
    entity = incident["entity"]                                      # 대응할 대상(사용자 이름 또는 IP)
    account = lookup_account(entity, users_info)                     # 계정 정보를 찾는다
    ip_info = lookup_source_ip(entity, source_ips, trusted_ips)      # 접속 IP 정보를 찾는다
    account_known = entity in users_info                             # 계정 정보에 있는 대상인지 구한다
    context = {"account_known": account_known, "employed": account["employed"], "vip": account["vip"], "source_ip": ip_info["source_ip"], "ip_trusted": ip_info["ip_trusted"]}  # 다섯 가지 맥락을 합친다
    incident["context"] = context                                    # 인시던트에 맥락을 붙인다
    return incident                                                  # 맥락이 붙은 인시던트를 리턴한다
```

**`day02_2-1_run.py`** — 7 ~ 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 파일을 저장하지는 않습니다.

```python
from incident import load_json, INCIDENTS_PATH                 # 월요일 파일의 함수를 불러온다
from enrichment import enrich_incident                         # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                          # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                      # 계정 정보 파일을 딕셔너리로 읽는다
source_ips = load_json("source_ips.json")                      # 알림이 난 접속의 IP 파일을 딕셔너리로 읽는다
trusted_ips = load_json("trusted_ips.json")                    # 신뢰 IP 파일을 리스트로 읽는다
incident_count = len(incidents)                                # 인시던트가 몇 건인지 센다
user_count = len(users_info)                                   # 계정 정보가 몇 명인지 센다
trusted_count = len(trusted_ips)                               # 신뢰 IP 가 몇 개인지 센다
print("--- 단계 1: 불러온 알림", incident_count, "건 · 계정 정보", user_count, "명 · 신뢰 IP", trusted_count, "개")  # 단계 1 시작을 알리는 줄

print("--- 단계 2: 알림마다 붙인 정보(재직 · VIP · 접속 IP)")  # 단계 2 시작을 알리는 줄
for incident in incidents:                                     # 인시던트를 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. enrich_incident(incident, users_info, source_ips, trusted_ips) 를 호출한다 (인시던트에 맥락이 붙는다)
    context = incident["context"]                              # 붙은 맥락을 꺼낸다
    if context["account_known"]:                               # 계정 정보가 있으면
        if context["employed"]:                                # 재직 중이면
            employed_text = "재직"                             # 재직이라고 적는다
        else:                                                  # 아니면
            employed_text = "퇴사"                             # 퇴사라고 적는다
    else:                                                      # 계정 정보가 없으면
        employed_text = "계정 아님"                            # 계정이 아니라고 적는다
    vip_text = "아니오"                                        # 처음에는 아니오로 적는다
    if context["vip"]:                                         # VIP 이면
        vip_text = "예"                                        # 예라고 적는다
    ip_text = "없음"                                           # 처음에는 없음으로 적는다
    if context["source_ip"]:                                   # 접속 IP 가 있으면
        ip_text = context["source_ip"]                         # 그 IP 를 적는다
    trusted_text = "아니오"                                    # 처음에는 아니오로 적는다
    if context["ip_trusted"]:                                  # 신뢰 IP 이면
        trusted_text = "예"                                    # 예라고 적는다
    print(incident["id"], incident["entity"], "· 재직:", employed_text, "· VIP:", vip_text, "· 접속 IP:", ip_text, "· 신뢰 IP:", trusted_text)  # 한 줄로 출력한다

print("--- 단계 3: VIP 계정 알림 수")                          # 단계 3 시작을 알리는 줄
vip_count = 0                                                  # VIP 계정 알림 수 : 처음에는 0 이다
for incident in incidents:                                     # 인시던트를 하나씩 꺼낸다
    context = incident["context"]                              # 붙은 맥락을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. context 의 "vip" 가 참이면 (if)
    # 9.   vip_count 에 vip_count + 1 을 담는다 (1 늘린다)
print("VIP 계정 알림", vip_count, "건")                        # VIP 계정 알림 수를 출력한다
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch enrichment.py day02_2-1_run.py
   ls
   ```
2. **[VS Code]** `enrichment.py` 1 ~ 6번, `day02_2-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day02_2-1_run.py
   ```
4. 출력은 세 단계입니다. 단계 1 은 숫자가 제목 줄에 함께 나옵니다. 단계 2 는 알림 5건이 한 줄씩 나오고 한 줄에는 번호 · 대상 · 재직 · VIP · 접속 IP · 신뢰 IP 가 순서대로 있습니다. 단계 3 은 1줄입니다.
5. **[보고서]** `day02_am_report.md` 의 `## 2교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 재직 여부가 「퇴사」인 알림과 VIP 가 「예」인 알림의 번호, 단계 3 의 VIP 계정 알림 수를 적어 주세요.
   - (나) 🔍 INC-005 는 맥락이 모두 처음 값(`False` · `None`)으로 남았습니다. 왜 그렇게 나왔는지 `lookup_account` 와 `lookup_source_ip` 의 `if` 조건을 근거로 적어 주세요. 또 INC-005 의 `employed` 가 `True`(재직)로 나온다면 어떤 문제가 생길지도 적어 주세요.
   - (다) 🔍 INC-002 와 INC-004 는 접속 IP 가 같고 둘 다 「신뢰 IP: 예」입니다. 두 알림의 `reasons`(알림이 난 이유인 탐지 규칙 이름 목록)를 비교해 보세요. 접속 IP 가 같은 신뢰 IP 라는 이유만으로 두 알림을 똑같이 처리해도 되는지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 딕셔너리에 그 이름(키)이 있는지 | `if entity in users_info:` |
| 딕셔너리 안의 딕셔너리 값 꺼내기 (`users_info["gaeun"]["vip"]` 는 `True`) | `users_info[entity]["employed"]` |
| 딕셔너리에 값 저장하기 | `account["vip"] = users_info[entity]["vip"]` |
| 리스트 안에 있는지 확인한 결과(`True` · `False`) 담기 | `ip_info["ip_trusted"] = source_ips[entity] in trusted_ips` |
| 함수 호출하기 | `enrich_incident(incident, users_info, source_ips, trusted_ips)` |
| 1 늘려 다시 저장하기 | `vip_count = vip_count + 1` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 맥락을 보고 승인 필요 · 오탐 종료 · 기본 경로로 나누기 (조건 분기)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 지난주 협력사 사무실(`203.0.113.80`)에서 온 `평소와 다른 IP` 알림이 12건 있었습니다. 분석팀이 한 건씩 열어 확인했고 12건 모두 평소 업무였습니다. 12건을 확인하는 데 1시간이 들었습니다(한 건당 5분).
> - **문제**:
>   - 그 1시간 동안 다른 알림을 확인하는 일이 늦어졌습니다.
>   - 반대로 계정 관리자 `gaeun`(VIP 계정)의 알림이 와도 지금은 일반 계정과 같은 절차로 처리됩니다. 이 계정이 잘못 막히면 직원들의 계정 관리 업무가 멈춥니다.
> - **부탁**: 협력사의 정상 접속 알림은 이유를 적어 두고 자동으로 닫아(처리를 끝내) 주세요. 이처럼 실제로는 위협이 아닌데 위협이라고 알린 알림을 **오탐**(false positive, 폴스 포지티브)이라고 합니다. VIP 계정은 담당자가 허락한 뒤에만 처리해 주세요.
> - **바뀌는 점**: 분석팀은 아낀 1시간에 위험한 알림을 확인합니다. VIP 계정은 담당자가 허락하기 전에는 처리되지 않습니다. 오늘 샘플에서는 5건 가운데 `INC-004` 한 건이 자동으로 닫히고 `INC-003` 한 건이 담당자 확인으로 넘어갑니다. 12건과 5분은 설명을 위한 예시 숫자입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 3.1 조건 분기 — 맥락에 따라 다른 처리 경로로 보낸다

알림을 조건에 따라 세 가지 처리 경로 가운데 하나로 나눕니다. 이것을 **조건 분기**(branching, 브랜칭)라고 합니다.

| 경로 | 보내는 조건 | 하는 일 | 오늘 샘플 |
|---|---|---|---|
| `승인 필요` | 대상이 VIP 계정이다 | 담당자가 확인하기 전에는 조치하지 않는다 | `INC-003`(`gaeun`) |
| `오탐 종료` | 접속 IP 가 신뢰 IP 이고, 탐지된 규칙이 **모두** IP 관련 규칙이다 | 상태(알림을 어디까지 처리했는지 나타내는 값)를 `분류됨` 으로, 이어서 `종료` 로 바꾸고 이유를 기록한다 | `INC-004`(`jiwoo`) |
| `기본` | 위 두 경우가 아니다 | 어제 만든 플레이북 절차대로 처리한다 | `INC-001` · `INC-002` · `INC-005` |

- **탐지된 규칙**: 알림에는 `reasons` 라는 리스트가 있고, 이 리스트에는 이 알림이 나게 한 탐지 규칙(알림을 내는 조건)의 이름이 들어 있습니다. 예를 들어 `INC-002` 는 `["평소와 다른 IP", "대량 다운로드"]` 입니다.
- **IP 관련 규칙**: 접속 IP 를 보고 낸 규칙입니다. 오늘은 `평소와 다른 IP` 와 `업무 시간 밖 로그인` 두 가지입니다.

- **상태**는 알림을 어디까지 처리했는지 나타내는 값이고, `탐지됨` → `분류됨` → `조치됨` 또는 `종료` 순서로 바뀝니다.
- <mark>VIP 를 먼저 확인합니다.</mark> VIP 계정의 알림이 신뢰 IP 에서 접속했다는 이유만으로 자동으로 닫히면 안 되기 때문입니다.
- <mark>탐지된 규칙이 **모두** IP 관련일 때만 닫습니다.</mark> 믿을 만한 IP 에서 접속했어도 `대량 다운로드` 처럼 IP 와 상관없는 규칙이 함께 걸렸다면, 그 다운로드가 정상이라는 근거는 되지 못하기 때문입니다. `INC-002` 가 그런 경우입니다.

**🐍 문법 상자 — 튜플 리턴과 언패킹(tuple unpacking): 두 값을 한 번에 리턴하고 한 번에 받는다**

```python
def check(score):
    if score >= 60:
        return "높음", "바로 확인"
    return "낮음", "나중에 확인"

level, action = check(70)
print(level)
print(action)
```

| 코드 | 뜻 |
|---|---|
| `return "높음", "바로 확인"` | 값 두 개를 쉼표로 이어 함께 리턴한다. 이렇게 쉼표로 이은 값 묶음을 **튜플**(tuple)이라고 한다 |
| `level, action = check(70)` | 튜플로 온 두 값을 순서대로 변수 두 개에 하나씩 저장한다. 이렇게 묶음을 풀어 변수에 저장하는 것을 **언패킹**(unpacking)이라고 한다 |
| 위 코드의 출력 | `높음` 과 `바로 확인` 이 한 줄씩 나온다 |

- 리턴하는 값의 개수와 받는 변수의 개수가 다르면 `ValueError`(밸류 에러: 값의 개수나 형태가 맞지 않을 때 나는 오류)가 납니다.

직접 쓰는 곳은 함수와 실행 파일을 합쳐 **아홉 군데**입니다.

```
routing.py   is_only_ip_related : 규칙을 하나씩 꺼내 IP 관련이 아닌 것이 있으면 False 를 리턴한다 (1 ~ 3번)
             decide_route       : VIP 이면 「승인 필요」 (4 · 5번) / 신뢰 IP 이고 규칙이 모두 IP 관련이면 「오탐 종료」 (6 · 7번) / 아니면 「기본」 (미리 채움)
             apply_route        : 오탐 종료이면 상태를 종료로 옮기고 이유를 기록한다 (미리 채움)
실행 파일    day02_3-1_run.py   : decide_route 가 리턴한 두 값을 언패킹으로 받고 (8번), 경로별 건수를 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 3-1 · VIP 는 승인 경로로, 신뢰 IP 의 IP 관련 알림은 오탐으로 종료하고 경로별로 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 5건이 모두 같은 절차로 처리되므로 계정 관리자(VIP)의 알림과 협력사의 정상 접속 알림을 따로 다룰 수 없습니다</mark>.
- **만드는 것**: 규칙이 모두 IP 관련인지 확인하기와 경로 정하기(`routing.py`), 경로 받기와 경로별 건수 세기(`day02_3-1_run.py`). 경로를 정할 때마다, 그렇게 정한 이유도 문장으로 함께 리턴합니다.
- **실행하면**: <mark>단계 1: 알림마다 경로 · 이유 · 상태, 단계 2: 경로별 건수가 나옵니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 1 · 2 를 읽습니다.

**`routing.py`** — 맥락을 보고 처리 경로를 정합니다. 이 파일이 정한 경로(`승인 필요` · `오탐 종료` · `기본`)를 오후 5교시 이후에도 씁니다. 직접 쓰는 곳은 1 ~ 7번입니다.

```python
from incident import change_status                                          # 월요일 파일의 상태 바꾸기 함수를 불러온다

IP_RELATED_RULES = ["평소와 다른 IP", "업무 시간 밖 로그인"]                # 접속 IP 만 보고 낸 알림의 규칙 이름


def is_only_ip_related(incident):                                           # 인시던트 하나를 받는 함수
    """알림이 난 이유(규칙)가 모두 IP 와 관련된 것이면 True, 하나라도 다른 이유가 있으면 False 를 리턴한다.
    IP 때문에만 난 알림인지, 다른 증거도 있는 알림인지 구별할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. incident["reasons"] 의 규칙을 하나씩 꺼낸다 (for, rule)
    # 2.   rule 이 IP_RELATED_RULES 안에 없으면 (if, not in)
    # 3.     False 를 리턴한다 (IP 와 관계없는 다른 증거가 있다)
    return True                                                             # 모두 IP 관련이면 True 를 리턴한다 — 미리 채운 줄


def decide_route(incident):                                                 # 맥락이 붙은 인시던트를 받는 함수
    """붙어 있는 맥락을 보고 이 알림을 어느 경로(승인 필요 · 오탐 종료 · 기본)로 보낼지 정해, 이유 문장과 함께 리턴한다.
    같은 플레이북이어도 누구의 알림이냐에 따라 처리를 다르게 하고 싶을 때 쓴다.
    """
    context = incident["context"]                                           # 붙어 있는 맥락
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. context 의 "vip" 가 참이면 (if)
    # 5.   "승인 필요" 와 "VIP 계정이라 담당자 승인이 필요함" 을 쉼표로 이어 함께 리턴한다
    # 6. context 의 "ip_trusted" 가 참이고(and) is_only_ip_related(incident) 가 참이면 (if)
    # 7.   "오탐 종료" 와 "신뢰 IP 에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄" 을 쉼표로 이어 함께 리턴한다
    return "기본", "플레이북 기본 절차대로 처리함"                          # 어느 경우도 아니면 기본 경로로 보낸다


def apply_route(incident, route, reason, incident_log):                     # 인시던트 · 경로 · 이유 · 기록 리스트를 받는 함수
    """정한 경로를 알림에 적용한다. 오탐 종료이면 상태를 분류됨을 거쳐 종료로 바꾸고, 경로와 이유를 기록에 남긴다.
    나중에 「왜 이 알림을 이렇게 처리했나」에 답할 수 있게 하려고 쓴다.
    """
    if route == "오탐 종료":                                                # 오탐 종료이면
        change_status(incident, "분류됨")                                   # 먼저 분류됨으로 옮기고
        change_status(incident, "종료")                                     # 종료로 옮긴다
    entry = {"incident": incident["id"], "route": route, "reason": reason}  # 기록 한 건을 만든다
    incident_log.append(entry)                                              # 기록 리스트에 추가한다
```

**`day02_3-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 2교시의 `enrichment.py` 가 같은 폴더에 있어야 합니다.

```python
from incident import load_json, INCIDENTS_PATH                      # 월요일 파일의 함수를 불러온다
from enrichment import enrich_incident                              # 2교시에 만든 함수를 불러온다
from routing import decide_route, apply_route                       # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                               # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                           # 계정 정보 파일을 읽는다
source_ips = load_json("source_ips.json")                           # 알림이 난 접속의 IP 파일을 읽는다
trusted_ips = load_json("trusted_ips.json")                         # 신뢰 IP 파일을 읽는다
incident_log = []                                                   # 경로 기록을 담을 빈 리스트
route_counts = {"기본": 0, "승인 필요": 0, "오탐 종료": 0}          # 경로마다 몇 건인지 셀 딕셔너리

print("--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태")          # 단계 1 시작을 알리는 줄
for incident in incidents:                                          # 인시던트를 하나씩 꺼낸다
    enrich_incident(incident, users_info, source_ips, trusted_ips)  # 맥락을 붙인다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. decide_route(incident) 가 리턴한 두 값을 route 와 reason 에 한 번에 받는다
    apply_route(incident, route, reason, incident_log)              # 경로를 적용하고 기록한다
    # 9. route_counts[route] 에 route_counts[route] + 1 을 담는다 (그 경로의 건수를 1 늘린다)
    print(incident["id"], incident["entity"], incident["grade"], "->", route, "·", reason, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 2: 경로별 건수")                                    # 단계 2 시작을 알리는 줄
for route in route_counts:                                          # 경로를 하나씩 꺼낸다
    print(route, route_counts[route], "건")                         # 경로와 건수를 출력한다
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch routing.py day02_3-1_run.py
   ls
   ```
2. **[VS Code]** `routing.py` 1 ~ 7번, `day02_3-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day02_3-1_run.py
   ```
4. 출력은 두 단계입니다. 단계 1 은 알림 5건이 한 줄씩 나오고 한 줄에는 번호, 대상, 등급이 나오고 `->` 뒤에 경로, 이유, 괄호 안에 상태가 순서대로 나옵니다. 단계 2 는 경로마다 한 줄씩 3줄입니다.
5. **[보고서]** `day02_am_report.md` 의 `## 3교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 경로별 건수와 `종료` 상태가 된 알림의 번호를 적어 주세요.
   - (나) 🔍 INC-002 와 INC-004 는 둘 다 신뢰 IP 에서 접속했는데 INC-002 는 `기본`, INC-004 는 `오탐 종료` 입니다. 두 알림의 `reasons` 를 근거로 경로가 갈린 이유를 적어 주세요.
   - (다) 🔍 6번 조건을 확인하기 전에 4번 VIP 확인을 먼저 두었습니다. VIP 계정이 신뢰 IP 에서 접속했고 `평소와 다른 IP` 규칙 하나만 걸렸다고 해 봅시다. 이 알림이 어느 경로로 가는지 적어 주세요. 그리고 4번과 6번 조건의 순서를 바꾸면 무엇이 달라지는지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 하나씩 꺼내기 | `for rule in incident["reasons"]:` |
| 리스트 안에 없으면 | `if rule not in IP_RELATED_RULES:` |
| 참이면 | `if context["vip"]:` |
| 두 조건이 모두 참이면 | `if context["ip_trusted"] and is_only_ip_related(incident):` |
| 값 두 개를 함께 리턴 | `return "승인 필요", "VIP 계정이라 담당자 승인이 필요함"` |
| 리턴된 값 두 개를 한 번에 받기(언패킹) | `route, reason = decide_route(incident)` |
| 1 늘려 다시 저장하기 | `route_counts[route] = route_counts[route] + 1` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 같은 알림을 두 번 처리하지 않고 한 번에 잠글 수 있는 계정 수 제한하기 (안전장치)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 월요일에 만든 실행기(플레이북의 액션을 실제로 실행하는 프로그램)는 같은 알림 파일을 두 번 처리하면 `dami` 계정을 두 번 잠그고 티켓(ticket, 티켓: 담당자에게 일을 맡기려고 만드는 작업 요청 기록)을 두 번 만듭니다. 더 큰 문제는 인사 시스템의 오류입니다. 직원 전체가 퇴사자로 잘못 표시되면 퇴사자 알림이 한꺼번에 들어옵니다. 오늘 샘플에서는 이런 알림 7건(계정 6개)이 몰립니다.
> - **문제**: 실행기는 알림 수만큼 계정을 모두 막습니다. 7건이 몰리면 서로 다른 계정 6개가 막히고, 100건이 몰리면 100개가 막힙니다. 이 샘플에서 실제 퇴사자는 `dami` 한 명뿐입니다.
> - **부탁**: 이미 끝난 인시던트는 다시 처리하지 말고, 이미 잠긴 계정은 다시 잠그지 마세요. 또 한 번 실행할 때 잠글 수 있는 계정은 최대 3개로 제한해 주세요.
> - **바뀌는 점**: 같은 알림을 두 번 처리해도 `dami` 는 한 번만 잠기고, 알림이 몰려도 잠기는 계정이 3개를 넘지 않습니다. 그 사이에 담당자가 확인할 시간이 생깁니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 4.1 안전장치 두 가지

안전장치는 실행기가 액션(계정 잠금처럼 대응으로 하는 동작 하나)을 실행하기 전에 「이걸 지금 해도 되나」를 한 번 더 확인하는 장치입니다. 코드에 나오는 말은 이렇습니다.

- **`state`**: 모의 시스템(실제 회사 시스템이 아니라 연습용으로 흉내 낸 시스템)의 지금 상태입니다. 잠긴 계정(`locked_users`) · 차단한 IP · 티켓이 들어 있는 딕셔너리입니다.
- **`DONE_STATUSES`**: 대응이 이미 끝난 상태 `조치됨` · `보고됨` · `종료` 를 모은 리스트입니다.
- **`MAX_LOCKS_PER_RUN`**: 한 번 실행에서 잠글 수 있는 계정의 최대 수이고 값은 3입니다.

| 안전장치 | 막는 일 | 오늘 실습에서 |
|---|---|---|
| **중복 실행 방지**(멱등성, idempotency, 아이뎀포턴시: 같은 일을 여러 번 해도 한 번 한 것과 결과가 같게 하는 것) | 같은 알림이 두 번 와서 같은 대응을 두 번 하는 일 | 이미 끝난 인시던트는 실행하지 않고(미리 채움), 이미 잠긴 계정은 다시 잠그지 않는다 (1 · 2번) |
| **영향 범위 제한**(blast radius limit, 블라스트 레이디어스 리밋: 잘못됐을 때 피해가 퍼지는 범위의 최대치를 정해 두는 것) | 잘못된 입력으로 계정이 대량으로 잠기는 일 | 한 번 실행에서 잠글 수 있는 계정을 `MAX_LOCKS_PER_RUN`(3개)까지만 허용한다 (3 · 4번) |

- 한도는 **틀린 알림을 찾아내지는 못합니다.** 틀린 알림이 들어와도 잠기는 계정이 3개를 넘지 않게 할 뿐이고, 한도를 넘은 건은 「담당자 확인 필요」라고 기록에 남깁니다.
- 오늘 `bulk_incidents.json` 은 인사 오류로 몰린 퇴사자 알림 7건(계정 6개, `dami` 알림이 두 건)입니다. `users_info.json` 의 `employed` 를 보면 <mark>실제 퇴사자는 `dami` 한 명뿐입니다.</mark>

**🐍 문법 상자 — `startswith` 는 글자가 어떤 말로 시작하는지 확인한다**

```python
result_text = "건너뜀: 이미 잠겨 있음"
print(result_text.startswith("건너뜀"))
print(result_text.startswith("실행"))
```

| 코드 | 결과 | 뜻 |
|---|---|---|
| `result_text.startswith("건너뜀")` | `True` | 글자가 「건너뜀」으로 시작한다 |
| `result_text.startswith("실행")` | `False` | 「실행」으로 시작하지 않는다 |

직접 쓰는 곳은 함수와 실행 파일을 합쳐 **아홉 군데**입니다.

```
safe_runner.py   find_skip_reason : 이미 잠긴 계정이면 (1 · 2번), 잠근 계정 수가 한도 이상이면 (3 · 4번) 건너뛸 이유를 리턴한다
                 safe_run_action  : 이유가 있으면 그 이유를 리턴하고 (5 · 6번), 없으면 어제의 run_action 으로 실행한다 (7번)
                 run_playbook_safe · process_safe : 결과를 이미 처리됨 · 승인 대기 · 일부 건너뜀 · 실행 완료로 나누고, 결과마다 몇 건인지 센다 (미리 채움)
실행 파일        day02_4-1_run.py : 기록에서 「건너뜀」으로 시작하는 결과만 골라 출력한다 (8 · 9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 4-1 · 중복 실행을 막고 한 번에 잠글 수 있는 계정을 3개로 제한하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>같은 알림을 두 번 처리하면 계정이 두 번 잠기고, 인사 오류 알림이 몰리면 모든 계정이 잠깁니다</mark>.
- **만드는 것**: 건너뛸 이유 찾기와 안전한 액션 실행(`safe_runner.py`), 건너뛴 액션 골라 출력(`day02_4-1_run.py`).
- **실행하면**: <mark>단계 1 ~ 2: 어제 방식의 결과, 단계 3 ~ 4: 안전한 방식의 결과, 마지막에 건너뛴 액션과 이유가 나옵니다.</mark>

**🎯 할 일**: 파일 세 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 어제 방식과 안전한 방식의 차이를 읽습니다.

**`bulk_incidents.json`** — 인사 시스템 오류로 몰린 퇴사자 알림 7건입니다(모두 `퇴사한 계정` · `high`). `INC-B01` 과 `INC-B02` 는 같은 계정 `dami` 의 알림으로, 번호가 다른 알림 두 건이 같은 계정을 가리키는 경우를 일부러 만들어 둔 것입니다.

```
[
  {"id": "INC-B01", "entity": "dami", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B02", "entity": "dami", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B03", "entity": "seoyeon", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B04", "entity": "gaeun", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B05", "entity": "jiwoo", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B06", "entity": "junho", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-B07", "entity": "hana", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"}
]
```

**`safe_runner.py`** — 안전장치를 건 실행기입니다. 오후 6교시에서 실패 처리를 더합니다. 직접 쓰는 곳은 1 ~ 7번입니다.

```python
from incident import change_status, match_playbooks, run_action, make_log_entry     # 월요일 파일의 함수를 불러온다

DONE_STATUSES = ["조치됨", "보고됨", "종료"]                                        # 이미 대응이 끝난 상태들
MAX_LOCKS_PER_RUN = 3                                                               # 한 번 실행에서 잠글 수 있는 계정의 최대 수


def find_skip_reason(action, entity, state):                                        # 액션 · 대상 · 모의 시스템을 받는 함수
    """이 액션을 건너뛰어야 하면 그 이유 문장을, 건너뛸 필요가 없으면 빈 글자("")를 리턴한다.
    계정을 잠그기 전에 이미 잠긴 계정인지, 한 번에 잠글 수 있는 수를 넘었는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. action 이 "계정 잠금" 이고(and) entity 가 state["locked_users"] 안에 있으면 (if, in)
    # 2.   "건너뜀: 이미 잠겨 있음" 을 리턴한다
    # 3. action 이 "계정 잠금" 이고(and) state["locked_users"] 의 개수(len)가 MAX_LOCKS_PER_RUN 이상이면 (if, >=)
    # 4.   "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)" 를 리턴한다
    return ""                                                                       # 건너뛸 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def safe_run_action(action, incident, state):                                       # 액션 · 인시던트 · 모의 시스템을 받는 함수
    """액션을 실행하기 전에 건너뛸 이유가 있는지 먼저 확인한다. 이유가 있으면 실행하지 않고 그 이유를, 없으면 월요일의 run_action 으로 실행한 결과를 리턴한다.
    같은 일을 두 번 하거나 너무 많이 하는 것을 막고 싶을 때 쓴다.
    """
    entity = incident["entity"]                                                     # 대응할 대상
    skip_reason = find_skip_reason(action, entity, state)                           # 건너뛸 이유를 구한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. skip_reason 이 빈 글자("")가 아니면 (if, !=)
    # 6.   skip_reason 을 리턴한다
    # 7. run_action(action, incident, state) 의 결과를 리턴한다 (건너뛸 이유가 없으면 원래대로 실행한다)


def run_playbook_safe(incident, playbook, state, action_log):                       # 인시던트 · 플레이북 · 모의 시스템 · 기록 리스트를 받는 함수
    """알림 한 건을 안전하게 처리한다. 이미 끝난 알림이면 건너뛰고, 승인이 필요하면 멈추고, 아니면 액션을 실행한다.
    처리 결과를 「실행 완료」 · 「승인 대기」 · 「이미 처리됨」 · 「일부 건너뜀」 중 하나로 리턴한다.
    """
    if incident["status"] in DONE_STATUSES:                                         # 이미 대응이 끝난 인시던트이면
        entry = make_log_entry(incident, playbook, "전체", "이미 처리됨 — 건너뜀")  # 건너뛴 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
        return "이미 처리됨"                                                        # 이미 처리됨을 리턴한다
    change_status(incident, "분류됨")                                               # 대응을 시작하기 전에 분류됨 상태로 옮긴다
    if playbook["approval"] != "자동":                                              # 승인이 필요하면
        entry = make_log_entry(incident, playbook, "전체", "승인 대기")             # 승인 대기 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
        return "승인 대기"                                                          # 승인 대기를 리턴한다
    skipped = False                                                                 # 건너뛴 액션이 있는지 : 처음에는 없다
    for action in playbook["actions"]:                                              # 액션을 하나씩 꺼낸다
        result = safe_run_action(action, incident, state)                           # 안전한 방식으로 실행한다
        if result.startswith("건너뜀"):                                             # 결과 문장이 「건너뜀」으로 시작하면
            skipped = True                                                          # 건너뛴 액션이 있다고 적는다
        entry = make_log_entry(incident, playbook, action, result)                  # 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
    if skipped:                                                                     # 건너뛴 액션이 있으면
        return "일부 건너뜀"                                                        # 조치됨으로 옮기지 않고 일부 건너뜀을 리턴한다
    change_status(incident, "조치됨")                                               # 모두 실행했으니 조치됨으로 옮긴다
    return "실행 완료"                                                              # 실행 완료를 리턴한다


def process_safe(incidents, registry, state, action_log):                           # 인시던트 리스트 · 플레이북 리스트 · 모의 시스템 · 기록 리스트를 받는 함수
    """알림을 하나씩 맞는 플레이북으로 안전하게 처리하고, 결과를 한 줄씩 출력한다.
    결과마다 몇 건인지 센 딕셔너리를 리턴한다.
    """
    counts = {}                                                                     # 실행 결과마다 몇 건인지 셀 딕셔너리
    for incident in incidents:                                                      # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                             # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                          # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                                  # 맞는 플레이북을 하나씩 꺼낸다
            result_text = run_playbook_safe(incident, playbook, state, action_log)  # 안전하게 실행한다
        counts[result_text] = counts.get(result_text, 0) + 1                        # 그 결과의 건수를 1 늘린다
        print(incident["id"], incident["entity"], "->", result_text, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다
    return counts                                                                   # 결과별 건수를 리턴한다
```

**`day02_4-1_run.py`** — 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다. 어제 `playbook_runner.py` 의 완성된 `run_playbook` 이 필요합니다.

```python
from incident import load_json, match_playbooks, INCIDENTS_PATH, REGISTRY_PATH           # 월요일 파일의 함수를 불러온다
from playbook_runner import run_playbook                                                 # 월요일에 만든 실행기를 불러온다
from safe_runner import process_safe, MAX_LOCKS_PER_RUN                                  # 방금 만든 안전한 실행기를 불러온다

BULK_PATH = "bulk_incidents.json"                                                        # 인사 시스템 오류로 퇴사자 알림이 몰린 상황의 알림 파일 이름


def new_state():                                                                         # 인자가 없는 함수
    """잠긴 계정 · 차단한 IP · 티켓이 모두 비어 있는 모의 시스템 상태를 새로 만들어 리턴한다.
    실험마다 깨끗한 상태에서 시작하고 싶을 때 쓴다.
    """
    state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}  # 비어 있는 상태 딕셔너리
    return state                                                                         # 상태를 리턴한다


def run_monday_way(incidents, registry, state, action_log):                              # 월요일 방식으로 처리하는 함수
    """월요일에 만든 run_playbook 으로 알림을 모두 처리한다. 오늘 만든 안전장치는 쓰지 않는다.
    안전장치가 없으면 어떤 일이 생기는지 보고 싶을 때 쓴다.
    """
    for incident in incidents:                                                           # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                                  # 맞는 플레이북을 찾는다
        for playbook in playbooks:                                                       # 맞는 플레이북을 하나씩 꺼낸다
            run_playbook(incident, playbook, state, action_log)                          # 월요일 방식으로 실행한다


registry = load_json(REGISTRY_PATH)                                                      # 플레이북 등록 파일을 읽는다

print("--- 단계 1: 어제 방식(안전장치 없음)으로 같은 알림 5건을 두 번 처리")             # 단계 1 시작을 알리는 줄
incidents = load_json(INCIDENTS_PATH)                                                    # 알림 5건을 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
run_monday_way(incidents, registry, state, action_log)                                   # 첫 번째 처리
run_monday_way(incidents, registry, state, action_log)                                   # 같은 알림을 한 번 더 처리한다
print("잠긴 계정:", state["locked_users"])                                               # 잠긴 계정을 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 티켓 수를 출력한다

print("--- 단계 2: 어제 방식(안전장치 없음)으로 인사 오류 알림 7건 처리")                # 단계 2 시작을 알리는 줄
bulk_incidents = load_json(BULK_PATH)                                                    # 인사 오류 알림 7건을 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
run_monday_way(bulk_incidents, registry, state, action_log)                              # 월요일 방식으로 처리한다
locked_count = len(state["locked_users"])                                                # 잠긴 계정이 몇 개인지 센다
print("잠긴 계정", locked_count, "개:", state["locked_users"])                           # 잠긴 계정 수와 이름을 출력한다

print("--- 단계 3: 안전한 방식으로 같은 알림 5건을 두 번 처리")                          # 단계 3 시작을 알리는 줄
incidents = load_json(INCIDENTS_PATH)                                                    # 알림 5건을 다시 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
print("첫 번째 처리")                                                                    # 첫 번째 처리임을 알리는 줄
process_safe(incidents, registry, state, action_log)                                     # 안전한 방식으로 처리한다
print("두 번째 처리")                                                                    # 두 번째 처리임을 알리는 줄
process_safe(incidents, registry, state, action_log)                                     # 같은 알림을 한 번 더 처리한다
print("잠긴 계정:", state["locked_users"])                                               # 잠긴 계정을 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 티켓 수를 출력한다

print("--- 단계 4: 안전한 방식으로 인사 오류 알림 7건 처리 (한 번에 최대", MAX_LOCKS_PER_RUN, "개)")  # 단계 4 시작을 알리는 줄
bulk_incidents = load_json(BULK_PATH)                                                    # 인사 오류 알림 7건을 다시 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
counts = process_safe(bulk_incidents, registry, state, action_log)                       # 안전한 방식으로 처리한다
locked_count = len(state["locked_users"])                                                # 잠긴 계정이 몇 개인지 센다
print("잠긴 계정", locked_count, "개:", state["locked_users"])                           # 잠긴 계정 수와 이름을 출력한다
print("결과별 건수:", counts)                                                            # 결과별 건수를 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 만든 티켓 수를 출력한다
print("건너뛴 액션과 이유:")                                                             # 건너뛴 액션을 모아 보여 주는 제목 줄
for entry in action_log:                                                                 # 기록을 하나씩 꺼낸다
    result_text = entry["result"]                                                        # 기록의 결과 문장
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. result_text 가 "건너뜀" 으로 시작하면 (if, startswith)
    # 9.   entry["incident"] · entry["action"] · "->" · result_text 를 출력한다 (print)
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 붙여 넣습니다.
   ```bash
   pwd
   touch bulk_incidents.json safe_runner.py day02_4-1_run.py
   ls
   ```
2. **[VS Code]** `safe_runner.py` 1 ~ 7번, `day02_4-1_run.py` 8 · 9번을 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
3. **[터미널]** 실행합니다(맥북은 `python3`).
   ```bash
   python day02_4-1_run.py
   ```
4. 출력은 네 단계와 건너뛴 이유입니다. 단계 1 은 2줄, 단계 2 는 1줄, 단계 3 은 14줄(「첫 번째 처리」 · 「두 번째 처리」 제목 2줄과 결과 10줄, 마지막의 잠긴 계정 · 티켓 2줄), 단계 4 는 알림 7건의 결과 7줄과 요약 3줄(잠긴 계정 · 결과별 건수 · 티켓)입니다. 마지막 `건너뛴 액션과 이유:` 아래는 건너뛴 액션만큼 줄이 나옵니다.
5. **[보고서]** `day02_am_report.md` 의 `## 4교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 단계 1 · 3 · 4 의 잠긴 계정과 티켓 수를 적어 주세요.
   - (나) 🔍 단계 1(어제 방식)에서는 `dami` 가 두 번 잠기고 티켓이 2건 생겼는데, 단계 3(안전한 방식)에서는 1건입니다. 단계 3 의 「두 번째 처리」 줄을 근거로 어떤 장치가 두 번째 실행을 막았는지 적어 주세요.
   - (다) 🔍 단계 4 에서 잠긴 계정 3개 가운데 `users_info.json` 의 `employed` 로 볼 때 잘못 잠긴 계정이 있는지 적고, 한도가 없을 때와 비교해 잘못 잠긴 계정이 몇 개 줄었는지 적어 주세요. 한도로 막지 못한 문제가 무엇인지도 적어 주세요. 마지막으로, 2교시의 맥락과 3교시의 경로 중 무엇을 쓰면 잘못 잠긴 계정을 줄일 수 있는지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 조건이 모두 참이면 | `if action == "계정 잠금" and entity in state["locked_users"]:` |
| 리스트의 개수 | `len(state["locked_users"])` |
| 이상이면 | `>=` |
| 같지 않으면 | `if skip_reason != "":` |
| 다른 함수의 결과를 그대로 리턴 | `return run_action(action, incident, state)` |
| 글자가 어떤 말로 시작하면 | `if result_text.startswith("건너뜀"):` |

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 알림에 재직 · VIP · 접속 IP 맥락을 붙였다 | 오전 2-1 |
| 맥락으로 승인 필요 · 오탐 종료 · 기본 경로를 나누고 이유를 남겼다 | 오전 3-1 |
| 중복 실행을 막고 한 번에 잠글 수 있는 계정을 제한했다 | 오전 4-1 |

오전에 만든 맥락 · 경로 · 안전장치는 서로 이어집니다. <mark>오후에는 두 가지를 만듭니다. 첫째, 3교시에서 `승인 필요` 로 나눈 알림을 담당자가 승인하거나 거절하는 처리입니다. 둘째, 4교시의 실행기가 액션에 실패했을 때 하는 처리입니다. 그리고 맥락 붙이기 · 경로 나누기 · 안전하게 실행하기를 이어서 한 번에 실행합니다.</mark> 4교시 마지막에 본 「한도 안에서도 잘못 잠긴 계정」 문제는, 오후에 맥락을 함께 쓰면 줄어듭니다.

---

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — `enrichment.py` 의 1 ~ 6번입니다.

```python
    # 1. entity 가 users_info 안에 있으면 (if, in)
    if entity in users_info:                                       # 계정 정보에 있는 대상이면
    # 2.   account 의 "employed" 에 users_info[entity]["employed"] 를 담는다
        account["employed"] = users_info[entity]["employed"]       # 재직 여부를 담는다
    # 3.   account 의 "vip" 에 users_info[entity]["vip"] 를 담는다
        account["vip"] = users_info[entity]["vip"]                 # VIP 여부를 담는다
    # 4. entity 가 source_ips 안에 있으면 (if, in)
    if entity in source_ips:                                       # 접속 IP 를 아는 대상이면
    # 5.   ip_info 의 "source_ip" 에 source_ips[entity] 를 담는다
        ip_info["source_ip"] = source_ips[entity]                  # 접속 IP 를 담는다
    # 6.   ip_info 의 "ip_trusted" 에 source_ips[entity] 가 trusted_ips 안에 있는지(in)의 결과를 담는다
        ip_info["ip_trusted"] = source_ips[entity] in trusted_ips  # 신뢰 IP 안에 있는지 확인한 결과를 담는다
```

`day02_2-1_run.py` 의 7 ~ 9번입니다.

```python
    # 7. enrich_incident(incident, users_info, source_ips, trusted_ips) 를 호출한다 (인시던트에 맥락이 붙는다)
    enrich_incident(incident, users_info, source_ips, trusted_ips)  # 맥락을 붙인다
    # 8. context 의 "vip" 가 참이면 (if)
    if context["vip"]:                                              # VIP 계정이면
    # 9.   vip_count 에 vip_count + 1 을 담는다 (1 늘린다)
        vip_count = vip_count + 1                                   # VIP 계정 알림 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 재직 여부가 「퇴사」인 알림은 <mark style="background:#bde3ff">**INC-001**</mark>, VIP 가 「예」인 알림은 <mark style="background:#bde3ff">**INC-003**</mark> 이고, 단계 3 의 VIP 계정 알림 수는 <mark style="background:#bde3ff">**1건**</mark>입니다.

```
--- 단계 1: 불러온 알림 5 건 · 계정 정보 6 명 · 신뢰 IP 1 개
--- 단계 2: 알림마다 붙인 정보(재직 · VIP · 접속 IP)
INC-001 dami · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-002 seoyeon · 재직: 재직 · VIP: 아니오 · 접속 IP: 203.0.113.80 · 신뢰 IP: 예
INC-003 gaeun · 재직: 재직 · VIP: 예 · 접속 IP: 198.51.100.77 · 신뢰 IP: 아니오
INC-004 jiwoo · 재직: 재직 · VIP: 아니오 · 접속 IP: 203.0.113.80 · 신뢰 IP: 예
INC-005 198.51.100.90 · 재직: 계정 아님 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
--- 단계 3: VIP 계정 알림 수
VIP 계정 알림 1 건
```

- (나) INC-005 의 대상 `198.51.100.90` 은 <mark style="background:#bde3ff">`users_info` 에도 `source_ips` 에도 키로 없습니다.</mark>
  - 근거: `lookup_account` 의 `if entity in users_info:`(1번)와 `lookup_source_ip` 의 `if entity in source_ips:`(4번)가 모두 거짓이라 `if` 안의 2 · 3번과 5 · 6번이 실행되지 않고, 처음 값(`False` · `None`)이 그대로 남습니다.
  - 문제: 모르는 대상의 `employed` 가 `True`(재직) 로 나오면 사람이 아닌 IP 를 「재직 중인 정상 사용자」로 오해하고, 뒤의 경로 판단이 틀립니다. 모르는 대상은 「모른다」는 값(`False`)으로 남겨 두어야 안전합니다.
- (다) 두 알림의 `reasons` 는 다릅니다.
  - INC-002: `평소와 다른 IP` · <mark style="background:#bde3ff">**`대량 다운로드`**</mark>. INC-004: `업무 시간 밖 로그인` · `평소와 다른 IP`.
  - 신뢰 IP 라는 사실은 「IP 때문에 난 알림」이 정상이라는 근거는 되지만, `대량 다운로드` 는 IP 와 관계없이 일어난 행동이라, 신뢰 IP 가 정상이라는 근거가 되지 못합니다. 맥락이 같아도 <mark>같게 처리하면 안 됩니다.</mark> 이 차이를 3교시에서 처리합니다.

**왜**

- <mark>조치하기 전에 알림에 정보를 붙이면, 프로그램도 알림마다 다르게 대응할 수 있습니다.</mark> 정보가 없으면 모든 알림이 이름과 등급만 다른 똑같은 알림으로 보입니다.

**자주 틀리는 곳**

- 4번의 `if` 를 빼고 5 · 6번만 쓰면 `source_ips` 에 없는 대상에서 오류가 납니다. <mark>**딕셔너리에서 꺼내기 전에 `in` 으로 키가 있는지 먼저 확인합니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`KeyError: 'dami'`</mark>, 키 에러: 딕셔너리에 없는 키를 꺼내려 할 때 나는 오류). `dami` 는 `source_ips.json` 에 없는 키입니다.

```
KeyError: 'dami'
```

- 6번을 빠뜨리면 오류는 나지 않지만 <mark>**신뢰 IP 가 모두 「아니오」로 나옵니다.**</mark> INC-002 와 INC-004 의 접속 IP 는 `203.0.113.80` 인데 신뢰 IP 가 「아니오」인 것이 이 실수의 결과입니다.

```
INC-001 dami · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-002 seoyeon · 재직: 재직 · VIP: 아니오 · 접속 IP: 203.0.113.80 · 신뢰 IP: 아니오
INC-003 gaeun · 재직: 재직 · VIP: 예 · 접속 IP: 198.51.100.77 · 신뢰 IP: 아니오
```

- 두 함수를 채우지 않고 실행하면 <mark>**오류 없이 계정 정보에 있는 대상이 모두 「퇴사」로 나오고 VIP 계정 알림이 0건입니다.**</mark> `employed` 의 처음 값이 `False` 이기 때문이고, 오류가 나지 않아도 출력된 내용이 맞는지 직접 읽어서 확인해야 합니다.

```
--- 단계 2: 알림마다 붙인 정보(재직 · VIP · 접속 IP)
INC-001 dami · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-002 seoyeon · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-003 gaeun · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-004 jiwoo · 재직: 퇴사 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
INC-005 198.51.100.90 · 재직: 계정 아님 · VIP: 아니오 · 접속 IP: 없음 · 신뢰 IP: 아니오
--- 단계 3: VIP 계정 알림 수
VIP 계정 알림 0 건
```

- 실행 파일의 7번을 비워 두면 맥락이 붙지 않아 오류가 납니다. <mark>**맥락을 붙이는 함수를 호출해야 `incident["context"]` 가 생깁니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`KeyError: 'context'`</mark>).

```
KeyError: 'context'
```

- 9번에서 `vip_count + 1` 대신 `vip_count` 를 그대로 다시 저장하면 오류는 나지 않지만 <mark>**VIP 계정 알림이 항상 0건으로 나옵니다.**</mark> 센 값이 늘지 않기 때문입니다.

```
--- 단계 3: VIP 계정 알림 수
VIP 계정 알림 0 건
```

**관제에서는**

- 알림을 열었을 때 대상의 정보가 이미 붙어 있으면 분석하는 시간이 크게 줄어듭니다. <mark>알림에 정보를 붙이는 보강은 자동 대응(SOAR, 쏘아: 정해 둔 절차대로 대응을 자동으로 실행하는 것)의 플레이북에서 널리 쓰입니다.</mark> 오늘은 JSON 파일에서 정보를 읽었지만, 인사 시스템 같은 곳에서 가져오게 바꿔도 붙이는 방식은 그대로입니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — `routing.py` 의 1 ~ 7번입니다.

```python
    # 1. incident["reasons"] 의 규칙을 하나씩 꺼낸다 (for, rule)
    for rule in incident["reasons"]:                                               # 탐지된 규칙을 하나씩 꺼낸다
    # 2.   rule 이 IP_RELATED_RULES 안에 없으면 (if, not in)
        if rule not in IP_RELATED_RULES:                                           # IP 관련 규칙이 아닌 것이 있으면
    # 3.     False 를 리턴한다 (IP 와 관계없는 다른 증거가 있다)
            return False                                                           # 다른 증거가 있으니 False 를 리턴한다
    # 4. context 의 "vip" 가 참이면 (if)
    if context["vip"]:                                                             # VIP 계정이면
    # 5.   "승인 필요" 와 "VIP 계정이라 담당자 승인이 필요함" 을 쉼표로 이어 함께 리턴한다
        return "승인 필요", "VIP 계정이라 담당자 승인이 필요함"                    # 경로와 이유를 함께 리턴한다
    # 6. context 의 "ip_trusted" 가 참이고(and) is_only_ip_related(incident) 가 참이면 (if)
    if context["ip_trusted"] and is_only_ip_related(incident):                     # 신뢰 IP 이고 규칙이 모두 IP 관련이면
    # 7.   "오탐 종료" 와 "신뢰 IP 에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄" 을 쉼표로 이어 함께 리턴한다
        return "오탐 종료", "신뢰 IP 에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄"  # 경로와 이유를 함께 리턴한다
```

`day02_3-1_run.py` 의 8 · 9번입니다.

```python
    # 8. decide_route(incident) 가 리턴한 두 값을 route 와 reason 에 한 번에 받는다
    route, reason = decide_route(incident)         # 처리 경로와 이유를 한 번에 받는다
    # 9. route_counts[route] 에 route_counts[route] + 1 을 담는다 (그 경로의 건수를 1 늘린다)
    route_counts[route] = route_counts[route] + 1  # 그 경로의 건수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 경로별 건수는 <mark style="background:#bde3ff">**기본 3건 · 승인 필요 1건 · 오탐 종료 1건**</mark>이고, `종료` 상태가 된 알림은 <mark style="background:#bde3ff">**INC-004**</mark> 입니다.

```
--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태
INC-001 dami high -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-002 seoyeon mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-003 gaeun mid -> 승인 필요 · VIP 계정이라 담당자 승인이 필요함 (상태: 탐지됨)
INC-004 jiwoo mid -> 오탐 종료 · 신뢰 IP 에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄 (상태: 종료)
INC-005 198.51.100.90 low -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
--- 단계 2: 경로별 건수
기본 3 건
승인 필요 1 건
오탐 종료 1 건
```

- (나) INC-004 의 `reasons` 는 `업무 시간 밖 로그인` · `평소와 다른 IP` 로 <mark style="background:#bde3ff">두 규칙 모두 IP 관련 규칙</mark>이라 `is_only_ip_related` 가 `True` 이고, 신뢰 IP 이므로 6번 조건이 참입니다.
  - INC-002 의 `reasons` 에는 IP 관련이 아닌 <mark style="background:#bde3ff">`대량 다운로드`</mark> 가 있어서 `is_only_ip_related` 가 `False` 입니다. 신뢰 IP 에서 접속했어도 `대량 다운로드` 는 IP 와 상관없는 행동입니다. 그래서 정상이라고 할 수 없고, 기본 경로로 보내 분석합니다.
- (다) 한 예: 그 VIP 계정은 <mark style="background:#bde3ff">`승인 필요`</mark> 경로로 갑니다.
  - 4번이 먼저라서 VIP 이면 6번까지 가지 않고 바로 리턴합니다.
  - 순서를 바꾸면 6번 조건이 먼저 검사됩니다. 이 VIP 알림은 「신뢰 IP 이고 규칙이 모두 IP 관련」이라서 `오탐 종료` 로 닫힙니다. 중요한 계정의 알림이 담당자 확인 없이 닫히는 일이므로, <mark>더 위험한 쪽을 먼저 확인합니다.</mark>

**왜**

- <mark>맥락을 보고 경로를 나누면 중요한 알림은 사람에게 보내고, 이유가 분명한 알림은 자동으로 닫을 수 있습니다.</mark> 닫은 이유를 함께 적어 두어야 나중에 「왜 이 알림을 보지 않았나」라는 질문에 답할 수 있습니다.

**자주 틀리는 곳**

- 1 ~ 3번을 빠뜨리면 `is_only_ip_related` 가 항상 `True` 를 리턴해서 오류는 나지 않지만 <mark>**INC-002 가 오탐으로 닫힙니다.**</mark> 6번에서 `and is_only_ip_related(incident)` 를 빼도 같은 결과가 나옵니다. 이 실수가 가장 위험합니다. 대량 다운로드가 있었던 알림이 아무도 확인하지 않은 채 종료되기 때문입니다.

```
--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태
INC-001 dami high -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-002 seoyeon mid -> 오탐 종료 · 신뢰 IP 에서 온 IP 관련 규칙뿐이라 정상 접속으로 봄 (상태: 종료)
```

- 4 · 5번을 빠뜨리면 <mark>**VIP 인 `gaeun`(INC-003) 이 `기본` 경로로 갑니다.**</mark> 중요한 계정이 담당자 승인 없이 기본 절차대로 처리되는 것이 이 실수의 결과입니다.

```
--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태
INC-001 dami high -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-002 seoyeon mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-003 gaeun mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
```

- 5번에서 값을 하나만 리턴하면 실행 파일의 `route, reason = decide_route(incident)` 에서 오류가 납니다. <mark>**리턴하는 값의 개수와 받는 변수의 개수가 같아야 합니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`too many values to unpack (expected 2)`</mark>). INC-003 에서 멈추는 것이 이 실수의 결과입니다.

```
--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태
INC-001 dami high -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-002 seoyeon mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
ValueError: too many values to unpack (expected 2)
```

- 두 함수만 채우지 않고 실행하면 <mark>**오류 없이 5건이 모두 `기본` 으로 나옵니다.**</mark>

```
--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태
INC-001 dami high -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-002 seoyeon mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-003 gaeun mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-004 jiwoo mid -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
INC-005 198.51.100.90 low -> 기본 · 플레이북 기본 절차대로 처리함 (상태: 탐지됨)
--- 단계 2: 경로별 건수
기본 5 건
승인 필요 0 건
오탐 종료 0 건
```

- 실행 파일의 8번을 비워 두면 `route` 가 만들어지지 않아 오류가 납니다. <mark>**리턴된 두 값을 변수에 받아야 아래에서 쓸 수 있습니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`name 'route' is not defined`</mark>, `route` 라는 이름의 변수가 아직 만들어지지 않았다는 뜻입니다). 파이썬 버전에 따라 뒤에 `Did you mean: …`(혹시 이걸 말한 것인가요?라는 추천 문구)이 더 붙을 수 있습니다.

```
NameError: name 'route' is not defined
```

**관제에서는**

- 오탐으로 닫는 규칙은 <mark>「모두 이런 경우일 때만 닫는다」처럼 조건을 좁게 쓰는 것</mark>이 원칙입니다. 닫은 알림도 이유와 함께 목록으로 남겨 두고, 가끔 그 목록에서 몇 건을 골라 잘못 닫은 것이 없는지 확인합니다. (이 실습 코드에는 없는 운영 절차입니다.)

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day02_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — `safe_runner.py` 의 1 ~ 7번입니다.

```python
    # 1. action 이 "계정 잠금" 이고(and) entity 가 state["locked_users"] 안에 있으면 (if, in)
    if action == "계정 잠금" and entity in state["locked_users"]:                  # 계정 잠금인데 이미 잠긴 계정이면
    # 2.   "건너뜀: 이미 잠겨 있음" 을 리턴한다
        return "건너뜀: 이미 잠겨 있음"                                            # 건너뛸 이유를 리턴한다
    # 3. action 이 "계정 잠금" 이고(and) state["locked_users"] 의 개수(len)가 MAX_LOCKS_PER_RUN 이상이면 (if, >=)
    if action == "계정 잠금" and len(state["locked_users"]) >= MAX_LOCKS_PER_RUN:  # 잠근 계정이 한도 이상이면
    # 4.   "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)" 를 리턴한다
        return "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)"    # 건너뛸 이유를 리턴한다
    # 5. skip_reason 이 빈 글자("")가 아니면 (if, !=)
    if skip_reason != "":                                                          # 건너뛸 이유가 있으면
    # 6.   skip_reason 을 리턴한다
        return skip_reason                                                         # 실행하지 않고 이유를 리턴한다
    # 7. run_action(action, incident, state) 의 결과를 리턴한다 (건너뛸 이유가 없으면 원래대로 실행한다)
    return run_action(action, incident, state)                                     # 이유가 없으면 어제의 방식대로 실행한 결과를 리턴한다
```

`day02_4-1_run.py` 의 8 · 9번입니다.

```python
    # 8. result_text 가 "건너뜀" 으로 시작하면 (if, startswith)
    if result_text.startswith("건너뜀"):                              # 결과 문장이 「건너뜀」으로 시작하면
    # 9.   entry["incident"] · entry["action"] · "->" · result_text 를 출력한다 (print)
        print(entry["incident"], entry["action"], "->", result_text)  # 인시던트 · 액션 · 이유를 출력한다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 1 의 잠긴 계정은 <mark style="background:#bde3ff">**`['dami', 'dami']`, 티켓 2건**</mark>, 단계 3 은 <mark style="background:#bde3ff">**`['dami']`, 티켓 1건**</mark>, 단계 4 는 <mark style="background:#bde3ff">**3개(`dami` · `seoyeon` · `gaeun`)**</mark> 입니다.

```
--- 단계 1: 어제 방식(안전장치 없음)으로 같은 알림 5건을 두 번 처리
잠긴 계정: ['dami', 'dami']
티켓: 2 건
--- 단계 2: 어제 방식(안전장치 없음)으로 인사 오류 알림 7건 처리
잠긴 계정 7 개: ['dami', 'dami', 'seoyeon', 'gaeun', 'jiwoo', 'junho', 'hana']
--- 단계 3: 안전한 방식으로 같은 알림 5건을 두 번 처리
첫 번째 처리
INC-001 dami -> 실행 완료 (상태: 조치됨)
INC-002 seoyeon -> 승인 대기 (상태: 분류됨)
INC-003 gaeun -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-004 jiwoo -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-005 198.51.100.90 -> 승인 대기 (상태: 분류됨)
두 번째 처리
INC-001 dami -> 이미 처리됨 (상태: 조치됨)
INC-002 seoyeon -> 승인 대기 (상태: 분류됨)
INC-003 gaeun -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-004 jiwoo -> 맞는 플레이북 없음 (상태: 탐지됨)
INC-005 198.51.100.90 -> 승인 대기 (상태: 분류됨)
잠긴 계정: ['dami']
티켓: 1 건
--- 단계 4: 안전한 방식으로 인사 오류 알림 7건 처리 (한 번에 최대 3 개)
INC-B01 dami -> 실행 완료 (상태: 조치됨)
INC-B02 dami -> 일부 건너뜀 (상태: 분류됨)
INC-B03 seoyeon -> 실행 완료 (상태: 조치됨)
INC-B04 gaeun -> 실행 완료 (상태: 조치됨)
INC-B05 jiwoo -> 일부 건너뜀 (상태: 분류됨)
INC-B06 junho -> 일부 건너뜀 (상태: 분류됨)
INC-B07 hana -> 일부 건너뜀 (상태: 분류됨)
잠긴 계정 3 개: ['dami', 'seoyeon', 'gaeun']
결과별 건수: {'실행 완료': 3, '일부 건너뜀': 4}
티켓: 7 건
건너뛴 액션과 이유:
INC-B02 계정 잠금 -> 건너뜀: 이미 잠겨 있음
INC-B05 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B06 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B07 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
```

- (나) 단계 3 의 「두 번째 처리」에서 INC-001 이 <mark style="background:#bde3ff">`이미 처리됨 (상태: 조치됨)`</mark> 으로 나옵니다.
  - 장치: `run_playbook_safe` 의 첫 `if` 가 인시던트 상태를 확인해서, `조치됨` · `보고됨` · `종료` 이면 실행하지 않고 건너뜁니다. 첫 번째 처리에서 INC-001 이 `조치됨` 이 되었기 때문입니다.
  - 월요일 방식에는 이 확인이 없어서 두 번째 처리에서 `dami` 를 다시 잠그고 티켓을 또 만들었습니다.
- (다) 잠긴 3개 가운데 <mark style="background:#bde3ff">`seoyeon` 과 `gaeun` 은 `employed` 가 `true` 인 재직자라 잘못 잠긴 계정</mark>입니다. 실제 퇴사자는 `dami` 한 명입니다.
  - 한도가 없고 중복 방지만 있다면 서로 다른 계정 6개가 모두 잠깁니다. 이 가운데 실제 퇴사자는 `dami` 한 명이라 5명이 잘못 잠깁니다(`dami` 는 알림이 두 건이라도 한 번만 잠깁니다). 한도 3개로 잘못 잠긴 계정이 5명에서 2명으로 줄었습니다.
  - 한도가 막지 못한 문제: 한도 안에서도 틀린 알림은 그대로 실행됩니다. 한도는 잠기는 계정 수를 제한할 뿐, 잘못된 알림을 가려내지는 못합니다.
  - 줄이는 방법: 2교시에서 붙인 `employed` 맥락을 잠그기 전에 확인하면 `seoyeon` 과 `gaeun` 은 재직 중이라 잠금 대상에서 빠집니다. `gaeun` 은 VIP 라서 3교시의 `승인 필요` 경로로도 걸러집니다. 오후 6교시에서 이 확인들을 한 흐름으로 잇습니다.
  - 계정 잠금을 건너뛴 알림에도 티켓은 만들어집니다(티켓 7건). 건너뛰는 것이 알림 전체가 아니라 계정 잠금 액션 하나뿐이기 때문이며, 담당자가 티켓을 보고 이어서 확인합니다.

**왜**

- <mark>자동 대응에서 더 큰 문제는 한 번 틀리는 일이 아니라, 틀린 판단이 순식간에 여러 번 반복되는 일입니다. 예를 들어 잘못된 알림 100건이 들어오면 계정 100개가 몇 초 만에 잠깁니다.</mark> 같은 일을 두 번 하지 않게 하는 장치와 한 번에 피해가 퍼지는 범위를 제한하는 장치가 있으면, 알림이 잘못 들어와도 피해가 커지지 않습니다.

**자주 틀리는 곳**

- 1 · 2번을 빠뜨리면 오류는 나지 않지만 <mark>**같은 계정의 두 번째 알림(INC-B02)이 `dami` 를 다시 잠급니다.**</mark> 잠긴 계정 리스트에 `dami` 가 두 번 들어가서 한도 3개 가운데 2개를 쓰기 때문에, `gaeun` 은 잠기지 않습니다. 단계 4 의 `잠긴 계정` 줄이 이 실수의 결과입니다.

```
INC-B04 gaeun -> 일부 건너뜀 (상태: 분류됨)
INC-B05 jiwoo -> 일부 건너뜀 (상태: 분류됨)
INC-B06 junho -> 일부 건너뜀 (상태: 분류됨)
INC-B07 hana -> 일부 건너뜀 (상태: 분류됨)
잠긴 계정 3 개: ['dami', 'dami', 'seoyeon']
결과별 건수: {'실행 완료': 3, '일부 건너뜀': 4}
티켓: 7 건
건너뛴 액션과 이유:
INC-B04 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B05 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B06 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B07 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
```

- 3 · 4번을 빠뜨리면 <mark>**한도가 없어져 재직자까지 모두 잠깁니다.**</mark> 단계 4 의 잠긴 계정이 6개로 나오는 것이 이 실수의 결과입니다.

```
INC-B01 dami -> 실행 완료 (상태: 조치됨)
INC-B02 dami -> 일부 건너뜀 (상태: 분류됨)
INC-B03 seoyeon -> 실행 완료 (상태: 조치됨)
INC-B04 gaeun -> 실행 완료 (상태: 조치됨)
INC-B05 jiwoo -> 실행 완료 (상태: 조치됨)
INC-B06 junho -> 실행 완료 (상태: 조치됨)
INC-B07 hana -> 실행 완료 (상태: 조치됨)
잠긴 계정 6 개: ['dami', 'seoyeon', 'gaeun', 'jiwoo', 'junho', 'hana']
결과별 건수: {'실행 완료': 6, '일부 건너뜀': 1}
티켓: 7 건
건너뛴 액션과 이유:
INC-B02 계정 잠금 -> 건너뜀: 이미 잠겨 있음
```

- 3번에서 `>=` 대신 `>` 를 쓰면 <mark>**한도 3개가 아니라 4개까지 잠깁니다.**</mark> 「3개 이상이면 멈춘다」와 「3개를 넘으면 멈춘다」는 다릅니다.

```
INC-B03 seoyeon -> 실행 완료 (상태: 조치됨)
INC-B04 gaeun -> 실행 완료 (상태: 조치됨)
INC-B05 jiwoo -> 실행 완료 (상태: 조치됨)
INC-B06 junho -> 일부 건너뜀 (상태: 분류됨)
INC-B07 hana -> 일부 건너뜀 (상태: 분류됨)
잠긴 계정 4 개: ['dami', 'seoyeon', 'gaeun', 'jiwoo']
결과별 건수: {'실행 완료': 4, '일부 건너뜀': 3}
티켓: 7 건
건너뛴 액션과 이유:
INC-B02 계정 잠금 -> 건너뜀: 이미 잠겨 있음
INC-B06 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
INC-B07 계정 잠금 -> 건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)
```

- 5 · 6번을 빠뜨리면 <mark>**건너뛸 이유를 찾아 놓고도 쓰지 않아 한도와 중복 방지가 모두 무시됩니다.**</mark> 단계 4 의 잠긴 계정이 7개로 나오고 `dami` 가 두 번 들어 있는 것이 이 실수의 결과입니다.

```
--- 단계 4: 안전한 방식으로 인사 오류 알림 7건 처리 (한 번에 최대 3 개)
INC-B01 dami -> 실행 완료 (상태: 조치됨)
INC-B02 dami -> 실행 완료 (상태: 조치됨)
INC-B03 seoyeon -> 실행 완료 (상태: 조치됨)
INC-B04 gaeun -> 실행 완료 (상태: 조치됨)
INC-B05 jiwoo -> 실행 완료 (상태: 조치됨)
INC-B06 junho -> 실행 완료 (상태: 조치됨)
INC-B07 hana -> 실행 완료 (상태: 조치됨)
잠긴 계정 7 개: ['dami', 'dami', 'seoyeon', 'gaeun', 'jiwoo', 'junho', 'hana']
결과별 건수: {'실행 완료': 7}
티켓: 7 건
건너뛴 액션과 이유:
```

- 7번을 빠뜨리면 `safe_run_action` 이 값을 리턴하지 않아 오류가 납니다. <mark>**건너뛸 이유가 없을 때 실행하는 줄이 있어야 합니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`'NoneType' object has no attribute 'startswith'`</mark>, 값이 없다는 뜻의 `None` 에 `startswith` 를 쓰려 해서 난 오류).

```
AttributeError: 'NoneType' object has no attribute 'startswith'
```

**관제에서는**

- 자동 대응을 켤 때는 <mark>「한 번에 최대 몇 건까지 자동으로 하고, 넘으면 사람에게 넘긴다」</mark>를 먼저 정합니다. 한도에 걸린 건이 나왔다면, 알림이 잘못 들어오는 사고가 났다는 신호일 수 있습니다. 그래서 담당자에게 따로 연락하기도 합니다. 이 연락 기능은 이번 실습 코드에는 없고, 실제 운영에서 쓰는 절차입니다. 같은 알림이 여러 번 와도 결과가 같게 만드는 것이 기본입니다.
