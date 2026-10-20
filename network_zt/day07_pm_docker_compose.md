# 10/20(화) 오후 · Docker ② — 어제 명령 복습 · 내 이미지 만들기 · 이미지 버전 다루기 — 실습

어제는 남이 만든 이미지(`nginx:1.28`)를 받아 서버를 켜고, `-v` 로 내 파일을 연결했습니다. 오늘은 세 가지를 합니다.

- **5교시**: 어제 배운 명령을 같은 순서로 한 번 더 치고, 서버를 **두 대** 켜서 서버마다 접속 기록이 따로 쌓이는 것을 읽는다.
- **6교시**: 내 파일이 들어 있는 **내 이미지**를 직접 만든다(Dockerfile).
- **7교시**: 파일을 고쳐 새 이미지로 반영하고, 문제가 생기면 이전 버전으로 되돌리고, 쓰지 않는 이미지를 지운다. 마지막에 오늘 만든 것을 깃허브에 올린다.

## 시작하기

**오후에 받은 파일 두 개를 `network_zt` 폴더로 옮깁니다.** VS Code 왼쪽 목록의 `network_zt` 폴더로 끌어다 놓거나, 탐색기(맥북은 Finder)로 옮깁니다.

- `day07_pm_docker_compose.md` (이 파일) — 오후 실습 안내. 읽기만 합니다.
- `day07_pm_report.md` — **오후 보고서.** 5 · 6 · 7교시 답을 여기에 적습니다.

1. **[VS Code]** 이 파일을 열고 `Ctrl + Shift + V`(맥북은 `Cmd + Shift + V`)를 누릅니다 — 왼쪽.
2. **[VS Code]** `day07_pm_report.md` 를 오른쪽 클릭 › **Open to the Side** — 오른쪽. 질문마다 `쓸 내용:` 을 보고 `답:` 뒤에 씁니다.
3. 문제는 **할 일 → 순서**대로 합니다. 순서 앞의 `[창 이름]` 이 지금 쓸 창입니다. 막히면 문서 맨 아래 「정답」을 봅니다.
4. **[터미널]** Docker Desktop 이 켜져 있는지 확인하고, 어제 켠 컨테이너가 남아 있으면 지웁니다. 아래 첫 줄이 에러 없이 표를 보여 주면 켜져 있는 것입니다. 에러가 나면 Docker Desktop 을 실행하고 **Engine running** 이 될 때까지 기다린 뒤 다시 칩니다.
   ```bash
   docker ps -a
   ```
   - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
   - `NAMES` 열의 `web` · `web-one` · `web-two` 같은 어제 컨테이너가 보이면 아래 명령으로 지웁니다. 없는 이름에는 `No such container` 가 나와도 괜찮습니다.
   - 이름이 달라도 `PORTS` 열에 `8080` 이나 `8081` 이 보이는 컨테이너는 `docker rm -f 이름` 으로 지웁니다.
   - 지운 뒤 `docker ps -a` 에 `IMAGE` 열이 `hello-world` 인 줄만 남아야 합니다.
   ```bash
   docker rm -f web web-one web-two
   ```
   - 명령 풀이: `docker rm` 꺼진 컨테이너를 지움 · `-f` 켜져 있어도 끄고 지움 · `web` · `web-one` · `web-two` 대상 컨테이너 이름
   - 지운 결과를 봅니다. `IMAGE` 칸이 `hello-world` 인 줄만 남으면 됩니다.
     ```bash
     docker ps -a
     ```
     - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두

> 오늘도 명령은 모두 **터미널**에서 칩니다(윈도에서는 Git Bash). 어제 배운 `MSYS_NO_PATHCONV=1`(Git Bash 가 경로를 자동으로 바꾸지 못하게 끄는 설정)은 오늘 5-1 의 서버를 켜는 명령 두 개와 서버 안 파일을 보는 명령 한 개, **세 곳에만** 붙입니다. 맥북은 붙이지 않고 칩니다. 이미지는 7교시 7-2 에서 `docker rmi` 로 지웁니다. 그 전에는 지우지 않습니다. 오늘 쓰는 `nginx:1.28` 은 어제 받았으므로 새로 받지 않습니다.

작업 폴더는 `network_zt` 안에 `day07_docker` 로 만듭니다.

```bash
pwd
```
- 명령 풀이: `pwd` 지금 있는 폴더 위치를 보여 줌

- 결과가 `…/network_zt` 로 끝나지 않으면 `cd network_zt` 로 이동한 뒤 다시 `pwd` 를 칩니다.

- 작업 폴더 `day07_docker` 를 만듭니다.
  ```bash
  mkdir -p day07_docker
  ```
  - 명령 풀이: `mkdir` 폴더를 만듦 · `-p` 이미 있어도 에러 없이 넘어감
- 만든 작업 폴더로 들어갑니다.
  ```bash
  cd day07_docker
  ```
  - 명령 풀이: `cd day07_docker` `day07_docker` 로 옮겨 감
- 지금 위치를 확인합니다. `…/day07_docker` 로 끝나야 합니다.
  ```bash
  pwd
  ```
  - 명령 풀이: `pwd` 지금 있는 폴더 위치를 보여 줌

- 마지막 `pwd` 가 `…/network_zt/day07_docker` 로 끝나면 됩니다. 터미널을 새로 열었다면 `network_zt` 로 이동한 뒤 `cd day07_docker` 를 다시 칩니다.

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">5교시 (14:00–14:50) · 어제 명령 복습 · 서버 두 대 켜고 접속 기록 구분해 읽기</mark>

> 📨 **오늘 들어온 일**
> A사 보안 담당이 보낸 메시지: 「고객용 안내 페이지와 직원용 안내 페이지를 서버 두 대로 따로 켜 주세요. 고객용(`site-three`)은 8082번, 직원용(`site-four`)은 8083번입니다. 이상한 접속이 생기면 어느 페이지에 온 요청인지 바로 가려야 하니, 접속 기록이 서버마다 따로 남는지 확인해 주세요.」
> - 이 교시에서 하는 일: 어제 배운 명령(`run -d --name -p -v` · `ps` · `logs` · `exec` · `stop` · `rm`)으로 서버 두 대(`web-three` · `web-four`)를 켜고, 서버마다 접속 기록이 따로 쌓이는 것을 읽은 뒤, 두 대를 끄고 지웁니다(5-1).
> - 끝나면 쓰는 것: **보고서 한 줄**(보안 담당에게 보낼 답 한 문장)

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

1. 도커 명령은 처음에는 낯섭니다. 어제 명령을 같은 순서로 한 번 더 치면 순서와 옵션이 손에 익습니다.
2. 같은 이미지로 서버를 여러 대 켤 때는 이름(`--name`)과 내 PC 포트(`-p`)로 서버를 구분합니다. 이렇게 여러 대를 켜는 일을 파일 하나에 적어 한 번에 켜는 방법(Docker Compose)은 4과목 첫날 배웁니다.
3. 서버가 여러 대면 접속 기록도 서버마다 따로 쌓입니다. 관제는 「어느 서버의 기록인가」를 구분해서 읽어야 합니다.

### 📖 5.1 어제 명령 한눈에

> ⚠ **읽기만 합니다 — 따라 치지 않습니다.** 아래 「✍️ 문제 5-1」에서 순서대로 칩니다.

| 명령 | 필요한 상황 | 달라지는 점 |
|---|---|---|
| `docker run -d --name 이름 -p 내포트:80 이미지` | 서버를 켜고 싶다 | 컨테이너가 백그라운드로 켜지고 내 PC 포트로 접속된다 |
| `-v "$(pwd)/폴더:/usr/share/nginx/html:ro"` (`run` 의 옵션) | 내 PC 파일을 서버가 보여 주게 하고 싶다 | 내 폴더의 파일이 서버의 화면이 된다 |
| `docker ps` | 지금 켜져 있는 서버를 보고 싶다 | 켜진 컨테이너만 나온다 |
| `docker ps -a` | 꺼진 서버까지 보고 싶다 | 꺼진 컨테이너(`Exited`)도 나온다 |
| `docker logs 이름` | 한 서버의 접속 기록이 보고 싶다 | 그 서버의 시작 메시지와 접속 기록만 나온다 |
| `docker exec 이름 명령` | 서버 안에서 명령을 실행하고 싶다 | 어제의 `exec -it … sh` 와 달리 명령 하나만 실행하고 바로 돌아온다 |
| `docker stop 이름` | 서버를 끄고 싶다 | `ps` 에서는 보이지 않고 `ps -a` 에는 `Exited` 로 남는다 |
| `docker rm 이름` | 꺼진 서버를 지우고 싶다 | `ps -a` 에서도 보이지 않는다 |

### 📖 5.2 서버가 두 대일 때 구분하는 법

> ⚠ **읽기만 합니다 — 따라 치지 않습니다.** 아래 「✍️ 문제 5-1」에서 칩니다.

```
이미지 nginx:1.28 (하나)
  ├─ docker run → 서버 web-three : 내 PC 8082 번 · 연결한 폴더 site-three
  └─ docker run → 서버 web-four  : 내 PC 8083 번 · 연결한 폴더 site-four
```

- 두 서버가 같은 것: 이미지 `nginx:1.28`
- 두 서버가 다른 것: 이름 · 내 PC 포트 · 연결한 폴더. 그래서 화면도 서로 다릅니다(고객용 · 직원용)
- `docker logs 이름`: 그 이름의 서버가 받은 요청만 기록에 나옵니다. 8082 로 온 요청은 `web-three` 의 기록에만, 8083 으로 온 요청은 `web-four` 의 기록에만 남습니다
- 이름을 공백으로 이어 쓰면 한 번에 여러 개를 처리합니다. 예: `docker stop web-three web-four`

### <mark>✍️ 문제 5-1 · 어제와 같은 명령으로 서버 두 대를 켜고 접속 기록을 구분해 읽기</mark>

**📍 이런 상황이 있습니다**

- 보안 담당이 「고객용 · 직원용 안내 페이지를 서버 두 대로 따로 켜 달라」고 합니다. 보는 사람이 다른 페이지라서, 이상한 접속이 생기면 어느 페이지에 온 요청인지 가려야 합니다. 담당자는 어제와 같은 순서로 `web-three`(8082)와 `web-four`(8083)를 켜고, 서버마다 접속 기록이 따로 남는지 읽고, 정리해야 합니다.
- 현업에서는 같은 명령을 서버 이름과 포트만 바꿔 반복해서 서버를 늘립니다. 기록을 읽을 때는 어느 서버의 기록인지부터 구분합니다.

**🎯 할 일**

