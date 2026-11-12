from incident import load_json                                                          # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log  # 상태 · 기록 함수를 불러온다
from session_actions import find_open_sessions                                          # 방금 만든 세션 점검 함수를 불러온다
from containment import contain_account                                                 # 방금 만든 통합 조치 함수를 불러온다

vip_accounts = load_json("config/vip_accounts.json")                                    # VIP 계정 리스트를 읽는다
requests = [("INC-001", "dami", "퇴사한 계정의 서버 요청"), ("INC-003", "gaeun", "여러 로그 연결"), ("INC-006", "junho", "퇴사 처리 확인")]  # 조치 요청 3건 : (인시던트 번호, 계정, 이유)
state = new_state()                                                                     # 처음 상태에서 시작한다
reset_log()                                                                             # 기록 파일을 비운다

print("--- 단계 1: 점검 — 잠겼는데 세션이 열려 있는 계정")                              # 단계 1 시작을 알리는 줄
print(find_open_sessions(state))                                                        # 실습 전부터 있는 빈틈을 출력한다

print("--- 단계 2: 잠금 → 세션 종료")                                                   # 단계 2 시작을 알리는 줄
for incident_id, user, reason in requests:                                              # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. contain_account(user, state, vip_accounts, incident_id, reason) 의 결과를 records 에 저장한다
    records = contain_account(user, state, vip_accounts, incident_id, reason)
    for record in records:                                                              # 조치 기록을 하나씩 꺼낸다
        append_log(record)                                                              # 조치 기록을 파일에 남긴다
        print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 3: 조치 뒤 다시 점검")                                                  # 단계 3 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. find_open_sessions(state) 의 결과를 gaps_after 에 저장한다
gaps_after = find_open_sessions(state)
print("빈틈이 남은 계정:", gaps_after)                                                  # 점검 결과를 출력한다
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다

# 9. save_state(state) 를 호출한다 (상태를 파일에 저장한다)
save_state(state)
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                         # 단계 4 시작을 알리는 줄
print("잠긴 계정:", load_state()["locked_users"])                                       # 저장된 잠긴 계정을 출력한다
print("조치 기록:", len(load_json("containment_log.json")), "건")                       # 저장된 기록 수를 출력한다
