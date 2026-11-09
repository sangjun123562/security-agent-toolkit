# 11/9(월) 오전 · 4과목 이상탐지 ⑥ — Gemini API 를 활용한 AI 요약 만들기 · 탐지부터 보고서까지 한 번에 실행하기 · 4과목 총정리 — 실습

지난 금요일(11/6(금))까지 이상탐지 규칙을 만들고, 알림이 맞았는지 세고, 틀린 알림을 줄였습니다. 오늘 오전에는 <mark>**이번 주에 만든 탐지를 한 번에 실행해 보고서 파일 하나로 남기고**</mark>, 4과목에서 만난 상황을 정리합니다. 4과목의 마지막 수업입니다.

- **2교시**: 11/5 에 저장한 대상별 점수 파일에서 먼저 확인할 대상을 고르고, **AI** 에게 파일에 있는 사실만으로 짧은 요약문을 쓰게 합니다(`event_summary.py`).
- **3교시**: 이벤트 읽기 → 연결 · 탐지 · 점수 → Gemini API 를 활용한 AI 요약 → 보고서 저장을 **`pipeline.py`**(파이프라인, pipeline, 파이프라인: 여러 단계를 순서대로 이어 한 번에 실행하는 프로그램) 하나로 실행합니다.
- **4교시**: **4과목 총정리.** 새로 배우는 것 없이, 상황 8개의 원인과 고치는 방법을 내 말로 정리하고 오전 작업을 깃허브에 올립니다.

오늘은 오전 2 · 3 · 4교시이고, 오후부터는 5과목(자동 대응)을 시작합니다. <mark>깃허브에 올리는 일은 4교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널 · git** 이고, 2 · 3교시에는 1과목에서 만든 **LLM 호출 함수**(`llm_client.py` 의 `call_llm`)를 씁니다.
  - 이 안내에서 말하는 **AI** 는 구글의 **Gemini API** 입니다.
  - `call_llm` 이 Gemini API 에 글을 보내고 답을 받아 옵니다.
- 오늘 새로 배우는 문법은 2교시의 문자열 이어 붙이기 `"구분 글자".join(리스트)` 와 3교시의 `Series.to_dict()` 두 개입니다. 나머지는 이번 주에 쓴 문법(f-문자열 · `if` · `and` · 딕셔너리 · `value_counts()` · `json.dump`)을 다시 씁니다.
- <mark>AI 가 쓰는 요약 문장은 실행할 때마다 조금씩 달라집니다.</mark> 이 안내의 출력 예와 문장이 달라도 정상입니다. 점수와 등급과 건수는 같아야 합니다.
- ⚠ <mark style="background:#ffc4d6">**무료 Gemini 키는 1분에 15번까지만 호출할 수 있습니다.**</mark> 오늘은 2교시 실행에 3번, 3교시 실행마다 3번 호출합니다. `[LLM 호출 실패] 상태 코드 429` 가 나오면 <mark>1분 기다린 뒤 다시 실행</mark>합니다. 실패해도 오늘 프로그램은 멈추지 않도록 만듭니다.
- ⚠ <mark>앞 수업(특히 11/5)에 결석했거나 파일이 없는 사람은 아래 📎 표를 보고, 없는 파일만 「복구 파일 모음」(`day06_am_recovery_files.md`)으로 만듭니다.</mark> 이미 다 가진 사람은 그 파일을 받지 않아도 됩니다.
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 출력이나 샘플 데이터의 값을 근거로 이유까지 서술합니다</mark>.
- 점수 기준(high 60 이상 · mid 35 이상)과 AI 에게 요약시킬 대상 수(3명)는 **고정**하고, <mark>값을 바꿔 가며 비교하지 않습니다</mark>.

📎 **오늘 불러 쓰는 이전 파일**이 있습니다. 아래 표에서 <mark>`event_summary.py` 만 오늘 2교시에 만들고, 나머지는 모두 앞 수업이나 1과목에서 만든 파일</mark>입니다. <mark>없는 파일은 「복구 파일 모음」(`day06_am_recovery_files.md`)으로 만듭니다.</mark> 이 파일은 앞 수업 파일이 없는 사람만 받습니다.

| 파일 | 만든 곳 | 쓰는 곳 | 없거나 완성하지 못했을 때 |
|---|---|---|---|
| `llm_client.py` · `.env`(API 키) | 1과목(`agent_core` 폴더와 `security-agent-toolkit` 폴더) | 2 · 3교시 | 아래 시작하기 3번의 `cp` 명령으로 복사합니다. `agent_core` 에도 없으면 복구 파일 모음의 `llm_client.py` 로 만듭니다 |
| `day03_risk_scores.json` | 11/5 오후 6교시 | 2교시가 읽습니다 | 아래 시작하기 5번의 내용으로 파일을 만듭니다(항상 이 내용으로 덮어씁니다) |
| `normalized_events.json` · `rbac.py` · `config/users.json` · `config/roles.json` | 11/5 오전 안내(`day04_am_suspicious_logs.md`) 시작하기 6번 | 3교시 | 복구 파일 모음의 내용으로 파일을 만듭니다 |
| `access_detection.py` · `saas_detection.py` · `malicious_detection.py` | 11/5 오전 2 · 3 · 4교시 | 3교시 | 복구 파일 모음의 완성본으로 파일을 만듭니다 |
| `correlation.py` · `risk_scores.py` | 11/5 오후 5 · 6교시 | 3교시 | 복구 파일 모음의 완성본으로 파일을 만듭니다 |
| `event_summary.py` | 오늘 2교시 문제 2-1 | 3교시 `pipeline.py` 가 불러옵니다 | 이 안내 문제 2-1 의 코드 칸에 「정답 2-1」의 「채운 코드」를 넣어 완성합니다 |

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치와 앞 수업 파일을 확인합니다(맥북은 `python3`). <mark>`pwd` 가 `…/anomaly_detection` 으로 끝나고, `ls` 결과에 위 표의 11/5 파일들이 보여야</mark> 합니다. 없는 파일이 있으면 복구 파일 모음으로 만든 뒤 `ls` 를 다시 칩니다. <mark>자리를 바꾼 사람은 3번 전에 아래 「.env 와 API 키 다시 받기」를 먼저 합니다.</mark>
   ```bash
   cd anomaly_detection
   pwd
   ls
   ```
   - 명령 풀이: `cd 폴더이름` 그 폴더로 이동 · `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
3. **[터미널]** 1과목에서 만든 LLM 호출 파일을 이 폴더로 복사하고, API 키를 읽을 수 있는지 확인합니다. <mark>마지막 명령에서 `True` 가 나오면</mark> 됩니다. 키 값은 화면에 나오지 않습니다.
   ```bash
   cp ../agent_core/llm_client.py .
   ls llm_client.py
   python -c "from llm_client import read_api_key; print(read_api_key() is not None)"
   ```
   - 명령 풀이: `cp 원본 대상` 파일 복사(`..` 은 한 단계 위 폴더, `.` 은 지금 폴더) · `ls 파일이름` 그 파일이 있는지 확인
4. **오늘 받은 파일 두 개**(`day06_am_ai_summary_pipeline.md`, `day06_am_report.md`)를 <mark>`다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다. 위 📎 표에서 없는 파일이 있는 사람은 `day06_am_recovery_files.md` 도 같은 방법으로 받습니다. 그리고 **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-09(월))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[터미널]** 2교시가 읽을 점수 파일을 만들고 **[VS Code]** 에서 열어 아래 내용을 그대로 붙여 넣습니다. <mark>같은 이름의 파일이 이미 있으면 아래 내용으로 덮어씁니다</mark>(출력이 문서와 같아야 하기 때문입니다).
   ```bash
   touch day03_risk_scores.json
   ls day03_risk_scores.json
   ```
   - 명령 풀이: `touch 파일이름` 빈 파일 만들기 · `ls 파일이름` 그 파일이 있는지 확인

**`day03_risk_scores.json`** — 11/5 오후에 저장한 대상별 점수 기록 5건입니다. `entity` 는 점수를 매긴 대상(사용자 또는 IP), `score` 는 점수, `grade` 는 등급, `reasons` 는 탐지된 규칙 이름입니다. 점수가 높은 순서로 저장돼 있습니다.

```
[
  {
    "entity": "dami",
    "score": 60,
    "grade": "high",
    "reasons": [
      "퇴사한 계정"
    ]
  },
  {
    "entity": "seoyeon",
    "score": 45,
    "grade": "mid",
    "reasons": [
      "평소와 다른 IP",
      "대량 다운로드"
    ]
  },
  {
    "entity": "gaeun",
    "score": 40,
    "grade": "mid",
    "reasons": [
      "규칙은 허용인데 서버가 거절",
      "여러 로그 연결"
    ]
  },
  {
    "entity": "jiwoo",
    "score": 35,
    "grade": "mid",
    "reasons": [
      "업무 시간 밖 로그인",
      "평소와 다른 IP"
    ]
  },
  {
    "entity": "198.51.100.90",
    "score": 30,
    "grade": "low",
    "reasons": [
      "경로 스캔"
    ]
  }
]
```

6. **[터미널]** 파일이 정상인지 확인합니다. <mark>`5` 가 나오고, 아래 두 줄에서 오류가 나오지 않으면</mark> 됩니다. 오류가 나면 그 줄의 파일이 없거나 이름이 다른 것이니 복구 파일 모음으로 만듭니다.
   ```bash
   python -c "import json; print(len(json.load(open('day03_risk_scores.json', encoding='utf-8'))))"
   python -c "from access_detection import load_events, EVENTS_PATH; from saas_detection import pick_saas; from malicious_detection import pick_web_failures"
   python -c "from correlation import find_chains_in_events; from risk_scores import collect_findings, save_records"
   ```

### .env 와 API 키 다시 받기 (자리를 바꾼 사람 · 3번에서 오류가 난 사람)

처음부터 새로 받는 방법입니다. 키를 만들고, 키가 맞는지 확인하고, `.env` 파일에 넣고, 깃허브에 올라가지 않게 막은 뒤, 마지막으로 읽히는지 봅니다.

- **왜 다시 받나**:
  - API 키는 `.env` 파일에 들어 있고, 이 파일은 PC 마다 따로 있습니다.
  - `.env` 는 깃허브에 올리지 않으므로 다른 PC 로 따라오지 않습니다.
  - 자리를 바꾼 PC 에는 `.env` 가 없어서 오늘 2 · 3교시의 AI 호출이 되지 않습니다.
- **먼저 확인하기**: <mark>이미 `.env` 가 있으면 이 절은 건너뜁니다.</mark>
  - **[터미널]** `anomaly_detection` 폴더에서 한 단계 위 폴더의 파일을 숨김 파일까지 봅니다.
    ```bash
    ls -a ..
    ```
  - 명령 풀이: `ls -a` 숨김 파일(이름이 점으로 시작하는 파일)까지 보기 · `..` 한 단계 위 폴더(`security-agent-toolkit`)
  - 나오는 것: 목록에 <mark>`.env` 와 `.gitignore` 가 둘 다 보이면</mark> 됩니다. 하나라도 없으면 아래를 합니다.

**1단계 · 구글 AI Studio 에서 새 키 만들기**

- **[브라우저]** `https://aistudio.google.com` 에 들어갑니다. 바로 키 화면으로 가려면 `https://aistudio.google.com/app/apikey` 를 씁니다.
- **로그인**: 개인 gmail 계정으로 로그인합니다. 학교나 회사 계정은 관리자가 막아 두었을 수 있습니다. 처음이면 약관 동의 화면이 나오고 **동의**를 누릅니다.
- **키 만들기**: 왼쪽 메뉴의 **Get API key** 를 누르고, **Create API key** 를 누릅니다.
  - 이미 만든 키가 있는 사람도 새 키를 만들어도 됩니다.
  - 프로젝트(구글이 키를 묶어 두는 이름)를 고르거나 만들라는 창이 나오면, 제안하는 기본 프로젝트를 고르거나 새로 만들고 계속합니다.
- **키 복사**: 목록에 새 키가 나오면 복사 단추를 눌러 복사합니다. 영문자와 숫자가 섞인 긴 글자이고, 보통 `AIza` 로 시작합니다. <mark>복사한 글자 앞뒤에 빈칸이 끼지 않게</mark> 합니다.
- <mark style="background:#ffc4d6">카드 번호나 결제 정보는 넣지 않습니다.</mark> 결제를 요구하는 화면이 나오면 닫습니다.
- 화면의 글자는 구글이 바꿀 수 있습니다. 이름이 조금 달라도 「API 키를 만든다」는 뜻의 단추를 찾으면 됩니다.
- 「접속할 수 없다」는 화면이 나오면 구글 계정에 생년월일이 등록되어 있는지(`https://myaccount.google.com` › 개인 정보) 확인합니다.

**2단계 · 키가 맞는지 먼저 확인하기**

- **[터미널]** 아래 명령의 `여기에_내_키` 를 복사한 키로 바꿔서 칩니다. 키는 따옴표 안에 그대로 붙여 넣습니다. 화면을 공유하는 중이면 하지 않습니다.
  ```bash
  curl -H "x-goog-api-key: 여기에_내_키" "https://generativelanguage.googleapis.com/v1beta/models"
  ```
  - 명령 풀이: `curl 주소` 주소로 요청을 보내 답을 받아 오기 · `-H "이름: 값"` 요청에 붙이는 머리글(여기서는 키)
- 나오는 것: <mark>`"models"` 로 시작하는 긴 목록이 나오면</mark> 키가 맞습니다. 키의 마지막 글자를 하나 지우고 치면 `UNAUTHENTICATED` 가 나옵니다. 오류 글자가 나오면 키를 다시 복사합니다.
- 같은 명령을 여러 번 반복하지 않습니다. 호출 횟수에 한도가 있습니다.

**3단계 · `.env` 파일 만들기**

- **[터미널]** 한 단계 위 폴더(`security-agent-toolkit`)로 가서 빈 파일 두 개를 만들고 숨김 파일까지 봅니다. <mark>`pwd` 가 `security-agent-toolkit` 으로 끝나야</mark> 합니다.
  ```bash
  cd ..
  pwd
  touch .env .gitignore
  ls -a
  ```
  - 명령 풀이: `cd ..` 한 단계 위 폴더로 이동 · `touch 파일이름들` 빈 파일 만들기(이미 있는 파일은 지우지 않습니다)
  - 나오는 것: 목록에 <mark>`.env` 와 `.gitignore` 가 둘 다 보이면</mark> 됩니다.
  - 이렇게 터미널로 만드는 이유: VS Code 의 저장 창에서 이름을 적으면 `.env.txt` 처럼 뒤에 `.txt` 가 붙는 실수가 잦기 때문입니다.
- **[VS Code]** 왼쪽 파일 목록에서 `security-agent-toolkit` 바로 아래의 `.env` 를 열고 아래 한 줄만 적습니다. <mark>등호 앞뒤에 빈칸을 넣지 않고, 따옴표도 넣지 않습니다.</mark>
  ```
  GEMINI_API_KEY=여기에_복사한_키를_붙여넣습니다
  ```
  - 탭 이름 옆에 점(●)이 없으면 저장된 것입니다. 이 한 줄 말고 다른 글자는 넣지 않습니다.

