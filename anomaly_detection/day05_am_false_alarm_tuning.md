# 11/6(금) 오전 · 4과목 이상탐지 ⑤ — 오탐 · 미탐 세기 · 예외 규칙으로 튜닝 · 놓친 문제 줄이기 — 실습

이번 주에 만든 탐지 규칙은 알림을 냈지만, **그 알림이 맞았는지**는 아직 세어 보지 않았습니다. 오늘 오전에는 <mark>**알림이 맞았는지 세고(평가), 틀린 알림을 줄이는(튜닝)**</mark> 일을 합니다. 세어 보지 않으면 틀린 알림이 쌓여 담당자가 알림을 무시하게 되고, 놓친 문제는 아무도 모른 채 남습니다. 오늘은 <mark>한 교시에 질문 하나씩만</mark> 봅니다.

- **2교시**: 알림 7개와 사람이 조사한 정답(진짜 문제 5개)을 비교해 **오탐**(false positive, 폴스 포지티브: 문제가 아닌데 난 알림)과 **미탐**(false negative, 폴스 네거티브: 진짜 문제인데 알림이 나지 않은 것)을 셉니다.
- **3교시**: 오탐 4개 중 같은 원인 2개를 **예외 규칙**(튜닝: 규칙을 고쳐 틀린 알림을 줄이는 일) 하나로 줄이고, 진짜 문제를 지우지 않았는지 확인합니다.
- **4교시**: 로그인 규칙의 알림을 합쳐 놓친 문제가 줄었는지 확인하고, 평가 결과를 한 문장으로 만듭니다.

오늘은 오전 2 · 3 · 4교시이고, 오후 5 · 6교시에는 도커 컴포즈를 합니다. <mark>깃허브에 올리는 일은 오후 6교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 오전에 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널**입니다.
- 오늘 새로 배우는 판다스 문법은 `.unique()` 와 `.dropna()` 두 개입니다. `.sum()` 은 이번 주에 쓴 것을 `True` 개수 세기에 다시 쓰고, 나머지도 이번 주에 쓴 문법(`isin` · `~` · `&` · `value_counts()` · `pd.concat`)을 다시 씁니다.
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 출력이나 샘플 데이터의 값을 근거로 이유까지 서술합니다</mark>.
- 알림 번호(`A1` ~ `A8`)와 진짜 문제 번호(`P1` ~ `P5`)는 아래 시작하기의 JSON 파일(`alerts.json` · `problems.json` · `login_alerts.json`)에 들어 있습니다. 번호는 구분하려고 붙인 이름입니다.
- 오늘 정하는 기준(예외로 믿는 IP `203.0.113.80` 한 개)은 **고정**하고, <mark>값을 바꿔 가며 비교하지 않습니다</mark>.

📎 **오늘 불러 쓰는 이전 파일**: 없습니다. 오늘 오전은 아래 시작하기에서 만드는 JSON 파일 세 개로 시작하므로, 앞 수업 파일을 만들지 못했어도 그대로 따라 하면 됩니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치를 확인하고, 판다스가 설치돼 있는지 봅니다(맥북은 `python3`). <mark>`pwd` 가 `…/anomaly_detection` 으로 끝나고, 마지막에 버전 번호(예: `2.3.3`)가 나오면</mark> 됩니다. `No module named 'pandas'` 가 나오면 아래 「🆘」 둘째 줄을 따릅니다.
   ```bash
   cd anomaly_detection
   pwd
   python -c "import pandas; print(pandas.__version__)"
   ```
3. **오늘 받은 파일 두 개**(`day05_am_false_alarm_tuning.md`, `day05_am_report.md`)를 <mark>`다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-06(금))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[터미널]** 오늘 쓸 JSON 파일 세 개를 만들고 확인합니다. 같은 이름의 파일이 이미 있으면 건너뜁니다.
   ```bash
   touch alerts.json problems.json login_alerts.json
   ls
   ```
   - 명령 풀이: `touch 파일이름` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
6. **[VS Code]** 세 파일을 열어 아래 내용을 그대로 붙여 넣습니다(<mark>파일 세 개를 모두 붙인 뒤 맨 아래 7번으로 확인합니다</mark>). <mark>같은 이름의 파일이 이미 있으면 아래 내용으로 덮어씁니다</mark>(출력이 문서와 같아야 하기 때문입니다). `null` 은 그 값이 없다는 뜻입니다.

**`alerts.json`** — 이번 주 탐지 규칙이 11/2 에 낸 알림 7개이고, 사람이 조사한 결과가 붙어 있습니다. `real` 은 조사해 보니 진짜 문제였으면 `true`, `problem` 은 그 진짜 문제의 번호(`problems.json` 의 `id`), `memo` 는 조사 메모입니다.

```
[
  {"id": "A1", "rule": "서버 반복 거절", "user": "dami", "ip": null, "real": true, "problem": "P1", "memo": "퇴사한 계정이 서버에 4번 요청함"},
  {"id": "A2", "rule": "서버 반복 거절", "user": "gaeun", "ip": null, "real": false, "problem": null, "memo": "서버 설정 오류로 확인됨 — 공격 아님"},
  {"id": "A3", "rule": "SaaS 업무 시간 밖 로그인", "user": "jiwoo", "ip": "203.0.113.80", "real": false, "problem": null, "memo": "출장 중 협력사 사무실에서 비밀번호를 잘못 입력함"},
  {"id": "A4", "rule": "SaaS 평소와 다른 IP", "user": "jiwoo", "ip": "203.0.113.80", "real": false, "problem": null, "memo": "출장 중 협력사 사무실에서 접속함"},
  {"id": "A5", "rule": "SaaS 평소와 다른 IP", "user": "seoyeon", "ip": "203.0.113.80", "real": false, "problem": null, "memo": "외근 중 협력사 사무실에서 접속함"},
  {"id": "A6", "rule": "SaaS 대량 다운로드", "user": "seoyeon", "ip": "203.0.113.80", "real": true, "problem": "P2", "memo": "업무와 상관없는 파일 6개를 한꺼번에 내려받음"},
  {"id": "A7", "rule": "웹 경로 스캔", "user": null, "ip": "198.51.100.90", "real": true, "problem": "P3", "memo": "스캐너 경로 3개를 연속으로 요청함"}
]
```

**`problems.json`** — 사람이 조사해서 확인한 11/2 의 진짜 문제 5개입니다.

```
[
  {"id": "P1", "who": "dami", "what": "퇴사한 계정으로 서버에 요청함"},
  {"id": "P2", "who": "seoyeon", "what": "업무와 상관없는 파일을 대량으로 내려받음"},
  {"id": "P3", "who": "198.51.100.90", "what": "스캐너 경로를 요청해 접근 가능한 곳을 찾음"},
  {"id": "P4", "who": "203.0.113.50", "what": "로그인 5번 실패 뒤 성공하고 관리자 화면을 요청함"},
  {"id": "P5", "who": "seoyeon", "what": "권한 없는 정산 조회를 시도함"}
]
```

**`login_alerts.json`** — 로그인 규칙(웹 로그인 반복 실패)이 낸 알림 1개입니다. 4교시에서 씁니다.

```
[
  {"id": "A8", "rule": "웹 로그인 반복 실패", "user": null, "ip": "203.0.113.50", "real": true, "problem": "P4", "memo": "로그인 5번 실패 뒤 성공, 이어서 관리자 화면을 요청함"}
]
```

7. **[터미널]** <mark>파일이 정상인지 확인합니다</mark>(맥북은 `python3`).
   ```bash
   python -c "import pandas as pd; print(len(pd.read_json('alerts.json')), len(pd.read_json('problems.json')), len(pd.read_json('login_alerts.json')))"
   ```
   - <mark>`7 5 1` 이 나와야</mark> 합니다. 다르면 파일 내용이나 위치(`anomaly_detection` 폴더 안인지)를 다시 확인합니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `No module named 'pandas'`: <mark>가상환경이 활성화되지 않은 터미널입니다</mark>. `security-agent-toolkit` 폴더에서 가상환경을 활성화한 뒤(`source .venv/Scripts/activate`, 맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 다르면 그 이름으로) `python -m pip install pandas` 를 칩니다.
- `FileNotFoundError` 나 `ValueError` 가 나오면 <mark>JSON 파일 세 개가 `anomaly_detection` 폴더 바로 아래에 있는지</mark> `ls` 로 보고, 붙여 넣은 내용에 쉼표나 대괄호가 빠지지 않았는지 봅니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 알림이 맞았는지 세기 — 오탐과 미탐</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「이번 주에 만든 탐지 규칙들이 11/2 에 알림을 7건 냈습니다. 팀원 세 명이 7건을 모두 열어 보느라 반나절이 걸렸는데, 그중에는 조사해 보니 문제가 아닌 알림이 여럿 있었습니다. 반대로 사고 조사팀이 확인한 진짜 문제는 5건인데, 알림이 난 것은 그중 3건뿐이라고 합니다.
>
> 규칙이 얼마나 맞았는지 숫자로 알려 주세요. 문제가 아닌데 난 알림이 몇 건이고, 알림이 나지 않은 진짜 문제가 몇 건인가요?」
> - **왜 중요한가**: <mark>문제가 아닌 알림이 많으면 담당자가 알림을 무시하게 되고, 알림이 나지 않은 진짜 문제는 아무도 모르고 지나갑니다.</mark> 숫자로 세어 봐야 어느 규칙을 고칠지 정할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 탐지 규칙은 알림을 내지만, 알림이 모두 맞는 것은 아닙니다. 사람이 조사해 보면 문제가 아닌 알림도 있고, 알림이 나지 않았는데 진짜 문제인 경우도 있습니다.
2. 오늘 질문은 하나입니다. <mark>**알림 7개 중 몇 개가 틀렸고, 진짜 문제 5개 중 몇 개를 놓쳤는가?**</mark>
3. 틀리는 방식은 두 가지이고, 줄여야 하는 쪽이 다릅니다.

| | 진짜 문제였다 | 문제가 아니었다 |
|---|---|---|
| **알림이 났다** | 맞게 찾음 | **오탐** — 담당자의 확인 시간만 씀 |
| **알림이 나지 않았다** | **미탐** — 진짜 문제를 놓침 | 해당 없음 |

### 📖 2.1 알림 7개와 진짜 문제 5개

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`alerts.json` 의 알림 7개입니다. `real` 열이 `True` 이면 조사해 보니 진짜 문제였습니다.

| id | 규칙 | 대상 | real | 조사 메모 |
|---|---|---|---|---|
| A1 | 서버 반복 거절 | dami | `True` | 퇴사한 계정이 서버에 4번 요청함 |
| A2 | 서버 반복 거절 | gaeun | `False` | 서버 설정 오류로 확인됨 — 공격 아님 |
| A3 | SaaS 업무 시간 밖 로그인 | jiwoo | `False` | 출장 중 협력사 사무실에서 비밀번호를 잘못 입력함 |
| A4 | SaaS 평소와 다른 IP | jiwoo | `False` | 출장 중 협력사 사무실에서 접속함 |
| A5 | SaaS 평소와 다른 IP | seoyeon | `False` | 외근 중 협력사 사무실에서 접속함 |
| A6 | SaaS 대량 다운로드 | seoyeon | `True` | 업무와 상관없는 파일 6개를 한꺼번에 내려받음 |
| A7 | 웹 경로 스캔 | 198.51.100.90 | `True` | 스캐너 경로 3개를 연속으로 요청함 |

- 진짜 문제였던 알림은 A1 · A6 · A7 세 개이고, <mark>나머지 네 개(A2 · A3 · A4 · A5)가 오탐</mark>입니다.
- `problems.json` 의 진짜 문제 P1 ~ P5 중 알림이 나온 것은 P1 · P2 · P3 이고, <mark>P4 · P5 는 알림이 나지 않았습니다(미탐)</mark>.
- 오탐이라고 해서 알림을 만든 규칙이 잘못 작동한 것은 아닙니다. 규칙대로 찾았지만 조사해 보니 문제가 아니었다는 뜻입니다.

**🐼 판다스 문법 상자 — 리스트에 없는 것 찾기 `~열.isin(리스트)`**

**<mark>`~열.isin(리스트)`</mark> 는 열의 값이 리스트 안에 없으면 `True`, 있으면 `False` 를 줍니다**

아래는 알림이 난 사용자 기록입니다. 이미 확인을 끝낸 사용자 리스트(`checked_users`)에 **없는** 기록만 찾습니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                          # 표에 넣을 내용(열 이름: 값들)
    "user": ["gaeun", "dami", "seoyeon", "junho", "dami"],        # user 열
    "action": ["login", "download", "login", "upload", "login"],  # action 열
}
df = pd.DataFrame(data)                                           # 내용으로 표(DataFrame)를 만든다
print(df)                                                         # 표를 출력한다
```

