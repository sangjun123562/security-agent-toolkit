def log_line(item, action, text):  # 인시던트 · 액션 · 결과 문장을 받는 함수
    """감사 기록(어떤 알림에 · 어떤 액션을 해서 · 결과가 무엇인지) 한 건을 딕셔너리로 만들어 리턴한다.
    모든 대응을 같은 모양으로 남겨 두면 나중에 한 목록으로 되짚을 수 있어서 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 키 "incident"(item 의 "id"), "playbook"(item 의 "playbook"), "action"(action), "result"(text) 를 가진 딕셔너리를 entry 에 담는다
    entry = {
        "incident": item["id"],
        "playbook": item["playbook"],
        "action": action,
        "result": text
    }
    return entry                   # 기록 한 건을 리턴한다
