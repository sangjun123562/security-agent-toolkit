# 11/6(금) 오후 · 4과목 이상탐지 ⑤ — 도커 컴포즈로 서버 두 대를 켜고 웹 서버 로그 만들기 — 실습

오전에는 샘플 알림이 맞았는지 세고, 틀린 알림을 줄였습니다. 오후에는 월요일 통합 실습에 쓸 **웹 서버 로그**를 직접 만듭니다. 서버를 켜고, 요청을 보내고, 서버가 남긴 기록(로그)에서 스캐너 요청을 찾아 파일로 저장합니다. 서버는 **도커 컴포즈**(Docker Compose, 도커 컴포즈: 서버 여러 대의 설정을 파일 하나에 적어 두고 한 번에 켜고 끄는 도구)로 켭니다.

- **5교시**: 서버 한 대를 켜는 `docker run` 을 복습하고, 컴포즈 파일(`compose.yaml`) 하나로 서버 두 대를 한 번에 켭니다.
- **6교시**: 서버를 세 대로 늘리면서 서버마다 누가 접속할 수 있는지를 컴포즈 파일에 정하고(`127.0.0.1:`), 설정을 바꿔도 바뀐 서버만 다시 켜지는 것을 확인합니다. 곁다리로 서버 로그를 내 폴더에 남기고 `grep` 으로 다룹니다.

오늘은 오후 5 · 6교시이고, <mark>깃허브에 올리는 일은 6교시 마지막에 합니다.</mark> 교시마다 문제는 하나입니다.

- 오늘 쓰는 도구는 **도커 · 터미널 · VS Code · git** 입니다. <mark>오늘 오후는 파이썬 · 판다스 코드를 쓰지 않고, 터미널 명령만 씁니다.</mark>
- 서버가 쓰는 포트(port, 포트: 컴퓨터로 들어오는 요청을 구분하는 번호)는 `8080` · `8081` · `8082` 로 **고정**합니다. <mark>번호를 바꾸지 않습니다.</mark>
- 보고서에서 🔍 가 붙은 질문은 이 교시에서 꼭 알아야 할 핵심 질문이고, <mark>내 화면의 값을 근거로 이유까지 서술합니다</mark>.

> ⚠ **먼저 확인 — 오늘 만드는 파일은 모두 4과목 폴더 `anomaly_detection` 안에서 만듭니다.**
> - <mark style="background:#ffc4d6">터미널에서 `pwd` 를 쳐서 결과가 `…/anomaly_detection` 으로 끝나는지 확인한 뒤 시작합니다.</mark> 이전 과목 폴더가 아닙니다.
> - 다른 폴더에서 `docker compose` 를 치면 상위 폴더에 있는 옛 `compose.yaml` 이 켜질 수 있습니다.

📎 **오늘 불러 쓰는 이전 파일**: 없습니다. 오늘 만드는 파일은 `compose.yaml` · `compose.secure.yaml` 과 `logs/web_404.log` 입니다.

## 시작하기

> 🐳 **먼저 Docker Desktop 앱을 켭니다.** 시작 메뉴(맥북은 응용 프로그램)에서 Docker Desktop 을 열고, <mark>화면 구석에 **고래 모양 아이콘**이 보이고 움직임이 멈추면</mark> 준비된 것입니다.

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** `anomaly_detection` 폴더로 들어가 위치를 확인합니다.

   ① 폴더로 들어갑니다.

   ```bash
   cd anomaly_detection
   ```

   - 하는 일: `anomaly_detection` 폴더로 이동합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark>`…/anomaly_detection` 으로 끝나는 글자가 나오면</mark> 됩니다.

3. **[Docker Desktop]** 도커 프로그램(Docker Desktop)이 켜져 있는지 확인합니다.

   ① 켜져 있는 서버를 봅니다.

   ```bash
   docker ps
   ```

   - 하는 일: 지금 켜져 있는 컨테이너(container, 컨테이너: 이미지로 실제로 켜진 서버 하나)를 보여 줍니다.
   - 나오는 것: <mark>`CONTAINER ID` 로 시작하는 머리글 줄이 나오면</mark> 도커가 켜져 있는 것입니다. 다른 서버가 없으면 머리글 줄만 나와도 됩니다. 오류가 나오면 아래 「🆘」 둘째 줄을 따릅니다.

4. **[터미널]** 오늘 쓸 포트 `8080` · `8081` · `8082` 번을 이미 켜져 있는 서버가 쓰고 있지 않은지 확인합니다. <mark>쓰고 있으면 오늘 켤 서버가 켜지지 않습니다.</mark>

   ① 세 포트를 쓰는 서버가 있는지 봅니다.

   ```bash
   docker ps --filter publish=8080 --filter publish=8081 --filter publish=8082
   ```

   - 하는 일: `--filter publish=포트번호` 는 그 포트를 쓰는 서버만 보여 줍니다.
   - 나오는 것: <mark>`CONTAINER ID` 로 시작하는 머리글 줄만 나오면</mark> 아무도 쓰고 있지 않은 것이니 다음으로 갑니다.

   ```
   CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
   ```

   서버가 한 줄이라도 나오면 그 서버가 포트를 쓰고 있는 것입니다. 줄 맨 끝 `NAMES` 열의 이름을 보고, 다른 수업에서 쓰는 서버일 수 있으니 <mark>내가 켠 서버가 맞는지 확인한 뒤</mark> 아래 명령으로 끕니다.

   ② (서버가 나왔을 때만) 그 서버를 끕니다.

   ```bash
   docker stop 이름
   ```

   - 하는 일: `이름` 자리에 `NAMES` 열의 이름을 넣어 그 서버를 끕니다.
   - 나오는 것: 끈 서버의 이름이 한 줄 나옵니다. 그 뒤 ① 의 명령을 다시 쳐서 머리글 줄만 나오는지 봅니다.


5. **오늘 받은 파일 두 개**(`day05_pm_docker_compose_logs.md`, `day05_pm_report.md`)를 <mark>`다운로드` 폴더에서 `anomaly_detection` 폴더로 끌어다 놓습니다</mark>(안 되면 **File › Save As…**). 이미 있으면 건너뜁니다.
6. **[VS Code]** 보고서 맨 위 제목 `(이름 · 2026-11-06(금))` 의 <mark>`이름` 을 내 이름으로 바꿉니다</mark>. 안내 파일은 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)로 미리보기를 엽니다.

### 🆘 오류가 나면

