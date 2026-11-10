from incident import load_json, match_playbooks, INCIDENTS_PATH, REGISTRY_PATH           # 월요일 파일의 함수를 불러온다
from playbook_runner import run_playbook                                                 # 월요일에 만든 실행기를 불러온다
from safe_runner import process_safe, MAX_LOCKS_PER_RUN                                  # 방금 만든 안전한 실행기를 불러온다

BULK_PATH = "bulk_incidents.json"                                                        # 인사 시스템 오류로 퇴사자 알림이 몰린 상황의 알림 파일 이름


def new_state():                                                                         # 인자가 없는 함수
    """잠긴 계정 · 차단한 IP · 티켓이 모두 비어 있는 모의 시스템 상태를 새로 만들어 리턴한다.
    실험마다 깨끗한 상태에서 시작하고 싶을 때 쓴다.
    """
    state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}  # 비어 있는 상태 딕셔너리
    return state                                                                         # 상태를 리턴한다


def run_monday_way(incidents, registry, state, action_log):                              # 월요일 방식으로 처리하는 함수
    """월요일에 만든 run_playbook 으로 알림을 모두 처리한다. 오늘 만든 안전장치는 쓰지 않는다.
    안전장치가 없으면 어떤 일이 생기는지 보고 싶을 때 쓴다.
    """
    for incident in incidents:                                                           # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                                  # 맞는 플레이북을 찾는다
        for playbook in playbooks:                                                       # 맞는 플레이북을 하나씩 꺼낸다
            run_playbook(incident, playbook, state, action_log)                          # 월요일 방식으로 실행한다


registry = load_json(REGISTRY_PATH)                                                      # 플레이북 등록 파일을 읽는다

print("--- 단계 1: 어제 방식(안전장치 없음)으로 같은 알림 5건을 두 번 처리")             # 단계 1 시작을 알리는 줄
incidents = load_json(INCIDENTS_PATH)                                                    # 알림 5건을 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
run_monday_way(incidents, registry, state, action_log)                                   # 첫 번째 처리
run_monday_way(incidents, registry, state, action_log)                                   # 같은 알림을 한 번 더 처리한다
print("잠긴 계정:", state["locked_users"])                                               # 잠긴 계정을 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 티켓 수를 출력한다

print("--- 단계 2: 어제 방식(안전장치 없음)으로 인사 오류 알림 7건 처리")                # 단계 2 시작을 알리는 줄
bulk_incidents = load_json(BULK_PATH)                                                    # 인사 오류 알림 7건을 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
run_monday_way(bulk_incidents, registry, state, action_log)                              # 월요일 방식으로 처리한다
locked_count = len(state["locked_users"])                                                # 잠긴 계정이 몇 개인지 센다
print("잠긴 계정", locked_count, "개:", state["locked_users"])                           # 잠긴 계정 수와 이름을 출력한다

print("--- 단계 3: 안전한 방식으로 같은 알림 5건을 두 번 처리")                          # 단계 3 시작을 알리는 줄
incidents = load_json(INCIDENTS_PATH)                                                    # 알림 5건을 다시 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
print("첫 번째 처리")                                                                    # 첫 번째 처리임을 알리는 줄
process_safe(incidents, registry, state, action_log)                                     # 안전한 방식으로 처리한다
print("두 번째 처리")                                                                    # 두 번째 처리임을 알리는 줄
process_safe(incidents, registry, state, action_log)                                     # 같은 알림을 한 번 더 처리한다
print("잠긴 계정:", state["locked_users"])                                               # 잠긴 계정을 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 티켓 수를 출력한다

print("--- 단계 4: 안전한 방식으로 인사 오류 알림 7건 처리 (한 번에 최대", MAX_LOCKS_PER_RUN, "개)")  # 단계 4 시작을 알리는 줄
bulk_incidents = load_json(BULK_PATH)                                                    # 인사 오류 알림 7건을 다시 읽는다
state = new_state()                                                                      # 깨끗한 상태로 시작한다
action_log = []                                                                          # 기록 리스트를 만든다
counts = process_safe(bulk_incidents, registry, state, action_log)                       # 안전한 방식으로 처리한다
locked_count = len(state["locked_users"])                                                # 잠긴 계정이 몇 개인지 센다
print("잠긴 계정", locked_count, "개:", state["locked_users"])                           # 잠긴 계정 수와 이름을 출력한다
print("결과별 건수:", counts)                                                            # 결과별 건수를 출력한다
print("티켓:", len(state["tickets"]), "건")                                              # 만든 티켓 수를 출력한다
print("건너뛴 액션과 이유:")                                                             # 건너뛴 액션을 모아 보여 주는 제목 줄
for entry in action_log:                                                                 # 기록을 하나씩 꺼낸다
    result_text = entry["result"]                                                        # 기록의 결과 문장
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. result_text 가 "건너뜀" 으로 시작하면 (if, startswith)
    if result_text.startswith("건너뜀"):
    # 9.   entry["incident"] · entry["action"] · "->" · result_text 를 출력한다 (print)
        print(entry["incident"], entry["action"], "->", result_text)