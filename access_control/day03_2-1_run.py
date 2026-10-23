from req_create import REQUESTS, create_request                  # 방금 만든 요청서 함수와 목록을 불러온다

INBOX = [                                                        # 오늘 아침에 들어온 요청 일곱 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),           # 어제 끝난 예외가 아직 필요함
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 08:40"),              # 계정 관리자의 영업 실적 조회
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 08:50"),           # 접수 단계에서는 걸러지지 않는 요청
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),                  # 접수 단계에서는 걸러지지 않는 요청
    ("hana", "SALES", "QUERY", "2026-10-27 18:00", "신규 업무 지원", "2026-10-23 09:05"),               # 접수되는지 실행해서 확인
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "", "2026-10-23 09:10"),                        # 접수되는지 실행해서 확인
    ("gaeun", "ACCOUNT", "QUERY", "2026-10-22 18:00", "어제 적은 요청서 재사용", "2026-10-23 09:15"),   # 접수되는지 실행해서 확인
]

print("--- 단계 1: 접수 - 요청 일곱 건을 하나씩 넣는다")             # 단계 1 시작을 알리는 줄
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼낸다
    ok, result = create_request(user, resource, action, until, reason, received_at)   # 접수를 시도하고 결과를 받는다
    if ok:                                                       # 접수됐으면
        print(user, resource, action, "-> 접수됨, 요청 번호", result["id"])   # 요청 번호를 출력한다
    else:                                                        # 접수되지 않았으면
        print(user, resource, action, "-> 접수 안 됨:", result)    # 이유를 출력한다

print("--- 단계 2: 점검 - 요청서 목록")                            # 단계 2 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], request["permission"], request["status"])   # 번호 · 요청자 · 권한 · 상태를 출력한다