1. <mark>`site-three/index.html`</mark> 과 <mark>`site-four/index.html`</mark> 을 만듭니다.
2. <mark>`web-three`</mark>(8082)와 <mark>`web-four`</mark>(8083)를 켜고 `ps` · 브라우저로 확인합니다.
3. <mark>`logs`</mark> 로 서버마다 접속 기록이 따로 쌓인 것을 읽습니다.
4. <mark>`stop` → `rm`</mark> 으로 둘 다 정리하고 `ps` · `ps -a` 로 달라진 점을 봅니다.

**순서**

1. **[터미널]** 작업 폴더가 `day07_docker` 인지 확인합니다.
   ```bash
   pwd
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더 위치를 보여 줌
   - 결과가 `…/network_zt/day07_docker` 로 끝나야 합니다. 아니면 `cd` 로 옮겨 갑니다.
2. **[터미널]** 두 서버가 보여 줄 폴더를 만듭니다.
   ```bash
   mkdir -p site-three site-four
   ```
   - 명령 풀이: `mkdir` 폴더를 만듦 · `-p` 이미 있어도 에러 없이 넘어감 · `site-three` · `site-four` 만들 폴더 이름 두 개(공백으로 이어 쓰면 한 번에 만듦)
3. **[VS Code 또는 터미널]** `site-three/index.html` 을 만듭니다. 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**
     1. VS Code 왼쪽 목록에서 `day07_docker` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 `site-three/index.html` 라고 입력하고 Enter 를 누릅니다. 앞쪽 폴더가 아직 없으면 함께 만들어집니다.
     4. 열린 파일에 내용을 입력하고 저장합니다.
   - **방법 2 · touch**: `touch site-three/index.html` → VS Code 에서 파일을 열어 글 입력
   - **방법 3 · vim 으로 만들기**: `vim site-three/index.html` → `i` → 글 입력 → `Esc` → `:wq` Enter

   파일 내용입니다.
   ```html
   <meta charset="utf-8">
   <h1>site-three</h1>
   <p>고객 안내 페이지입니다</p>
   ```
4. **[VS Code 또는 터미널]** `site-four/index.html` 도 같은 방법으로 만듭니다. 아래 세 가지 방법 중 **하나만** 고릅니다.
   - **방법 1 · VS Code 에서 만들기**
     1. VS Code 왼쪽 목록에서 `day07_docker` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 `site-four/index.html` 라고 입력하고 Enter 를 누릅니다. 앞쪽 폴더가 아직 없으면 함께 만들어집니다.
     4. 열린 파일에 내용을 입력하고 저장합니다.
   - **방법 2 · touch**: `touch site-four/index.html` → VS Code 에서 파일을 열어 글 입력
   - **방법 3 · vim 으로 만들기**: `vim site-four/index.html` → `i` → 글 입력 → `Esc` → `:wq` Enter

   파일 내용입니다.
   ```html
   <meta charset="utf-8">
   <h1>site-four</h1>
   <p>직원 안내 페이지입니다</p>
   ```
5. **[터미널]** 두 파일이 모두 있는지 봅니다.
   ```bash
   ls site-three site-four
   ```
   - 명령 풀이: `ls` 폴더 안의 파일 목록을 보여 줌 · `site-three` · `site-four` 볼 폴더 두 개
   - 화면:
     ```
     site-four:
     index.html

     site-three:
     index.html
     ```
6. **[터미널]** 8082 번과 8083 번을 쓰는 컨테이너가 없는지 확인합니다. `PORTS` 열에 `8082` · `8083` 이 보이는 컨테이너가 없어야 합니다.
   ```bash
   docker ps -a
   ```
   - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
   - `8082` 나 `8083` 을 쓰는 컨테이너가 있으면 `docker rm -f 이름` 으로 지웁니다.
7. **[터미널]** `web-three` 를 켭니다. 내 `site-three` 폴더가 컨테이너에 읽기 전용으로 연결됩니다.
   ```bash
   MSYS_NO_PATHCONV=1 docker run -d --name web-three -p 8082:80 -v "$(pwd)/site-three:/usr/share/nginx/html:ro" nginx:1.28
   ```
   맥북은 `MSYS_NO_PATHCONV=1 ` 을 빼고 칩니다.
   - 명령 풀이: `MSYS_NO_PATHCONV=1` Git Bash 가 경로를 바꾸지 못하게 끔(이 명령 한 번만) · `docker run` 이미지로 컨테이너를 만들어 켬 · `-d` 백그라운드로 실행(터미널을 계속 쓸 수 있음) · `--name web-three` 컨테이너 이름 붙이기 → `web-three` · `-p 8082:80` 내 PC 8082 포트를 컨테이너 80 포트에 연결(모든 주소로 열림) · `-v "$(pwd)/site-three:/usr/share/nginx/html:ro"` 내 `site-three` 폴더를 컨테이너 안 폴더에 읽기 전용으로 연결 · `nginx:1.28` 쓸 이미지(이름:태그)
   - 긴 영문 숫자 한 줄(컨테이너 ID)이 나오면 켜진 것입니다. 값은 PC마다 다릅니다.
8. **[터미널]** `web-four` 를 켭니다. 이름 · 포트 · 폴더만 `web-four` · `8083` · `site-four` 로 바뀝니다.
   ```bash
   MSYS_NO_PATHCONV=1 docker run -d --name web-four -p 8083:80 -v "$(pwd)/site-four:/usr/share/nginx/html:ro" nginx:1.28
   ```
   맥북은 `MSYS_NO_PATHCONV=1 ` 을 빼고 칩니다.
   - 명령 풀이: `MSYS_NO_PATHCONV=1` Git Bash 가 경로를 바꾸지 못하게 끔(이 명령 한 번만) · `docker run` 이미지로 컨테이너를 만들어 켬 · `-d` 백그라운드로 실행(터미널을 계속 쓸 수 있음) · `--name web-four` 컨테이너 이름 붙이기 → `web-four` · `-p 8083:80` 내 PC 8083 포트를 컨테이너 80 포트에 연결(모든 주소로 열림) · `-v "$(pwd)/site-four:/usr/share/nginx/html:ro"` 내 `site-four` 폴더를 컨테이너 안 폴더에 읽기 전용으로 연결 · `nginx:1.28` 쓸 이미지(이름:태그)
9. **[터미널]** 켜진 서버를 봅니다. 두 서버 모두 `STATUS` 가 `Up` 이고, `PORTS` 가 각각 `8082` · `8083` 이어야 합니다.
   ```bash
   docker ps
   ```
   - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록
   - 화면(맥북에서 실제로 나온 모양이고 `CONTAINER ID` · `CREATED` 는 PC마다 다릅니다. 나중에 켠 서버가 위에 나옵니다):
     ```
     CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                     NAMES
     fc7a977b1fcb   nginx:1.28   "/docker-entrypoint.…"   3 seconds ago   Up 3 seconds   0.0.0.0:8083->80/tcp, [::]:8083->80/tcp   web-four
     3a7d71ccb3cc   nginx:1.28   "/docker-entrypoint.…"   3 seconds ago   Up 3 seconds   0.0.0.0:8082->80/tcp, [::]:8082->80/tcp   web-three
     ```
10. **[브라우저]** `http://127.0.0.1:8082` 를 엽니다. 제목 **site-three** 와 「고객 안내 페이지입니다」가 보이면 성공입니다. 이어서 새로 고침(`F5`)을 **두 번** 누릅니다. 8082 로 모두 세 번 접속한 것이 됩니다.
    - 「Welcome to nginx!」가 보이면 `-v` 연결이 안 된 것입니다. 윈도에서 `MSYS_NO_PATHCONV=1 ` 을 빠뜨렸는지 봅니다. `docker rm -f web-three` 로 지우고 7번을 다시 칩니다.
11. **[브라우저]** `http://127.0.0.1:8083` 을 **한 번만** 엽니다. 제목 **site-four** 와 「직원 안내 페이지입니다」가 보이면 성공입니다.
    - 「Welcome to nginx!」가 보이면 위와 같은 이유입니다. `docker rm -f web-four` 로 지우고 8번을 다시 칩니다.
12. **[터미널]** `web-three` 의 접속 기록을 봅니다. 맨 아래에 `"GET / HTTP/1.1"` 줄이 **세 개** 있습니다(8082 로 세 번 접속했기 때문입니다).
    ```bash
    docker logs web-three
    ```
    - 명령 풀이: `docker logs` 컨테이너의 기록(시작 메시지 · 접속 기록)을 봄 · `web-three` 대상 컨테이너 이름
    - 화면(맥북에서 `curl` 로 세 번 접속한 모양입니다. 브라우저로 접속하면 맨 뒤가 브라우저 이름으로 나오고, 새로 고침한 줄은 응답 번호가 `304` 일 수 있습니다. 시각 · IP 는 PC마다 다릅니다):
      ```
      /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
      /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
      10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
      10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
      /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
      /docker-entrypoint.sh: Configuration complete; ready for start up
      2026/10/19 14:19:56 [notice] 1#1: using the "epoll" event method
      2026/10/19 14:19:56 [notice] 1#1: nginx/1.28.3
      2026/10/19 14:19:56 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
      2026/10/19 14:19:56 [notice] 1#1: OS: Linux 6.12.76-linuxkit
      2026/10/19 14:19:56 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
      2026/10/19 14:19:56 [notice] 1#1: start worker processes
      2026/10/19 14:19:56 [notice] 1#1: start worker process 30
      2026/10/19 14:19:56 [notice] 1#1: start worker process 31
      2026/10/19 14:19:56 [notice] 1#1: start worker process 32
      2026/10/19 14:19:56 [notice] 1#1: start worker process 33
      2026/10/19 14:19:56 [notice] 1#1: start worker process 34
      2026/10/19 14:19:56 [notice] 1#1: start worker process 35
      2026/10/19 14:19:56 [notice] 1#1: start worker process 36
      2026/10/19 14:19:56 [notice] 1#1: start worker process 37
      192.168.65.1 - - [19/Oct/2026:14:19:59 +0000] "GET / HTTP/1.1" 200 83 "-" "curl/8.7.1" "-"
      192.168.65.1 - - [19/Oct/2026:14:19:59 +0000] "GET / HTTP/1.1" 200 83 "-" "curl/8.7.1" "-"
      192.168.65.1 - - [19/Oct/2026:14:19:59 +0000] "GET / HTTP/1.1" 200 83 "-" "curl/8.7.1" "-"
      ```
    - 브라우저가 따로 요청하는 `/favicon.ico` 의 `404` 줄이 함께 보여도 정상입니다. 세는 것은 `"GET / HTTP/1.1"` 줄입니다.
