# 11/4(수) 오전 · 4과목 이상탐지 ③ — 평소 기준 정하기 · 로그인 실패 찾기 · 이벤트 유형 — 실습

어제는 로그를 표로 읽고 세는 법을 배웠습니다. 오늘 오전에는 두 가지를 합니다. 첫째, **「평소」가 얼마인지 정합니다.** 둘째, **평소보다 많은 일을 찾는 규칙**을 만듭니다. 이렇게 규칙으로 일을 찾는 것을 **탐지**라고 하며, SIEM(심, 보안 로그를 모아 탐지 · 알림하는 시스템)의 네 단계(수집 → 정규화 → 탐지 → 알림) 중 세 번째입니다.

- **2교시**: 지난 7일의 로그인 실패 횟수로 **평소 기준**을 정하고, 알림을 보낼 기준 숫자(임계값, threshold, 쓰레숄드)를 정합니다.
- **3교시**: 같은 주소의 로그인 실패가 알림 기준(5번) 이상인 곳을 찾아 알림 대상으로 뽑습니다.
- **4교시**: 이벤트마다 **유형 이름**을 정하고 유형별 개수를 셉니다.

오늘은 오전 2 · 3 · 4교시이고, 깃허브에 올리는 일은 오후 6교시 마지막에 합니다. 교시마다 문제는 하나입니다.

- 오늘 오전에 쓰는 도구는 **파이썬 · 판다스 · VS Code · 터미널**입니다. 판다스는 어제 설치했고, 안 했다면 아래 「🆘」를 봅니다.
- **이상(anomaly, 애너멀리)** 은 평소 범위를 벗어난 일입니다. 예를 들어 지난 7일 동안 하루 최대 4번이던 로그인 실패가 한 주소에서 5번이 되는 것입니다. 이상은 **먼저 살펴볼 일**이라는 뜻입니다.
- 「5번 이상」의 이상(以上)은 「5번이거나 5번보다 많음」이라는 다른 뜻입니다.
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, 내 출력이나 샘플 데이터의 값을 근거로 이유까지 서술합니다.
- 알림 기준(임계값)은 **평소 기준에서 정한 숫자로 고정**하고, 값을 바꿔 가며 비교하지 않습니다.
- 📎 **오늘 불러 쓰는 이전 파일**은 없습니다. 어제 파일이 없어도 풀 수 있습니다.

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치를 확인하고, 판다스가 설치돼 있는지 봅니다(맥북은 `python3`). `pwd` 가 `…/anomaly_detection` 으로 끝나고, 마지막에 버전 번호(예: `2.3.3`)가 나오면 됩니다. `No module named 'pandas'` 가 나오면 아래 「🆘」 첫 줄을 따릅니다.
   ```bash
   cd anomaly_detection
   pwd
   python -c "import pandas; print(pandas.__version__)"
   ```
3. **오늘 받은 파일 두 개**(`day03_am_baseline_login.md`, `day03_am_report.md`)를 `다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
4. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-04(수))` 의 `이름` 을 내 이름으로 바꿉니다. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.
5. **[VS Code 또는 터미널]** `anomaly_detection` 폴더에 `normalized_events.json` 과 `baseline_logins.csv` 파일을 만들어 아래 내용을 그대로 붙여 넣습니다(터미널에서는 `touch 파일이름` 후 VS Code 에서 엽니다). 두 파일을 모두 붙인 뒤 아래 6번으로 이어 갑니다.

**`normalized_events.json`** — 어제 오후에 만든 이벤트 샘플 57개입니다. 어제 만든 파일이 있어도 열이 6개가 아니거나 아래 6번에서 `57` 이 나오지 않으면 아래 내용으로 덮어씁니다. 이벤트 날짜는 모두 2026-11-02 입니다. `null` 은 그 값이 로그에 없다는 뜻입니다.

```
[
  {"time": "2026-11-02 02:14:08", "source": "saas", "user": "jiwoo", "ip": "203.0.113.80", "action": "login", "result": "실패"},
  {"time": "2026-11-02 09:01:05", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /", "result": "성공"},
  {"time": "2026-11-02 09:01:06", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /static/app.css", "result": "성공"},
  {"time": "2026-11-02 09:03:47", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /login", "result": "성공"},
  {"time": "2026-11-02 09:03:59", "source": "web", "user": null, "ip": "198.51.100.34", "action": "POST /login", "result": "성공"},
  {"time": "2026-11-02 09:04:00", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:05:21", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /board?page=2", "result": "성공"},
  {"time": "2026-11-02 09:05:30", "source": "saas", "user": "seoyeon", "ip": "198.51.100.9", "action": "login", "result": "성공"},
  {"time": "2026-11-02 09:05:40", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /board/12", "result": "성공"},
  {"time": "2026-11-02 09:12:01", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /login", "result": "성공"},
  {"time": "2026-11-02 09:12:03", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:06", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:09", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:12", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:15", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "실패"},
  {"time": "2026-11-02 09:12:18", "source": "web", "user": null, "ip": "203.0.113.50", "action": "POST /login", "result": "성공"},
  {"time": "2026-11-02 09:12:25", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /admin", "result": "실패"},
  {"time": "2026-11-02 09:12:27", "source": "web", "user": null, "ip": "203.0.113.50", "action": "GET /admin/users", "result": "실패"},
  {"time": "2026-11-02 09:20:10", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /.env", "result": "실패"},
  {"time": "2026-11-02 09:20:11", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /wp-login.php", "result": "실패"},
  {"time": "2026-11-02 09:20:12", "source": "web", "user": null, "ip": "198.51.100.90", "action": "GET /phpmyadmin", "result": "실패"},
  {"time": "2026-11-02 09:22:30", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board/99", "result": "실패"},
  {"time": "2026-11-02 09:25:02", "source": "web", "user": null, "ip": "198.51.100.34", "action": "GET /report", "result": "실패"},
  {"time": "2026-11-02 09:26:44", "source": "web", "user": null, "ip": "192.0.2.15", "action": "GET /search?q=network", "result": "성공"},
  {"time": "2026-11-02 09:28:13", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /", "result": "성공"},
  {"time": "2026-11-02 09:28:20", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:30:12", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "login", "result": "성공"},
  {"time": "2026-11-02 09:31:15", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board", "result": "성공"},
  {"time": "2026-11-02 09:33:51", "source": "web", "user": null, "ip": "198.51.100.77", "action": "GET /admin", "result": "실패"},
  {"time": "2026-11-02 09:35:02", "source": "web", "user": null, "ip": "192.0.2.88", "action": "GET /logout", "result": "성공"},
  {"time": "2026-11-02 09:36:10", "source": "web", "user": null, "ip": "198.51.100.21", "action": "GET /board/12", "result": "성공"},
  {"time": "2026-11-02 09:40:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 09:52:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:CHANGE", "result": "성공"},
  {"time": "2026-11-02 10:05:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 10:09:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 10:12:55", "source": "saas", "user": "gaeun", "ip": "198.51.100.77", "action": "login", "result": "성공"},
  {"time": "2026-11-02 10:14:00", "source": "server", "user": "gaeun", "ip": null, "action": "ACCOUNT:CHANGE", "result": "실패"},
  {"time": "2026-11-02 11:02:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:03:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:05:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:CHANGE", "result": "실패"},
  {"time": "2026-11-02 11:08:00", "source": "server", "user": "dami", "ip": null, "action": "SALES:QUERY", "result": "실패"},
  {"time": "2026-11-02 11:25:40", "source": "saas", "user": "seoyeon", "ip": "198.51.100.9", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 11:40:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SETTLE:QUERY", "result": "실패"},
  {"time": "2026-11-02 13:15:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 13:50:21", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "file.upload", "result": "성공"},
  {"time": "2026-11-02 14:30:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:CHANGE", "result": "성공"},
  {"time": "2026-11-02 15:05:00", "source": "server", "user": "junho", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 15:20:03", "source": "saas", "user": "junho", "ip": "192.0.2.41", "action": "login", "result": "성공"},
  {"time": "2026-11-02 16:02:18", "source": "saas", "user": "jiwoo", "ip": "198.51.100.52", "action": "login", "result": "성공"},
  {"time": "2026-11-02 16:10:00", "source": "server", "user": "gaeun", "ip": null, "action": "SALES:QUERY", "result": "성공"},
  {"time": "2026-11-02 17:38:10", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "login", "result": "성공"},
  {"time": "2026-11-02 17:40:02", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:40:31", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:41:05", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:41:48", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 17:42:20", "source": "saas", "user": "seoyeon", "ip": "203.0.113.80", "action": "file.download", "result": "성공"},
  {"time": "2026-11-02 18:20:00", "source": "server", "user": "seoyeon", "ip": null, "action": "SALES:CHANGE", "result": "실패"}
]
```

**`baseline_logins.csv`** — 하루마다 **로그인에 가장 많이 실패한 주소 한 곳의 실패 횟수**를 적은 연습용 숫자 7개입니다. CSV 는 값을 쉼표로 구분해 적은 텍스트 파일입니다. 첫 줄은 **헤더(header)** 로, 열 이름이 적힌 줄입니다. 둘째 줄부터 한 줄이 하루입니다.

```
date,failed_logins
2026-10-26,2
2026-10-27,3
2026-10-28,1
2026-10-29,4
2026-10-30,2
2026-10-31,3
2026-11-01,2
```

6. **[터미널]** 두 파일이 정상인지 확인합니다(맥북은 `python3`).
   ```bash
   python -c "import json; print(len(json.load(open('normalized_events.json', encoding='utf-8'))))"
   python -c "print(len(open('baseline_logins.csv', encoding='utf-8').read().splitlines()))"
   ```
   - `python -c "코드"` 는 파일을 만들지 않고 코드를 한 줄로 바로 실행합니다. 순서대로 `57`(이벤트 개수)과 `8`(헤더 줄 포함)이 나와야 합니다. 다르면 줄이 빠졌거나 빈 줄이 끼어든 것이니 다시 붙여 넣습니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 파일 이름이 문서와 같은지 봅니다. `cd anomaly_detection` 이 안 되면 `ls` 로 폴더 이름을 확인하고, 없으면 `mkdir anomaly_detection` 으로 만든 뒤 들어갑니다.