실행 결과:

```
      user    action
0    gaeun     login
1     dami  download
2  seoyeon     login
3    junho    upload
4     dami     login
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
checked_users = ["gaeun", "seoyeon"]         # 확인을 끝낸 사용자 두 명을 리스트에 담는다
is_checked = df["user"].isin(checked_users)  # user 열의 각 값이 그 리스트 안에 있는지 확인한다
print(is_checked)                            # True · False 를 출력한다
```

실행 결과:

```
0     True
1    False
2     True
3    False
4    False
Name: user, dtype: bool
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
is_unchecked = ~is_checked  # True 와 False 를 서로 뒤집는다 (리스트에 없으면 True)
print(is_unchecked)         # 뒤집은 결과를 출력한다
```

실행 결과:

```
0    False
1     True
2    False
3     True
4     True
Name: user, dtype: bool
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
unchecked_df = df[is_unchecked]  # True 인 행만 남긴다
print(unchecked_df)              # 아직 확인하지 않은 사용자의 기록을 출력한다
```

실행 결과:

```
    user    action
1   dami  download
3  junho    upload
4   dami     login
```

- 읽는 법: 두 번째 출력은 `isin` 의 결과이고, <mark style="background:#bde3ff">gaeun · seoyeon 의 행이 `True`</mark> 입니다. 세 번째 출력은 그 결과를 `~` 로 뒤집은 것이라 <mark style="background:#bde3ff">dami · junho 의 행이 `True`</mark> 입니다. 네 번째 출력은 그 `True` 인 세 행만 남은 표입니다.
- `~is_checked` 는 「리스트에 없다」는 뜻입니다. 오늘은 이 방식으로 「알림이 하나도 나지 않은 진짜 문제」를 찾습니다.

**🐼 판다스 문법 상자 — `True` 개수 세기에 쓰는 `.sum()` (복습)**

**<mark>`열.sum()`</mark> 은 열의 값을 모두 더합니다. `True · False` 열에 쓰면 `True` 의 개수를 셉니다(`True` 는 1, `False` 는 0)**

이번 주에 그룹마다 점수를 더할 때 쓴 `.sum()` 입니다. 아래는 `is_blocked` 열이 차단된 기록이면 `True` 인 표이고, 차단된 기록이 몇 개인지 셉니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                    # 표에 넣을 내용(열 이름: 값들)
    "user": ["gaeun", "dami", "seoyeon", "junho", "dami"],  # user 열
    "is_blocked": [False, True, False, False, True],        # is_blocked 열 (차단된 기록이면 True)
}
df = pd.DataFrame(data)                                     # 내용으로 표(DataFrame)를 만든다
blocked_count = df["is_blocked"].sum()                      # is_blocked 열에서 True 가 몇 개인지 더해서 센다
print(blocked_count)                                        # 차단된 기록 수를 출력한다
```

실행 결과:

```
2
```

- 읽는 법: 출력 <mark style="background:#bde3ff">`2`</mark> 는 `True` 가 두 개(dami 의 행 두 개)라는 뜻입니다. `.sum()` 은 괄호까지 써야 합니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_table` · `pick_real_alerts` | 파일 경로 · 알림 표 | 표 · 진짜 문제였던 알림 표(미리 채움) |
| `find_false_alarms` | 알림 표 | 오탐 표와 규칙별 오탐 개수 |
| `find_missed` | 진짜 문제 표 · 진짜 알림 표 | 놓친 진짜 문제 표 |
| `count_real_alerts` | 알림 표 | 진짜 문제였던 알림 수 |

- **직접 쓰는 곳은 일곱 군데**(번호 1 ~ 7)이고, 함수 세 개 안에 나뉘어 있습니다.
  - `find_false_alarms`(1 ~ 3번, 3곳): 진짜가 아닌 알림을 뒤집어 고르고, 규칙별로 셉니다.
  - `find_missed`(4 ~ 6번, 3곳): 알림이 가리키는 문제 번호를 꺼내고, 알림이 나지 않은 문제를 뒤집어 고릅니다.
  - `count_real_alerts`(7번, 1곳): `True` 가 몇 개인지 `.sum()` 으로 셉니다.
- 오늘 새 문법은 없습니다. `.sum()` 은 이번 주에 쓴 것을 `True` 개수 세기에 다시 쓰고, `isin` · `~` · `value_counts()` 도 다시 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 알림이 맞았는지 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>알림 7개 중 몇 개가 틀렸는지, 진짜 문제를 몇 개 놓쳤는지 세어 본 적이 없습니다</mark>.
- **그래서 만드는 것**: `evaluation.py` 입니다.
  - 진짜 문제였던 알림을 골라 셉니다.
  - 문제가 아니었던 알림(오탐)을 골라 규칙별로 셉니다.
  - 알림이 나지 않은 진짜 문제(미탐)를 찾습니다.
- **실행하면**: <mark>단계 1: 알림 수, 단계 2: 진짜 문제였던 알림 수, 단계 3: 오탐 수와 규칙별 개수, 단계 4: 놓친 진짜 문제가 나옵니다.</mark>
- **현업에서는**: 알림을 낸 규칙마다 오탐 수를 세어 두면 어느 규칙부터 고칠지 정할 수 있고, 미탐은 새 규칙이 필요하다는 신호입니다.

**🎯 할 일**

1. `evaluation.py` · `day05_2-1_run.py` 두 파일을 만들고, `evaluation.py` 의 세 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>알림 수</mark>(단계 1), <mark>진짜 문제였던 알림 수</mark>(단계 2), <mark>오탐</mark>(단계 3), <mark>미탐</mark>(단계 4)을 읽습니다.