13. **[터미널]** `web-four` 의 접속 기록을 봅니다. 이번에는 `"GET / HTTP/1.1"` 줄이 **한 개**뿐입니다(8083 으로 한 번 접속했기 때문입니다).
    ```bash
    docker logs web-four
    ```
    - 명령 풀이: `docker logs` 컨테이너의 기록(시작 메시지 · 접속 기록)을 봄 · `web-four` 대상 컨테이너 이름
    - 화면:
      ```
      /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
      /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
      10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
      10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
      /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
      /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
      /docker-entrypoint.sh: Configuration complete; ready for start up
      2026/10/19 14:19:56 [notice] 1#1: using the "epoll" event method
      2026/10/19 14:19:56 [notice] 1#1: nginx/1.28.3
      2026/10/19 14:19:56 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
      2026/10/19 14:19:56 [notice] 1#1: OS: Linux 6.12.76-linuxkit
      2026/10/19 14:19:56 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
      2026/10/19 14:19:56 [notice] 1#1: start worker processes
      2026/10/19 14:19:56 [notice] 1#1: start worker process 29
      2026/10/19 14:19:56 [notice] 1#1: start worker process 30
      2026/10/19 14:19:56 [notice] 1#1: start worker process 31
      2026/10/19 14:19:56 [notice] 1#1: start worker process 32
      2026/10/19 14:19:56 [notice] 1#1: start worker process 33
      2026/10/19 14:19:56 [notice] 1#1: start worker process 34
      2026/10/19 14:19:56 [notice] 1#1: start worker process 35
      2026/10/19 14:19:56 [notice] 1#1: start worker process 36
      192.168.65.1 - - [19/Oct/2026:14:19:59 +0000] "GET / HTTP/1.1" 200 82 "-" "curl/8.7.1" "-"
      ```
    - 8082 로 온 요청은 `web-three` 에만, 8083 으로 온 요청은 `web-four` 에만 기록되었습니다. 응답 크기(`200` 뒤의 숫자)가 `83` 과 `82` 로 다른 것은 두 서버가 보여 준 파일이 다르기 때문입니다.
14. **[터미널]** `web-four` 안에 내 파일이 있는지 봅니다. 서버 안 폴더에 `index.html` 이 보입니다.
    ```bash
    MSYS_NO_PATHCONV=1 docker exec web-four ls /usr/share/nginx/html
    ```
    맥북은 `MSYS_NO_PATHCONV=1 ` 을 빼고 칩니다.
    - 명령 풀이: `MSYS_NO_PATHCONV=1` Git Bash 가 경로를 바꾸지 못하게 끔(이 명령 한 번만) · `docker exec` 켜진 컨테이너 안에서 명령을 실행 · `web-four` 대상 컨테이너 이름 · `ls /usr/share/nginx/html` 컨테이너 안 폴더의 파일 목록 (어제의 `exec -it … sh` 와 달리 명령 하나만 실행하고 바로 돌아옴)
    - 화면: `index.html`
15. **[터미널]** 두 서버를 한 번에 끕니다.
    ```bash
    docker stop web-three web-four
    ```
    - 명령 풀이: `docker stop` 켜진 컨테이너를 끔 · `web-three` · `web-four` 대상 컨테이너 이름 두 개(공백으로 이어 쓰면 한 번에 끔)
    - 화면: 이름 두 줄 `web-three` · `web-four`
16. **[터미널]** 켜진 서버 목록을 봅니다. 두 서버가 모두 목록에 없어야 합니다.
    ```bash
    docker ps
    ```
    - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록
17. **[터미널]** 꺼진 것까지 봅니다. 두 서버의 `STATUS` 가 `Exited (0)` 으로 남아 있습니다.
    ```bash
    docker ps -a
    ```
    - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
18. **[터미널]** 꺼진 서버를 둘 다 지웁니다.
    ```bash
    docker rm web-three web-four
    ```
    - 명령 풀이: `docker rm` 꺼진 컨테이너를 지움 · `web-three` · `web-four` 대상 컨테이너 이름 두 개
    - 화면: 이름 두 줄 `web-three` · `web-four`
19. **[터미널]** 지운 결과를 봅니다. `web-three` · `web-four` 줄이 더 이상 보이지 않아야 합니다.
    ```bash
    docker ps -a
    ```
    - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
20. **[보고서]** `day07_pm_report.md` 의 `## 5교시` › `### 문제 5-1` 아래를 채웁니다.
    - (가) 내가 `web-three` 와 `web-four` 를 켠 `docker run` 명령 두 개를 붙여 넣어 주세요.
    - (나) 🔍 `docker ps` 에서 `web-three` 와 `web-four` 줄의 `PORTS` 값을 각각 적어 주세요.
    - (다) 🔍 8082 로 세 번, 8083 으로 한 번 접속했을 때 `docker logs web-three` 와 `docker logs web-four` 의 `"GET / HTTP/1.1"` 줄은 각각 몇 개였고, 왜 그렇게 나뉘나요?
    - (라) 🔍 `stop` 뒤에 `docker ps` 와 `docker ps -a` 에서 두 서버가 각각 어떻게 보였고, `rm` 뒤에는 어떻게 되었나요?
    - (한 줄) 보안 담당에게 보낼 답을 한 문장으로 적어 주세요.
    - 이 교시에서 새로 알게 된 것 하나를 적어 주세요.

### 5교시 한눈에

| 하려는 일 | 명령 · 옵션 |
|---|---|
| 서버 켜기 | `docker run -d --name 이름 -p 내포트:80 -v "$(pwd)/폴더:/usr/share/nginx/html:ro" nginx:1.28` |
| 서버가 여러 대일 때 구분 | 이름 · 내 PC 포트 · 연결한 폴더가 서버마다 다르다 |
| 한 서버의 접속 기록 | `docker logs 이름` |
| 서버 안에서 명령 하나 | `docker exec 이름 명령` |
| 여러 서버 한 번에 끄고 지우기 | `docker stop 이름1 이름2` → `docker rm 이름1 이름2` |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">6교시 (15:00–15:50) · 내 이미지 만들기 (Dockerfile)</mark>

> 📨 **오늘 들어온 일**
> A사 보안 담당이 보낸 메시지: 「안내 페이지 서버를 다른 PC에도 똑같이 넘기고 싶습니다. 5교시처럼 `-v` 로 폴더를 연결하면 폴더도 같이 보내야 하는데, 폴더 없이 이미지 하나만 보내도 서버가 똑같이 켜지게 할 수는 없나요?」
> - 이 교시에서 하는 일: 안내 웹 페이지 파일을 **이미지 안에 복사해 넣은** 내 이미지를 만들어 서버를 켭니다. 파일을 고치면 이미지를 새로 만들어야 반영된다는 것도 확인합니다.
> - 끝나면 쓰는 것: **보고서 한 줄**(보안 담당에게 보낼 답 한 문장)

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

1. 5교시의 `-v` 방식은 서버를 켜려면 **서버 이미지 + 내 폴더** 두 가지가 필요했습니다. 다른 PC에 넘기려면 폴더도 같이 보내야 하고, 폴더가 빠지면 기본 화면이 나옵니다.
2. 파일을 **이미지 안에 넣어 두면** 이미지 하나만 있으면 어느 PC에서나 같은 화면이 나옵니다. 같은 환경을 재현해야 하는 관제 도구나 테스트 서버를 넘길 때 이 방식을 씁니다.
3. 이미지를 만드는 방법을 적은 파일이 **Dockerfile** 입니다. 6교시에서는 두 줄짜리 Dockerfile 로 시작합니다.

### 📖 6.1 Dockerfile → build → image → run → container

> ⚠ **읽기만 합니다 — 따라 치지 않습니다.** 아래 「✍️ 문제 6-1」에서 칩니다.

```
Dockerfile (이미지를 만드는 방법을 적은 파일)
   +-- FROM nginx:1.28                                               (기존 이미지 지정)
   +-- COPY site-three/index.html /usr/share/nginx/html/index.html   (내 파일을 이미지 안에 복사)
   |
   | docker build
   v
이미지 my-nginx:1
   |
   | docker run
   v
컨테이너
```

- 위에서 아래로 **Dockerfile → 이미지 → 컨테이너** 순서입니다. `FROM` 은 새 이미지에 포함할 기존 이미지를 정하는 줄, `COPY` 는 내 파일을 이미지 안에 복사하는 줄입니다.

- **Dockerfile**(도커파일): 이미지를 만드는 방법을 적은 텍스트 파일. 이름은 `Dockerfile`(대문자 D, 확장자 없음)이고, 한 줄에 명령 하나를 씁니다.
- **`docker build`**(빌드): Dockerfile 을 읽어 이미지를 만드는 명령. 이미지 안에 내 파일이 들어갑니다.
- 어제 배운 이미지(서버 프로그램과 파일을 모아 둔 읽기 전용 파일)와 컨테이너(이미지를 실행한 것)는 그대로입니다. 오늘은 **이미지를 직접 만듭니다.**

### 📖 6.2 Dockerfile 두 줄의 뜻

| 줄 | 형식 | 하는 일 |
|---|---|---|
| `FROM` | `FROM 이미지:태그` | 새 이미지에 포함할 기존 이미지를 정한다. 새 이미지에는 이 이미지의 내용이 모두 들어간다 |
| `COPY` | `COPY 내PC경로 이미지안경로` | 내 PC의 파일을 이미지 안의 지정한 경로에 복사한다 |

- 이미지 안에서 nginx 가 응답하는 파일은 `/usr/share/nginx/html/index.html` 입니다. 어제 `ls` 로 본 그 파일입니다. 여기에 내 파일이 들어가면 기본 화면 대신 내 화면이 나옵니다.
- `FROM nginx:1.28` 은 `nginx:1.28` 이미지의 내용(nginx 프로그램과 기본 파일)을 새 이미지에 그대로 포함한다는 뜻입니다. 거기에 `COPY` 로 복사한 내 파일이 추가되고, 같은 경로에 있던 기본 파일은 내 파일로 바뀝니다.
- `COPY` 의 앞쪽 경로는 **Dockerfile 이 있는 폴더 기준**입니다. `site-three/index.html` 은 `day07_docker/site-three/index.html` 입니다.

### 📖 6.3 build 명령

> ⚠ **읽기만 합니다 — 따라 치지 않습니다.** 지금 치면 `Dockerfile` 이 없어 에러가 납니다. 아래 「✍️ 문제 6-1」에서 `Dockerfile` 을 만든 뒤 `day07_docker` 폴더에서 칩니다.