**4단계 · 깃허브에 키가 올라가지 않게 막기**

- **[VS Code]** `security-agent-toolkit` 바로 아래의 `.gitignore` 를 엽니다. 맨 아래에 `.env` 한 줄이 있는지 보고, 없으면 적습니다.
  ```
  .env
  ```
- **[터미널]** 막혔는지 확인합니다. <mark>목록에 `.env` 가 보이지 않으면</mark> 막힌 것입니다.
  ```bash
  git status
  ```
  - 나오는 것: 바뀐 파일 목록에 `.env` 가 있으면 아직 막히지 않은 것입니다. `.gitignore` 의 `.env` 줄이 맞는지 다시 봅니다. 깃허브에 올리기 전에는 항상 이 확인을 합니다.

**5단계 · 오늘 쓸 폴더에서 읽히는지 확인하기**

- **[터미널]** `anomaly_detection` 폴더로 돌아와 시작하기 3번의 마지막 명령을 칩니다. <mark>`True` 가 나오면</mark> 됩니다. 키 값은 화면에 나오지 않습니다.
  ```bash
  cd anomaly_detection
  pwd
  python -c "from llm_client import read_api_key; print(read_api_key() is not None)"
  ```
  - 명령 풀이: `python -c "코드"` 적은 코드를 바로 실행(맥북은 `python3`)

**막혔을 때**

- `.env.txt` 처럼 이름이 다르게 만들어졌다면, `security-agent-toolkit` 폴더에서 `mv .env.txt .env` 를 칩니다(`mv 이전이름 새이름` 은 이름 바꾸기).
- `False` 가 나오면 `.env` 를 `anomaly_detection` 폴더 안에 만들었거나, `GEMINI_API_KEY=` 글자가 틀렸거나, 등호 앞뒤에 빈칸이 있는 것입니다. 3단계를 다시 봅니다.
- 키가 맞는데(2단계는 성공) 오늘 실행에서 `상태 코드 429` 가 1분을 기다려도 계속 나오면, 구글이 그 계정의 무료 호출 한도를 0 으로 둔 경우가 구글 포럼에 보고되어 있습니다. 보고서 (가)에 「막힘: 429 가 계속 나옴」이라고 적고 넘어갑니다. 요약 자리에는 대체 문장이 나오고 프로그램은 멈추지 않습니다.

**키를 다룰 때 지킬 것**

- 단톡방이나 메신저에 키를 올리지 않습니다.
- 화면을 공유할 때 `.env` 를 열어 두지 않습니다.
- 깃허브에 웹으로 파일을 올릴 때 `.env` 를 끌어다 놓지 않습니다. `.gitignore` 는 웹 업로드를 막아 주지 않습니다.
- 키가 노출됐다면 구글 AI Studio 의 키 목록에서 그 키를 삭제하고 새로 만듭니다. 쓰지 않는 예전 키도 같은 곳에서 삭제해 둡니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'llm_client'`(또는 `correlation` · `risk_scores` · `access_detection` 등): <mark>그 파일이 `anomaly_detection` 폴더 바로 아래에 없다는 뜻</mark>입니다. 위 📎 표의 「없거나 완성하지 못했을 때」를 따라 복구 파일 모음(`day06_am_recovery_files.md`)으로 그 파일을 만듭니다.
- `TypeError: expected str, bytes or os.PathLike object, not NoneType`: <mark>`llm_client.py` 가 `.env` 파일을 찾지 못한 것</mark>입니다. 위 「.env 와 API 키 다시 받기」를 따릅니다. API 키는 화면이나 AI 질문에 붙여 넣지 않습니다.
- `ModuleNotFoundError: No module named 'requests'`: 새 PC 의 가상환경에 `requests` 가 없는 것입니다. 가상환경을 활성화한 뒤 `python -m pip install requests` 를 칩니다.
- `[LLM 호출 실패] 상태 코드 429`: 1분에 15번을 넘었다는 뜻입니다. <mark>1분 기다린 뒤 다시 실행</mark>합니다. 요약 자리에 `(요약 실패 — 점수와 이유를 직접 확인)` 이 나와도 오늘 프로그램이 일부러 그렇게 만든 것이라 정상입니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 점수 파일의 사실만 Gemini API 에 보내 대상별 AI 요약 받기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「11/5 에 대상별 점수 기록(사용자나 IP 마다 위험 점수와 등급을 적은 기록)을 5건 만들어 주셨습니다. 그런데 담당자 세 명이 「평소와 다른 IP」 같은 규칙 이름만 보고는 무슨 일인지 바로 알기 어렵다고 합니다. 내일 아침 회의에서 먼저 확인할 대상 3명이 왜 위험한지 대상마다 한두 문장으로 정리해 주세요.
>
> 다만 AI 가 파일에 없는 내용을 지어내면 안 됩니다. 없는 사고를 말하면 엉뚱한 사람을 조사하게 됩니다.」
> - **왜 중요한가**: <mark>점수만 있고 설명이 없으면 담당자가 로그를 처음부터 다시 읽어야 하고, AI 가 없는 내용을 지어내면 잘못된 대상을 조사하게 됩니다.</mark> 그래서 AI 에게는 파일에 있는 사실만 보내고, 그 사실만 쓰라고 지시합니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 먼저 떠올리기 — 11/5 에 만든 점수 기록

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- **점수 기록이란**: <mark>사용자나 IP 하나마다 「얼마나 위험한지」를 점수와 등급으로 적은 기록</mark>입니다.
  - 11/2 하루 동안 쌓인 로그 57개를 이번 주에 만든 탐지 규칙으로 검사했습니다.
  - 규칙에 걸린 대상(사용자 또는 IP)마다 점수를 더해 한 건씩 적었습니다.
  - 그 결과가 5건이고, 파일 이름은 `day03_risk_scores.json` 입니다.
- **왜 만들었나**:
  - 규칙에 걸린 알림이 여러 개여서 어느 대상부터 확인해야 할지 알 수 없었습니다.
  - 점수를 매기면 높은 순서대로 확인할 순서가 정해집니다.
- **점수는 이렇게 정했습니다**:
  - 규칙마다 점수가 정해져 있습니다. 예를 들어 `퇴사한 계정` 60점, `대량 다운로드` 25점, `평소와 다른 IP` 20점입니다.
  - 같은 대상에게 걸린 규칙의 점수를 모두 더합니다. 예를 들어 seoyeon 은 `평소와 다른 IP` 20점 + `대량 다운로드` 25점 = <mark>45점</mark>입니다.
  - 합계로 등급을 정합니다. <mark>60점 이상이 `high`, 35점 이상이 `mid`, 그보다 낮으면 `low`</mark> 입니다.
- **한 건에 든 네 가지**는 다음과 같습니다.

| 키 | 뜻 | 예 (seoyeon) |
|---|---|---|
| `entity` | 점수를 매긴 대상(사용자 이름 또는 IP) | `seoyeon` |
| `score` | 합계 점수 | `45` |
| `grade` | 등급 | `mid` |
| `reasons` | 걸린 규칙 이름의 리스트 | `평소와 다른 IP` · `대량 다운로드` |

- **오늘 이 파일은**:
  - 시작하기 5번에서 내용을 붙여 넣어 만듭니다. 11/5 에 이미 저장한 사람도 같은 내용으로 덮어씁니다.
  - 오늘 2교시는 이 파일을 읽기만 합니다. 점수와 등급은 바꾸지 않습니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 11/5 에 만든 점수 파일에는 대상 · 점수 · 등급 · 규칙 이름이 있지만, 담당자가 읽기에는 규칙 이름만 나열돼 있습니다.
2. 오늘 질문은 하나입니다. <mark>**AI 가 지어내지 않고 점수 파일의 사실만으로 요약하게 하려면, AI 에게 무엇을 보내야 하는가?**</mark>
3. 일을 둘로 나누고, 각각 맡는 쪽이 다릅니다.

| 일 | 맡는 쪽 | 이유 |
|---|---|---|
| 점수 · 등급 정하기 | 코드(`risk_scores.py`) | 같은 입력이면 항상 같은 결과가 나와야 확인할 순서가 흔들리지 않습니다 |
| 설명 문장 쓰기 | AI(`call_llm`) | 문장은 실행마다 조금 달라도 순서가 바뀌지 않습니다 |

- <mark>AI 는 점수와 등급을 바꾸지 않고, 코드가 정한 값을 문장으로 풀어 쓰기만 합니다.</mark>

### 📖 2.1 AI 에게 보내는 글과 요약할 대상

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 문법 상자의 코드는 눈으로 읽으면 됩니다.

`day03_risk_scores.json` 의 기록 5건입니다. 점수가 높은 순서로 저장돼 있습니다.

| 대상 | 점수 | 등급 | 탐지된 규칙 |
|---|---|---|---|
| dami | 60 | high | 퇴사한 계정 |
| seoyeon | 45 | mid | 평소와 다른 IP · 대량 다운로드 |
| gaeun | 40 | mid | 규칙은 허용인데 서버가 거절 · 여러 로그 연결 |
| jiwoo | 35 | mid | 업무 시간 밖 로그인 · 평소와 다른 IP |
| 198.51.100.90 | 30 | low | 경로 스캔 |

- 요약할 대상은 <mark>`low` 가 아닌 대상 중 앞에서부터 3명</mark>입니다. 위 표에서는 dami · seoyeon · gaeun 입니다. 기록이 점수 순서로 저장돼 있어서, 앞에서부터 고르면 먼저 확인할 대상부터 요약됩니다.
- AI 에게 보내는 글은 두 덩어리입니다.
  - **지시문**: AI 가 지킬 규칙입니다. 「아래 [사실]만 사용하세요 · 없는 내용을 지어내지 마세요 · 공격이라고 단정하지 마세요」를 적습니다.
  - **[사실]**: 점수 파일에서 꺼낸 값입니다. 대상 · 등급 · 점수와 탐지된 내용을 한 줄로 적습니다.
- 규칙 이름(`평소와 다른 IP`)만 보내면 AI 가 그 이름의 뜻을 짐작해서 쓰게 됩니다. 그래서 규칙 이름마다 <mark>사실 한 문장</mark>을 미리 정해 두고(`RULE_MEANING`) 그 문장을 보냅니다.

| 규칙 이름 | AI 에게 보내는 사실 한 문장 |
|---|---|
| 퇴사한 계정 | 퇴사한 사람의 계정으로 서버에 요청함 |
| 권한 없음 | 역할에 없는 권한을 서버에 요청함 |
| 규칙은 허용인데 서버가 거절 | 규칙으로는 허용되는 요청을 서버가 거절함 |
| 업무 시간 밖 로그인 | 업무 시간 밖에 SaaS 에 로그인함 |
| 평소와 다른 IP | 평소와 다른 IP 에서 SaaS 에 접속함 |
| 대량 다운로드 | SaaS 에서 파일을 한꺼번에 많이 내려받음 |
| 경로 스캔 | 없는 주소를 연달아 요청해 서버에 무엇이 있는지 확인함 |
| 여러 로그 연결 | 서로 다른 로그에서 한 사용자의 이벤트가 짧은 시간 안에 확인됨 |

- 한 대상에 규칙이 여러 개이면 사실 문장도 여러 개입니다. 이 문장들을 한 줄로 이어 붙이는 데 아래 문법 상자의 `join` 을 씁니다.
- AI 호출이 실패하면 빈 문자열이 돌아옵니다. 그대로 두면 요약 칸이 비므로, <mark>실패했다는 문장(`FAIL_TEXT`)으로 대신 채워</mark> 담당자가 그 대상은 점수와 이유를 직접 읽게 합니다.

**🐍 문법 상자 — 리스트를 한 문자열로 이어 붙이기 `"구분 글자".join(리스트)`**

**<mark>`"구분 글자".join(리스트)`</mark> 는 리스트에 든 글자들을 구분 글자로 이어 붙여 글자 하나로 만듭니다**

과일 이름 세 개가 든 리스트로 익힙니다.

```python
words = ["사과", "배", "귤"]   # 과일 이름 세 개의 리스트
fruit_text = ", ".join(words)  # 이름들을 ", " 로 이어 붙여 글자 하나로 만든다
print(fruit_text)              # 이어 붙인 글자를 출력한다
```

실행 결과:

```
사과, 배, 귤
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
slash_text = " / ".join(words)  # 구분 글자를 " / " 로 바꿔 이어 붙인다
print(slash_text)               # 이어 붙인 글자를 출력한다
```

실행 결과:

```
사과 / 배 / 귤
```

- **읽는 법**:
  - <mark style="background:#bde3ff">점 앞의 `", "` 가 구분 글자</mark>이고, 괄호 안의 `words` 가 이어 붙일 리스트입니다.
  - 구분 글자는 이름과 이름 사이에만 들어가고, 맨 앞과 맨 뒤에는 붙지 않습니다.
- **오늘은**:
  - 과일 이름 대신 「사실 문장」을 이어 붙입니다.
  - 구분 글자는 `"; "`(세미콜론과 공백 한 칸)입니다.
- **주의**:
  - <mark style="background:#ffc4d6">`join` 을 쓰지 않고 리스트를 그대로 출력하면 대괄호와 따옴표가 그대로 나옵니다.</mark> 예를 들어 `['사과', '배', '귤']` 처럼 보입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_records` | 점수 파일 경로 | 기록 리스트(미리 채움) |
| `pick_records_to_summarize` | 기록 리스트 | 요약할 기록 리스트 |
| `describe_reasons` | 규칙 이름 리스트 | 사실 문장을 이어 붙인 문자열 |
| `build_prompt` | 기록 하나 | AI 에게 보낼 글 |
| `summarize_record` | 기록 하나 | 요약 문장(실패하면 `FAIL_TEXT`) |

- **직접 쓰는 곳은 일곱 군데**(번호 1 ~ 7)이고, 함수 네 개 안에 나뉘어 있습니다.
  - `pick_records_to_summarize`(1 · 2번): low 가 아니고 아직 3명이 안 찼으면 고른 목록에 추가합니다.
  - `describe_reasons`(3번): 사실 문장들을 `join` 으로 이어 붙입니다.
  - `build_prompt`(4번): 점수 파일의 값을 f-문자열로 [사실] 한 줄에 넣습니다.
  - `summarize_record`(5 · 6 · 7번): Gemini API 를 호출하고, 결과가 비어 있으면 대체 문장을 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · AI 에게 사실만 보내 대상별 요약 받기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>점수 기록 5건에 규칙 이름만 있어서 담당자가 왜 위험한지 바로 알 수 없습니다</mark>.
- **그래서 만드는 것**: `event_summary.py` 입니다.
  - 점수 파일에서 low 가 아닌 대상을 앞에서부터 3명 고릅니다.
  - 대상마다 지시문과 [사실]을 합쳐 AI 에게 보낼 글을 만듭니다.
  - Gemini API 를 호출해 요약을 받고, 실패하면 대체 문장을 씁니다.
