from incident import change_status, match_playbooks, run_action, make_log_entry     # 월요일 파일의 함수를 불러온다

DONE_STATUSES = ["조치됨", "보고됨", "종료"]                                        # 이미 대응이 끝난 상태들
MAX_LOCKS_PER_RUN = 3                                                               # 한 번 실행에서 잠글 수 있는 계정의 최대 수


def find_skip_reason(action, entity, state):                                        # 액션 · 대상 · 모의 시스템을 받는 함수
    """이 액션을 건너뛰어야 하면 그 이유 문장을, 건너뛸 필요가 없으면 빈 글자("")를 리턴한다.
    계정을 잠그기 전에 이미 잠긴 계정인지, 한 번에 잠글 수 있는 수를 넘었는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. action 이 "계정 잠금" 이고(and) entity 가 state["locked_users"] 안에 있으면 (if, in)
    if action == "계정 잠금" and entity in state["locked_users"]:
    # 2.   "건너뜀: 이미 잠겨 있음" 을 리턴한다
        return "건너뜀: 이미 잠겨 있음"
    # 3. action 이 "계정 잠금" 이고(and) state["locked_users"] 의 개수(len)가 MAX_LOCKS_PER_RUN 이상이면 (if, >=)
    if action == "계정 잠금" and len(state["locked_users"]) >= MAX_LOCKS_PER_RUN:
    # 4.   "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)" 를 리턴한다
        return "건너뜀: 한 번에 잠글 수 있는 계정 수를 넘음 (담당자 확인 필요)"
    return ""                                                                       # 건너뛸 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def safe_run_action(action, incident, state):                                       # 액션 · 인시던트 · 모의 시스템을 받는 함수
    """액션을 실행하기 전에 건너뛸 이유가 있는지 먼저 확인한다. 이유가 있으면 실행하지 않고 그 이유를, 없으면 월요일의 run_action 으로 실행한 결과를 리턴한다.
    같은 일을 두 번 하거나 너무 많이 하는 것을 막고 싶을 때 쓴다.
    """
    entity = incident["entity"]                                                     # 대응할 대상
    skip_reason = find_skip_reason(action, entity, state)                           # 건너뛸 이유를 구한다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. skip_reason 이 빈 글자("")가 아니면 (if, !=)
    if skip_reason != "":
    # 6.   skip_reason 을 리턴한다
        return skip_reason
    # 7. run_action(action, incident, state) 의 결과를 리턴한다 (건너뛸 이유가 없으면 원래대로 실행한다)
    return run_action(action, incident, state)

def run_playbook_safe(incident, playbook, state, action_log):                       # 인시던트 · 플레이북 · 모의 시스템 · 기록 리스트를 받는 함수
    """알림 한 건을 안전하게 처리한다. 이미 끝난 알림이면 건너뛰고, 승인이 필요하면 멈추고, 아니면 액션을 실행한다.
    처리 결과를 「실행 완료」 · 「승인 대기」 · 「이미 처리됨」 · 「일부 건너뜀」 중 하나로 리턴한다.
    """
    if incident["status"] in DONE_STATUSES:                                         # 이미 대응이 끝난 인시던트이면
        entry = make_log_entry(incident, playbook, "전체", "이미 처리됨 — 건너뜀")  # 건너뛴 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
        return "이미 처리됨"                                                        # 이미 처리됨을 리턴한다
    change_status(incident, "분류됨")                                               # 대응을 시작하기 전에 분류됨 상태로 옮긴다
    if playbook["approval"] != "자동":                                              # 승인이 필요하면
        entry = make_log_entry(incident, playbook, "전체", "승인 대기")             # 승인 대기 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
        return "승인 대기"                                                          # 승인 대기를 리턴한다
    skipped = False                                                                 # 건너뛴 액션이 있는지 : 처음에는 없다
    for action in playbook["actions"]:                                              # 액션을 하나씩 꺼낸다
        result = safe_run_action(action, incident, state)                           # 안전한 방식으로 실행한다
        if result.startswith("건너뜀"):                                             # 결과 문장이 「건너뜀」으로 시작하면
            skipped = True                                                          # 건너뛴 액션이 있다고 적는다
        entry = make_log_entry(incident, playbook, action, result)                  # 기록을 만들고
        action_log.append(entry)                                                    # 기록 리스트에 추가한다
    if skipped:                                                                     # 건너뛴 액션이 있으면
        return "일부 건너뜀"                                                        # 조치됨으로 옮기지 않고 일부 건너뜀을 리턴한다
    change_status(incident, "조치됨")                                               # 모두 실행했으니 조치됨으로 옮긴다
    return "실행 완료"                                                              # 실행 완료를 리턴한다


def process_safe(incidents, registry, state, action_log):                           # 인시던트 리스트 · 플레이북 리스트 · 모의 시스템 · 기록 리스트를 받는 함수
    """알림을 하나씩 맞는 플레이북으로 안전하게 처리하고, 결과를 한 줄씩 출력한다.
    결과마다 몇 건인지 센 딕셔너리를 리턴한다.
    """
    counts = {}                                                                     # 실행 결과마다 몇 건인지 셀 딕셔너리
    for incident in incidents:                                                      # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                             # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                          # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                                  # 맞는 플레이북을 하나씩 꺼낸다
            result_text = run_playbook_safe(incident, playbook, state, action_log)  # 안전하게 실행한다
        counts[result_text] = counts.get(result_text, 0) + 1                        # 그 결과의 건수를 1 늘린다
        print(incident["id"], incident["entity"], "->", result_text, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다
    return counts                                                                   # 결과별 건수를 리턴한다