- `No module named 'pandas'`: 가상환경이 활성화되지 않은 터미널입니다. `security-agent-toolkit` 폴더에서 가상환경을 활성화한 뒤(`source .venv/Scripts/activate`, 맥북은 `Scripts` 를 `bin` 으로, 폴더 이름이 다르면 그 이름으로) `python -m pip install pandas` 를 칩니다.
- `FileNotFoundError` · `ValueError`: 위치나 파일 이름이 틀렸거나 붙여 넣은 내용이 틀렸습니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 막히면 맨 아래 「정답」을 보고, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 **터미널**에서 합니다. 파일을 지금 위치 기준으로 찾기 때문입니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 지난 7일로 평소 기준과 알림 기준 정하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「로그인 실패 알림을 만들려는데, 한 주소가 하루 동안 로그인에 몇 번 실패하면 알려야 할지 모르겠습니다. 너무 낮아도, 너무 높아도 곤란합니다.
>
> 지난 7일 동안 하루에 로그인에 가장 많이 실패한 주소가 몇 번 실패했는지 표를 드립니다. 하루 평균과 가장 많았던 날의 횟수를 구해서, 알림 기준 숫자를 하나 정해 주세요(정하는 방법은 아래 2.1 에서 설명합니다).」
> - **왜 중요한가**: <mark>「하루 로그인 실패가 몇 번 이상이면 평소보다 많다고 볼 것인가」는 평소를 모르면 정할 수 없습니다.</mark> 평소 기준(baseline, 베이스라인)을 먼저 구해 두면 기준 숫자에 근거가 생기고, 담당자가 바뀌어도 같은 이유로 설명할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다. (판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.)

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 어제까지는 이벤트를 **세기**만 했습니다. 오늘부터는 세어 낸 숫자가 「많은가?」를 판단합니다.
2. 판단하려면 비교할 **평소**가 있어야 합니다. 평소를 모르고 정한 기준에는 두 가지 문제가 생깁니다.
   - 너무 낮으면 평범한 날에도 알림이 발생해서, 담당자가 알림을 무시하게 됩니다.
   - 너무 높으면 누군가 비밀번호를 계속 바꿔 가며 로그인을 시도해도 알림이 나지 않습니다.
3. 그래서 **지난 며칠의 숫자(평소 기준)** 를 먼저 구하고, 거기서 알림 기준 숫자를 정합니다.

### 📖 2.1 평소 기준과 알림 기준

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 말 | 뜻 | 오늘 예 |
|---|---|---|
| 평소 기준(baseline, 베이스라인) | 지난 7일에 실제로 나온 숫자들 | 지난 7일 표의 숫자 7개(하루마다 주소 하나가 가장 많이 실패한 횟수) |
| 임계값(threshold, 쓰레숄드) | 한 주소의 하루 로그인 실패 횟수가 이 숫자 이상이면 알리기로 정한 숫자 | 5번(평소 기준의 최댓값 4 에 1 을 더함) |
| 알림(alert, 얼럿) | 한 주소의 하루 로그인 실패 횟수가 임계값 이상일 때 담당자에게 먼저 확인해 달라고 보내는 통지 | 한 주소가 하루에 로그인에 5번 이상 실패함 |

지난 7일의 숫자는 이렇게 생겼습니다(연습용 숫자입니다).

| 날짜 | 하루 최다 로그인 실패 횟수 |
|---|---|
| 10/26 | 2 |
| 10/27 | 3 |
| 10/28 | 1 |
| 10/29 | 4 |
| 10/30 | 2 |
| 10/31 | 3 |
| 11/1 | 2 |

- **평균**은 7개 숫자를 모두 더해 7로 나눈 값으로, 하루에 보통 몇 번인지 알려 줍니다. **최댓값**은 7개 중 가장 큰 숫자로, 가장 많았던 날이 몇 번인지 알려 줍니다.
- 이 수업에서는 **최댓값보다 1 큰 숫자**를 알림 기준으로 삼습니다. 지난 7일의 최댓값은 4번이므로 알림 기준은 5번입니다. 5번은 지난 7일에 한 번도 없었던 횟수라서, 평소에는 알림이 발생하지 않습니다.
- 「5번 이상」은 5번 · 6번 · 7번 …을 모두 포함합니다.
- 오늘 정한 기준은 이 규칙에서 나온 값 하나로 **고정**하고, 값을 바꿔 가며 비교하지 않습니다.

**🐼 판다스 문법 상자 — CSV 파일을 표로 읽기**

**<mark>`pd.read_csv(파일 이름)`</mark> 은 쉼표로 나뉜 CSV 파일을 열어 표로 만듭니다. 첫 줄은 헤더(열 이름)가 되고, 둘째 줄부터 한 줄이 한 행이 됩니다**

CSV 파일 안은 이렇게 생겼고(왼쪽), 읽으면 표가 됩니다(오른쪽). 어제 `pd.read_json` 으로 JSON 파일을 표로 읽은 것과 같은 일을 CSV 로 합니다.

| CSV 파일의 줄 | 표에서의 모양 |
|---|---|
| `date,failed_logins` | 헤더(열 이름 두 개): `date` · `failed_logins` |
| `2026-10-26,2` | 0번 행: `date` 가 2026-10-26, `failed_logins` 가 2 |
| `2026-10-27,3` | 1번 행: `date` 가 2026-10-27, `failed_logins` 가 3 |

```python
import pandas as pd                         # 판다스를 pd 라는 짧은 이름으로 불러온다
daily = pd.read_csv("baseline_logins.csv")  # CSV 파일을 읽어 표로 만든다 — 한 행이 하루

shape = daily.shape                         # 표의 크기를 (행 수, 열 수) 로 구한다
print(shape)                                # (7, 2) — 하루 7개(행), 열 2개
```

실행 결과:

```
(7, 2)
```

앞 칸에 이어서 쓰는 다음 칸입니다.

```python
print(daily)  # 표 전체를 출력한다 — 왼쪽 숫자는 판다스가 붙인 행 번호
```

실행 결과:

```
         date  failed_logins
0  2026-10-26              2
1  2026-10-27              3
2  2026-10-28              1
3  2026-10-29              4
4  2026-10-30              2
5  2026-10-31              3
6  2026-11-01              2
```

- 읽는 법: `(7, 2)` 는 **7행 2열**입니다. 하루가 7개(행), 열이 `date` · `failed_logins` 2개라는 뜻입니다. 왼쪽 숫자 0 ~ 6 은 판다스가 붙인 행 번호입니다.
- 어제 배운 `pd.read_json` 과 이름만 다르고 쓰는 모양은 같습니다. 파일이 JSON 이면 `read_json`, CSV 면 `read_csv` 를 씁니다.

**🐼 판다스 문법 상자 — 열의 평균 구하기**

**<mark>`열.mean()`</mark> 은 열에 있는 숫자들의 평균을 구합니다**

`daily["failed_logins"]` 는 숫자 7개로 이루어진 열(시리즈)입니다. 여기에 `.mean()` 을 쓰면 평균 숫자 하나를 리턴합니다.

- `mean`(민)은 줄임말이 아니라 영어 단어이고, 통계에서 「평균」을 뜻합니다. 모든 값을 더해 개수로 나눈 값입니다.

| 행 번호 | `daily["failed_logins"]` |
|---|---|
| 0 | 2 |
| 1 | 3 |
| 2 | 1 |
| 3 | 4 |
| 4 | 2 |
| 5 | 3 |
| 6 | 2 |

합은 2 + 3 + 1 + 4 + 2 + 3 + 2 = 17 이고, 17 ÷ 7 = 2.428… 입니다. 이 값을 아래에서 `round` 로 2.4 까지만 남깁니다.

```python
import pandas as pd                         # 판다스를 pd 라는 짧은 이름으로 불러온다
daily = pd.read_csv("baseline_logins.csv")  # CSV 파일을 읽어 표로 만든다 — 한 행이 하루

counts = daily["failed_logins"]             # failed_logins 열만 꺼낸다 — 하루 실패 횟수 7개가 나열된 열
average = counts.mean()                     # 7개의 평균을 구한다
rounded_average = round(average, 1)         # 소수 첫째 자리까지 반올림한다 (2.428571… → 2.4)
print(rounded_average)                      # 2.4 — 하루 평균 약 2.4번
```

실행 결과:

```
2.4
```

- 읽는 법: `2.4` 는 하루마다 가장 많이 실패한 주소의 실패 횟수 7개를 평균한 값입니다. 하루에 가장 많이 실패한 주소가 보통 약 2.4번 실패했다는 뜻입니다.
- `round`(라운드)는 판다스가 아니라 파이썬 기본 함수입니다. 영어로 「둥글게 만들다」라는 뜻이고, 숫자를 **반올림**합니다.
- `round(숫자, 1)` 의 `1` 은 소수 몇째 자리까지 남길지입니다. 평균 2.428571… 에서 소수 첫째 자리(4)까지 남기고, 그 아래 자리(2)가 5 보다 작아서 버려 2.4 가 됩니다.
- 열을 꺼내는 `daily["failed_logins"]` 는 어제 배운 `표["열 이름"]` 과 같습니다.

**🐼 판다스 문법 상자 — 열의 최댓값 구하기**

**<mark>`열.max()`</mark> 는 열에 있는 숫자 중 가장 큰 숫자를 구합니다**

- `max`(맥스)는 maximum(맥시멈, 최댓값)의 줄임말입니다.

