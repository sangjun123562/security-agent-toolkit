import json                                                      # JSON 문자열을 읽는 모듈을 불러온다
import os                                                        # 파일이 있는지 보고 지우는 데 쓴다
import requests                                                  # 서버에 요청을 보내는 모듈을 불러온다

BASE_URL = "http://127.0.0.1:5001"                               # 서버 주소
LOG_PATH = "server_log.jsonl"                                    # 서버가 남기는 로그 파일 이름
CASES = [                                                        # 서버에 보낼 요청 아홉 건. 주소의 ?user=… 로 들어가는 값이다
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "office", "time": "2026-10-30T09:00"},     # 1. 시작 시각 정각, 사내망
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "office", "time": "2026-10-30T18:00"},     # 2. 끝 시각 정각
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "network": "external", "time": "2026-10-30T10:00"},   # 3. 외부 접속
    {"user": "seoyeon", "resource": "SALES", "action": "QUERY", "network": "external", "time": "2026-10-30T23:00"},    # 4. 조건이 없는 조회
    {"user": "junho", "resource": "SETTLE", "action": "QUERY", "network": "vpn", "time": "2026-10-30T19:30"},          # 5. 정산 조회는 20시까지
    {"user": "junho", "resource": "SETTLE", "action": "QUERY", "network": "external", "time": "2026-10-30T10:00"},     # 6. 외부 접속
    {"user": "gaeun", "resource": "ACCOUNT", "action": "CHANGE", "network": "vpn", "time": "2026-10-30T10:00"},        # 7. 계정 변경은 사내망만
    {"user": "dami", "resource": "SALES", "action": "QUERY", "network": "office", "time": "2026-10-30T10:00"},         # 8. 퇴사한 사용자
    {"user": "seoyeon", "resource": "SALES", "action": "CHANGE", "time": "2026-10-30T10:00"},                          # 9. 접속 위치(network)를 빠뜨린 요청
]

if os.path.exists(LOG_PATH):                                     # 이전에 남은 로그 파일이 있으면
    os.remove(LOG_PATH)                                          # 지운다(이번 요청 로그만 보려고. 실제 서비스에서는 로그를 지우지 않고 보관한다)

print("--- 단계 1: 응답 - 요청", len(CASES), "건")               # 단계 1 시작을 알리는 줄
results = []                                                     # 서버의 응답을 담을 빈 리스트
case_count = len(CASES)                                          # 개수를 먼저 구한다
for i in range(case_count):                                      # 번호 i 로 요청을 하나씩 꺼낸다
    case = CASES[i]                                              # i 번째 요청
    response = requests.get(BASE_URL + "/check", params=case)    # 서버의 /check 에 요청을 보낸다(params 의 값이 주소의 ?user=… 가 된다)
    body = response.json()                                       # 응답의 JSON 문자열을 딕셔너리로 바꾼다
    result = {
        "status": response.status_code,                          # 응답 상태 코드
        "allowed": body["allowed"],                              # 허용 여부
        "reason": body["reason"],                                # 이유
    }
    results.append(result)                                       # 상태 코드 · 허용 여부 · 이유를 응답 리스트에 추가한다
    permission = case["resource"] + ":" + case["action"]         # 자원과 행위를 : 로 이어 붙여 권한 문자열을 만든다
    print(i + 1, case["user"], permission, "->", response.status_code, body["reason"])  # 번호 · 사용자 · 권한 -> 상태 코드 · 이유를 출력한다

entries = []                                                     # 로그에서 읽은 기록을 담을 빈 리스트
with open(LOG_PATH, encoding="utf-8") as f:                      # 로그 파일을 읽기 모드로 연다
    for line in f:                                               # 파일에서 한 줄씩 꺼낸다
        entry = json.loads(line)                                 # JSON 한 줄을 딕셔너리로 바꾼다
        entries.append(entry)                                    # 그 줄의 JSON 문자열을 딕셔너리로 바꿔 추가한다
print("--- 단계 2: 로그 - 서버가 남긴", len(entries), "줄")      # 단계 2 시작을 알리는 줄
for entry in entries:                                            # 로그의 기록을 하나씩 꺼낸다
    print(entry["user"], entry["permission"], entry["network"], entry["time"], "->", entry["allowed"], entry["reason"])  # 사용자 · 권한 · 접속 위치 · 시각 -> 결과를 출력한다

answered = 0                                                     # 판정까지 간 응답 수를 0 으로 시작한다
for result in results:                                           # 응답을 하나씩 꺼낸다
    if result["status"] != 400:                                  # 입력 부족(400)이 아니면 서버가 판정까지 한 것이다
        answered = answered + 1                                  # 판정까지 간 응답 수를 1 늘린다
print("--- 단계 3: 대조 - 판정까지 간 응답과 로그")              # 단계 3 시작을 알리는 줄
print("판정까지 간 응답", answered, "건 / 로그에 남은 줄", len(entries), "줄")  # 두 수가 같은지 출력한다