**`evaluation.py`**

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
PROBLEMS_PATH = "problems.json"                       # 읽을 진짜 문제 파일 이름


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def pick_real_alerts(alerts):                         # 알림 표를 받는 함수
    """알림 중 조사해 보니 진짜 문제였던 것만 골라 새 표로 만든다.
    맞게 찾은 알림을 셀 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    real_alerts = alerts[is_real]                     # True 인 행만 골라 새 표로 만든다
    return real_alerts                                # 진짜 문제였던 알림 표를 리턴한다


def find_false_alarms(alerts):                        # 알림 표를 받는 함수
    """진짜 문제가 아니었는데 난 알림(오탐)을 골라 규칙별로 센다.
    어느 규칙이 오탐을 많이 내는지 볼 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. is_real 을 ~ 로 뒤집어 is_false 에 담는다
    # 2. alerts 에서 is_false 가 True 인 행만 골라 false_alarms 에 담는다
    # 3. false_alarms 의 "rule" 열에서 값별 개수를 value_counts() 로 세어 false_alarm_rule_counts 에 담는다
    return false_alarms, false_alarm_rule_counts      # 오탐 표와 규칙별 오탐 개수를 리턴한다


def find_missed(problems, real_alerts):               # 진짜 문제 표와 진짜 알림 표를 받는 함수
    """알림이 하나도 나지 않은 진짜 문제(미탐)를 골라 새 표로 만든다.
    놓친 문제를 찾을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. real_alerts 의 "problem" 열을 꺼내 caught_ids 에 담는다
    is_caught = problems["id"].isin(caught_ids)       # 각 문제 번호가 그 안에 있는지 구한다
    # 5. is_caught 를 ~ 로 뒤집어 is_missed 에 담는다
    # 6. problems 에서 is_missed 가 True 인 행만 골라 missed_problems 에 담는다
    return missed_problems                            # 놓친 문제 표를 리턴한다


def count_real_alerts(alerts):                        # 알림 표를 받는 함수
    """진짜 문제였던 알림이 몇 개인지 센다.
    알림이 얼마나 맞았는지 숫자 하나로 볼 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. is_real 의 True 개수를 .sum() 으로 세어 real_alert_count 에 담는다
    return real_alert_count                           # 진짜 문제였던 알림 수를 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 7번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `NameError: name 'real_alert_count' is not defined` 오류가 납니다. 7번을 아직 안 썼기 때문입니다.

**`day05_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(표)` 는 표의 행 수입니다.

```python
from evaluation import load_table, pick_real_alerts, find_false_alarms, find_missed, count_real_alerts, ALERTS_PATH, PROBLEMS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
problems = load_table(PROBLEMS_PATH)                  # 진짜 문제 파일을 표로 읽는다
alert_count = len(alerts)                             # 알림이 모두 몇 개인지 센다
print("--- 단계 1: 알림 전체 ---")                    # 단계 1 제목
print("알림 수:", alert_count)                        # 알림 수를 출력한다

real_alerts = pick_real_alerts(alerts)                # 진짜 문제였던 알림만 골라낸다
real_alert_count = count_real_alerts(alerts)          # 진짜 문제였던 알림이 몇 개인지 센다
print("--- 단계 2: 진짜 문제였던 알림 (맞게 찾은 알림) ---")  # 단계 2 제목
print("진짜 문제였던 알림 수:", real_alert_count)     # 맞게 찾은 알림 수를 출력한다

false_alarms, false_alarm_rule_counts = find_false_alarms(alerts)  # 오탐과 규칙별 오탐 개수를 구한다
false_alarm_count = len(false_alarms)                 # 오탐이 몇 개인지 센다
print("--- 단계 3: 오탐 (문제가 아닌데 난 알림) ---")  # 단계 3 제목
print("오탐 수:", false_alarm_count)                  # 오탐 수를 출력한다
print("오탐이 난 규칙과 오탐 수:")                    # 아래 표가 무엇인지 알리는 줄
print(false_alarm_rule_counts)                        # 규칙마다 오탐이 몇 개인지 출력한다

missed_problems = find_missed(problems, real_alerts)  # 알림이 나지 않은 진짜 문제를 찾는다
missed_count = len(missed_problems)                   # 놓친 문제가 몇 개인지 센다
print("--- 단계 4: 미탐 (알림이 나지 않은 진짜 문제) ---")  # 단계 4 제목
print("미탐 수:", missed_count)                       # 미탐 수를 출력한다
missed_list = missed_problems.to_dict("records")      # 표를 문제 딕셔너리 리스트로 바꾼다
for problem in missed_list:                           # 놓친 문제를 하나씩 꺼낸다
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])  # 문제 번호 · 대상 · 내용을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `evaluation.py` · `day05_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `evaluation.py` 에서 <mark>직접 쓰는 곳 일곱 군데를 씁니다</mark>. 위 판다스 문법 상자와 2.1 의 표를 참고해 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day05_2-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **네 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1과 단계 2는 각각 1줄, 단계 3은 7줄(오탐 수 1줄 · 안내 1줄 · 규칙별 개수 표 5줄), 단계 4는 3줄(미탐 수 1줄 · 놓친 문제 2줄)입니다. 개수가 같은 규칙의 순서는 달라도 됩니다.
5. **[보고서]** `day05_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 알림 수와 오탐 수와 미탐 수를 적어 주세요.
   - (나) 🔍 A2(gaeun)는 조사해 보니 서버 설정 오류여서 오탐으로 셌습니다. 이 알림이 오탐인 이유와, 그래도 한 번은 확인해야 했던 이유를 적어 주세요.
   - (다) 🔍 미탐인 P5(seoyeon 의 권한 없는 정산 조회 시도)는 왜 알림이 나지 않았을까요? 그 문제를 찾으려면 어떤 규칙이 필요한지도 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 조건 뒤집기 | `is_false = ~is_real` |
| 조건에 맞는 행만 | `false_alarms = alerts[is_false]` |
| 이름별 개수 | `false_alarm_rule_counts = false_alarms["rule"].value_counts()` |
| 열 하나 꺼내기 | `caught_ids = real_alerts["problem"]` |
| 리스트에 없는 것 | `is_missed = ~is_caught` |
| `True` 개수 세기 | `real_alert_count = is_real.sum()` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 예외 규칙 하나로 오탐 줄이기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「오탐 4건 중 'SaaS 평소와 다른 IP' 알림 2건(알림 번호 `A4` jiwoo · `A5` seoyeon, `alerts.json` 에 있습니다)은 모두 협력사 사무실 IP `203.0.113.80` 에서 로그인한 것이었습니다. 협력사 사무실은 직원이 출장이나 외근으로 자주 쓰는 곳입니다.
>
> 이 IP 에서 온 'SaaS 평소와 다른 IP' 알림만 빠지도록 규칙을 고쳐 주세요. 단, 진짜 문제까지 같이 지워지면 안 됩니다.」
> - **왜 중요한가**: <mark>같은 원인의 오탐을 규칙 하나로 줄이면 담당자가 매일 열어 보는 알림이 줄지만, 예외를 넓게 만들면 진짜 문제까지 지워질 수 있습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 오탐을 줄이는 가장 쉬운 방법은 **예외 규칙**입니다. 「이 IP 에서 온 이 규칙의 알림은 뺀다」처럼 조건을 정해 틀린 알림을 빼냅니다.
2. 오늘 질문은 하나입니다. <mark>**예외 규칙 하나로 오탐을 몇 개 줄일 수 있고, 진짜 문제는 지워지지 않았는가?**</mark>
3. 예외는 **한 규칙에만** 적용합니다. 같은 IP `203.0.113.80` 에서 온 알림이라도 다른 규칙의 알림은 그대로 둡니다.

### 📖 3.1 같은 IP 에서 온 알림 네 개

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`203.0.113.80` 에서 온 알림은 A3 · A4 · A5 · A6 네 개입니다. A1 · A2 는 서버 알림이라 IP 가 없어서 이 표에서 뺐습니다. 예외 규칙은 `IP_RULE`(SaaS 평소와 다른 IP)의 알림 중 믿는 IP 에서 온 것만 뺍니다.

| id | 규칙 | 대상 | real | 예외 규칙이 빼는가 |
|---|---|---|---|---|
| A3 | SaaS 업무 시간 밖 로그인 | jiwoo | `False` | 아니오 (다른 규칙) |
| A4 | SaaS 평소와 다른 IP | jiwoo | `False` | **예** |
| A5 | SaaS 평소와 다른 IP | seoyeon | `False` | **예** |
| A6 | SaaS 대량 다운로드 | seoyeon | `True` | 아니오 (다른 규칙) |

- A4 · A5 두 개가 빠지면 오탐은 4개에서 2개(A2 · A3)로 줄어듭니다.
- <mark>A6 은 같은 IP 에서 왔지만 진짜 문제입니다.</mark> 규칙을 가리지 않고 이 IP 의 알림을 모두 빼면 A6 까지 지워집니다.
- <mark style="background:#ffc4d6">예외에는 위험도 있습니다. 믿는 IP 에서 누군가 계정을 도용해 로그인해도, 그 규칙은 알림을 내지 않습니다.</mark>

**🐼 판다스 문법 상자 — 같은 값을 한 번씩만 꺼내기 `.unique()`**

**<mark>`열.unique()`</mark> 는 열에서 같은 값을 한 번씩만 모아 줍니다**

아래는 알림이 난 기록이고, 같은 사용자가 여러 번 나옵니다. 어떤 사용자가 나왔는지만 한 번씩 봅니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                                          # 표에 넣을 내용(열 이름: 값들)
    "user": ["dami", "gaeun", "dami", "seoyeon", "dami"],         # user 열
    "action": ["login", "login", "download", "login", "upload"],  # action 열
}
df = pd.DataFrame(data)                                           # 내용으로 표(DataFrame)를 만든다
print(df)                                                         # 표를 출력한다
```