```bash
docker build -t my-nginx:1 .
```
- 명령 풀이: `docker build` Dockerfile 을 읽어 이미지를 만듦 · `-t my-nginx:1` 만든 이미지에 `이름:태그` 를 붙임 · `.` 지금 폴더의 Dockerfile 을 씀

| 부분 | 뜻 |
|---|---|
| `docker build` | 이미지를 만든다 |
| `-t my-nginx:1` | 만들 이미지에 `이름:태그` 를 붙인다. 이름은 내 마음대로, `:1` 은 내가 정한 버전 |
| `.` | Dockerfile 이 있는 폴더(= 지금 폴더). 마지막의 점을 빼먹으면 에러가 난다 |

### 📖 6.4 `-v` 방식과 이미지에 넣는 방식

```
5교시 (-v)
  내 PC  site-three/index.html  <==== 연결 ====>  컨테이너
  파일을 고치면 -> 서버가 바로 새 파일을 보여 준다

6교시 (이미지 안에 COPY)
  내 PC  site-three/index.html --COPY (build 할 때)--> 이미지 my-nginx:1 ---> 컨테이너
  파일을 고쳐도 -> 이미 만든 이미지는 그대로다
```

- 위가 5교시 방식, 아래가 6교시 방식입니다. 5교시에는 파일을 연결해 두었고, 6교시에는 build 하는 순간 파일을 복사해 이미지에 넣습니다.

| | `-v` 로 연결 | 이미지에 넣기 |
|---|---|---|
| 서버를 넘길 때 | 이미지 + 폴더 | 이미지 하나 |
| 파일을 고치면 | 새로 고침만 | 이미지를 다시 build 해야 반영 |
| 잘 맞는 때 | 자주 고치는 설정 · 페이지 | 내용이 바뀌지 않는 서버 |

### <mark>✍️ 문제 6-1 · Dockerfile 두 줄을 써서 내 이미지 만들기</mark>

**📍 이런 상황이 있습니다**

- 보안 담당이 「안내 페이지가 들어 있는 서버를 이미지 하나로 넘겨 달라」고 합니다. 담당자는 5교시에서 만든 `site-three/index.html` 을 이미지에 넣는 Dockerfile 을 쓰고, 이미지를 만들고, 그 이미지로 서버를 켜서 같은 화면이 나오는지 확인해야 합니다.
- 5교시의 `web-three` 는 `-v` 로 폴더를 연결했습니다. 이번에는 `-v` 없이 파일이 이미지 안에 들어 있습니다.
- 현업에서는 설정과 페이지를 이미지에 넣어 두면 어느 PC에서 켜도 같은 서버가 되고, 이미지 이름과 태그로 어느 버전인지 구분합니다.

**🎯 할 일**

1. <mark>`Dockerfile`</mark> 에 두 줄(`FROM` · `COPY`)을 적습니다.
2. <mark>`docker build`</mark> 로 이미지를 만들고 출력을 읽고, `docker images` 로 목록을 봅니다.
3. 그 이미지로 서버를 켜서 `-v` 없이도 <mark>같은 화면</mark>이 나오는지 접속합니다.

**순서**

1. **[터미널]** 작업 폴더가 `day07_docker` 이고, 5교시에서 만든 `site-three/index.html` 이 있는지 봅니다.
   ```bash
   pwd
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더 위치를 보여 줌
   - 결과가 `…/network_zt/day07_docker` 로 끝나야 합니다.
   ```bash
   ls site-three
   ```
   - 명령 풀이: `ls` 폴더 안의 파일 목록을 보여 줌 · `site-three` 볼 폴더
   - 화면: `index.html`. 없으면 5-1 의 3번 단계로 돌아가 `site-three/index.html` 을 먼저 만듭니다.
2. **[VS Code 또는 터미널]** `Dockerfile` 을 만듭니다. 아래 세 가지 방법 중 **하나만** 고릅니다. 파일 이름은 대문자 `D` 로 시작하고 확장자가 없습니다.
   - **방법 1 · VS Code 에서 만들기**
     1. VS Code 왼쪽 목록에서 `day07_docker` 폴더를 클릭해 선택합니다(선택하지 않으면 다른 폴더에 만들어집니다).
     2. 목록 위쪽의 **새 파일**(New File, 파일 모양에 `+`) 아이콘을 누릅니다.
     3. 이름 칸에 `Dockerfile` 이라고 입력하고 Enter 를 누릅니다.
     4. 열린 파일에 다음 3번의 두 줄을 입력하고 저장합니다.
   - **방법 2 · touch**: `touch Dockerfile` → VS Code 에서 파일을 열어 다음 3번의 두 줄을 입력
   - **방법 3 · vim 으로 만들기**: `vim Dockerfile` → `i` → 다음 3번의 두 줄 입력 → `Esc` → `:wq` Enter
3. **[VS Code 또는 vim]** `Dockerfile` 에 아래 두 줄을 적고 저장합니다.
   ```dockerfile
   FROM nginx:1.28
   COPY site-three/index.html /usr/share/nginx/html/index.html
   ```
   - 첫 줄 `FROM nginx:1.28`: 새 이미지에 포함할 기존 이미지로 `nginx:1.28` 을 지정합니다. 어제 받은 그 이미지입니다.
   - 둘째 줄 `COPY site-three/index.html /usr/share/nginx/html/index.html`: 내 PC의 `site-three/index.html` 을 이미지 안의 `/usr/share/nginx/html/index.html` 에 복사합니다.
     - 앞쪽 `site-three/index.html` 은 내 PC의 경로(Dockerfile 이 있는 폴더 기준)입니다.
     - 뒤쪽 `/usr/share/nginx/html/index.html` 은 이미지 안의 경로이고, nginx 가 응답하는 파일 자리입니다.
     - 두 경로는 공백 한 칸으로 구분하고, **줄바꿈 없이 한 줄로** 씁니다. 줄이 나뉘면 build 가 에러를 냅니다.
4. **[터미널]** 이미지를 만듭니다.
   ```bash
   docker build -t my-nginx:1 .
   ```
   - 명령 풀이: `docker build` Dockerfile 을 읽어 이미지를 만듦 · `-t my-nginx:1` 만든 이미지에 `이름:태그` 를 붙임 · `.` 지금 폴더의 Dockerfile 을 씀(마지막의 점을 빼먹으면 에러)
   - 화면(맥북에서 실제로 나온 모양입니다. 시간 · `sha256:` 뒤의 긴 숫자 · `transferring context` 의 크기는 PC마다 다릅니다):
     ```
     [+] Building 0.3s (7/7) FINISHED                                                                                       docker:desktop-linux
      => [internal] load build definition from Dockerfile                                                                                   0.0s
      => => transferring dockerfile: 113B                                                                                                   0.0s
      => [internal] load metadata for docker.io/library/nginx:1.28                                                                          0.0s
      => [internal] load .dockerignore                                                                                                      0.0s
      => => transferring context: 2B                                                                                                        0.0s
      => [internal] load build context                                                                                                      0.0s
      => => transferring context: 159B                                                                                                      0.0s
      => CACHED [1/2] FROM docker.io/library/nginx:1.28@sha256:146adea4768b83c607d0bdfa4188464e3da6e0a3ad4475db1d1d8f64f27c29cc             0.0s
      => => resolve docker.io/library/nginx:1.28@sha256:146adea4768b83c607d0bdfa4188464e3da6e0a3ad4475db1d1d8f64f27c29cc                    0.0s
      => [2/2] COPY site-three/index.html /usr/share/nginx/html/index.html                                                                  0.0s
      => exporting to image                                                                                                                 0.1s
      => => exporting layers                                                                                                                0.0s
      => => exporting manifest sha256:60a8b219ab1b6a935872dcd4546b38b25a0a1126ce0806439024959afd63d38e                                      0.0s
      => => exporting config sha256:68e848ad4d863af7b1482aa5d21b3ab3b73a64885384c41aebfe4f3c43d7e433                                        0.0s
      => => exporting attestation manifest sha256:d3e0e124f6749978b206ad85a516dca3cda6912f4c0d4d17d095b8c540683704                          0.0s
      => => exporting manifest list sha256:41b51c862dfbe1ddda2271dd559a5fbf37dbaa98b847d908672d99efb3def61d                                 0.0s
      => => naming to docker.io/library/my-nginx:1                                                                                      0.0s
      => => unpacking to docker.io/library/my-nginx:1                                                                                   0.0s
     ```
   - 이 출력에서 꼭 볼 곳은 다섯 군데입니다. 나머지 `exporting …` 줄은 만든 이미지를 저장하는 과정이라 지금은 몰라도 됩니다.
     - 맨 위 `[+] Building … FINISHED`: build 가 에러 없이 끝났다는 표시입니다. 시간은 PC마다 다릅니다.
     - `[internal] load build definition from Dockerfile` 아래 `transferring dockerfile: 113B`: 방금 쓴 `Dockerfile` 을 읽었다는 뜻입니다. 크기가 몇 B 달라도 줄바꿈 방식 차이일 수 있어 대부분 정상입니다. `FROM` · `COPY` 두 줄이 맞게 적혔는지 `cat Dockerfile` 로 확인합니다.
     - `[1/2] FROM docker.io/library/nginx:1.28@sha256:…`: Dockerfile 첫째 줄을 처리한 단계입니다. `nginx:1.28` 기존 이미지를 확인했고, `sha256:` 뒤의 긴 숫자는 그 이미지의 고유 번호입니다.
     - `[2/2] COPY site-three/index.html /usr/share/nginx/html/index.html`: Dockerfile 둘째 줄을 처리한 단계입니다. 이 줄이 있으면 내 파일이 이미지 안에 들어간 것입니다.
     - `naming to docker.io/library/my-nginx:1`: 완성한 이미지에 `my-nginx:1` 이름을 붙였다는 뜻입니다. 이 줄이 있어야 다음 `docker run` 에 이 이름을 쓸 수 있습니다.
   - 단계 앞의 `CACHED` 는 전에 같은 내용으로 이미 해 본 단계라 다시 하지 않고 저장해 둔 결과를 쓴 것입니다. 위 화면의 `[1/2] FROM` 앞 `CACHED` 는 어제 받은 `nginx:1.28` 을 그대로 쓴다는 뜻이고, PC마다 붙을 수도 안 붙을 수도 있습니다. 같은 명령을 한 번 더 치면 `[2/2] COPY` 앞에도 `CACHED` 가 붙습니다(아래는 두 번째로 친 화면입니다).
     ```
     [+] Building 0.1s (7/7) FINISHED                                                                                       docker:desktop-linux
      => [internal] load build definition from Dockerfile                                                                                   0.0s
      => => transferring dockerfile: 113B                                                                                                   0.0s
      => [internal] load metadata for docker.io/library/nginx:1.28                                                                          0.0s
      => [internal] load .dockerignore                                                                                                      0.0s
      => => transferring context: 2B                                                                                                        0.0s
      => [internal] load build context                                                                                                      0.0s
      => => transferring context: 72B                                                                                                       0.0s
      => [1/2] FROM docker.io/library/nginx:1.28@sha256:146adea4768b83c607d0bdfa4188464e3da6e0a3ad4475db1d1d8f64f27c29cc                    0.0s
      => => resolve docker.io/library/nginx:1.28@sha256:146adea4768b83c607d0bdfa4188464e3da6e0a3ad4475db1d1d8f64f27c29cc                    0.0s
      => CACHED [2/2] COPY site-three/index.html /usr/share/nginx/html/index.html                                                           0.0s
      => exporting to image                                                                                                                 0.0s
      => => exporting layers                                                                                                                0.0s
      => => exporting manifest sha256:60a8b219ab1b6a935872dcd4546b38b25a0a1126ce0806439024959afd63d38e                                      0.0s
      => => exporting config sha256:68e848ad4d863af7b1482aa5d21b3ab3b73a64885384c41aebfe4f3c43d7e433                                        0.0s
      => => exporting attestation manifest sha256:510cb5a060a9f162d4035ffe7a6c25cd052c48488f31061247bd519e8fed9f4b                          0.0s
      => => exporting manifest list sha256:d3f530d69fba9bd1ca9af6b4ec3113944abc6577198f8042ecfcaaef6731e23f                                 0.0s
      => => naming to docker.io/library/my-nginx:1                                                                                      0.0s
      => => unpacking to docker.io/library/my-nginx:1                                                                                   0.0s
     ```
5. **[터미널]** 만든 이미지가 목록에 있는지 봅니다.
   ```bash
   docker images
   ```
   - 명령 풀이: `docker images` 내 PC 에 받아 둔 이미지 목록
   - 화면(`ID` 는 PC마다 다릅니다):
     ```
     IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
     hello-world:latest   11a3eb1597e8       22.6kB         10.3kB
     my-nginx:1           d558389de9b8        255MB         61.2MB
     nginx:1.28           146adea4768b        258MB         64.1MB
     ```
   - `my-nginx:1` 이 새로 생긴 줄입니다. `nginx:1.28` 은 어제 받은 기존 이미지이고, 내 이미지는 그 내용을 포함해서 크기가 거의 같습니다(`DISK USAGE`).
   - `EXTRA` 열의 `U` 는 그 이미지로 켠 컨테이너가 있다는 표시입니다. 아직 켜지 않아서 비어 있습니다.
6. **[터미널]** 내 이미지로 서버를 켭니다. 5교시와 달리 `-v` 가 없고, 이름은 `my-site`, 내 PC 포트는 `8090` 입니다.
   ```bash
   docker run -d --name my-site -p 8090:80 my-nginx:1
   ```
   - 명령 풀이: `docker run` 이미지로 컨테이너를 만들어 켬 · `-d` 백그라운드로 실행(터미널을 계속 쓸 수 있음) · `--name my-site` 컨테이너 이름 붙이기 → `my-site` · `-p 8090:80` 내 PC 8090 포트를 컨테이너 80 포트에 연결(모든 주소로 열림) · `my-nginx:1` 쓸 이미지(이름:태그)
   - 긴 영문 숫자 한 줄(컨테이너 ID)이 나오면 켜진 것입니다. 값은 PC마다 다릅니다.
   - 에러가 나면:
     - `Bind for 0.0.0.0:8090 failed: port is already allocated`: 8090 을 다른 컨테이너가 쓰고 있습니다. `docker ps -a` 의 `PORTS` 열에서 `8090` 이 있는 줄의 `NAMES` 를 찾아 `docker rm -f 그 이름` 으로 지우고, 방금 만든 `my-site` 도 `docker rm -f my-site` 로 지운 뒤 다시 칩니다.
     - `The container name "/my-site" is already in use`: 같은 이름의 `my-site` 가 이미 있습니다. `docker rm -f my-site` 로 지우고 다시 칩니다.
   - 켜진 서버를 봅니다. `IMAGE` 칸이 `my-nginx:1`, `STATUS` 가 `Up`, `PORTS` 가 `8090` 이어야 합니다.
     ```bash
     docker ps
     ```
     - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록
     - 화면(`CONTAINER ID` · `CREATED` 는 PC마다 다릅니다):
       ```
       CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                     NAMES
       0d49b4650041   my-nginx:1   "/docker-entrypoint.…"   2 seconds ago   Up 2 seconds   0.0.0.0:8090->80/tcp, [::]:8090->80/tcp   my-site
       ```
7. **[브라우저]** `http://127.0.0.1:8090` 을 엽니다.
   - 화면: 큰 제목 **site-three** 와 그 아래 「고객 안내 페이지입니다」가 보이면 성공입니다. `-v` 를 쓰지 않았는데도 5교시와 같은 화면이 나오는 것은 파일이 이미지 안에 들어 있기 때문입니다.
   - 「Welcome to nginx!」가 보이면 내 이미지가 아니라 다른 nginx 서버가 답하고 있는 것입니다. 6번의 `docker ps` 에서 `IMAGE` 칸이 `my-nginx:1` 인지 확인합니다. `nginx:1.28` 이면 이름을 잘못 쓴 것이니 `docker rm -f my-site` 로 지우고 6번을 다시 칩니다.