- 먼저 `pwd` 가 `anomaly_detection` 으로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `Cannot connect to the Docker daemon` 처럼 도커에 연결할 수 없다는 오류(Windows 에서는 문구가 다를 수 있습니다): <mark>Docker Desktop 이 꺼져 있는 것입니다.</mark> Docker Desktop 을 실행하고, 아래쪽 상태가 초록색(Running)이 될 때까지 1분쯤 기다린 뒤 다시 칩니다.
- `toomanyrequests` 가 나오면 이미지를 너무 많이 받았다는 뜻입니다. <mark>1시간 뒤에 다시 하고,</mark> 그동안은 옆 사람이 아니라 보고서 질문부터 채웁니다.
- 오류 전체를 친 명령과 함께 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). <mark>막히면 맨 아래 「정답」을 보고</mark>, 풀리지 않으면 보고서 (가)에 「모름 — 막힌 곳: …」 이라고 쓰고 넘어갑니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark>**터미널**에서</mark> 합니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 도커 복습 · 컴포즈로 서버 두 대 한 번에 켜기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「월요일에 이번 주에 만든 탐지를 한꺼번에 돌려 볼 예정입니다. 쓸 웹 서버 로그가 필요해서 서버를 두 대 켜려고 합니다. 그런데 서버 한 대를 켜는 `docker run` 명령이 옵션이 길어서, 두 대를 켜려면 긴 명령을 두 번 쳐야 하고 한 군데만 틀려도 서버가 다르게 켜집니다.
>
> 서버 설정을 파일 하나에 적어 두고, 명령 한 줄로 두 대를 켤 수 있을까요?」
> - **왜 중요한가**: <mark>설정을 파일로 적어 두면 누가 켜도 같은 서버가 켜지고, 파일을 저장소에 올려 두면 설정 기록도 남습니다.</mark>

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 서버(server, 서버: 요청을 받아 응답을 돌려주는 프로그램)를 켜는 방법을 `docker run` 으로 배웠습니다. 서버 한 대를 켤 때도 옵션을 여러 개 씁니다.
2. 서버가 두 대가 되면 같은 명령을 두 번 쳐야 합니다. <mark>설정을 `compose.yaml` 파일에 적어 두면 `docker compose up -d` 한 줄로 두 대를 한 번에 켭니다.</mark>
3. 오늘 질문은 하나입니다. <mark>**서버 두 대를 명령 한 줄로 켤 수 있는가?**</mark>

### 📖 5.1 `docker run` 옵션은 `compose.yaml` 의 어디에 적을까

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| `docker run` 에서 | `compose.yaml` 에서 | 뜻 |
|---|---|---|
| `--name web-run` | `web:` · `web2:` (서비스 이름) | 서버를 구분하는 이름. 컴포즈에서는 서비스(service, 서비스: 컴포즈 파일에 적은 서버 한 대의 설정)라고 부릅니다 |
| `nginx:1.28` | `image: nginx:1.28` | 서버를 켜는 데 쓰는 이미지(image, 이미지: 서버 프로그램과 설정을 묶어 둔 파일) |
| `-p 8080:80` | `ports:` 아래 `- "8080:80"` | 내 컴퓨터의 8080번 포트로 온 요청을 서버의 80번 포트로 보냄 |
| `-d` | `docker compose up -d` 의 `-d` | 백그라운드(background, 백그라운드: 터미널 화면을 차지하지 않고 안에서 계속 실행되는 방식)에서 실행함 |

- `nginx`(엔진엑스)는 웹 서버 프로그램입니다. 서버를 켜면 컨테이너가 하나 생깁니다.
- 컴포즈 파일은 YAML(야믈) 형식으로 씁니다. YAML 은 바로 아래 5.2 에서 설명합니다.

### 📖 5.2 YAML(야믈) 파일이란

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. **정의**: YAML(야믈)은 설정 내용을 사람이 읽기 쉽게 글로 적는 파일 형식입니다. 파일 이름이 `.yaml` 이나 `.yml` 로 끝나고, 오늘 쓰는 `compose.yaml` 이 이 형식입니다. 처음 보는 형식이지만 아래 네 가지 모양만 알면 읽을 수 있습니다.

| 모양 | 뜻 | `compose.yaml` 에서 |
|---|---|---|
| `이름: 값` | 이름과 값을 짝으로 적음 (콜론 뒤에 공백 한 칸) | `image: nginx:1.28` |
| 줄 앞의 공백 (들여쓰기) | 그 줄이 어느 이름 아래에 속하는지 나타냄 | `web1:` 아래에 `image:` 와 `ports:` 가 속함 |
| `- 값` | 값이 여러 개일 때 한 줄에 하나씩 적음 | `ports:` 아래의 `- "8080:80"` |
| `#` 뒤의 글 | 사람이 읽는 설명 (실행에는 영향이 없음) | 각 줄 끝의 설명 |

2. **같은 내용을 JSON 과 비교하면**: 오전에 쓴 JSON 파일과 같은 정보를 담지만 모양이 다릅니다. 아래 둘은 같은 내용입니다.

```
JSON : {"services": {"web1": {"image": "nginx:1.28"}}}
```

```
YAML :
services:
  web1:
    image: nginx:1.28
```

3. **장점**
   - <mark>읽기 쉽습니다.</mark> 중괄호(`{ }`)와 따옴표가 거의 없어서 위에서 아래로 읽으면 구조가 보입니다.
   - <mark>설명(주석)을 적을 수 있습니다.</mark> JSON 은 주석을 쓸 수 없지만, YAML 은 `#` 로 「왜 이 값인지」를 파일에 남길 수 있습니다.
   - <mark>여러 도구가 같은 형식을 씁니다.</mark> Docker Compose 외에도 GitHub Actions(깃허브에서 작업을 자동으로 실행하는 설정), Kubernetes(쿠버네티스: 서버 여러 대를 관리하는 도구), Ansible(앤서블: 서버 설정을 자동화하는 도구)의 설정 파일이 YAML 입니다. 오늘 읽는 방법을 그대로 쓸 수 있습니다.
4. **주의할 점**
   - <mark style="background:#ffc4d6">들여쓰기는 공백으로 합니다. 탭 문자를 넣으면 오류가 납니다.</mark> VS Code 에서 붙여 넣으면 공백으로 들어가서 괜찮습니다.
   - <mark style="background:#ffc4d6">같은 단계의 줄은 공백 수가 같아야 합니다.</mark> 이 파일은 한 단계 안쪽마다 공백 2칸입니다. 공백이 어긋나면 다른 이름 아래에 속하는 것으로 읽혀서 오류가 나거나 다른 뜻이 됩니다.
   - `이름: 값` 에서 콜론 뒤에 공백 한 칸을 씁니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 5-1 · 서버 한 대를 복습하고 컴포즈로 두 대 켜기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>서버를 켤 때마다 긴 `docker run` 명령을 쳐야 하고, 서버가 늘수록 틀리기 쉽습니다</mark>.
- **그래서 하는 것**:
  - `docker run` 으로 서버 한 대를 켜고 끄는 것을 복습합니다.
  - `compose.yaml` 을 읽고, 서버 두 대를 한 번에 켭니다.
  - 두 서버가 모두 응답하는지 확인합니다.
- **실행하면**: <mark>`docker compose ps` 에 서버 두 개(`web1` · `web2`)가 `Up` 으로 나오고, 8080번과 8081번 모두 결과 번호 `200` 이 나옵니다.</mark>
- **현업에서는**: 서버가 늘수록 설정 파일 하나로 관리하는 방식을 씁니다. 파일에 포트와 이미지 버전이 적혀 있어서 누가 켜도 같은 결과가 나옵니다.

**🎯 할 일**

1. 서버 한 대를 `docker run` 으로 켜고 확인한 뒤 끕니다.
2. `compose.yaml` 파일을 만들어 붙여 넣고 읽습니다.
3. `docker compose up -d` 로 서버 두 대를 켜고, 두 서버가 응답하는지 확인합니다.

**순서**

1. **[터미널]** 서버를 켜는 데 쓸 이미지가 내 PC 에 이미 있는지 먼저 확인합니다. <mark>이미 있으면 다시 받지 않아도 됩니다.</mark>

   ① 이미지가 있는지 봅니다.

   ```bash
   docker images nginx:1.28
   ```

   - 하는 일: 내 PC 에 받아 둔 이미지 중 `nginx:1.28` 을 보여 줍니다.
   - 나오는 것: <mark>`nginx:1.28` 이 적힌 줄이 있으면</mark> 이미 받은 것이니 ② 는 건너뛰고 2번으로 갑니다. 머리글 줄만 나오면 아직 없는 것입니다. 도커 버전에 따라 머리글의 글자는 다를 수 있습니다.

   ```
   IMAGE        ID             DISK USAGE   CONTENT SIZE   EXTRA
   nginx:1.28   146adea4768b        258MB         64.1MB   U
   ```

   ② (없을 때만) 이미지를 받습니다.

   ```bash
   docker pull nginx:1.28
   ```

   - 하는 일: `nginx:1.28` 이미지를 인터넷에서 내려받습니다.
   - 나오는 것: 마지막에 `Status: Downloaded newer image` 가 나오면 됩니다.