실행 결과:

```
      user    action
0     dami     login
1    gaeun     login
2     dami  download
3  seoyeon     login
4     dami    upload
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
users = df["user"].unique()  # user 열에서 같은 값을 한 번씩만 꺼낸다
print(users)                 # 사용자 이름을 출력한다
```

실행 결과:

```
['dami' 'gaeun' 'seoyeon']
```

- 읽는 법: 표에는 사용자가 다섯 번 나오지만, <mark style="background:#bde3ff">두 번째 출력에는 `dami` · `gaeun` · `seoyeon` 이 한 번씩만</mark> 나옵니다. 처음 나온 순서대로 나옵니다.
- 출력의 `[` `]` 안에 따옴표로 묶인 이름이 공백으로 이어지는 모양은 정상입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_table` · `count_false_alarms` | 파일 경로 · 알림 표 | 표 · 오탐 수(미리 채움) |
| `apply_exception` | 알림 표 | 빼낸 알림 표와 남은 알림 표 |
| `count_real_removed` | 빼낸 알림 표 | 빼낸 알림 중 진짜 문제였던 알림 수 |
| `find_removed_users` | 빼낸 알림 표 | 빼낸 알림에 나온 사용자(중복 없이) |

- **직접 쓰는 곳은 일곱 군데**(번호 1 ~ 7)이고, 함수 세 개 안에 나뉘어 있습니다.
  - `apply_exception`(1 ~ 4번, 4곳): 알림의 규칙이 IP 규칙인지 비교하고, 믿는 IP 인지 구하고, 둘을 합쳐 빼낼 알림을 정한 뒤, 남은 알림을 고릅니다.
  - `count_real_removed`(5 · 6번, 2곳): 빼낸 알림 중 진짜 문제였던 것을 고릅니다.
  - `find_removed_users`(7번, 1곳): 빼낸 알림에 나온 사용자를 중복 없이 꺼냅니다.
- 오늘 새 문법은 `.unique()` 하나입니다. 이번 주에 쓴 `isin` · `&` 와 2교시의 `~` 는 다시 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 믿는 IP 예외 규칙으로 오탐 줄이기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>협력사 사무실 IP 에서 온 'SaaS 평소와 다른 IP' 알림이 오탐으로 계속 쌓입니다</mark>.
- **그래서 만드는 것**: `tuning.py` 입니다.
  - IP 규칙의 알림 중 믿는 IP 에서 온 것을 찾아 빼냅니다.
  - 적용 전과 후의 오탐 수를 비교합니다.
  - 빼낸 알림 중 진짜 문제가 있었는지 확인합니다.
  - 빼낸 알림에 나온 사용자를 중복 없이 모읍니다.
- **실행하면**: <mark>단계 1: 적용 전 알림 수와 오탐 수, 단계 2: 빠진 알림과 그 사용자, 단계 3: 적용 후 알림 수와 오탐 수, 단계 4: 빠진 알림 중 진짜 문제였던 알림 수(0이면 진짜 문제는 지워지지 않은 것)가 나옵니다.</mark>
- **현업에서는**: 예외를 넣을 때마다 「빠진 알림 중 진짜 문제가 있는가」를 확인합니다. 예외 리스트는 근거(협력사 사무실 IP)와 함께 기록해 두어야 나중에 지울 수 있습니다.

**🎯 할 일**

1. `tuning.py` · `day05_3-1_run.py` 두 파일을 만들고, `tuning.py` 의 세 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>적용 전 오탐 수</mark>(단계 1), <mark>빠진 알림</mark>(단계 2), <mark>적용 후 오탐 수</mark>(단계 3), <mark>빠진 알림 중 진짜 문제였던 알림 수</mark>(단계 4)를 읽습니다.

**`tuning.py`**

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
IP_RULE = "SaaS 평소와 다른 IP"                       # 예외를 적용할 규칙 이름
TRUSTED_IPS = ["203.0.113.80"]                        # 믿는 IP 리스트 : 협력사 사무실 IP 한 개


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def count_false_alarms(alerts):                       # 알림 표를 받는 함수
    """진짜 문제가 아니었는데 난 알림(오탐)이 몇 개인지 센다.
    튜닝 전과 후를 비교할 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    is_false = ~is_real                               # 문제가 아니었던 알림을 True 로 만든다
    false_alarms = alerts[is_false]                   # True 인 행만 골라 새 표로 만든다
    false_alarm_count = len(false_alarms)             # 오탐이 몇 개인지 센다
    return false_alarm_count                          # 오탐 개수를 리턴한다


def apply_exception(alerts):                          # 알림 표를 받는 함수
    """IP 규칙 알림 중 믿는 IP 에서 온 것만 빼낸다.
    오탐을 줄이는 예외 규칙을 적용할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. alerts 의 "rule" 열이 IP_RULE 과 같은지 비교해 is_ip_rule 에 담는다
    # 2. alerts 의 "ip" 열이 TRUSTED_IPS 안에 있는지 isin 으로 구해 is_trusted 에 담는다
    # 3. is_ip_rule 과 is_trusted 가 모두 True 인 행을 & 로 구해 is_removed 에 담는다
    removed_alerts = alerts[is_removed]               # 빼낼 알림만 골라 새 표로 만든다
    is_kept = ~is_removed                             # 빼지 않을 알림을 True 로 만든다
    # 4. alerts 에서 is_kept 가 True 인 행만 골라 kept_alerts 에 담는다
    return removed_alerts, kept_alerts                # 빼낸 알림 표와 남은 알림 표를 리턴한다


def count_real_removed(removed_alerts):               # 빼낸 알림 표를 받는 함수
    """빼낸 알림 중 진짜 문제였던 것이 몇 개인지 센다.
    예외 규칙이 진짜 문제를 지우지 않았는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. removed_alerts 의 "real" 열을 꺼내 is_real_removed 에 담는다
    # 6. removed_alerts 에서 is_real_removed 가 True 인 행만 골라 real_removed 에 담는다
    real_removed_count = len(real_removed)            # 진짜 문제였던 알림이 몇 개 빠졌는지 센다
    return real_removed_count                         # 그 개수를 리턴한다


def find_removed_users(removed_alerts):               # 빼낸 알림 표를 받는 함수
    """빼낸 알림에 나온 사용자를 중복 없이 모은다.
    예외로 빠진 알림이 누구의 것인지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. removed_alerts 의 "user" 열에서 같은 값은 한 번씩만 .unique() 로 꺼내 removed_users 에 담는다
    return removed_users                              # 중복 없는 사용자 이름을 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 7번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `NameError: name 'is_removed' is not defined` 오류가 납니다. 3번을 아직 안 썼기 때문입니다.

**`day05_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