```python
import pandas as pd                         # 판다스를 pd 라는 짧은 이름으로 불러온다
daily = pd.read_csv("baseline_logins.csv")  # CSV 파일을 읽어 표로 만든다 — 한 행이 하루

counts = daily["failed_logins"]             # failed_logins 열만 꺼낸다 — 하루 실패 횟수 7개가 나열된 열
maximum = counts.max()                      # 7개 중 가장 큰 값을 구한다
print(maximum)                              # 4 — 가장 많았던 날이 4번
```

실행 결과:

```
4
```

- 읽는 법: `4` 는 지난 7일 중 가장 많았던 날이 4번이라는 뜻입니다. 위 표의 3번 행입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_daily_failures` | 파일 경로 | 하루가 한 행인 표 |
| `average_failures` | 그 표 | 하루 평균 실패 횟수 |
| `maximum_failures` | 그 표 | 하루 최대 실패 횟수 |
| `make_limit` | 평소 최댓값 | 알림 기준(최댓값 + 1) |

- **직접 쓰는 곳은 여섯 군데**(번호 1 ~ 6)이고, 함수 네 개 안에 나뉘어 있습니다. 함수마다 1 ~ 2줄만 쓰고, `import` 와 실행 파일은 미리 채웠습니다.
  - `load_daily_failures`(1번): 파일을 표로 읽습니다.
  - `average_failures`(2 · 3번): 열을 꺼내 평균을 구합니다.
  - `maximum_failures`(4 · 5번): 열을 꺼내 최댓값을 구합니다.
  - `make_limit`(6번): 최댓값에 1을 더해 알림 기준을 정합니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 2-1 · 지난 7일의 로그인 실패로 평소 기준과 알림 기준 정하기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 로그인 실패가 몇 번이면 알려야 하는지 정해진 숫자가 없습니다.
- **그래서 만드는 것**: `baseline.py` 입니다.
  - 지난 7일 파일을 표로 읽습니다.
  - 하루 평균과 하루 최대를 구합니다.
  - 최대보다 1 큰 숫자를 알림 기준으로 정합니다.
- **실행하면**: 단계 1: 지난 7일 표, 단계 2: 평균, 단계 3: 최대, 단계 4: 알림 기준이 나옵니다.
- **현업에서는**: 알림 규칙을 만들 때는 며칠 치 평소 숫자부터 모아 기준을 정합니다. 근거가 남아 있으면 「왜 5번인가」에 답할 수 있습니다.

**🎯 할 일**

1. `baseline.py` · `day03_2-1_run.py` 두 파일을 만들고, `baseline.py` 의 네 함수에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>지난 7일 표</mark>(단계 1), <mark>하루 평균</mark>(단계 2), <mark>하루 최대</mark>(단계 3), <mark>알림 기준</mark>(단계 4)를 읽습니다.

**`baseline.py`**

```python
import pandas as pd                 # 판다스를 pd 라는 짧은 이름으로 불러온다

LOGIN_PATH = "baseline_logins.csv"  # 지난 7일의 하루 로그인 실패 횟수 파일 이름


def load_daily_failures(path):      # 파일 경로를 받는 함수
    """지난 7일의 하루 로그인 실패 횟수 파일을 표로 읽는다.
    평소 기준을 만들기 전에 맨 먼저 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. pd.read_csv 로 path 의 파일을 읽어 daily 에 담는다 (path 는 따옴표 없이 그대로 쓴다)
    return daily                    # 하루가 한 행인 표를 리턴한다


def average_failures(daily):        # 표를 받는 함수
    """지난 7일 표 숫자 7개의 평균을 구한다.
    「평소 하루에 몇 번쯤 실패하는가」를 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. daily 의 "failed_logins" 열을 꺼내 counts 에 담는다
    # 3. counts 의 평균을 .mean() 으로 구해 average 에 담는다
    return average                  # 평균을 리턴한다


def maximum_failures(daily):        # 표를 받는 함수
    """하루 최대 로그인 실패 횟수를 구한다.
    「평소 가장 많았던 날」이 얼마나 많았는지 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. daily 의 "failed_logins" 열을 꺼내 counts 에 담는다
    # 5. counts 의 최댓값을 .max() 로 구해 maximum 에 담는다
    return maximum                  # 최댓값을 리턴한다


def make_limit(maximum):            # 평소 최댓값을 받는 함수
    """평소 최댓값보다 1 큰 숫자를 알림 기준(임계값)으로 정한다.
    이 숫자 이상이면 평소보다 많다고 보고 알릴 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. maximum 에 1 을 더해 limit 에 담는다
    return limit                    # 알림 기준을 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 6번은 모두 함수 안이라 앞에 공백 4개입니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. 주석은 지우지 않습니다.
- 채우기 전에 실행하면 `NameError: name 'daily' is not defined` 오류가 납니다. 1번을 아직 안 썼기 때문입니다.

**`day03_2-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. 네 단계로 출력합니다.

```python
from baseline import load_daily_failures, average_failures, maximum_failures, make_limit, LOGIN_PATH  # 방금 만든 함수를 불러온다

daily = load_daily_failures(LOGIN_PATH)                                                               # 지난 7일 파일을 표로 읽는다
print("--- 단계 1: 지난 7일 하루 로그인 실패 횟수")                                                   # 단계 1 시작을 알리는 줄
print(daily)                                                                                          # 표를 출력한다

average = average_failures(daily)                                                                     # 하루 평균을 구한다
rounded_average = round(average, 1)                                                                   # 소수 첫째 자리까지 반올림한다
print("--- 단계 2: 하루 평균", rounded_average, "번")                                                 # 단계 2 시작을 알리는 줄과 평균

maximum = maximum_failures(daily)                                                                     # 하루 최대를 구한다
print("--- 단계 3: 하루 최대", maximum, "번")                                                         # 단계 3 시작을 알리는 줄과 최댓값

limit = make_limit(maximum)                                                                           # 알림 기준을 정한다
print("--- 단계 4: 알림 기준(임계값)", limit, "번 이상")                                              # 단계 4 시작을 알리는 줄과 알림 기준
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `baseline.py` · `day03_2-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `baseline.py` 에서 직접 쓰는 곳 여섯 군데를 씁니다. 위 판다스 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day03_2-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_2-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 네 단계입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 표 8줄이고, 단계 2 · 3 · 4는 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없습니다.
5. **[보고서]** `day03_am_report.md` 의 `## 2교시` › `### 문제 2-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 하루 평균과 최댓값, 알림 기준을 적어 주세요.
   - (나) 🔍 ① 지난 7일 중 평균(2.4번) 이상인 날은 며칠인가요? ② 평균(2.4번)을 알림 기준으로 했다면 지난 7일 중 알림이 발생했을 날은 며칠이고, 그 날들은 평소와 다른 날이었나요? ③ 그래서 알림 기준을 평균이 아니라 최댓값보다 1 큰 숫자(5번)로 정한 이유를 적어 주세요.
   - (다) 🔍 지난 7일 중 하루가 평소와 달랐다고 가정합니다(예: 어느 하루에 실패가 12번). 그러면 최댓값과 알림 기준(최댓값 + 1)이 어떻게 바뀌는지 적고, 바뀐 알림 기준을 쓰면 어떤 문제가 생기는지 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| CSV 파일을 표로 읽기 | `daily = pd.read_csv(path)` (`load_daily_failures`) |
| 열 꺼내기 | `counts = daily["failed_logins"]` |
| 평균 · 최댓값 | `average = counts.mean()` · `maximum = counts.max()` |
| 알림 기준 | `limit = maximum + 1` (`make_limit`) |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 같은 주소의 로그인 실패가 알림 기준(5번) 이상인 곳 찾기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「2교시에 정한 대로, 같은 주소가 하루에 로그인에 5번 이상 실패하면 담당자에게 알리기로 했습니다.
>
> 샘플 이벤트 57개 중에서 로그인 요청(`POST /login`)이 실패한 것이 모두 몇 개인지 세 주세요. 주소별로 몇 번씩 실패했는지 정리하고, 5번 이상 실패한 주소가 있으면 알려 주세요.」
> - **왜 중요한가**: <mark>로그인에 연달아 실패하는 것은 다른 사람이 비밀번호를 맞혀 보는 대표적인 모습입니다.</mark> 이벤트 수만 개를 사람이 하나씩 읽지 않고, 알림 기준(5번) 이상인 주소만 뽑아 보여 주면 담당자가 먼저 볼 곳이 정해집니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 2교시에서 「한 주소가 하루에 로그인에 5번 이상 실패하면 알린다」는 알림 기준(임계값)을 정했습니다. 이제 이벤트 57개에 그 기준을 적용합니다.
2. 찾는 순서는 세 단계입니다: ① **로그인 요청이면서 실패한 것**만 고르고, ② **접속 주소별로 센** 뒤, ③ **5번 이상인 주소**만 남깁니다.

### 📖 3.1 로그인 실패 규칙과 문법 상자 네 개

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

샘플에서 203.0.113.50 이 보낸 이벤트 전부입니다(9개, 표에서의 행 번호 포함).

| 행 번호 | 시각 | `action` | `result` | 로그인 요청인가 | 실패인가 | 둘 다인가 |
|---|---|---|---|---|---|---|
| 9 | 09:12:01 | `GET /login` | 성공 | 아니오 | 아니오 | 아니오 |
| 10 | 09:12:03 | `POST /login` | 실패 | 예 | 예 | **예** |
| 11 | 09:12:06 | `POST /login` | 실패 | 예 | 예 | **예** |
| 12 | 09:12:09 | `POST /login` | 실패 | 예 | 예 | **예** |
| 13 | 09:12:12 | `POST /login` | 실패 | 예 | 예 | **예** |
| 14 | 09:12:15 | `POST /login` | 실패 | 예 | 예 | **예** |
| 15 | 09:12:18 | `POST /login` | 성공 | 예 | 아니오 | 아니오 |
| 16 | 09:12:25 | `GET /admin` | 실패 | 아니오 | 예 | 아니오 |
| 17 | 09:12:27 | `GET /admin/users` | 실패 | 아니오 | 예 | 아니오 |

