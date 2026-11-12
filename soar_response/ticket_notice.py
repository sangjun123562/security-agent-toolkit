from notifier import notify                                            # 1과목 notifier.py 의 알림 함수를 불러온다 (성공하면 True, 실패하면 False)

MAX_TRIES = 3                                                          # 알림을 보내 보는 최대 횟수


def pick_recipients(grade, rules):                                     # 등급과 규칙을 받는 함수
    """등급에 맞는 수신자 이름 리스트를 리턴한다.
    위험한 알림일수록 더 많은 사람에게 알려야 할 때 쓴다.
    """
    table = rules["recipients"]                                        # 등급마다 정한 수신자 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table[grade] 를 리턴한다 (이 등급의 수신자 리스트)
    return table[grade]

def should_send(ticket, now, gap):                                     # 티켓 · 지금 시각(분) · 알림 간격(분)을 받는 함수
    """이 티켓의 알림을 지금 보내도 되면 True, 너무 일러서 건너뛰어야 하면 False 를 리턴한다.
    같은 티켓의 알림이 연달아 가서 사람이 알림을 무시하게 되는 일을 막을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. ticket 의 "notified_count" 가 0 이면 (if, ==) 처음 보내는 것이다
    if ticket["notified_count"] == 0:
    # 3.   True 를 리턴한다
        return True
    elapsed = now - ticket["last_notified"]                            # 마지막으로 보낸 뒤 몇 분 지났는지 — 미리 채운 줄
    # 4. elapsed 가 gap 이상인지(>=)의 결과를 리턴한다
    return elapsed >= gap


def send_with_retry(message, url, max_tries):                          # 메시지 · 알림 주소 · 최대 횟수를 받는 함수
    """알림을 최대 max_tries 번 보내 본다. 성공한 시도 번호를, 모두 실패하면 0 을 리턴한다.
    알림 서버가 잠깐 응답하지 않을 때 바로 포기하지 않고 다시 보내 보려고 쓴다.
    """
    for attempt in range(1, max_tries + 1):                            # 시도 번호를 1 부터 최대 횟수까지 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. notify(message, url) 의 결과가 참이면 (if)
        if notify(message, url):
            # 6. attempt 를 리턴한다
            return attempt
    return 0                                                           # 모두 실패했으면 0 을 리턴한다 — 미리 채운 줄


def send_ticket_notice(ticket, now, rules):                            # 티켓 · 지금 시각(분) · 규칙을 받는 함수
    """티켓 알림을 보낼지 정하고, 보내야 하면 수신자를 붙여 보낸다. 「전송」 · 「건너뜀」 · 「실패」 중 하나를 리턴한다.
    티켓이 만들어지거나 합쳐질 때마다 부른다.
    """
    if not should_send(ticket, now, rules["send_gap_minutes"]):        # 너무 일러서 보내면 안 되면
        return "건너뜀"                                                # 보내지 않고 「건너뜀」을 리턴한다
    recipients = pick_recipients(ticket["grade"], rules)               # 이 등급의 수신자 리스트를 구한다
    names = ""                                                         # 수신자 이름을 이어 붙일 빈 문자열
    for name in recipients:                                            # 수신자를 하나씩 읽는다
        if names != "":                                                # 이미 이름이 있으면
            names = names + ", "                                       # 쉼표를 붙이고
        names = names + name                                           # 이름을 이어 붙인다
    message = ticket["title"] + " · " + ticket["id"] + " · 알림 " + str(ticket["count"]) + "건 · 기한 " + str(ticket["sla_due"]) + "분 · 수신: " + names  # 알림 내용을 만든다
    attempt = send_with_retry(message, rules["alert_url"], MAX_TRIES)  # 최대 3번까지 보내 본다
    if attempt == 0:                                                   # 모두 실패했으면
        return "실패"                                                  # 「실패」를 리턴한다
    ticket["notified_count"] = ticket["notified_count"] + 1            # 보낸 횟수를 1 늘린다
    ticket["last_notified"] = now                                      # 마지막으로 보낸 시각을 적는다
    return "전송"                                                      # 「전송」을 리턴한다