- **실행하면**: <mark>단계 1: 불러온 기록 수, 단계 2: 요약할 대상, 단계 3: AI 에게 보내는 글(seoyeon), 단계 4: 대상별로 Gemini API 를 활용한 AI 요약이 나옵니다.</mark>
- **현업에서는**: AI 에게 값만 보내고 판단은 코드가 하면, AI 가 틀린 말을 해도 점수와 등급은 그대로여서 담당자가 사실과 요약을 나란히 보고 확인할 수 있습니다.

**🎯 할 일**

1. `event_summary.py` · `day06_2-1_run.py` 두 파일을 만들고, `event_summary.py` 의 네 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>요약할 대상</mark>(단계 2), <mark>AI 에게 보내는 글</mark>(단계 3), <mark>Gemini API 를 활용한 AI 요약</mark>(단계 4)을 읽습니다. 단계 4 에서 Gemini API 를 3번 호출합니다.

**`event_summary.py`**

```python
import json                                             # JSON 파일을 읽기 위해 json 을 불러온다
from llm_client import call_llm                         # 1과목에서 만든 LLM 호출 함수를 불러온다

RISK_PATH = "day03_risk_scores.json"                    # 읽을 점수 파일 이름(11/5 에 저장한 파일)
SUMMARY_LIMIT = 3                                       # AI 에게 요약을 시킬 대상의 최대 수
FAIL_TEXT = "(요약 실패 — 점수와 이유를 직접 확인)"     # AI 호출이 실패했을 때 대신 쓰는 문장
RULE_MEANING = {                                        # 탐지된 규칙 이름마다 사실 한 문장
    "퇴사한 계정": "퇴사한 사람의 계정으로 서버에 요청함",
    "권한 없음": "역할에 없는 권한을 서버에 요청함",
    "규칙은 허용인데 서버가 거절": "규칙으로는 허용되는 요청을 서버가 거절함",
    "업무 시간 밖 로그인": "업무 시간 밖에 SaaS 에 로그인함",
    "평소와 다른 IP": "평소와 다른 IP 에서 SaaS 에 접속함",
    "대량 다운로드": "SaaS 에서 파일을 한꺼번에 많이 내려받음",
    "경로 스캔": "없는 주소를 연달아 요청해 서버에 무엇이 있는지 확인함",
    "여러 로그 연결": "서로 다른 로그에서 한 사용자의 이벤트가 짧은 시간 안에 확인됨",
}
PROMPT_RULES = (                                        # AI 에게 주는 지시문 : 사실만 쓰게 하는 규칙
    "당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. "
    "[사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 먼저 확인할 것을 한 가지 제안하세요.\n"
)


def load_records(path):                                 # 점수 파일 경로를 받는 함수
    """점수 파일(JSON)을 읽어 기록 리스트로 리턴한다.
    11/5 에 저장한 대상별 점수 · 등급 · 이유를 다시 쓸 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:          # 파일을 읽기 모드로 연다
        records = json.load(file)                       # JSON 글자를 리스트로 바꾼다
    return records                                      # 기록 리스트를 리턴한다


def pick_records_to_summarize(records):                 # 기록 리스트를 받는 함수
    """low 가 아닌 대상 중 앞에서부터 SUMMARY_LIMIT 명만 고른다.
    기록은 점수가 높은 순으로 저장돼 있어서, 먼저 확인할 대상부터 요약할 때 쓴다.
    """
    picked = []                                         # 고른 기록을 담을 빈 리스트
    for record in records:                              # 기록을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. record["grade"] 가 "low" 가 아니고(!=) 그리고(and) picked 의 개수(len)가 SUMMARY_LIMIT 보다 작으면 (if)
        # 2.   picked 에 record 를 추가한다
    return picked                                       # 고른 기록을 리턴한다


def describe_reasons(reasons):                          # 탐지된 규칙 이름 리스트를 받는 함수
    """규칙 이름마다 사실 한 문장을 찾아 세미콜론으로 이어 붙인 문자열을 리턴한다.
    AI 에게 보낼 [사실]에 탐지된 내용을 넣을 때 쓴다.
    """
    meanings = []                                       # 사실 문장을 담을 빈 리스트
    for rule in reasons:                                # 규칙 이름을 하나씩 꺼낸다
        meanings.append(RULE_MEANING[rule])             # 그 규칙의 사실 문장을 추가한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. "; " 에 .join(meanings) 를 붙여 사실 문장을 이어 붙인 결과를 meaning_text 에 담는다
    return meaning_text                                 # 이어 붙인 문자열을 리턴한다


def build_prompt(record):                               # 기록 하나를 받는 함수
    """AI 에게 보낼 글(지시문 + 사실)을 만든다.
    점수 파일의 값만 넣어서 AI 가 다른 내용을 지어내지 못하게 할 때 쓴다.
    """
    entity = record["entity"]                           # 대상(사용자 또는 IP)
    grade = record["grade"]                             # 등급
    score = record["score"]                             # 점수
    meaning_text = describe_reasons(record["reasons"])  # 탐지된 내용을 사실 문장으로 바꾼다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. f-문자열 f"[사실] 대상: {entity} / 등급: {grade} / 점수: {score}점 / 탐지된 내용: {meaning_text}" 의 결과를 facts 에 담는다
    prompt = PROMPT_RULES + facts                       # 지시문과 사실을 이어 붙인다 — 미리 채운 줄
    return prompt                                       # AI 에게 보낼 글을 리턴한다


def summarize_record(record):                           # 기록 하나를 받는 함수
    """AI 에게 기록 하나의 요약을 시키고, 호출이 실패하면 FAIL_TEXT 를 리턴한다.
    AI 호출이 실패해도 나머지 작업이 멈추지 않게 할 때 쓴다.
    """
    prompt = build_prompt(record)                       # AI 에게 보낼 글을 만든다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. call_llm(prompt) 의 결과를 summary 에 담는다
    # 6. summary 가 빈 문자열("")이면 (if)
    # 7.   FAIL_TEXT 를 summary 에 담는다
    return summary                                      # 요약 문장을 리턴한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1번은 `for` 안이라 앞에 공백 8개, 2번은 `if` 안이라 12개입니다. 3 ~ 6번은 함수 안이라 4개이고, 7번은 6번의 `if` 안이라 8개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.**
- 3번의 `"; "` 는 세미콜론과 공백 한 칸입니다. <mark>공백까지 같아야 출력이 같습니다.</mark>
- 4번의 문장은 따옴표 앞에 `f` 를 붙여야 `{entity}` 같은 부분이 값으로 바뀝니다. `f` 를 빼면 `{entity}` 라는 글자가 그대로 나갑니다.
- 채우기 전에 실행하면 `IndentationError: expected an indented block` 오류가 납니다. `for` 안쪽의 1 · 2번이 비어 있기 때문입니다.

**`day06_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(리스트)` 는 리스트의 개수입니다.

```python
from event_summary import load_records, pick_records_to_summarize, summarize_record, build_prompt, RISK_PATH, SUMMARY_LIMIT  # 방금 만든 함수를 불러온다

records = load_records(RISK_PATH)                                                 # 점수 파일을 기록 리스트로 읽는다
record_count = len(records)                                                       # 기록이 모두 몇 건인지 센다
print("--- 단계 1: 불러온 점수 기록", record_count, "건")                         # 단계 1 시작을 알리는 줄과 건수

picked = pick_records_to_summarize(records)                                       # 요약할 기록을 고른다
picked_count = len(picked)                                                        # 고른 기록이 몇 건인지 센다
print("--- 단계 2: 요약할 대상", picked_count, "명 (최대", SUMMARY_LIMIT, "명)")  # 단계 2 시작을 알리는 줄과 인원
for record in picked:                                                             # 고른 기록을 하나씩 꺼낸다
    print(record["grade"], record["entity"], record["score"])                     # 등급 · 대상 · 점수를 출력한다

print("--- 단계 3: AI 에게 보내는 글 (seoyeon)")                                  # 단계 3 시작을 알리는 줄
seoyeon_record = picked[1]                                                        # 두 번째 기록(seoyeon)을 꺼낸다
prompt = build_prompt(seoyeon_record)                                             # seoyeon 에게 보낼 글을 만든다
print(prompt)                                                                     # AI 에게 보내는 글을 출력한다

print("--- 단계 4: Gemini API 를 활용한 AI 요약")                                 # 단계 4 시작을 알리는 줄
for record in picked:                                                             # 고른 기록을 하나씩 꺼낸다
    summary = summarize_record(record)                                            # AI 에게 요약을 시킨다
    print(record["entity"], ":", summary)                                         # 대상과 요약 문장을 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `event_summary.py` · `day06_2-1_run.py` 를 `anomaly_detection` 폴더에 만들어 위 코드를 붙여 넣습니다. 터미널에서는 `touch` 로 만든 뒤 VS Code 에서 엽니다.
   ```bash
   pwd
   touch event_summary.py day06_2-1_run.py
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
2. **[VS Code]** `event_summary.py` 에서 <mark>직접 쓰는 곳 일곱 군데를 씁니다</mark>. 위 문법 상자와 2.1 의 표를 참고해 씁니다. 막히면 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day06_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day06_2-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **네 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없고, 단계 2는 제목 줄에 숫자가 있고 그 아래 3줄(대상마다 등급 · 대상 · 점수), 단계 3은 2줄(지시문 1줄, [사실] 1줄), 단계 4는 대상마다 1줄씩 3줄입니다. <mark>단계 4 의 문장은 사람마다, 실행할 때마다 다릅니다.</mark>
5. **[보고서]** `day06_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 요약한 대상 수와 `(요약 실패 …)` 가 나온 대상 수를 적어 주세요.
   - (나) 🔍 단계 3 의 지시문이 AI 에게 하지 말라고 한 것 두 가지를 찾고, 각각 하면 왜 위험한지 적어 주세요.
   - (다) 🔍 단계 4 의 요약 하나를 골라 2.1 의 점수 기록 표(대상 · 점수 · 등급 · 탐지된 규칙)와 비교해, 표에 없는 내용이 들어 있는지 적어 주세요. 있으면 어떤 문장인지와 지시문을 어떻게 고칠지, 없으면 없다고 쓰고 탐지된 규칙이 모두 문장에 들어갔는지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 조건 두 개가 모두 참 | `if record["grade"] != "low" and len(picked) < SUMMARY_LIMIT:` |
| 리스트에 추가 | `picked.append(record)` |
| 문장들을 한 문자열로 | `meaning_text = "; ".join(meanings)` |
| 변수 값을 문장에 넣기 | `facts = f"… {entity} … {score}점 …"` |
| AI 호출 | `summary = call_llm(prompt)` |
| 실패하면 대체 문장 | `if summary == "":` → `summary = FAIL_TEXT` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 탐지부터 보고서 저장까지 pipeline.py 로 한 번에 실행하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「이번 주에 만든 탐지를 확인하려면 지금은 파일을 하나씩 따로 실행해야 합니다. 순서를 하나 빠뜨리면 점수가 틀리게 나오는데, 틀린 줄도 모르고 보고하게 됩니다.
>
> 명령 한 번으로 읽기부터 점수 저장, 요약, 보고서 저장까지 끝나게 해 주세요. 그리고 AI 가 응답하지 않는 날에도 점수와 등급이 담긴 보고서는 나와야 합니다.」
> - **왜 중요한가**: <mark>단계를 따로 실행하면 순서를 빠뜨리거나 앞 단계의 결과를 잘못 넘길 수 있고, AI 호출 하나가 실패해서 보고서 전체가 만들어지지 않으면 담당자가 아침에 아무것도 볼 수 없습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 파이프라인은 <mark>앞 단계의 리턴값을 다음 단계에 전달해 이어 가는 구조</mark>입니다. 어느 함수에 무엇을 전달하는지가 오늘의 핵심입니다.
2. 오늘 질문은 하나입니다. <mark>**각 단계의 결과를 다음 단계에 어떻게 넘기고, 한 단계가 실패해도 나머지 결과를 어떻게 남기는가?**</mark>

### 📖 3.1 단계 연결 흐름과 이번 주 파일의 자리

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

```
단계 1  이벤트 읽기               normalized_events.json  →  events (표)
   ↓
단계 2  연결 · 탐지 · 점수         events  →  chains  →  findings  →  totals · reasons  →  records
   ↓                              (records 는 day03_risk_scores.json 에도 저장)
단계 3  Gemini API 를 활용한 AI 요약                   records  →  summaries   (실패하면 대체 문장)
   ↓
단계 4  보고서 저장               events · findings · records · summaries
                                  →  anomaly_detection_report_2026-11-02.json
```

이번 주에 만든 파일 가운데 파이프라인에 들어가는 것과 아직 들어가지 않은 것은 다음과 같습니다.

| 만든 날 | 파일 | 파이프라인에서 |
|---|---|---|
| 11/3 | `normalized_events.json` | 단계 1 의 입력 |
| 11/5 오전 | `access_detection.py` · `saas_detection.py` · `malicious_detection.py` | 단계 2 안에서 `collect_findings` 가 호출합니다 |
| 11/5 오후 | `correlation.py` · `risk_scores.py` | 단계 2 |
| 오늘 2교시 | `event_summary.py` | 단계 3 |
| 11/4 | 로그인 · 트래픽 규칙(`login_detection.py` · `traffic_detection.py` · `alerts.py`) | **넣지 않았습니다.** 알림을 `alerts.json` 에 따로 모으는 방식이라 점수 기록과 모양이 다릅니다 |
| 11/6 | 평가 · 튜닝(`evaluation.py` · `tuning.py` · `final_check.py`) | **넣지 않았습니다.** 입력이 사람이 조사한 결과가 붙은 파일(`review_alerts.json`)이라 이벤트 표가 아닙니다 |

- 오늘 파이프라인은 점수 기록 쪽만 이어 붙였습니다. 11/4 의 알림이나 11/6 의 평가를 더하려면 입력과 출력의 모양을 맞추는 단계가 필요하고, 현업에서도 이 단계를 따로 만들어 이어 붙입니다.
- 보고서 파일 `anomaly_detection_report_2026-11-02.json` 에 들어가는 키는 다음과 같습니다. 파일 이름의 날짜 `2026-11-02` 는 샘플 이벤트의 날짜입니다.

| 키 | 값 |
|---|---|
| `date` | 샘플 이벤트의 날짜 |
| `event_count` | 읽은 이벤트 수 |
| `source_event_counts` | 로그 종류(`web` · `server` · `saas`)마다 이벤트 수 |
| `finding_count` | 탐지된 규칙 건수 |
| `records` | 대상별 점수 · 등급 · 이유 기록 |
| `summaries` | 대상별 Gemini API 를 활용한 AI 요약(실패하면 대체 문장) |

