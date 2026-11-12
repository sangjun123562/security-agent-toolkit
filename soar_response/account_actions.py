from containment_store import make_record                                             # 기록 한 건을 만드는 함수를 불러온다


def check_policy(user, vip_accounts):                                                 # 계정 이름과 VIP 계정 리스트를 받는 함수
    """자동으로 조치하면 안 되는 계정(VIP)이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    경로에서 이미 `승인 필요` 로 보냈어도 조치 함수가 마지막으로 한 번 더 막고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. user 가 vip_accounts 안에 있으면 (if, in)
    if user in vip_accounts:
    # 4.   "VIP 계정이라 자동 조치 대상이 아님" 을 리턴한다
        return "VIP 계정이라 자동 조치 대상이 아님"

    return ""                                                                         # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def verify_locked(user, state):                                                       # 계정 이름과 모의 시스템 상태를 받는 함수
    """계정이 잠긴 계정 리스트에 들어 있으면 True, 없으면 False 를 리턴한다.
    잠그라고 호출한 것과 실제로 잠긴 것이 같은지 조치 뒤에 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. user 가 state["locked_users"] 안에 있는지(in)의 결과를 리턴한다
    return user in state["locked_users"]

def lock_account(user, state, vip_accounts, incident_id, reason):                     # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """VIP 인지 먼저 확인하고 계정을 잠근 뒤, 실제로 잠겼는지 다시 확인해 조치 기록 한 건을 리턴한다.
    VIP 이거나 이미 잠겨 있으면 잠그지 않고 그 이유를 기록에 남긴다.
    """
    blocked = check_policy(user, vip_accounts)                                        # 자동 조치를 막을 이유를 구한다 — 미리 채운 줄
    if blocked != "":                                                                 # 막을 이유가 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "변경 없음", "변경 없음", blocked)  # 바꾸지 않고 이유를 기록한다 — 미리 채운 줄
    if user in state["locked_users"]:                                                 # 이미 잠겨 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "잠김", "잠김", "이미 잠겨 있어 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. state["locked_users"] 에 user 를 추가한다 (append)
    state["locked_users"].append(user)
    after = "잠김"                                                                    # 조치 뒤 상태 : 일단 잠겼다고 적고 — 미리 채운 줄
    if not verify_locked(user, state):                                                # 실제로 확인해 잠기지 않았으면 — 미리 채운 줄
        after = "잠기지 않음 (확인 실패)"                                             # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 잠금", user, incident_id, "잠기지 않음", after, reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unlock_account(user, state, incident_id, reason):                                 # 계정 · 상태 · 인시던트 번호 · 이유를 받는 함수
    """잠긴 계정을 해제하고 실제로 해제됐는지 확인해 조치 기록 한 건을 리턴한다.
    오탐으로 확인된 계정을 되돌릴 때 쓴다.
    """
    if user not in state["locked_users"]:                                             # 잠겨 있지 않으면 — 미리 채운 줄
        return make_record("계정 해제", user, incident_id, "잠기지 않음", "잠기지 않음", "잠겨 있지 않아 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. state["locked_users"] 에서 user 를 제거한다 (remove)
    state["locked_users"].remove(user)
    after = "잠기지 않음"                                                             # 조치 뒤 상태 : 일단 해제됐다고 적고 — 미리 채운 줄
    if verify_locked(user, state):                                                    # 실제로 확인해 아직 잠겨 있으면 — 미리 채운 줄
        after = "잠김 (확인 실패)"                                                    # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 해제", user, incident_id, "잠김", after, reason)         # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄
