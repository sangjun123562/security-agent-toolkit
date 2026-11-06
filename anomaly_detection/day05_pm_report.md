# 4과목 Day 5 도커 컴포즈로 서버 두 대 켜기 · 웹 서버 로그 만들기 · 오후 (이름 · 2026-11-06(금))

> **쓰는 법**
> - 문제를 풀 때마다 그 문제 제목 아래 질문에 답합니다.
> - 질문마다 `쓸 내용:` 에 무엇을 쓰면 되는지 적혀 있습니다. 그대로 `답:` 뒤에 씁니다.
> - 출력이나 코드를 붙여 넣는 질문은 `답:` 아래 빈 코드 상자에 붙여 넣고, 설명은 `답:` 뒤에 씁니다.
> - 「왜」를 묻는 질문은 한 단어로 끝내지 말고, 내 화면에서 본 값이나 배운 내용을 근거로 이유까지 씁니다.
> - 🔍 는 이 교시에서 꼭 알아야 할 핵심 질문입니다. 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다. 🔍 가 없는 질문도 못 적으면 같은 말을 씁니다.

---

## 5교시 · 도커 복습 · 컴포즈로 서버 두 대 한 번에 켜기

### 문제 5-1 · 서버 한 대를 복습하고 컴포즈로 두 대 켜기

- (가) 5교시 순서의 서버 켜기 · 확인 명령(`docker images` 부터 `curl` 까지)과 그 결과를 친 순서대로 붙여 넣고, 서비스 이름 두 개와 각 서비스의 포트를 적어 주세요.
  - 쓸 내용: ① 명령과 결과를 친 순서대로(코드 상자에 붙여 넣기): `docker images` · `docker run` · `docker ps` · `docker stop` · `docker compose up -d` · `docker compose ps` · `curl` 두 개 (`docker pull` 은 받았을 때만, `pwd` · `touch` · `ls` 는 붙이지 않아도 됩니다) ② 서비스 이름 두 개 ③ 각 서비스의 포트
  - 답:web1 8080 >80 / web2 8081 > 80

```
$ docker images nginx:1.28
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
nginx        1.28      146adea4768b   2 weeks ago    258MB

$ docker run -d --rm -p 8080:80 --name web-run nginx:1.28
e1a2ad01c5448378bfca44f56f8f7422b406e25dc9f3b53f65b4cbf9d7bcfa76

$ docker ps
CONTAINER ID   IMAGE        COMMAND                  CREATED                  STATUS                  PORTS                                     NAMES
e1a2ad01c544   nginx:1.28   "/docker-entrypoint.…"   Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web-run

$ docker stop web-run
web-run

$ docker compose up -d
[+] Running 3/3
 ✔ Network anomaly_detection_default       Created
 ✔ Container anomaly_detection-web1-1      Started
 ✔ Container anomaly_detection-web2-1      Started

$ docker compose ps
NAME                       IMAGE        COMMAND                  SERVICE   CREATED          STATUS          PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      10 seconds ago   Up 9 seconds    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      10 seconds ago   Up 9 seconds    0.0.0.0:8081->80/tcp, [::]:8081->80/tcp

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
200
```

- (나) 🔍 서버 두 대를 `docker run` 으로 켜는 것과 `compose.yaml` 과 `docker compose up -d` 로 켜는 것을 비교해, 컴포즈가 더 나은 점을 두 가지 적어 주세요.
  - 쓸 내용: ① 컴포즈가 더 나은 점 두 가지
  - 답:반복 명령 제거 및 휴먼 에러 방지: 긴 옵션(-p, --name, -d, 이미지 버전 등)을 매번 터미널에 반복해서 칠 필요 없이, docker compose up -d 한 줄로 여러 컨테이너를 정확하게 일괄 기동할 수 있습니다.

설정의 코드화(IaC) 및 문서화: 포트 매핑, 이미지 버전, 재시작 정책 등의 서버 구성 정보가 텍스트 파일(compose.yaml)에 명시적으로 보존되므로 누가 켜도 항상 동일한 환경을 일관되게 생성할 수 있습니다.