8. **[보고서]** `day07_pm_report.md` 의 `## 6교시` › `### 문제 6-1` 아래를 채웁니다.
   - (가) 내가 쓴 Dockerfile 두 줄을 붙여 넣어 주세요.
   - (나) 🔍 `FROM` 과 `COPY` 가 각각 하는 일을 적어 주세요.
   - (다) 🔍 5교시와 달리 `docker run` 에 `-v` 가 없는데도 내 화면이 나오는 이유는 무엇인가요?
   - (라) 🔍 `docker build` 출력에서 `[2/2] COPY` 줄과 `naming to` 줄을 붙여 넣고, 각각 무엇을 알려 주는지 적어 주세요.

### 6교시 한눈에

| 하려는 일 | 명령 · 파일 |
|---|---|
| 이미지를 만드는 파일 | `Dockerfile` (`FROM` 기존 이미지 지정 · `COPY` 내 파일 복사) |
| 이미지 만들기 | `docker build -t 이름:태그 .` |
| 만든 이미지 보기 | `docker images` |
| 내 이미지로 서버 켜기 | `docker run -d --name 이름 -p 포트:80 이름:태그` |
| 파일을 고친 뒤 반영 | 새 태그로 다시 build → 서버 교체 |

---

# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">7교시 (16:00–16:50) · 이미지 버전 다루기 · 되돌리기 · 정리 · 올리기</mark>

> 📨 **오늘 들어온 일**
> A사 보안 담당이 보낸 메시지: 「안내 문구를 바꿨는데 서버에 반영이 안 됩니다. 반영해 주세요. 그리고 새 버전에 문제가 있으면 이전 버전으로 바로 돌아갈 수 있어야 하고, 쓰지 않는 이미지는 정리해 주세요.」
> - 이 교시에서 하는 일: 파일을 고친 뒤 새 이미지로 반영하고(7-1), 문제가 생겼다고 보고 이전 버전으로 되돌린 뒤 쓰지 않는 이미지를 지웁니다(7-2). 마지막에 오늘 만든 것을 깃허브에 올립니다(7-3).
> - 끝나면 쓰는 것: **보고서 한 줄**(보안 담당에게 보낼 답 한 문장)

> 📖 **읽을거리 — 문제가 아닙니다.** 이 아래부터 첫 「✍️ 문제」 전까지는 이 교시의 배경지식입니다. 답할 질문도 따라 칠 명령도 없으니 읽고 이해만 합니다.

### 📖 왜 필요한가

1. 6교시에서 만든 이미지는 만든 순간의 파일을 그대로 가집니다. 파일을 고쳐도 이미지가 자동으로 바뀌지 않으니, 고친 뒤에는 이미지를 다시 만들어야 합니다.
2. 이미지에 `:1` · `:2` 같은 태그를 붙여 두면, 새 버전에 문제가 생겼을 때 이전 태그로 서버를 다시 켜서 바로 되돌릴 수 있습니다.
3. 쓰지 않는 이미지는 디스크를 차지합니다. `docker rmi` 로 지우되, 컨테이너가 쓰고 있는 이미지는 지워지지 않으니 컨테이너부터 지웁니다.

### <mark>✍️ 문제 7-1 · 파일을 고쳐 보고, 이미지를 다시 만들어 반영하기</mark>

**📍 이런 상황이 있습니다**

- 보안 담당이 「안내 문구를 바꿨는데 서버에서는 예전 문구가 나온다」고 합니다. 담당자는 파일을 고치고, 반영되지 않는 것을 확인하고, 이미지를 새로 만들어 반영해야 합니다.
- 현업에서는 이미지에 파일을 넣어 두는 방식에서 이 일이 흔합니다. 그래서 이미지에 `:2` 같은 새 태그를 붙여, 어느 버전이 켜져 있는지 구분합니다.

**이 문제에서 확인하려는 것**: 이미지에 복사해 넣은 파일은 내 PC의 원본을 고쳐도 **자동으로 바뀌지 않습니다.** 컨테이너는 만들 때 정한 이미지를 계속 쓰기 때문에, 화면을 바꾸려면 새 이미지를 만들고 **컨테이너를 지운 뒤 새 이미지로 다시 만들어야** 합니다.

```
1. 내 PC 의 site-three/index.html 을 v2 로 고침
        → 이미 만든 이미지 my-nginx:1 은 그대로입니다 (안에는 v1 이 들어 있음)
2. 컨테이너 my-site 는 만들 때 정한 이미지 my-nginx:1 을 계속 씁니다
        → 브라우저에는 여전히 v1
3. docker build -t my-nginx:2 .
        → v2 가 들어 있는 새 이미지 my-nginx:2 가 생깁니다
4. 컨테이너 my-site 를 지움 (docker rm -f my-site)
        → 이름 my-site 와 8090 번이 비워집니다
5. my-nginx:2 로 my-site 를 새로 만듦
        → 브라우저에 v2
```

- 4번에서 `docker stop` 이 아니라 `docker rm -f` 를 쓰는 이유: `stop` 은 끄기만 해서 컨테이너와 이름 `my-site` 가 남습니다. 이름이 남아 있으면 같은 이름으로 새 컨테이너를 만들 수 없습니다.
- `docker rm -f my-site` 가 지우는 것은 **컨테이너뿐**입니다. 이미지(`my-nginx:1`)와 내 PC의 `site-three/index.html` 은 그대로 남습니다.

