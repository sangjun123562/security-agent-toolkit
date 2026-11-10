from incident import load_json                                                              # 어제 파일의 함수를 불러온다
from approvals import apply_decision                                                        # 방금 만든 결정 적용 함수를 불러온다

pending = load_json("pending.json")                                                         # 승인 대기 3건을 읽는다
decisions = load_json("decisions.json")                                                     # 담당자 결정을 읽는다
state = {"locked_users": [], "blocked_ips": [], "tickets": [], "notifications": []}         # 깨끗한 모의 시스템 상태
action_log = []                                                                             # 감사 기록을 담을 빈 리스트

print("--- 단계 1: 승인 대기 건")                                                           # 단계 1 시작을 알리는 줄
for item in pending:                                                                        # 대기 건을 하나씩 꺼낸다
    print(item["id"], item["entity"], "·", item["playbook"], "·", item["why"])              # 번호 · 대상 · 플레이북 · 이유를 출력한다

print("--- 단계 2: 담당자 결정 처리")                                                       # 단계 2 시작을 알리는 줄
for item in pending:                                                                        # 대기 건을 하나씩 꺼낸다
    result_text = "결정 없음"                                                               # 결정이 없으면 이 글자가 남는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. item["id"] 가 decisions 안에 있으면 (if, in)
    if item["id"] in decisions:
    # 9.   apply_decision(item, decisions[item["id"]], state, action_log) 의 결과를 result_text 에 담는다
        result_text = apply_decision(item, decisions[item["id"]], state, action_log)
    print(item["id"], item["entity"], "->", result_text, "(상태: " + item["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 3: 처리 뒤 모의 시스템 상태")                                               # 단계 3 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                                  # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                   # 차단한 IP 를 출력한다
print("티켓:", len(state["tickets"]), "건 · 담당자 알림:", len(state["notifications"]), "건")  # 티켓과 알림 수를 출력한다

print("--- 단계 4: 감사 기록")                                                              # 단계 4 시작을 알리는 줄
for entry in action_log:                                                                    # 기록을 하나씩 꺼낸다
    print(entry["incident"], entry["playbook"], entry["action"], ":", entry["result"])      # 인시던트 · 플레이북 · 액션 · 결과를 출력한다
