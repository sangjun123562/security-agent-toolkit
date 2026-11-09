from incident import load_json, save_json, INCIDENTS_PATH, REGISTRY_PATH, STATE_PATH, LOG_PATH  # 제공받은 함수를 불러온다
from playbook_runner import process_incidents                                           # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                                                   # 인시던트 파일을 리스트로 읽는다
registry = load_json(REGISTRY_PATH)                                                     # 플레이북 등록 파일을 리스트로 읽는다
incident_count = len(incidents)                                                         # 인시던트가 몇 건인지 센다
playbook_count = len(registry)                                                          # 등록된 플레이북이 몇 개인지 센다
print("--- 단계 1: 불러온 인시던트", incident_count, "건 · 등록된 플레이북", playbook_count, "개")  # 단계 1 시작을 알리는 줄

state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}     # 모의 시스템의 처음 상태 : 아무것도 없다
action_log = []                                                                         # 감사 기록을 담을 빈 리스트
print("--- 단계 2: 실행 전 모의 시스템 상태")                                           # 단계 2 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                               # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 3: 인시던트마다 플레이북 실행")                                         # 단계 3 시작을 알리는 줄
pending = process_incidents(incidents, registry, state, action_log)                     # 플레이북을 실행한다

print("--- 단계 4: 실행 후 모의 시스템 상태")                                           # 단계 4 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                              # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                               # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

pending_count = len(pending)                                                            # 승인 대기가 몇 건인지 센다
print("--- 단계 5: 승인 대기", pending_count, "건")                                     # 단계 5 시작을 알리는 줄과 건수
for waiting in pending:                                                                 # 승인 대기 건을 하나씩 꺼낸다
    print(waiting["incident"], waiting["entity"], waiting["playbook"], "·", waiting["approval"])  # 번호 · 대상 · 플레이북 · 승인 값을 출력한다

save_json(state, STATE_PATH)                                                            # 모의 시스템 상태를 파일에 저장한다
save_json(action_log, LOG_PATH)                                                         # 감사 기록을 파일에 저장한다
log_count = len(action_log)                                                             # 감사 기록이 몇 건인지 센다
print("--- 단계 6: 감사 기록", log_count, "건을", LOG_PATH, "에 저장")                  # 단계 6 시작을 알리는 줄과 건수
for entry in action_log:                                                                # 감사 기록을 하나씩 꺼낸다
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])  # 번호 · 플레이북 · 액션 · 결과를 출력한다