2. **[터미널]** 복습입니다. 서버 한 대를 켜고, 확인하고, 끕니다. 아래 세 명령을 <mark>하나씩 쳐서</mark> 결과를 봅니다.

   ① 서버를 켭니다.

   ```bash
   docker run -d --rm -p 8080:80 --name web-run nginx:1.28
   ```

   - 하는 일: 서버 한 대를 켭니다. 옵션은 이렇습니다.
     - `-d`: 백그라운드에서 켬 (터미널을 계속 쓸 수 있음)
     - `--rm`: 서버를 끄면 그 서버(컨테이너)를 자동으로 지움
     - `-p 8080:80`: 내 컴퓨터의 8080번 포트를 서버의 80번 포트에 연결
     - `--name web-run`: 서버 이름을 `web-run` 으로 정함
   - 나오는 것: 서버의 고유 번호(긴 글자)가 한 줄 나옵니다.

   ② 켜졌는지 봅니다.

   ```bash
   docker ps
   ```

   - 하는 일: 켜져 있는 서버를 보여 줍니다.
   - 나오는 것: <mark>`web-run` 이 `Up` 으로 보이고, PORTS 에 `0.0.0.0:8080->80/tcp` 가 있으면</mark> 됩니다.

   ```
   CONTAINER ID   IMAGE        COMMAND                  CREATED                  STATUS                  PORTS                                     NAMES
   e1a2ad01c544   nginx:1.28   "/docker-entrypoint.…"   Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web-run
   ```

   ③ 서버를 끕니다.

   ```bash
   docker stop web-run
   ```

   - 하는 일: `web-run` 서버를 끕니다.
   - 나오는 것: `web-run` 이 한 줄 나옵니다. <mark>이어서 `docker ps` 를 쳤을 때 `web-run` 이 없으면</mark> 정상입니다. `--rm` 때문에 끄면 서버가 지워집니다.

3. **[터미널]** 컴포즈 파일을 만들고 확인합니다. 두 명령을 하나씩 칩니다.

   ① 빈 `compose.yaml` 파일을 만듭니다.

   ```bash
   touch compose.yaml
   ```

   - 하는 일: 비어 있는 `compose.yaml` 파일을 만듭니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 파일이 생겼는지 봅니다.

   ```bash
   ls
   ```

   - 하는 일: 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: <mark>`compose.yaml` 이 보이면</mark> 됩니다.

4. **[VS Code]** `compose.yaml` 을 열어 아래 내용을 그대로 붙여 넣고 저장합니다. <mark>각 줄의 `#` 뒤 설명을 읽으면서 붙여 넣습니다.</mark>

   ```yaml
   services:                      # 켤 서버들을 적는 곳이 여기서 시작된다
     web1:                        # 첫 번째 서버의 이름 (명령에서 이 이름으로 부른다)
       image: nginx:1.28          # 사용할 프로그램 : nginx 웹 서버 1.28 버전
       ports:                     # 내 컴퓨터와 서버를 이어 주는 포트를 적는 곳
         - "8080:80"              # 내 컴퓨터의 8080번으로 보낸 요청이 서버의 80번으로 들어간다
       restart: unless-stopped    # 서버가 저절로 꺼지면 다시 켠다 (내가 직접 끈 경우는 그대로 둔다)
     web2:                        # 두 번째 서버의 이름
       image: nginx:1.28          # 같은 nginx 웹 서버를 하나 더 켠다
       ports:                     # 내 컴퓨터와 서버를 이어 주는 포트를 적는 곳
         - "8081:80"              # 두 번째 서버는 8081번으로 받는다 (8080번과 겹치면 안 된다)
       restart: unless-stopped    # 서버가 저절로 꺼지면 다시 켠다
   ```

   - `restart: unless-stopped` 는 서버가 저절로 꺼지면 다시 켜라는 설정입니다. 내가 직접 끈 서버는 다시 켜지 않습니다.
   - <mark style="background:#ffc4d6">`web1` 은 8080번, `web2` 는 8081번입니다. 두 서버가 같은 번호를 쓰면 한쪽이 켜지지 않습니다.</mark>

5. **[터미널]** 서버 두 대를 한 번에 켜고 상태를 봅니다. <mark>컴포즈 파일이 있는 폴더(`anomaly_detection`)에서 칩니다.</mark>

   ① 서버 두 대를 한 번에 켭니다.

   ```bash
   docker compose up -d
   ```

   - 하는 일: 컴포즈 파일의 서버를 모두 백그라운드에서 켭니다.
   - 나오는 것: 서버마다 `Created`, `Started` 줄이 차례로 나옵니다.

   ```
    Network anomaly_detection_default Creating
    Network anomaly_detection_default Created
    Container anomaly_detection-web1-1 Creating
    Container anomaly_detection-web2-1 Creating
    Container anomaly_detection-web1-1 Created
    Container anomaly_detection-web2-1 Created
    Container anomaly_detection-web2-1 Starting
    Container anomaly_detection-web1-1 Starting
    Container anomaly_detection-web2-1 Started
    Container anomaly_detection-web1-1 Started
   ```

   ② 켜진 상태를 봅니다.

   ```bash
   docker compose ps
   ```

   - 하는 일: 컴포즈로 켠 서버의 상태를 보여 줍니다.
   - 나오는 것: <mark>`web1` 과 `web2` 가 모두 `Up` 이고, PORTS 에 `8080` 과 `8081` 이 보이면</mark> 됩니다. 서버 이름 앞의 `anomaly_detection` 은 컴포즈 파일이 있는 폴더 이름이고, 끝의 `-1` 은 컴포즈가 자동으로 붙이는 번호입니다.

   ```
   NAME                       IMAGE        COMMAND                  SERVICE   CREATED                  STATUS                  PORTS
   anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
   anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      Less than a second ago   Up Less than a second   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
   ```

6. **[터미널]** 두 서버가 모두 응답하는지 확인합니다. 명령 끝의 `-s -o /dev/null -w "%{http_code}\n"` 는 HTML 을 화면에 안 보이고 결과 번호만 보여 주는 설정이라 외우지 않아도 됩니다. 결과 번호 `200` 은 요청이 성공했다는 뜻입니다.

   ① 8080번 서버(`web1`)를 확인합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
   ```

   - 하는 일: 그 주소에 요청을 보내고 결과 번호만 보여 줍니다.
   - 나오는 것: <mark>결과 번호가 `200` 이면</mark> 됩니다.

   ```
   200
   ```

   ② 8081번 서버(`web2`)를 확인합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
   ```

   - 하는 일: 같은 방법으로 두 번째 서버를 확인합니다.
   - 나오는 것: <mark>결과 번호가 `200` 이면</mark> 됩니다.

   ```
   200
   ```


