from incident import load_json                                                              # 월요일 파일의 JSON 읽기 함수를 불러온다
from ticket_merge import handle_alert, change_ticket_status                                 # 방금 만든 함수를 불러온다

alerts = load_json("alerts_thu.json")                                                       # 오늘 오전 알림 파일을 읽는다
rules = load_json("config/escalation_rules.json")                                           # 규칙 파일을 읽는다
tickets = []                                                                                # 만든 티켓을 저장할 빈 리스트

window = rules["merge_window_minutes"]                                                      # 같은 사건으로 보는 시간(분)을 꺼낸다
print("--- 단계 1: 알림", len(alerts), "건 처리 (합치는 시간", window, "분)")               # 단계 1 시작을 알리는 줄과 개수
for alert in alerts:                                                                        # 알림을 하나씩 읽는다
    ticket, action = handle_alert(alert, tickets, rules)                                    # 알림을 처리하고 티켓과 처리 방식을 함께 받는다
    print(alert["id"], "->", ticket["id"], action, "· 합쳐진 알림", ticket["count"], "건")  # 알림 한 건의 결과를 출력한다

print("--- 단계 2: 알림", len(alerts), "건 → 티켓", len(tickets), "장")                     # 단계 2 시작을 알리는 줄과 개수
for ticket in tickets:                                                                      # 티켓을 하나씩 읽는다
    print(ticket["id"], ticket["title"], "· 알림", ticket["incidents"], "· 상태", ticket["status"])  # 티켓 한 줄을 출력한다

print("--- 단계 3: TCK-1 상태 바꾸기")                                                      # 단계 3 시작을 알리는 줄
first = tickets[0]                                                                          # 첫 번째 티켓을 꺼낸다
moves = [("확인 중", "kim.sec", 50), ("해결", "kim.sec", 65), ("열림", "lee.soc", 70)]      # 바꿀 상태 · 바꾼 사람 · 시각을 모은 리스트
for new_status, who, minute in moves:                                                       # 세 값을 한 번에 받아 하나씩 읽는다
    changed = change_ticket_status(first, new_status, minute, who)                          # 상태를 바꿔 본다
    if changed:                                                                             # 바뀌었으면
        print(first["id"], "→", new_status, "· 바꾼 사람", who)                             # 바뀐 상태를 출력한다
    else:                                                                                   # 안 바뀌었으면
        reason = first["status"] + "에서는 갈 수 없음"                                      # 거절한 이유를 문자열로 만든다
        print(first["id"], "→", new_status, "· 거절됨 ·", reason)                           # 거절한 이유를 출력한다
print("댓글 기록:")                                                                         # 댓글 제목을 출력한다
for comment in first["comments"]:                                                           # 댓글을 하나씩 읽는다
    print(" -", comment)                                                                    # 댓글을 출력한다