- `GET /login` 은 로그인 화면을 보여 달라는 요청이고, `POST /login` 은 아이디와 비밀번호를 보내는 요청입니다. 오늘은 `POST /login` 이 실패한 이벤트만 셉니다.
- SaaS 의 `login` 실패 1건(jiwoo, 02:14)은 11/5(목)에 다루므로 오늘은 세지 않습니다. 그래서 로그인 실패 이벤트는 5개입니다.

**알아 둘 것 — 열 꺼내기와 평균도 실무에서는 한 줄로 씁니다**

2교시에서 쓴 두 줄(`counts = daily["failed_logins"]` → `average = counts.mean()`)은 실무에서 아래 한 줄로 자주 씁니다. 같은 일입니다. 직접 쓰지 않고 읽기만 합니다. 자세한 쓰임은 다음에 차차 배웁니다.

```python
import pandas as pd                         # 판다스를 pd 라는 짧은 이름으로 불러온다
daily = pd.read_csv("baseline_logins.csv")  # CSV 파일을 읽어 표로 만든다 — 한 행이 하루

average = daily["failed_logins"].mean()     # 열 꺼내기와 평균을 한 줄로 쓴 모양 — 위 두 줄과 같은 결과
print(average)                              # 2.4285714285714284 — 소수점 아래가 길게 나오는 것은 round 를 쓰지 않았기 때문이다
```

실행 결과:

```
2.4285714285714284
```

**🐍 문법 상자 — `=` 와 `==`**

**`=` 는 오른쪽 값을 왼쪽 이름에 담고, `==` 는 두 값이 같은지 비교합니다. 한 줄에 같이 쓰면 비교(`==`)를 먼저 하고 그 결과를 `=` 로 담습니다**

```python
age = 20              # age 에 20을 담는다 (=)
is_adult = age == 20  # age 가 20과 같은지 비교하고(==), 그 결과를 is_adult 에 담는다(=)
print(is_adult)       # True
```

실행 결과:

```
True
```

- 읽는 법: 오른쪽의 비교 `age == 20` 을 먼저 계산하고, 그 결과 `True` 를 왼쪽 이름에 담습니다. `(age == 20)` 처럼 괄호를 넣어도 같은 뜻이고, 계산 순서가 눈에 보일 뿐입니다.
- `is_fail = results == "실패"` 를 `is_fail = results = "실패"` 로 잘못 쓰면 그 줄은 오류 없이 지나가지만 `is_fail` 이 열이 아니라 문자열 `"실패"` 가 되어, 다음 줄 `events[is_fail]` 에서 `KeyError` 가 납니다. 비교는 항상 `==` 로 씁니다.

**🐼 판다스 문법 상자 — 조건에 맞는 행만 걸러 내기**

**<mark>`표[조건]`</mark> 은 조건이 `True` 인 행만 남겨 새 표를 만듭니다**

`results == "실패"` 는 `result` 열의 값을 하나씩 `"실패"` 와 비교합니다. 같으면 `True`, 다르면 `False` 입니다. 결과는 `True` · `False` 로 된 열(시리즈)입니다. 이 열을 `표[…]` 안에 넣으면 `True` 인 행만 남습니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

results = events["result"]                       # result 열만 꺼낸다 — 성공 · 실패가 57개 나열된 열
is_fail = results == "실패"                      # 행마다 실패인지 비교해 True 또는 False 를 만든다
failed = events[is_fail]                         # True 인 행만 남겨 새 표(failed)를 만든다
failed_shape = failed.shape                      # 새 표의 크기를 꺼낸다
print(failed_shape)                              # (23, 6) — 실패한 이벤트 23개, 열은 그대로 6개
```

실행 결과:

```
(23, 6)
```

- 읽는 법: 실패한 이벤트 23개만 남았다는 뜻입니다. `(23, 6)` 은 23행 6열입니다(`.shape` 는 표의 (행 수, 열 수)를 알려 줍니다).

**🐼 판다스 문법 상자 — 두 조건을 함께 걸기**

**<mark>`조건A & 조건B`</mark> 는 행마다 두 조건을 모두 만족하면 `True`, 아니면 `False` 입니다. 이 열을 `표[…]` 에 넣으면 두 조건을 모두 만족하는 행만 남습니다**

위에서는 조건 하나(`results == "실패"`)로 걸렀습니다. 「로그인 요청이면서 실패」처럼 조건이 둘이면 각각 `True` · `False` 열로 만든 뒤 `&` 로 합칩니다(둘 다 `True` 인 행만 `True`). `and` 가 아니라 `&` 를 씁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

actions = events["action"]                       # action 열만 꺼낸다 — 무엇을 했는지가 57개 나열된 열
is_login = actions == "POST /login"              # 행마다 로그인 요청인지 비교해 True 또는 False 를 만든다
results = events["result"]                       # result 열만 꺼낸다 — 성공 · 실패가 57개 나열된 열
is_fail = results == "실패"                      # 행마다 실패인지 비교해 True 또는 False 를 만든다

both_true = is_login & is_fail                   # 행마다 두 조건이 모두 True 일 때만 True 가 된다
login_failures = events[both_true]               # True 인 행만 골라 새 표를 만든다
failure_shape = login_failures.shape             # 새 표의 크기를 꺼낸다
print(failure_shape)                             # (5, 6) — 로그인 실패 이벤트 5개, 열은 그대로 6개
```

실행 결과:

```
(5, 6)
```

- 읽는 법: `(5, 6)` 은 두 조건을 모두 만족하는 행이 5행(이벤트 5개)이라는 뜻입니다. 열은 그대로 6개입니다.
- 한 줄씩 따라가면 이렇습니다.

| 코드 | 만들어지는 것 |
|---|---|
| `is_login = actions == "POST /login"` | 로그인 요청인 행만 `True` |
| `is_fail = results == "실패"` | 실패인 행만 `True` |
| `both_true = is_login & is_fail` | 둘 다 `True` 인 행만 `True` |
| `login_failures = events[both_true]` | `True` 인 행만 모은 새 표 |

- `&` 는 파이썬에서 원래 다른 용도의 기호인데, 판다스는 열 두 개를 행마다 합치는 데 씁니다. `==` 가 열에서 행마다 비교하는 것과 같은 이유입니다.
- `and` 는 `True` 또는 `False` 하나씩 두 개를 이을 때만 씁니다. 열에는 값이 57개 있어서 `and` 로 이을 수 없고(`ValueError` 오류), 열을 이을 때는 `&` 를 씁니다. 4교시의 `result == "실패" and …` 는 값이 하나씩이라 `and` 를 씁니다.
- 비교를 `&` 로 바로 이을 때는 괄호가 꼭 필요합니다: `(a == 1) & (b == 2)`. `&` 가 `==` 보다 먼저 계산되기 때문입니다. 오늘은 비교를 이름에 먼저 담은 뒤 `is_login & is_fail` 로 이어서 괄호가 필요 없습니다.

**🐼 판다스 문법 상자 — 기준 이상인 것만 남기기**

**<mark>`counts >= 기준`</mark> 은 값이 기준 이상이면 `True` 인 열을 만들고, 그 열을 `counts[…]` 에 넣으면 `True` 인 것만 남습니다**

위에서 배운 `==` 처럼 `>=` 도 행마다 `True` · `False` 를 만듭니다. 아래 `counts` 는 주소별 실패 횟수입니다(왼쪽 인덱스가 주소, 오른쪽이 횟수). `counts >= 3` 은 주소마다 「3번 이상인가」를 `True` · `False` 로 만듭니다. 아래 코드는 실패한 이벤트를 주소별로 센 뒤 3번 이상인 주소를 남깁니다.

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

results = events["result"]                       # result 열만 꺼낸다 — 성공 · 실패가 57개 나열된 열
is_fail = results == "실패"                      # 행마다 실패인지 비교해 True 또는 False 를 만든다
failed = events[is_fail]                         # True 인 행만 골라 실패한 이벤트의 표를 만든다
counts = failed.groupby("ip").size()             # ip 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size) — 주소별 실패 횟수
print(counts)                                    # 주소와 실패 횟수가 줄마다 나온다
```

실행 결과:

```
ip
198.51.100.21    1
198.51.100.34    1
198.51.100.77    1
198.51.100.90    3
203.0.113.50     7
203.0.113.80     1
dtype: int64
```

앞 칸에 이어서 쓰는 다음 칸입니다.

```python
is_many = counts >= 3   # 주소마다 「3번 이상인가?」를 물어 True 또는 False 를 만든다
many = counts[is_many]  # True 인 주소만 남긴다
print(many)             # 3번 이상인 주소와 횟수
```

실행 결과:

```
ip
198.51.100.90    3
203.0.113.50     7
dtype: int64
```

- 읽는 법: 첫 번째 출력은 주소 6개의 실패 횟수이고, 두 번째 출력은 그중 3번 이상인 주소 2개입니다. 주소별 합이 14 인 것은 판정 서버 이벤트 9개의 `ip` 가 없어(`null`) 그룹에서 빠지기 때문입니다.
- `failed.groupby("ip").size()` 는 어제 두 줄로 나눠 배운 동작을 점(`.`)으로 이은 한 줄입니다. 왼쪽부터 차례로 읽습니다. ① `groupby("ip")` 가 ip 가 같은 행끼리 그룹을 만들고, ② 바로 이어서 `.size()` 가 그룹마다 행이 몇 개인지 셉니다. 이 수업에서는 점으로 이어 쓰는 것을 두 개까지만 씁니다.
- 이 예는 로그인뿐 아니라 실패 전체를 센 것이라 203.0.113.50 이 7번입니다. 문제에서는 로그인 요청의 실패만 세어 5번이 됩니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` | 파일 경로 | 이벤트 표(미리 채움) |
| `pick_login_failures` | 이벤트 표 | 로그인 요청이면서 실패한 행만 담은 표 |
| `count_by_ip` | 로그인 실패 표 | 주소별 실패 횟수(미리 채움) |
| `pick_alert_ips` | 주소별 횟수와 알림 기준 | 기준 이상인 주소와 횟수 |

