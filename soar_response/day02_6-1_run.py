from incident import load_json, INCIDENTS_PATH                                              # 어제 파일의 함수를 불러온다
from approvals import apply_decision                                                        # 5교시에 만든 결정 적용 함수를 불러온다
from retry_runner import run_with_retry, MAX_TRIES                                          # 방금 만든 재시도 함수를 불러온다
from flow import run_day_flow                                                               # 하루 흐름 함수를 불러온다
from failure_report import collect_failures                                                 # 실패한 기록을 모으는 함수를 불러온다


def new_state():                                                                            # 인자가 없는 함수
    """잠긴 계정 · 차단한 IP · 티켓이 모두 비어 있는 모의 시스템 상태를 새로 만들어 리턴한다.
    실험마다 깨끗한 상태에서 시작하고 싶을 때 쓴다.
    """
    state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}     # 비어 있는 상태 딕셔너리
    return state                                                                            # 상태를 리턴한다


incidents = load_json(INCIDENTS_PATH)                                                       # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                                                   # 계정 정보 파일을 읽는다
source_ips = load_json("source_ips.json")                                                   # 접속 IP 파일을 읽는다
trusted_ips = load_json("trusted_ips.json")                                                 # 신뢰 IP 파일을 읽는다
registry = load_json("config/playbook_registry.json")                                       # 플레이북 세 건을 읽는다
decisions = load_json("decisions.json")                                                     # 담당자 결정을 읽는다

print("--- 단계 1: 일시 장애 — 티켓 서비스가 2번 실패한 뒤 복구")                           # 단계 1 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
fail_plan = {"INC-001|티켓 생성": 2}                                                        # INC-001 의 티켓 생성이 2번 실패하게 한다
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)             # 재시도하며 실행한다
print(result)                                                                               # 결과 문장을 출력한다
print("만든 티켓:", len(state["tickets"]), "건")                                            # 만든 티켓 수를 출력한다

print("--- 단계 2: 서비스 중단 — 티켓 서비스가 계속 실패")                                  # 단계 2 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
fail_plan = {"INC-001|티켓 생성": 99}                                                       # INC-001 의 티켓 생성이 계속 실패하게 한다
result = run_with_retry("티켓 생성", incidents[0], state, fail_plan, MAX_TRIES)             # 재시도하며 실행한다
print(result)                                                                               # 결과 문장을 출력한다
print("만든 티켓:", len(state["tickets"]), "건")                                            # 만든 티켓 수를 출력한다

print("--- 단계 3: 하루 흐름 — 티켓 서비스가 계속 실패하는 상황")                           # 단계 3 시작을 알리는 줄
state = new_state()                                                                         # 깨끗한 상태로 시작한다
action_log = []                                                                             # 감사 기록을 담을 빈 리스트
fail_plan = {"INC-001|티켓 생성": 99}                                                       # INC-001 의 티켓 생성이 계속 실패하게 한다
pending = run_day_flow(incidents, registry, users_info, source_ips, trusted_ips, state, action_log, fail_plan)  # 하루 흐름을 실행한다

print("--- 단계 4: 담당자 결정 처리")                                                       # 단계 4 시작을 알리는 줄
for item in pending:                                                                        # 승인 대기 건을 하나씩 꺼낸다
    result_text = apply_decision(item, decisions[item["id"]], state, action_log)            # 담당자 결정을 적용한다
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 5: 하루가 끝난 뒤 모의 시스템 상태")                                        # 단계 5 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                                  # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                   # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 6: 담당자 확인이 필요한 건")                                                # 단계 6 시작을 알리는 줄
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. collect_failures(action_log) 의 결과를 failures 에 담는다
failures = collect_failures(action_log)
for entry in failures:                                                                      # 실패한 기록을 하나씩 꺼낸다
    incident_id = entry["incident"]                                                         # 실패한 인시던트 번호
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 9. incident_id · entry["action"] · ":" · entry["result"] 를 출력한다 (print)
    print(incident_id, entry["action"], ":", entry["result"])
for item in pending:                                                                        # 승인 대기 건을 하나씩 꺼낸다
    if item["status"] == "분류됨":                                                          # 아직 처리되지 않았으면
        print(item["id"], "승인 대기 :", item["why"])                                       # 승인 대기 건과 이유를 출력한다
