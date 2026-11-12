from incident import load_json, save_json                                             # 월요일 파일의 JSON 읽기 · 저장 함수를 불러온다
from ticket_merge import handle_alert                                                 # 3교시에 만든 알림 처리 함수를 불러온다
from ticket_notice import send_ticket_notice, send_with_retry, MAX_TRIES              # 방금 만든 알림 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                 # 오늘 오전 알림 파일을 읽는다
rules = load_json("config/escalation_rules.json")                                     # 규칙 파일을 읽는다
tickets = []                                                                          # 만든 티켓을 저장할 빈 리스트
sent_count = 0                                                                        # 알림을 보낸 수 : 처음에는 0
skipped_count = 0                                                                     # 건너뛴 수 : 처음에는 0

print("--- 단계 1: 알림", len(alerts), "건 처리와 담당자 알리기")                     # 단계 1 시작을 알리는 줄과 개수
for alert in alerts:                                                                  # 알림을 하나씩 읽는다
    ticket, action = handle_alert(alert, tickets, rules)                              # 알림을 처리하고 티켓과 처리 방식을 받는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. send_ticket_notice(ticket, alert["minute"], rules) 의 결과를 result 에 저장한다
    result = send_ticket_notice(ticket, alert["minute"], rules)
    print(alert["id"], "->", ticket["id"], action, "· 담당자 알리기:", result)        # 알림 한 건의 결과를 출력한다
    # 8. result 가 "전송" 이면 (if, ==)
    if result == "전송":
        # 9. sent_count 에 sent_count + 1 을 저장한다 (1 늘린다)
        sent_count = sent_count + 1
    if result == "건너뜀":                                                            # 건너뛰었으면 — 미리 채운 줄
        skipped_count = skipped_count + 1                                             # 건너뛴 수를 1 늘린다 — 미리 채운 줄

print("--- 단계 2: 담당자에게 전송", sent_count, "건 · 건너뜀", skipped_count, "건")  # 단계 2 시작을 알리는 줄과 건수
for ticket in tickets:                                                                # 티켓을 하나씩 읽는다
    print(ticket["id"], "담당자에게 알린 횟수", ticket["notified_count"], "번 · 마지막으로 알린 시각", ticket["last_notified"], "분")  # 티켓별 전송 횟수를 출력한다

url_off = "http://127.0.0.1:5999/alert"                                               # 아무 서버도 없는 주소 — 알림 서버가 꺼진 상황
print("--- 단계 3: 꺼진 주소로 최대", MAX_TRIES, "번 보내 보기")                      # 단계 3 시작을 알리는 줄
attempt = send_with_retry("[테스트] 꺼진 알림 서버", url_off, MAX_TRIES)              # 꺼진 주소로 보내 본다
print("성공한 시도 번호:", attempt, "(0 은 모두 실패)")                               # 시도 결과를 출력한다

save_json(tickets, "tickets_day4.json")                                               # 티켓을 파일에 저장한다
saved = load_json("tickets_day4.json")                                                # 저장한 파일을 다시 읽는다
print("--- 단계 4: 파일에 저장된 티켓", len(saved), "장")                             # 단계 4 시작을 알리는 줄과 장수