**🎯 할 일**

1. <mark>`site-three/index.html` 을 고치고</mark> 새로 고쳐도 반영되지 않는 것을 확인합니다.
2. <mark>`my-nginx:2`</mark> 로 이미지를 다시 만듭니다.
3. 기존 <mark>`my-site` 를 지우고</mark> `my-nginx:2` 로 다시 켭니다.

**순서**

1. **[VS Code 또는 vim]** `site-three/index.html` 의 `<h1>` 줄을 `<h1>site-three v2</h1>` 로 고쳐 저장합니다. VS Code 면 왼쪽 목록에서 `site-three/index.html` 을 열어 고치고 저장합니다. vim 이면 `vim site-three/index.html` 으로 열고 `i` → 고침 → `Esc` → `:wq` 입니다.
2. **[브라우저]** `http://127.0.0.1:8090` 을 새로 고칩니다. 아직 제목이 **site-three** 인 것이 정상입니다(`v2` 가 안 붙음). 서버가 쓰는 파일은 이미지 안에 복사된 것이라서 내 PC의 파일을 고쳐도 바뀌지 않습니다.
3. **[터미널]** 같은 Dockerfile 로 태그만 `2` 로 바꿔 이미지를 다시 만듭니다.
   ```bash
   docker build -t my-nginx:2 .
   ```
   - 명령 풀이: `docker build` Dockerfile 을 읽어 이미지를 만듦 · `-t my-nginx:2` 만든 이미지에 `이름:태그` 를 붙임 · `.` 지금 폴더의 Dockerfile 을 씀
   - 화면 아래쪽에 `naming to docker.io/library/my-nginx:2` 가 보이면 성공입니다. 6-1 과 비교할 곳은 `[2/2] COPY` 줄입니다. 파일 내용이 바뀌었으므로 이번에는 앞에 `CACHED` 가 붙지 않고 새로 복사합니다.
4. **[터미널]** 켜져 있는 서버를 지우고 `my-nginx:2` 로 다시 켭니다. `my-site` 는 `my-nginx:1` 을 쓰도록 만들어진 컨테이너라서, 새 이미지를 build 해도 쓰는 이미지가 바뀌지 않기 때문입니다.
   - `my-nginx:1` 로 켠 `my-site` 를 끄고 지웁니다.
     ```bash
     docker rm -f my-site
     ```
     - 명령 풀이: `docker rm` 꺼진 컨테이너를 지움 · `-f` 켜져 있어도 끄고 지움 · `my-site` 대상 컨테이너 이름
   - 지운 결과를 봅니다. `my-site` 줄이 더 이상 보이지 않습니다. 이름이 남아 있으면 바로 아래 명령에서 이름 충돌이 납니다.
     ```bash
     docker ps -a
     ```
     - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
   - 새로 만든 `my-nginx:2` 이미지로 `my-site` 를 다시 켭니다. 이름 `my-site` 와 8090 번이 비어 있어서 켜집니다.
     ```bash
     docker run -d --name my-site -p 8090:80 my-nginx:2
     ```
     - 명령 풀이: `docker run` 이미지로 컨테이너를 만들어 켬 · `-d` 백그라운드로 실행(터미널을 계속 쓸 수 있음) · `--name my-site` 컨테이너 이름 붙이기 → `my-site` · `-p 8090:80` 내 PC 8090 포트를 컨테이너 80 포트에 연결(모든 주소로 열림) · `my-nginx:2` 쓸 이미지(이름:태그)
5. **[브라우저]** `http://127.0.0.1:8090` 을 새로 고쳐 제목이 **site-three v2** 로 바뀌었는지 확인합니다. 바뀌지 않으면 `Ctrl + F5` 로 새로 고칩니다.
6. **[보고서]** `day07_pm_report.md` 의 `## 7교시` › `### 문제 7-1` 아래를 채웁니다.
   - (가) 파일을 고친 직후 새로 고침했을 때 화면에 무엇이 나왔나요?
   - (나) 🔍 파일을 고쳤는데도 화면이 바뀌지 않은 이유와, 바꾸려면 무엇을 해야 하는지 적어 주세요.
   - (다) 🔍 5교시의 `-v` 방식과 6교시의 이미지에 넣는 방식은 파일을 고쳤을 때 반영되는 방법이 어떻게 다른가요?

### 📖 7.1 `docker rmi` — 이미지 지우기

> 📖 **읽을거리** — 다음 문제의 배경지식입니다. 읽고 나서 아래 「✍️ 문제」로 갑니다. 여기 나오는 명령은 **따라 치지 않습니다.** 아래 「✍️ 문제 7-2」에서 칩니다.

| 명령 | 필요한 상황 | 달라지는 점 |
|---|---|---|
| `docker rmi 이름:태그` | 쓰지 않는 이미지를 지우고 싶다 | `docker images` 목록에서 그 줄이 없어진다 |
| `docker rm -f 이름` | 이미지를 쓰는 컨테이너가 있어 이미지가 안 지워진다 | 컨테이너가 없어지면 이미지를 지울 수 있다 |

- `docker rm` 은 **컨테이너**를 지우고, `docker rmi` 는 **이미지**를 지웁니다. 이름이 비슷하니 `rmi` 의 `i` 는 image 의 `i` 로 기억합니다.
- 컨테이너가 쓰고 있는 이미지를 지우려 하면 에러가 나고 이미지는 그대로 남습니다.

### <mark>✍️ 문제 7-2 · 이전 버전으로 되돌리고 쓰지 않는 이미지 지우기</mark>

**📍 이런 상황이 있습니다**

- 보안 담당이 「v2 로 바꿨는데 문제가 있어 보이니 이전 버전으로 바로 돌려 달라. 그리고 안 쓰는 이미지는 정리해 달라」고 합니다.
- 담당자는 `my-site` 를 `my-nginx:1` 로 다시 켜서 되돌리고, 안 쓰는 이미지를 지워야 합니다. 쓰는 이미지가 지워지지 않는 것도 확인합니다.
- 현업에서는 이미지에 `:1` · `:2` 같은 태그를 붙여 두는 이유가 이것입니다. 문제가 생겨도 이전 태그로 켜면 됩니다.

**🎯 할 일**

1. <mark>`my-site`</mark> 를 `my-nginx:1` 로 다시 켜 이전 화면으로 되돌립니다.
2. 쓰고 있는 이미지를 <mark>지우려 해 보고</mark> 에러를 읽습니다.
3. 안 쓰는 이미지를 지우고, 컨테이너를 지운 뒤 <mark>남은 이미지</mark>도 지웁니다.

**순서**

1. **[터미널]** v2(`my-nginx:2`)로 켜져 있는 `my-site` 를 지웁니다.
   ```bash
   docker rm -f my-site
   ```
   - 명령 풀이: `docker rm` 컨테이너를 지움 · `-f` 켜져 있어도 끄고 지움 · `my-site` 대상 컨테이너 이름
   - 화면: `my-site`
2. **[터미널]** 이번에는 이전 버전 `my-nginx:1` 로 `my-site` 를 켭니다.
   ```bash
   docker run -d --name my-site -p 8090:80 my-nginx:1
   ```
   - 명령 풀이: `docker run` 이미지로 컨테이너를 만들어 켬 · `-d` 백그라운드로 실행(터미널을 계속 쓸 수 있음) · `--name my-site` 컨테이너 이름 붙이기 → `my-site` · `-p 8090:80` 내 PC 8090 포트를 컨테이너 80 포트에 연결(모든 주소로 열림) · `my-nginx:1` 쓸 이미지(이름:태그)
   - 긴 영문 숫자 한 줄(컨테이너 ID)이 나오면 켜진 것입니다. 값은 PC마다 다릅니다.
3. **[터미널]** 켜진 서버를 봅니다. `IMAGE` 칸이 `my-nginx:1` 이어야 합니다.
   ```bash
   docker ps
   ```
   - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록
   - 화면(`CONTAINER ID` · `CREATED` 는 PC마다 다릅니다):
     ```
     CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                     NAMES
     80ea733b154c   my-nginx:1   "/docker-entrypoint.…"   2 seconds ago   Up 2 seconds   0.0.0.0:8090->80/tcp, [::]:8090->80/tcp   my-site
     ```
4. **[브라우저]** `http://127.0.0.1:8090` 을 새로 고칩니다. 제목이 **site-three** 로 돌아오면(`v2` 가 안 붙으면) 이전 버전으로 되돌아온 것입니다. 안 바뀌면 `Ctrl + F5` 로 새로 고칩니다.
5. **[터미널]** 이미지 목록을 봅니다. `my-nginx:1` 과 `my-nginx:2` 두 개가 있고, 켜진 컨테이너가 쓰는 `my-nginx:1` 에만 `U` 가 붙어 있습니다.
   ```bash
   docker images
   ```
   - 명령 풀이: `docker images` 내 PC 에 받아 둔 이미지 목록
   - 화면(`ID` 는 PC마다 다릅니다):
     ```
     IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
     hello-world:latest   11a3eb1597e8       22.6kB         10.3kB
     my-nginx:1           74eaeeb6495e        255MB         61.2MB   U
     my-nginx:2           b936d303b72a        255MB         61.2MB
     nginx:1.28           146adea4768b        258MB         64.1MB
     ```
6. **[터미널]** 쓰고 있는 `my-nginx:1` 을 지워 봅니다. 에러가 나는 것이 정상입니다.
   ```bash
   docker rmi my-nginx:1
   ```
   - 명령 풀이: `docker rmi` 이미지를 지움 · `my-nginx:1` 지울 이미지(이름:태그)
   - 화면:
     ```
     Error response from daemon: conflict: unable to delete my-nginx:1 (must be forced) - container 80ea733b154c is using its referenced image 74eaeeb6495e
     ```
   - 읽는 법: `container … is using its referenced image` 는 「컨테이너 `80ea…` 가 이 이미지를 쓰고 있다」는 뜻이라 지워지지 않습니다. 컨테이너 ID 는 3번의 `docker ps` 에서 본 `my-site` 의 ID 와 같습니다.
7. **[터미널]** 안 쓰는 `my-nginx:2` 는 지울 수 있습니다.
   ```bash
   docker rmi my-nginx:2
   ```
   - 명령 풀이: `docker rmi` 이미지를 지움 · `my-nginx:2` 지울 이미지(이름:태그)
   - 화면(`sha256:` 뒤의 긴 숫자는 PC마다 다릅니다):
     ```
     Untagged: my-nginx:2
     Deleted: sha256:b936d303b72a4f19c4c17564670602e8753424272c8ef671aea565131b66f118
     ```
   - `Untagged` 는 `my-nginx:2` 라는 이름을 뗐다는 뜻이고, `Deleted` 는 이미지 자체를 지웠다는 뜻입니다.