```python
from tuning import load_table, count_false_alarms, apply_exception, count_real_removed, find_removed_users, ALERTS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
alert_count = len(alerts)                             # 알림이 모두 몇 개인지 센다
false_alarm_count_before = count_false_alarms(alerts)  # 예외 규칙을 적용하기 전의 오탐 수를 센다
print("--- 단계 1: 예외 규칙을 적용하기 전 ---")      # 단계 1 제목
print("알림 수:", alert_count)                        # 적용 전 알림 수를 출력한다
print("오탐 수:", false_alarm_count_before)           # 적용 전 오탐 수를 출력한다

removed_alerts, kept_alerts = apply_exception(alerts)  # 믿는 IP 에서 온 IP 규칙 알림을 빼낸다
removed_count = len(removed_alerts)                   # 빠진 알림이 몇 개인지 센다
print("--- 단계 2: 예외 규칙으로 빠진 알림 ---")      # 단계 2 제목
print("빠진 알림 수:", removed_count)                 # 빠진 알림 수를 출력한다
removed_list = removed_alerts.to_dict("records")      # 표를 알림 딕셔너리 리스트로 바꾼다
for alert in removed_list:                            # 빠진 알림을 하나씩 꺼낸다
    print("빠진 알림:", alert["id"], alert["rule"], alert["user"], alert["ip"])  # 번호 · 규칙 · 사용자 · IP 를 출력한다
removed_users = find_removed_users(removed_alerts)    # 빠진 알림에 나온 사용자를 중복 없이 모은다
print("빠진 알림의 사용자:", removed_users)           # 사용자 이름을 출력한다

kept_count = len(kept_alerts)                         # 남은 알림이 몇 개인지 센다
false_alarm_count_after = count_false_alarms(kept_alerts)  # 적용 후의 오탐 수를 센다
print("--- 단계 3: 예외 규칙을 적용한 뒤 ---")        # 단계 3 제목
print("알림 수:", kept_count)                         # 적용 후 알림 수를 출력한다
print("오탐 수:", false_alarm_count_after)            # 적용 후 오탐 수를 출력한다

real_removed_count = count_real_removed(removed_alerts)  # 빠진 알림 중 진짜 문제였던 것을 센다
print("--- 단계 4: 빠진 알림 중 진짜 문제였던 것 ---")  # 단계 4 제목
print("진짜 문제였던 알림 수:", real_removed_count)   # 0 이면 진짜 문제는 지워지지 않은 것이다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `tuning.py` · `day05_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `tuning.py` 에서 <mark>직접 쓰는 곳 일곱 군데를 씁니다</mark>. 2교시에서 쓴 방식과 위 판다스 문법 상자, 3.1 의 표를 참고해 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day05_3-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **네 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 2줄(알림 수 · 오탐 수), 단계 2는 4줄(빠진 알림 수 1줄 · 빠진 알림 2줄 · 사용자 1줄), 단계 3은 2줄, 단계 4는 1줄입니다.
5. **[보고서]** `day05_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 적용 전후의 오탐 수와 빠진 알림을 적어 주세요.
   - (나) 🔍 예외 규칙을 적용한 뒤 오탐이 몇 개에서 몇 개로 줄었나요? A3(jiwoo 의 업무 시간 밖 로그인)은 같은 IP 인데 왜 줄어들지 않았는지도 적어 주세요.
   - (다) 🔍 `SaaS 평소와 다른 IP` 규칙에서 `203.0.113.80` 을 믿는 IP 로 두면, 이 IP 에서 오는 진짜 공격을 그 규칙으로는 놓칠 수 있습니다. 어떤 경우인지 한 가지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 값이 같은지 비교 | `is_ip_rule = alerts["rule"] == IP_RULE` |
| 리스트 안에 있는지 | `is_trusted = alerts["ip"].isin(TRUSTED_IPS)` |
| 두 조건이 모두 맞는 행 | `is_removed = is_ip_rule & is_trusted` |
| 조건에 맞는 행만 | `kept_alerts = alerts[is_kept]` |
| 같은 값을 한 번씩만 | `removed_users = removed_alerts["user"].unique()` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 규칙을 합쳐 놓친 문제 다시 세기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「203.0.113.50 은 로그인에 5번 실패한 뒤 성공하고 관리자 화면까지 요청했습니다. 사고 조사팀이 이것을 진짜 문제로 확인했습니다(문제 번호 `P4`, `problems.json` 에 있습니다). 그런데 오늘 알림 표에는 이 IP 의 알림이 없습니다. 이번 주 초에 만든 로그인 규칙은 이 IP 를 찾아 알림을 1건 냈습니다(알림 번호 `A8`, `login_alerts.json` 에 있습니다).
>
> 로그인 규칙의 알림을 합치면 놓친 문제가 몇 개 줄고 오탐은 늘지 않는지 확인해 주세요. 결과는 보고서에 한 문장으로 적을 수 있게 정리해 주세요.」
> - **왜 중요한가**: <mark>규칙을 하나 더 합치면 놓친 문제는 줄지만 오탐이 늘 수도 있어서, 합친 뒤에 다시 세어 봐야 합니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 규칙마다 찾는 문제가 다릅니다. 한 규칙이 놓친 문제는 다른 규칙이 찾을 수 있으므로, 알림 표를 합쳐서 한꺼번에 평가합니다.
2. 오늘 질문은 하나입니다. <mark>**규칙의 알림을 합치면 놓친 문제는 몇 개 남고, 오탐은 몇 개인가?**</mark>
3. 평가 결과는 숫자 세 개(알림 수 · 오탐 수 · 놓친 문제 수)를 한 문장으로 적어 두면, 규칙을 고칠 때 전후를 비교하기 쉽습니다.

### 📖 4.1 진짜 문제 5개를 어느 규칙이 찾는가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 문제 | 내용 | 찾는 알림 |
|---|---|---|
| P1 | dami 가 퇴사한 계정으로 서버에 요청함 | A1 (서버 반복 거절) |
| P2 | seoyeon 이 업무와 상관없는 파일을 대량으로 내려받음 | A6 (SaaS 대량 다운로드) |
| P3 | 198.51.100.90 이 스캐너 경로를 요청함 | A7 (웹 경로 스캔) |
| P4 | 203.0.113.50 이 로그인 5번 실패 뒤 성공함 | A8 (웹 로그인 반복 실패) — **오늘 합칩니다** |
| P5 | seoyeon 이 권한 없는 정산 조회를 시도함 | **없음** |

- 오탐은 `problem` 열이 비어 있어서, 빈 값을 지우면 알림이 가리키는 문제 번호만 남습니다.
- A8 을 합치면 P4 가 잡혀서 놓친 문제가 2개에서 1개(P5)로 줄어듭니다.
- 오탐은 A8 이 진짜 문제(`real` 이 `True`)라서 늘지 않습니다. 오탐은 3교시에서 줄인 2개(A2 · A3) 그대로입니다.
- <mark>P5 는 오늘 규칙으로는 찾을 수 없습니다.</mark> 보고서 (다)에서 어떤 규칙이 필요한지 생각해 봅니다.

**🐼 판다스 문법 상자 — 표 두 개를 이어 붙이기 `pd.concat`**

**<mark>`pd.concat([표1, 표2])`</mark> 는 열 이름이 같은 표 두 개를 위아래로 이어 붙여 표 하나로 만듭니다**

아래는 규칙 두 개가 낸 알림 표입니다. 두 표를 하나로 합칩니다. 표는 반드시 **대괄호 `[ ]` 안에 리스트로** 묶어 전달합니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

first_data = {                                     # 첫 번째 규칙의 알림 내용
    "id": ["A1", "A2"],                            # id 열
    "rule": ["서버 반복 거절", "서버 반복 거절"],  # rule 열
}
first_alerts = pd.DataFrame(first_data)            # 첫 번째 알림 표를 만든다
print(first_alerts)                                # 표를 출력한다
```

실행 결과:

```
   id      rule
0  A1  서버 반복 거절
1  A2  서버 반복 거절
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
second_data = {                            # 두 번째 규칙의 알림 내용
    "id": ["A8"],                          # id 열
    "rule": ["웹 로그인 반복 실패"],       # rule 열
}
second_alerts = pd.DataFrame(second_data)  # 두 번째 알림 표를 만든다
print(second_alerts)                       # 표를 출력한다
```

실행 결과:

```
   id         rule
0  A8  웹 로그인 반복 실패
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
merged_alerts = pd.concat([first_alerts, second_alerts])  # 두 표를 대괄호 리스트로 묶어 위아래로 이어 붙인다
print(merged_alerts)                                      # 합친 표를 출력한다
```

실행 결과:

```
   id         rule
0  A1     서버 반복 거절
1  A2     서버 반복 거절
0  A8  웹 로그인 반복 실패
```

- 읽는 법: 세 번째 출력에는 알림 세 개(A1 · A2 · A8)가 모두 들어 있습니다. <mark style="background:#bde3ff">왼쪽 번호는 각 표의 번호를 그대로 가져와서 `0` 이 두 번 나오지만</mark> 내용은 모두 합쳐진 것입니다.
- 열 이름이 같아야 같은 열끼리 이어 붙습니다. 이름이 다르면 빈 값(`NaN`)이 생깁니다.

**🐼 판다스 문법 상자 — 빈 값 지우기 `.dropna()`**

**<mark>`열.dropna()`</mark> 는 열에서 비어 있는 값(`None`)을 지우고 나머지만 남깁니다**

아래는 알림 표이고, `problem` 열은 진짜 문제를 가리키는 번호입니다. 문제가 아니었던 알림은 번호가 비어 있습니다. 번호가 있는 것만 남깁니다.

```python
import pandas as pd  # 판다스를 pd 라는 짧은 이름으로 불러온다

data = {                                  # 표에 넣을 내용(열 이름: 값들)
    "id": ["A1", "A2", "A3", "A4"],       # id 열
    "problem": ["P1", None, "P3", None],  # problem 열 (문제가 아니었으면 None)
}
df = pd.DataFrame(data)                   # 내용으로 표(DataFrame)를 만든다
print(df)                                 # 표를 출력한다
```

실행 결과:

```
   id problem
0  A1      P1
1  A2    None
2  A3      P3
3  A4    None
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
problem_ids = df["problem"].dropna()  # problem 열에서 비어 있는 값을 지운다
print(problem_ids)                    # 남은 문제 번호를 출력한다
```

실행 결과:

```
0    P1
2    P3
Name: problem, dtype: object
```