- 단계 3 이 실패해도 단계 4 가 이어지도록 <mark>요약 함수는 오류를 내지 않고 `FAIL_TEXT` 를 리턴</mark>합니다. 그래서 점수와 등급은 항상 보고서에 들어갑니다.

**🐼 판다스 문법 상자 — 시리즈를 딕셔너리로 바꾸기 `시리즈.to_dict()`**

**<mark>`시리즈.to_dict()`</mark> 는 시리즈의 이름(인덱스)을 키로, 값을 값으로 하는 딕셔너리를 만듭니다**

보고서는 JSON 파일로 저장하는데, 판다스의 시리즈는 JSON 으로 바로 저장되지 않습니다. 센 결과(`value_counts()`)를 딕셔너리로 바꿔야 합니다. 과일 이름 다섯 개를 센 예로 익힙니다.

```python
import pandas as pd                                       # 판다스를 pd 라는 짧은 이름으로 불러온다

fruits = pd.Series(["사과", "사과", "배", "사과", "귤"])  # 과일 이름 다섯 개로 시리즈를 만든다
fruit_counts = fruits.value_counts()                      # 이름마다 몇 개인지 센다
print(fruit_counts)                                       # 센 결과를 출력한다
```

실행 결과:

```
사과    3
배     1
귤     1
Name: count, dtype: int64
```

위 코드에 이어서 실행하는 다음 코드입니다.

```python
fruit_count_dict = fruit_counts.to_dict()  # 시리즈를 딕셔너리로 바꾼다
print(fruit_count_dict)                    # 딕셔너리를 출력한다
```

실행 결과:

```
{'사과': 3, '배': 1, '귤': 1}
```

- **읽는 법**:
  - <mark style="background:#bde3ff">`사과` · `배` · `귤` 이 키이고 3 · 1 · 1 이 값</mark>인 딕셔너리가 됩니다.
  - 이 딕셔너리는 `json.dump` 로 저장할 수 있습니다.
- **오늘은**:
  - 과일 이름 대신 로그 종류(`web` · `server` · `saas`)마다 센 이벤트 수에 씁니다.
- **주의**:
  - <mark style="background:#ffc4d6">`json.dump` 에 시리즈를 그대로 전달하면 `TypeError` 오류가 납니다.</mark>
  - `.to_dict()` 는 괄호까지 써야 합니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `analyze_events` | 이벤트 표 | 탐지된 규칙 리스트 · 점수 기록 리스트 |
| `summarize_records` | 점수 기록 리스트 | 요약 리스트(미리 채움) |
| `count_failed` | 요약 리스트 | 실패한 요약 수(미리 채움) |
| `build_report` | 이벤트 표 · 탐지된 규칙 · 점수 기록 · 요약 | 보고서 딕셔너리 |
| `save_report` | 보고서 · 파일 경로 | 없음(파일에 저장, 미리 채움) |
| `run_pipeline` | 없음 | 없음(단계마다 결과를 출력, 미리 채움) |

- **직접 쓰는 곳은 일곱 군데**(번호 1 ~ 7)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `analyze_events`(1 ~ 4번): 함수 네 개를 차례로 호출하면서, 앞 함수의 리턴값을 다음 함수에 전달합니다.
  - `build_report`(5 ~ 7번): 로그 종류마다 이벤트 수를 세고(`value_counts`), 딕셔너리로 바꾸고(`to_dict`), 보고서 딕셔너리로 모읍니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 읽기부터 보고서 저장까지 pipeline.py 로 실행하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>탐지를 확인하려면 파일을 따로따로 실행해야 하고, AI 호출이 실패하면 결과를 한 번에 남길 방법이 없습니다</mark>.
- **그래서 만드는 것**: `pipeline.py` 입니다.
  - 이벤트를 읽고 연결 · 탐지 · 점수까지 한 함수에서 이어 실행합니다.
  - 점수 기록을 파일에 저장하고, 대상마다 Gemini API 를 활용한 AI 요약을 받습니다.
  - 모든 결과를 보고서 파일 하나로 저장합니다.
- **실행하면**: <mark>단계 1: 읽은 이벤트 수, 단계 2: 탐지된 규칙과 점수 기록 수, 단계 3: Gemini API 를 활용한 AI 요약, 단계 4: 보고서 저장, 단계 5: 확인할 순서가 나옵니다.</mark>
- **현업에서는**: 파이프라인을 정해진 시각에 자동으로 실행하고 보고서 파일을 담당자에게 보냅니다. 자동 실행은 AI 가 없는 날에도 멈추지 않아야 해서 실패한 단계를 대체 값으로 넘깁니다.

**🎯 할 일**

1. `pipeline.py` · `day06_3-1_run.py` 두 파일을 만들고, `pipeline.py` 의 두 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>읽은 이벤트 수</mark>(단계 1), <mark>탐지된 규칙과 점수 기록 수</mark>(단계 2), <mark>Gemini API 를 활용한 AI 요약</mark>(단계 3), <mark>보고서 저장</mark>(단계 4), <mark>확인할 순서</mark>(단계 5)를 읽고, 새로 생긴 `anomaly_detection_report_2026-11-02.json` 을 VS Code 에서 열어 봅니다.

`summarize_records` · `count_failed` · `save_report` · `run_pipeline` 은 읽기만 하는 미리 채운 함수입니다. 2교시에서 쓴 방식과 같아서 직접 쓰는 곳이 없습니다.

**`pipeline.py`**

```python
import json                                                                                # 보고서를 JSON 파일로 저장하기 위해 json 을 불러온다
from access_detection import load_events, EVENTS_PATH                                      # 11/5 오전 : 이벤트 파일을 읽는 함수를 불러온다
from correlation import find_chains_in_events                                              # 11/5 오후 : 서로 다른 로그를 연결하는 함수를 불러온다
from risk_scores import collect_findings, score_findings, collect_reasons, make_records, save_records, RISK_PATH  # 11/5 오후 : 탐지 · 점수 함수를 불러온다
from event_summary import pick_records_to_summarize, summarize_record, FAIL_TEXT           # 오늘 2교시 : Gemini API 를 활용한 AI 요약 함수를 불러온다

REPORT_DATE = "2026-11-02"                                                                 # 샘플 이벤트의 날짜
REPORT_PATH = "anomaly_detection_report_" + REPORT_DATE + ".json"                          # 보고서를 저장할 파일 이름


def analyze_events(events):                                                                # 이벤트 표를 받는 함수
    """이벤트에서 연결된 사건을 찾고, 탐지된 규칙을 모아 대상별 점수 기록을 만든다.
    11/5 에 하나씩 실행한 단계를 한 함수에서 이어 쓸 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. events 를 find_chains_in_events 에 전달해 연결된 사건을 구해 chains 에 담는다
    # 2. events 와 chains 를 collect_findings 에 전달해 탐지된 규칙 리스트를 구해 findings 에 담는다
    # 3. findings 를 score_findings 에 전달해 대상별 점수를 구해 totals 에 담는다
    # 4. findings 를 collect_reasons 에 전달해 대상별 규칙 이름을 구해 reasons 에 담는다
    records = make_records(totals, reasons)                                                # 점수 · 등급 · 이유 기록을 만든다 — 미리 채운 줄
    return findings, records                                                               # 탐지된 규칙 리스트와 기록을 리턴한다


def summarize_records(records):                                                            # 점수 기록 리스트를 받는 함수
    """요약할 대상을 고르고 대상마다 Gemini API 를 활용한 AI 요약을 받아 리스트로 모은다.
    요약에 실패한 대상은 FAIL_TEXT 가 들어가서 나머지 결과가 그대로 이어지게 할 때 쓴다.
    """
    picked = pick_records_to_summarize(records)                                            # 요약할 대상을 고른다
    summaries = []                                                                         # 요약을 담을 빈 리스트
    for record in picked:                                                                  # 대상을 하나씩 꺼낸다
        summary = summarize_record(record)                                                 # AI 에게 요약을 시킨다
        item = {"entity": record["entity"], "grade": record["grade"], "summary": summary}  # 대상 · 등급 · 요약을 딕셔너리로 만든다
        summaries.append(item)                                                             # 요약 리스트에 추가한다
    return summaries                                                                       # 요약 리스트를 리턴한다


def count_failed(summaries):                                                               # 요약 리스트를 받는 함수
    """요약 가운데 AI 호출이 실패한 것이 몇 개인지 센다.
    실패가 있으면 담당자가 그 대상은 점수와 이유를 직접 읽어야 하므로 알릴 때 쓴다.
    """
    failed = 0                                                                             # 실패한 개수를 0 으로 시작한다
    for item in summaries:                                                                 # 요약을 하나씩 꺼낸다
        if item["summary"] == FAIL_TEXT:                                                   # 실패 문장이면
            failed = failed + 1                                                            # 실패 개수를 1 늘린다
    return failed                                                                          # 실패한 개수를 리턴한다


def build_report(events, findings, records, summaries):                                    # 이벤트 표 · 탐지된 규칙 · 점수 기록 · 요약을 받는 함수
    """분석 결과를 담당자가 읽는 보고서 딕셔너리 하나로 모은다.
    분석 결과를 파일 하나로 전달할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. events 의 "source" 열을 꺼내 .value_counts() 를 붙여 로그 종류마다 이벤트 수를 구해 source_event_counts 에 담는다
    # 6. source_event_counts 에 .to_dict() 를 붙여 JSON 에 저장할 수 있는 딕셔너리로 바꿔 source_count_dict 에 담는다
    # 7. 키 "date" 에 REPORT_DATE, "event_count" 에 len(events), "source_event_counts" 에 source_count_dict, "finding_count" 에 len(findings), "records" 에 records, "summaries" 에 summaries 를 담은 딕셔너리를 report 에 담는다
    return report                                                                          # 보고서 딕셔너리를 리턴한다


def save_report(report, path):                                                             # 보고서 딕셔너리와 파일 경로를 받는 함수
    """보고서를 JSON 파일로 저장한다.
    담당자와 다른 프로그램이 같은 파일을 읽게 할 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                                        # path 파일을 쓰기 모드로 연다
        json.dump(report, file, ensure_ascii=False, indent=2)                              # 한글은 그대로, 줄을 나눠 저장한다


def run_pipeline():                                                                        # 인자가 없는 함수
    """읽기 → 분석 → 점수 저장 → Gemini API 를 활용한 AI 요약 → 보고서 저장을 차례로 실행하고 단계마다 결과를 출력한다.
    탐지부터 보고서까지 한 번에 돌릴 때 쓴다.
    """
    events = load_events(EVENTS_PATH)                                                      # 이벤트 파일을 표로 읽는다
    print("--- 단계 1: 읽은 이벤트", len(events), "개")                                    # 단계 1 : 읽은 이벤트 수

    findings, records = analyze_events(events)                                             # 연결 · 탐지 · 점수를 한 번에 실행한다
    saved_count = save_records(records, RISK_PATH)                                         # 점수 기록을 파일에 저장한다
    print("--- 단계 2: 탐지된 규칙", len(findings), "건 → 점수 기록", saved_count, "건을", RISK_PATH, "에 저장")  # 단계 2 : 탐지 · 점수

    summaries = summarize_records(records)                                                 # 대상마다 Gemini API 를 활용한 AI 요약을 받는다
    failed_count = count_failed(summaries)                                                 # 요약에 실패한 것이 몇 개인지 센다
    print("--- 단계 3: Gemini API 를 활용한 AI 요약", len(summaries), "건 (실패", failed_count, "건)")  # 단계 3 : Gemini API 를 활용한 AI 요약
    for item in summaries:                                                                 # 요약을 하나씩 꺼낸다
        print(item["entity"], ":", item["summary"])                                        # 대상과 요약 문장을 출력한다

    report = build_report(events, findings, records, summaries)                            # 보고서 딕셔너리를 만든다
    save_report(report, REPORT_PATH)                                                       # 보고서를 파일에 저장한다
    print("--- 단계 4: 보고서를", REPORT_PATH, "에 저장")                                  # 단계 4 : 보고서 저장

    print("--- 단계 5: 확인할 순서")                                                       # 단계 5 : 담당자가 볼 순서
    for record in records:                                                                 # 점수 기록을 하나씩 꺼낸다
        print(record["grade"], record["entity"], record["score"])                          # 등급 · 대상 · 점수를 출력한다
```

- 들여쓰기는 **미리 채운 줄에 맞춥니다.** 1 ~ 7번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. **주석은 지우지 않습니다.** 7번의 딕셔너리는 한 줄이 길어서 중괄호 안에서 줄을 나눠도 됩니다.
- 함수에 전달하는 순서는 주석에 적힌 순서입니다. <mark>2번은 `events` 다음에 `chains` 입니다.</mark>
- 채우기 전에 실행하면 `NameError: name 'totals' is not defined` 오류가 납니다. `totals` 를 만드는 3번을 아직 안 썼기 때문입니다.

**`day06_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다.

```python
from pipeline import run_pipeline  # 방금 만든 파이프라인 함수를 불러온다

run_pipeline()                     # 읽기부터 보고서 저장까지 한 번에 실행한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `pipeline.py` · `day06_3-1_run.py` 를 `anomaly_detection` 폴더에 만들어 위 코드를 붙여 넣습니다.
   ```bash
   pwd
   touch pipeline.py day06_3-1_run.py
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `touch 파일이름` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
2. **[VS Code]** `pipeline.py` 에서 <mark>직접 쓰는 곳 일곱 군데를 씁니다</mark>. 위 판다스 문법 상자와 3.1 의 그림을 참고해 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 의 결과가 `anomaly_detection` 으로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`). Gemini API 를 3번 호출합니다.
   ```bash
   pwd
   python day06_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day06_3-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 **다섯 단계**입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1과 2와 4는 숫자나 파일 이름이 제목 줄에 함께 나와 그 아래 줄이 없고, 단계 3은 제목 아래 3줄(대상마다 요약), 단계 5는 5줄(대상마다 등급 · 대상 · 점수)입니다. <mark>AI 호출이 실패하면 `[LLM 호출 실패]` 줄이 단계 3 제목 줄 위에 나옵니다.</mark>
5. **[VS Code]** 새로 생긴 `anomaly_detection_report_2026-11-02.json` 을 열어 `event_count` · `records` · `summaries` 를 확인합니다.
6. **[보고서]** `day06_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 보고서 파일의 `event_count` · `finding_count` 값과 `records` · `summaries` 의 건수를 적어 주세요.
   - (나) 🔍 점수와 등급은 코드가 정하고 AI 에게는 요약만 시킨 이유를 적어 주세요. 단계 5 의 확인할 순서와 단계 3 의 요약을 근거로 쓰세요.
   - (다) 🔍 AI 호출이 실패해도 파이프라인이 멈추지 않고 대체 문장을 쓰게 만든 이유를 적어 주세요. 대체 문장이 들어간 대상을 담당자가 어떻게 처리해야 하는지도 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 앞 결과를 다음 함수에 전달 | `findings = collect_findings(events, chains)` |