- **직접 쓰는 곳은 여덟 군데**(번호 1 ~ 8)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `pick_login_failures`(1 ~ 6번): 로그인 요청인 행과 실패인 행을 `&` 로 이어 걸러 냅니다.
  - `pick_alert_ips`(7 · 8번): 횟수가 기준 이상인 주소만 남깁니다.
- 주소별로 묶어 세는 `count_by_ip` 는 어제 배운 `groupby().size()` 와 같아서 미리 채웠습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 3-1 · 같은 주소의 로그인 실패가 알림 기준(5번) 이상인 곳 찾기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 57개 이벤트 중 로그인 실패가 몇 개이고 어느 주소가 많은지 사람이 하나씩 읽어야 합니다.
- **그래서 만드는 것**: `login_detection.py` 입니다.
  - 로그인 요청이면서 실패한 이벤트를 골라냅니다.
  - 접속 주소별로 실패를 셉니다.
  - 횟수가 5번 이상인 주소만 남깁니다.
- **실행하면**: 단계 1: 로그인 실패 이벤트 수, 단계 2: 주소별 횟수, 단계 3: 알림 대상 주소가 나옵니다.
- **현업에서는**: 로그인 실패 규칙은 거의 모든 관제 화면에 있는 기본 규칙입니다. 알림이 난 주소를 막을지 판단하는 첫 단서가 됩니다.

**🎯 할 일**

1. `login_detection.py` · `day03_3-1_run.py` 두 파일을 만들고, `login_detection.py` 의 `pick_login_failures` · `pick_alert_ips` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>로그인 실패 이벤트 수</mark>(단계 1), <mark>주소별 횟수</mark>(단계 2), <mark>알림 대상 주소</mark>(단계 3)를 읽습니다.

**`login_detection.py`**

```python
import pandas as pd                               # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"            # 읽을 정규화 이벤트 파일 이름
LOGIN_LIMIT = 5                                   # 알림 기준: 평소 하루 최대가 4번이라 5번 이상이면 알린다


def load_events(path):                            # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                   # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                 # 이벤트 표를 리턴한다


def pick_login_failures(events):                  # 이벤트 표를 받는 함수
    """로그인 요청이 실패한 이벤트만 골라 새 표로 만든다.
    로그인 실패가 많은 주소를 조사하기 전에 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. events 의 "action" 열을 꺼내 actions 에 담는다
    # 2. actions 가 "POST /login" 과 같은지 비교한 결과(==)를 is_login 에 담는다
    # 3. events 의 "result" 열을 꺼내 results 에 담는다
    # 4. results 가 "실패" 와 같은지 비교한 결과(==)를 is_fail 에 담는다
    # 5. is_login & is_fail 로 두 조건을 합쳐 both_true 에 담는다 (둘 다 True 인 행만 True)
    # 6. events 에서 both_true 가 True 인 행만 골라 login_failures 에 담는다 (events[both_true])
    return login_failures                         # 로그인 실패 이벤트만 담은 표를 리턴한다


def count_by_ip(login_failures):                  # 로그인 실패 표를 받는 함수
    """로그인 실패를 접속 주소별로 센다.
    같은 주소가 반복해서 실패했는지 볼 때 쓴다.
    """
    counts = login_failures.groupby("ip").size()  # ip 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size)
    return counts                                 # 주소별 실패 횟수를 리턴한다


def pick_alert_ips(counts, limit):                # 주소별 횟수와 알림 기준을 받는 함수
    """실패 횟수가 알림 기준 이상인 주소만 골라 리턴한다.
    알림을 보낼 주소를 가릴 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. counts 가 limit 이상인지 비교한 결과(>=)를 is_many 에 담는다
    # 8. counts 에서 is_many 가 True 인 것만 골라 alert_ips 에 담는다 (counts[is_many])
    return alert_ips                              # 알림 기준 이상인 주소와 횟수를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 ~ 8번은 모두 함수 안이라 앞에 공백 4개입니다.
- 미리 채운 `count_by_ip` 의 `groupby("ip").size()` 는 3.1 에서 본 것처럼 두 동작을 점으로 이은 한 줄입니다. ① `groupby("ip")` 로 ip 가 같은 행끼리 그룹을 만들고 ② `.size()` 로 그룹마다 행 수를 셉니다.
- 각 번호 주석 바로 아래에 새 줄을 만들어 그 번호의 코드를 한 줄 씁니다. 주석은 지우지 않습니다.
- 채우기 전에 실행하면 `NameError: name 'login_failures' is not defined` 오류가 납니다. 1 ~ 6번을 아직 안 썼기 때문입니다.

**`day03_3-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `len(표)` 는 표의 행 수입니다.

```python
from login_detection import load_events, pick_login_failures, count_by_ip, pick_alert_ips, EVENTS_PATH, LOGIN_LIMIT  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                              # 이벤트 파일을 표로 읽는다
login_failures = pick_login_failures(events)                   # 로그인 실패 이벤트만 골라낸다
failure_count = len(login_failures)                            # 로그인 실패가 모두 몇 개인지 센다
print("--- 단계 1: 로그인 실패 이벤트", failure_count, "개")   # 단계 1 시작을 알리는 줄과 개수

counts = count_by_ip(login_failures)                           # 주소별로 실패 횟수를 센다
print("--- 단계 2: 주소별 로그인 실패 횟수")                   # 단계 2 시작을 알리는 줄
print(counts)                                                  # 주소별 횟수를 출력한다

alert_ips = pick_alert_ips(counts, LOGIN_LIMIT)                # 알림 기준 이상인 주소만 고른다
print("--- 단계 3: 알림 기준", LOGIN_LIMIT, "번 이상인 주소")  # 단계 3 시작을 알리는 줄과 알림 기준
print(alert_ips)                                               # 알림을 보낼 주소를 출력한다
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `login_detection.py` · `day03_3-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `login_detection.py` 에서 직접 쓰는 곳 여덟 군데를 씁니다. 3.1 의 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day03_3-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_3-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 세 단계입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없고, 단계 2와 단계 3은 각각 3줄입니다.
5. **[보고서]** `day03_am_report.md` 의 `## 3교시` › `### 문제 3-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 로그인 실패 이벤트 수와 알림 대상 주소, 그 횟수를 적어 주세요.
   - (나) 🔍 203.0.113.50 이 알림 대상이 되었습니다. 공격이라고 확정할 수 있는지 적고, 3.1 의 표에서 시각 간격과 성공 뒤에 요청한 경로를 보고 의심스러운 점을 적어 주세요. 그리고 5번 실패가 공격인지 판단하려면 이 표에 없는 정보 중 무엇이 더 필요한지 한 가지 적어 주세요(예: 어떤 사용자 이름으로 시도했는지).
   - (다) 🔍 한 주소가 로그인에 4번 실패하고 5번째에 성공했습니다. 이 규칙(실패 5번 이상)은 이 접속을 알림으로 잡을까요? 잡는다 · 못 잡는다와 이유를 적고, 못 잡는다면 담당자가 놓치는 정보가 무엇인지 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 로그인 요청인 행 | `actions = events["action"]` → `is_login = actions == "POST /login"` |
| 실패인 행 | `results = events["result"]` → `is_fail = results == "실패"` |
| 둘 다인 행 | `both_true = is_login & is_fail` → `login_failures = events[both_true]` |
| 기준 이상인 주소 | `is_many = counts >= limit` → `alert_ips = counts[is_many]` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 이벤트의 유형 정하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「알림이 와도 담당자는 어떤 유형의 일인지부터 알아야 다음에 할 일을 정합니다. 이벤트마다 유형을 분류하고, 유형별로 몇 개씩인지 보여 주세요.
>
> 오늘은 두 유형만 구분하면 됩니다. 하나는 로그인에 실패한 것, 다른 하나는 관리자 경로에 접근했다가 실패한 것입니다. 나머지 실패는 「기타 실패」, 성공은 「정상」으로 묶어 주세요.」
> - **왜 중요한가**: <mark>알림이 100개 와도 유형을 모르면 처음부터 하나씩 읽어야 합니다.</mark> 유형별 개수를 보면 비정상 로그인이 많은지, 비인가 접근이 많은지 보고 어디부터 볼지 정할 수 있습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 3교시에서는 「로그인 실패」 하나만 찾았습니다. 실제 관제에서는 로그인 실패 · 관리자 경로 접근 · 요청 급증처럼 평소와 다른 일이 여러 유형으로 한꺼번에 들어옵니다.
2. 이벤트마다 **유형 이름**을 정해 두면, 유형별로 세고 유형별로 다르게 대응할 수 있습니다.

### 📖 4.1 이벤트 유형과 오늘 쓰는 규칙

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문은 없습니다. 판다스 문법 상자의 코드는 눈으로 읽으면 됩니다.

관제에서 알리는 일은 다섯 가지 유형으로 나눕니다. 오늘은 표의 첫 두 가지(비정상 로그인 · 비인가 접근)만 구분하고, 나머지 실패는 「기타 실패」, 성공은 「정상」으로 모읍니다(나머지 유형은 오후와 11/5(목)에 다룹니다).

| 유형 | 로그에서 보이는 모양 | 언제 |
|---|---|---|
| 비정상 로그인 | 로그인 요청이 실패함 | 오늘 |
| 비인가 접근 | 관리자 경로(`/admin`)를 요청했다가 실패함 | 오늘 |
| 트래픽 급증 | 짧은 시간에 요청이 많이 들어옴 | 오후 |
| SaaS 이상 사용 | 평소와 다른 서비스 사용(대량 내려받기 등) | 11/5(목) |
| 악성 행위 징후 | 없는 경로를 차례로 확인하는 시도 등 | 11/5(목) |

오늘 유형 이름을 정하는 순서입니다. **1번 규칙부터 차례로 확인해서, 처음 맞는 규칙의 유형 이름을 붙이고 멈춥니다.** 예: 결과가 실패이고 행동이 `POST /login` 인 이벤트는 1번에서 맞으므로 「비정상 로그인」이고, 2번부터는 보지 않습니다.

| 순서 | 조건 | 유형 이름 |
|---|---|---|
| 1 | 결과가 실패이고 행동이 `POST /login` | 비정상 로그인 |
| 2 | 결과가 실패이고 행동에 `/admin` 이 들어 있음 | 비인가 접근 |
| 3 | 결과가 실패(위 두 가지가 아님) | 기타 실패 |
| 4 | 그 밖(성공) | 정상 |

- 유형 이름은 이벤트 **한 건**에 붙이는 이름입니다.
- 로그인에 1번만 실패한 이벤트도 「비정상 로그인」입니다. 알림을 낼지는 3교시처럼 실패 횟수로 따로 정합니다.
- 「정상」은 결과가 성공이라는 유형 이름이며, 공격이 아니라는 뜻이 아닙니다. 3.1 표에서 본 203.0.113.50 의 15번 행(`POST /login` 성공)도 유형은 「정상」이고, 실패 뒤 성공이 먼저 살펴볼 일인지는 그 전후의 이벤트를 함께 봐서 판단합니다.
- SaaS 로그의 로그인 실패(jiwoo, 행동 `login`)는 행동이 `POST /login` 이 아니라서 1번 규칙에 걸리지 않고 「기타 실패」가 됩니다.
- 샘플에서 실패한 이벤트는 모두 23개입니다.
- 규칙의 `and` 는 이벤트 한 건의 값 하나씩을 이으므로 `and` 를 씁니다. 3교시에서 표의 열끼리 이을 때만 `&` 를 썼습니다.

**🐍 문법 상자 — 문자열 안에 다른 문자열이 있는지 `in`**

**<mark>`작은 문자열 in 큰 문자열`</mark> 은 큰 문자열 안에 작은 문자열이 들어 있으면 `True`, 없으면 `False` 입니다**

`==` 는 문자열 전체가 같아야 `True` 이지만, `in` 은 일부만 들어 있어도 `True` 입니다. 그래서 `GET /admin` 도 `GET /admin/users` 도 `"/admin" in action` 으로 한 번에 찾습니다.

```python
action = "GET /admin/users"                 # 이벤트의 action 값 예
has_admin = "/admin" in action              # action 안에 /admin 이 있는지 True 또는 False 로 구한다
print(has_admin)                            # True