7. **[보고서]** `day05_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
   - (가) 5교시 순서의 서버 켜기 · 확인 명령(`docker images` 부터 `curl` 까지)과 그 결과를 친 순서대로 붙여 넣고, 서비스 이름 두 개와 각 서비스의 포트를 적어 주세요.
   - (나) 🔍 서버 두 대를 `docker run` 으로 켜는 것과 `compose.yaml` 과 `docker compose up -d` 로 켜는 것을 비교해, 컴포즈가 더 나은 점을 두 가지 적어 주세요.
   - (다) 🔍 보안 사고가 난 뒤 감사팀이 「사고 당시와 같은 구성으로 서버를 다시 켜 보라」고 요청했습니다. 팀원 한 명은 3주 전에 긴 `docker run` 명령을 직접 쳐서 서버를 켰는데 그 명령을 기억하지 못합니다. 다른 팀은 `compose.yaml` 을 깃허브에 올려 두었습니다. 두 팀이 같은 구성을 다시 켤 수 있는지 비교하고, 파일에 `nginx:1.28` 처럼 버전을 적어 두는 것이 이런 재현에 왜 중요한지 적어 주세요.
   - (라) 🔍 팀원 세 명이 같은 `compose.yaml` 로 서버를 켰는데 한 명의 PC 에서만 `8081` 번 포트를 다른 프로그램이 쓰고 있어서 `web2` 가 켜지지 않았습니다. 이 사람이 파일의 어느 줄을 어떻게 바꾸면 되는지 적고, 바꿔도 서버 안에서는 여전히 `80` 번 포트로 동작하는 이유를 적어 주세요. 이 사람이 `curl` 로 확인할 때 달라지는 점도 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 명령 |
|---|---|
| 서버 한 대 켜기 · 확인 · 끄기 | `docker run -d --rm -p 8080:80 --name web-run nginx:1.28` → `docker ps` → `docker stop web-run` |
| 서버 두 대 한 번에 켜기 | `docker compose up -d` |
| 켜진 서버 상태 보기 | `docker compose ps` |
| 응답 확인 | `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 서버마다 접속 범위 정하기 · 설정 바꿔 적용하기</mark>

> 📨 **오늘 들어온 일**
>
> A사 보안 팀장이 보낸 메시지입니다:
> 「지금 켜 둔 서버 두 대(`web1` · `web2`)는 같은 네트워크에 있는 다른 사람의 PC 에서도 들어올 수 있습니다. 그런데 앞으로 관리자만 써야 하는 서버와 접속 기록을 모아 두는 서버를 더 켤 예정입니다. 이런 서버가 다른 사람에게 열려 있으면 위험합니다.
>
> 서버를 한 대 더 늘려서 이렇게 해 주세요.
> - ① `web1` 은 지금처럼 누구나 들어올 수 있게 둡니다.
> - ② `web2` 와 `web3` 은 **내 PC 에서만** 들어올 수 있게 바꿉니다.
> - ③ `web3` 의 접속 기록은 내 폴더에 파일로 남겨 주세요.
>
> 그리고 `web1` 은 지금 쓰고 있으니 중간에 끊기면 안 됩니다.」
> - **왜 중요한가**:
>   - <mark>열면 안 되는 서버를 다른 사람에게 열어 두는 실수는 보안 사고의 대표적인 원인입니다.</mark> 예를 들어 서버를 설정하는 관리 화면이 열려 있으면, 권한이 없는 사람도 들어오려고 시도할 수 있습니다.
>   - <mark>설정을 바꿔도 바뀐 서버만 다시 만들고, 바뀌지 않은 `web1` 은 계속 실행합니다.</mark> 그래서 쓰고 있는 서버를 끊지 않고 고칠 수 있습니다.
>   - 서버를 지우면 서버 안의 접속 기록도 같이 사라집니다. 기록을 내 폴더에 연결해 두면, 서버를 지워도 파일이 남습니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

1. 오늘 질문은 하나입니다. <mark>**서버마다 접속 범위(접속 범위: 어느 PC 에서 그 서버에 접속할 수 있는지)를 컴포즈 파일에 적고, 서버를 끊지 않고 바꿔 적용할 수 있는가?**</mark>
2. 5교시에는 두 서버가 모두 같은 방식(`"8080:80"`)으로 열려 있었습니다. 서버가 늘면 서버마다 열 범위를 따로 정해야 합니다.
3. 컴포즈는 파일을 고치고 같은 `docker compose up -d` 를 치면, 바뀐 서버만 다시 만들고 나머지는 그대로 둡니다.

### 📖 6.1 포트 줄에 접속 범위가 들어 있다

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

`127.0.0.1` 은 내 컴퓨터를 가리키는 주소입니다. 포트 줄 맨 앞에 붙이면 내 PC 에서만 접속할 수 있습니다.

| 포트 줄 | 읽는 법 | 누가 접속할 수 있나 |
|---|---|---|
| `"8080:80"` | 내 컴퓨터의 8080번 → 서버 안의 80번 | <mark>같은 네트워크의 다른 PC 도 가능</mark> (모두에게 열림) |
| `"127.0.0.1:8081:80"` | 맨 앞에 `127.0.0.1` 을 붙임 | <mark>내 PC 에서만</mark> |

- `docker compose ps` 의 PORTS 에서 읽을 수 있습니다. `0.0.0.0:8080` 은 모두에게 열린 것이고, `127.0.0.1:8081` 은 내 PC 에서만 열린 것입니다.
- <mark>관리 화면 · 데이터베이스처럼 밖에 열면 안 되는 서버는 `127.0.0.1:` 을 붙여 둡니다.</mark> 이것이 오늘 문제의 실무 의미입니다.

### 📖 6.2 `up -d` 의 출력은 서버마다 다르게 읽는다

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

| 출력 | 뜻 | 이번 파일에서 |
|---|---|---|
| `Running` | 설정이 같아서 그대로 둠 | `web1` |
| `Recreate` → `Recreated` | 설정이 바뀌어 기존 서버(컨테이너)를 새 설정으로 다시 만듦 | `web2` (포트 줄이 바뀜) |
| `Created` | 새로 만듦 | `web3` |

- <mark>`web1` 은 설정이 바뀌지 않아서 끊기지 않습니다.</mark> 서버가 여러 대여도 바뀐 서버만 다시 켜지는 것이 컴포즈를 쓰는 이유입니다.

### 📖 6.3 곁다리 — 로그를 내 폴더에 남기고 다루기

> 📖 **읽을거리 — 읽기만 합니다.** 문제가 아닙니다. 답할 질문도, 따라 칠 명령도 없습니다.

- <mark>`volumes` 는 내 폴더와 서버 안 폴더를 연결하는 설정입니다.</mark> `- ./logs:/var/log/nginx` 는 서버가 로그를 쓰는 폴더(오른쪽)를 내 `logs` 폴더(왼쪽)에 연결한다는 뜻입니다.
- 연결해 두면 로그가 내 폴더의 파일로 쌓이고, 서버를 지워도(`down`) 파일은 남습니다. 서버 안에만 있는 로그는 서버와 함께 사라집니다.
- 그 파일을 다룰 때 아래 세 표시를 씁니다.

| 표시 | 하는 일 | 오늘 쓰는 곳 |
|---|---|---|
| `\|` (파이프, pipe: 앞 명령의 출력을 뒤 명령에 넘김) | 왼쪽 명령의 출력을 오른쪽 명령에 넘긴다 | `grep " 404 " logs/access.log \| wc -l` |
| `grep "글자"` (그렙: 글자가 들어 있는 줄만 남김) | 파일이나 출력에서 그 글자가 든 줄만 남긴다 | `grep " 404 " logs/access.log` |
| `> 파일이름` (리다이렉션, redirection: 출력을 화면 대신 파일에 저장) | 화면에 나올 내용을 파일에 저장한다 | `> logs/web_404.log` |

