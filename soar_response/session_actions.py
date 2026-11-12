from containment_store import make_record                  # 기록 한 건을 만드는 함수를 불러온다


def terminate_sessions(user, state, incident_id, reason):  # 계정 · 상태 · 인시던트 번호 · 이유를 받는 함수
    """계정에 열려 있는 로그인 세션을 모두 종료하고, 조치 전과 후의 세션 수를 기록 한 건으로 리턴한다.
    계정을 잠가도 이미 로그인한 세션은 남기 때문에, 잠근 뒤에 이어서 쓴다.
    """
    before_count = len(state["sessions"].get(user, []))    # 조치 전 세션 수 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. state["sessions"][user] 에 빈 리스트를 저장한다 (세션을 모두 종료한다)
    state["sessions"][user] = []
    after_count = len(state["sessions"].get(user, []))     # 조치 뒤 세션 수를 다시 구한다 — 미리 채운 줄
    return make_record("세션 종료", user, incident_id, "세션 " + str(before_count) + "개", "세션 " + str(after_count) + "개", reason)  # 조치 전 · 후 세션 수와 함께 기록한다 — 미리 채운 줄


def find_open_sessions(state):                             # 모의 시스템 상태를 받는 함수
    """잠겨 있는데도 열린 세션이 남아 있는 계정의 리스트를 리턴한다.
    잠금만 하고 세션을 끝내지 않아 생긴 빈틈을 점검할 때 쓴다.
    """
    gaps = []                                              # 빈틈이 있는 계정을 저장할 빈 리스트
    for user in state["locked_users"]:                     # 잠긴 계정을 하나씩 꺼낸다
        open_count = len(state["sessions"].get(user, []))  # 그 계정에 열린 세션 수 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. open_count 가 0 보다 크면 (if, >)
        if open_count > 0:
        # 3.   gaps 에 user 를 추가한다 (append)
            gaps.append(user)
    return gaps                                            # 빈틈이 있는 계정 리스트를 리턴한다