- 읽는 법: 첫 번째 출력에서 `problem` 이 비어 있는 행은 `None` 으로 보입니다. <mark style="background:#bde3ff">두 번째 출력에는 번호가 있는 0번 행(P1)과 2번 행(P3)만</mark> 남았습니다. `Name: problem, dtype: object` 줄은 몰라도 됩니다.
- `.dropna()` 는 괄호까지 써야 합니다. 괄호를 빼면 `isin` 에 넣을 때 오류가 납니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_table` · `apply_exception` | 파일 경로 · 알림 표 | 표 · 빼낸 알림 표와 남은 알림 표(미리 채움, 3교시와 같은 코드) |
| `merge_alerts` | 알림 표 두 개 | 합친 알림 표 |
| `evaluate` | 합친 알림 표 · 진짜 문제 표 | 오탐 수와 놓친 진짜 문제 표 |
| `make_summary` | 알림 수 · 오탐 수 · 놓친 문제 수 | 한 문장 |

- **직접 쓰는 곳은 여섯 군데**(번호 1 ~ 6)이고, 함수 세 개 안에 나뉘어 있습니다.
  - `merge_alerts`(1번, 1곳): 두 표를 이어 붙입니다.
  - `evaluate`(2 ~ 5번, 4곳): 알림이 가리키는 문제 번호만 남기고(빈 값 지우기), 그 번호가 알림에 있는지 구한 뒤, 놓친 문제를 뒤집어 고릅니다.
  - `make_summary`(6번, 1곳): 숫자를 문자열로 바꿔 이어 붙여 한 문장을 만듭니다.
- 오늘 새 문법은 `.dropna()` 하나입니다. `pd.concat` 은 이번 주에 한 번 쓴 것을 다시 설명합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 알림을 합쳐 놓친 문제 다시 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>예외 규칙으로 오탐은 줄였지만, 놓친 진짜 문제 2개는 그대로입니다</mark>.
- **그래서 만드는 것**: `final_check.py` 입니다.
  - 예외 규칙을 적용한 알림에 로그인 규칙의 알림을 합칩니다.
  - 합친 알림의 오탐 수와 놓친 문제를 다시 구합니다.
  - 결과를 한 문장으로 만듭니다.
- **실행하면**: <mark>단계 1: 예외 규칙으로 빠진 알림과 남은 알림, 단계 2: 합친 알림 수, 단계 3: 오탐 수, 단계 4: 아직 놓친 문제, 단계 5: 한 문장 요약이 나옵니다.</mark>
- **현업에서는**: 규칙을 고치거나 더할 때마다 오탐과 미탐을 다시 세어 전후 숫자를 보고서에 남깁니다.

**🎯 할 일**

1. `final_check.py` · `day05_4-1_run.py` 두 파일을 만들고, `final_check.py` 의 세 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>합친 알림 수</mark>(단계 2), <mark>오탐 수</mark>(단계 3), <mark>아직 놓친 문제</mark>(단계 4), <mark>한 문장 요약</mark>(단계 5)을 읽습니다.
3. 마지막으로 오전 작업 파일이 모두 있는지 확인합니다.

**`final_check.py`**

```python
import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
LOGIN_ALERTS_PATH = "login_alerts.json"               # 읽을 로그인 규칙 알림 파일 이름
PROBLEMS_PATH = "problems.json"                       # 읽을 진짜 문제 파일 이름
IP_RULE = "SaaS 평소와 다른 IP"                       # 예외를 적용할 규칙 이름
TRUSTED_IPS = ["203.0.113.80"]                        # 믿는 IP 리스트 : 협력사 사무실 IP 한 개


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def apply_exception(alerts):                          # 알림 표를 받는 함수
    """IP 규칙 알림 중 믿는 IP 에서 온 것만 빼낸다.
    3교시에서 만든 예외 규칙을 다시 적용할 때 쓴다.
    """
    is_ip_rule = alerts["rule"] == IP_RULE            # 각 알림이 IP 규칙의 알림인지 비교한다
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)       # 각 알림의 IP 가 믿는 IP 리스트에 있는지 구한다
    is_removed = is_ip_rule & is_trusted              # IP 규칙의 알림이면서 믿는 IP 에서 온 것만 True 로 만든다
    removed_alerts = alerts[is_removed]               # 빼낼 알림만 골라 새 표로 만든다
    is_kept = ~is_removed                             # 빼지 않을 알림을 True 로 만든다
    kept_alerts = alerts[is_kept]                     # True 인 행만 골라 새 표로 만든다
    return removed_alerts, kept_alerts                # 빼낸 알림 표와 남은 알림 표를 리턴한다


def merge_alerts(alerts, login_alerts):               # 알림 표 두 개를 받는 함수
    """두 규칙 묶음의 알림 표를 위아래로 이어 하나로 만든다.
    새 규칙의 알림까지 한꺼번에 평가할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. pd.concat 에 두 표를 대괄호 리스트로 묶어 전달하고, 합친 표를 all_alerts 에 담는다 (모양: pd.concat([표1, 표2]))
    return all_alerts                                 # 합친 알림 표를 리턴한다


def evaluate(all_alerts, problems):                   # 알림 표와 진짜 문제 표를 받는 함수
    """합친 알림에서 오탐 수와 놓친 문제를 구한다.
    튜닝을 마친 뒤 결과를 마지막으로 평가할 때 쓴다.
    """
    is_real = all_alerts["real"]                      # real 열(진짜 문제이면 True)을 꺼낸다
    is_false = ~is_real                               # 문제가 아니었던 알림을 True 로 만든다
    false_alarms = all_alerts[is_false]               # True 인 행만 골라 새 표로 만든다
    false_alarm_count = len(false_alarms)             # 오탐이 몇 개인지 센다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. all_alerts 의 "problem" 열에서 빈 값을 .dropna() 로 지워 caught_ids 에 담는다
    # 3. problems 의 "id" 열이 caught_ids 안에 있는지 isin 으로 구해 is_caught 에 담는다
    # 4. is_caught 를 ~ 로 뒤집어 is_missed 에 담는다
    # 5. problems 에서 is_missed 가 True 인 행만 골라 missed_problems 에 담는다
    return false_alarm_count, missed_problems         # 오탐 수와 놓친 문제 표를 리턴한다


def make_summary(alert_count, false_alarm_count, missed_count):  # 세 개수를 받는 함수
    """알림 수 · 오탐 수 · 놓친 문제 수를 한 문장으로 만든다.
    평가 결과를 보고서에 한 줄로 적을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. "알림 " 과 알림 수, "개 중 오탐 " 과 오탐 수, "개 · 놓친 문제 " 와 놓친 문제 수, "개" 를 + 로 이어 summary 에 담는다 (숫자는 str() 로 문자열로 바꿔서 이어 붙인다)
    return summary                                    # 한 문장을 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 채우기 전에 실행하면 `NameError: name 'all_alerts' is not defined` 오류가 납니다. 1번을 아직 안 썼기 때문입니다.

**`day05_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

```python
from final_check import load_table, apply_exception, merge_alerts, evaluate, make_summary, ALERTS_PATH, LOGIN_ALERTS_PATH, PROBLEMS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
login_alerts = load_table(LOGIN_ALERTS_PATH)          # 로그인 규칙 알림 파일을 표로 읽는다
problems = load_table(PROBLEMS_PATH)                  # 진짜 문제 파일을 표로 읽는다

removed_alerts, kept_alerts = apply_exception(alerts)  # 믿는 IP 예외 규칙을 적용한다
removed_count = len(removed_alerts)                   # 빠진 알림이 몇 개인지 센다
kept_count = len(kept_alerts)                         # 남은 알림이 몇 개인지 센다
print("--- 단계 1: 믿는 IP 예외 규칙 적용 ---")       # 단계 1 제목
print("빠진 알림 수:", removed_count)                 # 빠진 알림 수를 출력한다
print("남은 알림 수:", kept_count)                    # 남은 알림 수를 출력한다

all_alerts = merge_alerts(kept_alerts, login_alerts)  # 로그인 규칙의 알림을 합친다
all_count = len(all_alerts)                           # 합친 알림이 몇 개인지 센다
print("--- 단계 2: 로그인 규칙의 알림 합치기 ---")    # 단계 2 제목
print("합친 뒤 알림 수:", all_count)                  # 합친 알림 수를 출력한다

false_alarm_count, missed_problems = evaluate(all_alerts, problems)  # 오탐 수와 놓친 문제를 구한다
print("--- 단계 3: 합친 알림의 오탐 ---")             # 단계 3 제목
print("오탐 수:", false_alarm_count)                  # 오탐 수를 출력한다

missed_count = len(missed_problems)                   # 놓친 문제가 몇 개인지 센다
print("--- 단계 4: 아직 놓친 진짜 문제 ---")          # 단계 4 제목
print("미탐 수:", missed_count)                       # 미탐 수를 출력한다
missed_list = missed_problems.to_dict("records")      # 표를 문제 딕셔너리 리스트로 바꾼다
for problem in missed_list:                           # 놓친 문제를 하나씩 꺼낸다
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])  # 문제 번호 · 대상 · 내용을 출력한다