- `wc -l` 은 줄이 몇 개인지 세어 줍니다. 위 파이프 예시는 「`404` 가 든 줄이 몇 개인가」입니다.

> ✍️ **여기부터 문제입니다.** 위는 읽을거리였고, 아래에서 직접 합니다.

### <mark>✍️ 문제 6-1 · 서버마다 접속 범위를 정해 컴포즈 파일로 적용하기</mark>

> 🎯 **이 문제를 내는 이유**
> - **서버마다 열 범위를 정하는 연습입니다.** 접속 범위는 보안 설정의 가장 기본이고, 컴포즈 파일의 포트 줄 하나로 정해집니다.
> - **서버를 끊지 않고 설정을 바꾸는 방법을 확인합니다.** `web1` 이 `Running` 으로 남는 것을 직접 보면 컴포즈를 왜 쓰는지 알 수 있습니다.
> - **곁다리로** 로그를 내 폴더에 남기고 `grep` 으로 다룹니다. 서버를 지워도 접속 기록 파일이 남는 방법입니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>5교시에 켠 서버 두 대가 모두 같은 네트워크의 다른 PC 에서 접속할 수 있게 열려 있고, 서버를 늘리거나 접속 범위를 바꾸는 방법을 정하지 않았습니다</mark>.
- **그래서 하는 것**:
  - 새 컴포즈 파일 `compose.secure.yaml` 로 서버를 세 대로 늘립니다.
  - `web2` · `web3` 의 포트 줄에 `127.0.0.1:` 을 붙여 내 PC 에서만 접속되게 합니다.
  - `web1` 이 끊기지 않고 `Running` 으로 남는지 `up -d` 의 출력으로 확인합니다.
  - (곁다리) `web3` 의 로그를 내 `logs` 폴더 파일로 남기고 `grep` 으로 다룹니다.
- **실행하면**: <mark>`up -d` 에서 `web1` 은 `Running`, `web2` 는 `Recreated`, `web3` 은 `Created` 로 나오고, `ps` 의 PORTS 에 `web2` · `web3` 은 `127.0.0.1:` 이 붙습니다.</mark>
- **현업에서는**: 서버마다 공개 범위를 컴포즈 파일에 적어 두고, 설정을 바꿀 때는 파일을 고쳐 같은 `docker compose up -d` 로 적용합니다. 설정이 바뀐 서버만 다시 만들어지고 바뀌지 않은 서버는 계속 실행됩니다. 이번 실습에서는 설정이 그대로인 `web1` 이 계속 실행되는 것을 확인합니다.

**🎯 할 일**

1. 5교시 서버의 접속 범위(PORTS)를 확인하고, 새 파일을 만들어 붙여 넣고 읽습니다.
2. `compose.secure.yaml` 로 적용하고, `web1` · `web2` · `web3` 의 출력과 PORTS 가 서로 다른 것을 읽습니다.
3. (곁다리) `web3` 의 로그 파일을 읽고 `404` 요청을 세어 저장합니다.

**순서**

1. **[터미널]** 5교시에 켠 서버의 접속 범위를 확인합니다. 이 출력은 보고서 (가)에 붙여 넣습니다.

   ① 서버 상태를 봅니다.

   ```bash
   docker compose ps
   ```

   - 하는 일: 컴포즈로 켠 서버의 상태를 보여 줍니다.
   - 나오는 것: <mark>`web1` · `web2` 가 `Up` 이고, PORTS 가 둘 다 `0.0.0.0:` 으로 시작하면</mark> 됩니다. 켜져 있지 않으면 `docker compose up -d` 를 먼저 칩니다.

   ```
   NAME                       IMAGE        COMMAND                  SERVICE   CREATED                  STATUS                  PORTS
   anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
   anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      Less than a second ago   Up Less than a second   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
   ```

2. **[터미널]** 새 파일을 만들 준비를 합니다. 두 명령을 하나씩 칩니다.

   ① (곁다리에서 쓸) 로그 폴더를 만듭니다.

   ```bash
   mkdir logs
   ```

   - 하는 일: `logs` 폴더를 만듭니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 새 컴포즈 파일을 만듭니다.

   ```bash
   touch compose.secure.yaml
   ```

   - 하는 일: 비어 있는 `compose.secure.yaml` 파일을 만듭니다. 5교시의 `compose.yaml` 은 그대로 둡니다.
   - 나오는 것: 아무것도 나오지 않습니다.

3. **[VS Code]** `compose.secure.yaml` 을 열어 아래 내용을 그대로 붙여 넣고 저장합니다. <mark>주석을 읽으면서 5교시 파일과 다른 곳 세 군데를 찾아봅니다.</mark>

   ```yaml
   services:                      # 켤 서버들을 적는 곳이 여기서 시작된다
     web1:                        # 일반 서버 : 같은 네트워크의 다른 PC 도 접속할 수 있다
       image: nginx:1.28          # 5교시와 같은 프로그램
       ports:                     # 접속 범위를 정하는 곳
         - "8080:80"              # 주소를 적지 않으면 모두에게 열린다 (5교시와 같다)
       restart: unless-stopped    # 서버가 저절로 꺼지면 다시 켠다 (5교시와 같다)
     web2:                        # 관리용 서버 : 내 PC 에서만 접속한다
       image: nginx:1.28          # 5교시와 같은 프로그램
       ports:                     # 접속 범위를 정하는 곳
         - "127.0.0.1:8081:80"    # 맨 앞의 127.0.0.1 은 「내 PC 에서만」이라는 뜻이다 (바뀐 줄)
       restart: unless-stopped    # 서버가 저절로 꺼지면 다시 켠다
     web3:                        # 로그 서버 : 내 PC 에서만 접속하고, 로그를 내 폴더에 남긴다 (새로 추가한 서버)
       image: nginx:1.28          # 같은 nginx 웹 서버
       ports:                     # 접속 범위를 정하는 곳
         - "127.0.0.1:8082:80"    # web2 와 같이 내 PC 에서만 접속한다 (포트는 8082)
       restart: unless-stopped    # 서버가 저절로 꺼지면 다시 켠다
       volumes:                   # 내 폴더와 서버 안 폴더를 연결하는 곳
         - ./logs:/var/log/nginx  # 서버가 로그를 쓰는 폴더를 내 logs 폴더에 연결한다 (왼쪽 내 폴더, 오른쪽 서버 안)
   ```

   - `web1`: 5교시와 같습니다. <mark>바뀌지 않은 서버입니다.</mark>
   - `web2`: 포트 줄 맨 앞에 `127.0.0.1:` 이 붙었습니다. <mark>바뀐 서버입니다.</mark>
   - `web3`: 새로 추가한 서버이고, (곁다리) `volumes` 줄이 있습니다.
   - <mark style="background:#ffc4d6">`web1` · `web2` · `web3` 의 포트 번호(8080 · 8081 · 8082)를 바꾸지 않습니다.</mark>