- (다) 🔍 보안 사고가 난 뒤 감사팀이 「사고 당시와 같은 구성으로 서버를 다시 켜 보라」고 요청했습니다. 팀원 한 명은 3주 전에 긴 `docker run` 명령을 직접 쳐서 서버를 켰는데 그 명령을 기억하지 못합니다. 다른 팀은 `compose.yaml` 을 깃허브에 올려 두었습니다. 두 팀이 같은 구성을 다시 켤 수 있는지 비교하고, 파일에 `nginx:1.28` 처럼 버전을 적어 두는 것이 이런 재현에 왜 중요한지 적어 주세요.
  - 쓸 내용: ① 두 팀의 차이 ② 버전을 적어 두는 것이 재현에 중요한 이유
  - 답:두 팀의 사고 재현 가능 여부 비교:

명령을 직접 친 팀: 당시 실행했던 포트, 옵션, 컨테이너 설정 등을 기억하지 못하므로 사고 당시와 완전히 동일한 환경을 재현하는 것이 불가능합니다.

컴포즈 파일을 Git에 올린 팀: 저장소의 커밋 이력에 당시 설정 파일이 그대로 보존되어 있으므로 파일만 내려받아 docker compose up -d를 실행하면 즉시 사고 당시와 100% 동일한 구성을 재현할 수 있습니다.

nginx:1.28처럼 버전을 명시해야 하는 이유:

latest 태그를 쓰면 시간이 흐름에 따라 최신 버전으로 자동 업데이트되어 취약점 패치 여부나 기본 동작 설정이 달라질 수 있습니다.

버전을 정확히 고정해 두어야 시간이 지나도 당시 취약점 상태 및 동일한 소프트웨어 버그를 그대로 가진 환경을 오차 없이 재현하고 검증할 수 있습니다.

- (라) 🔍 팀원 세 명이 같은 `compose.yaml` 로 서버를 켰는데 한 명의 PC 에서만 `8081` 번 포트를 다른 프로그램이 쓰고 있어서 `web2` 가 켜지지 않았습니다. 이 사람이 파일의 어느 줄을 어떻게 바꾸면 되는지 적고, 바꿔도 서버 안에서는 여전히 `80` 번 포트로 동작하는 이유를 적어 주세요. 이 사람이 `curl` 로 확인할 때 달라지는 점도 적어 주세요.
  - 쓸 내용: ① 바꿀 줄과 바꾼 모양 ② 서버 안은 그대로 80 인 이유 ③ curl 주소의 달라지는 점
  - 답:수정해야 할 파일 위치와 내용:

compose.yaml의 web2 서비스 아래 ports: 부분인 - "8081:80" 줄을 충돌하지 않는 다른 포트(예: - "8082:80")로 수정합니다.

서버 안에서는 여전히 80번 포트로 동작하는 이유:

호스트포트:컨테이너포트 매핑에서 앞의 숫자는 '내 컴퓨터(호스트) 외부에서 접속할 포트'이고, 뒤의 80은 '도커 가상 격리망 내부 컨테이너의 포트'입니다.

포트포워딩은 외부 포트로 들어온 요청을 컨테이너 내부의 80번으로 넘겨주는 네트워크 전달 규칙일 뿐이므로, 호스트 외부 포트를 8082로 바꾸더라도 컨테이너 내부의 Nginx 프로세스는 고유 포트인 80번에서 변경 없이 동작합니다.

curl 확인 명령 시 달라지는 점:

호스트 접근 포트가 바뀌었으므로 curl 요청 주소 역시 변경된 포트로 지정해야 합니다.

## 6교시 · 서버마다 접속 범위 정하기 · 설정 바꿔 적용하기

### 문제 6-1 · 서버마다 접속 범위를 정해 컴포즈 파일로 적용하기

- (가) 1번과 5번의 `docker compose ps` 출력을 붙여 넣고, 접속 범위가 바뀐 기존 서비스와 새로 추가된 서비스를 따로 적어 주세요.
  - 쓸 내용: ① 1번 출력(코드 상자에 붙여 넣기) ② 5번 출력(코드 상자에 붙여 넣기) ③ 접속 범위가 바뀐 기존 서비스 ④ 새로 추가된 서비스
  - 답:web2 / web3

