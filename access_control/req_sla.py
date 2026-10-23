from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다

SLA_HOURS = load_json("config/sla.json", {"hours": 4})["hours"]  # 처리 기한(시간). 파일이 없거나 깨졌으면 기본값 4


def check_sla_breach(requests, now):                             # 요청서 목록과 지금 시각(datetime)을 받는 함수
    """검토 중(reviewing)인 요청서 가운데 접수한 지 SLA_HOURS 시간을 초과한 것의 목록을 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 기한을 초과한 요청서를 담을 빈 목록 breached 를 만든다
    breached = []
    # 2. requests 에서 request 를 하나씩 꺼낸다
    for request in requests:
    # 3.   request["status"] 가 "reviewing" 이면(검토 중인 것만 본다)
        if request["status"] == "reviewing":
    # 4.     request["requested_at"] 을 TIME_FORMAT 으로 시각으로 바꿔 requested 에 담는다
            requested = datetime.strptime(request["requested_at"], TIME_FORMAT)
    # 5.     (now - requested) 를 .total_seconds() 로 초 단위 숫자로 바꾸고 3600 으로 나눠 hours 에 담는다
            hours = (now - requested).total_seconds() / 3600
    # 6.     hours 가 SLA_HOURS 보다 크면(같으면 아직 아니다)
        if hours > SLA_HOURS:
    # 7.       request.copy() 로 요청서를 복사해 overdue 에 담는다
             overdue = request.copy()
    # 8.       overdue["wait_hours"] 를 round(hours, 1) 로 정한다 (지난 시간을 소수 첫째 자리까지 반올림)
             overdue["wait_hours"] = round(hours, 1)
    # 9.       breached 에 overdue 를 더한다
             breached.append(overdue)
    # 10. 반복이 끝나면 breached 를 리턴한다
    return breached
