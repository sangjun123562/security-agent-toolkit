DEFAULT_NEXT_STEP = "담당자가 알림 내용을 읽고 필요한 일을 정한다"                      # 알림 상태를 모를 때 쓰는 다음 할 일
MANUAL_STEP = "조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다"  # 조치 확인에 실패한 티켓의 다음 할 일
NEXT_STEPS = {                                                                          # 알림 상태마다 담당자가 할 다음 일
    "조치됨": "조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다",                # 자동 조치가 끝난 알림
    "승인 대기": "승인할지 거절할지 정하고 정한 사람의 이름을 남긴다",                  # 승인을 기다리는 알림
    "조치 없음": "자동 조치가 없는 알림이니 직접 보고 조치가 필요한지 정한다",          # 자동 조치 대상이 아닌 알림
}


def make_title(alert):                                                                  # 알림 한 건을 받는 함수
    """티켓 제목(등급 · 대상 · 규칙)을 문자열로 만들어 리턴한다.
    티켓 목록에서 제목만 봐도 무슨 일인지 알 수 있게 할 때 쓴다.
    """
    grade = alert["grade"]                                                              # 알림 등급 — 미리 채운 줄
    entity = alert["entity"]                                                            # 알림 대상(사용자 이름 또는 IP) — 미리 채운 줄
    rule = alert["rule"]                                                                # 탐지된 규칙 이름 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. "[" + grade + "] " + entity + " — " + rule 을 이어 붙인 문자열를 리턴한다
    return "[" + grade + "] " + entity + " — " + rule

def find_next_step(alert, next_steps):                                                  # 알림 한 건과 다음 할 일 딕셔너리를 받는 함수
    """알림 상태에 맞는 다음 할 일 문장을 리턴한다. 정해 둔 문장이 없으면 기본 문장을 리턴한다.
    담당자가 티켓을 열자마자 무엇부터 할지 알게 할 때 쓴다.
    """
    status = alert["status"]                                                            # 알림 상태(조치됨 · 승인 대기 · 조치 없음) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. next_steps.get(status, DEFAULT_NEXT_STEP) 의 결과를 리턴한다 (키가 없으면 기본 문장)
    return next_steps.get(status, DEFAULT_NEXT_STEP)

def has_failed_action(done_list):                                                       # 조치 내역 문장 리스트를 받는 함수
    """조치 내역에 「확인 실패」가 들어 있는 문장이 하나라도 있으면 True, 없으면 False 를 리턴한다.
    조치했다고 했지만 실제로 바뀌지 않은 알림을 사람이 직접 보게 할 때 쓴다.
    """
    for text in done_list:                                                              # 조치 내역 문장을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. text 안에 "확인 실패" 가 들어 있으면 (if, in)
        if "확인 실패" in text:
            # 4. True 를 리턴한다
            return True
    return False                                                                        # 하나도 없으면 False 를 리턴한다 — 미리 채운 줄


def make_ticket(alert, ticket_no, rules, next_steps):                                   # 알림 · 티켓 번호 · 규칙 · 다음 할 일 딕셔너리를 받는 함수
    """알림 한 건으로 티켓 한 장(딕셔너리)을 만들어 리턴한다. 만든 시각과 응답 기한(SLA)을 함께 적는다.
    알림이 오면 바로 담당자가 읽을 수 있는 티켓을 만들 때 쓴다.
    """
    sla_table = rules["sla_minutes"]                                                    # 등급마다 정한 응답 기한(분) 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. sla_table[alert["grade"]] 를 sla_minutes 에 저장한다 (이 알림 등급의 응답 기한)
    sla_minutes = sla_table[alert["grade"]]
    # 6. alert["minute"] + sla_minutes 를 sla_due 에 저장한다 (응답해야 하는 시각)
    sla_due = alert["minute"] + sla_minutes
    needs_manual = has_failed_action(alert["done"])                                     # 조치 확인에 실패한 내역이 있는지 — 미리 채운 줄
    next_step = find_next_step(alert, next_steps)                                       # 다음 할 일 문장 — 미리 채운 줄
    if needs_manual:                                                                    # 확인 실패가 있으면 — 미리 채운 줄
        next_step = MANUAL_STEP                                                         # 직접 확인하라는 문장으로 바꾼다 — 미리 채운 줄
    ticket = {                                                                          # 티켓 한 장 — 미리 채운 줄
        "id": "TCK-" + str(ticket_no),                                                  # 티켓 번호
        "title": make_title(alert),                                                     # 제목
        "entity": alert["entity"],                                                      # 대상
        "rule": alert["rule"],                                                          # 규칙
        "grade": alert["grade"],                                                        # 등급
        "playbook": alert["playbook"],                                                  # 실행한 플레이북
        "done": alert["done"],                                                          # 조치 내역
        "status": "열림",                                                               # 티켓 상태 : 처음에는 열림
        "next_step": next_step,                                                         # 다음 할 일
        "needs_manual": needs_manual,                                                   # 직접 확인이 필요한지
        "created_at": alert["minute"],                                                  # 만든 시각(분)
        "updated_at": alert["minute"],                                                  # 마지막으로 갱신한 시각(분)
        "sla_due": sla_due,                                                             # 응답 기한 시각(분)
        "count": 1,                                                                     # 합쳐진 알림 수 : 처음에는 1
        "incidents": [alert["id"]],                                                     # 합쳐진 알림 번호
        "notified_count": 0,                                                            # 알림을 보낸 횟수
        "last_notified": -1,                                                            # 마지막으로 알림을 보낸 시각(분) : 아직 없음
        "acked_at": -1,                                                                 # 담당자가 처음 확인한 시각(분) : 아직 없음
        "resolved_at": -1,                                                              # 해결한 시각(분) : 아직 없음
        "escalation_level": 0,                                                          # 상급자에게 올린 단계 : 아직 없음
        "comments": [],                                                                 # 상태를 바꾼 기록
    }
    return ticket                                                                       # 만든 티켓을 리턴한다
