from incident import change_status, match_playbooks, run_action, make_log_entry

def run_playbook(incident, playbook, state, action_log):
    change_status(incident, "분류됨")
    
    # 1. approval 값이 "자동"이 아니면 멈추고 승인 대기 기록
    approval_val = str(playbook.get("approval", "")).strip()
    if approval_val != "자동":
        # 2. make_log_entry(incident, playbook, "전체", "승인 대기") 를 action_log에 추가
        action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))
        # 3. False 리턴
        return False
        
    # 자동인 경우 액션 순차 실행
    for action in playbook["actions"]:
        # 4. run_action 실행
        result = run_action(action, incident, state)
        # 5. 실행 결과 로그에 추가
        action_log.append(make_log_entry(incident, playbook, action, result))
        
    # 6. 조치 완료 상태로 변경
    change_status(incident, "조치됨")
    return True                    # 모두 실행했으니 True 를 리턴한다


def process_incidents(incidents, registry, state, action_log):                   # 인시던트 리스트 · 플레이북 리스트 · 시스템 상태 · 감사 기록을 받는 함수
    """인시던트마다 맞는 플레이북을 찾아 실행하고 결과를 한 줄씩 출력한다.
    승인 대기로 멈춘 건의 리스트를 리턴한다.
    """
    pending = []                                                                 # 승인 대기로 멈춘 건을 담을 빈 리스트
    for incident in incidents:                                                   # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                          # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                       # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                               # 맞는 플레이북을 하나씩 꺼낸다
            done = run_playbook(incident, playbook, state, action_log)           # 플레이북을 실행한다
            if done:                                                             # 실행했으면
                result_text = playbook["id"] + " 실행 완료"                      # 실행 완료라고 적는다
            else:                                                                # 승인 대기로 멈췄으면
                result_text = playbook["id"] + " 승인 대기"                      # 승인 대기라고 적는다
                waiting = {"incident": incident["id"], "entity": incident["entity"], "playbook": playbook["id"], "approval": playbook["approval"]}  # 대기 건 한 건
                pending.append(waiting)                                          # 승인 대기 리스트에 추가한다
        status_text = "(상태: " + incident["status"] + ")"                       # 지금 상태를 괄호 글자로 만든다
        print(incident["id"], incident["entity"], incident["grade"], "->", result_text, status_text)  # 번호 · 대상 · 등급 · 결과 · 상태를 출력한다
    return pending                                                               # 승인 대기 리스트를 리턴한다