4. **[터미널]** 새 파일로 적용합니다. <mark>5교시 서버를 끄지 않고 바로 칩니다.</mark> 이 출력을 서버마다 읽는 것이 오늘 문제의 핵심입니다.

   ① 새 파일로 적용합니다.

   ```bash
   docker compose -f compose.secure.yaml up -d
   ```

   - 하는 일: `-f 파일이름` 은 사용할 컴포즈 파일을 정합니다. 적용하는 방식은 5교시와 같습니다.
   - 나오는 것: <mark>`web1-1 Running`, `web2-1 Recreated`, `web3-1 Created` 세 줄이 보이면</mark> 됩니다. `Creating` · `Starting` 은 준비 과정이니 6.2 의 표로 위 세 줄만 읽습니다.

   ```
    Container anomaly_detection-web1-1 Running
    Container anomaly_detection-web3-1 Creating
    Container anomaly_detection-web2-1 Recreate
    Container anomaly_detection-web3-1 Created
    Container anomaly_detection-web2-1 Recreated
    Container anomaly_detection-web3-1 Starting
    Container anomaly_detection-web2-1 Starting
    Container anomaly_detection-web2-1 Started
    Container anomaly_detection-web3-1 Started
   ```

5. **[터미널]** 접속 범위가 바뀐 것을 확인합니다. 이 출력도 보고서 (가)에 붙여 넣습니다.

   ① 적용 뒤 서버 상태를 봅니다.

   ```bash
   docker compose -f compose.secure.yaml ps
   ```

   - 하는 일: 새 파일의 서버 상태를 보여 줍니다. 앞에서 친 1번의 출력과 PORTS 를 비교합니다.
   - 나오는 것: <mark>`web1` 은 `0.0.0.0:8080` 그대로이고, `web2` · `web3` 은 `127.0.0.1:` 으로 시작하면</mark> 됩니다.

   ```
   NAME                       IMAGE        COMMAND                  SERVICE   CREATED        STATUS                  PORTS
   anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      1 second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
   anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      1 second ago   Up Less than a second   127.0.0.1:8081->80/tcp
   anomaly_detection-web3-1   nginx:1.28   "/docker-entrypoint.…"   web3      1 second ago   Up Less than a second   127.0.0.1:8082->80/tcp
   ```

