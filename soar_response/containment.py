from account_actions import lock_account                              # 2교시에 만든 계정 잠금 함수를 불러온다
from session_actions import terminate_sessions                        # 방금 만든 세션 종료 함수를 불러온다


def contain_account(user, state, vip_accounts, incident_id, reason):  # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """계정을 먼저 잠그고, 잠겼다고 확인되면 이어서 열린 세션을 종료한 뒤, 조치 기록 리스트를 리턴한다.
    잠금과 세션 종료를 따로 하다가 생기는 빈틈을 막고 싶을 때 쓴다.
    """
    records = []                                                      # 조치 기록을 저장할 빈 리스트
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 lock_record 에 저장한다
    lock_record = lock_account(user, state, vip_accounts, incident_id, reason)
    records.append(lock_record)                                       # 잠금 기록을 리스트에 추가한다 — 미리 채운 줄
    # 5. lock_record 의 "after" 가 "잠김" 이면 (if, ==)
    if lock_record["after"] == "잠김":
    # 6.   terminate_sessions(user, state, incident_id, reason) 의 결과를 records 에 추가한다 (append)
        records.append(terminate_sessions(user, state, incident_id, reason))
    return records                                                    # 조치 기록 리스트를 리턴한다
