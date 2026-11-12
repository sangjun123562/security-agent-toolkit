from ticketing import make_ticket, has_failed_action, NEXT_STEPS, MANUAL_STEP        # 2교시에 만든 함수와 문장을 불러온다

ALLOWED_MOVES = {                                                                    # 티켓 상태마다 옮겨 갈 수 있는 상태의 리스트
    "열림": ["확인 중", "해결"],                                                     # 열림에서는 확인 중이나 해결로 갈 수 있다
    "확인 중": ["해결"],                                                             # 확인 중에서는 해결로만 갈 수 있다
    "해결": [],                                                                      # 해결에서는 어디로도 갈 수 없다
}


def find_open_ticket(tickets, alert, window):                                        # 티켓 리스트 · 알림 · 병합 시간(분)을 받는 함수
    """같은 대상 · 같은 규칙이고, 해결되지 않았고, window 분 안에 갱신된 티켓을 찾아 리턴한다. 없으면 None 을 리턴한다.
    같은 사건의 알림이 티켓 여러 장이 되는 것을 막을 때 쓴다.
    """
    for ticket in tickets:                                                           # 티켓을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. ticket 의 "entity" 가 alert 의 "entity" 와 같고(and) ticket 의 "rule" 도 alert 의 "rule" 과 같으면 (if, ==)
        if (
            ticket["entity"] == alert["entity"] 
            and ticket["rule"] == alert["rule"]
        ):
            if ticket["status"] != "해결":                                           # 해결되지 않은 티켓이면 — 미리 채운 줄
                gap = alert["minute"] - ticket["updated_at"]                         # 마지막 갱신 뒤 몇 분 지났는지 — 미리 채운 줄
                # 2. gap 이 window 이하이면 (if, <=)
                if gap <= window:
                    # 3. ticket 을 리턴한다
                    return ticket
    return None                                                                      # 맞는 티켓이 없으면 None 을 리턴한다 — 미리 채운 줄


def merge_alert(ticket, alert):                                                      # 티켓과 새 알림을 받는 함수
    """이미 있는 티켓에 새 알림을 합친다. 합친 알림 수를 1 늘리고, 알림 번호를 더하고, 갱신 시각을 알림이 온 시각으로 바꾼다.
    같은 사건이 되풀이될 때 새 티켓 대신 기존 티켓에 기록을 더할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. ticket 의 "count" 에 ticket["count"] + 1 을 저장한다 (1 늘린다)
    ticket["count"] = ticket["count"] + 1
    # 5. ticket 의 "incidents" 리스트에 alert 의 "id" 를 추가한다 (append)
    ticket["incidents"].append(alert["id"])
    # 6. ticket 의 "updated_at" 에 alert 의 "minute" 을 저장한다
    ticket["updated_at"] = alert["minute"]
    ticket["done"] = ticket["done"] + alert["done"]                                  # 새 알림의 조치 내역을 티켓의 조치 내역 뒤에 이어 붙인다 — 미리 채운 줄
    if has_failed_action(alert["done"]):                                             # 새 알림의 조치 확인이 실패했으면 — 미리 채운 줄
        ticket["needs_manual"] = True                                                # 직접 확인이 필요하다고 표시하고 — 미리 채운 줄
        ticket["next_step"] = MANUAL_STEP                                            # 다음 할 일도 직접 확인하라는 문장으로 바꾼다 — 미리 채운 줄


def handle_alert(alert, tickets, rules):                                             # 알림 · 티켓 리스트 · 규칙을 받는 함수
    """알림 한 건을 처리한다. 합칠 티켓이 있으면 합치고, 없으면 새 티켓을 만든다. 처리한 티켓과 「새 티켓」 또는 「병합」을 함께 리턴한다.
    알림이 올 때마다 부른다.
    """
    window = rules["merge_window_minutes"]                                           # 같은 사건으로 보는 시간(분) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. find_open_ticket(tickets, alert, window) 의 결과를 existing 에 저장한다
    existing = find_open_ticket(tickets, alert, window)
    # 8. existing 이 None 이면 (if, is)
    if existing is None:
        ticket_no = len(tickets) + 1                                                 # 새 티켓 번호 — 미리 채운 줄
        ticket = make_ticket(alert, ticket_no, rules, NEXT_STEPS)                    # 새 티켓을 만들고 — 미리 채운 줄
        tickets.append(ticket)                                                       # 티켓 리스트에 추가한다 — 미리 채운 줄
        return ticket, "새 티켓"                                                     # 티켓과 「새 티켓」을 함께 리턴하고 끝낸다 — 미리 채운 줄
    # 9. merge_alert(existing, alert) 를 호출한다 (합칠 티켓이 있을 때만 여기까지 온다)
    merge_alert(existing, alert)
    return existing, "병합"                                                          # 티켓과 「병합」을 함께 리턴한다 — 미리 채운 줄


def change_ticket_status(ticket, new_status, minute, who):                           # 티켓 · 바꿀 상태 · 시각(분) · 바꾼 사람을 받는 함수
    """허용된 이동이면 티켓 상태를 바꾸고 True, 아니면 바꾸지 않고 False 를 리턴한다. 바꾼 사람과 시각을 댓글로 남긴다.
    담당자가 티켓을 확인하기 시작했는지 끝냈는지 추적할 때 쓴다.
    """
    old_status = ticket["status"]                                                    # 지금 상태
    if new_status not in ALLOWED_MOVES[old_status]:                                  # 갈 수 없는 이동이면
        return False                                                                 # 바꾸지 않고 False 를 리턴한다
    ticket["status"] = new_status                                                    # 상태를 바꾼다
    if ticket["acked_at"] == -1:                                                     # 처음 확인하는 것이면
        ticket["acked_at"] = minute                                                  # 확인한 시각을 적는다
    if new_status == "해결":                                                         # 해결로 바꾸는 것이면
        ticket["resolved_at"] = minute                                               # 해결한 시각을 적는다
    ticket["updated_at"] = minute                                                    # 갱신 시각을 적는다
    comment = who + " · " + str(minute) + "분 · " + old_status + " → " + new_status  # 누가 언제 무엇을 했는지 문자열로 만든다
    ticket["comments"].append(comment)                                               # 댓글 리스트에 추가한다
    return True                                                                      # 바꿨다고 True 를 리턴한다