summary = make_summary(all_count, false_alarm_count, missed_count)  # 결과를 한 문장으로 만든다
print("--- 단계 5: 한 문장 요약 ---")                 # 단계 5 제목
print(summary)                                        # 요약 문장을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `final_check.py` · `day05_4-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `final_check.py` 에서 <mark>직접 쓰는 곳 여섯 군데를 씁니다</mark>. 위 판다스 문법 상자와 4.1 의 표를 참고해 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day05_4-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day05_4-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **다섯 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 2줄(빠진 알림 수 · 남은 알림 수), 단계 2와 단계 3은 각각 1줄, 단계 4는 2줄(미탐 수 · 놓친 문제), 단계 5는 1줄입니다.
5. **[보고서]** `day05_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 한 문장 요약을 적어 주세요.
   - (나) 🔍 로그인 규칙의 알림을 합치자 놓친 문제가 몇 개에서 몇 개로 줄었나요? P4 가 잡힌 이유와, 오탐이 늘지 않은 이유를 함께 적어 주세요.
   - (다) 🔍 아직 놓친 P5(seoyeon 의 권한 없는 정산 조회 시도)를 찾으려면 어떤 규칙이 필요하고, 그 규칙을 더하면 오탐이 늘 수 있는 이유는 무엇인지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 표 두 개를 위아래로 이어 붙이기 | `all_alerts = pd.concat([alerts, login_alerts])` |
| 빈 값 지우기 | `caught_ids = all_alerts["problem"].dropna()` |
| 리스트 안에 있는지 | `is_caught = problems["id"].isin(caught_ids)` |
| 조건 뒤집기 | `is_missed = ~is_caught` |
| 숫자를 문자열로 바꿔 이어 붙이기 | `"알림 " + str(alert_count) + "개 중 …"` |

---

### 마무리 · 오전 작업 확인하기

오전 작업을 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다. <mark>오전에는 파일이 모두 있는지만 확인합니다</mark>.

**순서**

1. **[터미널]** `anomaly_detection` 폴더에서 <mark>오늘 만든 파일이 있는지 확인합니다.</mark>
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - `evaluation.py` · `tuning.py` · `final_check.py` · `day05_2-1_run.py` · `day05_3-1_run.py` · `day05_4-1_run.py` · `alerts.json` · `problems.json` · `login_alerts.json` 과 이 안내 · 보고서 두 파일이 보여야 합니다.
2. **[보고서]** `day05_am_report.md` 의 2 · 3 · 4교시 칸에서 <mark>`답:` 뒤가 비어 있는 질문이 없는지</mark> 봅니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 알림 7개 중 오탐 4개, 진짜 문제 5개 중 미탐 2개를 세었다 | 오전 2-1 |
| 믿는 IP 예외 규칙으로 오탐을 4개에서 2개로 줄이고, 진짜 문제가 지워지지 않았음을 확인했다 | 오전 3-1 |
| 로그인 규칙의 알림을 합쳐 놓친 문제를 2개에서 1개로 줄이고 한 문장으로 요약했다 | 오전 4-1 |

오후에는 도커 컴포즈로 서버를 켜고, <mark>정상 요청과 스캐너 요청을 보내 로그를 만든 뒤</mark> 월요일 통합 실습에 쓸 로그를 저장합니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `find_false_alarms` 안

```python
    is_false = ~is_real                               # True 와 False 를 뒤집어 문제가 아니었던 알림을 True 로 만든다
    false_alarms = alerts[is_false]                   # True 인 행만 골라 새 표로 만든다
    false_alarm_rule_counts = false_alarms["rule"].value_counts()  # 오탐이 규칙마다 몇 개인지 센다
```

② `find_missed` 안

```python
    caught_ids = real_alerts["problem"]               # 진짜 알림이 가리키는 문제 번호를 꺼낸다
    is_missed = ~is_caught                            # 알림이 나지 않은 문제를 True 로 만든다
    missed_problems = problems[is_missed]             # True 인 행만 골라 새 표로 만든다
```

③ `count_real_alerts` 안

```python
    real_alert_count = is_real.sum()                  # True 가 몇 개인지 더해서 센다 (True 는 1, False 는 0)
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 알림은 <mark style="background:#bde3ff">**7개**</mark>, 오탐은 <mark style="background:#bde3ff">**4개**</mark>, 미탐은 <mark style="background:#bde3ff">**2개**</mark>입니다.

```
--- 단계 1: 알림 전체 ---
알림 수: 7
--- 단계 2: 진짜 문제였던 알림 (맞게 찾은 알림) ---
진짜 문제였던 알림 수: 3
--- 단계 3: 오탐 (문제가 아닌데 난 알림) ---
오탐 수: 4
오탐이 난 규칙과 오탐 수:
rule
SaaS 평소와 다른 IP      2
서버 반복 거절            1
SaaS 업무 시간 밖 로그인    1
Name: count, dtype: int64
--- 단계 4: 미탐 (알림이 나지 않은 진짜 문제) ---
미탐 수: 2
놓친 문제: P4 203.0.113.50 로그인 5번 실패 뒤 성공하고 관리자 화면을 요청함
놓친 문제: P5 seoyeon 권한 없는 정산 조회를 시도함
```

- (나) A2(gaeun)는 규칙이 정한 조건(서버 거절 3번 이상)에는 맞았지만, 조사해 보니 <mark style="background:#bde3ff">서버 설정 오류였고 공격이나 권한 문제가 아니었습니다.</mark> 그래서 오탐입니다.
  - 그래도 한 번은 확인해야 했던 이유: 조사하기 전에는 설정 오류인지 공격인지 알 수 없기 때문입니다. <mark style="background:#bde3ff">오탐인지는 확인한 뒤에야 알 수 있습니다.</mark>
  - 오탐을 세는 것은 확인한 알림 중 문제가 아니었던 것의 개수를 세는 일입니다.
- (다) P5(seoyeon 의 `SETTLE:QUERY`)는 서버가 한 번 거절했을 뿐이라 「3번 이상 거절」 규칙에 걸리지 않았습니다. 그래서 <mark style="background:#bde3ff">알림이 나지 않았습니다.</mark>
  - 필요한 규칙의 예: 정산처럼 중요한 자원에 권한 없이 접근을 시도하면 한 번만 거절돼도 알리는 규칙입니다.
  - 이런 규칙은 횟수가 아니라 대상의 중요도를 보기 때문에 오탐이 늘 수 있습니다.

**왜**

- <mark>오탐과 미탐은 줄여야 하는 방향이 반대입니다.</mark> 오탐을 줄이려고 규칙을 엄격하게 만들면 미탐이 늘고, 미탐을 줄이려고 규칙을 느슨하게 만들면 오탐이 늡니다. 그래서 둘을 따로 세어 둡니다.

**자주 틀리는 곳**

- `is_false = ~is_real` 대신 `not is_real` 이라고 쓰면 `ValueError` 오류가 납니다. <mark>**표의 열에는 `not` 이 아니라 `~` 를 씁니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`The truth value of a Series is ambiguous`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day05_2-1_run.py", line 14, in <module>
  File "…/anomaly_detection/evaluation.py", line 31, in find_false_alarms
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

  - 줄 번호는 사람마다 다릅니다.
- `is_real.sum()` 에서 괄호를 빼고 `is_real.sum` 으로 쓰면 오류는 나지 않지만 <mark>**숫자가 아니라 `<bound method Series.sum of …>` 라는 긴 글자가 나옵니다.**</mark> 단계 2의 `진짜 문제였던 알림 수:` 줄에 숫자 대신 `<bound method Series.sum of …>` 가 나오면 이 실수입니다. `.sum()` 은 괄호까지 써야 합니다.
- `is_missed = ~is_caught` 에서 `~` 를 빼고 `is_missed = is_caught` 로 쓰면 오류는 나지 않지만 <mark>**단계 4의 `미탐 수:` 가 2가 아니라 3으로 나옵니다.**</mark> 알림이 난 P1 · P2 · P3 이 놓친 문제로 나오는 것이 이 실수의 모습입니다.

**관제에서는**

- 오탐을 세는 것은 담당자의 시간을 지키는 일이고, 미탐을 세는 것은 놓친 위험을 줄이는 일입니다. <mark>규칙을 평가할 때는 이 두 숫자를 함께 보고합니다.</mark>

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `apply_exception` 안

```python
    is_ip_rule = alerts["rule"] == IP_RULE            # 각 알림이 IP 규칙의 알림인지 비교한다
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)       # 각 알림의 IP 가 믿는 IP 리스트에 있는지 구한다
    is_removed = is_ip_rule & is_trusted              # IP 규칙의 알림이면서 믿는 IP 에서 온 것만 True 로 만든다
    kept_alerts = alerts[is_kept]                     # True 인 행만 골라 새 표로 만든다
```

② `count_real_removed` 안

```python
    is_real_removed = removed_alerts["real"]          # real 열(진짜 문제이면 True)을 꺼낸다
    real_removed = removed_alerts[is_real_removed]    # True 인 행만 골라 새 표로 만든다
```

③ `find_removed_users` 안