other_action = "GET /login"                 # /admin 이 없는 action 값 예
has_admin_other = "/admin" in other_action  # other_action 안에 /admin 이 있는지 구한다
print(has_admin_other)                      # False
```

실행 결과:

```
True
False
```

- 읽는 법: 첫 번째 출력은 `GET /admin/users` 안에 `/admin` 이 있어서 `True`, 두 번째 출력은 `GET /login` 안에 없어서 `False` 입니다.
- `if` 조건에 그대로 씁니다(`if "/admin" in action:`). `== True` 는 붙이지 않습니다. `for … in` 과는 다른 쓰임입니다.

**🐼 판다스 문법 상자 — 표를 딕셔너리 리스트로 바꾸기**

**<mark>`표.to_dict("records")`</mark> 는 표의 행을 딕셔너리 하나씩으로 바꾸고, 그 딕셔너리들을 리스트로 리턴합니다. 열 이름은 키가 되고, 그 행의 데이터는 그 키의 값이 됩니다**

이벤트 표의 한 행이 딕셔너리 하나로 바뀌므로, 이후에는 판다스가 아니라 3과목에서 쓰던 `for` 와 `event["키"]` 로 하나씩 처리할 수 있습니다.

| 표의 0번 행 | `to_dict("records")` 로 바꾼 뒤 |
|---|---|
| `time` 열이 2026-11-02 02:14:08 | `{"time": "2026-11-02 02:14:08", …}` |
| `source` 열이 saas | `"source": "saas"` |
| `action` 열이 login, `result` 열이 실패 | `"action": "login", "result": "실패"` |

```python
import pandas as pd                              # 판다스를 pd 라는 짧은 이름으로 불러온다
events = pd.read_json("normalized_events.json")  # 파일 속 이벤트 57개를 표 한 개(events)로 읽는다 — 행 하나가 이벤트 하나

event_list = events.to_dict("records")           # 표를 「한 행이 딕셔너리 하나」인 리스트로 바꾼다
first_event = event_list[0]                      # 첫 번째 딕셔너리(표의 0번 행)를 꺼낸다
print(first_event)                               # 열 이름이 키, 그 행의 값이 값이 된 딕셔너리
```

실행 결과:

```
{'time': '2026-11-02 02:14:08', 'source': 'saas', 'user': 'jiwoo', 'ip': '203.0.113.80', 'action': 'login', 'result': '실패'}
```

- 읽는 법: 출력은 0번 행 하나가 딕셔너리로 바뀐 모양입니다. 키는 열 이름 6개이고 값은 그 행의 값입니다.
- `"records"` 는 정해진 문구라서 그대로 씁니다. 빼거나 다른 문구를 쓰면 행마다 딕셔너리 하나인 리스트가 만들어지지 않습니다.
- `classify_event` 함수는 이벤트 하나의 행동과 결과를 전달받아 규칙(`if`)을 적용합니다. 그래서 표를 딕셔너리 리스트로 바꿔 이벤트를 하나씩 꺼냅니다. `if` 는 값 하나씩만 판단하기 때문입니다.
- 미리 채운 `counts.get(type_name, 0) + 1` 은 처음 보는 유형이면 0 에서 시작해 1 을 더한다는 뜻입니다.

**한 장 정리**

| 함수 | 받는 것 | 리턴하는 것 |
|---|---|---|
| `load_events` | 파일 경로 | 이벤트 표(미리 채움) |
| `classify_event` | 이벤트 하나의 행동과 결과 | 유형 이름(`비정상 로그인` · `비인가 접근` · `기타 실패` · `정상`) |
| `count_types` | 이벤트 표 | `{유형: 개수}` 딕셔너리 |

- **직접 쓰는 곳은 다섯 군데**(번호 1 ~ 5)이고, 함수 두 개 안에 나뉘어 있습니다.
  - `classify_event`(1 ~ 4번): 위 순서대로 1번 · 2번 규칙을 `if` 로 씁니다. 나머지 두 규칙은 미리 채웠습니다.
  - `count_types`(5번): 표를 딕셔너리 리스트로 바꿉니다. 하나씩 꺼내 세는 줄은 미리 채웠습니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 4-1 · 이벤트의 유형을 정하고 유형별로 세기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: 이벤트 57개는 성공 · 실패만 나뉘어 있어서, 실패가 어떤 일인지 알 수 없습니다.
- **그래서 만드는 것**: `classify.py` 입니다.
  - 이벤트 하나의 행동과 결과로 유형 이름을 정합니다.
  - 유형 이름별로 몇 개인지 셉니다.
- **실행하면**: 단계 1: 유형별 이벤트 수(4줄), 단계 2: 전체 이벤트 수가 나옵니다.
- **현업에서는**: 알림에 유형 이름이 적혀 있으면 담당자가 그 유형의 처리 절차(비밀번호 초기화, 주소 차단 등)를 바로 찾습니다.

**🎯 할 일**

1. `classify.py` · `day03_4-1_run.py` 두 파일을 만들고, `classify.py` 의 `classify_event` · `count_types` 에서 직접 쓰는 곳을 씁니다.
2. 실행해서 <mark>유형별 이벤트 수</mark>(단계 1)와 <mark>전체 이벤트 수</mark>(단계 2)를 읽습니다.

**`classify.py`**

```python
import pandas as pd                                                 # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                              # 읽을 정규화 이벤트 파일 이름
TYPE_ORDER = ["비정상 로그인", "비인가 접근", "기타 실패", "정상"]  # 결과를 보여 줄 유형 순서


def load_events(path):                                              # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                                     # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                                   # 이벤트 표를 리턴한다


def classify_event(action, result):                                 # 행동과 결과를 받는 함수
    """이벤트 하나의 유형 이름을 정한다.
    알림이 온 이벤트가 어떤 유형의 일인지 담당자가 바로 알 수 있게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. if 로 시작한다: result 가 "실패" 이고(and) action 이 "POST /login" 과 같으면
    # 2.   그 if 안쪽에서 "비정상 로그인" 을 리턴한다
    # 3. if 로 시작한다: result 가 "실패" 이고(and) "/admin" in action 이 True 이면
    # 4.   그 if 안쪽에서 "비인가 접근" 을 리턴한다
    if result == "실패":                                            # 위 두 유형이 아닌 실패이면
        return "기타 실패"                                          # 기타 실패로 분류한다
    return "정상"                                                   # 실패가 아니면 정상이다


def count_types(events):                                            # 이벤트 표를 받는 함수
    """유형별 이벤트 수를 {유형: 개수} 딕셔너리로 센다.
    어떤 유형의 일이 얼마나 있는지 한눈에 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. events.to_dict("records") 로 표를 딕셔너리 리스트로 바꿔 event_list 에 담는다
    counts = {}                                                     # 유형별 횟수를 담을 딕셔너리
    for event in event_list:                                        # 이벤트를 하나씩 꺼낸다
        action = event["action"]                                    # 그 이벤트의 행동
        result = event["result"]                                    # 그 이벤트의 결과
        type_name = classify_event(action, result)                  # 유형 이름을 정한다
        counts[type_name] = counts.get(type_name, 0) + 1            # counts 에 이 유형이 있으면 그 값을, 없으면 0 을 꺼내 1 을 더하고 다시 저장한다
    return counts                                                   # 유형별 횟수를 리턴한다