8. **[터미널]** 컨테이너를 먼저 지웁니다.
   ```bash
   docker rm -f my-site
   ```
   - 명령 풀이: `docker rm` 컨테이너를 지움 · `-f` 켜져 있어도 끄고 지움 · `my-site` 대상 컨테이너 이름
   - 화면: `my-site`
9. **[터미널]** 지운 결과를 봅니다. `my-site` 줄이 더 이상 보이지 않아야 합니다(`hello-world` 줄은 남아 있을 수 있습니다).
   ```bash
   docker ps -a
   ```
   - 명령 풀이: `docker ps` 켜져 있는 컨테이너 목록 · `-a` 꺼진 것까지 모두
10. **[터미널]** 이제 `my-nginx:1` 을 지웁니다.
    ```bash
    docker rmi my-nginx:1
    ```
    - 명령 풀이: `docker rmi` 이미지를 지움 · `my-nginx:1` 지울 이미지(이름:태그)
    - 화면(`sha256:` 뒤의 긴 숫자는 PC마다 다릅니다):
      ```
      Untagged: my-nginx:1
      Deleted: sha256:74eaeeb6495e980e4a00162158a2b219c3532639c42f9e82dd91bbac8ba75cf9
      ```
11. **[터미널]** 이미지 목록을 다시 봅니다. `my-nginx:1` · `my-nginx:2` 줄이 모두 없어야 합니다.
    ```bash
    docker images
    ```
    - 명령 풀이: `docker images` 내 PC 에 받아 둔 이미지 목록
    - 화면:
      ```
      IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
      hello-world:latest   11a3eb1597e8       22.6kB         10.3kB
      nginx:1.28           146adea4768b        258MB         64.1MB
      ```
12. **[보고서]** `day07_pm_report.md` 의 `## 7교시` › `### 문제 7-2` 아래를 채웁니다.
    - (가) 이전 버전으로 되돌린 뒤 `docker ps` 의 `IMAGE` 칸 값과 브라우저에 나온 제목을 적어 주세요.
    - (나) 🔍 쓰고 있는 `my-nginx:1` 을 `docker rmi` 로 지우려 했을 때 에러 문구의 핵심과, 어떻게 해결했는지 적어 주세요.
    - (다) 🔍 이미지에 `:1` · `:2` 같은 태그를 붙여 두면 문제가 생겼을 때 어떤 점이 좋은가요?
    - (한 줄) 보안 담당에게 보낼 답을 한 문장으로 적어 주세요.
    - 이 교시에서 새로 알게 된 것 하나를 적어 주세요.

### <mark>✍️ 문제 7-3 · 오늘 만든 것을 깃허브에 올리기</mark>

**📍 이런 상황이 있습니다**

- 팀장이 「오늘 만든 Dockerfile 과 실습 파일을 저장소에 남겨 달라」고 합니다. 올리기 전에 올라갈 파일을 확인하고, 비밀 키 파일(`.env`)이 섞이지 않았는지 봐야 합니다.

**🎯 할 일**

1. 터미널에서 <mark>`git status`</mark> 로 올라갈 파일을 확인합니다.
2. <mark>`git add .` → `git commit` → `git push`</mark> 순서로 올립니다.
3. 깃허브에서 <mark>`day07_docker` 폴더와 보고서 두 개</mark>가 보이는지 확인합니다.

**순서**

1. **[터미널]** `security-agent-toolkit` 폴더로 옮기고 위치를 확인합니다. 결과가 `…/security-agent-toolkit` 으로 끝나야 합니다.
   - 두 단계 위의 `security-agent-toolkit` 폴더로 옮깁니다. `..` 은 한 단계 위 폴더입니다.
     ```bash
     cd ../..
     ```
     - 명령 풀이: `cd ../..` `../..` 로 옮겨 감 · `..` 은 한 단계 위 폴더
   - 위치를 확인합니다. `…/security-agent-toolkit` 으로 끝나야 합니다.
     ```bash
     pwd
     ```
     - 명령 풀이: `pwd` 지금 있는 폴더 위치를 보여 줌
2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. 빨간 목록에 `.env` 나 `.venv` 가 보이면 올리지 않고 멈춥니다.
   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다. `.venv` 도 같은 방법으로 합니다.
   - `Untracked files:` 나 `modified:` 아래에 나오는 줄이 올라갈 파일입니다. 오늘 만든 `day07_docker` 폴더와 보고서 파일이 보여야 합니다.
   ```bash
   git status
   ```
   - 명령 풀이: `git status` 바뀐 파일 목록을 봄
3. **[보고서]** `### 문제 7-3` 아래를 채웁니다. 올리기 전에 채워야 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 빨간 목록에 줄이 몇 개였는지, 그 가운데 `.env` · `.venv` 가 있었는지 적어 주세요.
4. **[터미널]** 바뀐 파일을 모두 담고(`add`), 기록하고(`commit`), 올립니다(`push`).
   - 바뀐 파일을 모두 올릴 목록에 담습니다.
     ```bash
     git add .
     ```
     - 명령 풀이: `git add .` 바뀐 파일을 모두 올릴 목록에 담음
   - 올릴 내용을 한 줄 설명과 함께 기록합니다.
     ```bash
     git commit -m "Add day 7 docker image practice and report"
     ```
     - 명령 풀이: `git commit -m "…"` 담은 것을 설명 한 줄과 함께 기록
   - 기록한 것을 깃허브에 올립니다.
     ```bash
     git push
     ```
     - 명령 풀이: `git push` 기록을 깃허브에 올림
   - `git push` 가 거절(`rejected`)되면 `git pull` 을 입력해 받아 온 뒤 `git push` 를 다시 합니다
   - 편집기 화면이 뜨면 `Esc` 를 누르고 `:wq` 를 입력한 뒤 `Enter` 를 누릅니다
5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `network_zt` 폴더 안에 `day07_docker` 폴더와 오전 · 오후 보고서가 있는지 확인합니다.

### 7교시 한눈에

| 하려는 일 | 명령 · 값 |
|---|---|
| 파일을 고친 뒤 반영 | 새 태그로 다시 build → 컨테이너를 지우고 새 이미지로 다시 켜기 |
| 이전 버전으로 되돌리기 | `docker rm -f 이름` → `docker run … 이름:이전태그` |
| 이미지 목록 | `docker images` (`EXTRA` 의 `U` = 컨테이너가 쓰는 이미지) |
| 이미지 지우기 | `docker rmi 이름:태그` (쓰는 컨테이너가 있으면 에러 → 컨테이너부터 지움) |
| 오늘 만든 것 올리기 | `git status` → `git add .` → `git commit -m "…"` → `git push` |

---

## 오늘 마무리

| 확인 | 문제 |
|---|---|
| 어제 명령으로 서버 두 대를 켜고, 서버마다 접속 기록이 따로 쌓이는 것을 읽고 정리했다 | 5-1 |
| Dockerfile 두 줄을 쓰고 내 이미지를 만들었다 | 6-1 |
| 파일을 고치면 이미지를 다시 만들어야 한다는 것을 확인했다 | 7-1 |
| 이전 버전 이미지로 서버를 되돌리고, 안 쓰는 이미지를 지웠다 | 7-2 |
| 오늘 만든 파일과 보고서를 깃허브에 올렸다 | 7-3 |

내일(10/21(수)) 2교시에는 「서버가 어디까지 열려 있는지」와 「안 열릴 때의 증상」을 실습합니다. 여러 서버를 파일 하나에 적어 한 번에 켜는 Docker Compose 는 4과목 첫날(11/2(월) 오후)에 배웁니다.

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

설명하는 답은 한 예이고, 핵심이 같으면 맞습니다.

---

### 정답 5-1

💻 **터미널에 입력합니다.**

```bash
MSYS_NO_PATHCONV=1 docker run -d --name web-three -p 8082:80 -v "$(pwd)/site-three:/usr/share/nginx/html:ro" nginx:1.28
```

```bash
MSYS_NO_PATHCONV=1 docker run -d --name web-four -p 8083:80 -v "$(pwd)/site-four:/usr/share/nginx/html:ro" nginx:1.28
```

맥북은 `MSYS_NO_PATHCONV=1 ` 을 빼고 칩니다.

**결과**

- (가) 위의 `docker run` 명령 두 개입니다. 윈도는 맨 앞의 `MSYS_NO_PATHCONV=1 ` 도 함께 적습니다.
- (나) `web-three` 의 `PORTS` 는 `0.0.0.0:8082->80/tcp, [::]:8082->80/tcp`, `web-four` 의 `PORTS` 는 `0.0.0.0:8083->80/tcp, [::]:8083->80/tcp` 입니다. 내 PC의 8082 번이 `web-three` 의 80 번에, 8083 번이 `web-four` 의 80 번에 연결되어 있다는 뜻입니다.
- (다) `docker logs web-three` 에는 `"GET / HTTP/1.1"` 줄이 **세 개**, `docker logs web-four` 에는 **한 개**입니다. 8082 로 온 요청은 `web-three` 만 받고 8083 으로 온 요청은 `web-four` 만 받기 때문에, 접속 기록도 서버마다 따로 쌓입니다. 한 예(맥북에서 `curl` 로 접속했을 때의 줄이고, 브라우저로 접속하면 맨 뒤가 브라우저 이름으로 나옵니다):

```
192.168.65.1 - - [19/Oct/2026:14:19:59 +0000] "GET / HTTP/1.1" 200 83 "-" "curl/8.7.1" "-"
```

  - 브라우저가 따로 요청하는 `/favicon.ico` 의 `404` 줄이 함께 보여도 정상입니다. 새로 고침한 줄은 응답 번호가 `304` 일 수 있습니다.
- (라) `stop` 뒤에 `docker ps` 에는 두 서버가 모두 없고, `docker ps -a` 에는 두 서버의 `STATUS` 가 `Exited (0)` 으로 남아 있습니다. `rm` 뒤에는 `docker ps -a` 에서도 두 줄이 없어집니다.
- (한 줄) 예: 「고객용 · 직원용 페이지 서버 두 대를 이름과 포트만 바꿔 켰고, 접속 기록이 서버마다 따로 남아 어느 페이지에 온 요청인지 구분할 수 있음을 확인한 뒤 둘 다 정리했습니다.」