```
1번: NAME                       IMAGE        COMMAND                  SERVICE   CREATED          STATUS          PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      10 minutes ago   Up 10 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      10 minutes ago   Up 10 minutes   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
5번:NAME                       IMAGE        COMMAND                  SERVICE   CREATED          STATUS          PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      12 minutes ago   Up 12 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      15 seconds ago   Up 14 seconds   127.0.0.1:8081->80/tcp
anomaly_detection-web3-1   nginx:1.28   "/docker-entrypoint.…"   web3      15 seconds ago   Up 14 seconds   127.0.0.1:8082->80/tcp
```

- (나) 🔍 `"8081:80"` 과 `"127.0.0.1:8081:80"` 은 누가 접속할 수 있는지가 어떻게 다른가요? 관리 화면이나 데이터베이스 서버를 이렇게 설정하는 이유도 적어 주세요.
  - 쓸 내용: ① 두 포트 줄에서 누가 접속할 수 있는지의 차이 ② 관리 화면 · 데이터베이스를 이렇게 설정하는 이유
  - 답:접속 범위 차이점:

"8081:80" (0.0.0.0 바인딩): 호스트의 모든 네트워크 인터페이스를 개방하므로, 내 PC뿐만 아니라 동일 네트워크(공유기, 사내망 등)에 연결된 외부의 다른 PC에서도 접속할 수 있습니다.

"127.0.0.1:8081:80" (루프백 바인딩): 호스트의 로컬 루프백 주소에만 포트를 묶어두기 때문에 내 PC 내부에서만 접속할 수 있으며, 동일 망의 다른 PC에서는 접근이 원천 차단됩니다.
관리 화면/DB를 이렇게 설정하는 이유:

관리 콘솔(/admin)이나 데이터베이스 포트처럼 내부 관리자만 취급해야 하는 핵심 자원이 외부에 열려 있으면, 공격자의 무차별 대입 공격이나 취약점 스캔에 노출되어 계정 탈취 및 기밀 유출 사고가 발생하기 때문입니다. 로컬 접속(127.0.0.1)으로 제한하여 비인가자의 접근 경로를 네트워크 레벨에서 차단합니다.

- (다) 🔍 `up -d` 의 출력에서 `web1` 은 `Running`, `web2` 는 `Recreated`, `web3` 은 `Created` 였습니다. 서버마다 출력이 다른 이유와, 운영 중인 서비스의 설정을 바꿀 때 이것이 왜 도움이 되는지 적어 주세요.
  - 쓸 내용: ① 서버마다 출력이 다른 이유 ② 서버를 끊지 않고 바꿀 수 있는 것의 쓸모
  - 답:서버마다 출력이 다른 이유:

web1 (Running): compose.yaml 대비 설정(image, ports, restart 등)에 변경 사항이 전혀 없으므로, 컨테이너를 중단하거나 새로 만들지 않고 기존 상태를 그대로 유지했습니다.

web2 (Recreated): 포트 매핑 설정이 8081:80에서 127.0.0.1:8081:80으로 변경되었기 때문에, 도커 컴포즈가 기존 컨테이너를 안전하게 삭제하고 새 설정이 적용된 컨테이너로 다시 생성했습니다.

web3 (Created): 기존 컴포즈 파일에는 없었던 새로운 서비스가 추가되었으므로 신규 컨테이너로 처음 생성되었습니다.
운영 서비스 변경 시 도움이 되는 이유:

운영 중인 시스템에서 여러 컨테이너 중 일부 서비스의 설정만 변경할 때, 전체 서비스를 내렸다가 다시 올리는 전면 중단(Downtime)을 거칠 필요가 없습니다.

변경되지 않은 서비스(web1)는 서비스 단절 없이 지속 가동(무중단)하면서, 변경이 필요한 특정 서비스만 선별적으로 재배포할 수 있어 운영 가용성을 안정적으로 유지할 수 있습니다.

### 마무리 · 오늘 만든 것을 깃허브에 올리기

- (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
  - 쓸 내용: ① `.env` · `.venv` 가 보였는지 ② 보였다면 한 조치
  - 답:
