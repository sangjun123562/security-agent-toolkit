from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request, reject_request           # 오전 3교시에 만든 승인 · 반려 함수를 불러온다
from req_grant import grant_request                              # 오전 4교시에 만든 부여 함수를 불러온다
from req_sla import check_sla_breach                             # 5교시에 만든 기한 점검 함수를 불러온다
from request_flow import save_requests, count_by_status          # 방금 만든 저장 · 집계 함수를 불러온다

NOW = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)

INBOX = [                                                        # 오늘 들어온 요청 여섯 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 10:30"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 12:00"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "계정 권한 점검", "2026-10-23 07:50"),
    ("tester", "SALES", "QUERY", "2026-10-27 18:00", "시험 계정 확인", "2026-10-23 10:00"),
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다

print("--- 단계 1: 처리 - 승인 · 반려 · 부여")                      # 단계 1 시작을 알리는 줄
approve_request(REQUESTS[0], "security_manager")                 # 1번 승인
reject_request(REQUESTS[1], "security_manager")                  # 2번 반려
approve_request(REQUESTS[2], "security_manager")                 # 3번 승인
approve_request(REQUESTS[3], "security_manager")                 # 4번 승인
for request in REQUESTS:                                         # 요청서를 하나씩 꺼내
    ok, result = grant_request(request)                          # 부여를 시도한다(승인된 것만 의미가 있다)
    print(request["id"], request["user"], request["status"], "->", result)   # 번호 · 요청자 · 상태 -> 결과 를 출력한다

print("--- 단계 2: 점검 - 상태별 건수와 SLA")                      # 단계 2 시작을 알리는 줄
print(count_by_status(REQUESTS))                                 # 상태별 건수를 출력한다
for request in check_sla_breach(REQUESTS, NOW):                  # 기한을 초과한 요청서를 하나씩 꺼낸다
    print("SLA 초과 요청 번호:", request["id"])                    # 요청 번호를 출력한다

print("--- 단계 3: 저장 - requests.json")                        # 단계 3 시작을 알리는 줄
count = save_requests(REQUESTS, "requests.json")                 # 요청서 목록 전체를 파일로 저장하고 저장한 건수를 받는다
print("저장 함수가 리턴한 건수:", count)                            # 리턴한 건수를 출력한다
saved = load_json("requests.json", [])                           # 저장한 파일을 다시 읽어
print("저장한 요청서", len(saved), "건, 첫 요청서의 상태:", saved[0]["status"])   # 건수와 첫 요청서의 상태를 출력한다