| 점수 합계 | `totals = score_findings(findings)` |
| 로그 종류마다 개수 | `source_event_counts = events["source"].value_counts()` |
| 시리즈를 딕셔너리로 | `source_count_dict = source_event_counts.to_dict()` |
| 보고서 딕셔너리 | `report = {"date": REPORT_DATE, … "summaries": summaries}` |

### 📁 4과목 폴더 구조 한눈에 보기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

4과목이 끝나면 `anomaly_detection` 폴더에 날짜별로 아래 파일이 있어야 합니다파일을 어디에 저장했는지 헷갈리면 내 VS Code 왼쪽 목록과 비교합니다.

- **`config/` 안에는 JSON 설정 파일만** 둡니다. 11/5 오전에 만든 `users.json` · `roles.json` 입니다.
- **그 밖의 파일은 모두 `anomaly_detection/` 바로 아래**에 둡니다. 코드(`.py`), 실행 파일(`day0N_…_run.py`), 데이터, 안내와 보고서(`.md`), 컴포즈 파일이 해당합니다. `logs/` 는 11/6 오후에 컴포즈로 만든 접속 기록 폴더입니다.
- 터미널은 항상 `…/anomaly_detection` 에서 실행합니다(`pwd` 로 확인).

```
security-agent-toolkit/
  .env
  .gitignore
  agent_core/                       1과목
  network_zt/                       2과목
  access_control/                   3과목
  anomaly_detection/                4과목   ← 여기서 작업
    config/                         ← JSON 설정만
      roles.json
      users.json
    logs/                           ← 11/6 오후에 컴포즈가 남긴 접속 기록
      access.log
      error.log
      web_404.log
    __pycache__/                    ← 파이썬이 자동으로 만듦
    ── 11/2 ──
    access_sample.log
    log_parse.py
    log_classify.py
    day01_5-1_run.py
    day01_6-1_run.py
    ── 11/3 ──
    server_log.jsonl
    saas_events.csv
    normalize_web.py
    normalize_json_csv.py
    normalize.py
    normalized_events.json
    events_basic.py
    events_time.py
    day02_2-1_run.py  ~  day02_6-1_run.py
    ── 11/4 ──
    baseline_logins.csv
    baseline_traffic.csv
    baseline.py
    login_detection.py
    classify.py
    traffic_detection.py
    alerts.py
    alerts.json
    day03_2-1_run.py  ~  day03_6-1_run.py
    ── 11/5 ──
    rbac.py
    access_detection.py
    saas_detection.py
    malicious_detection.py
    advanced_detection.py
    correlation.py
    risk_scores.py
    day03_risk_scores.json
    day04_2-1_run.py  ~  day04_6-1_run.py
    ── 11/6 ──
    review_alerts.json
    problems.json
    login_alerts.json
    evaluation.py
    tuning.py
    final_check.py
    day05_2-1_run.py  ~  day05_4-1_run.py
    compose.yaml
    compose.secure.yaml
    ── 11/9 (오늘) ──
    llm_client.py
    event_summary.py
    pipeline.py
    day06_2-1_run.py
    day06_3-1_run.py
    anomaly_detection_report_2026-11-02.json
    ── 날마다 받은 안내와 보고서 ──
    day01_pm_*.md  day02_am_*.md  day02_pm_*.md  day03_am_*.md  day03_pm_*.md
    day04_am_*.md  day04_pm_*.md  day05_am_*.md  day05_pm_*.md  day06_am_*.md
```

- `__pycache__/` 는 파이썬이 자동으로 만드는 임시 폴더라서 신경 쓰지 않고 깃허브에도 올리지 않습니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 4과목 총정리: 상황마다 원인과 고치는 방법 정리하기</mark>

> 📌 **이번 교시는 새로 배우는 것이 없습니다.** 4과목에서 만든 파일과 함수를 **상황별로 되짚으면서**, 각 상황의 원인과 고치는 방법을 내 말로 정리합니다. 정리한 글이 4과목의 총정리가 되고, 보고서의 4교시 칸에 씁니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. 코드는 4과목에서 만든 파일에서 가져온 것이라, 앞 수업 파일이 없어도 읽을 수 있습니다.

### 📖 상황을 풀 때 쓰는 틀

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

상황이 생기면 같은 네 단계로 생각합니다.

- **확인**: 로그나 평가 결과로 무슨 일인지 알아봅니다.
- **원인**: 왜 이런 일이 생겼는지 가립니다. 원인은 보통 셋 중 하나입니다.
  - 데이터 문제: 파일에 있어야 할 것이 없거나, 빠졌거나, 깨져 있습니다. 예를 들어 읽지 못한 로그 줄, 사용자 이름이 없는 로그, 합치지 않은 알림 파일이 있습니다.
  - 규칙 문제: 「무엇을 의심할지」 정해 둔 기준이 비어 있거나 현실과 맞지 않습니다(너무 느슨하거나 너무 엄격합니다). 이 수업에서 기준을 적어 둔 곳은 `SUSPICIOUS_STATUS`(의심으로 보는 상태 코드), `REPEAT_LIMIT`(서버 거절을 몇 번부터 확인할지), `WINDOW_MINUTES`(몇 분 안의 이벤트를 한 사건으로 볼지), `WEIGHTS`(규칙마다 점수), `TRUSTED_IPS`(예외로 믿는 IP)입니다.
  - 운영 설정 문제: 서버를 켜고 접속을 허용하는 설정(`compose.yaml`)이 목적과 맞지 않습니다.
- **고치기**: 어느 파일을 열어서 어떻게 고칠지 정합니다. 방법은 셋 중 하나입니다.

| 방법 | 뜻 | 4과목에서 한 예 |
|---|---|---|
| 새로 넣는다(추가) | 없던 것을 파일에 적어 넣음 | `TRUSTED_IPS` 리스트에 `203.0.113.80` 을 넣음. `pd.concat` 으로 로그인 알림을 알림 표에 합침 |
| 값을 바꾼다(수정) | 있는 값이나 조건을 다른 것으로 고침 | 포트 `"8081:80"` 을 `"127.0.0.1:8081:80"` 으로 바꿈 |
| 지운다(삭제) | 있던 것을 뺌 | 믿는 IP 에서 온 `SaaS 평소와 다른 IP` 알림을 알림 표에서 뺌 |

- **다시 확인**: 고친 뒤에 무엇을 다시 실행하거나 어떤 출력을 보면 고쳐진 것을 알 수 있는지 정합니다.
- 알림에는 두 가지 틀린 모양이 있습니다. <mark>**오탐**은 문제가 아닌데 난 알림, **미탐**은 진짜 문제인데 나지 않은 알림</mark>입니다. 상황마다 둘 중 어느 쪽인지도 함께 생각합니다.

### 📖 4.1 상황 8개와 읽을 핵심 코드

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

> 4교시는 코드를 실행하지 않고 읽고 글로 씁니다. 표의 파일은 4과목에서 만든 것이고, 상황의 값은 11/2 의 샘플 데이터에서 가져온 것입니다. 앞 수업 파일이 없으면 문서의 코드 조각만 읽고 답합니다.

| # | 상황 (이렇게 알게 됐습니다) | 읽을 핵심 코드 |
|---|---|---|
| 1 | 198.51.100.90 이 `/.env` · `/wp-login.php` · `/phpmyadmin` 을 1초 간격으로 요청했는데, 분류 결과가 세 줄 모두 「오류」이고 「의심」 목록에는 없다 | `log_classify.py` 의 `is_suspicious` · `is_error` |
| 2 | 웹 서버 로그 파일은 30줄인데 `normalized_events.json` 의 웹 서버 이벤트(`source` 가 `web`)는 28개이다. 담당자가 「로그 2줄이 사라졌다」고 보고했다 | `normalize_web` 의 깨진 줄 검사 |
| 3 | 웹 서버 로그의 실패 요청 13개 중 어느 사용자의 요청인지 알 수 있는 것은 1개뿐이다. 203.0.113.50 의 로그인 실패 5번은 누구의 일인지 모른다 | `correlation.py` 의 `make_ip_user_map` · `attach_user_to_web` |
| 4 | seoyeon 은 SaaS 로그와 서버 로그에 모두 나오는데 연결된 사건에 없고, gaeun 은 연결됐다 | `correlation.py` 의 `find_chains` |
| 5 | 알림 7개 중 4개가 오탐인데, 그중 2개는 협력사 사무실 IP 203.0.113.80 에서 온 접속이다 **(본보기)** | `tuning.py` 의 `apply_exception` |
| 6 | 로그인 5번 실패 뒤 성공한 203.0.113.50 의 일(P4)이 평가에서 놓친 문제로 나온다. 로그인 규칙은 알림을 이미 냈다 **(본보기)** | `final_check.py` 의 `merge_alerts`, `login_alerts.json` |
| 7 | seoyeon 이 권한 없는 정산 조회를 시도했는데(P5) 알림이 나지 않는다 | `access_detection.py` 의 `pick_suspicious`, `REPEAT_LIMIT` |
| 8 | 컴포즈로 켠 `web2` 에 같은 사무실 네트워크의 다른 PC 에서도 접속할 수 있다. 서버를 지우면 서버 안의 접속 기록도 사라진다 | `compose.yaml` · `compose.secure.yaml` 의 `ports` · `volumes` |

- 파일들은 서로의 함수를 호출합니다. 상황 3 · 4는 같은 이벤트 표에서 이어지고, 상황 5 · 6 · 7은 평가 결과에서 이어집니다.
  - 상황 3 → 4: 웹 로그의 요청에 사용자를 붙이는 `attach_user_to_web` 의 결과가 `build_timeline` 을 거쳐 `find_chains` 로 들어갑니다.
  - 상황 5 → 6 → 7: 알림을 센 결과(오탐 · 미탐)가 예외 규칙(`apply_exception`), 알림 합치기(`merge_alerts`), 새 규칙이 필요한 미탐으로 이어집니다.

아래는 상황마다 관련된 코드입니다. 각 코드 앞의 문장은 **이 코드를 왜 읽는지**를 알려 줍니다. 답을 알려 주는 것은 아니고, 코드에서 어디를 볼지만 짚어 줍니다. 읽고 나서 보고서의 4교시 상황 정리를 쓸 때 참고합니다.

#### 상황 1 · 설정 파일 주소를 연달아 요청했는데 「의심」이 아니라 「오류」로 분류됨

요청 하나를 「의심」으로 보는 조건이 무엇인지 읽습니다. 아래 세 줄은 11/2 에 분류한 결과 가운데 「오류」로 나온 요청입니다.

```
198.51.100.90 GET /.env 404
198.51.100.90 GET /wp-login.php 404
198.51.100.90 GET /phpmyadmin 404
```

`log_classify.py` 의 `is_suspicious` 와 `is_error` 입니다. 의심 조건이 상태 코드와 `/admin` 만 보는지 읽습니다.

```python
SUSPICIOUS_STATUS = (401, 403)                         # 의심으로 보는 상태 코드(로그인 실패 · 접근 거부)


def is_suspicious(entry):                              # 읽은 요청 딕셔너리를 받는 함수
    bad_status = entry["status"] in SUSPICIOUS_STATUS  # 상태 코드가 401 이나 403 인지
    admin_path = "/admin" in entry["path"]             # 경로에 /admin 이 들어 있는지
    return bad_status or admin_path                    # 둘 중 하나라도 참이면 True 를 리턴한다


def is_error(entry):                                   # 읽은 요청 딕셔너리를 받는 함수
    return entry["status"] >= 400                      # 400 이상이면 True 를 리턴한다
```

#### 상황 2 · 로그 30줄이 이벤트 28개가 됨

줄 수를 비교한 표입니다. 같은 샘플 로그를 정규화하기 전과 후의 숫자입니다.

| 단계 | 개수 |
|---|---|
| 정규화 전: 웹 서버 로그 파일의 줄 | 30 |
| 정규화 후: `source` 가 `web` 인 이벤트 | 28 |

`normalize_web` 의 앞부분입니다. 줄을 읽기 전에 무엇을 검사하는지 읽습니다.

```python
def normalize_web(line):  # 로그 한 줄을 받는 함수
    if line.count('"') < 2:                                  # 큰따옴표가 두 개보다 적은 깨진 줄이면
        return None       # 읽지 않고 None 을 리턴한다
```

#### 상황 3 · 웹 서버 로그에서 사용자를 알 수 있는 요청이 1개뿐

웹 서버 로그의 이벤트 한 개입니다. `user` 값이 어떤지 읽습니다.

```
{'time': '2026-11-02 09:12:09', 'source': 'web', 'user': None, 'ip': '203.0.113.50', 'action': 'POST /login', 'result': '실패'}
```

`correlation.py` 의 `make_ip_user_map` 입니다. 사용자를 어디에서 알아내는지 읽습니다.

```python
def make_ip_user_map(logins):                     # SaaS 로그인 표를 받는 함수
    ip_user = {}                                  # IP → 사용자 딕셔너리
    login_list = logins.to_dict("records")        # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                      # 로그인을 하나씩 꺼낸다
        if login["result"] == "성공":             # 성공한 로그인이면
            ip_user[login["ip"]] = login["user"]  # 그 IP 의 사용자를 딕셔너리에 담는다
    return ip_user                                # IP → 사용자 딕셔너리를 리턴한다
```

11/5 에 이 함수로 만든 딕셔너리에는 IP 가 다섯 개 있었고, 203.0.113.50 은 그 안에 없었습니다.

#### 상황 4 · 두 로그에 나오는 seoyeon 이 연결되지 않음

`find_chains` 의 두 조건입니다. 「처음부터 마지막까지」가 어느 범위인지 읽습니다.

```python
MIN_SOURCES = 2                            # 서로 다른 로그 종류가 이 개수 이상이어야 연결한다
WINDOW_MINUTES = 60                        # 한 사용자의 이벤트가 이 분 안에 모여 있어야 연결한다

# find_chains 안에서 사용자마다
latest = grouped["minute_of_day"].max()    # 그 사용자의 가장 늦은 시각(분)
earliest = grouped["minute_of_day"].min()  # 그 사용자의 가장 이른 시각(분)
spans = latest - earliest                  # 처음부터 마지막까지 몇 분인지
is_close = span <= WINDOW_MINUTES          # 시간 간격이 기준 이내인지
```

seoyeon 의 이벤트를 시각순으로 놓은 표입니다. 11/5 에 단계 4 로 나온 결과는 `{'user': 'seoyeon', 'source_count': 2, 'span_minutes': 555}` 이고, gaeun 은 `서로 다른 로그 3종류 · 41분 안` 으로 연결됐습니다.

| 시각 | 로그 | 행동 | 결과 |
|---|---|---|---|
| 09:05:30 | saas | login | 성공 |
| 11:25:40 | saas | file.download | 성공 |
| 11:40:00 | server | SETTLE:QUERY | 실패 |
| 17:38:10 | saas | login | 성공 |
| 17:40:02 ~ 17:42:20 | saas | file.download 5번 | 성공 |
| 18:20:00 | server | SALES:CHANGE | 실패 |