```

- 들여쓰기는 미리 채운 줄에 맞춥니다. 1 · 3번은 함수 안이라 앞에 공백 4개이고, 2 · 4번의 `return` 은 `if` 안쪽이라 8개이며, 5번은 공백 4개입니다.
- 번호 주석이 연달아 붙어 있어도, 주석 사이마다 줄을 끼워 넣어 각 주석 바로 아래 줄에 그 번호의 코드를 하나씩 씁니다.
- 채우기 전에 실행하면 `NameError: name 'event_list' is not defined` 오류가 납니다. 5번을 아직 안 썼기 때문입니다.

**`day03_4-1_run.py`** — 그대로 붙여 넣습니다. 학생이 쓰는 줄은 없습니다. `.values()` 는 딕셔너리의 값(개수)만 꺼내고, `sum(…)` 은 그 숫자를 모두 더합니다.

```python
from classify import load_events, count_types, EVENTS_PATH, TYPE_ORDER  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                       # 이벤트 파일을 표로 읽는다
counts = count_types(events)                                            # 유형별로 센다
print("--- 단계 1: 유형별 이벤트 수")                                   # 단계 1 시작을 알리는 줄
for type_name in TYPE_ORDER:                                            # 정해 둔 유형 순서대로 꺼낸다
    count = counts.get(type_name, 0)                                    # 그 유형의 개수(없으면 0)
    print(type_name, count)                                             # 유형과 개수를 출력한다

values = counts.values()                                                # 유형별 개수만 꺼낸다
total = sum(values)                                                     # 모든 유형의 개수를 더한다
print("--- 단계 2: 전체 이벤트", total, "개")                           # 단계 2 시작을 알리는 줄과 전체 개수
```

**순서**

1. **[VS Code 또는 터미널]** 파일 `classify.py` · `day03_4-1_run.py` 를 만들어 위 코드를 붙여 넣습니다.
2. **[VS Code]** `classify.py` 에서 직접 쓰는 곳 다섯 군데를 씁니다. 4.1 의 규칙 순서와 문법 상자를 보고 씁니다.
3. **[터미널]** `pwd` 의 결과가 `anomaly_detection` 으로 끝나는지 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   pwd
   python day03_4-1_run.py
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_4-1_run.py` 파이썬으로 실행 파일 실행
4. 출력은 두 단계입니다. 제목 줄(`--- 단계 …`)은 줄 수에 넣지 않습니다. 단계 1은 4줄이고, 단계 2는 숫자가 제목 줄에 함께 나오므로 그 아래 줄이 없습니다.
5. **[보고서]** `day03_am_report.md` 의 `## 4교시` › `### 문제 4-1` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 유형별 이벤트 수를 적어 주세요.
   - (나) 🔍 「기타 실패」(결과가 실패이면서 `POST /login` 도 아니고 `/admin` 도 없는 이벤트)는 실패한 유형 중 15개로 가장 많습니다. 샘플 이벤트에서 `source` 가 `server` 인 이벤트 하나와 `web` 인 이벤트 하나를 찾아, 각각 `action` 과 함께 적어 주세요(예: `server` 의 `ACCOUNT:CHANGE`, `web` 의 `GET /.env` 처럼 규칙 1 · 2번에 걸리지 않는 것). 그리고 이 둘이 같은 이름 「기타 실패」로 묶여 있으면 담당자가 무엇을 하기 어려운지 적어 주세요.
   - (다) 🔍 유형 규칙은 위에서부터 차례로 보고 먼저 맞는 것으로 정합니다. 「기타 실패」(결과가 실패이면 맞음)를 맨 위로 옮겼다고 합시다. 그러면 「비정상 로그인」 · 「비인가 접근」 · 「기타 실패」 이벤트는 각각 몇 개가 될까요? 그리고 그때 담당자가 구분하지 못하게 되는 것은 무엇인가요?

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 비정상 로그인 | `if result == "실패" and action == "POST /login":` → `return "비정상 로그인"` |
| 비인가 접근 | `if result == "실패" and "/admin" in action:` → `return "비인가 접근"` |
| 표를 리스트로 | `event_list = events.to_dict("records")` |
| 유형별 세기 | `counts[type_name] = counts.get(type_name, 0) + 1` (미리 채움) |

---

### 마무리 · 오전 작업 확인하기

오전 작업을 깃허브에 올리는 일은 오후 6교시 마지막에 한 번에 합니다. 오전에는 파일이 모두 있는지만 확인합니다.

**순서**

1. **[터미널]** `anomaly_detection` 폴더에서 오늘 만든 파일이 있는지 확인합니다.
   ```bash
   pwd
   ls
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기
   - `baseline.py` · `login_detection.py` · `classify.py` · `day03_2-1_run.py` · `day03_3-1_run.py` · `day03_4-1_run.py` · `normalized_events.json` · `baseline_logins.csv` 와 이 안내 · 보고서 두 파일이 보여야 합니다.
2. **[보고서]** `day03_am_report.md` 의 2 · 3 · 4교시 칸에서 `답:` 뒤가 비어 있는 질문이 없는지 봅니다. 못 적은 칸은 `모름 — 막힌 곳: …` 으로 적습니다.

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 지난 7일 숫자로 평소 기준을 구하고 알림 기준(5번)을 정했다 | 오전 2-1 |
| 같은 주소의 로그인 실패가 알림 기준(5번) 이상인 곳을 찾았다 | 오전 3-1 |
| 이벤트의 유형을 정하고 유형별로 셌다 | 오전 4-1 |

오후에는 분 단위로 요청 수를 세어 **요청이 갑자기 늘어난 때**(트래픽 급증)를 찾고, 오전의 알림을 한 파일로 모읍니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_2-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 네 함수입니다.

① `load_daily_failures` 안

```python
    daily = pd.read_csv(path)  # CSV 파일을 읽어 표로 만든다 — 한 행이 하루
```

② `average_failures` 안

```python
    counts = daily["failed_logins"]  # failed_logins 열만 꺼낸다 — 하루 실패 횟수 7개가 나열된 열
    average = counts.mean()          # 7개의 평균을 구한다
```

③ `maximum_failures` 안

```python
    counts = daily["failed_logins"]  # failed_logins 열만 꺼낸다 — 하루 실패 횟수 7개가 나열된 열
    maximum = counts.max()           # 7개 중 가장 큰 값을 구한다
```

④ `make_limit` 안

```python
    limit = maximum + 1  # 평소 최댓값보다 1 큰 숫자를 기준으로 삼는다
```

**결과**

- (가) 출력은 다음과 같고, 하루 평균은 <mark>**2.4번**</mark>, 최댓값은 <mark>**4번**</mark>, 알림 기준은 <mark>**5번 이상**</mark>입니다.

```
--- 단계 1: 지난 7일 하루 로그인 실패 횟수
         date  failed_logins
0  2026-10-26              2
1  2026-10-27              3
2  2026-10-28              1
3  2026-10-29              4
4  2026-10-30              2
5  2026-10-31              3
6  2026-11-01              2
--- 단계 2: 하루 평균 2.4 번
--- 단계 3: 하루 최대 4 번
--- 단계 4: 알림 기준(임계값) 5 번 이상
```

- (나) ① 평균(2.4번) 이상인 날은 10/27(3번) · 10/29(4번) · 10/31(3번)으로 7일 중 **3일**입니다.
  - ② 평균을 기준으로 하면 지난 7일 중 위 3일에 알림이 발생하고, 이 3일은 모두 평소와 같은 평범한 날입니다. 평범한 날에도 알림이 나서 담당자가 알림에 익숙해지고 진짜 알림도 무시하게 됩니다.
  - ③ 최댓값보다 1 큰 숫자(5번)를 기준으로 하면 지난 7일 중 알림이 발생한 날이 **0일**입니다. 평소에는 알림이 나지 않고, 평소보다 많아졌을 때만 알림이 나게 하려는 것입니다.
- (다) 12번이 섞이면 최댓값은 4번에서 12번이 되고, 알림 기준은 5번에서 13번이 됩니다. 그러면 5 ~ 12번 실패는 알림이 나지 않아 놓칩니다.
  - 7일 중 하루만 평소와 달라도 평소 최댓값이 커져서 알림 기준이 높아집니다. 지난 7일 표가 7일 치뿐이라 그 하루의 영향을 크게 받습니다.
  - 그래서 지난 7일 표에 평소와 다른 날이 섞이지 않았는지 확인하고, 며칠 쓴 뒤에는 새 데이터로 다시 구합니다.

**왜**

- <mark>평소를 구해서 기준을 정하면 숫자에 근거가 생깁니다.</mark> 「왜 5번인가」에 「지난 7일 중 가장 많은 날이 4번이었다」로 답할 수 있습니다.

**자주 틀리는 곳**

- 열 이름을 틀리면 `KeyError` 오류가 납니다. 열 이름은 파일 첫 줄의 `failed_logins` 와 정확히 같아야 합니다.
  - 실행하면 다음 오류가 납니다(<mark>`KeyError: 'failed_login'`</mark> 처럼 열 이름이 나오면 이 실수입니다).

```
Traceback (most recent call last):
KeyError: 'failed_login'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "…/anomaly_detection/day03_2-1_run.py", line 7, in <module>
    average = average_failures(daily)  # 하루 평균을 구한다
  File "…/anomaly_detection/baseline.py", line 22, in average_failures
    counts = daily["failed_login"]  # 열 이름을 잘못 썼다
