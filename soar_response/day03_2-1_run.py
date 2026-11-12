from incident import load_json                                                          # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log  # 방금 만든 상태 · 기록 함수를 불러온다
from account_actions import lock_account, unlock_account                                # 방금 만든 계정 조치 함수를 불러온다

vip_accounts = load_json("config/vip_accounts.json")                                    # VIP 계정 리스트를 읽는다
requests = [("INC-001", "dami", "퇴사한 계정의 서버 요청"), ("INC-003", "gaeun", "여러 로그 연결"), ("INC-006", "junho", "퇴사 처리 확인")]  # 잠금 요청 3건 : (인시던트 번호, 계정, 이유)
state = new_state()                                                                     # 처음 상태에서 시작한다
reset_log()                                                                             # 기록 파일을 비운다

print("--- 단계 1: 조치 전에 잠겨 있는 계정")                                           # 단계 1 시작을 알리는 줄
print(state["locked_users"])                                                            # 잠긴 계정을 출력한다

print("--- 단계 2: 잠금 요청 3건")                                                      # 단계 2 시작을 알리는 줄
for incident_id, user, reason in requests:                                              # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. lock_account(user, state, vip_accounts, incident_id, reason) 의 결과를 record 에 저장한다
    record = lock_account(user, state, vip_accounts, incident_id, reason)
    # 9. append_log(record) 를 호출한다 (조치 기록을 파일에 남긴다)
    append_log(record)
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 3: 오탐으로 확인되어 dami 해제")                                        # 단계 3 시작을 알리는 줄
record = unlock_account("dami", state, "INC-001", "오탐으로 확인되어 해제")             # 해제한다
append_log(record)                                                                      # 해제 기록도 남긴다
print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

save_state(state)                                                                       # 상태를 파일에 저장한다
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                         # 단계 4 시작을 알리는 줄
saved_state = load_state()                                                              # 저장한 상태 파일을 읽는다
saved_log = load_json("containment_log.json")                                           # 저장한 기록 파일을 읽는다
print("잠긴 계정:", saved_state["locked_users"])                                        # 파일에 저장된 잠긴 계정을 출력한다
print("조치 기록:", len(saved_log), "건")                                               # 파일에 저장된 기록 수를 출력한다