```python
    removed_users = removed_alerts["user"].unique()   # 같은 사용자는 한 번씩만 꺼낸다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 오탐은 <mark style="background:#bde3ff">**4개에서 2개**</mark>로 줄었고 빠진 알림은 <mark style="background:#bde3ff">**A4 · A5**</mark>(사용자 jiwoo · seoyeon), 빠진 진짜 문제 알림은 <mark style="background:#bde3ff">**0개**</mark>입니다.

```
--- 단계 1: 예외 규칙을 적용하기 전 ---
알림 수: 7
오탐 수: 4
--- 단계 2: 예외 규칙으로 빠진 알림 ---
빠진 알림 수: 2
빠진 알림: A4 SaaS 평소와 다른 IP jiwoo 203.0.113.80
빠진 알림: A5 SaaS 평소와 다른 IP seoyeon 203.0.113.80
빠진 알림의 사용자: ['jiwoo' 'seoyeon']
--- 단계 3: 예외 규칙을 적용한 뒤 ---
알림 수: 5
오탐 수: 2
--- 단계 4: 빠진 알림 중 진짜 문제였던 것 ---
진짜 문제였던 알림 수: 0
```

- (나) 오탐이 <mark style="background:#bde3ff">4개에서 2개로 줄었습니다.</mark> A3 은 같은 IP `203.0.113.80` 에서 왔지만 규칙이 `SaaS 업무 시간 밖 로그인` 이라서, <mark style="background:#bde3ff">예외 규칙이 `IP_RULE` 의 알림만 빼도록 정했기 때문에</mark> 그대로 남았습니다.
  - A3 까지 빼려면 그 규칙에도 예외를 따로 정해야 하고, 그때도 빠진 진짜 문제가 없는지 다시 확인합니다.
- (다) 믿는 IP 에서 <mark style="background:#bde3ff">계정이 도용되어 로그인해도</mark> 이 규칙은 알림을 내지 않습니다. 예를 들어 협력사 사무실에 있는 누군가가 다른 직원의 계정으로 접속해도 「평소와 다른 IP」 알림은 나지 않습니다.
  - 그래서 다른 규칙(대량 다운로드 등)은 예외에서 빼고 그대로 둡니다. 예외는 근거와 함께 기록하고 주기적으로 다시 검토합니다.

**왜**

- <mark>예외를 규칙 하나에만 적용하면 오탐은 줄이면서 다른 규칙이 찾는 진짜 문제는 지키는 효과가 있습니다.</mark> 단계 4의 `진짜 문제였던 알림 수:` 가 0인 것은 빠진 알림 A4 · A5 가 모두 오탐이었다는 뜻입니다.

**자주 틀리는 곳**

- `is_removed = is_ip_rule & is_trusted` 에서 `is_ip_rule &` 를 빼고 `is_removed = is_trusted` 로 쓰면 오류는 나지 않지만 <mark>**단계 4의 `진짜 문제였던 알림 수:` 가 0이 아니라 1로 나옵니다.**</mark> 같은 IP 에서 온 A3 · A6 까지 빠지고, 빠진 A6 은 진짜 문제입니다.
  - 이때 출력은 다음과 같습니다(<mark style="background:#ffc4d6">`빠진 알림 수: 4`</mark> 와 <mark style="background:#ffc4d6">`진짜 문제였던 알림 수: 1`</mark> 이 나오면 이 실수입니다).

```
--- 단계 1: 예외 규칙을 적용하기 전 ---
알림 수: 7
오탐 수: 4
--- 단계 2: 예외 규칙으로 빠진 알림 ---
빠진 알림 수: 4
빠진 알림: A3 SaaS 업무 시간 밖 로그인 jiwoo 203.0.113.80
빠진 알림: A4 SaaS 평소와 다른 IP jiwoo 203.0.113.80
빠진 알림: A5 SaaS 평소와 다른 IP seoyeon 203.0.113.80
빠진 알림: A6 SaaS 대량 다운로드 seoyeon 203.0.113.80
빠진 알림의 사용자: ['jiwoo' 'seoyeon']
--- 단계 3: 예외 규칙을 적용한 뒤 ---
알림 수: 3
오탐 수: 1
--- 단계 4: 빠진 알림 중 진짜 문제였던 것 ---
진짜 문제였던 알림 수: 1
```

**관제에서는**

- 예외 규칙은 오탐을 빠르게 줄이는 방법이지만, <mark>예외를 넣은 뒤에는 빠진 알림 중 진짜 문제가 있는지 항상 확인합니다.</mark> 예외 리스트는 근거와 함께 기록해 두고, 협력사 계약이 끝나면 지웁니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day05_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 세 함수입니다.

① `merge_alerts` 안

```python
    all_alerts = pd.concat([alerts, login_alerts])    # 두 알림 표를 위아래로 이어 붙인다
```

② `evaluate` 안

```python
    caught_ids = all_alerts["problem"].dropna()       # 문제 번호가 비어 있는 알림(오탐)을 빼고 번호만 남긴다
    is_caught = problems["id"].isin(caught_ids)       # 각 문제 번호가 그 안에 있는지 구한다
    is_missed = ~is_caught                            # 알림이 나지 않은 문제를 True 로 만든다
    missed_problems = problems[is_missed]             # True 인 행만 골라 새 표로 만든다
```

③ `make_summary` 안

```python
    summary = "알림 " + str(alert_count) + "개 중 오탐 " + str(false_alarm_count) + "개 · 놓친 문제 " + str(missed_count) + "개"  # 문자열과 숫자를 이어 한 문장으로 만든다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 한 문장 요약은 <mark style="background:#bde3ff">**「알림 6개 중 오탐 2개 · 놓친 문제 1개」**</mark>입니다.

```
--- 단계 1: 믿는 IP 예외 규칙 적용 ---
빠진 알림 수: 2
남은 알림 수: 5
--- 단계 2: 로그인 규칙의 알림 합치기 ---
합친 뒤 알림 수: 6
--- 단계 3: 합친 알림의 오탐 ---
오탐 수: 2
--- 단계 4: 아직 놓친 진짜 문제 ---
미탐 수: 1
놓친 문제: P5 seoyeon 권한 없는 정산 조회를 시도함
--- 단계 5: 한 문장 요약 ---
알림 6개 중 오탐 2개 · 놓친 문제 1개
```

- (나) 놓친 문제가 <mark style="background:#bde3ff">2개(P4 · P5)에서 1개(P5)로 줄었습니다.</mark>
  - P4 가 잡힌 이유: 로그인 규칙의 알림 A8 이 `problem` 열에 `P4` 를 가리키기 때문에 「알림이 난 문제」에 들어갑니다.
  - 오탐이 늘지 않은 이유: A8 은 조사해 보니 진짜 문제(`real` 이 `True`)였기 때문에, 오탐은 3교시에서 줄인 2개(A2 · A3) 그대로입니다.
- (다) P5 를 찾으려면 <mark style="background:#bde3ff">정산처럼 중요한 자원에 권한 없이 접근하면 한 번만 거절돼도 알리는 규칙</mark>이 필요합니다.
  - 그 규칙을 더하면 업무상 실수로 권한 없는 곳을 한 번 건드린 사용자까지 알림이 나서 <mark style="background:#bde3ff">오탐이 늘 수 있습니다.</mark>
  - 그래서 규칙을 더한 뒤에는 오늘처럼 오탐과 미탐을 다시 세어 봅니다.

**왜**

- <mark>규칙을 합치면 놓친 문제는 줄지만, 합친 뒤에 다시 세어 봐야 오탐이 늘지 않았는지 알 수 있습니다.</mark> 숫자 세 개를 한 문장으로 만들어 두면 다음에 규칙을 고칠 때 전후를 바로 비교할 수 있습니다.

**자주 틀리는 곳**

- `pd.concat([alerts, login_alerts])` 대신 `pd.concat(alerts, login_alerts)` 라고 쓰면 `TypeError` 오류가 납니다. <mark>**표는 대괄호 `[ ]` 안에 리스트로 묶어 전달합니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`concat() takes 1 positional argument but 2 were given`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day05_4-1_run.py", line 14, in <module>
  File "…/anomaly_detection/final_check.py", line 37, in merge_alerts
TypeError: concat() takes 1 positional argument but 2 were given
```

  - 줄 번호는 사람마다 다릅니다.
- `.dropna()` 에서 괄호를 빼면 `TypeError` 오류가 납니다. <mark>**`.dropna()` 는 괄호까지 써야 합니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`only list-like objects are allowed to be passed to isin()`</mark> 로 시작하는 줄이 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day05_4-1_run.py", line 19, in <module>
  File "…/anomaly_detection/final_check.py", line 53, in evaluate
TypeError: only list-like objects are allowed to be passed to isin(), you passed a `method`
```

  - 줄 번호는 사람마다 다릅니다.
- `is_missed = ~is_caught` 에서 `~` 를 빼면 오류는 나지 않지만 <mark>**놓친 문제로 알림이 난 문제가 나옵니다.**</mark> 단계 4의 `놓친 문제:` 줄에 P1 · P2 · P3 · P4 가 나오는 것이 이 실수의 모습입니다.

**관제에서는**

- 새 규칙을 운영에 넣기 전에 오탐과 미탐을 세어 전후를 비교하는 것은 흔한 절차입니다. <mark>숫자를 보고서에 한 줄로 남겨 두면 어떤 규칙이 효과가 있었는지 나중에 확인할 수 있습니다.</mark>

---

### 정답 마무리

- `ls` 결과에 오늘 파일들과 이 안내 · 보고서 두 파일이 모두 보이면 됩니다.
- 보고서에 빈 `답:` 이 없으면 됩니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.
