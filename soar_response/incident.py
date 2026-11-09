import json                                                                       # JSON 파일을 읽고 쓰기 위해 json 을 불러온다
from datetime import datetime                                                     # 감사 기록에 시각을 적기 위해 datetime 을 불러온다

INCIDENTS_PATH = "incident_samples.json"                                          # 읽을 인시던트 파일 이름
REGISTRY_PATH = "config/playbook_registry.json"                                   # 읽을 플레이북 등록 파일 이름
STATE_PATH = "system_state.json"                                                  # 실행 결과 상태를 저장할 파일 이름
LOG_PATH = "action_log.json"                                                      # 감사 기록을 저장할 파일 이름
GRADE_ORDER = {"low": 1, "mid": 2, "high": 3}                                     # 등급을 크기를 비교할 수 있는 숫자로 바꾸는 딕셔너리
TRANSITIONS = {                                                                   # 상태마다 다음에 갈 수 있는 상태의 리스트
    "탐지됨": ["분류됨"],
    "분류됨": ["조치됨", "종료"],
    "조치됨": ["보고됨"],
    "보고됨": ["종료"],
    "종료": [],
}


def load_json(path):                                                              # 파일 경로를 받는 함수
    """JSON 파일을 읽어 리스트나 딕셔너리로 리턴한다.
    인시던트와 플레이북 등록 파일을 읽을 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:                                    # 파일을 읽기 모드로 연다
        data = json.load(file)                                                    # JSON 글자를 파이썬 값으로 바꾼다
    return data                                                                   # 읽은 값을 리턴한다


def save_json(data, path):                                                        # 저장할 값과 파일 경로를 받는 함수
    """값을 JSON 파일로 저장한다.
    실행 결과 상태와 감사 기록을 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                               # 파일을 쓰기 모드로 연다
        json.dump(data, file, ensure_ascii=False, indent=2)                       # 한글은 그대로, 줄을 나눠 저장한다


def change_status(incident, new_status):                                          # 인시던트와 바꿀 상태를 받는 함수
    """허용된 이동이면 상태를 바꾸고 True, 아니면 바꾸지 않고 False 를 리턴한다.
    분류하지 않은 인시던트에 바로 조치하는 실수를 막을 때 쓴다.
    """
    current_status = incident["status"]                                           # 지금 상태
    allowed_statuses = TRANSITIONS[current_status]                                # 지금 상태에서 갈 수 있는 상태 리스트
    if new_status not in allowed_statuses:                                        # 갈 수 있는 상태 리스트에 없는 이동이면
        return False                                                              # 바꾸지 않고 False 를 리턴한다
    incident["status"] = new_status                                               # 허용된 이동이므로 상태를 바꾼다
    return True                                                                   # 상태를 바꿨으니 True 를 리턴한다


def is_grade_enough(incident_grade, min_grade):                                   # 인시던트 등급과 플레이북의 최소 등급을 받는 함수
    """인시던트 등급이 최소 등급 이상이면 True, 아니면 False 를 리턴한다.
    등급이 낮은 인시던트에 무거운 대응이 실행되지 않게 할 때 쓴다.
    """
    return GRADE_ORDER[incident_grade] >= GRADE_ORDER[min_grade]                  # 등급을 숫자로 바꿔 비교한 결과를 리턴한다


def match_playbooks(incident, registry):                                          # 인시던트와 플레이북 리스트를 받는 함수
    """트리거 규칙과 조건 등급이 모두 맞는 플레이북을 리스트로 리턴한다.
    알림이 올 때 어떤 대응 절차를 쓸지 찾을 때 쓴다.
    """
    matched = []                                                                  # 맞는 플레이북을 담을 빈 리스트
    for playbook in registry:                                                     # 플레이북을 하나씩 꺼낸다
        has_rule = playbook["trigger_rule"] in incident["reasons"]                # 트리거 규칙이 탐지된 규칙 리스트 안에 있는지 구한다
        grade_ok = is_grade_enough(incident["grade"], playbook["min_grade"])      # 인시던트 등급이 최소 등급 이상인지 구한다
        if has_rule and grade_ok:                                                 # 트리거와 조건이 모두 맞으면
            matched.append(playbook)                                              # 맞는 플레이북을 리스트에 추가한다
    return matched                                                                # 맞는 플레이북 리스트를 리턴한다


def run_action(action, incident, state):                                          # 액션 · 인시던트 · 시스템 상태를 받는 함수
    """액션 하나를 모의 시스템(state)에서 실행하고 결과 문장을 리턴한다.
    대상 종류와 맞지 않는 액션은 실행하지 않고 건너뛴 이유를 리턴한다.
    """
    entity = incident["entity"]                                                   # 대응할 대상(사용자 이름 또는 IP)
    is_ip = "." in entity                                                         # 점이 있으면 IP 로 본다
    if action == "계정 잠금":                                                     # 계정 잠금이면
        if is_ip:                                                                 # 대상이 IP 이면
            return "건너뜀: 대상이 IP 라서 계정 잠금을 할 수 없습니다"            # 실행하지 않고 이유를 리턴한다
        state["locked_users"].append(entity)                                      # 잠긴 계정 리스트에 추가한다
        return "계정 " + entity + " 잠금 완료"                                    # 결과 문장을 리턴한다
    if action == "IP 차단":                                                       # IP 차단이면
        if not is_ip:                                                             # 대상이 사용자 계정이면
            return "건너뜀: 대상이 사용자라서 IP 차단을 할 수 없습니다"           # 실행하지 않고 이유를 리턴한다
        state["blocked_ips"].append(entity)                                       # 차단한 IP 리스트에 추가한다
        return "IP " + entity + " 차단 완료"                                      # 결과 문장을 리턴한다
    if action == "티켓 생성":                                                     # 티켓 생성이면
        ticket_id = "TCK-" + str(len(state["tickets"]) + 1)                       # 지금까지 만든 티켓 수에 1 을 더해 번호를 만든다
        ticket = {"id": ticket_id, "incident": incident["id"], "target": entity}  # 티켓 한 건을 딕셔너리로 만든다
        state["tickets"].append(ticket)                                           # 티켓 리스트에 추가한다
        return "티켓 " + ticket_id + " 생성"                                      # 결과 문장을 리턴한다
    if action == "담당자 알림":                                                   # 담당자 알림이면
        message = "인시던트 " + incident["id"] + " 확인 요청"                     # 알림 문장을 만든다
        state["notifications"].append(message)                                    # 알림 리스트에 추가한다
        return "담당자 알림 전송"                                                 # 결과 문장을 리턴한다
    return "알 수 없는 액션: " + action                                           # 어느 액션도 아니면 이유를 리턴한다


def make_log_entry(incident, playbook, action, result):                           # 인시던트 · 플레이북 · 액션 · 결과를 받는 함수
    """감사 기록 한 건을 딕셔너리로 만든다.
    어떤 인시던트에 어떤 플레이북이 무엇을 했는지 나중에 증명할 때 쓴다.
    """
    now_text = datetime.now().strftime("%H:%M:%S")                                # 지금 시각을 시:분:초 글자로 만든다
    entry = {"time": now_text, "incident": incident["id"], "playbook": playbook["id"], "action": action, "result": result}  # 기록 한 건
    return entry                                                                  # 기록을 리턴한다
