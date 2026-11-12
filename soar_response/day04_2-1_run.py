from incident import load_json                                                                # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticketing import make_ticket, NEXT_STEPS                                                 # 방금 만든 티켓 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                         # 오늘 오전 알림 파일을 리스트로 읽는다
rules = load_json("config/escalation_rules.json")                                             # 응답 기한 규칙 파일을 딕셔너리로 읽는다
sla_count = len(rules["sla_minutes"])                                                         # 응답 기한을 정한 등급이 몇 개인지 센다
print("--- 단계 1: 불러온 알림", len(alerts), "건 · 응답 기한을 정한 등급", sla_count, "개")  # 단계 1 시작을 알리는 줄

tickets = []                                                                                  # 만든 티켓을 저장할 빈 리스트
manual_count = 0                                                                              # 직접 확인이 필요한 티켓 수 : 처음에는 0
print("--- 단계 2: 알림마다 만든 티켓")                                                       # 단계 2 시작을 알리는 줄
for alert in alerts:                                                                          # 알림을 하나씩 읽는다
    ticket_no = len(tickets) + 1                                                              # 티켓 번호는 지금까지 만든 수 + 1
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. make_ticket(alert, ticket_no, rules, NEXT_STEPS) 의 결과를 ticket 에 저장한다
    ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)
    # 8. tickets 리스트에 ticket 을 추가한다 (append)
    tickets.append(ticket)
    print(ticket["id"], ticket["title"], "· 만든 시각", ticket["created_at"], "분 · 기한", ticket["sla_due"], "분")  # 티켓 한 줄을 출력한다
    if ticket["needs_manual"]:                                                                # 직접 확인이 필요하면
        # 9. manual_count 에 manual_count + 1 을 저장한다 (1 늘린다)
        manual_count = manual_count + 1
print("--- 단계 3: 티켓 본문 예 (TCK-1)")                                                     # 단계 3 시작을 알리는 줄
first = tickets[0]                                                                            # 첫 번째 티켓을 꺼낸다
print("제목:", first["title"])                                                                # 제목을 출력한다
print("조치 내역:")                                                                           # 조치 내역 제목을 출력한다
for text in first["done"]:                                                                    # 조치 내역 문장을 하나씩 읽는다
    print(" -", text)                                                                         # 문장 앞에 - 를 붙여 출력한다
print("다음 할 일:", first["next_step"])                                                      # 다음 할 일을 출력한다
print("응답 기한:", first["sla_due"], "분 (만든 시각", first["created_at"], "분)")            # 응답 기한을 출력한다

print("--- 단계 4: 직접 확인이 필요한 티켓", manual_count, "건")                              # 단계 4 시작을 알리는 줄과 건수
for ticket in tickets:                                                                        # 티켓을 하나씩 읽는다
    if ticket["needs_manual"]:                                                                # 직접 확인이 필요하면
        print(ticket["id"], ticket["title"], "→", ticket["next_step"])                        # 티켓과 다음 할 일을 출력한다
