from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from req_create import REQUESTS, create_request                  # 오전 2교시에 만든 요청서 함수와 목록을 불러온다
from req_review import approve_request                           # 오전 3교시에 만든 승인 함수를 불러온다
from req_sla import SLA_HOURS, check_sla_breach                  # 방금 만든 기한 점검 함수와 SLA 시간을 불러온다

NOW = datetime.strptime("2026-10-23 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)

INBOX = [                                                        # 오늘 들어온 요청 여섯 건. (요청자, 자원, 행위, 희망 만료 시각, 이유, 접수 시각)
    ("seoyeon", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 대조 지원", "2026-10-23 08:30"),    # 오전 일찍 접수한 요청
    ("gaeun", "SALES", "QUERY", "2026-10-28 18:00", "감사 자료 대응", "2026-10-23 10:30"),       # 오전에 접수한 요청
    ("dami", "SALES", "QUERY", "2026-10-27 18:00", "인수인계 자료 확인", "2026-10-23 12:00"),    # 낮에 접수한 요청
    ("junho", "SETTLE", "QUERY", "2026-10-27 18:00", "정산 확인", "2026-10-23 09:00"),           # 나중에 승인해서 처리가 끝나게 될 요청
    ("seoyeon", "ACCOUNT", "QUERY", "2026-10-27 18:00", "계정 권한 점검", "2026-10-23 07:50"),   # 이른 아침에 접수한 요청
    ("tester", "SALES", "QUERY", "2026-10-27 18:00", "시험 계정 확인", "2026-10-23 10:00"),      # 오전 10시 정각에 접수한 요청
]
for user, resource, action, until, reason, received_at in INBOX:         # 요청을 하나씩 꺼내
    create_request(user, resource, action, until, reason, received_at)   # 접수한다
approve_request(REQUESTS[3], "security_manager")                 # 4번(junho)은 이미 승인해 처리가 끝난 요청으로 만든다

print("--- 단계 1: 현황 - SLA 시간", SLA_HOURS, "시간, 지금 14:00")   # 단계 1 시작을 알리는 줄
for request in REQUESTS:                                         # 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], request["status"], request["requested_at"])   # 번호 · 요청자 · 상태 · 접수 시각을 출력한다

print("--- 단계 2: 판정 - SLA 를 초과한 요청")                       # 단계 2 시작을 알리는 줄
for request in check_sla_breach(REQUESTS, NOW):                  # 기한을 초과한 요청서를 하나씩 꺼낸다
    print(request["id"], request["user"], "접수", request["requested_at"], "->", request["wait_hours"], "시간 지남")   # 번호 · 요청자 · 접수 시각 · 지난 시간을 출력한다