**왜** — 서버를 켜고, 확인하고, 끄고, 지우는 순서는 서버가 몇 대든 같습니다. 서버가 늘면 어느 서버의 기록인지부터 구분해야 합니다. 이름과 포트로 서버를 가르고, `logs 이름` 으로 그 서버의 기록만 봅니다.

**자주 틀리는 곳** — 윈도에서 `MSYS_NO_PATHCONV=1 ` 을 빼먹으면 오류 없이 연결만 안 되어 「Welcome to nginx!」 기본 화면이 나옵니다. 8082 나 8083 번을 다른 컨테이너가 쓰고 있으면 `port is already allocated` 에러가 납니다. 두 번째 서버의 이름 · 포트 · 폴더 가운데 하나를 첫 번째와 같게 두면 이름 충돌 에러가 나거나 같은 화면이 나옵니다. 방금 켠 직후에 접속하면 연결이 거부될 수 있어, 1~2초 뒤 다시 엽니다. `rm` 을 켜진 컨테이너에 먼저 치면 `stop` 하거나 `-f` 를 붙이라는 에러가 납니다.

**관제에서는** — 서버가 여러 대일 때 로그는 서버 이름으로 먼저 가른 뒤 읽습니다. 같은 요청 수라도 서버마다 기록이 달라서, 어느 서버에서 `404` 나 에러가 났는지를 먼저 알아야 합니다. 서버를 늘리거나 줄인 뒤에는 `docker ps` 의 `PORTS` 와 `STATUS` 로 의도한 서버만 켜져 있는지 확인합니다.

---

### 정답 6-1

💻 **Dockerfile 에 쓰는 두 줄입니다.**

```dockerfile
FROM nginx:1.28
COPY site-three/index.html /usr/share/nginx/html/index.html
```

💻 **터미널에 입력합니다.**

```bash
docker build -t my-nginx:1 .
docker images
docker run -d --name my-site -p 8090:80 my-nginx:1
```

**결과**

- (가) 위의 Dockerfile 두 줄입니다.
- (나) `FROM nginx:1.28` 은 새 이미지에 포함할 기존 이미지로 `nginx:1.28` 을 정합니다. 새 이미지에는 이 이미지의 내용이 모두 들어가고, 거기에 내 파일이 추가됩니다. `COPY site-three/index.html /usr/share/nginx/html/index.html` 은 내 PC의 `site-three/index.html` 을 이미지 안의 nginx 가 응답하는 파일 자리로 복사해 넣습니다.
- (다) 내 파일이 `docker build` 때 이미지 안에 복사되어 이미 들어 있기 때문입니다. 5교시에서는 파일이 내 PC에 있고 `-v` 로 연결해야 컨테이너가 볼 수 있었지만, 이번에는 이미지 안에 파일이 들어 있어서 연결이 필요 없습니다.
- (라) 한 예:

```
 => [2/2] COPY site-three/index.html /usr/share/nginx/html/index.html              0.0s
 => => naming to docker.io/library/my-nginx:1                                      0.0s
```

  - `[2/2] COPY …` 줄은 Dockerfile 의 두 단계 중 둘째(COPY)가 실행되어 내 `site-three/index.html` 이 이미지 안에 들어갔다는 것을 알려 줍니다. 이 줄 앞에 `CACHED` 가 있으면 전에 같은 내용으로 만든 결과를 다시 쓴 것입니다.
  - `naming to …my-nginx:1` 줄은 만든 이미지에 `my-nginx:1` 이라는 이름이 붙어 build 가 성공했다는 것을 알려 줍니다. 이 줄이 없으면 `docker run` 에 쓸 이름이 없습니다.

**왜** — 파일을 이미지 안에 넣으면 이미지 하나만 넘겨도 같은 서버가 됩니다. 서버를 재현해야 하는 일에 알맞습니다.

**자주 틀리는 곳** — `docker build` 마지막의 점(`.`)을 빼먹는 일이 가장 많습니다. `COPY` 의 앞쪽 경로를 `index.html` 로만 써서 파일을 못 찾는 경우도 많습니다(`site-three/` 폴더 안에 있습니다). `Dockerfile` 을 소문자 `dockerfile` 로 만들면 못 찾는 경우도 있습니다. `COPY` 줄을 둘로 나누면 build 가 에러를 냅니다. 8090 포트나 `my-site` 이름이 이미 쓰이고 있으면 `docker run` 이 에러를 냅니다.

**관제에서는** — 같은 이름과 태그의 이미지는 같은 내용이라는 것을 전제로 합니다. 서버를 넘길 때 어느 태그인지 함께 남깁니다.

---

### 정답 7-1

💻 **터미널에 입력합니다.**

```bash
docker build -t my-nginx:2 .
docker rm -f my-site
docker run -d --name my-site -p 8090:80 my-nginx:2
```

**결과**

- (가) 제목이 **site-three** 인 예전 화면이 그대로 나옵니다(`v2` 가 붙지 않음).
- (나) 서버가 보여 주는 파일은 이미지 안에 복사된 것이고, 내 PC의 `site-three/index.html` 은 연결돼 있지 않기 때문입니다. 반영하려면 이미지를 다시 만들고(`docker build`, 새 태그 `:2`) 그 이미지로 서버를 다시 켭니다.
- (다) `-v` 방식은 내 PC의 파일을 그대로 보므로 파일을 고치고 새로 고침만 하면 바뀝니다. 이미지에 넣는 방식은 build 때의 파일을 복사해 둔 것이므로 파일을 고친 뒤 이미지를 다시 build 하고 서버를 교체해야 바뀝니다.

**왜** — 이미지는 만든 시점의 파일을 그대로 가진 읽기 전용 파일입니다. 새 태그로 만들면 이전 버전은 그대로 남아 있어서, 문제가 생겼을 때 이전 버전으로 돌아갈 수 있습니다.

**자주 틀리는 곳** — 이미지를 다시 build 하고도 서버를 지우지 않아 예전 이미지로 켜진 서버가 계속 도는 경우가 많습니다. `docker ps` 의 `IMAGE` 열이 `my-nginx:2` 인지 봅니다. `docker stop my-site` 만 하면 이름이 남아 같은 이름으로 다시 만들 수 없습니다. 브라우저가 이전 화면을 보여 줄 때는 `Ctrl + F5` 로 새로 고칩니다.

**관제에서는** — 서버에 문제가 생기면 지금 켜진 서버가 어느 이미지(태그)인지부터 확인합니다. 태그가 `latest` 뿐이면 어느 버전인지 알 수 없어서 추적이 어렵습니다.

---

### 정답 7-2

💻 **터미널에 입력합니다.**

```bash
docker rm -f my-site
docker run -d --name my-site -p 8090:80 my-nginx:1
docker rmi my-nginx:1
docker rmi my-nginx:2
docker rm -f my-site
docker rmi my-nginx:1
```

세 번째 줄 `docker rmi my-nginx:1` 은 에러가 나는 것이 정상이고, 네 번째 줄부터 지워집니다.

**결과**

- (가) `docker ps` 의 `IMAGE` 칸은 `my-nginx:1` 이고, 브라우저 제목은 **site-three** 입니다(`v2` 가 붙지 않음). 이전 버전으로 되돌아온 것입니다.
- (나) 에러 문구의 핵심은 `unable to delete my-nginx:1 (must be forced) - container … is using its referenced image …` 입니다. 켜진 컨테이너 `my-site` 가 `my-nginx:1` 을 쓰고 있어서 지워지지 않는다는 뜻입니다. `docker rm -f my-site` 로 컨테이너를 먼저 지운 뒤 `docker rmi my-nginx:1` 을 다시 치면 지워집니다.
- (다) 태그를 나눠 두면 새 버전(`:2`)에 문제가 있을 때 이전 태그(`:1`)로 서버를 다시 켜는 것만으로 바로 되돌릴 수 있습니다. 어느 버전이 켜져 있는지도 `docker ps` 의 `IMAGE` 칸으로 구분됩니다.
- (한 줄) 예: 「새 버전에 문제가 있어 이전 버전 이미지(`my-nginx:1`)로 서버를 다시 켜 되돌렸고, 쓰지 않는 이미지 두 개를 정리했습니다.」

**왜** — 이미지는 만든 시점의 파일을 그대로 가진 읽기 전용 파일이라, 버전별 이미지를 남겨 두면 서버를 바꾸는 것만으로 되돌릴 수 있습니다. 이미지를 지우는 일은 쓰는 컨테이너가 없을 때만 됩니다.

**자주 틀리는 곳** — `docker rm`(컨테이너)과 `docker rmi`(이미지)를 서로 바꿔 치는 경우가 많습니다. 이미지를 쓰는 컨테이너를 지우지 않고 `docker rmi` 를 반복해 같은 에러를 보는 경우도 있습니다. 되돌릴 때 `docker stop my-site` 만 하면 이름이 남아 같은 이름으로 다시 켤 수 없습니다. 이미지를 지우면 다시 쓰려면 build 해야 하니, 지우기 전에 어느 이미지인지 `docker images` 로 확인합니다.

**관제에서는** — 장애가 나면 지금 켜진 서버의 이미지 태그를 먼저 확인하고, 직전 태그로 되돌려 서비스를 살린 뒤 원인을 조사합니다. 이미지는 쌓이면 디스크를 차지하므로 쓰지 않는 것을 주기적으로 정리하되, 롤백용으로 남길 버전은 지우지 않습니다.

---

### 정답 7-3

💻 **터미널에 입력합니다.**

```bash
cd ../..
pwd
git status
git add .
git commit -m "Add day 7 docker image practice and report"
git push
```

**결과**

- (가) 한 예: 「줄이 3개였고(`day07_docker/` 폴더, 오후 보고서 `day07_pm_report.md`, 안내 문서 등), `.env` · `.venv` 는 없었다」. 줄 수와 이름은 학생마다 다를 수 있습니다. `.env` 나 `.venv` 가 보였다면 `.gitignore` 에 한 줄을 적고 `git status` 를 다시 쳤다고 적습니다.

**왜** — 올리기 전에 올라갈 파일을 확인해야 비밀 키가 섞이지 않습니다. 저장소에 남기면 누가 언제 무엇을 했는지 기록이 남고 다음 사람이 이어받을 수 있습니다.

**자주 틀리는 곳** — `.env` 가 보이는데 그대로 `git add .` 를 하는 실수가 가장 위험합니다. 멈추고 `.gitignore` 를 확인합니다. 올린 뒤 브라우저에서 확인하지 않으면 올라갔는지 알 수 없습니다.

**관제에서는** — `Dockerfile` 을 저장소에 남기면 서버 구성이 기록으로 남아 사고 때 같은 환경을 다시 만들 수 있습니다. 비밀 키는 저장소에 올리지 않습니다.
