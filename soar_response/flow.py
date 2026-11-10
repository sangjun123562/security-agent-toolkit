from incident import change_status, match_playbooks                             # 어제 파일의 함수를 불러온다
from enrichment import enrich_incident                                          # 오전 2교시 : 맥락 붙이기
from routing import decide_route, apply_route                                   # 오전 3교시 : 경로 정하기
from approvals import hold_for_approval                                         # 5교시 : 승인 대기로 멈추기
from audit import log_line                                                      # 5교시 : 감사 기록 한 건 만들기
from retry_runner import run_with_retry, MAX_TRIES                              # 6교시 : 재시도하며 실행하기

VIP_REVIEW_ACTIONS = ["담당자 알림", "티켓 생성"]                               # VIP 계정 알림을 담당자가 승인하면 실행할 액션


def run_playbook_with_retry(incident, playbook, state, action_log, fail_plan):  # 인시던트 · 플레이북 · 모의 시스템 · 기록 · 실패 계획을 받는 함수
    """자동으로 해도 되는 플레이북의 액션을 하나씩, 실패하면 다시 시도하며 실행하고 기록한다.
    모두 성공하면 조치됨으로 바꾸고 「실행 완료」를, 하나라도 끝내 실패하면 상태를 그대로 두고 「일부 실패」를 리턴한다.
    """
    incident["playbook"] = playbook["id"]                                       # 기록에 남길 플레이북 번호를 적고
    change_status(incident, "분류됨")                                           # 대응을 시작하기 전에 분류됨으로 옮긴다
    failed = False                                                              # 실패한 액션이 있는지 : 처음에는 없다
    for action in playbook["actions"]:                                          # 액션을 하나씩 꺼낸다
        result = run_with_retry(action, incident, state, fail_plan, MAX_TRIES)  # 재시도하며 실행한다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. result 가 "실패" 로 시작하면 (if, startswith)
        if result.startswith("실패"):
        # 5.   failed 에 True 를 담는다 (실패한 액션이 있다고 적는다)
            failed = True
        action_log.append(log_line(incident, action, result))                   # 결과를 기록에 추가한다 — 미리 채운 줄
    if failed:                                                                  # 실패한 액션이 있으면
        return "일부 실패"                                                      # 조치됨으로 옮기지 않고 일부 실패를 리턴한다
    change_status(incident, "조치됨")                                           # 모두 성공했으니 조치됨으로 옮긴다
    return "실행 완료"                                                          # 실행 완료를 리턴한다


def run_day_flow(incidents, registry, users_info, source_ips, trusted_ips, state, action_log, fail_plan):  # 하루 흐름 전체를 받는 함수
    """알림마다 맥락 붙이기 → 경로 정하기 → 경로에 따라 처리하기(오탐 종료 · 승인 대기 · 재시도하며 실행)를 차례로 한다.
    알림마다 결과를 한 줄씩 출력하고, 승인 대기 건의 리스트를 리턴한다.
    """
    pending = []                                                                # 승인 대기 건을 담을 빈 리스트
    route_log = []                                                              # 경로 기록을 담을 빈 리스트
    for incident in incidents:                                                  # 인시던트를 하나씩 꺼낸다
        enrich_incident(incident, users_info, source_ips, trusted_ips)          # [오전 2교시] 맥락을 붙인다
        route, reason = decide_route(incident)                                  # [오전 3교시] 처리 경로와 이유를 정한다
        apply_route(incident, route, reason, route_log)                         # [오전 3교시] 경로를 적용한다 (오탐 종료이면 여기서 닫힌다)
        result_text = "맞는 플레이북 없음"                                      # 처음에는 없다고 적어 둔다
        if route == "오탐 종료":                                                # 오탐으로 닫았으면
            result_text = "오탐 종료"                                           # 오탐 종료라고 적는다
        elif route == "승인 필요":                                              # VIP 계정이라 담당자 승인이 필요하면
            pending.append(hold_for_approval(incident, "VIP 확인", VIP_REVIEW_ACTIONS, "VIP 계정이라 경로가 승인 필요", action_log))  # [5교시] 승인 대기로 멈춘다
            result_text = "승인 대기"                                           # 승인 대기라고 적는다
        else:                                                                   # 기본 경로이면
            for playbook in match_playbooks(incident, registry):                # 맞는 플레이북을 하나씩 꺼낸다
                if playbook["approval"] != "자동":                              # 플레이북이 승인을 요구하면
                    pending.append(hold_for_approval(incident, playbook["id"], playbook["actions"], "플레이북 승인 값이 " + playbook["approval"], action_log))  # [5교시] 승인 대기로 멈춘다
                    result_text = "승인 대기"                                   # 승인 대기라고 적는다
                else:                                                           # 자동이면
                    result_text = run_playbook_with_retry(incident, playbook, state, action_log, fail_plan)  # [6교시] 재시도하며 실행한다
        print(incident["id"], incident["entity"], "->", result_text, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다
    return pending                                                              # 승인 대기 리스트를 리턴한다