6. **[터미널]** 내 PC 에서는 세 서버가 모두 열려 있는지 확인합니다. `127.0.0.1` 로 제한한 서버도 **내 PC 에서는** 접속됩니다. 막히는 것은 다른 PC 에서 들어오는 요청입니다.

   ① `web1` 에 요청합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
   ```

   - 하는 일: 8080번 서버에 요청을 보내고 결과 번호만 보여 줍니다.
   - 나오는 것: <mark>결과 번호가 `200` 이면</mark> 됩니다.

   ```
   200
   ```

   ② `web2` 에 요청합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
   ```

   - 하는 일: 8081번 서버(내 PC 에서만 열린 서버)에 요청합니다.
   - 나오는 것: <mark>결과 번호가 `200` 이면</mark> 됩니다.

   ```
   200
   ```

   ③ `web3` 에 요청합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082
   ```

   - 하는 일: 8082번 서버(내 PC 에서만 열린 서버)에 요청합니다.
   - 나오는 것: <mark>결과 번호가 `200` 이면</mark> 됩니다.

   ```
   200
   ```

7. **[터미널]** (곁다리) 접속 범위와 재생성 확인이 끝난 뒤에 하는 로그 실습입니다. 서버를 지워도 접속 기록 파일이 내 `logs` 폴더에 남는 것을 확인합니다. 6번에서 `web3` 에 보낸 요청 한 건이 `logs/access.log` 첫 줄에 기록되어 있으니, 요청 두 개를 더 보냅니다.

   ① 없는 주소 `/.env` 를 요청합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/.env
   ```

   - 하는 일: 스캐너가 자주 찾는 설정 파일 주소를 요청합니다.
   - 나오는 것: 결과 번호가 `404` 이면 됩니다.

   ```
   404
   ```

   ② 없는 주소 `/phpmyadmin` 을 요청합니다.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/phpmyadmin
   ```

   - 하는 일: 스캐너가 자주 찾는 관리 화면 주소를 요청합니다.
   - 나오는 것: 결과 번호가 `404` 이면 됩니다.

   ```
   404
   ```

   ③ 로그 파일을 읽습니다.

   ```bash
   cat logs/access.log
   ```

   - 하는 일: `web3` 가 내 `logs` 폴더에 남긴 접속 기록을 보여 줍니다.
   - 나오는 것: <mark>요청 3줄(`200` 하나, `404` 둘)이 보이면</mark> 됩니다. IP 와 시각은 사람마다 다릅니다.

   ```
   172.18.0.1 - - [06/Nov/2026:03:37:43 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/8.7.1" "-"
   172.18.0.1 - - [06/Nov/2026:03:37:43 +0000] "GET /.env HTTP/1.1" 404 153 "-" "curl/8.7.1" "-"
   172.18.0.1 - - [06/Nov/2026:03:37:43 +0000] "GET /phpmyadmin HTTP/1.1" 404 153 "-" "curl/8.7.1" "-"
   ```

   ④ `404` 요청이 몇 개인지 셉니다.

   ```bash
   grep " 404 " logs/access.log | wc -l
   ```

   - 하는 일: `grep` 이 `404` 가 든 줄만 남기고, `|` 가 그 줄들을 `wc -l` 에 넘겨 줄 수를 셉니다. `404` 앞뒤의 공백까지 따옴표 안에 씁니다.
   - 나오는 것: <mark>`2` 가 나오면</mark> 됩니다.

   ```
   2
   ```

   ⑤ `404` 요청만 파일로 저장합니다.

   ```bash
   grep " 404 " logs/access.log > logs/web_404.log
   ```

   - 하는 일: ④ 와 같은 `grep` 인데 끝에 `> logs/web_404.log` 를 붙였습니다. `>` 는 화면에 나올 내용을 파일에 저장합니다.
   - 나오는 것: 화면에는 아무것도 나오지 않습니다. 내용이 파일로 들어갔기 때문입니다.

8. **[터미널]** 확인이 끝났으므로 세 서버를 모두 종료합니다. (곁다리) 서버를 지워도 `logs` 폴더의 기록이 남는지 봅니다.

   ① 서버를 모두 끄고 지웁니다.

   ```bash
   docker compose -f compose.secure.yaml down
   ```

   - 하는 일: 새 파일의 서버를 모두 끄고 지웁니다.
   - 나오는 것: `Stopped`, `Removed` 줄이 차례로 나옵니다.

   ```
    Container anomaly_detection-web1-1 Stopping
    Container anomaly_detection-web3-1 Stopping
    Container anomaly_detection-web2-1 Stopping
    Container anomaly_detection-web1-1 Stopped
    Container anomaly_detection-web1-1 Removing
    Container anomaly_detection-web1-1 Removed
    Container anomaly_detection-web2-1 Stopped
    Container anomaly_detection-web2-1 Removing
    Container anomaly_detection-web2-1 Removed
    Container anomaly_detection-web3-1 Stopped
    Container anomaly_detection-web3-1 Removing
    Container anomaly_detection-web3-1 Removed
    Network anomaly_detection_default Removing
    Network anomaly_detection_default Removed
   ```

   ② 로그 파일이 남았는지 봅니다.

   ```bash
   ls logs
   ```

   - 하는 일: `logs` 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: <mark>서버를 지웠는데도 `access.log` · `web_404.log` 가 보이면</mark> 됩니다. 이것이 볼륨으로 로그를 남기는 이유입니다.

   ```
   access.log
   error.log
   web_404.log
   ```

9. **[보고서]** `day05_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 1번과 5번의 `docker compose ps` 출력을 붙여 넣고, 접속 범위가 바뀐 기존 서비스와 새로 추가된 서비스를 따로 적어 주세요.
   - (나) 🔍 `"8081:80"` 과 `"127.0.0.1:8081:80"` 은 누가 접속할 수 있는지가 어떻게 다른가요? 관리 화면이나 데이터베이스 서버를 이렇게 설정하는 이유도 적어 주세요.
   - (다) 🔍 `up -d` 의 출력에서 `web1` 은 `Running`, `web2` 는 `Recreated`, `web3` 은 `Created` 였습니다. 서버마다 출력이 다른 이유와, 운영 중인 서비스의 설정을 바꿀 때 이것이 왜 도움이 되는지 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 명령 · 설정 |
|---|---|
| 서버를 내 PC 에서만 접속하게 | `ports:` 줄 앞에 `127.0.0.1:` → `"127.0.0.1:8081:80"` |
| 다른 컴포즈 파일로 적용 | `docker compose -f compose.secure.yaml up -d` |
| 접속 범위 읽기 | `docker compose -f compose.secure.yaml ps` 의 PORTS |
| (곁다리) 로그를 내 폴더에 연결 | `volumes: - ./logs:/var/log/nginx` |
| (곁다리) 찾고 세기 · 저장 | `grep " 404 " logs/access.log \| wc -l` · `… > logs/web_404.log` |
| 모두 끄고 지우기 | `docker compose -f compose.secure.yaml down` |


---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 오늘 한 일을 저장소에 올리는 마무리입니다.</mark> 6교시 마지막 약 10분에 합니다. 어느 터미널을 써도 되고, `pwd` 로 위치를 먼저 확인한 뒤 결과가 `anomaly_detection` 으로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「오늘 만든 컴포즈 파일과 로그 파일을 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `anomaly_detection` 폴더에 오늘 오전과 오후에 만든 파일이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `anomaly_detection` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day05_pm_report.md` 의 5 · 6교시 칸에서 `답:` 뒤와 코드 상자가 비어 있는 질문이 없는지도 봅니다(마무리 (가)는 3번에서 채웁니다).

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
   - 나오는 것: `compose.yaml` · `compose.secure.yaml` 과 `logs` 폴더가 보이면 됩니다.

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
   git commit -m "Add docker compose servers with limited access and web3 log files"
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

## 오늘 오후 마무리

| 확인 | 문제 |
|---|---|
| 컴포즈 파일로 서버 두 대를 한 번에 켜고 두 서버의 응답을 확인했다 | 오후 5-1 |
| 서버마다 접속 범위를 정해 컴포즈 파일로 적용했고, 바뀐 서버만 다시 켜지는 것을 확인했다 | 오후 6-1 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 마무리 |

다음 수업은 11/9(월)입니다. <mark>월요일 오전에는 이번 주에 만든 탐지를 한 번에 돌리는 통합 실습을 합니다.</mark> 오늘 저장한 로그 파일을 그 실습에서 다시 씁니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark>

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
docker ps --filter publish=8080 --filter publish=8081 --filter publish=8082
docker images nginx:1.28
docker pull nginx:1.28
docker run -d --rm -p 8080:80 --name web-run nginx:1.28
docker ps
docker stop web-run
touch compose.yaml
ls
docker compose up -d
docker compose ps
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
```
- 명령 풀이: `docker ps --filter publish=포트번호` 그 포트를 쓰는 서버 확인(줄이 나오면 `docker stop 이름` 으로 끔) · `docker images 이름:버전` 받아 둔 이미지 확인(있으면 `docker pull` 은 건너뜀) · `docker compose up -d` 컴포즈 파일의 서버를 모두 백그라운드에서 켬 · `docker compose ps` 컴포즈로 켠 서버의 상태 보기 · `curl 주소` 그 주소에 요청을 보내 결과 번호 보기

**결과**

- (가) 서버 켜기 · 확인 명령과 결과를 친 순서대로 붙인 예입니다. 서비스 이름은 <mark style="background:#bde3ff">**`web1` · `web2`**</mark>, 포트는 <mark style="background:#bde3ff">**8080 · 8081**</mark>입니다.

  ```
  $ docker images nginx:1.28
  IMAGE        ID             DISK USAGE   CONTENT SIZE   EXTRA
  nginx:1.28   146adea4768b        258MB         64.1MB   U
  $ docker run -d --rm -p 8080:80 --name web-run nginx:1.28
  e1a2ad01c5441866eae9a81e97aa28caabf3a1efdd4c12bf66817887c63237a4
  $ docker ps
  CONTAINER ID   IMAGE        COMMAND                  CREATED                  STATUS                  PORTS                                     NAMES
  e1a2ad01c544   nginx:1.28   "/docker-entrypoint.…"   Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web-run
  $ docker stop web-run
  web-run
  $ docker compose up -d
   Network anomaly_detection_default Creating
   Network anomaly_detection_default Created
   Container anomaly_detection-web1-1 Creating
   Container anomaly_detection-web2-1 Creating
   Container anomaly_detection-web1-1 Created
   Container anomaly_detection-web2-1 Created
   Container anomaly_detection-web2-1 Starting
   Container anomaly_detection-web1-1 Starting
   Container anomaly_detection-web2-1 Started
   Container anomaly_detection-web1-1 Started
  $ docker compose ps
  NAME                       IMAGE        COMMAND                  SERVICE   CREATED                  STATUS                  PORTS
  anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
  anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      Less than a second ago   Up Less than a second   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
  $ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
  200
  $ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
  200
  ```

  - 이미지가 없어서 `docker pull` 을 했다면 그 결과도 맨 앞에 붙입니다. 컨테이너 번호(긴 글자)와 시각은 사람마다 다릅니다.

- (나) 컴포즈가 더 나은 점의 예:
  - <mark style="background:#bde3ff">긴 옵션을 파일에 적어 두어서 누가 켜도 같은 서버가 켜집니다.</mark>
  - 명령 한 줄(`docker compose up -d`)로 서버 두 대를 한 번에 켜고 끌 수 있습니다.
  - 파일을 저장소에 올려 두면 서버 설정이 기록으로 남습니다.
- (다) 두 팀의 차이:
  - `docker run` 팀은 <mark style="background:#bde3ff">명령을 기억하지 못하면 포트 · 이름 · 이미지 버전을 알 수 없어서 같은 구성을 다시 켤 수 없고,</mark> 켠 기록도 남아 있지 않습니다.
  - 컴포즈 팀은 `compose.yaml` 과 깃허브 기록이 있어서 <mark style="background:#bde3ff">`docker compose up -d` 한 줄로 같은 구성을 다시 켤 수 있습니다.</mark>
  - 버전을 적어 두는 것이 중요한 이유: `nginx:1.28` 처럼 적어 두면 <mark style="background:#bde3ff">몇 주 뒤에도 같은 버전의 이미지로 켜서</mark> 사고 당시와 같은 환경이 됩니다. 이름만 적으면(`nginx`) 가장 최신 버전을 받아 와서 동작이 달라질 수 있어, 재현한 결과를 믿기 어렵습니다.
- (라) 바꿀 줄:
  - `web2` 의 <mark style="background:#bde3ff">`- "8081:80"` 에서 왼쪽 숫자만</mark> 다른 프로그램이 쓰지 않는 번호로 바꿉니다. 예: `- "8082:80"`
  - 서버 안이 그대로 `80` 인 이유: 콜론 <mark style="background:#bde3ff">왼쪽은 내 컴퓨터의 포트이고, 오른쪽은 서버(컨테이너) 안의 포트이기 때문입니다.</mark> 내 컴퓨터 쪽 번호만 바꿨으므로 서버 안은 달라지지 않습니다.
  - `curl` 이 달라지는 점: 요청 주소의 포트를 <mark style="background:#bde3ff">왼쪽 숫자로 바꿔서</mark> `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082` 로 칩니다. 다른 팀원은 그대로 `8081` 입니다.

**왜**

- <mark>서버 설정을 파일에 적어 두면 사람이 옵션을 외우거나 두 번 치지 않아도 되어서 실수가 줄고, 서버가 늘어도 명령은 그대로입니다.</mark>

**자주 틀리는 곳**

- 복습에서 켠 `web-run` 을 `docker stop web-run` 으로 끄지 않고 `docker compose up -d` 를 치면 <mark>**`web1` 서버가 켜지지 않습니다.**</mark> 같은 8080번 포트를 `web-run` 이 이미 쓰고 있기 때문입니다.
  - 이때 오류는 다음과 같습니다(<mark style="background:#ffc4d6">`port is already allocated`</mark> 가 나오면 이 실수입니다).

    ```
    Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint anomaly_detection-web1-1 (…): Bind for 0.0.0.0:8080 failed: port is already allocated
    ```

  - 고치는 방법: `docker stop web-run` 으로 복습 서버를 끄고, 이미 켜진 `web2` 까지 `docker compose down` 으로 정리한 뒤 `docker compose up -d` 를 다시 칩니다.
- `compose.yaml` 의 들여쓰기에 탭 문자가 들어가면 오류가 납니다. <mark>**VS Code 에서 붙여 넣으면 이 오류는 나지 않지만,**</mark> 탭 문자를 직접 넣었다면 이런 문구가 나옵니다.

    ```
    yaml: while scanning for the next token at line 3: found character that cannot start any token
    ```

  - 줄 번호는 사람마다 다릅니다.
- `docker compose up -d` 를 `compose.yaml` 이 없는 폴더에서 치면 `no configuration file provided: not found` 가 나옵니다. <mark>`pwd` 로 `anomaly_detection` 폴더인지 먼저 봅니다.</mark>

**관제에서는**

- 로그를 모으는 서버나 대응 대상 서버를 여러 대 켜야 할 때 컴포즈 파일 하나로 같은 환경을 다시 만듭니다. <mark>설정 파일을 저장소에 두면 누가 어느 PC 에서 켜도 같은 환경이 됩니다.</mark>

---

### 정답 6-1

💻 **터미널에 입력합니다.**

```bash
docker compose ps
mkdir logs
touch compose.secure.yaml
docker compose -f compose.secure.yaml up -d
docker compose -f compose.secure.yaml ps
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082
cat logs/access.log
grep " 404 " logs/access.log | wc -l
grep " 404 " logs/access.log > logs/web_404.log
docker compose -f compose.secure.yaml down
ls logs
```
- 명령 풀이: `-f 파일이름` 사용할 컴포즈 파일 지정 · `127.0.0.1:` 포트 줄 앞에 붙여 내 PC 에서만 접속 · `grep "글자" 파일` 그 글자가 든 줄만 남김 · `wc -l` 줄 수 세기 · `>` 출력을 파일에 저장

**결과**

- (가) 1번 출력은 두 서버 모두 `0.0.0.0:` 으로 시작하고, 5번 출력은 다음과 같습니다. 접속 범위가 바뀐 서비스는 <mark style="background:#bde3ff">**`web2`**</mark> 이고, 새로 생긴 서비스는 <mark style="background:#bde3ff">**`web3`**</mark> 입니다.

  ```
  NAME                       IMAGE        COMMAND                  SERVICE   CREATED        STATUS                  PORTS
  anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      1 second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
  anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      1 second ago   Up Less than a second   127.0.0.1:8081->80/tcp
  anomaly_detection-web3-1   nginx:1.28   "/docker-entrypoint.…"   web3      1 second ago   Up Less than a second   127.0.0.1:8082->80/tcp
  ```

- (나) `"8081:80"` 은 <mark style="background:#bde3ff">같은 네트워크의 다른 PC 에서도 접속할 수 있고</mark>, `"127.0.0.1:8081:80"` 은 <mark style="background:#bde3ff">내 PC 에서만 접속할 수 있습니다.</mark>
  - 이유: 관리 화면이나 데이터베이스는 필요한 사람만 쓰는 서버입니다. 밖에 열어 두면 스캐너가 `/phpmyadmin` 같은 주소를 찾아 들어올 수 있으므로 <mark style="background:#bde3ff">꼭 열어야 하는 서버만 열고 나머지는 `127.0.0.1:` 으로 제한합니다.</mark>
- (다) `web1` 은 <mark style="background:#bde3ff">설정이 바뀌지 않아서 `Running`</mark>, `web2` 는 <mark style="background:#bde3ff">포트 줄이 바뀌어서 기존 서버를 새 설정으로 다시 만들어 `Recreated`</mark>, `web3` 은 <mark style="background:#bde3ff">새로 추가한 서버라서 `Created`</mark> 였습니다.
  - 도움이 되는 점: 설정을 바꿔도 <mark style="background:#bde3ff">바뀐 서버만 다시 켜지고 나머지는 끊기지 않습니다.</mark> 운영 중인 서비스(`web1`)를 멈추지 않고 보안 설정을 고칠 수 있습니다.

**왜**

- <mark>서버마다 접속 범위를 파일에 적어 두면 설정 실수를 검토하기 쉽고, 같은 `up -d` 로 바뀐 서버만 적용하면 운영 중인 서비스가 끊기지 않습니다.</mark> 곁다리로 배운 볼륨은 서버를 지워도 접속 기록 파일을 내 폴더에 남겨 줍니다.

**자주 틀리는 곳**

- `up -d` 에 `-f compose.secure.yaml` 을 빼고 `docker compose up -d` 만 치면 <mark>**아무것도 바뀌지 않습니다.**</mark> 5교시의 `compose.yaml` 이 그대로 적용되기 때문입니다.
  - 이때 `ps` 의 PORTS 가 다음처럼 둘 다 `0.0.0.0:` 인 것이 이 실수의 모습입니다. `-f compose.secure.yaml` 을 붙여 다시 칩니다.

    ```
    SERVICE   PORTS
    web1      0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
    web2      0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
    ```

- 8082번 포트를 이미 다른 서버가 쓰고 있으면 `web3` 이 켜지지 않습니다. <mark>시작하기의 포트 확인에서 `8082` 도 비어 있는지 봅니다.</mark>
  - 이때 오류는 다음과 같습니다(<mark style="background:#ffc4d6">`port is already allocated`</mark> 가 나오면 이 실수입니다).

    ```
    Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint anomaly_detection-web3-1 (…): Bind for 0.0.0.0:8082 failed: port is already allocated
    ```

- `web2` 의 포트 줄에서 `127.0.0.1:` 을 빼고 `"8081:80"` 으로 쓰면 <mark>오류는 나지 않지만 다시 모두에게 열립니다.</mark> 보안 설정은 오류가 나지 않아도 PORTS 로 확인해야 합니다.

**관제에서는**

- 서버를 새로 켤 때 「누구에게 열지」를 먼저 정하고, 열어 둔 포트는 `ps` 의 PORTS 로 확인합니다. <mark>외부에 열린 포트를 점검하는 일은 보안 점검의 첫 단계입니다.</mark>

---

### 정답 마무리

- (가) 예: 「`git status` 에 `.env` 와 `.venv` 는 보이지 않았다」. 보였다면 `.gitignore` 맨 아래에 한 줄을 적고 저장한 뒤 `git status` 를 다시 쳐서 사라졌는지 확인했다고 적습니다.
- 깃허브의 `anomaly_detection` 폴더에 오늘 오전과 오후 파일(`compose.yaml` · `logs/web_404.log` 포함)이 보이면 됩니다.
