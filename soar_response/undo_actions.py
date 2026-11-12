from account_actions import unlock_account  # 오전 2교시에 만든 계정 해제 함수를 불러온다
from ip_actions import unblock_ip           # 오전 3교시에 만든 IP 해제 함수를 불러온다


def undo_account(record, state):            # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """계정 잠금 기록 한 건을 되돌려 계정을 해제하고, 해제 기록을 리턴한다.
    자동으로 잠근 계정을 오탐이 확인된 뒤에 원래대로 풀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. unlock_account(record["target"], state, record["incident"], "되돌리기: " + record["reason"]) 의 결과를 리턴한다
    return unlock_account(
        record["target"], state, record["incident"], "되돌리기: " + record["reason"]
    )

def undo_ip(record, state):                 # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """IP 차단 기록 한 건을 되돌려 IP 차단을 풀고, 해제 기록을 리턴한다.
    자동으로 차단한 IP 를 오탐이 확인된 뒤에 원래대로 풀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. unblock_ip(record["target"], state, record["incident"], "되돌리기: " + record["reason"]) 의 결과를 리턴한다
    return unblock_ip(
        record["target"], state, record["incident"], "되돌리기: " + record["reason"]
    )

def undo_record(record, state):             # 되돌릴 조치 기록과 연습용 시스템 상태를 받는 함수
    """조치 종류(계정 잠금 · IP 차단)에 맞는 되돌리기 함수를 골라 불러서, 해제 기록을 리턴한다.
    기록 한 건을 받아 알맞은 방법으로 되돌릴 때 쓴다.
    """
    if record["action"] == "계정 잠금":     # 계정 잠금 기록이면 — 미리 채운 줄
        return undo_account(record, state)  # 계정을 해제한다 — 미리 채운 줄
    return undo_ip(record, state)           # 아니면 IP 차단 기록이므로 IP 를 해제한다 — 미리 채운 줄
