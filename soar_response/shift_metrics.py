def average(numbers):                                                   # 숫자 리스트를 받는 함수
    """숫자 리스트의 평균을 리턴한다. 리스트가 비어 있으면 0 을 리턴한다.
    평균 확인 시간과 평균 해결 시간을 계산할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. numbers 의 개수(len)가 0 이면 (if, ==)
    if len(numbers) == 0:
    # 2.   0 을 리턴한다 (비어 있으면 나눌 수 없다)
        return 0
    # 3. sum(numbers) / len(numbers) 를 리턴한다 (합계를 개수로 나눈다)
    return sum(numbers) / len(numbers)

def collect_response_times(tickets):                                    # 티켓 리스트를 받는 함수
    """담당자가 처음 확인한 티켓마다 (확인한 시각 − 만든 시각)을 모아 리스트로 리턴한다. 아직 확인하지 않은 티켓은 뺀다.
    평균 확인 시간(MTTA)을 구할 재료를 만들 때 쓴다.
    """
    times = []                                                          # 걸린 시간(분)을 저장할 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. ticket 의 "acked_at" 이 -1 이 아니면 (if, !=)
        if ticket["acked_at"] != -1:
            # 5. times 리스트에 ticket["acked_at"] - ticket["created_at"] 을 추가한다 (append)
            times.append(ticket["acked_at"] - ticket["created_at"])
    return times                                                        # 걸린 시간 리스트를 리턴한다 — 미리 채운 줄


def collect_resolve_times(tickets):                                     # 티켓 리스트를 받는 함수
    """해결한 티켓마다 (해결한 시각 − 만든 시각)을 모아 리스트로 리턴한다. 아직 해결하지 않은 티켓은 뺀다.
    평균 해결 시간(MTTR)을 구할 재료를 만들 때 쓴다.
    """
    times = []                                                          # 걸린 시간(분)을 저장할 빈 리스트
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다
        if ticket["resolved_at"] != -1:                                 # 해결한 티켓이면
            times.append(ticket["resolved_at"] - ticket["created_at"])  # 걸린 시간을 추가한다
    return times                                                        # 걸린 시간 리스트를 리턴한다


def count_sla_breaches(tickets, now):                                   # 티켓 리스트와 지금 시각(분)을 받는 함수
    """응답 기한을 넘긴 티켓 수를 리턴한다. 아직 확인하지 않은 티켓은 지금 시각에 확인한 것으로 본다.
    응답 기한(SLA)을 얼마나 지켰는지 보고할 때 쓴다.
    """
    late = 0                                                            # 기한을 넘긴 티켓 수 : 처음에는 0 — 미리 채운 줄
    for ticket in tickets:                                              # 티켓을 하나씩 읽는다 — 미리 채운 줄
        checked_time = ticket["acked_at"]                               # 확인한 시각 — 미리 채운 줄
        if checked_time == -1:                                          # 아직 확인하지 않았으면 — 미리 채운 줄
            checked_time = now                                          # 지금 시각에 확인한 것으로 본다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. checked_time 이 ticket 의 "sla_due" 보다 크면 (if, >)
        if checked_time > ticket["sla_due"]:
            # 7. late 에 late + 1 을 저장한다 (1 늘린다)
            late = late + 1
    return late                                                         # 기한을 넘긴 티켓 수를 리턴한다 — 미리 채운 줄