#### 상황 5 · 협력사 사무실에서 접속한 정상 접속에 알림이 남 (본보기)

11/6 오전의 알림 가운데 `SaaS 평소와 다른 IP` 규칙에서 난 세 건입니다. 조사 메모를 읽습니다.

| id | 규칙 | 대상 | IP | 진짜 문제? | 조사 메모 |
|---|---|---|---|---|---|
| A4 | SaaS 평소와 다른 IP | jiwoo | 203.0.113.80 | 아니오 | 출장 중 협력사 사무실에서 접속함 |
| A5 | SaaS 평소와 다른 IP | seoyeon | 203.0.113.80 | 아니오 | 외근 중 협력사 사무실에서 접속함 |
| A6 | SaaS 대량 다운로드 | seoyeon | 203.0.113.80 | 예 | 업무와 상관없는 파일 6개를 한꺼번에 내려받음 |

`tuning.py` 의 `apply_exception` 입니다. 어떤 조건의 알림만 빼는지 읽습니다.

```python
IP_RULE = "SaaS 평소와 다른 IP"                  # 예외를 적용할 규칙 이름
TRUSTED_IPS = ["203.0.113.80"]                   # 믿는 IP 리스트 : 협력사 사무실 IP 한 개


def apply_exception(alerts):                     # 알림 표를 받는 함수
    is_ip_rule = alerts["rule"] == IP_RULE       # 규칙이 IP 규칙인지
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)  # IP 가 믿는 IP 안에 있는지
    is_removed = is_ip_rule & is_trusted         # 둘 다 참인 행을 뺄 알림으로 본다
    removed_alerts = alerts[is_removed]          # 빼낼 알림
    is_kept = ~is_removed                        # 빼지 않을 알림
    kept_alerts = alerts[is_kept]                # 남은 알림
    return removed_alerts, kept_alerts           # 빼낸 알림과 남은 알림을 리턴한다
```

#### 상황 6 · 로그인 규칙이 낸 알림이 평가에서 빠짐 (본보기)

11/6 오전 2교시의 마지막 단계입니다. 알림 7개로 센 결과입니다.

```
--- 단계 4: 미탐 (알림이 나지 않은 진짜 문제) ---
미탐 수: 2
놓친 문제: P4 203.0.113.50 로그인 5번 실패 뒤 성공하고 관리자 화면을 요청함
놓친 문제: P5 seoyeon 권한 없는 정산 조회를 시도함
```

로그인 규칙(`LOGIN_LIMIT = 5`)이 만든 알림 `login_alerts.json` 입니다. 이 알림이 어느 문제를 가리키는지 읽습니다.

```
[
  {"id": "A8", "rule": "웹 로그인 반복 실패", "user": null, "ip": "203.0.113.50", "real": true, "problem": "P4", "memo": "로그인 5번 실패 뒤 성공, 이어서 관리자 화면을 요청함"}
]
```

`final_check.py` 의 `merge_alerts` 입니다. 두 알림 표를 어떻게 다루는지 읽습니다.

```python
def merge_alerts(alerts, login_alerts):             # 알림 표 두 개를 받는 함수
    all_alerts = pd.concat([alerts, login_alerts])  # 두 알림 표를 위아래로 이어 붙인다
    return all_alerts                               # 합친 알림 표를 리턴한다
```

#### 상황 7 · 정산 조회 시도에는 알림이 나지 않음

`access_detection.py` 의 `pick_suspicious` 입니다. 서버 거절이 몇 번이어야 먼저 확인할 대상이 되는지 읽습니다.

```python
REPEAT_LIMIT = 3                           # 한 사용자의 실패가 이 횟수 이상이면 먼저 확인한다


def pick_suspicious(server_failures):      # 서버 실패 표를 받는 함수
    users = server_failures["user"]        # user 열만 꺼낸다
    user_counts = users.value_counts()     # 사용자마다 실패가 몇 번인지 센다
    is_many = user_counts >= REPEAT_LIMIT  # 실패 횟수가 REPEAT_LIMIT 이상인지 비교한다
```

서버 로그에서 seoyeon 의 요청 가운데 실패한 두 건입니다. 진짜 문제 P5 는 `권한 없는 정산 조회를 시도함` 입니다.

| 시각 | 행동 | 결과 |
|---|---|---|
| 11:40:00 | SETTLE:QUERY | 실패 |
| 18:20:00 | SALES:CHANGE | 실패 |

#### 상황 8 · 서버가 같은 네트워크에 열려 있고, 지우면 접속 기록도 사라짐

5교시 `compose.yaml` 로 켠 `web2` 의 상태입니다. PORTS 에 `0.0.0.0` 이 보입니다.

```
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2   Up   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
```

`compose.secure.yaml` 의 `web2` 와 `web3` 입니다. 접속 범위를 정하는 `ports` 와 기록을 내 폴더에 연결하는 `volumes` 를 읽습니다. 5교시 `compose.yaml` 의 `web2` 는 `"8081:80"` 으로 적혀 있었습니다.

```yaml
  web2:                          # 관리용 서버
    image: nginx:1.28            # 같은 nginx 웹 서버
    ports:                       # 접속 범위를 정하는 곳
      - "127.0.0.1:8081:80"      # 맨 앞의 127.0.0.1 은 「내 PC 에서만」이라는 뜻이다
  web3:                          # 로그 서버
    image: nginx:1.28            # 같은 nginx 웹 서버
    ports:                       # 접속 범위를 정하는 곳
      - "127.0.0.1:8082:80"      # web2 와 같이 내 PC 에서만 접속한다
    volumes:                     # 내 폴더와 서버 안 폴더를 연결하는 곳
      - ./logs:/var/log/nginx    # 서버가 로그를 쓰는 폴더를 내 logs 폴더에 연결한다
```

11/6 에 `logs/access.log` 에 남은 한 줄의 모양입니다. 금요일에 이 폴더를 만들었다면 `cat logs/access.log` 로 내 파일의 줄과 비교해 읽습니다.

```
172.18.0.1 - - [06/Nov/2026:03:37:43 +0000] "GET /.env HTTP/1.1" 404 153 "-" "curl/8.7.1" "-"
```

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 상황 8개의 원인과 고치는 방법을 내 말로 정리하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 4과목에서 파일과 함수를 하나씩 만들었지만, 상황이 생겼을 때 「무엇이 문제이고 어디를 어떻게 고치는지」를 한 번에 말하기는 어렵습니다.
- **그래서 하는 것**: 상황 8개마다 원인, 고칠 파일, 어떻게 고치는지, 고친 뒤 확인, 담당자가 가장 먼저 할 일을 내 말로 정리합니다.
  - 상황 5 · 6 은 본보기가 있습니다. 먼저 읽고, 나머지 여섯 개(1 · 2 · 3 · 4 · 7 · 8) 중에서 내가 약하다고 느끼는 것부터 **4개 이상** 씁니다. 다 쓰고 싶으면 다 써도 됩니다.
  - 분량은 정하지 않습니다. 짧게 써도 되고, 더 공부하고 싶으면 깊게 써도 됩니다.
- **끝나면**: 보고서의 4교시 상황 정리가 4과목 총정리가 됩니다.
- **현업에서는**: 인수인계 문서는 「이런 일이 생기면 여기를 이렇게 고친다」를 상황별로 적어 둡니다. 마지막 칸에 적은 「담당자가 가장 먼저 할 일」은 오후 5과목에서 자동 대응을 만들 때 대응 목록의 출발점이 됩니다.

**🎯 할 일**

1. 보고서 `day06_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래 「상황 정리」 틀을 엽니다. 상황 5 · 6 은 본보기라 이미 적혀 있습니다.
2. 상황 1 · 2 · 3 · 4 · 7 · 8 중 4개 이상을 골라 `-` 뒤를 채웁니다. 4과목에서 만든 내 파일을 열어 보면서 써도 됩니다.

- 칸마다 무엇을 쓰는지
  - **원인**: 데이터 문제인지, 규칙 문제인지, 운영 설정 문제인지 고르고 이유를 씁니다.
  - **고칠 파일**: 어느 파일을 열어서 고치는지 씁니다.
  - **어떻게 고치나요**: 새로 넣는지, 값을 바꾸는지, 지우는지 고르고, 정확히 무엇을 넣거나 바꾸거나 지우는지 씁니다.
  - **고친 뒤 확인**: 무엇을 다시 실행하거나 어떤 출력을 보면 고쳐진 것을 알 수 있는지 씁니다.
  - **담당자가 가장 먼저 할 일(선택)**: 이 상황의 알림이 났을 때 사람이 가장 먼저 확인하거나 하는 일 한 가지를 씁니다.
- 상황 하나에서 답이 여러 개일 수 있습니다(예: 상황 8은 접속 범위와 접속 기록 두 가지입니다). 떠오르는 대로 모두 씁니다. 같은 칸에 케이스 A · B 를 쓸 때는 줄을 나눠 「케이스 A: …」 처럼 적습니다.

**순서**

1. **[VS Code]** 보고서 `day06_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래 「상황 정리」 를 엽니다. 본보기(상황 5 · 6)를 먼저 읽습니다.
2. **[VS Code]** 4.1 의 상황 표와 코드를 보면서 상황 1 · 2 · 3 · 4 · 7 · 8 중 4개 이상의 `-` 뒤를 채웁니다. 막히면 4과목에서 만든 내 파일을 열어서 읽습니다.
3. **[보고서]** 같은 `### 문제 4-1` 아래의 질문을 채웁니다.
   - (가) 내가 쓴 상황 번호를 적어 주세요. 쓰지 못한 상황이 있으면 막힌 곳도 적어 주세요.
   - (나) 🔍 상황 8개를 「데이터 문제」 · 「규칙 문제」 · 「운영 설정 문제」로 나누면 각각 어떤 상황인가요? 어느 쪽에서 실수하면 더 위험한지 이유와 함께 적어 주세요.
   - (다) 🔍 4과목에서 가장 헷갈렸던 로직 하나와, 어떻게 이해했는지 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 상황이 생기면 | 확인 → 원인 → 고치기(추가 · 수정 · 삭제) → 다시 확인 |
| 원인 | 데이터 문제 · 규칙 문제 · 운영 설정 문제 |
| 틀린 알림 | 오탐(문제가 아닌데 난 알림) · 미탐(진짜 문제인데 나지 않은 알림) |
| 데이터를 고치는 곳 | 로그 줄 · `normalized_events.json` · 알림 파일(`review_alerts.json` · `login_alerts.json`) |
| 규칙을 고치는 곳 | `SUSPICIOUS_STATUS` · `REPEAT_LIMIT` · `WINDOW_MINUTES` · `WEIGHTS` · `TRUSTED_IPS` |
| 운영 설정을 고치는 곳 | `compose.yaml` 의 `ports` · `volumes` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 4과목 작업을 저장소에 올리는 마무리입니다.</mark> 4교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, `pwd` 로 위치를 먼저 확인한 뒤 결과가 `anomaly_detection` 으로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「4과목에서 만든 파일과 보고서 파일을 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `anomaly_detection` 폴더에 오늘 만든 `event_summary.py` · `pipeline.py` · `anomaly_detection_report_2026-11-02.json` 이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `anomaly_detection` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day06_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤와 코드 상자가 비어 있는 질문이 없는지도 봅니다(마무리 (가)는 3번에서 채웁니다).

   ① 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark>`anomaly_detection` 으로 끝나야</mark> 합니다.

   ② 폴더 안의 파일을 봅니다.

   ```bash
   ls
   ```

   - 하는 일: 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: `event_summary.py` · `pipeline.py` · `anomaly_detection_report_2026-11-02.json` 이 보이면 됩니다.

1. **[터미널]** `security-agent-toolkit` 폴더로 옮깁니다. 0번의 `pwd` 결과가 `anomaly_detection` 으로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.

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

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark>빨간 글씨 줄에 `.env` 나 `.venv` 가 보이면 올리지 말고,</mark> 아래 안내대로 `.gitignore` 를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `anomaly_detection/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.
   - `anomaly_detection/llm_client.py` 는 API 키가 들어 있지 않은 코드 파일이라 올라가도 됩니다. 키는 `.env` 에만 있습니다.

3. **[보고서]** `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 담습니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 올릴 대상에 담습니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add Gemini API summary and pipeline for anomaly detection"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark>`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다.
   - `git pull` 뒤에 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다.

5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `anomaly_detection` 폴더를 열고, VS Code 왼쪽 목록의 `anomaly_detection` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
   - 빠진 이름이 있으면 VS Code 왼쪽 목록의 `anomaly_detection` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `anomaly_detection` 안으로 옮기고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `anomaly_detection` 폴더와 파일이 있는지 확인 |

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 점수 파일의 사실만 AI 에게 보내 대상 3명의 요약을 받고, 실패하면 대체 문장을 쓰게 했다 | 오전 2-1 |
| 이벤트 읽기부터 연결 · 탐지 · 점수 · Gemini API 를 활용한 AI 요약 · 보고서 저장까지 `pipeline.py` 한 번으로 실행했다 | 오전 3-1 |
| 상황 8개의 원인과 고치는 방법을 내 말로 정리해 보고서에 4과목 총정리를 썼다 | 오전 4-1 |
| 4과목 작업과 보고서를 깃허브에 올렸다 | 마무리 |

오후에는 5과목(자동 대응)을 시작합니다. <mark>오늘 만든 점수 기록에서 등급이 `high` 인 대상을 만났을 때 사람이 하던 일을 프로그램이 대신하는 것이 5과목의 출발점</mark>입니다. 보고서 4교시 상황 정리의 마지막 칸(담당자가 가장 먼저 할 일)이 그때 참고 자료가 됩니다. 오후 첫 교시에 새 폴더 `soar_response` 를 만듭니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 네 함수입니다.

① `pick_records_to_summarize` 안

```python
        if record["grade"] != "low" and len(picked) < SUMMARY_LIMIT:  # low 가 아니고 아직 3명이 안 찼으면
            picked.append(record)                                     # 고른 목록에 추가한다
```

② `describe_reasons` 안

```python
    meaning_text = "; ".join(meanings)  # 사실 문장들을 "; " 로 이어 붙여 문자열 하나로 만든다
```

③ `build_prompt` 안

```python
    facts = f"[사실] 대상: {entity} / 등급: {grade} / 점수: {score}점 / 탐지된 내용: {meaning_text}"  # 점수 파일의 값을 [사실] 한 줄에 넣는다
```

④ `summarize_record` 안

