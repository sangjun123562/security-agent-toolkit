from containment_store import make_record                                    # 기록 한 건을 만드는 함수를 불러온다
from undo_actions import undo_record                                         # 방금 만든 되돌리기 함수를 불러온다

UNDOABLE_ACTIONS = ["계정 잠금", "IP 차단"]                                  # 해제로 되돌릴 수 있는 조치 이름


def find_incident_records(log, incident_id):                                 # 기록 리스트와 인시던트 번호를 받는 함수
    """기록 중 그 인시던트(알림 한 건)의 기록만 모은 뒤, 나중에 한 일이 먼저 오도록 순서를 뒤집어 리턴한다.
    조치를 거꾸로 되돌릴 때 쓴다.
    """
    found = []                                                               # 그 인시던트의 기록을 저장할 빈 리스트
    for record in log:                                                       # 기록을 하나씩 꺼낸다
        action_name = record["action"]                                       # 기록의 조치 이름 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. record 의 "incident" 가 incident_id 와 같으면 (if, ==)
        if record["incident"] == incident_id:
        # 4.   found 에 record 를 추가한다 (append)
            found.append(record)
    return list(reversed(found))                                             # 순서를 뒤집어 리턴한다 — 미리 채운 줄


def should_undo(record):                                                     # 기록 한 건을 받는 함수
    """자동 조치가 실제로 바꾼 것이고 해제로 되돌릴 수 있으면 True, 아니면 False 를 리턴한다.
    조치 전부터 그 상태였던 것과 확인에 실패한 조치는 되돌리지 않으려고 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. record 의 "before" 와 "after" 가 같으면 (if, ==)
    if record["before"] == record["after"]:
    # 6.   False 를 리턴한다 (바뀐 것이 없으니 되돌릴 것도 없다)
        return False
    if "확인 실패" in record["after"]:                                       # 확인에 실패한 조치이면 — 미리 채운 줄
        return False                                                         # 실제로 바뀌지 않았으니 되돌리지 않는다 — 미리 채운 줄
    return record["action"] in UNDOABLE_ACTIONS                              # 해제로 되돌릴 수 있는 조치 종류인지의 결과를 리턴한다 — 미리 채운 줄


def rollback_incident(incident_id, log, state):                              # 인시던트 번호 · 기록 리스트 · 연습용 시스템 상태를 받는 함수
    """인시던트의 기록을 거꾸로 훑으며 자동이 바꾼 것만 되돌리고, 되돌릴 수 없는 조치는 따로 기록해 리턴한다.
    조치 전부터 있던 상태를 건드리지 않고 오탐을 복구할 때 쓴다.
    """
    records = []                                                             # 되돌리기 기록을 저장할 빈 리스트
    for record in find_incident_records(log, incident_id):                   # 그 인시던트의 기록을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. should_undo(record) 가 참이면 (if)
        if should_undo(record):
        # 8.   undo_record(record, state) 의 결과를 records 에 추가한다 (append)
            records.append(undo_record(record, state))
        if record["before"] != record["after"] and not should_undo(record):  # 바뀌었는데 되돌릴 수 없는 조치이면 — 미리 채운 줄
            note = "되돌릴 수 없는 조치(" + record["action"] + ") — 사용자가 다시 로그인해야 함"  # 이유 문장을 만들고 — 미리 채운 줄
            records.append(make_record("되돌리기 불가", record["target"], incident_id, record["before"], record["after"], note))  # 기록으로 남긴다 — 미리 채운 줄
    return records                                                           # 되돌리기 기록 리스트를 리턴한다
