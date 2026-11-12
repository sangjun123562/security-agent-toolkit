from incident import load_json                                                       # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticket_merge import change_ticket_status                                        # 3교시에 만든 상태 바꾸기 함수를 불러온다
from escalation import overdue_minutes, needs_escalation, escalate_ticket            # 방금 만든 함수를 불러온다

tickets = load_json("tickets_day4.json")                                             # 오전 4교시가 저장한 티켓을 읽는다
rules = load_json("config/escalation_rules.json")                                    # 규칙 파일을 읽는다
steps_count = len(rules["escalation_steps"])                                         # 올림 단계가 몇 개인지 센다
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 올림 단계", steps_count, "개")  # 단계 1 시작을 알리는 줄
escalated_count = 0                                                                  # 상급자에게 올린 횟수 : 처음에는 0

print("--- 단계 2: 점검 시각마다 상급자에게 올릴 티켓 찾기")                         # 단계 2 시작을 알리는 줄
for now in [20, 60, 110]:                                                            # 점검할 시각(분)을 하나씩 읽는다
    print("[" + str(now) + "분] 점검")                                               # 점검 시각을 출력한다
    for ticket in tickets:                                                           # 티켓을 하나씩 읽는다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. needs_escalation(ticket, now) 가 참이면 (if)
        if needs_escalation(ticket, now):
            # 8. escalate_ticket(ticket, now, rules) 의 결과를 result 에 저장한다
            result = escalate_ticket(ticket, now, rules)
            overdue = overdue_minutes(ticket, now)                                   # 기한을 얼마나 넘겼는지 구한다 — 미리 채운 줄
            print(ticket["id"], ticket["title"], "→", result, "· 기한을", overdue, "분 넘김 · 올림 단계", ticket["escalation_level"])  # 결과를 출력한다 — 미리 채운 줄
            if result == "올림":                                                     # 올렸으면 — 미리 채운 줄
                # 9. escalated_count 에 escalated_count + 1 을 저장한다 (1 늘린다)
                escalated_count = escalated_count + 1
    if now == 20:                                                                    # 20분 점검이 끝나면 — 미리 채운 줄
        change_ticket_status(tickets[0], "확인 중", 25, "kim.sec")                   # 25분에 kim.sec 이 TCK-1 을 확인하기 시작한다 — 미리 채운 줄
        print("[25분] TCK-1 → 확인 중 · kim.sec")                                    # 담당자의 동작을 출력한다 — 미리 채운 줄

print("--- 단계 3: 올린 결과 요약 (올린 횟수", escalated_count, "번)")               # 단계 3 시작을 알리는 줄과 횟수
for ticket in tickets:                                                               # 티켓을 하나씩 읽는다
    if ticket["escalation_level"] > 0:                                               # 상급자에게 올린 티켓이면
        print(ticket["id"], "올림 단계", ticket["escalation_level"], "· 상태", ticket["status"])  # 올림 단계와 지금 상태를 출력한다
