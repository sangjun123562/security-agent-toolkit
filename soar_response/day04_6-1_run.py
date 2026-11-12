from incident import load_json, save_json                                             # 월요일 파일의 JSON 읽기 · 저장 함수를 불러온다
from ticket_merge import handle_alert, change_ticket_status                           # 3교시에 만든 함수를 불러온다
from ticket_notice import send_ticket_notice                                          # 4교시에 만든 알리기 함수를 불러온다
from escalation import needs_escalation, escalate_ticket                              # 5교시에 만든 올리기 함수를 불러온다
from shift_metrics import average, collect_response_times, collect_resolve_times, count_sla_breaches  # 방금 만든 계산 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                 # 오늘 오전 알림 파일을 읽는다
events = load_json("status_events.json")                                              # 담당자의 동작 기록을 읽는다
rules = load_json("config/escalation_rules.json")                                     # 규칙 파일을 읽는다
tickets = []                                                                          # 만든 티켓을 저장할 빈 리스트

print("--- 단계 1: 가상 근무 0분부터 180분까지 (알림", len(alerts), "건 · 담당자 동작", len(events), "건)")  # 단계 1 시작을 알리는 줄
for now in range(0, 181):                                                             # 지금 시각을 0 분부터 180 분까지 1분씩 꺼낸다
    for alert in alerts:                                                              # 알림을 하나씩 읽는다
        if alert["minute"] == now:                                                    # 이 시각에 온 알림이면
            ticket, action = handle_alert(alert, tickets, rules)                      # 알림을 처리하고 티켓과 처리 방식을 받는다
            result = send_ticket_notice(ticket, now, rules)                           # 담당자에게 알린다
            print("[" + str(now) + "분]", alert["id"], "→", ticket["id"], action, "· 알리기", result)  # 알림 처리 결과를 출력한다
    for event in events:                                                              # 담당자의 동작을 하나씩 읽는다
        if event["minute"] == now:                                                    # 이 시각에 한 동작이면
            for ticket in tickets:                                                    # 티켓을 하나씩 읽는다
                if ticket["id"] == event["ticket"]:                                   # 동작 대상 티켓이면
                    change_ticket_status(ticket, event["status"], now, event["who"])  # 상태를 바꾼다
                    print("[" + str(now) + "분]", ticket["id"], "→", event["status"], "·", event["who"])  # 담당자의 동작을 출력한다
    if now % 10 == 0:                                                                 # 10분마다 (10 으로 나눈 나머지가 0 이면)
        for ticket in tickets:                                                        # 티켓을 하나씩 읽는다
            if needs_escalation(ticket, now):                                         # 상급자에게 올릴 티켓이면
                result = escalate_ticket(ticket, now, rules)                          # 상급자에게 올린다
                if result != "그대로":                                                # 새로 올렸거나 실패했으면
                    print("[" + str(now) + "분]", ticket["id"], "상급자에게", result, "· 올림 단계", ticket["escalation_level"])  # 올린 결과를 출력한다

print("--- 단계 2: 근무 지표")                                                        # 단계 2 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. collect_response_times(tickets) 의 결과를 ack_times 에 저장한다
ack_times = collect_response_times(tickets)
# 9. average(ack_times) 의 결과를 mtta 에 저장한다
mtta = average(ack_times)
resolve_times = collect_resolve_times(tickets)                                        # 해결한 티켓의 걸린 시간 리스트 — 미리 채운 줄
mttr = average(resolve_times)                                                         # 평균 해결 시간(MTTR) — 미리 채운 줄
late_count = count_sla_breaches(tickets, 180)                                         # 응답 기한을 넘긴 티켓 수 — 미리 채운 줄
print("티켓", len(tickets), "장 · 확인한 티켓", len(ack_times), "장 · 해결한 티켓", len(resolve_times), "장")  # 티켓 수를 출력한다
print("평균 확인 시간(MTTA):", mtta, "분")                                            # 평균 확인 시간을 출력한다
print("평균 해결 시간(MTTR):", mttr, "분")                                            # 평균 해결 시간을 출력한다
print("응답 기한을 넘긴 티켓:", late_count, "장")                                     # 응답 기한을 넘긴 티켓 수를 출력한다

print("--- 단계 3: 다음 근무자에게 넘길 티켓 (해결되지 않은 티켓)")                   # 단계 3 시작을 알리는 줄
for ticket in tickets:                                                                # 티켓을 하나씩 읽는다
    if ticket["status"] != "해결":                                                    # 해결되지 않은 티켓이면
        print(ticket["id"], ticket["title"], "· 상태", ticket["status"], "·", ticket["next_step"])  # 티켓과 다음 할 일을 출력한다

save_json(tickets, "shift_tickets.json")                                              # 근무가 끝난 티켓을 파일에 저장한다
saved = load_json("shift_tickets.json")                                               # 저장한 파일을 다시 읽는다
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")                             # 단계 4 시작을 알리는 줄과 장수
