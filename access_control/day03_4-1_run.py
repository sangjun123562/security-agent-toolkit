from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request, reject_request           # 오전 3교시에 만든 승인 · 반려 함수를 불러온다
from req_grant import grant_request                              # 방금 만든 부여 함수를 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 최종 판정 함수를 불러온다

NOW = datetime.strptime("2026-10-23 10:00", "%Y-%m-%d %H:%M")    # 오늘 실습의 지금 시각(고정)

INBOX = [                                                        # 접수에 성공하는 요청 네 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다
for number in [1, 3, 4]:                                         # 보안 담당이 1 · 3 · 4번을 승인하고
    approve_request(REQUESTS[number - 1], "security_manager")    # 승인 처리한다
reject_request(REQUESTS[1], "security_manager")                  # 2번은 반려한다


def show(title):                                                 # 제목을 받아 요청서마다 지금 판정을 출력하는 함수
    print("---", title)                                          # 제목 줄을 출력한다
    for request in REQUESTS:                                     # 요청서를 하나씩 꺼낸다
        ok, reason = evaluate_access(request["user"], request["resource"], request["action"], NOW)   # 22일의 최종 판정을 받는다
        print(request["id"], request["user"], request["permission"], "->", ok, reason)   # 요청 번호 · 요청자 · 권한 -> 판정 을 출력한다


show("단계 1: 판정 - 부여 전")                                     # 부여하기 전의 판정을 본다

print("--- 단계 2: 부여 - 요청서마다 부여를 시도한다")                # 단계 2 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    ok, result = grant_request(request)                          # 부여를 시도한다
    print(request["id"], request["user"], request["status"], "->", ok, result)   # 요청 번호 · 요청자 · 상태 -> 결과 를 출력한다

for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    if "exception_id" in request:                                # exception_id 칸이 적힌 요청서(부여된 것)만
        print("부여된 예외 번호:", request["exception_id"])         # 그 예외 번호를 출력한다

show("단계 3: 점검 - 부여 후")                                     # 부여한 뒤의 판정을 다시 본다