KeyError: 'failed_login'
```

  - 줄 번호는 사람마다 다릅니다.
- `counts.mean` 처럼 괄호를 빼면 값이 아니라 메서드가 담겨서, 실행 파일의 `round(average, 1)` 에서 `TypeError` 가 납니다. `mean` 과 `max` 는 뒤에 괄호를 붙여 호출하는 메서드입니다.

**관제에서는**

- 알림 기준은 몇 주마다 최근 데이터로 다시 구합니다. 기준을 구한 날짜와 이유를 남겨 두어야 나중에 바꿀 때 근거가 됩니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_3-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `pick_login_failures` 안

```python
    actions = events["action"]           # action 열만 꺼낸다 — 무엇을 했는지가 57개 나열된 열
    is_login = actions == "POST /login"  # 행마다 로그인 요청인지 비교해 True 또는 False 를 만든다
    results = events["result"]           # result 열만 꺼낸다 — 성공 · 실패가 57개 나열된 열
    is_fail = results == "실패"          # 행마다 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_login & is_fail       # 행마다 「로그인 요청이면서 실패」일 때만 True 가 된다
    login_failures = events[both_true]   # True 인 행만 골라 새 표를 만든다
```

② `pick_alert_ips` 안

```python
    is_many = counts >= limit    # 주소마다 「횟수가 기준 이상인가?」를 물어 True 또는 False 를 만든다
    alert_ips = counts[is_many]  # True 인 주소만 남긴다
```

**결과**

- (가) 출력은 다음과 같고, 로그인 실패 이벤트는 <mark>**5개**</mark>, 알림 대상은 <mark>**203.0.113.50(5번)**</mark> 한 주소입니다.

```
--- 단계 1: 로그인 실패 이벤트 5 개
--- 단계 2: 주소별 로그인 실패 횟수
ip
203.0.113.50    5
dtype: int64
--- 단계 3: 알림 기준 5 번 이상인 주소
ip
203.0.113.50    5
dtype: int64
```

- (나) 203.0.113.50 이 공격이라고 확정할 수는 없습니다. 다만 의심할 단서는 여럿 있습니다.
  - 단서: 일정한 3초 간격으로 5번 연달아 실패했고(자동 입력처럼 보임), 6번째에 로그인에 성공한 뒤 곧바로 관리자 경로(`/admin` · `/admin/users`)를 두 번 요청했습니다.
  - 이 표에 없는 더 필요한 정보: 그 주소가 회사 직원의 주소인지, 로그인에 성공한 계정이 누구인지입니다(웹 서버 로그에는 계정 이름이 없으므로 판정 서버 · SaaS 로그와 시각을 맞춰 봐야 합니다).
  - 알림은 「먼저 살펴볼 곳」이고 공격의 확정이 아닙니다.
- (다) 알림이 나지 않습니다.
  - 이 규칙은 실패한 이벤트만 주소별로 세어 5번 이상인지 봅니다. 4번 실패한 주소는 기준(5번)보다 적고, 5번째의 성공은 세는 대상이 아닙니다. 그래서 그 주소 하나만 있다면 단계 3 이 비어 알림이 나지 않습니다(샘플에서는 203.0.113.50 이 따로 있어 단계 3 에 나옵니다).
  - 그래서 담당자는 이 접속이 있었다는 것을 알림으로는 알 수 없습니다. 알림이 없다는 것은 안전하다는 뜻이 아니라 「이 규칙에 걸리지 않았다」는 뜻일 뿐입니다.
  - 알림 기준(5번) 미만으로 천천히 시도하는 공격도 이 규칙에는 걸리지 않습니다. 그래서 「알림 없음 ≠ 안전」입니다.

**왜**

- <mark>로그인 실패 5번을 사람이 57개 이벤트에서 직접 찾으면 놓치기 쉽습니다.</mark> 조건 두 개와 주소별 센 값을 이어 쓰면 몇 줄로 끝나고, 이벤트가 수만 개여도 같은 코드입니다.

**자주 틀리는 곳**

- 두 조건을 이을 때 `&` 대신 `and` 를 쓰면 `ValueError` 오류가 납니다.
  - 실행하면 다음 오류가 납니다(<mark>`The truth value of a Series is ambiguous`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day03_3-1_run.py", line 4, in <module>
    login_failures = pick_login_failures(events)  # 로그인 실패 이벤트만 골라낸다
  File "…/anomaly_detection/login_detection.py", line 29, in pick_login_failures
    both_true = is_login and is_fail  # & 대신 and 를 썼다
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

  - 줄 번호는 사람마다 다릅니다.
- `GET /login` 까지 세는 실수가 있습니다. 이 규칙은 로그인 정보를 보내는 `POST /login` 만 셉니다.

**관제에서는**

- 로그인 실패 규칙의 알림에는 보통 주소와 횟수, 실패 뒤 성공이 있었는지가 함께 표시됩니다. 성공이 있었다면 계정이 탈취됐을 수 있어 우선순위가 올라갑니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day03_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python day03_4-1_run.py` 파이썬으로 실행 파일 실행

**채운 코드** (한 예) — 직접 쓰는 곳은 두 함수입니다.

① `classify_event` 안

```python
    if result == "실패" and action == "POST /login":  # 로그인 요청이 실패했으면
        return "비정상 로그인"                        # 비정상 로그인으로 분류한다
    if result == "실패" and "/admin" in action:       # 관리자 경로 요청이 실패했으면
        return "비인가 접근"                          # 비인가 접근으로 분류한다
```

② `count_types` 안

```python
    event_list = events.to_dict("records")  # 표를 딕셔너리 리스트로 바꾼다 — 이벤트 하나가 딕셔너리 하나
```

**결과**

- (가) 출력은 다음과 같고, 비정상 로그인 <mark>**5**</mark>, 비인가 접근 <mark>**3**</mark>, 기타 실패 <mark>**15**</mark>, 정상 <mark>**34**</mark>(합계 57)입니다.

```
--- 단계 1: 유형별 이벤트 수
비정상 로그인 5
비인가 접근 3
기타 실패 15
정상 34
--- 단계 2: 전체 이벤트 57 개
```

- (나) 「기타 실패」 15개에는 서로 다른 일이 섞여 있습니다.
  - `server`(판정 서버) 실패 9개: gaeun 의 `ACCOUNT:CHANGE` 3번, dami 의 `SALES:QUERY` 3번과 `SALES:CHANGE` 1번, seoyeon 의 `SETTLE:QUERY` 1번과 `SALES:CHANGE` 1번입니다.
  - `web`(웹 서버) 실패 5개: 198.51.100.90 이 09:20:10 ~ 09:20:12 에 `/.env` · `/wp-login.php` · `/phpmyadmin` 을 차례로 요청한 것 3개와, 페이지 요청 실패 2개(`/board/99` · `/report`)입니다.
  - `saas`(SaaS) 실패 1개: jiwoo 의 `login` 입니다.
  - 하나로 묶으면 이 일들이 모두 같은 유형으로 보여서, 담당자가 대응을 정할 수 없습니다. 예를 들어 같은 사용자의 계정 변경이 3번 실패한 것과 `/.env` · `/wp-login.php` · `/phpmyadmin` 을 차례로 요청한 것은 대응이 전혀 다릅니다. 그래서 11/5(목)에 유형을 더 나눕니다.
- (다) 「기타 실패」를 맨 위에 두면 결과가 실패인 이벤트 23개가 모두 먼저 맞아서 **기타 실패 23개**가 되고, 비정상 로그인과 비인가 접근은 **0개**가 됩니다. 정상은 34개 그대로입니다.
  - 담당자는 로그인 실패와 관리자 경로 요청 실패를 구분할 수 없게 되어, 비밀번호 대응과 접근 차단 중 무엇을 할지 정하지 못합니다.
  - 먼저 맞는 규칙에서 멈추기 때문입니다. 좁은 조건(로그인 실패, 관리자 경로)을 위에 두고 넓은 조건(모든 실패)을 아래에 두어야 유형이 나뉩니다.

**왜**

- <mark>유형 이름을 정하는 규칙은 위에서부터 차례로 보고 먼저 맞는 것을 씁니다.</mark> 로그인 실패를 먼저 보고, 그다음 관리자 경로를 보고, 나머지 실패를 「기타 실패」로 모읍니다.

**자주 틀리는 곳**

- `events.to_dict("records")` 를 빼고 `event_list = events` 로 쓰면, `for event in event_list` 가 이벤트가 아니라 **열 이름**을 하나씩 꺼내서 오류가 납니다.
  - 실행하면 다음 오류가 납니다(<mark>`string indices must be integers`</mark> 가 나오면 이 실수입니다).

```
Traceback (most recent call last):
  File "…/anomaly_detection/day03_4-1_run.py", line 4, in <module>
    counts = count_types(events)  # 유형별로 센다
  File "…/anomaly_detection/classify.py", line 42, in count_types
    action = event["action"]  # 그 이벤트의 행동
TypeError: string indices must be integers
```

  - 줄 번호는 사람마다 다릅니다.
- `if` 두 조건을 `and` 로 잇지 않고 `result == "실패"` 만 쓰면 모든 실패가 첫 번째 규칙에 걸려 「비정상 로그인」으로 나옵니다.

**관제에서는**

- 유형 규칙은 운영하면서 계속 고칩니다. 「기타」가 너무 크면 규칙이 부족하다는 신호입니다.

---

### 정답 마무리

💻 **터미널에 입력합니다.**

```bash
pwd
ls
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `ls` 폴더 안의 파일 이름 보기

**결과**

- 오늘 만든 파일 여덟 개와 안내 · 보고서 두 파일이 보여야 합니다. 깃허브에 올리는 일은 오후 6교시 마지막에 합니다.