```python
    summary = call_llm(prompt)  # AI 에게 보낼 글을 전달해 요약을 받는다
    if summary == "":           # 요약이 빈 문자열이면(호출이 실패했으면)
        summary = FAIL_TEXT     # 대체 문장을 쓴다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 점수 기록은 <mark style="background:#bde3ff">**5건**</mark>, 요약할 대상은 <mark style="background:#bde3ff">**3명**</mark>(dami · seoyeon · gaeun)입니다. 단계 4 의 문장은 AI 가 쓴 한 예이고 사람마다 다릅니다. `(요약 실패 …)` 가 나온 대상은 0명입니다.

```
--- 단계 1: 불러온 점수 기록 5 건
--- 단계 2: 요약할 대상 3 명 (최대 3 명)
high dami 60
mid seoyeon 45
mid gaeun 40
--- 단계 3: AI 에게 보내는 글 (seoyeon)
당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. [사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 먼저 확인할 것을 한 가지 제안하세요.
[사실] 대상: seoyeon / 등급: mid / 점수: 45점 / 탐지된 내용: 평소와 다른 IP 에서 SaaS 에 접속함; SaaS 에서 파일을 한꺼번에 많이 내려받음
--- 단계 4: Gemini API 를 활용한 AI 요약
dami : 퇴사한 사람의 계정으로 서버에 요청한 기록이 있습니다. 먼저 이 계정이 비활성화되어 있는지 확인하세요.
seoyeon : 평소와 다른 IP 에서 접속하고 파일을 한꺼번에 많이 내려받은 기록이 있습니다. 먼저 내려받은 파일 목록을 확인하세요.
gaeun : 규칙으로는 허용되는 요청을 서버가 거절했고, 서로 다른 로그에서 짧은 시간 안에 이벤트가 확인되었습니다. 먼저 거절된 요청의 서버 설정을 확인하세요.
```

- (나) 지시문이 하지 말라고 한 것은 <mark style="background:#bde3ff">**[사실]에 없는 내용을 지어내는 것**</mark>과 <mark style="background:#bde3ff">**공격이라고 단정하는 것**</mark> 두 가지입니다.
  - 지어내는 것이 위험한 이유: 점수 파일에 없는 사고를 AI 가 쓰면 담당자가 없는 일을 조사하게 되고, 실제로 확인할 대상은 뒤로 밀립니다.
  - 단정하는 것이 위험한 이유: 점수와 등급은 먼저 확인할 순서를 뜻할 뿐 공격이라는 판정이 아닙니다. 예를 들어 dami 는 `퇴사한 계정` 한 가지로 high 이지만, 파일에는 어떤 사고가 있었다는 내용이 없습니다. 「공격이 있었다」고 쓰면 파일에 없는 판단을 사실처럼 말하는 것입니다.
- (다) 한 예: seoyeon 의 요약이 「평소와 다른 IP 에서 접속하고 파일을 많이 내려받았습니다. 먼저 내려받은 파일의 목록을 확인하세요.」라면 <mark style="background:#bde3ff">표에 없는 내용이 없고, 탐지된 규칙 두 개(평소와 다른 IP · 대량 다운로드)가 모두 들어 있습니다.</mark>
  - 만약 요약에 「계정이 해킹당했습니다」 같은 문장이 있다면 표에 없는 단정입니다. 이 경우에는 지시문의 「공격이라고 단정하지 마세요」 앞에 「[사실]에 적힌 것만 말하세요」를 한 번 더 적고 다시 실행해 문장이 사라지는지 확인합니다.
  - 탐지된 규칙이 하나 빠졌다면 [사실]에는 두 규칙이 모두 있는데 AI 가 한 가지만 쓴 것입니다. 지시문에 「탐지된 내용을 모두 포함하세요」를 더하는 방법이 있습니다.

**왜**

- <mark>점수와 등급은 코드가 정하고, AI 는 코드가 정한 값을 문장으로 풀어 쓰기만 합니다.</mark> AI 의 문장은 실행마다 달라지지만 확인할 순서는 바뀌지 않습니다. 그리고 보내는 글에 값을 그대로 넣었기 때문에 담당자가 [사실]과 요약을 나란히 보고 틀린 곳을 찾을 수 있습니다.

**자주 틀리는 곳**

- 1번 조건을 `and` 대신 `or` 로 쓰면 오류는 나지 않지만 <mark>**요약할 대상이 3명이 아니라 4명으로 나옵니다.**</mark> 단계 2 의 제목 줄에 `4 명 (최대 3 명)` 이 나오는 것이 이 실수의 모습입니다. `or` 는 하나만 참이어도 통과해서, 3명이 찬 뒤에도 `low` 가 아닌 jiwoo 가 들어옵니다.
  - 단계 2 는 다음처럼 나옵니다.

```
--- 단계 2: 요약할 대상 4 명 (최대 3 명)
high dami 60
mid seoyeon 45
mid gaeun 40
mid jiwoo 35
```

- 3번에서 `.join` 을 쓰지 않고 `meaning_text = meanings` 로 쓰면 오류는 나지 않지만 <mark>**[사실]의 탐지된 내용에 대괄호와 따옴표가 그대로 나옵니다.**</mark> 단계 3 의 마지막 줄이 이 실수의 모습입니다.

```
--- 단계 3: AI 에게 보내는 글 (seoyeon)
당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. [사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 먼저 확인할 것을 한 가지 제안하세요.
[사실] 대상: seoyeon / 등급: mid / 점수: 45점 / 탐지된 내용: ['평소와 다른 IP 에서 SaaS 에 접속함', 'SaaS 에서 파일을 한꺼번에 많이 내려받음']
```

- 4번에서 따옴표 앞의 `f` 를 빼면 오류는 나지 않지만 <mark>**{entity} 라는 글자가 그대로 AI 에게 갑니다.**</mark> 값이 들어가지 않아 AI 는 요약할 내용을 받지 못합니다.

```
--- 단계 3: AI 에게 보내는 글 (seoyeon)
당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. [사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 먼저 확인할 것을 한 가지 제안하세요.
[사실] 대상: {entity} / 등급: {grade} / 점수: {score}점 / 탐지된 내용: {meaning_text}
```

- 6 · 7번을 빠뜨리면 평소에는 문제가 없다가 <mark>**AI 호출이 실패했을 때 요약 자리가 빈칸으로 나옵니다.**</mark> 무료 키의 한도(1분에 15번)를 넘어 `429` 가 나는 때가 그렇습니다. 오류가 아니라서 눈에 띄지 않는 것이 문제입니다.

```
[LLM 호출 실패] 상태 코드 429
dami : 
[LLM 호출 실패] 상태 코드 429
seoyeon : 
[LLM 호출 실패] 상태 코드 429
gaeun : 
```

**관제에서는**

- Gemini API 를 활용한 AI 요약은 담당자가 점수와 이유를 읽는 시간을 줄이는 도구입니다. <mark>값은 규칙이 정하고 AI 는 설명만 하게 하면, AI 가 틀려도 확인할 순서는 안 틀립니다.</mark>

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `analyze_events` 안

```python
    chains = find_chains_in_events(events)       # 이벤트에서 서로 다른 로그로 연결된 사건을 구한다
    findings = collect_findings(events, chains)  # 이벤트와 연결된 사건에서 탐지된 규칙을 모은다
    totals = score_findings(findings)            # 탐지된 규칙으로 대상별 점수를 더한다
    reasons = collect_reasons(findings)          # 대상마다 탐지된 규칙 이름을 모은다
```

② `build_report` 안

```python
    source_event_counts = events["source"].value_counts()                                  # 로그 종류마다 이벤트가 몇 개인지 센다
    source_count_dict = source_event_counts.to_dict()                                      # 센 결과를 JSON 에 저장할 수 있는 딕셔너리로 바꾼다
    report = {"date": REPORT_DATE, "event_count": len(events), "source_event_counts": source_count_dict,
              "finding_count": len(findings), "records": records, "summaries": summaries}  # 보고서 딕셔너리로 모은다
```

내가 채운 코드는 위의 코드입니다. <mark>줄 수가 달라도 주석이 말한 일을 하면 맞습니다.</mark>

**결과**

- (가) 출력은 다음과 같고, 이벤트는 <mark style="background:#bde3ff">**57개**</mark>, 탐지된 규칙은 <mark style="background:#bde3ff">**8건**</mark>, 점수 기록은 <mark style="background:#bde3ff">**5건**</mark>, Gemini API 를 활용한 AI 요약은 <mark style="background:#bde3ff">**3건**</mark>(실패 0건)입니다. 단계 3 의 문장은 AI 가 쓴 한 예이고 사람마다 다릅니다.

```
--- 단계 1: 읽은 이벤트 57 개
--- 단계 2: 탐지된 규칙 8 건 → 점수 기록 5 건을 day03_risk_scores.json 에 저장
--- 단계 3: Gemini API 를 활용한 AI 요약 3 건 (실패 0 건)
dami : 퇴사한 사람의 계정으로 서버에 요청한 기록이 있습니다. 먼저 이 계정이 비활성화되어 있는지 확인하세요.
seoyeon : 평소와 다른 IP 에서 접속하고 파일을 한꺼번에 많이 내려받은 기록이 있습니다. 먼저 내려받은 파일 목록을 확인하세요.
gaeun : 규칙으로는 허용되는 요청을 서버가 거절했고, 서로 다른 로그에서 짧은 시간 안에 이벤트가 확인되었습니다. 먼저 거절된 요청의 서버 설정을 확인하세요.
--- 단계 4: 보고서를 anomaly_detection_report_2026-11-02.json 에 저장
--- 단계 5: 확인할 순서
high dami 60
mid seoyeon 45
mid gaeun 40
mid jiwoo 35
low 198.51.100.90 30
```

- 보고서 파일 `anomaly_detection_report_2026-11-02.json` 의 앞부분은 다음과 같습니다. `date` 는 `2026-11-02`, `event_count` 는 57, `finding_count` 는 8이고 `records` 는 5건, `summaries` 는 3건입니다. 로그 종류마다 이벤트 수는 웹 서버 28 · 판정 서버 15 · SaaS 14 입니다.

```
{
  "date": "2026-11-02",
  "event_count": 57,
  "source_event_counts": {
    "web": 28,
    "server": 15,
    "saas": 14
  },
  "finding_count": 8,
  "records": [
    {
      "entity": "dami",
      "score": 60,
      "grade": "high",
      "reasons": [
        "퇴사한 계정"
      ]
    },
    …
  ],
  "summaries": [
    …
  ]
}
```

- (나) 점수와 등급을 코드가 정하는 이유는 <mark style="background:#bde3ff">같은 입력이면 항상 같은 결과가 나와야 확인할 순서가 흔들리지 않기 때문</mark>입니다.
  - 단계 5 의 확인할 순서(dami → seoyeon → gaeun → jiwoo → 198.51.100.90)는 Gemini API 를 활용한 AI 요약이 어떻게 나와도 같습니다. 점수는 `risk_scores.py` 의 `WEIGHTS` 와 등급 기준으로 정해지기 때문입니다.
  - 단계 3 의 요약 문장은 실행할 때마다 다르게 나올 수 있습니다. 순서를 AI 가 정하면 같은 로그로 실행해도 오늘과 내일의 순서가 달라질 수 있습니다.
  - AI 는 값을 풀어 쓰기만 해서, 요약이 틀려도 점수와 등급은 그대로입니다.
- (다) AI 호출이 실패해도 멈추지 않게 만든 이유는 <mark style="background:#bde3ff">AI 하나가 실패했다고 점수와 등급이 담긴 보고서까지 못 만들면 담당자가 아침에 아무것도 볼 수 없기 때문</mark>입니다.
  - 실패한 요약은 `(요약 실패 — 점수와 이유를 직접 확인)` 이라는 문장으로 채워지고, 단계 3 의 제목 줄에 실패 건수가 나옵니다.
  - 대체 문장이 들어간 대상은 담당자가 `records` 의 점수와 이유(`reasons`)를 직접 읽고 판단합니다. 1분 뒤에 다시 실행해 요약을 받을 수도 있습니다.
  - 실패했을 때의 출력은 다음과 같습니다(`429` 로 3번 모두 실패한 경우).

```
--- 단계 1: 읽은 이벤트 57 개
--- 단계 2: 탐지된 규칙 8 건 → 점수 기록 5 건을 day03_risk_scores.json 에 저장
[LLM 호출 실패] 상태 코드 429
[LLM 호출 실패] 상태 코드 429
[LLM 호출 실패] 상태 코드 429
--- 단계 3: Gemini API 를 활용한 AI 요약 3 건 (실패 3 건)
dami : (요약 실패 — 점수와 이유를 직접 확인)
seoyeon : (요약 실패 — 점수와 이유를 직접 확인)
gaeun : (요약 실패 — 점수와 이유를 직접 확인)
--- 단계 4: 보고서를 anomaly_detection_report_2026-11-02.json 에 저장
--- 단계 5: 확인할 순서
high dami 60
mid seoyeon 45
mid gaeun 40
mid jiwoo 35
low 198.51.100.90 30
```

**왜**

- <mark>단계를 이어 실행할 때는 앞 단계의 결과를 다음 단계에 정확히 전달하고, 바깥 서비스(AI)처럼 실패할 수 있는 단계는 대체 값으로 이어 가게 만듭니다.</mark> 그래야 한 번 실행한 결과를 믿고 보고서로 보낼 수 있습니다.

**자주 틀리는 곳**

- 2번에서 `collect_findings(events, chains)` 의 순서를 바꿔 `collect_findings(chains, events)` 로 쓰면 `TypeError` 오류가 납니다. <mark>**함수에 전달하는 순서는 정의한 순서(이벤트 표, 연결된 사건)입니다.**</mark>
  - 실행하면 다음 오류가 납니다(<mark style="background:#ffc4d6">`list indices must be integers or slices, not str`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day06_3-1_run.py", line 3, in <module>
  File "…/anomaly_detection/pipeline.py", line 75, in run_pipeline
  File "…/anomaly_detection/pipeline.py", line 17, in analyze_events
  File "…/anomaly_detection/risk_scores.py", line 31, in collect_findings
  File "…/anomaly_detection/access_detection.py", line 21, in pick_server_failures
TypeError: list indices must be integers or slices, not str
```

  - 줄 번호는 사람마다 다릅니다.
- 1번을 빠뜨리면 2번 줄에서 `NameError` 가 납니다. <mark>**앞 단계의 결과 `chains` 가 만들어지지 않았기 때문입니다.**</mark>

```
Traceback (most recent call last):
  File "…/anomaly_detection/day06_3-1_run.py", line 3, in <module>
  File "…/anomaly_detection/pipeline.py", line 74, in run_pipeline
  File "…/anomaly_detection/pipeline.py", line 16, in analyze_events
NameError: name 'chains' is not defined
```

- 6번에서 `.to_dict` 의 괄호를 빼거나, 6번을 통째로 쓰지 않고 시리즈를 그대로 보고서에 넣으면 `TypeError` 가 납니다. <mark>**`.to_dict()` 는 괄호까지 써야 합니다.**</mark> 보고서를 저장하는 단계에서 오류가 나고, 단계 4 의 제목 줄 앞까지는 정상으로 출력됩니다.
  - 괄호를 빼면 다음 오류가 납니다(<mark style="background:#ffc4d6">`Object of type method is not JSON serializable`</mark>).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day06_3-1_run.py", line 3, in <module>
  File "…/anomaly_detection/pipeline.py", line 86, in run_pipeline
  File "…/anomaly_detection/pipeline.py", line 65, in save_report
TypeError: Object of type method is not JSON serializable
```

  - `.to_dict()` 를 쓰지 않고 시리즈를 그대로 넣으면 `Object of type Series is not JSON serializable` 오류가 납니다.
- 7번의 딕셔너리에서 키와 값 묶음 사이의 쉼표를 빼면 실행하기 전에 `SyntaxError` 가 납니다(오류 문구는 파이썬 버전마다 조금 다릅니다).

```
  File "…/anomaly_detection/pipeline.py", line 56
    "finding_count": len(findings), "records": records, "summaries": summaries}
    ^
SyntaxError: invalid syntax
```

**관제에서는**

- 여러 단계를 한 번에 실행하는 프로그램은 어느 단계가 어떤 결과를 냈는지 단계마다 한 줄씩 출력해 둡니다. <mark>그래야 결과가 이상할 때 어느 단계에서 틀어졌는지 바로 찾을 수 있습니다.</mark>

---

### 정답 4-1

**용어 풀이**

- 데이터 문제: 로그나 알림 같은 <mark>자료</mark>에 있어야 할 것이 없거나, 빠졌거나, 깨져 있는 경우입니다.
- 규칙 문제: 「무엇을 의심할지」 정해 둔 <mark>기준</mark>이 없거나 현실과 맞지 않는 경우입니다.
- 운영 설정 문제: 서버를 켜고 접속을 허용하는 <mark>설정</mark>이 목적과 맞지 않는 경우입니다.

아래 답은 한 예이고, 상황마다 원인이 겹치면 겹치는 대로 쓰면 맞습니다. 4개 이상 쓴 것이 기준입니다.

#### 상황 1 · 설정 파일 주소를 연달아 요청했는데 「의심」이 아니라 「오류」로 분류됨

- 원인: <mark style="background:#bde3ff">규칙 문제</mark>입니다.
  - `is_suspicious` 는 요청 하나의 상태 코드가 401 · 403 이거나 경로에 `/admin` 이 있을 때만 「의심」으로 가릅니다.
  - 198.51.100.90 의 세 요청은 상태 코드가 모두 404 이고 경로에 `/admin` 이 없어서 의심 조건에 맞지 않습니다. 400 이상이라는 `is_error` 조건에만 맞아서 「오류」가 됩니다.
  - 한 줄씩은 흔한 404 이지만, 설정 파일 · 관리 화면 주소를 1초 간격으로 연달아 요청한 것은 탐색입니다. 이 규칙은 경로 이름도 같은 주소의 반복도 보지 않습니다.
- 고칠 파일: `log_classify.py`
- 어떻게 고치나요:
  - 케이스 A: <mark style="background:#bde3ff">값을 바꿉니다.</mark> `is_suspicious` 에 「경로에 `/.env` · `/wp-login` · `/phpmyadmin` 중 하나가 들어 있다」는 조건을 하나 더하고 `or` 로 잇습니다.
  - 케이스 B: 경로 목록만 늘리면 목록에 없는 새 주소는 또 놓칩니다. 그래서 같은 주소가 없는 주소를 연달아 요청하는 횟수를 세는 규칙을 <mark style="background:#bde3ff">새로 넣습니다.</mark> 이 수업에서는 11/5 오전에 `find_scan_ips` 로 만들었습니다.
- 고친 뒤 확인: 같은 로그를 다시 분류해서 198.51.100.90 의 세 줄이 「의심」 목록에 나오는지 봅니다. 분류별 개수는 정상 15 · 오류 5 · 의심 8 에서 정상 15 · 오류 2 · 의심 11 로 바뀝니다.
- 담당자가 가장 먼저 할 일: 198.51.100.90 의 같은 시간대 요청이 더 있었는지, 성공(200)한 요청이 있었는지 접속 기록에서 확인합니다.

#### 상황 2 · 로그 30줄이 이벤트 28개가 됨

- 원인: <mark style="background:#bde3ff">데이터 문제</mark>입니다.
  - 원본 로그 30줄 가운데 2줄은 `GET /board/5 HTTP/1.1` 에서 잘려 있거나 `-` 하나만 있어서 큰따옴표가 두 개보다 적습니다.
  - `normalize_web` 은 이런 줄을 읽지 않고 `None` 을 리턴하므로 이벤트가 되지 못합니다. 그래서 웹 서버 이벤트가 30개가 아니라 28개입니다.
  - 줄이 사라진 것이 아니라 읽기 실패로 센 것입니다. 11/3 오전 2교시 실행 파일의 단계 1 에 `읽기 실패 2 줄` 로 나옵니다.
- 고칠 파일: 고칠 코드는 없습니다. 정규화 코드(`normalize_web.py`)는 의도한 대로 동작했고, 문제는 원본 로그의 두 줄입니다.
- 어떻게 고치나요:
  - 케이스 A: 코드를 바꾸지 않고 <mark style="background:#bde3ff">확인합니다.</mark> 읽기 성공 28 + 읽기 실패 2 = 전체 30 이 맞는지 계산해 보고서에 적어 둡니다.
  - 케이스 B: 로그를 만드는 서버에서 줄이 끊기는 원인을 찾아 고칩니다. 이 수업에서는 서버 설정을 바꾸지 않았습니다.
- 고친 뒤 확인: 정규화한 이벤트 수와 읽기 실패 줄 수를 더해 원본 줄 수 30 과 같은지 봅니다. 같으면 사라진 줄 없이 모두 설명됩니다.
- 담당자가 가장 먼저 할 일: 읽지 못한 2줄의 원문을 원본 로그에서 찾아, 서버가 로그를 쓰는 도중 끊긴 것인지 확인합니다.

#### 상황 3 · 웹 서버 로그에서 사용자를 알 수 있는 요청이 1개뿐

- 원인: <mark style="background:#bde3ff">데이터 문제</mark>입니다.
  - 웹 서버 로그에는 사용자 이름이 없고 IP 주소만 있어서 이벤트의 `user` 가 `None` 입니다.
  - 사용자를 알려면 SaaS 에서 로그인에 성공한 IP 를 찾아 연결해야 합니다(`make_ip_user_map`). 웹 서버 실패 요청 13개 중 이렇게 사용자를 알 수 있는 것은 198.51.100.77(gaeun)의 `/admin` 1개뿐입니다.
  - 203.0.113.50 은 SaaS 로그와 판정 서버 로그에 기록이 없어서 누구의 일인지 알 수 없습니다.
- 고칠 파일: 케이스 A 는 웹 서버의 로그 설정, 케이스 B 는 `risk_scores.py` 입니다.
- 어떻게 고치나요:
  - 케이스 A: <mark style="background:#bde3ff">새로 넣습니다.</mark> 웹 서버가 로그인한 사용자의 이름도 로그 한 줄에 남기도록 설정을 바꿉니다. 이 수업에서는 서버 설정을 바꾸지 않았습니다.
  - 케이스 B: 사용자를 모르는 요청은 사용자가 아니라 IP 를 대상으로 점수를 매깁니다. 경로 스캔 198.51.100.90 을 IP 로 점수를 매긴 것이 이 방식입니다.
- 고친 뒤 확인: 케이스 A 는 다시 실행해 「IP 로 사용자를 알 수 있는 웹 실패 이벤트」 수가 1개보다 늘었는지 봅니다. 케이스 B 는 점수 파일의 `entity` 에 IP(198.51.100.90)가 나오는지 봅니다.
- 담당자가 가장 먼저 할 일: 203.0.113.50 으로 로그인한 기록이 다른 로그에 있는지 검색해 계정을 찾습니다.

#### 상황 4 · 두 로그에 나오는 seoyeon 이 연결되지 않음

- 원인: <mark style="background:#bde3ff">규칙 문제</mark>입니다.
  - `find_chains` 는 사용자의 하루 첫 이벤트부터 마지막 이벤트까지 걸린 시간(`span`)이 `WINDOW_MINUTES`(60분) 이내여야 연결합니다.
  - seoyeon 의 이벤트는 09:05 부터 18:20 까지 흩어져 있어서 `span` 이 555분이고 연결되지 않습니다. 17:38 의 로그인부터 18:20 의 서버 거절까지는 42분인데, 하루 전체로 계산해서 놓칩니다.
  - gaeun 은 이벤트 3종류가 41분 안에 있어서 연결됩니다.
- 고칠 파일: `correlation.py`
- 어떻게 고치나요:
  - 케이스 A: <mark style="background:#bde3ff">값을 바꿉니다.</mark> `WINDOW_MINUTES` 를 600 으로 올리면 이 샘플에서는 seoyeon 이 `서로 다른 로그 2종류 · 555분 안` 으로 연결됩니다. 하지만 하루 전체가 한 사건이 되어 「짧은 시간 안에 모였다」는 뜻이 약해집니다.
  - 케이스 B: `find_chains` 의 계산 방식을 <mark style="background:#bde3ff">바꿉니다.</mark> 첫 이벤트와 마지막 이벤트의 차이 대신, 이웃한 이벤트 사이가 60분 이내로 이어지는 이벤트끼리만 한 사건으로 묶습니다.
- 고친 뒤 확인: 다시 실행해 seoyeon 이 연결된 사건에 나오는지, 연결 이유에 적힌 분이 어떻게 달라졌는지 봅니다. 케이스 A 에서는 이유에 `555분 안` 이 나옵니다.
- 담당자가 가장 먼저 할 일: seoyeon 의 17:38 로그인부터 18:20 서버 거절까지를 시간순으로 읽습니다.

#### 상황 7 · 정산 조회 시도에는 알림이 나지 않음

- 원인: <mark style="background:#bde3ff">규칙 문제</mark>입니다(그 일을 잡는 규칙이 없습니다).
  - 서버 거절 규칙(`pick_suspicious`)은 한 사용자의 서버 실패가 `REPEAT_LIMIT`(3번) 이상일 때만 먼저 확인합니다.
  - seoyeon 의 서버 실패는 11:40 의 `SETTLE:QUERY` 와 18:20 의 `SALES:CHANGE` 두 번뿐이라 기준에 못 미칩니다. 그래서 P5 는 알림 대상이 아닙니다.
  - 횟수만 보는 규칙은 정산처럼 중요한 권한을 권한 없이 한 번 건드린 일을 놓칩니다.
- 고칠 파일: `access_detection.py`
- 어떻게 고치나요: <mark style="background:#bde3ff">새로 넣습니다.</mark>
  - 중요한 권한 목록(예: `SETTLE:QUERY`)을 정하고, 서버 실패 이벤트의 행동이 그 목록에 있으면 횟수와 상관없이 확인 대상에 넣는 함수를 `pick_suspicious` 옆에 더합니다.
  - 이 규칙은 업무상 실수로 한 번 건드린 사용자까지 알려서 오탐이 늘 수 있습니다.
- 고친 뒤 확인: 같은 이벤트로 다시 실행해 P5 가 알림 대상에 나오는지 보고, 11/6 오전처럼 오탐과 미탐을 다시 세어 오탐이 얼마나 늘었는지 봅니다.
- 담당자가 가장 먼저 할 일: seoyeon 에게 11:40 의 정산 조회가 업무 요청이었는지 확인합니다.

#### 상황 8 · 서버가 같은 네트워크에 열려 있고, 지우면 접속 기록도 사라짐

- 원인: <mark style="background:#bde3ff">운영 설정 문제</mark>입니다(두 가지).
  - 접속 범위: 5교시 `compose.yaml` 의 `ports` 가 `"8081:80"` 처럼 주소 없이 적혀 있으면 같은 네트워크의 다른 PC 도 접속할 수 있습니다. `docker compose ps` 의 PORTS 에 `0.0.0.0:8081->80/tcp` 로 나옵니다.
  - 접속 기록: 서버를 `down` 으로 지우면 서버 안에 쌓인 기록도 함께 사라집니다. 서버 안 기록 폴더를 내 `logs` 폴더에 연결(`volumes`)해 두지 않았기 때문입니다.
- 고칠 파일: `compose.secure.yaml`
- 어떻게 고치나요:
  - 케이스 A(접속 범위): <mark style="background:#bde3ff">값을 바꿉니다.</mark> `"8081:80"` 을 `"127.0.0.1:8081:80"` 으로 바꿔 내 PC 에서만 접속되게 합니다. 모두에게 열어 둘 서버(`web1`)는 그대로 둡니다.
  - 케이스 B(접속 기록): <mark style="background:#bde3ff">새로 넣습니다.</mark> 서버 설정에 `volumes:` 아래 `- ./logs:/var/log/nginx` 를 더해 접속 기록을 내 `logs` 폴더에 남깁니다.
- 고친 뒤 확인: 케이스 A 는 `docker compose ps` 의 PORTS 가 `127.0.0.1:8081->80/tcp` 로 바뀌었는지 봅니다. 케이스 B 는 서버를 지운 뒤에도 `ls logs` 에 `access.log` 가 남아 있는지 봅니다.
- 담당자가 가장 먼저 할 일: `logs/access.log` 에 내 PC 가 아닌 IP 의 요청이 있는지 확인합니다.

**왜**

- <mark>상황마다 원인이 데이터인지 규칙인지 설정인지 먼저 가려야 고칠 곳이 정해집니다.</mark> 데이터를 고쳐야 할 때 규칙의 기준 값을 바꾸면 증상만 가려지고, 규칙을 고쳐야 할 때 데이터를 바꾸면 같은 일이 다시 생깁니다.

**자주 틀리는 곳**

- <mark>원인을 「규칙 문제입니다」 한 줄로만 쓰는 경우</mark>입니다. 어느 파일의 어느 함수가 지금 어떻게 동작해서 그 일이 생기는지까지 써야 고칠 곳이 정해집니다.
- 「고치는 방법」에 값을 어디에 어떻게 넣는지 쓰지 않는 경우입니다. 예를 들어 「예외를 추가한다」가 아니라 「`TRUSTED_IPS` 에 `203.0.113.80` 을 넣는다」처럼 씁니다.
- 고친 뒤 확인을 「잘 되는지 본다」로 쓰는 경우입니다. 어떤 출력이 어떻게 바뀌면 고쳐진 것인지(오탐 4개 → 2개 등)를 씁니다.

**관제에서는**

- 인수인계 문서는 상황별로 「원인 → 고칠 파일 → 어떻게 → 확인」이 적혀 있어야 다음 담당자가 같은 일을 처음부터 다시 조사하지 않습니다. <mark>마지막 칸의 「가장 먼저 할 일」은 자동 대응을 만들 때 대응 목록의 출발점이 됩니다.</mark>

---

### 정답 마무리

- (가) 한 예: <mark>`git status` 에서 `.env` 와 `.venv` 가 보이지 않았습니다.</mark> `__pycache__` 가 보여서 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 다시 확인했습니다.
- 깃허브의 `anomaly_detection` 폴더에 `event_summary.py` · `pipeline.py` · `anomaly_detection_report_2026-11-02.json` 이 보이면 됩니다.
